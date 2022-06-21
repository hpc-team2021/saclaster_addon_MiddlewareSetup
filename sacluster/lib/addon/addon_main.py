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

######
logger = logging.getLogger("addon").getChild(os.path.basename(__file__))


os.chdir(os.path.dirname(os.path.abspath(__file__)))
common_path = os.path.abspath("../..")
sys.path.append(common_path + "/lib/others")
from API_method import get, post, put, delete
from info_print import printout
sys.path.append(common_path + "/lib/auth")
from auth_func_pro import authentication_cli

sys.path.append(common_path + "/lib/addon/mylib")
from edit_host           import edit_host
from get_cluster_info     import get_cluster_info
from load_addon_params    import load_addon_params
from port_open           import port_open
from get_IP_list        import get_IP_list
sys.path.append(common_path + "/lib/addon/setupIP")
from setup_ip_eth1        import setup_ip_eth1
from switch_fw_zone       import switch_fw_zone
sys.path.append(common_path + "/lib/addon/setupProxy")
from proxy_setup         import proxy_setup
sys.path.append(common_path + "/lib/addon/setupMoniter")
from monitor_setup       import monitor_setup
sys.path.append(common_path + "/lib/addon/setupMpi")
from setup_mpi       import setup_mpi
import logging

logger = logging.getLogger("addon").getChild(os.path.basename(__file__))

def addon_main(cls_bil, ext_info, addon_info, f, info_list):

    logger.debug("check arguments for addon_main.")
    addon_info = addon_arg_check(cls_bil, ext_info, addon_info, f, info_list)

    logger.debug("edit /etc/hosts file.")
    edit_host       (addon_info, f, info_list)

    logger.debug("change fire wall zone into Trusted.")
    switch_fw_zone  (cls_bil, ext_info, addon_info)

    # port_open       (cls_bil, ext_info, addon_info, service_type="Proxy", service_name="squid")
    proxy_setup     (addon_info, service="squid")

    # port_open       (cls_bil, ext_info, addon_info, service_type="Monitor", service_name="Ganglia")
    # monitor_setup   (cls_bil, clusterID, params, node_password, json_addon_params = json_addon_params, service_type="Monitor", service_name="Ganglia")

    # setup_mpi (cluster_id, params, node_password, json_addon_params, service_type="MPI"  , service_name="mpich")


def addon_start ():
    print ("ミドルウェアの起動")
    # daemonStart ()

def get_user_pass():
    while True:
        password = input('Enter cluster Password : ')
        password = password.strip()
        if password != '':
            break
    return password

def get_clusterID():
    while True:
        clusterID = input('Enter clusterID : ')
        clusterID = clusterID.strip()
        if len(clusterID) == 6:
            try:
                checkNum = int(clusterID)
                if 0 < checkNum & checkNum < 1000000:
                    break
            except:
                print("[ERROR]: You put a worng Cluster ID")
                continue
        else:
            print("[ERROR]: You put a worng Cluster ID")
    return clusterID

def check_clusterID(clusterID):
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
            if ID == clusterID:
                return 0

    print("[ERROR]: There is not " + clusterID + " in your servers.")
    print("Cluster IDs are as follows.")
    print(set(ID_list))
    print("Please enter your cluster ID again.")
    clusterID = get_clusterID()
    print(clusterID)
    check_clusterID(clusterID)

def addon_arg_check(cls_bil, ext_info, addon_info, f, info_list):
    # 直前まで f, info_list は使用しているの構文チェックしません
    try:
        addon_info["clusterID"] = cls_bil.cluster_id.split(": ")[1]
    except:
        logger.error("cls_bil does not contain clusterID.")
        clusterID = get_clusterID()
        addon_info["clusterID"] = clusterID
    
    addon_info["IP_list"] = get_IP_list(cls_bil, ext_info)

    # try:
    #     addon_info["IP_list"]           = get_IP_list(cls_bil, ext_info)
    # except:
    #     logger.error("cls_bil does not contain clusterID.")

    # 
    addon_info["IP_list"]           = get_IP_list(cls_bil, ext_info)
    addon_info["params"]            = get_cluster_info ()
    addon_info["json_addon_params"] = load_addon_params ()
    addon_info["node_password"]     = get_user_pass()
    

    
    return addon_info

if __name__ == '__main__':

    addon_info          = {
        # "clusterID"         : clusterID,
        # "IP_list"           : IP_list,
        # "params"            : params,
        # "json_addon_params" : json_addon_params,
        # "node_password"     : node_password,
        "proxy":"squid", 
        "options":{
            "moniter":{
                "index"     :True,
                "type"      :"",
                "params"    :[]
            },
            "job_scheduler":{
                "index"     :True,
                "type"      :"",
                "params"    :[]
            },
            "ParallelComputing":{
                "index"     :True,
                "type"      :"m",
                "params"    :[]
            }
        }
    }

    cls_bil  = []
    ext_info = []
    info_list = [1,0,0,1]
    f = []
    addon_main(cls_bil, ext_info, addon_info, f, info_list)
