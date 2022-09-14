import requests
import json

data_root = '../main_data/mcc_test'
teams_file_path = f'{data_root}/mcc_test_teams.json'
twitch_users_file_path = f'{data_root}/mcc_test_user_logins.json'
youtube_users_file_path = f'{data_root}/mcc_test_yt_channels_info.json'
mcc_name_file_path = f'./mcc.json'


def main():
    data = requests.get('https://mcc-data.memerson.xyz').json()

    with open(teams_file_path, 'w') as file:
        json.dump(data['teams'], file)

    with open(twitch_users_file_path, 'w') as file:
        json.dump(data['twitchUsers'], file)

    with open(youtube_users_file_path, 'w') as file:
        json.dump(data['youtubeUsers'], file)

    with open(mcc_name_file_path, 'w') as file:
        json.dump(data['event'], file)


if __name__ == '__main__':
    main()
