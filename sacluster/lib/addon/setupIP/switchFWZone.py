
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

sys.path.append(common_path + "/lib/addon/mylib")
from getClusterInfo import getClusterInfo

sys.path.append(common_path + "/lib/def_conf")
from load_external_data import external_data

import paramiko 

#ローカルのネットワークのFireWallのゾーンを指定したゾーンに変更する
def switchFWZone(clusterID, params,nodePassword):
    
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

                        #管理ノード
                        IP_ADDRESS1 = node_list[i]["Interfaces"][0]["IPAddress"]
                        PORT1 = 22
                        USER1 = 'root'
                        PASSWORD1 = nodePassword
                        CMD1 =[
                            'firewall-cmd --zone=trusted --change-interface=eth1 --permanent',
                            'firewall-cmd --reload'
                        ]
                        
                    
                        headnode = paramiko.SSHClient()
                        headnode.set_missing_host_key_policy(paramiko.WarningPolicy())

                        print("hostnode connecting...")
                        headnode.connect(hostname=IP_ADDRESS1, port=PORT1, username=USER1, password=PASSWORD1)
                        print('hostnode connected')

                        #コマンド実行
                        for i, CMD in enumerate(CMD1):
                            stdin, stdout, stderr = headnode.exec_command(CMD)
                            time.sleep(1)
                            hostname = stdout.read().decode()
                            print('hostname_head = %s' % hostname)

                    elif (node_list[i]["Interfaces"][0]["IPAddress"] == None):
                        if (node_list[i]["Interfaces"][0]["UserIPAddress"] != None):

                            #管理->計算ノード
                            #計算ノード

                            IP_ADDRESS2 = node_list[i]["Interfaces"][0]["UserIPAddress"]
                            PORT2 = 22
                            USER2 = 'root'
                            PASSWORD2 = nodePassword
                            CMD2 = [
                                'firewall-cmd --zone=trusted --change-interface=eth0 --permanent',
                                'firewall-cmd --zone=trusted --change-interface=eth1 --permanent',
                                'firewall-cmd --reload'
                            ]
                            
                            head = (IP_ADDRESS1,PORT1)
                            compute = (IP_ADDRESS2, PORT2)
                            transport1 = headnode.get_transport()
                            channel1 = transport1.open_channel("direct-tcpip", compute, head)
                            computenode = paramiko.SSHClient()
                            computenode.set_missing_host_key_policy(paramiko.WarningPolicy())

                            print("compurenode connecting...")
                            computenode.connect(hostname=IP_ADDRESS2,username=USER2,password=PASSWORD2,sock=channel1,auth_timeout=3600)
                            print('computenode connected')

                            #コマンド実行
                            for i, CMD in enumerate(CMD2):
                                stdin, stdout, stderr = computenode.exec_command(CMD)
                                time.sleep(1)
                                hostname = stdout.read().decode()
                                print('hostname_compute = %s' % hostname)

                        else:
                            pass
        else:
            pass

    #コネクションを閉じる
    headnode.close()
    computenode.close()
    del headnode, computenode, stdin, stdout, stderr

if __name__ == '__main__':
    switchFWZone (clusterID = '285208', nodePassword = 'test')
