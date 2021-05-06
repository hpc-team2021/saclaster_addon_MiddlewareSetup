import sys
import json
import os
import base64
import requests
import pprint

path = "../../.."
os.chdir(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(path + "/lib/others")

from API_method import get, post, put, delete
from info_print import printout

def json_input(filename):
    with open(filename, 'r') as f:
        json_f = json.load(f)
    return json_f

configuration_info = json_input("./trial_configfile.json")
zone = configuration_info["zone"]
url = "https://secure.sakura.ad.jp/cloud/zone/"+zone+"/api/cloud/1.1"

filename = "setting.json"
setting_info = json_input(path + "/setting/" + filename)
auth_res = base64.b64encode('{}:{}'.format(setting_info["access token"], setting_info["access token secret"]).encode('utf-8'))

#get server information
sub_url = "/server"
get_server_info = get(url+sub_url,auth_res)

servers_info = get_server_info["Servers"]
l_index = [d.get('Index') for d in servers_info]
l_name = [d.get('Name') for d in servers_info]
l_id = [d.get('ID') for d in servers_info]
index_name = dict(zip(l_index,l_name))
name_id = dict(zip(l_name,l_id))

pprint.pprint(index_name)
delete_server_index = printout('Select the delete server index:', info_type = 2, info_list = [1,0,0,0], fp = '')
delete_server_index = int(delete_server_index)
delete_server_name = index_name[delete_server_index]
delete_server_id = name_id[delete_server_name]

#該当IDのサーバ情報の取得
get_delete_server_info = get(url+sub_url+'/'+delete_server_id,auth_res)

# サーバーの電源をきる
if get_delete_server_info['Server']['Instance']['Status'] == 'up':
    sub_url_3 = "/server/" + delete_server_id + "/power"
    delete(url+sub_url_3, auth_res)
else:
    pass


# サーバーを削除する
sub_url_4 = "/server/" + delete_server_id
delete_res = delete(url+sub_url_4, auth_res)

'''
# スイッチの繋がりをきる（NICを削除）
sub_url_1 = "/interface/インタフェースID/to/switch"
delete(url+sub_url_1, auth_res)

# スイッチの削除
sub_url_2 = "/switch/スイッチID"
delete(url+sub_url_2, auth_res)
'''



