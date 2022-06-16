import sys
import json
import os
import datetime
import ipaddress
import logging
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

logger = logging.getLogger("sacluster").getChild(os.path.basename(__file__))

def addon_main(cls_bil, ext_info, addon_info, f, info_list):
    addon_info["clusterID"]         = cls_bil.cluster_id.split(": ")[1]
    addon_info["IP_list"]           = get_IP_list(cls_bil, ext_info)
    addon_info["params"]            = get_cluster_info ()
    addon_info["json_addon_params"] = load_addon_params ()
    addon_info["node_password"]     = get_user_pass()
    
    addon_info          = {
        # "clusterID"         : clusterID,
        # "IP_list"           : IP_list,
        # "params"            : params,
        # "json_addon_params" : json_addon_params,
        # "node_password"     : node_password,
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

    edit_host       (cls_bil, ext_info, addon_info)
    switch_fw_zone  (cls_bil, ext_info, addon_info)

    # port_open       (cls_bil, ext_info, addon_info, service_type="Proxy", service_name="squid")
    proxy_setup     (cls_bil, ext_info, addon_info, service="squid")

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

def addon_arg_check(cls_bil, ext_info, addon_info):

    
    return out

if __name__ == '__main__':
    cluster_id = "849936"
    sys.exit (addon_main (cluster_id))
