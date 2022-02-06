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

import paramiko 
import getpass
import json

#with open('C:\pg\population.json') as f:
   # jsn = json.load(f)


def packInstall(clusterID,params,nodePassword):

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
                        
                        if("CentOS" in params.cluster_info_all[clusterID]["clusterparams"]["server"][ZONE]["head"]["disk"][0]["os"]):
                            HEAD_CMD = "hostname" #jsonファイルを読み込む
                            #HEAD_CMD = jsn["OS"] + jsn[] +jsn[]
                            COMPUTE_CMD = "hostname -I" #jsonファイルを読み込む

                        elif("Ubuntu" in params.cluster_info_all[clusterID]["clusterparams"]["server"][ZONE]["head"]["disk"][0]["os"]):
                            HEAD_CMD =  "hostname -I"
                            COMPUTE_CMD =  "hostname"
                           
                        else:
                            pass

                    else:
                        computenum +=1
                
                else:
                    pass

        else:
            pass

    ssh_connect(IPADDRESS1,nodePassword,computenum,HEAD_CMD,COMPUTE_CMD)
    

def ssh_connect(IPADDRESS1,nodePassword,computenum,HEAD_CMD,COMPUTE_CMD):
    #管理ノード
    PORT1 = 22
    USER1 = 'root'
    
    #管理ノードに接続
    headnode = paramiko.SSHClient()
    headnode.set_missing_host_key_policy(paramiko.WarningPolicy())

    print("hostnode connecting...")
    headnode.connect(hostname=IPADDRESS1, port=PORT1, username=USER1, password=nodePassword)
    print('hostnode connected')

    stdin, stdout, stderr = headnode.exec_command(HEAD_CMD)
    time.sleep(1)
    hostname = stdout.read().decode()
    print('hostname_head = %s' % hostname)

    for i in range(1, computenum+1):
        #管理->計算ノード
        #計算ノード
        IPADDRESS2 = '192.168.100.' + str(i)
        PORT2 = 22
        USER2 = 'root'

        head = (IPADDRESS1,PORT1)
        compute = (IPADDRESS2, PORT2)
        transport1 = headnode.get_transport()
        channel1 = transport1.open_channel("direct-tcpip", compute, head)
        computenode = paramiko.SSHClient()
        computenode.set_missing_host_key_policy(paramiko.WarningPolicy())
        print("compurenode connecting...")
        computenode.connect(hostname=IPADDRESS2,username=USER2,password=nodePassword,sock=channel1)
        print('computenode connected')
        
        stdin, stdout, stderr = computenode.exec_command(COMPUTE_CMD)
        time.sleep(1)
        hostname = stdout.read().decode()
        print('hostname_compute01 = %s' % hostname)

    headnode.close()
    computenode.close()
    del headnode, stdin, stdout, stderr

if __name__ == '__main__':
    packInstall (clusterID = '285208', nodePassword = 'test')
