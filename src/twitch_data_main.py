import twitch_data
import csv
import json
import logging
import now_bst
import mcc_website
import error_alert
from datetime import datetime, timedelta


now = now_bst.now()
logger = logging.getLogger(__name__)

mcc = open('./src/mcc.txt').readlines()[0]

with open(f"./main_data/{mcc}/{mcc}_user_logins.json", 'r') as f:
    user_logins = json.load(f)

with open(f"./main_data/{mcc}/{mcc}_teams.json", 'r') as f:
    teams = json.load(f)


def get_stream_details(user_logins):
    query = twitch_data.get_user_streams_query(user_logins)
    stream_info = twitch_data.get_response(query)

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
    query2 = twitch_data.get_user_id_query(user_logins)
    user_info = twitch_data.get_response(query2)

    user_id = {}
    for i in range(len(user_logins)):
        user_id[f"{user_info.json()['data'][i]['display_name']}"] = int(user_info.json()['data'][i]['id'])

    return user_id


def get_follower_count(user_id):
    follower_count = {}
    for key in user_id:
        query3 = twitch_data.get_followers_query(user_id[key])
        followers_info = twitch_data.get_response(query3)
        follower_count[key] = [user_id[key], followers_info.json()['total']]   # name: user_id, followers

    return follower_count


def main():
    
    res = {}  # name: user id, followers, viewers, start, now, game, twitch, team
    user_id = get_user_id(user_logins)
    follower_count = get_follower_count(user_id)
    stream = get_stream_details(user_logins)
    game = mcc_website.get_game()
    mcc_website.driver.quit()

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
        logger.info(f"{now} twitch written to file")
    except PermissionError:
        logger.error(f"{now} excel sheet open")
        error_alert.tele_notify(msg = '*PERMISSION ERROR*, excel sheet open', remarks = '*Twitch:*')



if __name__ == "__main__":
    try:
        main()
    except:
        logger.exception(f"{now}")
        error_alert.tele_notify(msg = '*ERROR OCCURED*', remarks = '*Twitch:*')
