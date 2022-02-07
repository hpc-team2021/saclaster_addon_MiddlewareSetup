import os
import json

# User defined Library
os.chdir(os.path.dirname(os.path.abspath(__file__)))
common_path = os.path.abspath("../../..")

fileName = common_path + "\\lib\\addon\\addon.json"

def loadAddonParams ():
    # Load Command data
    json_open = open(fileName, 'r')
    jsonAddonParams = json.load(json_open)
    
    return jsonAddonParams