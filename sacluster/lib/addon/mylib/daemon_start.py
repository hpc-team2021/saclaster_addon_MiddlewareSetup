import os
from platform import node
import sys
import time
import logging
import paramiko
import string
import json
from numpy.lib.shape_base import tile
logger = logging.getLogger ("sacluster").getChild (os.path.basename (__file__))

from os.path import expanduser
home_path = expanduser ("~") + "/sacluster"
os.makedirs (home_path, exist_ok = True)

os.chdir (os.path.dirname (os.path.abspath (__file__)))
common_path = os.path.abspath("../../..")

sys.path.append (common_path + "/lib/others")
from API_method import get, post, put, delete
import get_params
import get_cluster_id
from info_print import printout

sys.path.append (common_path + "/lib/auth")
from auth_func_pro import authentication_cli

sys.path.append (common_path + "/lib/def_conf")
from load_external_data import external_data

sys.path.append (common_path + "/lib/addon/mylib")
from get_cluster_info import get_cluster_info

fileName = common_path + "\\lib\\addon\\setting.json"

# Start daemon on the computer node
# Noted!!
# The Setting could be diffrent among each OS & version.
# Need to check the file to edit 
def daemon_compute(addon_json, head_ip, target_ip, user_name, password, port, service_type, service_name, os_type):
    # Command variable
    cmdList = addon_json ['MiddleWare'][service_type][service_name]['Daemon'][os_type]['Compute']

    #--------------------
    # Head node Info
    IP_ADDRESS1 = head_ip
    port1 = port
    USER1 = user_name
    password1 = password

    # Target node Info
    IP_ADDRESS2 = target_ip
    port2 = port
    USER2 = user_name
    password2 = password
    # ---------------------

    # Connect to Head Node: Local --> Head Node
    headnode = paramiko.SSHClient()
    headnode.set_missing_host_key_policy(paramiko.WarningPolicy())
    print("hostnode connecting...")
    headnode.connect(hostname=IP_ADDRESS1, port=port1, username=USER1, password=password1)
    print('hostnode connected')

    # Head Node --> Compute Node
    head = (IP_ADDRESS1,port1)
    compute = (IP_ADDRESS2, port2)
    transport1 = headnode.get_transport()
    channel1 = transport1.open_channel("direct-tcpip", compute, head)
    computenode = paramiko.SSHClient()
    computenode.set_missing_host_key_policy(paramiko.WarningPolicy())
    print("compurenode connecting...")
    computenode.connect(hostname=IP_ADDRESS2,username=USER2,password=password2,sock=channel1)
    print('computenode connected')

    # Execute command & store the result------------------------
    for cmd in cmdList:
        stdin, stdout, stderr = computenode.exec_command (cmd)

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

    # Close Connection -----------------------------
    if len (cmdList) > 0:
        del stdin, stdout, stderr
    computenode.close()
    headnode.close()
    del headnode,computenode

# Login to node via SSH, run command & write into /etc/hosts on Headnode
def daemon_head (addon_json, head_ip, user_name, password, port, service_type, service_name, os_type):
    cmdList = addon_json ['MiddleWare'][service_type][service_name]['Daemon'][os_type]['Head']

    # Create SSH client
    headnode = paramiko.SSHClient ()
    headnode.set_missing_host_key_policy (paramiko.AutoAddPolicy())
    headnode.connect (head_ip, port, user_name, password)

    # Execute command & store the result
    for cmd in cmdList:
        stdin, stdout, stderr = headnode.exec_command (cmd)

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

    # close connection
    headnode.close ()
    del headnode, stdin, stdout, stderr

# Main
def daemon_start (addon_json, head_ip, target_ip, node_password, service_type, service_name, os_type):
    # ----------------------------------------------------------
    # サーバーへの接続情報を設定
    user_name = 'root'
    port = 22
    password = node_password
    # サーバー上で実行するコマンドを設定
    # ----------------------------------------------------------
    if target_ip == head_ip:
        daemon_head (addon_json, head_ip, user_name, password, port, service_type, service_name, os_type)
    else:
        daemon_compute (addon_json, head_ip, target_ip, user_name, password, port, service_type, service_name, os_type)

# Unit Test
if __name__ == '__main__':
     # authentication setting
    auth_res = authentication_cli(fp = '', info_list = [1,0,0,0], api_index = True)

    # Load addon setting parameter
    json_open = open(fileName, 'r')
    addon_json = json.load(json_open)

    # Prepare Argument-----------------------
    target_ip = "192.168.1.1"
    service_type = "Proxy"
    service_name = "squid"
    os_type = "CentOS 7.9 (2009) 64bit"
    nodepassword = "test"
    clusterID = "983867"
    head_ip  = "255.255.255.255"
    #-----------------------------------------
       
    params = getClusterInfo()
    node_dict = params.get_node_info()
    disk_dict = params.get_disk_info()

    # Get the global IP of Head node
    for zone, url in params.url_list.items():
        node_list = node_dict[zone]
        disk_list = list(disk_dict[zone].keys())
        if(len(node_list) != 0):
            print (zone + " has nodes")
            for i in range(len(node_list)):
                print(clusterID + ':' + node_list[i]["Tags"][0] + ' | ' + node_list[i]['Name'])
                if (clusterID in node_list[i]["Tags"][0] and 'headnode' in node_list[i]['Name']):
                    head_ip = node_list[i]['Interfaces'][0]['IPAddress']
    
    # Main
    daemon_start (addon_json, head_ip, target_ip, nodepassword, service_type, service_name, os_type)
