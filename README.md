# MCC-viewership

Data collection _(viewers, followers / subscribers etc)_ from Twitch, Youtube and mcc.live during Minecraft Championship (MCC) events.  
Google drive folder of all my MCC analyses: .

## Installation / Running the project

Before every MCC, I will manually type in the following:

- mcc_test_teams.json: Each team and their members
- mcc_test_user_logins.json: List of all Twitch streamers' usernames
- mcc_test_yt_channel_info.json: List of all Youtube streamers' usernames, user_id, video_id (video_id is initialised as 0)
- mcc.txt: mcc event _(ensure naming of files is consistent throughout)_

I used relative paths in the code, so ensure you have the same folder structure.

You will need your own Twitch and Youtube API credenials. I used Telegram to alert myself when errors occur, so if you want to do the same, you will need a Telegram bot token as well.

I used Windows Task Scheduler to automate running the scripts twitch_data_main.py and yt_data.py every minute.

## Others

Data manipulation is done afterwards with R, and graphs are done with Tableau.
