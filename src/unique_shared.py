import pandas as pd
import json
import logging
import os
import error_alert
import now_bst
import itertools

# only run after event ends

# check if chatters list alr exists, if not create one
# after mcc ends, should have full list of all chatters who visited each channel
# separate file: run it through channel_chatters
# try catch for if channel not in json

now = now_bst.now()

mcc = open('./src/mcc.txt').readlines()[0]

with open(f"./main_data/{mcc}/{mcc}_user_logins.json", 'r') as f:
    user_logins = json.load(f)
        
with open(f"./main_data/{mcc}/data/{mcc}_chatters_list.json", 'r') as f:
    chatters_dict = json.load(f)


def unique(chatters_dict):
    unique = {}
    for k, v in chatters_dict.items():
        unique[k] = len(v)

    unique_df = pd.DataFrame(unique.items(), columns = ['Channel', 'Unique'])
    
    return unique_df

# twitch = pd.read_csv(f"./main_data/{mcc}/data/{mcc}_twitch_data.csv")
# final = pd.merge(twitch, unique_df, how='left', on='Channel')
# print(final)


# n*m sparse matrix, n=channel, m=chatters, where 1 denotes if chatters is in the channel, else 0
def channel_chatters(chatters_dict):
    df1 = pd.DataFrame()

    for channel, chatters in chatters_dict.items():

        temp_df = pd.DataFrame(columns = chatters, index = [channel])
        df1 = pd.concat([df1, temp_df])

        for viewer in df1.columns:
            if viewer in chatters:
                df1.loc[channel, viewer] = 1
  
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


def main():
    
    unique_df = unique(chatters_dict)
    try:
        unique_df.to_csv(f"./main_data/{mcc}/data/{mcc}_unique.csv", mode='w', index=False)
        logging.info(f"{now} unique viewers written to file")
    except PermissionError:
        logging.error(f"{now} excel sheet open")
        error_alert.tele_notify(msg = 'unique viewers excel sheet open', remarks = '*UNIQUE_SHARED: PERMISSION ERROR*')
    
    df1 = channel_chatters(chatters_dict)
    shared = channels_overlap(df1)
    try:
        shared.to_csv(f"./main_data/{mcc}/data/{mcc}_channels_overlap.csv", mode='w', index=False)
        logging.info(f"{now} channels overlap written to file")
    except PermissionError:
        logging.error(f"{now} excel sheet open")
        error_alert.tele_notify(msg = 'channels overlap excel sheet open', remarks = '*UNIQUE_SHARED: PERMISSION ERROR*')
  
        
if __name__ == "__main__":
    try:
        main()
    except:
        logging.exception(f"{now}")
        error_alert.tele_notify(remarks = '*UNIQUE_SHARED: ERROR OCCURED*')

    
