import json
import string
import sys
import time
import logging
import os
import paramiko 

# from sacluster.lib.addon.mylib.editHost import Password
os.chdir(os.path.dirname(os.path.abspath(__file__)))
common_path = os.path.abspath("../../..")
from gangliaSetup import gangliaSetup

sys.path.append(common_path + "/lib/others")
from API_method import get, post, put, delete
sys.path.append(common_path + "/lib/auth")
from auth_func_pro import authentication_cli
sys.path.append(common_path + "/lib/addon/mylib")
from get_cluster_info import get_cluster_info
from load_addon_params import load_addon_params

logger = logging.getLogger("addon").getChild(os.path.basename(__file__))


def monitor_setup(addon_info, f, info_list):
    # Variable
    cluster_id = addon_info["clusterID"]
    params = addon_info["params"]
    node_password = addon_info["node_password"]
    ip_list = addon_info["IP_list"]

    # Get headnode IP address & number of computenodes
    head_ip = "255.255.255.255"
    num_compute = 0
    node_dict = params.get_node_info()
    disk_dict = params.get_disk_info()

    for zone, url in params.url_list.items():
        node_list = node_dict[zone]
        disk_list = list(disk_dict[zone].keys())
        if(len(node_list) != 0):
            for i in range(len(node_list)):
                # print(cluster_id + ':' + node_list[i]["Tags"][0] + ' | ' + node_list[i]['Name'])
                if (cluster_id in node_list[i]["Tags"][0] and 'headnode' in node_list[i]['Name']):
                    head_ip = node_list[i]['Interfaces'][0]['IPAddress']
                    os_type = params.cluster_info_all[cluster_id]["clusterparams"]["server"][zone]["head"]["disk"][0]["os"]
                elif (cluster_id in node_list[i]["Tags"][0]):
                    num_compute += 1
                else:
                    pass
        else:
            pass

    # Setitng to the Selected Service
    if addon_info["Monitor"]["index"] == True:
        if addon_info["Monitor"]["type"] == "ganglia":
            gangliaSetup (
                head_ip = head_ip,
                num_compute = num_compute,
                node_password = node_password,
                os_type = os_type,
                ip_list = ip_list["front"],
                info_list = info_list,
                fp = f
            )
    else:
        logger.debug ("Skip the Monitor Setting")
        return 0

if __name__ == '__main__':
    params              = get_cluster_info ()
    json_addon_params   = load_addon_params ()

    cls_bil  = []
    ext_info = []
    info_list = [1,0,0,1]
    f = []

    addon_info = {
        "Monitor":{
            "index": True
        },
        "clusterID"         : "619830",                 # !!! 任意のクラスターIDに変更 !!!
        "IP_list"           :{                          # コンピュートノードの数に合わせて変更
            "front" : ['192.168.2.1', '192.168.2.2'],
            "back"  : ['192.169.2.1', '192.169.2.2']
        },
        "params"            : params,
        "json_addon_params" : json_addon_params,
        "node_password"     : "test"                    # 設定したパスワードを入力
    }
    cluster_id       = addon_info["clusterID"]
    ip_list         = addon_info["IP_list"]
    params          = addon_info["params"]
    node_password    = addon_info["node_password"]
   
    monitor_setup(addon_info, f, info_list, service_name = 'Ganglia')

