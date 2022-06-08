import os
import json

# User defined Library
os.chdir(os.path.dirname(os.path.abspath(__file__)))
common_path = os.path.abspath("../../..")

fileName = common_path + "\\lib\\addon\\addon.json"

def load_addon_params ():
    # Load Command data
    json_open = open(fileName, 'r')
    json_addon_params = json.load(json_open)
    
    return json_addon_params