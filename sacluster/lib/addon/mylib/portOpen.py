# クラスターの構成を取得してＩＰアドレスの割り振りの自動化
# 引数１：  クラスターID
# 引数２：  クラスター情報(関数)
# 引数３：  クラスターのパスワード

from ast import Pass
import string
import sys
import time
import logging
from paramiko import channel
import tqdm
import numpy as np
import os

# from sacluster.lib.addon.mylib.editHost import Password
os.chdir(os.path.dirname(os.path.abspath(__file__)))
common_path = os.path.abspath("../../..")

sys.path.append(common_path + "/lib/others")
from API_method import get, post, put, delete
sys.path.append(common_path + "/lib/auth")
from auth_func_pro import authentication_cli

#並列処理を行う
import asyncio
import paramiko 

def portOpen(clusterID, params, nodePassword, changeTarget, ports, protocols):

    # グローバルIPと計算機ノードの数を把握する
    IP_ADDRESS1  = "255.255.255.255"
    nComputenode = 0

    node_dict = params.get_node_info()
    disk_dict = params.get_disk_info()

    for zone, url in params.url_list.items():
        node_list = node_dict[zone]
        disk_list = list(disk_dict[zone].keys())
        if(len(node_list) != 0):
            for i in range(len(node_list)):
                # print(clusterID + ':' + node_list[i]["Tags"][0] + ' | ' + node_list[i]['Name'])
                if (clusterID in node_list[i]["Tags"][0] and 'headnode' in node_list[i]['Name']):
                    IP_ADDRESS1 = node_list[i]['Interfaces'][0]['IPAddress']
                elif (clusterID in node_list[i]["Tags"][0]):
                    nComputenode += 1
                else:
                    pass
        else:
            pass

    # ヘッドノードに対する操作と接続情報を与える
    if changeTarget == "HEAD" or changeTarget == "ALL":
        command = []
        for i, port in enumerate(ports):
            command.append('firewall-cmd --permanent --zone=trusted --add-port=' + str(port) + '/' + protocols[i]) 

        headInfo = {
            'IP_ADDRESS':IP_ADDRESS1,
            'PORT'      :22,
            'USER'      :'root',
            'PASSWORD'  :nodePassword
        }
        setupPortEth1_head(headInfo, command)

    if changeTarget == "COMP" or changeTarget == "ALL":
        for iComputenode in range(nComputenode):
            command = []
            for i, port in enumerate(ports):
                command.append('firewall-cmd --permanent --zone=trusted --add-port=' + str(port) + '/' + protocols[i])

            IP_ADDRESS2 = '192.168.100.' + str(iComputenode+1)
            compInfo = {
                'IP_ADDRESS':IP_ADDRESS2,
                'PORT'      :22,
                'USER'      :'root',
                'PASSWORD'  :nodePassword
            }
            setupPortEth1_comp(headInfo, compInfo, command)



def setupPortEth1_head(headInfo, command):
    #管理ノードに接続
    headnode = paramiko.SSHClient()
    headnode.set_missing_host_key_policy(paramiko.WarningPolicy())

    print("hostnode connecting...")
    headnode.connect(hostname=headInfo['IP_ADDRESS'], port=headInfo['PORT'], username=headInfo['USER'], password=headInfo['PASSWORD'])
    print('hostnode connected')

    #コマンド実行
    for i, com in enumerate(command):
        stdin, stdout, stderr = headnode.exec_command(com)
        time.sleep(1)
        out = stdout.read().decode()
        print('head_stdout = %s' % out)
    
    headnode.close()



def setupPortEth1_comp(headInfo, compInfo, command):

    head = (headInfo['IP_ADDRESS'], headInfo['PORT'])
    compute = (compInfo['IP_ADDRESS'], compInfo['PORT'])

    headnode = paramiko.SSHClient()
    headnode.set_missing_host_key_policy(paramiko.WarningPolicy())
    headnode.connect(hostname=headInfo['IP_ADDRESS'], port=headInfo['PORT'], username=headInfo['USER'], password=headInfo['PASSWORD'])
    transport1 = headnode.get_transport()
    channel1 = transport1.open_channel("direct-tcpip", compute, head)
    
    computenode = paramiko.SSHClient()
    computenode.set_missing_host_key_policy(paramiko.WarningPolicy())

    print("compurenode connecting...")
    computenode.connect(hostname=compInfo['IP_ADDRESS'],username=compInfo['USER'],password=compInfo['PASSWORD'],sock=channel1)
    print('computenode connected')

    #コマンド実行
    for i, com in enumerate(command):
        (stdin, stdout, stderr) = computenode.exec_command(com)
        time.sleep(1)
        out = stdout.read().decode()
        print('comp_stdout = %s' % out)

    headnode.close()
    computenode.close()



if __name__ == '__main__':
    ports           = [4000, 4001]
    protocols       = ['udp', 'tcp']
    changeTarget    = "HEAD"        # "HEAD", "COMP", "ALL"
    portOpen(clusterID, params, nodePassword, changeTarget, ports, protocols)

