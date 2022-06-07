import json
import requests
import re
import logging
import sys
import now_bst
import error_alert

now = now_bst.now()

with open('./src/mcc.json', 'r') as f:
    mcc = json.load(f)

with open(f"./main_data/{mcc}/{mcc}_user_logins.json", 'r') as f:
    user_logins = json.load(f)
    
try:    
    with open(f"./main_data/{mcc}/data/{mcc}_chatters_list.json", 'r') as f:
        old_dict = json.load(f)
except FileNotFoundError:
    old_dict = {user_logins[0]: []}
    
logging.basicConfig(level=logging.INFO,
                    handlers=[logging.FileHandler(f"./main_data/{mcc}/logs/{mcc}_output.log",
                                                  mode='a'), logging.StreamHandler(sys.stdout)])


def is_bot(string):
    if re.match(".*bot$", string) or re.match("^stream.*", string):
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
 


def main():
    
    chatters_info = get_chatters_info(user_logins)
        
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
        error_alert.tele_notify(msg = 'ERROR chatters list json', remarks = '*CHATTERS:\n*')


if __name__ == "__main__":
    try:
        main()
    except:
        logging.exception(f"{now}")
        error_alert.tele_notify(remarks = '*CHATTERS: ERROR OCCURED*')