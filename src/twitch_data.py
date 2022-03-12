import os
import sys
import requests
import csv
import json
import logging
import now_bst
import mcc_website
import error_alert
from datetime import datetime, timedelta

now = now_bst.now()
mcc = open('./src/mcc.txt').readlines()[0]

logging.basicConfig(level=logging.INFO,
                    handlers=[logging.FileHandler(f"./main_data/{mcc}/logs/{mcc}_output.log",
                                                  mode='a'), logging.StreamHandler(sys.stdout)])


with open(f"./main_data/{mcc}/{mcc}_user_logins.json", 'r') as f:
    user_logins = json.load(f)

with open(f"./main_data/{mcc}/{mcc}_teams.json", 'r') as f:
    teams = json.load(f)


base_url = 'https://api.twitch.tv/helix/'
auth_url = 'https://id.twitch.tv/oauth2/token'
client_id = os.environ.get('twitch_client_id')
secret = os.environ.get('twitch_secret')
indent = 2

autparams = {'client_id': client_id,
             'client_secret': secret,
             'grant_type': 'client_credentials'
             }

autcall = requests.post(url=auth_url, params=autparams)
access_token = autcall.json()['access_token']

head = {
    'Client-ID': client_id,
    'Authorization': "Bearer " + access_token
}


# get response from twitch API call
def get_response(query):
    url = base_url + query
    response = requests.get(url, headers=head)
    logging.info(f"{now} {response}")
    return response


def print_response(response):
    response_json = response.json()
    print_response = json.dumps(response_json, indent=indent)
    print(print_response)


# pass in a twitch username and get the user's current live stream info
def get_user_streams_query(user_logins):  #user_logins must be a list (multiple users)
    temp = f'streams?user_login={user_logins[0]}'
    for i in user_logins[1:]:
        temp = f'{temp}&user_login={i}'
    return temp


def get_user_id_query(user_logins):  #user_logins must be a list (multiple users)
    temp = f'users?login={user_logins[0]}'
    for i in user_logins[1:]:
        temp = f'{temp}&login={i}'
    return temp


def get_followers_query(user_id):  #single user_id
    return f'users/follows?to_id={user_id}'


def get_stream_details(user_logins):
    query = get_user_streams_query(user_logins)
    stream_info = get_response(query)

    stream = {}
    for i in range(len(stream_info.json()['data'])):
        user_name = stream_info.json()['data'][i]['user_name']
        viewers = stream_info.json()['data'][i]['viewer_count']
        start_str = stream_info.json()['data'][i]['started_at']
        start_dt = datetime.strptime(start_str, "%Y-%m-%dT%H:%M:%SZ") #+ timedelta(hours=1)
        start = start_dt.strftime('%H:%M')
        stream[user_name] = [viewers, start]

    return stream


def get_user_id(user_logins):
    query2 = get_user_id_query(user_logins)
    user_info = get_response(query2)

    user_id = {}
    for i in range(len(user_logins)):
        user_id[f"{user_info.json()['data'][i]['display_name']}"] = int(user_info.json()['data'][i]['id'])

    return user_id


def get_follower_count(user_id):
    follower_count = {}
    for key in user_id:
        query3 = get_followers_query(user_id[key])
        followers_info = get_response(query3)
        follower_count[key] = [user_id[key], followers_info.json()['total']]   # name: user_id, followers

    return follower_count


def main(game):
    
    res = {}  # name: user id, followers, viewers, start, now, game, twitch, team
    user_id = get_user_id(user_logins)
    follower_count = get_follower_count(user_id)
    stream = get_stream_details(user_logins)

    offline = []

    for key in follower_count:
        if key in stream.keys():        # if live
            res[key] = follower_count[key] + stream[key] + [now, game, 'Twitch']
        else:       # if offline
            res[key] = follower_count[key] + [0, 0, now, game, 'Twitch']
            offline.append(key)

        for k, v in teams.items():  # teams
            if key in v:
                res[key] = res[key] + [k]

    if game != '' and offline:   # only notify if event has started and theres ppl offline
        error_alert.tele_notify(msg = '\n'.join(offline), remarks = '*Twitch offline:*\n')

    try:
        with open(f"./main_data/{mcc}/data/twitch_data.csv", 'a', newline='') as f:
            writer = csv.writer(f)
            for k, v in res.items():
                res_list = [k] + v  # channels, id, followers, viewers, start, output, game, platform, team
                writer.writerow(res_list)
        logging.info(f"{now} twitch written to file")
    except PermissionError:
        logging.error(f"{now} excel sheet open")
        error_alert.tele_notify(msg = '*PERMISSION ERROR*, excel sheet open', remarks = '*Twitch:*')



if __name__ == "__main__":
    try:
        game = mcc_website.get_game()
        main(game)
    except:
        logging.exception(f"{now}")
        error_alert.tele_notify(msg = '*ERROR OCCURED*', remarks = '*Twitch:*')
