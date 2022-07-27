import sys
import logging
import os

# User defined Library
os.chdir(os.path.dirname(os.path.abspath(__file__)))
common_path = os.path.abspath("../../..")
fileName = common_path + '/lib/addon/setupMpi/mpich.json'

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
def setup_job_scheduler (addon_info, f, info_list, job_scheduler_info):
    # 今回の処理に必要な変数のみを取り出す
    cluster_id       = addon_info["clusterID"]
    ip_list         = addon_info["IP_list"]
    params          = addon_info["params"]
    node_password    = addon_info["node_password"]
    
    head_ip, os_type, n_computenode = \
        get_info (cluster_id = cluster_id, params = params)
    
    if (job_scheduler_info["index"] == True):
        if (job_scheduler_info["type"] == "slurm"):
            slurm_main (
                head_ip = head_ip,
                n_computenode = n_computenode,
                node_password = node_password,
                os_type = os_type,
                ip_list = ip_list,
                cluster_id = cluster_id   
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
                if (len(node_list[i]["Tags"]) != 0):
                #print(cluster_id + ':' + node_list[i]["Tags"][0] + ' | ' + node_list[i]['Name'])
                    if (cluster_id in node_list[i]["Tags"][0] and 'head' in node_list[i]['Name']):
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
    params              = get_cluster_info ()
    json_addon_params   = load_addon_params ()

    cls_bil  = []
    ext_info = []
    info_list = [1,0,0,1]
    f = []
    
    addon_info = {
        "clusterID"         : "739512",                 # !!! 任意のクラスターIDに変更 !!!
        "IP_list"           :{                          # コンピュートノードの数に合わせて変更
            "front" : ['192.168.2.1', '192.168.2.2'],
            "back"  : ['192.169.2.1', '192.169.2.2']
        },
        "Job_scheduler":{
            "index": True,
            "type" : "slurm"
        },
        "params"            : params,
        "json_addon_params" : json_addon_params,
        "node_password"     : "test"                    # 設定したパスワードを入力
    }

    setup_job_scheduler (addon_info, f, info_list, job_scheduler_info = addon_info["Job_scheduler"])