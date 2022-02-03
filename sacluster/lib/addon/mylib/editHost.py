import sys
import time
import logging
from paramiko import channel
import tqdm
import numpy as np
import os
import asyncio
import paramiko 
import json

# User defined Library
os.chdir(os.path.dirname(os.path.abspath(__file__)))
common_path = os.path.abspath("../../..")

sys.path.append(common_path + "/lib/others")
from API_method import get, post, put, delete

sys.path.append(common_path + "/lib/auth")
from auth_func_pro import authentication_cli

sys.path.append (common_path + "/lib/addon/mylib")
from getClusterInfo import getClusterInfo

# Edit /etc/hosts on compute node.
# Noted!!
# The target file could be diffrent among each OS & version.
# Need to check the file to edit 
def hostsCompute(headIp, USER_NAME, nodePassword, PORT, nComputenode, nodeIndex):
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
    computenode.connect(hostname=IP_ADDRESS2,username=USER2,password=PASSWORD2,sock=channel1)
    print('computenode connected')

    # Execute command & store the result
    for j in range(nComputenode + 1):
        if j == 0:
            CMD = 'echo "headnode 192.168.100.254" > /etc/hosts'
            stdin, stdout, stderr = computenode.exec_command (CMD)
        else:
            if j < 10:
                index = '00' + str (j)
            elif (j > 10) & (j < 100):
                index = '0' + str (j)
            CMD = 'echo "computenode' + str(index) + ' 192.168.100.' + str(j) + '" >> /etc/hosts'
            stdin, stdout, stderr = computenode.exec_command (CMD)

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
def hostsHead (IpAddress, USER_NAME, Password, PORT, numNode):
    # Create SSH client
    headnode = paramiko.SSHClient ()
    headnode.set_missing_host_key_policy (paramiko.AutoAddPolicy())
    headnode.connect (IpAddress, PORT, USER_NAME, Password)

    # Execute command & store the result
    for i in range(numNode + 1):
        if i == 0:
            CMD = 'echo "headnode 192.168.100.254" > /etc/hosts'
            stdin, stdout, stderr = headnode.exec_command (CMD)
        else:
            if i < 10:
                index = '00' + str (i)
            elif (i > 10) & (i < 100):
                index = '0' + str (i)
            CMD = 'echo "computenode' + str(index) + ' 192.168.100.' + str(i) + '" >> /etc/hosts'
            stdin, stdout, stderr = headnode.exec_command (CMD)

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

def editHost (clusterID, params, nodePassword):
    # ----------------------------------------------------------
    # Common parameters to connect to nodes
    USER_NAME = 'root'
    PORT = 22
    # ----------------------------------------------------------
    
    # Parameters
    headIp  = "255.255.255.255"
    nComputenode = 0
    node_dict = params.get_node_info()
    disk_dict = params.get_disk_info()

    # 1. Get the global IP of Head node
    # 2. Count the compute nodes in the target cluster
    for zone, url in params.url_list.items():
        node_list = node_dict[zone]
        disk_list = list(disk_dict[zone].keys())
        if(len(node_list) != 0):
            for i in range(len(node_list)):
                print(clusterID + ':' + node_list[i]["Tags"][0] + ' | ' + node_list[i]['Name'])
                if (clusterID in node_list[i]["Tags"][0] and 'headnode' in node_list[i]['Name']):
                    headIp = node_list[i]['Interfaces'][0]['IPAddress']
                elif (clusterID in node_list[i]["Tags"][0] and 'computenode' in node_list[i]['Name']):
                    nComputenode += 1
                else:
                    pass
        else:
            print (zone + " has no nodes")
            pass

    for nodeIndex in range (nComputenode+1):
        if nodeIndex == 0 :
            hostsHead(headIp, USER_NAME, nodePassword, PORT, nComputenode)
        else :
            hostsCompute (headIp, USER_NAME, nodePassword, PORT, nComputenode, nodeIndex)

if __name__ == '__main__':
     # authentication setting
    auth_res = authentication_cli(fp = '', info_list = [1,0,0,0], api_index = True)
    
    # Prepare Argument
    params = getClusterInfo()
    clusterID = "983867"

    editHost (clusterID, params, nodePassword = "test")
