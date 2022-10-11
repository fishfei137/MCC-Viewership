import json
import pandas as pd

with open('./main_data/gephi_sigmajs/network/data.json', 'r') as f:
    data = json.load(f)
    
colours = {"0": "rgb(249,119,67)", "1": "rgb(154,150,229)", "2": "rgb(40,179,106)"}
modclass = {}
for i in data["nodes"]:
    modclass[i["id"]] = i["attributes"]["Modularity Class"]

for i in data["edges"]:
    i["color"] = colours[modclass[i["target"]]]
    
with open('./main_data/gephi_sigmajs/network/data.json', 'w') as f:   # update video id
    json.dump(data, f)
