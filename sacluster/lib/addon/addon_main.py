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

logger = logging.getLogger("sacluster").getChild(os.path.basename(__file__))

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

def addon_main(cls_bil, ext_info, cls_mid):
    cluster_id           = cls_bil.cluster_id.split(": ")[1]
    IP_list             = get_IP_list(cls_bil, ext_info, cls_mid)
    params              = get_cluster_info ()
    json_addon_params   = load_addon_params ()
    node_password       = get_user_pass()
    
    addon_info          = {
        "clusterID"         : cluster_id,
        "IP_list"           : IP_list,
        "params"            : params,
        "json_addon_params" : json_addon_params,
        "node_password"     : node_password
    }

    edit_host       (cls_bil, ext_info, cls_mid, addon_info)
    switch_fw_zone  (cls_bil, ext_info, cls_mid, addon_info)

    port_open       (cls_bil, ext_info, cls_mid, addon_info, service_type="Proxy", service_name="squid")
    proxy_setup     (cls_bil, ext_info, cls_mid, addon_info, service_name="squid")

    # port_open       (cls_bil, ext_info, cls_mid, addon_info, service_type="Monitor", service_name="Ganglia")
    # monitor_setup   (cls_bil, clusterID, params, node_password, json_addon_params = json_addon_params, service_type="Monitor", service_name="Ganglia")

    setup_mpi (cluster_id, params, node_password, json_addon_params, service_type="MPI"  , service_name="mpich")

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

if __name__ == '__main__':
    cluster_id = "779987"
    sys.exit (addon_main (cluster_id))
