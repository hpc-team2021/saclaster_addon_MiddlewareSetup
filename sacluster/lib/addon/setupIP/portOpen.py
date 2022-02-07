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
from getClusterInfo import getClusterInfo

fileName = common_path + "\\lib\\addon\\setting.json"

# Start daemon on the computer node
# Noted!!
# The Setting could be diffrent among each OS & version.
# Need to check the file to edit 
def portCompute(addonJson, headIp, targetIp, USER_NAME, PASSWORD, PORT, portService):
    # Command variable
    cmdMain = addonJson ['Common']['basic'][0]
    cmdSub = addonJson ['Common']['Port'][portService]
    
    #--------------------
    # Head node Info
    IP_ADDRESS1 = headIp
    PORT1 = PORT
    USER1 = USER_NAME
    PASSWORD1 = PASSWORD

    # Target node Info
    IP_ADDRESS2 = targetIp
    PORT2 = PORT
    USER2 = USER_NAME
    PASSWORD2 = PASSWORD
    # ---------------------

    # Connect to Head Node: Local --> Head Node
    headnode = paramiko.SSHClient()
    headnode.set_missing_host_key_policy(paramiko.WarningPolicy())
    print("hostnode connecting...")
    headnode.connect(hostname=IP_ADDRESS1, port=PORT1, username=USER1, password=PASSWORD1)
    print('hostnode connected')

    # Head Node --> Compute Node
    head = (IP_ADDRESS1,PORT1)
    compute = (IP_ADDRESS2, PORT2)
    transport1 = headnode.get_transport()
    channel1 = transport1.open_channel("direct-tcpip", compute, head)
    computenode = paramiko.SSHClient()
    computenode.set_missing_host_key_policy(paramiko.WarningPolicy())
    print("compurenode connecting...")
    computenode.connect(hostname=IP_ADDRESS2,username=USER2,password=PASSWORD2,sock=channel1)
    print('computenode connected')

    # Execute command & store the result------------------------
    CMD = cmdMain + str(' ') + cmdSub
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
    
    # Execute command & store the result -----------------
    cmdMain + str(' ') + cmdSub
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

    # Close Connection -----------------------------
    computenode.close()
    headnode.close()
    del headnode, computenode, stdin, stdout, stderr

# Login to node via SSH, run command & openthe target port on Headnode
def portHead (addonJson, headIp, USER_NAME, PASSWORD, PORT, portService):
    cmdMain = addonJson ['Common']['basic'][0]
    cmdSub = addonJson ['Common']['Port'][portService]

    # Create SSH client
    headnode = paramiko.SSHClient ()
    headnode.set_missing_host_key_policy (paramiko.AutoAddPolicy())
    headnode.connect (headIp, PORT, USER_NAME, PASSWORD)

    # Execute command & store the result
    CMD = cmdMain + str(' ') + cmdSub
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

    # Execute command & store the result
    CMD = cmdMain + str(' ') + cmdSub[2]
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
def portOpen (portService, addonJson, headIp, targetIp, nodePassword):
    # ----------------------------------------------------------
    # サーバーへの接続情報を設定
    USER_NAME = 'root'
    PORT = 22
    PASSWORD = nodePassword
    # サーバー上で実行するコマンドを設定
    # ----------------------------------------------------------
    if targetIp == headIp:
        portHead (addonJson, headIp, USER_NAME, PASSWORD, PORT, portService)
    else:
        portCompute (addonJson, headIp, targetIp, USER_NAME, PASSWORD, PORT, portService)

# Unit Test
if __name__ == '__main__':
     # authentication setting
    auth_res = authentication_cli(fp = '', info_list = [1,0,0,0], api_index = True)

    # Load addon setting parameter
    json_open = open(fileName, 'r')
    addonJson = json.load(json_open)

    # Prepare Argument-----------------------
    targetIp = "192.168.1.1"
    portService = "squid"
    nodePassword = "test"
    clusterID = "983867"
    headIp  = "255.255.255.255"
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
                    headIp = node_list[i]['Interfaces'][0]['IPAddress']
    
    # Main
    portOpen (portService, addonJson, headIp, targetIp, nodePassword)
