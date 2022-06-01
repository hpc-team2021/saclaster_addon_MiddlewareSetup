# プロキシサーバに
# 引数１：  クラスターID
# 引数２：  クラスター情報(関数)

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
sys.path.append(common_path + "/lib/addon/mylib")
from get_cluster_info     import get_cluster_info
from pack_install    import pack_install
from daemon_start    import daemon_start

#並列処理を行う
import asyncio
import paramiko 

def proxy_setup(clusterID, params, nodePassword, jsonAddonParams, serviceType, serviceName):

    # グローバルIPと計算機ノードの数を把握する
    IP_ADDRESS1  = "255.255.255.255"
    nComputenode = 0
    OSType       = ""

    packInstall(clusterID, params, nodePassword, jsonAddonParams, serviceType, serviceName)

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
                    OSType      = disk_dict[zone][disk_list[i]]["SourceArchive"]["Name"]
                elif (clusterID in node_list[i]["Tags"][0]):
                    nComputenode += 1
                else:
                    pass
        else:
            pass

    headInfo = {
        'IP_ADDRESS':IP_ADDRESS1,
        'PORT'      :22,
        'USER'      :'root',
        'PASSWORD'  :nodePassword
    }
    command = [
        'echo "acl mynetwork src 192.168.100.0/24"              >> /etc/squid/squid.conf',
        'echo "http_access allow mynetwork"                     >> /etc/squid/squid.conf',
        'echo "forwarded_for off"                               >> /etc/squid/squid.conf',
        'echo "request_header_access X-Forwarded-For deny all"  >> /etc/squid/squid.conf',
        'echo "request_header_access Via deny all"              >> /etc/squid/squid.conf',
        'echo "request_header_access Cache-Control deny all"    >> /etc/squid/squid.conf',
        'htpasswd -b -c /etc/squid/.htpasswd user1 test',
    ]
    setupProxy_head(headInfo, command)
    daemonStart (
        addonJson    = jsonAddonParams, 
        headIp       = IP_ADDRESS1, 
        targetIp     = IP_ADDRESS1, 
        nodePassword = nodePassword, 
        serviceType  = serviceType, 
        serviceName  = serviceName, 
        osType       = OSType
    )

    # コメントアウトした部分はdeamonStart()を実行したらいいんだけど...開発待ち

    for iComputenode in range(nComputenode):
        command = [
            'echo "export http_proxy=http://user1:test@192.168.100.254:3128" >> /root/.bashrc',
            'echo "export https_proxy=http://user1:test@192.168.100.254:3128" >> /root/.bashrc',
            'source .bashrc'
        ]
        IP_ADDRESS2 = '192.168.100.' + str(iComputenode+1)
        compInfo = {
            'IP_ADDRESS':IP_ADDRESS2,
            'PORT'      :22,
            'USER'      :'root',
            'PASSWORD'  :nodePassword
        }
        setupProxy_comp(headInfo, compInfo, command)
        daemonStart (
            addonJson    = jsonAddonParams, 
            headIp       = IP_ADDRESS1, 
            targetIp     = IP_ADDRESS2, 
            nodePassword = nodePassword, 
            serviceType  = serviceType, 
            serviceName  = serviceName, 
            osType       = OSType
        )




def setupProxy_head(cls_bil, headInfo, command):
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



def setupProxy_comp(headInfo, compInfo, command):

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
    params = getClusterInfo()
    clusterID = '622276'
    proxySetup(clusterID, params, nodePassword='test')

