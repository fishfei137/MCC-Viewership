import pandas as pd
import json
import logging
import error_alert
import now_bst

# only run after event ends

now = now_bst.now()

with open('./src/mcc.json', 'r') as f:
    mcc = json.load(f)

with open(f"./main_data/{mcc}/{mcc}_user_logins.json", 'r') as f:
    user_logins = json.load(f)
 
# after mcc ends, should have full list of all chatters who visited each channel       
with open(f"./main_data/{mcc}/data/{mcc}_chatters_list.json", 'r') as f:
    chatters_dict = json.load(f)


def unique(chatters_dict):
    unique = {}
    for k, v in chatters_dict.items():
        unique[k] = len(v)

    unique_df = pd.DataFrame(unique.items(), columns = ['Channel', 'Unique'])
    
    return unique_df


def main():
    
    unique_df = unique(chatters_dict)
    try:
        unique_df.to_csv(f"./main_data/{mcc}/data/{mcc}_unique.csv", mode='w', index=False)
        logging.info(f"{now} unique viewers written to file")
    except PermissionError:
        logging.error(f"{now} excel sheet open")
        error_alert.tele_notify(msg = 'unique viewers excel sheet open', remarks = '*UNIQUE: PERMISSION ERROR\n*')
  
        
if __name__ == "__main__":
    try:
        main()
    except:
        logging.exception(f"{now}")
        error_alert.tele_notify(remarks = '*UNIQUE: ERROR OCCURED*')

    
