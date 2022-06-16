import json
import sys
import os

# User defined Library
os.chdir(os.path.dirname(os.path.abspath(__file__)))
common_path = os.path.abspath("../../..")
fileName = common_path + '\\lib\\addon\\setupJobScheduler\\slurm.json'

# Changing standard output color for exception error
RED = '\033[31m'
END = '\033[0m'

sys.path.append(common_path + "/lib/addon/mylib")
from load_addon_params import load_addon_params
from get_cluster_info import get_cluster_info

sys.path.append(common_path + "/lib/addon/setupJobScheduler")
from munge_setup import munge_setup 
from slurm_setup import slurm_setup

#################
# Main Programm #
#################
def slurm_main (head_ip, n_computenode, node_password, json_addon_params, os_type):
   # Read json file for gaglia configuration 
    try:
        json_open = open(fileName, 'r')
    except OSError as err:
        print (RED + "Fialed to open file: {}" .format(fileName))
        print ("Error type: {}" .format(err))
        print ("Exit rogramm" + END)
        sys.exit ()
    try:
        cmd_slurm = json.load(json_open)
    except json.JSONDecodeError as err:
        print (RED + "Fialed to decode JSON file: {}" .format(fileName))
        print ("Error type: {}" .format(err))
        print ("Exit programm" + END)
        sys.exit ()
   
    munge_setup (
        head_ip = head_ip,
        n_computenode = n_computenode,
        node_password = node_password,
        json_addon_params = json_addon_params,
        os_type = os_type,
        cmd_slurm = cmd_slurm
    )

    slurm_setup ()

if __name__ == '__main__':
    params = get_cluster_info()
    cluster_id = '615003'
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
                    head_ip = node_list[i]['Interfaces'][0]['IPAddress']
                    os_type = params.cluster_info_all[cluster_id]["clusterparams"]["server"][zone]["head"]["disk"][0]["os"]
                elif (cluster_id in node_list[i]["Tags"][0]):
                    n_computenode += 1
                else:
                    pass
        else:
            pass

    # Read json file for gaglia configuration 
    json_addon_params = load_addon_params ()
    slurm_main (
        head_ip = head_ip,
        n_computenode = n_computenode,
        node_password = node_password,
        json_addon_params = json_addon_params,
        os_type = os_type
    )