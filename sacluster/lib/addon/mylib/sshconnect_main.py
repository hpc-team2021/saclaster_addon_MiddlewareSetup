import time
import os
import sys

from numpy import outer
os.chdir(os.path.dirname(os.path.abspath(__file__)))
common_path = os.path.abspath("../../..")

import logging
logger = logging.getLogger("addon").getChild(os.path.basename(__file__))

sys.path.append (common_path + "/lib/addon/mylib")
from get_cluster_info     import get_cluster_info

import subprocess
import paramiko 
from tqdm import tqdm

#import warnings
#warnings.filterwarnings('ignore')
# Changing standard output color for exception error
RED = '\033[31m'
END = '\033[0m'

def sshConnect_main(clusterID, params, nodePassword):
    headIp  = "255.255.255.255"
    nComputenode = 0
    OSType = ""

    node_dict = params.get_node_info()
    disk_dict = params.get_disk_info()
    
    for zone, url in params.url_list.items():
        node_list = node_dict[zone]
        disk_list = list(disk_dict[zone].keys())

        if(len(node_list) != 0):
            for i in range(len(node_list)):
                if (len(node_list[i]["Tags"]) != 0):
                    
                    if (clusterID in node_list[i]["Tags"][0] and 'head' in node_list[i]['Name']):
                        headIp = node_list[i]['Interfaces'][0]['IPAddress']
                        OSType = disk_dict[zone][disk_list[i]]["SourceArchive"]["Name"]
                         
                    elif (clusterID in node_list[i]["Tags"][0]):
                        nComputenode+= 1 
                    
                    else:
                        pass
        else:
            pass    

    headInfo = {
        'IP_ADDRESS':headIp,
        'PORT'      :22,
        'USER'      :'root',
        'PASSWORD'  :nodePassword
    }

    return headInfo, OSType, nComputenode

def headConnect(headInfo, HEAD_CMD):
    
    headnode = paramiko.SSHClient()
    headnode.set_missing_host_key_policy(paramiko.WarningPolicy())
    print("Headnode connecting...")
    try:
        headnode.connect(
            hostname = headInfo['IP_ADDRESS'],
            port = headInfo['PORT'],
            username = headInfo['USER'],
            password = headInfo['PASSWORD']
        )
    except Exception as err:
        print (RED + "Fialed to connect to headnode")
        print ("Error type: {}" .format(err))
        print ("Exit programm" + END)
        sys.exit ()
    print('Connected')

     #コマンド実行
    for CMD in tqdm(HEAD_CMD):
        stdin, stdout, stderr = headnode.exec_command(CMD)
        # time.sleep(3)
        out = stdout.read().decode()
        # print('comp_stdout = %s' % out)
        logger.debug('comp_stdout = %s' % out)
    """
        while not stdout.channel.exit_status_ready():
                if stdout.channel.recv_ready():
                    out = stdout.readlines()
                    #out = stdout.read().decode()
                    #print('comp_stdout = %s' % out)
    """
    
    headnode.close()
    del headnode, stdin, stdout, stderr

def computeConnect(headInfo, IP_list, COMPUTE_CMD):

    for IP in IP_list["front"]:
        IP_ADDRESS2 = IP
        compInfo = {
            'IP_ADDRESS':IP_ADDRESS2,
            'PORT'      :22,
            'USER'      :'root',
            'PASSWORD'  :headInfo['PASSWORD']
        }

        head = (headInfo['IP_ADDRESS'], headInfo['PORT'])
        compute = (compInfo['IP_ADDRESS'], compInfo['PORT'])

        headnode = paramiko.SSHClient()
        headnode.set_missing_host_key_policy(paramiko.WarningPolicy())
        headnode.connect(hostname=headInfo['IP_ADDRESS'], port=headInfo['PORT'], username=headInfo['USER'], password=headInfo['PASSWORD'])
        transport1 = headnode.get_transport()
        try:
            channel1 = transport1.open_channel("direct-tcpip", compute, head)
        except Exception as err:
            print (RED + "Failed to open channel to compute_node" + IP)
            print ("Error type: {}" .format(err))
            print ("Exit programm" + END)
            sys.exit ()
        computenode = paramiko.SSHClient()
        computenode.set_missing_host_key_policy(paramiko.WarningPolicy())

        print('IP : %s connecting...' %(IP))
        computenode.connect(hostname=compInfo['IP_ADDRESS'],username=compInfo['USER'],password=compInfo['PASSWORD'],sock=channel1,auth_timeout=100)

         #コマンド実行
        for CMD in tqdm(COMPUTE_CMD):
            stdin, stdout, stderr = computenode.exec_command(CMD)
            # time.sleep(3)
            out = stdout.read().decode()
            # print('comp_stdout = %s' % out)
            logger.debug('comp_stdout = %s' % out)

        """
            while not stdout.channel.exit_status_ready():
                if stdout.channel.recv_ready():
                    out = stdout.readlines()
                    #out = stdout.read().decode()
                    #print('comp_stdout = %s' % out)
        """

        computenode.close()
    headnode.close()
    del headnode, stdin, stdout, stderr



