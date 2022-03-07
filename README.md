# MCC-viewership

Data collection (viewers, followers / subscribers etc) from Twitch, Youtube and mcc.live during Minecraft Championship (MCC) events.  
Google drive folder of all my MCC analyses: .

## Installation / Running the project

Before every MCC, I will manually type in the following:

- mcc19_teams.json: Each team and their members
- user_logins.json: List of all Twitch streamers' usernames
- yt_channel_info.json: List of all Youtube streamers' usernames, user_id, video_id _(video_id is initialised as 0)_

<!-- I used relative paths in the code, and this is my folder structure:
&ensp;&ensp;mcc19  *(for example)*
&ensp;&ensp;&ensp;&ensp;data
&ensp;&ensp;&ensp;&ensp;logs
&ensp;&ensp;&ensp;&ensp;mcc19_teams.json
&ensp;&ensp;&ensp;&ensp;user_logins.json
&ensp;&ensp;&ensp;&ensp;yt_channel_info.json
&ensp;&ensp;src   -->

You will need your own Twitch and Youtube API credenials. I used Telegram to alert myself when errors occur, so if you want to do the same, you will need a Telegram bot token as well.

I used Windows Task Scheduler to automate running the scripts twitch_data_main.py and yt_data.py every minute.

## Others

Data manipulation is done afterwards with R, and graphs are done with Tableau.
