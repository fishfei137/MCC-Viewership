import json
import requests
import pandas as pd
import itertools
import now_bst


now = now_bst.now()

mcc = open('./src/mcc.txt').readlines()[0]

with open(f"./main_data/{mcc}/{mcc}_user_logins.json", 'r') as f:
    user_logins = json.load(f)


for i in range(len(user_logins)):   # convert to lowercase, as only lowercase is accepted
    user_logins[i] = user_logins[i].lower()


def get_chatters_info(user_logins): # multiple users
    chatters_info = {}
    for user in user_logins:
        url = f'https://tmi.twitch.tv/group/user/{user}/chatters'
        response = requests.get(url)

        keys = ['vips', 'moderators', 'staff', 'admins', 'global_mods', 'viewers']  # excludes broadcaster
        chatters = []
        for k in keys:
            for c in response.json()['chatters'][k]:
                chatters.append(c)  # unlists / flattens chatters

        chatters_info[user] = [response.json()['chatter_count'], chatters]
    return chatters_info
# {'c_1': [chatter_count, [list of chatters]], 'c_2': [chatter_count, [list of chatters]]}


# n*m sparse matrix, n=channel, m=chatters, where 1 denotes if chatters is in the channel, else 0
def channel_chatters(user_logins):
    chatters_info = get_chatters_info(user_logins)
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


# n*n shared matrix: (c_1, c_2) = number of shared viewers between channels c_1 and c_2
def channels_overlap(user_logins):
    df1 = channel_chatters(user_logins)

    pairs = []
    for p in itertools.combinations(df1.index, 2):
        pairs.append(p)

    shared = pd.DataFrame(index=user_logins, columns=user_logins)

    for p in pairs:
        shared_bool = df1.loc[p[0]] * df1.loc[p[1]] # 1 if shared, else 0
        shared.loc[p[0], p[1]] = sum(shared_bool)
        shared.loc[p[1], p[0]] = sum(shared_bool)

    shared = shared.fillna(0)
    return shared


# dict of [unique, total] chatters in each channel
def unique_total(user_logins):
    info = get_chatters_info(user_logins)
    df1 = channel_chatters(user_logins)
    
    res = {}
    for channel in df1.index:
        total = info[channel][0]
        unique = 0

        for chatter in df1.columns:
            if df1.loc[channel, chatter]==1 and sum(df1.loc[:, chatter])==1:  # if chatter is in channel, and this chatter is not in other channels
                unique += 1

        res[channel] = [unique, total]

    return res
# {'c_1': [39, 79], 'c_2': [95, 176], 'c_3': [92, 168]}


print('chatters info\n', get_chatters_info(user_logins))
print('channel * chatters\n', channel_chatters(user_logins))  
print('channel * channel, # of overlaps\n', channels_overlap(user_logins))
print('channel: [unique, total]', unique_total(user_logins))


# dic = {'col1':[0,1,0], 'col2': [1,1,0], 'col3': [1,1,1]}
# df = pd.DataFrame(dic, index = ['row1', 'row2', 'row3'])

