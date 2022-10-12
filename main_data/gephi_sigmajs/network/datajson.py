import json

# edge colour to follow target node colour

with open('./main_data/gephi_sigmajs/network/data.json', 'r') as f:
    data = json.load(f)

colours = {}
modclass = {}
for node in data["nodes"]:
    colours[node["attributes"]["Modularity Class"]] = node["color"]
    modclass[node["id"]] = node["attributes"]["Modularity Class"]

for edge in data["edges"]:
    edge["color"] = colours[modclass[edge["target"]]]
    
with open('./main_data/gephi_sigmajs/network/data.json', 'w') as f:
    json.dump(data, f)
