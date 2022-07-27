import sys
import json
import os
import datetime
import ipaddress
import logging
from tabnanny import check
from tqdm import tqdm
from concurrent import futures
import time
import pprint
from os.path import expanduser

home_path = expanduser("~") + "/sacluster"
os.makedirs(home_path, exist_ok = True)

dt_now = datetime.datetime.now()
log_filename = home_path + "/log/" + dt_now.strftime('%Y_%m_%d_%H_%M_%S.log')

logger = logging.getLogger("addon")
logger.setLevel(logging.DEBUG)
file_handler = logging.FileHandler(log_filename)
file_handler.setLevel(logging.WARNING)
handler_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(handler_format)
logger.addHandler(file_handler)

logger = logging.getLogger("addon").getChild(os.path.basename(__file__))

os.chdir(os.path.dirname(os.path.abspath(__file__)))
common_path = os.path.abspath("../..")
sys.path.append(common_path + "/lib/others")
from API_method import get, post, put, delete
from info_print import printout
sys.path.append(common_path + "/lib/auth")
from auth_func_pro import authentication_cli

sys.path.append(common_path + "/lib/addon/mylib")
from edit_host          import edit_host
from get_cluster_info   import get_cluster_info
from load_addon_params  import load_addon_params
from port_open          import port_open
from get_IP_list        import get_IP_list
sys.path.append(common_path + "/lib/addon/setupIP")
from setup_ip_eth1      import setup_ip_eth1
from switch_fw_zone     import switch_fw_zone
sys.path.append(common_path + "/lib/addon/setupProxy")
from proxy_setup        import proxy_setup
sys.path.append(common_path + "/lib/addon/setupMoniter")
from monitor_setup      import monitor_setup
sys.path.append(common_path + "/lib/addon/setupMpi")
from setup_mpi          import setup_mpi
sys.path.append(common_path + "/lib/addon/setupJobScheduler")
from setup_job_scheduler import setup_job_scheduler

import logging

logger = logging.getLogger("addon").getChild(os.path.basename(__file__))

def addon_main(cls_bil, ext_info, addon_info, f, info_list):

    logger.debug("check arguments for addon_main.")
    addon_info = addon_arg_check(cls_bil, ext_info, addon_info, f, info_list)

    logger.debug("edit /etc/hosts file.")
    edit_host(addon_info, f, info_list)

    logger.debug("change fire wall zone into Trusted.")
    switch_fw_zone(addon_info, f, info_list)

    logger.debug("Start setting up the Proxy server.")
    proxy_setup(addon_info, service_name="squid")
    print("please check squid!!")

    setup_job_scheduler (addon_info, f, info_list, job_scheduler_info = addon_info["Job_scheduler"])

    setup_mpi (addon_info, f, info_list, mpi_info = addon_info["MPI"])
    # setup_mpi (cluster_id, params, node_password, json_addon_params, service_type="MPI"  , service_name="mpich")

    logger.debug("Start setting up the Monitor.")
    monitor_setup (addon_info, f, info_list)
    print("Ganglia is Done!!")


#############################################################
########################## methods ##########################
#############################################################

def get_user_pass():
    while True:
        password = input('Enter cluster Password : ')
        password = password.strip()
        if password != '':
            break
    return password


def get_clusterID():
    while True:
        clusterID_tmp = input('Enter clusterID : ')
        clusterID_tmp = clusterID_tmp.strip()
        if len(clusterID_tmp) == 6:
            try:
                checkNum = int(clusterID_tmp)
                if 0 < checkNum & checkNum < 1000000:
                    break
            except:
                print("[ERROR]: You put a worng Cluster ID")
                continue
        else:
            print("[ERROR]: You put a worng Cluster ID")
    return clusterID_tmp


