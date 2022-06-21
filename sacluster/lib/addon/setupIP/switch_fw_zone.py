
import sys
import time
import logging
import os
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
import json

#ローカルのネットワークのFireWallのゾーンを指定したゾーンに変更する
def switch_fw_zone(cls_bil, ext_info, addon_info):

    # 今回の処理に必要な変数のみを取り出す
    clusterID       = addon_info["clusterID"]
    IP_list         = addon_info["IP_list"]
    params          = addon_info["params"]
    nodePassword    = addon_info["node_password"]
    jsonAddonParams = addon_info["json_addon_params"]

    IPADDRESS1  = "255.255.255.255"
    computenum = 0
    ZONE = " "

    node_dict = params.get_node_info()
    disk_dict = params.get_disk_info()

    for zone, url in params.url_list.items():
        node_list = node_dict[zone]
        disk_list = list(disk_dict[zone].keys())        

        if(len(node_list) != 0):
            for i in range(len(node_list)):
                desp = node_list[i]["Description"]
                if(clusterID in node_list[i]["Tags"][0]):
                    if(node_list[i]["Interfaces"][0]["IPAddress"] != None):
                        IPADDRESS1 = node_list[i]["Interfaces"][0]["IPAddress"]
                        ZONE = node_list[i]["Zone"]["Name"]

                        OSType      = disk_dict[zone][disk_list[i]]["SourceArchive"]["Name"]

                        HEAD_CMD = jsonAddonParams['Common']['Firewall']['Zone'][OSType]['Head']
                        COMPUTE_CMD = jsonAddonParams['Common']['Firewall']['Zone'][OSType]['Compute']
                        
                    else:
                        computenum +=1
                
                else:
                    pass

        else:
            pass

    ssh_connect(IPADDRESS1,nodePassword,computenum,IP_list,HEAD_CMD,COMPUTE_CMD)
    

def ssh_connect(IPADDRESS1,nodePassword,computenum,IP_list,HEAD_CMD,COMPUTE_CMD):
    #管理ノード
    PORT1 = 22
    USER1 = 'root'
    
    #管理ノードに接続
    headnode = paramiko.SSHClient()
    headnode.set_missing_host_key_policy(paramiko.WarningPolicy())

    print("hostnode connecting...")
    headnode.connect(hostname=IPADDRESS1, port=PORT1, username=USER1, password=nodePassword)
    print('hostnode connected')

    for i, CMD in enumerate(HEAD_CMD):
        stdin, stdout, stderr = headnode.exec_command(CMD)
        time.sleep(1)
        hostname = stdout.read().decode()
        print('hostname_head = %s' % hostname)

    for IP in IP_list["front"]:
        #管理->計算ノード
        #計算ノード
        IPADDRESS2 = IP
        PORT2 = 22
        USER2 = 'root'

        head = (IPADDRESS1,PORT1)
        compute = (IPADDRESS2, PORT2)
        transport1 = headnode.get_transport()
        channel1 = transport1.open_channel("direct-tcpip", compute, head)
        computenode = paramiko.SSHClient()
        computenode.set_missing_host_key_policy(paramiko.WarningPolicy())
        print("compurenode connecting...")
        computenode.connect(hostname=IPADDRESS2,username=USER2,password=nodePassword,sock=channel1, auth_timeout=300)
        print('computenode connected')

        for i, CMD in enumerate(COMPUTE_CMD):
            stdin, stdout, stderr = computenode.exec_command(CMD)
            time.sleep(1)
            hostname = stdout.read().decode()
            print('hostname_compute = %s' % hostname)

    headnode.close()
    computenode.close()
    del headnode, stdin, stdout, stderr


if __name__ == '__main__':
    params              = get_cluster_info ()
    json_addon_params   = load_addon_params ()

    cls_bil  = []
    ext_info = []

    addon_info = {
        "clusterID"         : "849936",                 # !!! 任意のクラスターIDに変更 !!!
        "IP_list"           :{                          # コンピュートノードの数に合わせて変更
            "front" : ['192.168.4.1', '192.168.4.2'],
            "back"  : ['192.169.4.1', '192.169.4.2']
        },
        "params"            : params,
        "json_addon_params" : json_addon_params,
        "node_password"     : "test"                    # 設定したパスワードを入力
    }

    switch_fw_zone  (cls_bil, ext_info, addon_info)