import os
import sys
import time
import logging
import ast

from numpy.lib.shape_base import tile

logger = logging.getLogger("sacluster").getChild(os.path.basename(__file__))

from os.path import expanduser
home_path = expanduser("~") + "/sacluster"
os.makedirs(home_path, exist_ok = True)

os.chdir(os.path.dirname(os.path.abspath(__file__)))
common_path = os.path.abspath("../../..")

sys.path.append(common_path + "/lib/others")
from API_method import get, post, put, delete
import get_params
from info_print import printout

sys.path.append(common_path + "/lib/auth")
from auth_func_pro import authentication_cli

sys.path.append(common_path + "/lib/def_conf")
from load_external_data import external_data

sys.path.append (common_path + "/lib/addon/mylib")
from get_cluster_info import get_cluster_info
from load_addon_params    import load_addon_params

import paramiko 
from tqdm import tqdm

def pack_install(cluster_id, params, node_password, json_addon_params, service_type, service_name):
    
    ipaddress1  = "255.255.255.255"
    n_compute = 0
    target_zone = " "

    node_dict = params.get_node_info()
    disk_dict = params.get_disk_info()

    for zone, url in params.url_list.items():
        node_list = node_dict[zone]
        disk_list = list(disk_dict[zone].keys())        

        if(len(node_list) != 0):
            for i in range(len(node_list)):
                desp = node_list[i]["Description"]
                if(cluster_id in node_list[i]["Tags"][0]):
                    if(node_list[i]["Interfaces"][0]["IPAddress"] != None):
                        ipaddress1 = node_list[i]["Interfaces"][0]["IPAddress"]
                        target_zone = node_list[i]["Zone"]["Name"]

                        OSType      = disk_dict[zone][disk_list[i]]["SourceArchive"]["Name"]

                        cmd_head = json_addon_params['MiddleWare'][service_type][service_name]['Packege'][OSType]['Head']
                        cmd_compute = json_addon_params['MiddleWare'][service_type][service_name]['Packege'][OSType]['Compute']

                        """
                        if("CentOS" in params.cluster_info_all[cluster_id]["clusterparams"]["server"][target_zone]["head"]["disk"][0]["os"]):
                            cmd_head = "hostname" #jsonファイルを読み込む
                            #cmd_head = jsn["OS"] + jsn[] +jsn[]
                            cmd_compute = "hostname -I" #jsonファイルを読み込む

                        elif("Ubuntu" in params.cluster_info_all[cluster_id]["clusterparams"]["server"][target_zone]["head"]["disk"][0]["os"]):
                            cmd_head =  "hostname -I"
                            cmd_compute =  "hostname"
                           
                        else:
                            pass

                        """
                    else:
                        n_compute +=1
                
                else:
                    pass

        else:
            pass

    ssh_connect(ipaddress1,node_password,n_compute,cmd_head,cmd_compute)
    

def ssh_connect(ipaddress1,node_password,n_compute,cmd_head,cmd_compute):
    #管理ノード
    port1 = 22
    user1 = 'root'
    
    #管理ノードに接続
    headnode = paramiko.SSHClient()
    headnode.set_missing_host_key_policy(paramiko.WarningPolicy())

    print("hostnode connecting...")
    headnode.connect(hostname=ipaddress1, port=port1, username=user1, password=node_password)
    print('hostnode connected')

    for CMD in tqdm(cmd_head):
        stdin, stdout, stderr = headnode.exec_command(CMD)
        time.sleep(1)
        hostname = stdout.read().decode()
        #print('hostname_head = %s' % hostname)

    for i in range(1, n_compute+1):
        #管理->計算ノード
        #計算ノード
        ipaddress2 = '192.168.100.' + str(i)
        port2 = 22
        user2 = 'root'

        head = (ipaddress1,port1)
        compute = (ipaddress2, port2)
        transport1 = headnode.get_transport()
        channel1 = transport1.open_channel("direct-tcpip", compute, head)
        computenode = paramiko.SSHClient()
        computenode.set_missing_host_key_policy(paramiko.WarningPolicy())
        print("compurenode connecting...")
        computenode.connect(hostname=ipaddress2,username=user2,password=node_password,sock=channel1)
        print('computenode connected')

        for CMD in tqdm(cmd_compute):
            stdin, stdout, stderr = computenode.exec_command(CMD)
            time.sleep(1)
            hostname = stdout.read().decode()
            #print('hostname_compute01 = %s' % hostname)

    headnode.close()
    computenode.close()
    del headnode, stdin, stdout, stderr

if __name__ == '__main__':
    params = get_cluster_info ()
    json_addon_params = load_addon_params ()
    pack_install (cluster_id = '108477',node_password = 'test', params=params ,json_addon_params = json_addon_params, service_type="Monitor", service_name="Ganglia")
