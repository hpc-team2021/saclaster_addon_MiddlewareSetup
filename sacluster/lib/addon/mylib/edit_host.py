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
common_path = os.path.abspath("../../..")

sys.path.append(common_path + "/lib/others")
from API_method import get, post, put, delete

sys.path.append(common_path + "/lib/auth")
from auth_func_pro import authentication_cli

sys.path.append (common_path + "/lib/addon/mylib")
from get_cluster_info import get_cluster_info
from load_addon_params    import load_addon_params

fileName = common_path + "\\lib\\addon\\addon.json"

# Edit /etc/hosts on compute node.
# Noted!!
# The target file could be diffrent among each OS & version.
# Need to check the file to edit 
def hosts_compute(head_ip, user_name, node_password, port, n_computenode, node_index, json_addon_params, os_type):
    # Load Command data
    if 'CentOS' in os_type:
        os_name = 'CentOS'
    elif 'Ubuntu' in os_type:
        os_name = 'Ubuntu'
    cmd_main = json_addon_params ['Common']['hosts']['cmd']
    target_file = json_addon_params ['Common']['hosts'][os_name]

    # Head node info #####
    ipaddress1 = head_ip
    port1 = port
    user1 = user_name
    password1 = node_password
    ######################

    # Connect to Head Node
    headnode = paramiko.SSHClient()
    headnode.set_missing_host_key_policy(paramiko.WarningPolicy())
    print("hostnode connecting...")
    headnode.connect(hostname=ipaddress1, port=port1, username=user1, password=password1)
    print('hostnode connected')

    # Head Node --> Compute Node
    # Login Info (Compute node) ###############
    ipaddress2 = '192.168.100.' + str (node_index)
    port2 = port
    user2 = user_name
    password2 = node_password
    ########################################### 

    head = (ipaddress1,port1)
    compute = (ipaddress2, port2)
    transport1 = headnode.get_transport()
    channel1 = transport1.open_channel("direct-tcpip", compute, head)
    computenode = paramiko.SSHClient()
    computenode.set_missing_host_key_policy(paramiko.WarningPolicy())

    print("compurenode connecting...")
    computenode.connect(hostname=ipaddress2,username=user2,password=password2,sock=channel1)
    print('computenode connected')

    # Execute command & store the result
    for j in range(n_computenode + 1):
        if j == 0:
            CMD = cmd_main + ' "' + '192.168.100.254  headnode" > ' + target_file
            #CMD = 'echo "headnode 192.168.100.254" > /etc/hosts'
            stdin, stdout, stderr = computenode.exec_command (CMD)
        else:
            if j < 10:
                index = '00' + str (j)
            elif (j > 10) & (j < 100):
                index = '0' + str (j)
            CMD = cmd_main + ' "' + '   192.168.100.' + str(j) + '  computenode' + str(index) +  '" >> ' + target_file
            #CMD = 'echo "computenode' + str(index) + ' 192.168.100.' + str(j) + '" >> /etc/hosts'
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
def hosts_head (IpAddress, user_name, Password, port, numNode, json_addon_params, os_type):
    # Load Command data
    if 'CentOS' in os_type:
        os_name = 'CentOS'
    elif 'Ubuntu' in os_type:
        os_name = 'Ubuntu'
    cmd_main = json_addon_params ['Common']['hosts']['cmd']
    target_file = json_addon_params ['Common']['hosts'][os_name]

    # Create SSH client
    headnode = paramiko.SSHClient ()
    headnode.set_missing_host_key_policy (paramiko.AutoAddPolicy())
    headnode.connect (IpAddress, port, user_name, Password)

    # Execute command & store the result
    for i in range(numNode + 1):
        if i == 0:
            CMD = cmd_main + ' "' + '192.168.100.254  headnode" > ' + target_file
            #CMD = 'echo "headnode 192.168.100.254" > /etc/hosts'
            stdin, stdout, stderr = headnode.exec_command (CMD)
        else:
            if i < 10:
                index = '00' + str (i)
            elif (i > 10) & (i < 100):
                index = '0' + str (i)
            CMD = cmd_main + ' "' + ' 192.168.100.' + str(i) + '  computenode' + str(index)  +  '" >> ' + target_file
            # CMD = 'echo "computenode' + str(index) + '    192.168.100.' + str(i) + '" >> /etc/hosts'
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

# Main
def edit_host (cls_bil, clusterID, params, node_password, json_addon_params):
    # ----------------------------------------------------------
    # Common parameters to connect to nodes
    user_name = 'root'
    port = 22
    os_type = ''
    # ----------------------------------------------------------
    
    # Parameters
    head_ip  = "255.255.255.255"
    n_computenode = 0
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
                        head_ip = node_list[i]['Interfaces'][0]['IPAddress']
                        os_type = disk_dict[zone][disk_list[i]]["SourceArchive"]["Name"]
                    elif (clusterID in node_list[i]["Tags"][0] and 'computenode' in node_list[i]['Name']):
                        n_computenode += 1
                    else:
                        pass
            print (" ")
        else:
            print (zone + " has no nodes")
            pass

    for node_index in range (n_computenode+1):
        if node_index == 0 :
            hosts_head(head_ip, user_name, node_password, port, n_computenode, json_addon_params, os_type)
        else :
            hosts_compute (head_ip, user_name, node_password, port, n_computenode, node_index, json_addon_params, os_type)

if __name__ == '__main__':
    # authentication setting
    auth_res = authentication_cli(fp = '', info_list = [1,0,0,0], api_index = True)

    json_addon_params = loadAddonParams ()

    # Prepare Argument
    clusterInfo = getClusterInfo ()
    clusterID = "138658"
    node_password = 'test'
    edit_host (clusterID, clusterInfo, node_password, json_addon_params)