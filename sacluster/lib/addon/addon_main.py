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
sys.path.append(common_path + "/lib/addon/setupIP")
from setup_ip_eth1        import setup_ip_eth1
from switch_fw_zone       import switch_fw_zone
sys.path.append(common_path + "/lib/addon/setupProxy")
from proxy_setup         import proxy_setup
sys.path.append(common_path + "/lib/addon/setupMoniter")
from monitor_setup       import monitor_setup

def addon_main(cluster_id):
    params          = get_cluster_info ()
    json_addon_params = load_addon_params ()
    node_password    = get_user_pass()

    # Setting IP address for Eth1
    # This method should be removed when
    # the coding on the sacluster side is done
    print ("Setting IP address to Eth1 connection")
    # setup_ip_eth1(cluster_id, params, node_password)

    #edit_host    (cluster_id, params, node_password, json_addon_params = json_addon_params)
    #switch_fw_zone(cluster_id, params, node_password, jsonAddonParams = json_addon_params)

    #port_open    (cluster_id, params, node_password, json_addon_params = json_addon_params, service_type="Proxy"  , service_name="Squid")
    proxy_setup  (cluster_id, params, node_password, json_addon_params = json_addon_params, service_type="Proxy"  , service_name="Squid")

    #port_open    (clusterID, params, node_password, json_addon_params = json_addon_params, service_type="Monitor", service_name="Ganglia")
    #monitor_setup(clusterID, params, node_password, json_addon_params = json_addon_params, service_type="Monitor", service_name="Ganglia")

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
    cluster_id = "986460"
    sys.exit (addon_main (cluster_id))
