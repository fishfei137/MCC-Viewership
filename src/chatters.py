import json
import requests
import re
import pandas as pd
import itertools
import logging
import os
import sys
import now_bst
import error_alert
from timeit import default_timer as timer

now = now_bst.now()

mcc = open('./src/mcc.txt').readlines()[0]

with open(f"./main_data/{mcc}/{mcc}_user_logins.json", 'r') as f:
    user_logins = json.load(f)
    
with open(f"./main_data/{mcc}/data/{mcc}_chatters_list.json", 'r') as f:
    old_dict = json.load(f)

logging.basicConfig(level=logging.INFO,
                    handlers=[logging.FileHandler(f"./main_data/{mcc}/logs/{mcc}_output.log",
                                                  mode='a'), logging.StreamHandler(sys.stdout)])

def is_bot(string):
    if re.match(".*bot$", string):
        return True
    elif re.match("^stream.*", string):
        return True
    else:
        return False


def get_chatters_info(user_logins): # multiple users
    chatters_info = {}
    for user in user_logins:
        url = f'https://tmi.twitch.tv/group/user/{user.lower()}/chatters'
        response = requests.get(url)

        keys = ['vips', 'moderators', 'staff', 'admins', 'global_mods', 'viewers']  # excludes broadcaster
        chatters = []
        for k in keys:
            for c in response.json()['chatters'][k]:
                if k=='moderators' and is_bot(c):   # exclude chatbots
                    pass
                else:
                    chatters.append(c)  # unlists / flattens chatters

        chatters_info[user] = [response.json()['chatter_count'], chatters]
    return chatters_info
# {'c_1': [chatter_count, [list of chatters]], 'c_2': [chatter_count, [list of chatters]]}


# n*m sparse matrix, n=channel, m=chatters, where 1 denotes if chatters is in the channel, else 0
def channel_chatters(user_logins, chatters_info):
    df1 = pd.DataFrame()

    for user in user_logins:
        data = chatters_info[user]
        cols = data[1]

        temp_df = pd.DataFrame(columns = cols, index = [user])
        df1 = pd.concat([df1, temp_df])

        for viewer in df1.columns:
            if viewer in cols:
                df1.loc[user, viewer] = 1
  
    df1 = df1.fillna(0)
    return df1  


# n*4 matrix: [time, c_1, c_2, overlap]
def channels_overlap(df1):

    pairs = []
    for p in itertools.combinations(df1.index, 2):
        pairs.append(p)

    shared_list = []

    for p in pairs:
        shared_bool = df1.loc[p[0]] * df1.loc[p[1]] # 1 if shared, else 0
        shared_list.append([now, p[0], p[1], sum(shared_bool)])

    shared = pd.DataFrame(shared_list, columns = ['Time', 'c_1', 'c_2', 'Overlap'])
    return shared


# dict {channel: [unique, total, percent]}
def unique_total(chatters_info, df1):
    
    res_dict = {}
    for channel in df1.index:
        total = chatters_info[channel][0]
        unique = 0

        for chatter in df1.columns:
            if df1.loc[channel, chatter]==1 and sum(df1.loc[:, chatter])==1:  # if chatter is in channel, and this chatter is not in other channels
                unique += 1

        res_dict[channel] = [now, unique, total, round(unique/total, 5)]

    res = pd.DataFrame.from_dict(res_dict, orient = 'index', columns = ['Time', 'Unique', 'Total', 'Percentage'])
    return res


# union both old and new lists
def merge_2_dicts(dict1, dict2):
    res = {}
    for k1, v1 in dict1.items():
        if k1 not in res:
            res[k1] = v1
        for k2, v2 in dict2.items():
            if k2 not in res:
                res[k2] = v2
            elif k1 == k2:
                temp = dict1[k1] + dict2[k2]
                res[k1] = list(dict.fromkeys(temp))
    return res


# def unique_viewers(user_logins):
#     df1 = channel_chatters(user_logins)
    
#     res_df = df1.sum(axis=1)
    
#     return res_df
 


def main():
    
    chatters_info = get_chatters_info(user_logins)
    df1 = channel_chatters(user_logins, chatters_info)
    
    try:
        header = os.path.exists(f"./main_data/{mcc}/data/{mcc}_channels_overlap.csv")
        channels_overlap(df1).to_csv(f"./main_data/{mcc}/data/{mcc}_channels_overlap.csv", mode='a', header = not header, index=False)  # add header only if file doesnt exist
        logging.info(f"{now} channels overlap written to file")
    except PermissionError:
        logging.error(f"{now} excel sheet open")
        error_alert.tele_notify(msg = '*PERMISSION ERROR*, channels overlap excel sheet open', remarks = '*CHATTERS:*')

    try:
        header = os.path.exists(f"./main_data/{mcc}/data/{mcc}_unique_total.csv")
        unique_total(chatters_info, df1).to_csv(f"./main_data/{mcc}/data/{mcc}_unique_total.csv", mode='a', header = not header, index_label='Channel')  # add header only if file doesnt exist
        logging.info(f"{now} unique total written to file")
    except PermissionError:
        logging.error(f"{now} excel sheet open")
        error_alert.tele_notify(msg = '*PERMISSION ERROR*, unique total excel sheet open', remarks = '*CHATTERS:*')
        
    try:
        new_dict = {}
        for k, v in chatters_info.items():
            new_dict[k] = v[1]
            
        final = merge_2_dicts(old_dict, new_dict)
        with open(f"./main_data/{mcc}/data/{mcc}_chatters_list.json", 'w') as f:
            json.dump(final, f)
        logging.info(f"{now} chatters list json updated")
        
    except:
        logging.error(f"{now} chatters list json")
        error_alert.tele_notify(msg = 'ERROR chatters list json', remarks = '*CHATTERS:*')


if __name__ == "__main__":
    try:
        main()
    except:
        logging.exception(f"{now}")
        error_alert.tele_notify(remarks = '*CHATTERS: ERROR OCCURED*')