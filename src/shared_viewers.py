import pandas as pd
import json
import logging
import error_alert
import itertools

# only run after event ends

with open('./src/mcc.json', 'r') as f:
    mcc = json.load(f)

with open(f"./main_data/{mcc}/{mcc}_user_logins.json", 'r') as f:
    user_logins = json.load(f)
 
# after mcc ends, should have full list of all chatters who visited each channel       
with open(f"./main_data/{mcc}/data/{mcc}_chatters_list.json", 'r') as f:
    chatters_init = json.load(f)

# sort chatters_dict by desc
chatters_dict = dict(sorted(chatters_init.items(), key = lambda x: -len(x[1])))   # x[0] = key, x[1] = values (list)


# n*m sparse matrix, n=channel, m=chatters, where 1 denotes if chatters is in the channel, else 0
def channel_chatters(chatters_dict):
    df1 = pd.DataFrame()

    for channel, chatters in chatters_dict.items():

        temp_df = pd.DataFrame(columns = chatters, index = [channel])
        df1 = pd.concat([df1, temp_df])

        for viewer in df1.columns:
            if viewer in chatters:
                df1.loc[channel, viewer] = 1
        
        remarks = f"*SHARED_VIEWERS: channel_chatters\n*{channel}"        
        error_alert.tele_notify(remarks = remarks)
  
    df1 = df1.fillna(0)
    print(f"channel_chatters done")
    error_alert.tele_notify(remarks = '*SHARED_VIEWERS: channel_chatters done*')
    return df1  


# n*4 matrix: [time, c_1, c_2, overlap]
def channels_overlap(df1):

    pairs = []
    for p in itertools.combinations(df1.index, 2):
        pairs.append(p)

    shared_list = []

    for p in pairs:
        shared_bool = df1.loc[p[0]] * df1.loc[p[1]] # 1 if shared, else 0
        shared_list.append([p[0], p[1], sum(shared_bool)])
        
        remarks = f"*SHARED_VIEWERS: channels_overlap\n{p[0]}, {p[1]}*"
        error_alert.tele_notify(remarks = remarks)

    shared = pd.DataFrame(shared_list, columns = ['c_1', 'c_2', 'Overlap'])
    print(f"channels overlap done")
    error_alert.tele_notify(remarks = '*SHARED_VIEWERS: channels_overlap done*')
    return shared


def main():
    
    df1 = channel_chatters(chatters_dict)
    shared = channels_overlap(df1)
    try:
        shared.to_csv(f"./main_data/{mcc}/data/{mcc}_channels_overlap.csv", mode='w', index=False)
        logging.info(f"channels overlap written to file")
    except PermissionError:
        logging.error(f"excel sheet open")
        error_alert.tele_notify(msg = 'channels overlap excel sheet open', remarks = '*SHARED_VIEWERS: PERMISSION ERROR\n*')
  
        
if __name__ == "__main__":
    try:
        main()
    except:
        logging.exception(f"error")
        error_alert.tele_notify(remarks = '*SHARED_VIEWERS: ERROR OCCURED*')

    
