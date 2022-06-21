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
from API_method         import get, post, put, delete
sys.path.append(common_path + "/lib/auth")
from auth_func_pro      import authentication_cli
sys.path.append (common_path + "/lib/addon/mylib")
from get_cluster_info   import get_cluster_info
from load_addon_params  import load_addon_params


#並列処理を行う
import asyncio
import paramiko 

def port_open(cls_bil, ext_info, addon_info, service_type, service_name):

    # 今回の処理に必要な変数のみを取り出す
    cluster_id        = addon_info["clusterID"]
    IP_list           = addon_info["IP_list"]
    params            = addon_info["params"]
    node_password     = addon_info["node_password"]
    json_addon_params = addon_info["json_addon_params"]

    # グローバルIPと計算機ノードの数を把握する
    ipaddress1  = "255.255.255.255"
    n_computenode = 0
    os_type       = ""


    node_dict = params.get_node_info()
    disk_dict = params.get_disk_info()

    for zone, url in params.url_list.items():
        node_list = node_dict[zone]
        disk_list = list(disk_dict[zone].keys())
        if(len(node_list) != 0):
            for i in range(len(node_list)):
                # print(cluster_id + ':' + node_list[i]["Tags"][0] + ' | ' + node_list[i]['Name'])
                if (cluster_id in node_list[i]["Tags"][0] and 'headnode' in node_list[i]['Name']):
                    ipaddress1 = node_list[i]['Interfaces'][0]['IPAddress']
                    os_type      = disk_dict[zone][disk_list[i]]["SourceArchive"]["Name"]
                elif (cluster_id in node_list[i]["Tags"][0]):
                    n_computenode += 1
                else:
                    pass
        else:
            pass

    # ヘッドノードに対する操作と接続情報を与える
    command = json_addon_params["Common"]["Firewall"][service_type][service_name][os_type]["Head"]

    head_info = {
        'ipaddress':ipaddress1,
        'port'      :22,
        'user'      :'root',
        'password'  :node_password
    }
    setup_port__head(head_info, command)

    for IP in IP_list["front"]:
        command = json_addon_params["Common"]["Firewall"][service_type][service_name][os_type]["Compute"]

        ipaddress2 = IP
        compute_info = {
            'ipaddress':ipaddress2,
            'port'      :22,
            'user'      :'root',
            'password'  :node_password
        }
        setup_port__comp(head_info, compute_info, command)



def setup_port__head(head_info, command):
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



def setup_port__comp(head_info, compute_info, command):

    head = (head_info['ipaddress'], head_info['port'])
    compute = (compute_info['ipaddress'], compute_info['port'])

    headnode = paramiko.SSHClient()
    headnode.set_missing_host_key_policy(paramiko.WarningPolicy())
    headnode.connect(hostname=head_info['ipaddress'], port=head_info['port'], username=head_info['user'], password=head_info['password'])
    transport1 = headnode.get_transport()
    channel1 = transport1.open_channel("direct-tcpip", compute, head)
    
    computenode = paramiko.SSHClient()
    computenode.set_missing_host_key_policy(paramiko.WarningPolicy())

    print("compurenode connecting...")
    computenode.connect(hostname=compute_info['ipaddress'],username=compute_info['user'],password=compute_info['password'],sock=channel1)
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

    port_open       (cls_bil, ext_info, addon_info, service_type="Proxy", service_name="squid")
    port_open       (cls_bil, ext_info, addon_info, service_type="Monitor", service_name="Ganglia")
