import time
import os

from numpy import outer
os.chdir(os.path.dirname(os.path.abspath(__file__)))
common_path = os.path.abspath("../../..")

import paramiko 
from tqdm import tqdm

import warnings
warnings.filterwarnings('ignore')

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
    headnode.connect(hostname=headInfo['IP_ADDRESS'], port=headInfo['PORT'], username=headInfo['USER'], password=headInfo['PASSWORD'])

     #コマンド実行
    for CMD in tqdm(HEAD_CMD):
        stdin, stdout, stderr = headnode.exec_command(CMD)
        time.sleep(1)
        # out = stdout.read().decode()
        # print('head_stdout = %s' % out)
    
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
        channel1 = transport1.open_channel("direct-tcpip", compute, head)

        computenode = paramiko.SSHClient()
        computenode.set_missing_host_key_policy(paramiko.WarningPolicy())

        print('IP : %s connecting...' %(IP))
        computenode.connect(hostname=compInfo['IP_ADDRESS'],username=compInfo['USER'],password=compInfo['PASSWORD'],sock=channel1,auth_timeout=100)

         #コマンド実行
        for CMD in tqdm(COMPUTE_CMD):
            stdin, stdout, stderr = computenode.exec_command(CMD)
            time.sleep(1)
            # out = stdout.read().decode()
            #print('comp_stdout = %s' % out)

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
    headnode.connect(hostname=headInfo['IP_ADDRESS'], port=headInfo['PORT'], username=headInfo['USER'], password=headInfo['PASSWORD'])
    transport1  = headnode.get_transport()
    channel1    = transport1.open_channel("direct-tcpip", compute, head)

    computenode = paramiko.SSHClient()
    computenode.set_missing_host_key_policy(paramiko.WarningPolicy())

    print('Connecting %s ' %(IP))
    computenode.connect(hostname=compInfo['IP_ADDRESS'],username=compInfo['USER'],password=compInfo['PASSWORD'],sock=channel1,auth_timeout=100)

        #コマンド実行
    for CMD in tqdm(COMPUTE_CMD):
        stdin, stdout, stderr = computenode.exec_command(CMD)
        time.sleep(1)
        # out = stdout.read().decode()
        #print('comp_stdout = %s' % out)

    computenode.close()
    headnode.close()
    del headnode, stdin, stdout, stderr

       

