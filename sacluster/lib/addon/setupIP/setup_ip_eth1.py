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

# from sacluster.lib.addon.mylib.editHost import password
os.chdir(os.path.dirname(os.path.abspath(__file__)))
common_path = os.path.abspath("../../..")

sys.path.append(common_path + "/lib/others")
from API_method import get, post, put, delete
sys.path.append(common_path + "/lib/auth")
from auth_func_pro import authentication_cli

import paramiko 

def setup_ip_eth1(cluster_id, params, node_password):

    # グローバルIPと計算機ノードの数を把握する
    ipaddress1  = "255.255.255.255"
    n_computenode = 0

    node_dict = params.get_node_info()
    disk_dict = params.get_disk_info()

    for zone, url in params.url_list.items():
        node_list = node_dict[zone]
        disk_list = list(disk_dict[zone].keys())
        if(len(node_list) != 0):
            for i in range(len(node_list)):
                if (len(node_list[i]["Tags"]) < 2):
                    continue
                # print(cluster_id + ':' + node_list[i]["Tags"][0] + ' | ' + node_list[i]['Name'])
                if (cluster_id in node_list[i]["Tags"][0] and 'headnode' in node_list[i]['Name']):
                    ipaddress1 = node_list[i]['Interfaces'][0]['IPAddress']
                elif (cluster_id in node_list[i]["Tags"][0]):
                    n_computenode += 1
                else:
                    pass
        else:
            pass

    # ヘッドノードに対する操作と接続情報を与える
    command = [
        'nmcli c add type ethernet ifname eth1 con-name "System eth1"',
        'nmcli c modify "System eth1" ipv4.method manual ipv4.addresses 192.168.100.254/24',
        'nmcli c modify "System eth1" connection.autoconnect yes',
        'nmcli c reload "System eth1"'
    ]
    head_info = {
        'ipaddress':ipaddress1,
        'port'      :22,
        'user'      :'root',
        'password'  :node_password
    }
    #setup_ip_eth1_head(head_info, command)

    for i_computenode in range(n_computenode):
        command = [
            'nmcli c mod "System eth1" ipv4.method manual ipv4.addresses 192.168.200.' + str(i_computenode+1) + '/24',
            'nmcli c mod "System eth1" connection.autoconnect yes',
            'nmcli c down "System eth1" && nmcli c up "System eth1"'
        ]
        ipaddress2 = '192.168.100.' + str(i_computenode+1)
        comp_info = {
            'ipaddress':ipaddress2,
            'port'      :22,
            'user'      :'root',
            'password'  :node_password
        }
        setup_ip_eth1_comp(head_info, comp_info, command)



def setup_ip_eth1_head(head_info, command):
    #管理ノードに接続
    headnode = paramiko.SSHClient()
    headnode.set_missing_host_key_policy(paramiko.WarningPolicy())

    print("hostnode connecting...")
    headnode.connect(hostname=head_info['ipaddress'], port=head_info['port'], username=head_info['user'], password=head_info['password'])
    print('hostnode connected')

    #コマンド実行
    for i, com in enumerate(command):
        stdin, stdout, stderr = headnode.exec_command(com)
        time.sleep(1)
        out = stdout.read().decode()
        print('head_stdout = %s' % out)
    
    headnode.close()



def setup_ip_eth1_comp(head_info, comp_info, command):

    head = (head_info['ipaddress'], head_info['port'])
    compute = (comp_info['ipaddress'], comp_info['port'])

    headnode = paramiko.SSHClient()
    headnode.set_missing_host_key_policy(paramiko.WarningPolicy())
    headnode.connect(hostname=head_info['ipaddress'], port=head_info['port'], username=head_info['user'], password=head_info['password'])
    transport1 = headnode.get_transport()
    channel1 = transport1.open_channel(kind="direct-tcpip", dest_addr=compute, src_addr=head)
    
    computenode = paramiko.SSHClient()
    computenode.set_missing_host_key_policy(paramiko.WarningPolicy())

    print("computenode connecting...")
    computenode.connect(hostname=comp_info['ipaddress'],username=comp_info['user'],password=comp_info['password'],sock=channel1, auth_timeout=300)
    print('computenode connected')

    #コマンド実行
    for i, com in enumerate(command):
        (stdin, stdout, stderr) = computenode.exec_command(com)
        time.sleep(1)
        out = stdout.read().decode()
        print('comp_stdout = %s' % out)

    computenode.close()
    headnode.close()



if __name__ == '__main__':
    setup_ip_eth1()

