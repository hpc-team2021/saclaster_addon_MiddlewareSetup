import sys
import time
import logging
from paramiko import channel
import tqdm
import os
import asyncio
import paramiko 
import json

# User defined Library
os.chdir(os.path.dirname(os.path.abspath(__file__)))
common_path = os.path.abspath("../..")

sys.path.append(common_path + "/lib/others")
from API_method import get, post, put, delete

sys.path.append(common_path + "/lib/auth")
from auth_func_pro import authentication_cli

sys.path.append (common_path + "/lib/addon/mylib")
from getClusterInfo import getClusterInfo
from loadAddonParams    import loadAddonParams

fileName = common_path + "\\lib\\addon\\addon.json"

# Edit /etc/hosts on compute node.
# Noted!!
# The target file could be diffrent among each OS & version.
# Need to check the file to edit 
def hostsCompute(headIp, USER_NAME, nodePassword, PORT, nodeIndex):
    # Head node info #####
    IP_ADDRESS1 = headIp
    PORT1 = PORT
    USER1 = USER_NAME
    PASSWORD1 = nodePassword
    ######################

    # Connect to Head Node
    headnode = paramiko.SSHClient()
    headnode.set_missing_host_key_policy(paramiko.WarningPolicy())
    print("hostnode connecting...")
    headnode.connect(hostname=IP_ADDRESS1, port=PORT1, username=USER1, password=PASSWORD1)
    print('hostnode connected')

    # Head Node --> Compute Node
    # Login Info (Compute node) ###############
    IP_ADDRESS2 = '192.168.100.' + str (nodeIndex)
    PORT2 = PORT
    USER2 = USER_NAME
    PASSWORD2 = nodePassword
    ########################################### 

    head = (IP_ADDRESS1,PORT1)
    compute = (IP_ADDRESS2, PORT2)
    transport1 = headnode.get_transport()
    channel1 = transport1.open_channel("direct-tcpip", compute, head)
    computenode = paramiko.SSHClient()
    computenode.set_missing_host_key_policy(paramiko.WarningPolicy())

    print("compurenode connecting...")
    computenode.connect(hostname=IP_ADDRESS2, username=USER2, password=PASSWORD2, sock=channel1, auth_timeout=100)
    print('computenode connected')

    #CMD = 'echo "computenode' + str(index) + ' 192.168.100.' + str(j) + '" >> /etc/hosts'
    stdin, stdout, stderr = computenode.exec_command ("hostname")

    # Store standard output
    cmd_result = ''
    for line in stdout :
        cmd_result += line
    print (cmd_result)
        
    # Store error output
    cmd_err = ''
    for line in stderr :
        cmd_err += line
    if cmd_err == '' :
        print (end = '') # output nothing. 
    else :
        print (cmd_err)
        sys.exit ()

    # Close Connection
    computenode.close()
    headnode.close()
    del headnode, computenode, stdin, stdout, stderr
    

# Login to node via SSH, run command & write into /etc/hosts on Headnode
def hostsHead (IpAddress, USER_NAME, Password, PORT):
    # Create SSH client
    headnode = paramiko.SSHClient ()
    headnode.set_missing_host_key_policy (paramiko.AutoAddPolicy())
    headnode.connect (IpAddress, PORT, USER_NAME, Password)

    stdin, stdout, stderr = headnode.exec_command ("hostname")

    # Store standard output
    cmd_result = ''
    for line in stdout :
        cmd_result += line
    print (cmd_result)
    
    # Store error output
    cmd_err = ''
    for line in stderr :
        cmd_err += line
    if cmd_err == '' :
        print (end = '') # output nothing. 
    else :
        print (cmd_err)
        sys.exit ()

    # close connection
    headnode.close ()
    del headnode, stdin, stdout, stderr

# Main
def editHost (clusterID, params, nodePassword, jsonAddonParams):
    # ----------------------------------------------------------
    # Common parameters to connect to nodes
    USER_NAME = 'root'
    PORT = 22
    OSType = ''
    # ----------------------------------------------------------
    
    # Parameters
    headIp  = "163.43.145.209"
    nComputenode = 0
    node_dict = params.get_node_info()
    disk_dict = params.get_disk_info()

    # 1. Get the global IP of Head node
    # 2. Count the compute nodes in the target cluster
    for zone, url in params.url_list.items():
        node_list = node_dict[zone]
        disk_list = list(disk_dict[zone].keys())
        if(len(node_list) != 0):
            print (zone + " has nodes")
            for i in range(len(node_list)):
                if (len(node_list[i]["Tags"]) == 0):
                    print(clusterID + ':' + 'No Tag' + ' | ' + node_list[i]['Name'])
                else:
                    print(clusterID + ':' + node_list[i]["Tags"][0] + ' | ' + node_list[i]['Name'])
                    if (clusterID in node_list[i]["Tags"][0] and 'headnode' in node_list[i]['Name']):
                        headIp = node_list[i]['Interfaces'][0]['IPAddress']
                        OSType = disk_dict[zone][disk_list[i]]["SourceArchive"]["Name"]
                    elif (clusterID in node_list[i]["Tags"][0] and 'computenode' in node_list[i]['Name']):
                        nComputenode += 1
                    else:
                        pass
            print (" ")
        else:
            print (zone + " has no nodes")
            pass

    for nodeIndex in range (nComputenode+1):
        if nodeIndex == 0 :
            hostsHead(headIp, USER_NAME, nodePassword, PORT)
        else :
            hostsCompute (headIp, USER_NAME, nodePassword, PORT, nodeIndex)

if __name__ == '__main__':
    # authentication setting
    auth_res = authentication_cli(fp = '', info_list = [1,0,0,0], api_index = True)

    jsonAddonParams = loadAddonParams ()

    # Prepare Argument
    clusterInfo = getClusterInfo ()
    clusterID = "558288"
    nodePassword = 'test'
    editHost (clusterID, clusterInfo, nodePassword, jsonAddonParams)