def check_clusterID(clusterID_tmp):
    # 認証周り
    auth_res = authentication_cli(fp = '', info_list = [1,0,0,0], api_index = True)
    max_workers = 1
    fp = ""
    monitor_info_list = [1,0,0,0]

    #set url
    url_list = {}
    zone_list = ['tk1a','tk1b', 'is1a', 'is1b']
    sub_url = ["/server","/disk","/switch","/interface","/bridge","/tag","/appliance","/power"]
    for zone in zone_list:
        url_list[zone] = "https://secure.sakura.ad.jp/cloud/zone/"+ zone +"/api/cloud/1.1"

    # 引数のクラスターIＤが存在するか調査、存在すれば終了
    ID_list = []
    for zone in zone_list:
        get_cluster_serever_info    = get(url_list[zone] + sub_url[0], auth_res)
        for i, server in enumerate(get_cluster_serever_info["Servers"]):
            ID = server["Tags"][0].split(": ")[1]
            ID_list.append(ID)
            if ID == clusterID_tmp:
                clusterID = clusterID_tmp
                return clusterID

    print("[ERROR]: There is not " + clusterID_tmp + " in your servers.")
    print("Cluster IDs are as follows.")
    print(set(ID_list))
    print("Please enter your cluster ID again.")
    clusterID_tmp = get_clusterID()
    clusterID     = check_clusterID(clusterID_tmp)
    return clusterID


def addon_arg_check(cls_bil, ext_info, addon_info, f, info_list):
    try:
        addon_info["clusterID"] = cls_bil.cluster_id.split(": ")[1]
    except:
        logger.error("cls_bil does not contain clusterID.")
        sys.exit()
    
    try:
        addon_info["IP_list"] = get_IP_list(cls_bil, ext_info)
    except:
        logger.error("Arguments for cls_bil and ext_info ERROR: They do not have enough data to create an IP_list.")
        sys.exit()

    addon_info["params"]            = get_cluster_info ()
    addon_info["json_addon_params"] = load_addon_params ()
    addon_info["node_password"]     = get_user_pass()
    
    return addon_info



#############################################################
######################### Test code #########################
#############################################################


if __name__ == '__main__':

    addon_info          = {
        "proxy":"squid",
        "options":{
            "config_name": "test",
            "Monitor": {
                "index": True,
                "params": {},
                "type": "openPBS"
            },
            "Job_scheduler": {
                "index": True,
                "params": {},
                "type": "slurm"
            },
            "ParallelComputing": {
                "index": True,
                "params": {},
                "type": "mpich"
            }
        }
    }

    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    path = os.path.abspath("../..")

    path_external = "/lib/.Ex_info/external_info_middle.json"
    with open(path + path_external, "r", encoding="utf-8") as f:
        data = json.load(f)

    ext_info = data["Infrastructure"]

    # home の sacluster から設定ファイル読み込み
    # addon_info["options"] = # middle_config_param

    import pickle
    with open("D:\Data\Doc\saclaster_addon_MiddlewareSetup\sacluster\sample01.pkl", "rb") as f:
        data01 = pickle.load(f)
    with open("D:\Data\Doc\saclaster_addon_MiddlewareSetup\sacluster\sample02.pkl", "rb") as f:
        data02 = pickle.load(f)

    class build_sacluster:
        def __init__(self):
            pass

    cls_bil  = build_sacluster
    cls_bil.cluster_id = data02
    cls_bil.all_id_dict = data01
    # ext_info = {
    #     "IP_addr":{
    #         "base": 192,
    #         "front": 168,
    #         "back": 169,
    #         "zone_seg": {
    #             "head":0,
    #             "tk1a":1,
    #             "tk1b":2,
    #             "is1a":3,
    #             "is1b":4,
    #             "tk1v":5
    #         }
    #     }
    # }
    info_list = [1,0,0,1]
    fp_filename = "test.txt"
    f = open(home_path + "/res/" + fp_filename, "w")
    info_list = [1,0,0,1]

    addon_main(cls_bil, ext_info, addon_info, f, info_list)