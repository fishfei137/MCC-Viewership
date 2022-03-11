import os
import csv
import subprocess
import json
import logging
import sys
import now_bst
import mcc_website
from googleapiclient.discovery import build
from datetime import datetime, timedelta
import error_alert

now = now_bst.now()

mcc = open('./src/mcc.txt').readlines()[0]

api_key = os.environ.get('yt_apikey')
youtube = build('youtube', 'v3', developerKey=api_key)

with open(f"./main_data/{mcc}/{mcc}_yt_channels_info.json", 'r') as f:
    channels_info = json.load(f)

with open(f"./main_data/{mcc}/{mcc}_teams.json", 'r') as f:
    teams = json.load(f)


base_url = 'https://www.youtube.com/'


def get_sub_count(channel_id):
    request = youtube.channels().list(
        part='statistics',
        id=channel_id
    )
    response = request.execute()
    subs = response.get('items')[0].get('statistics').get('subscriberCount')

    return subs


def check_live(channel_id):
    url = base_url + "channel/" + channel_id + "/live"
    check = subprocess.run(f"streamlink {url}", capture_output=True)

    return not check.returncode


def get_video_id(channel_id):
    try:
        request2 = youtube.search().list(
            part='snippet',
            channelId=channel_id,
            eventType='live',
            type='video'
        )
        response2 = request2.execute()
        video_id = response2.get('items')[0].get('id').get('videoId')

        return video_id

    except IndexError:
        return 0


def get_livestream_details(video_id):
    try:
        request3 = youtube.videos().list(
            part='liveStreamingDetails',
            id=video_id,
        )

        response3 = request3.execute()

        viewers = response3.get('items')[0].get('liveStreamingDetails').get('concurrentViewers')
        start_str = response3.get('items')[0].get('liveStreamingDetails').get('actualStartTime')
        start_dt = datetime.strptime(start_str, "%Y-%m-%dT%H:%M:%SZ") #+ timedelta(hours=1)
        start = start_dt.strftime('%H:%M')

        return [viewers, start]

    except IndexError:
        return [0, 0]


def main():
    logging.basicConfig(level=logging.INFO,
                        handlers=[logging.FileHandler(f"./main_data/{mcc}/logs/youtube_output.log",
                                                      mode='a'), logging.StreamHandler(sys.stdout)])

    res = {}
    game = mcc_website.get_game()
    mcc_website.driver.quit()

    offline = []
    for k, v in channels_info.items():
        channel_id = v[0]
        video_id = v[1]
        subs = get_sub_count(channel_id)

        if video_id == 0:   # if theres no video id
            if check_live(channel_id):   # only update video id if channel is live
                v[1] = get_video_id(channel_id)
                logging.info(f"{now} {k} vid id updated")
            else:
                offline.append(k)
        else:
            if not check_live(channel_id):   # if theres vid id but is not live -> ended stream, so change back to 0
                v[1] = 0
                logging.info(f"{now} {k} ended, vid id changed to 0")
                offline.append(k)

        res[k] = [channel_id, subs, get_livestream_details(v[1])[0], get_livestream_details(v[1])[1], now, game, 'Youtube']
        logging.info(f"{now} {k} {v[1]}")

        for key, value in teams.items():  # teams
            if k in value:
                res[k] += [key]

    if game != '' and offline:  # only notify if event has started and theres ppl offline
        error_alert.tele_notify(msg = '\n'.join(offline), remarks = '*Youtube offline:*\n')

    # channel name: channel id, followers (subs), viewers, start, now, game, youtube, team

    with open(f"./main_data/{mcc}/{mcc}_yt_channels_info.json", 'w') as f:   # update video id
        json.dump(channels_info, f)
        logging.info(f"{now} vid id json updated")

    try:
        with open(f"./main_data/{mcc}/data/youtube_data.csv", 'a', newline='') as f:
            writer = csv.writer(f)
            for k, v in res.items():
                res_list = [k] + v
                writer.writerow(res_list)  # channels, id, followers, viewers, start, output, game, platform, team
        logging.info(f"{now} yt written to file")
    except PermissionError:
        logging.error(f"{now} excel sheet open")
        error_alert.tele_notify(msg = '*PERMISSION ERROR*, excel sheet open', remarks = '*Youtube:*')


if __name__ == "__main__":
    try:
        main()
    except:
        logging.exception(f"{now}")
        error_alert.tele_notify(msg = '*ERROR OCCURED*', remarks = '*Youtube:*')
