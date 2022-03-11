import requests
import json
import os
import logging
import sys
import now_bst

now = now_bst.now()

mcc = open('./src/mcc.txt').readlines()[0]

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

logging.basicConfig(level=logging.INFO,
                    handlers=[logging.FileHandler(f"./main_data/{mcc}/logs/twitch_output.log",
                                                  mode='a'), logging.StreamHandler(sys.stdout)])

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
