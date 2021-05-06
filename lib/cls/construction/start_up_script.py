import sys
import json
import os
import base64
import requests
import pandas as pd
import random
import pprint
import datetime
import time
import ipaddress


path = "../../.."
os.chdir(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(path + "/lib/others")

from API_method import get, post, put
from info_print import printout

def json_input(filename):
    with open(filename, 'r') as f:
        json_f = json.load(f)
    return json_f


zone = "tk1v"
url = "https://secure.sakura.ad.jp/cloud/zone/"+ zone +"/api/cloud/1.1"
filename = "setting.json"
setting_info = json_input(path + "/setting/" + filename)
auth_res = base64.b64encode('{}:{}'.format(setting_info["access token"], setting_info["access token secret"]).encode('utf-8'))

note_param = {"Note":{"Name":"trial_script2","Content":"#!/bin/bash\necho 'Hello world!'"}}

make_note = post(url+"/note",auth_res,note_param)

print(make_note)

note_id = make_note["Note"]["ID"]

print(note_id)