def computeConnect_IP(headInfo,IP,COMPUTE_CMD):

    IP_ADDRESS2 = IP
    compInfo = {
        'IP_ADDRESS':IP_ADDRESS2,
        'PORT'      :22,
        'USER'      :'root',
        'PASSWORD'  :headInfo['PASSWORD']
    }

    head        = (headInfo['IP_ADDRESS'], headInfo['PORT'])
    compute     = (compInfo['IP_ADDRESS'], compInfo['PORT'])

    headnode    = paramiko.SSHClient()
    headnode.set_missing_host_key_policy(paramiko.WarningPolicy())
    try:
        headnode.connect(
            hostname = headInfo['IP_ADDRESS'],
            port = headInfo['PORT'],
            username = headInfo['USER'],
            password = headInfo['PASSWORD']
        )
    except Exception as err:
        print (RED + "Fialed to connect to headnode")
        print ("Error type: {}" .format(err))
        print ("Exit programm" + END)
        sys.exit ()
   
    transport1  = headnode.get_transport()
    channel1    = transport1.open_channel("direct-tcpip", compute, head)

    computenode = paramiko.SSHClient()
    computenode.set_missing_host_key_policy(paramiko.WarningPolicy())

    print('Connecting %s ' %(IP))
    computenode.connect(hostname=compInfo['IP_ADDRESS'],username=compInfo['USER'],password=compInfo['PASSWORD'],sock=channel1,auth_timeout=100)

        #コマンド実行
    for CMD in tqdm(COMPUTE_CMD):
        try:
            headnode.exec_command (CMD)
            stdin, stdout, stderr = computenode.exec_command(CMD)
            # time.sleep(1)
            out = stdout.read().decode()
            # print('comp_stdout = %s' % out)
            logger.debug('comp_stdout = %s' % out)

        except paramiko.SSHException as err:
            print (RED + "Failed to excute command on headnode")
            print ("Error Type: {}" .format (err))
            print ("Exit Programm" + END)
            sys.exit ()

    computenode.close()
    headnode.close()
    del headnode, stdin, stdout, stderr


def headConnect_command(headInfo, HEAD_CMD):
    out_list = []

    headnode = paramiko.SSHClient()
    headnode.set_missing_host_key_policy(paramiko.WarningPolicy())
    print("Headnode connecting...")
    try:
        headnode.connect(
            hostname = headInfo['IP_ADDRESS'],
            port = headInfo['PORT'],
            username = headInfo['USER'],
            password = headInfo['PASSWORD']
        )
    except Exception as err:
        print (RED + "Fialed to connect to headnode")
        print ("Error type: {}" .format(err))
        print ("Exit programm" + END)
        sys.exit ()
    
     #コマンド実行
    for CMD in tqdm(HEAD_CMD):
        stdin, stdout, stderr = headnode.exec_command(CMD)
        # time.sleep(3)
        out_list.append(stdout.read().decode())

    headnode.close()
    del headnode, stdin, stdout, stderr
    return out_list


def computeConnect_command(headInfo, IP_list, COMPUTE_CMD):
    out_list = []

    for IP in IP_list["front"]:
        IP_ADDRESS2 = IP
        compInfo = {
            'IP_ADDRESS':IP_ADDRESS2,
            'PORT'      :22,
            'USER'      :'root',
            'PASSWORD'  :headInfo['PASSWORD']
        }

        head = (headInfo['IP_ADDRESS'], headInfo['PORT'])
        compute = (compInfo['IP_ADDRESS'], compInfo['PORT'])

        headnode = paramiko.SSHClient()
        headnode.set_missing_host_key_policy(paramiko.WarningPolicy())
        headnode.connect(hostname=headInfo['IP_ADDRESS'], port=headInfo['PORT'], username=headInfo['USER'], password=headInfo['PASSWORD'])
        transport1 = headnode.get_transport()
        try:
            channel1 = transport1.open_channel("direct-tcpip", compute, head)
        except Exception as err:
            print (RED + "Failed to open channel to compute_node" + IP)
            print ("Error type: {}" .format(err))
            print ("Exit programm" + END)
            sys.exit ()
        computenode = paramiko.SSHClient()
        computenode.set_missing_host_key_policy(paramiko.WarningPolicy())

        print('IP : %s connecting...' %(IP))
        computenode.connect(hostname=compInfo['IP_ADDRESS'],username=compInfo['USER'],password=compInfo['PASSWORD'],sock=channel1,auth_timeout=100)

         #コマンド実行
        for CMD in tqdm(COMPUTE_CMD):
            stdin, stdout, stderr = computenode.exec_command(CMD)
            # time.sleep(3)
            out_list.append(stdout.read().decode())

        computenode.close()
    headnode.close()

    del headnode, stdin, stdout, stderr
    return out_list


if __name__ == '__main__':
    params              = get_cluster_info ()

    cls_bil  = []
    ext_info = []
    info_list = [1,0,0,1]
    f = []
    out_comp = []

    addon_info = {
        "clusterID"         : "649106",                 # !!! 任意のクラスターIDに変更 !!!
        "IP_list"           :{                          # コンピュートノードの数に合わせて変更
            "front" : ['192.168.3.1', '192.168.3.2'],
            "back"  : ['192.169.3.1', '192.169.3.2']
        },
        "params"            : params,
        "node_password"     : "test01pw"                    # 設定したパスワードを入力
    }
    cluster_id       = addon_info["clusterID"]
    ip_list         = addon_info["IP_list"]
    params          = addon_info["params"]
    node_password    = addon_info["node_password"]


    head_list, os_type, computememory = sshConnect_main(cluster_id,params,node_password)
    
    HEAD_CMD = ["hostname -s"]
    COMPUTE_CMD = ["slurmd -C"]

    out_head = headConnect_command(head_list, HEAD_CMD)
    print('head_stdout = %s' % out_head)

    out_comp = computeConnect_command(head_list, ip_list, COMPUTE_CMD)
    for x in out_comp:
        print('comp_stdout = %s' % x)
     #print('comp_stdout = %s' % out_comp[1])

    #RealMemory抽出
    memory = out_comp[0].split()
    print(memory)
    print(memory[1])



    

