import json
from operator import index
from platform import node
import re
import string
import sys
import time
import logging
import os
import paramiko

# User defined Library
os.chdir(os.path.dirname(os.path.abspath(__file__)))
common_path = os.path.abspath("../../..")
fileName = common_path + '\\lib\\addon\\setupMpi\\mpich.json'

# Changing standard output color for exception error
RED = '\033[31m'
END = '\033[0m'

sys.path.append(common_path + "/lib/addon/mylib")
from load_addon_params import load_addon_params
from get_cluster_info import get_cluster_info

sys.path.append(common_path + "/lib/addon/setupJobScheduler")
from slurm_main import slurm_main 

#################
# Main Programm #
#################
def setup_job_scheduler (addon_info, fp, info_list, service_name):
    # 今回の処理に必要な変数のみを取り出す
    cluster_id       = addon_info["clusterID"]
    ip_list         = addon_info["IP_list"]
    params          = addon_info["params"]
    node_password    = addon_info["node_password"]
    
    head_ip, os_type, n_computenode = \
        get_info (cluster_id = cluster_id, params = params)
    
    if (service_name == "slurm"):
        slurm_main (
            head_ip = head_ip,
            n_computenode = n_computenode,
            node_password = node_password,
            os_type = os_type   
        )
    
############
# get info #
############
def get_info (cluster_id, params):
    # Get headnode IP address & computenodes num
    head_ip  = "255.255.255.255"
    n_computenode = 0
    node_dict = params.get_node_info()
    disk_dict = params.get_disk_info()

    for zone, url in params.url_list.items():
        node_list = node_dict[zone]
        disk_list = list(disk_dict[zone].keys())
        if(len(node_list) != 0):
            for i in range(len(node_list)):
                print(cluster_id + ':' + node_list[i]["Tags"][0] + ' | ' + node_list[i]['Name'])
                if (cluster_id in node_list[i]["Tags"][0] and 'headnode' in node_list[i]['Name']):
                    head_ip = node_list[i]['Interfaces'][0]['IPAddress']
                    os_type = params.cluster_info_all[cluster_id]["clusterparams"]["server"][zone]["head"]["disk"][0]["os"]
                elif (cluster_id in node_list[i]["Tags"][0]):
                    n_computenode += 1
                else:
                    pass
        else:
            pass
    
    if head_ip == "255.255.255.255":
        try:
            raise ValueError (RED + "Failed to get IP address of head node")
        except:
            print ("Exit programm" + END)
            sys.exit ()
    return head_ip, os_type, n_computenode

if __name__ == '__main__':
    params = get_cluster_info()
    cluster_id = '290516'
    node_password = 'test'

    # Get headnode IP address & computenodes num
    head_ip  = "255.255.255.255"
    n_computenode = 0
    node_dict = params.get_node_info()
    disk_dict = params.get_disk_info()

    for zone, url in params.url_list.items():
        node_list = node_dict[zone]
        disk_list = list(disk_dict[zone].keys())
        if(len(node_list) != 0):
            for i in range(len(node_list)):
                print(cluster_id + ':' + node_list[i]["Tags"][0] + ' | ' + node_list[i]['Name'])
                if (cluster_id in node_list[i]["Tags"][0] and 'headnode' in node_list[i]['Name']):
                    headIp = node_list[i]['Interfaces'][0]['IPAddress']
                    os_type = params.cluster_info_all[cluster_id]["clusterparams"]["server"][zone]["head"]["disk"][0]["os"]
                elif (cluster_id in node_list[i]["Tags"][0]):
                    n_computenode += 1
                else:
                    pass
        else:
            pass

    # Read json file for gaglia configuration 
    json_addon_params = load_addon_params ()
    job_scheduler_setup(
        cluster_id = cluster_id,
        params = params,
        node_password = node_password,
        json_addon_params = json_addon_params,
        service_type="job_scheduler",
        service_name="slurm"
    )