import json
import requests
import pandas as pd


# mcc = "test"   # change

# with open(f"./main_data/{mcc}/{mcc}_user_logins.json", 'r') as f:
#     user_logins = json.load(f)

user_logins = ['dream', 'captainpuffy']

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

# info = {'dream': [3, {"broadcaster": ['dream'], "viewers": ['v1', 'v2']}],
# 'gnf': [4, {"broadcaster": ['gnf'], "mods": ['mod1'], "viewers": ['v3', 'v4']}]}


df1 = pd.DataFrame()
for user in user_logins:
    chatters_info = get_chatters_info(user_logins)
    data = chatters_info[user]
    cols = data[1]

    temp_df = pd.DataFrame(columns = cols, index = [user])
    df1 = pd.concat([df1, temp_df])

    for viewer in df1.columns:
        if viewer in cols:
            df1.loc[user, viewer] = 1
    
df1 = df1.fillna(0)
print(df1)


# df2 - n*n shared matrix: (c_1, c_2) = number of shared viewers between channels c_1 and c_2
