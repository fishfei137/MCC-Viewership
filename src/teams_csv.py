import json, csv

mcc = open('./src/mcc.txt').readlines()[0]

with open(f"./main_data/{mcc}/{mcc}_teams.json", 'r') as f:
    teams = json.load(f)

for k, v in teams.items():
    members = ''
    for i in range(len(v)-1):
        members += f'{v[i]}, '
    members += f'{v[-1]}'
    teams.update({k: members})

with open(f"./main_data/{mcc}/data/{mcc}_teams.csv", 'a', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['Team', 'Members'])
    for k, v in teams.items():
        teams_list = [k] + [v]
        writer.writerow(teams_list)
