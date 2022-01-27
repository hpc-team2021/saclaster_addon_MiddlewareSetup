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

common_path = "../.."
os.chdir(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(common_path + "/lib/others")
from API_method import get, post, put, delete
import get_params
import get_cluster_id
from info_print import printout

sys.path.append(common_path + "/lib/auth")
from auth_func_pro import authentication_cli

sys.path.append(common_path + "/lib/def_conf")
from load_external_data import external_data

sys.path.append(common_path + "/lib/cls/start")
from start_main import start_main

import paramiko 

def packInstall2(argv):
     # 認証周り
    auth_res = authentication_cli(fp = '', info_list = [1,0,0,0], api_index = True)
    
    #set url
    url_list = {}
    head_zone = 'is1b'
    zone      = 'is1b'
    zone_list = ['is1b']
    for zone in zone_list:
        url_list[zone] = "https://secure.sakura.ad.jp/cloud/zone/"+ zone +"/api/cloud/1.1"
    head_url = "https://secure.sakura.ad.jp/cloud/zone/"+ head_zone +"/api/cloud/1.1"
    sub_url = ["/server","/disk","/switch","/interface","/bridge","/tag","/appliance","/power","/ipaddress"]

    get_cluster_serever_info    = get(url_list[zone] + sub_url[0], auth_res)
    get_cluster_disk_info       = get(url_list[zone] + sub_url[1], auth_res)
    get_cluster_switch_info     = get(url_list[zone] + sub_url[2], auth_res)
    get_cluster_interface_info  = get(url_list[zone] + sub_url[3], auth_res)
    get_cluster_bridge_info     = get(url_list[zone] + sub_url[4], auth_res)
    get_cluster_tag_info        = get(url_list[zone] + sub_url[5], auth_res)
    get_cluster_appliance_info  = get(url_list[zone] + sub_url[6], auth_res)
    get_cluster_power_info      = get(url_list[zone] + sub_url[7], auth_res)
    get_cluster_ipaddress_info    = get(url_list[zone] + sub_url[8], auth_res)

     # 同一IDのホスト名のリストをとってくる
    ext_info = external_data(auth_res, info_list = [1,0,0,0], fp = '')
    params = get_params.get_params(ext_info, auth_res, info_list = [1,0,0,0], f = '', api_index = True)
    params()
    node_dict = params.get_node_info()
    disk_dict = params.get_disk_info()

    #print(params.url_list.items())
    

    print('##################################')
    print('######## ゾーン情報の表示 ########')
    for zone, url in params.url_list.items():
        node_list = node_dict[zone]
        disk_list = list(disk_dict[zone].keys())

        if(len(node_list) != 0):
            for i in range(len(node_list)):
                #print(node_list[i]["Tags"][0],node_list[i]["Interfaces"][0]["IPAddress"],node_list[i]["Interfaces"][0]["UserIPAddress"])

                desp = node_list[i]["Description"]
                #クラスタID有り
                
                if (len(node_list[i]["Tags"]) > 0 ):
                    if(node_list[i]["Interfaces"][0]["IPAddress"]!= None):
                        print('zone: ' + zone + ' | ' + node_list[i]["Tags"][0]   + ' | IPAddress: ' + node_list[i]["Interfaces"][0]["IPAddress"] + ' | nodeName: ' + node_list[i]['Name'])
                    elif (node_list[i]["Interfaces"][0]["IPAddress"] == None):
                        if (node_list[i]["Interfaces"][0]["UserIPAddress"] == None):
                            print('zone: ' + zone + ' | ' + node_list[i]["Tags"][0]   + ' | IPAddress: ' + 'NULL' + ' | nodeName: ' + node_list[i]['Name'])
                        else:
                            print('zone: ' + zone + ' | ' + node_list[i]["Tags"][0]   + ' | IPAddress: ' + node_list[i]["Interfaces"][0]["UserIPAddress"] + ' | nodeName: ' + node_list[i]['Name'])
                            
        
        else:
            pass

    print('##################################')
    print('##################################')


    #操作したいクラスタはあらかじめ起動させる必要があるので注意

    print('インストールをさせたいソフトとIDを選んでください >>')

    #hostnameを取るように想定しているので、現状はhostnameを入力してください
    install = input('install: ')
    clusterID = input('cluster ID: ')

    install.split('install: ')

    CMD = install

    for zone, url in params.url_list.items():
        node_list = node_dict[zone]
        disk_list = list(disk_dict[zone].keys())
        if(len(node_list) != 0):

            IP_ADDRESS1 = node_list[i]["Interfaces"][0]["IPAddress"]
            PORT1 = 22
            USER1 = 'root'
            PASSWORD1 = 'demo01pw'
            
            for i in range(len(node_list)):
            #for i in range(0,1,1)+range(1,3,1):
                desp = node_list[i]["Description"]
                
                if(clusterID in node_list[i]["Tags"][0]):
                    if(node_list[i]["Interfaces"][0]["IPAddress"]!= None):
                        #管理ノード
                      
                        headnode = paramiko.SSHClient()
                        headnode.set_missing_host_key_policy(paramiko.WarningPolicy())

                        print("hostnode connecting...")
                        headnode.connect(hostname=IP_ADDRESS1, port=PORT1, username=USER1, password=PASSWORD1)
                        print('hostnode connected')

                        #コマンド実行
                        stdin, stdout, stderr = headnode.exec_command(CMD)
                        time.sleep(1)
                        hostname = stdout.read().decode()
                        print('hostname_head = %s' % hostname)

                        print(node_list[i]["Tags"][0],node_list[i]["Interfaces"][0]["IPAddress"],node_list[i]["Interfaces"][0]["UserIPAddress"])

                        headnode.close()

                    elif (node_list[i]["Interfaces"][0]["IPAddress"] == None):
                        if (node_list[i]["Interfaces"][0]["UserIPAddress"] == None):
                            print('IPAddress: ' + 'NULL' + ' | nodeName: ' + node_list[i]['Name'])

                        else:
                            #管理->計算ノード
                            #計算ノード
                            print('COMPUTE:' + node_list[i]["Tags"][0],node_list[i]["Interfaces"][0]["IPAddress"],node_list[i]["Interfaces"][0]["UserIPAddress"])

                            IP_ADDRESS2 = node_list[i]["Interfaces"][0]["UserIPAddress"]
                            PORT2 = 22
                            USER2 = 'root'
                            PASSWORD2 = 'demo01pw'

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
                            stdin, stdout, stderr = computenode.exec_command(CMD)
                            time.sleep(1)
                            hostname = stdout.read().decode()
                            print('hostname_compute = %s' % hostname)

                            computenode.close()
        else:
            pass

    #コネクションを閉じる
   # headnode.close()
   # computenode.close()
    del headnode, computenode, stdin, stdout, stderr
        
if __name__ == '__main__':
   sys.exit(packInstall2(sys.argv))