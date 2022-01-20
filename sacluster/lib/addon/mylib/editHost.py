import sys
import time
import logging
from paramiko import channel
import tqdm
import numpy as np
import os
os.chdir(os.path.dirname(os.path.abspath(__file__)))
common_path = os.path.abspath("../../..")

sys.path.append(common_path + "/lib/others")
from API_method import get, post, put, delete
sys.path.append(common_path + "/lib/auth")
from auth_func_pro import authentication_cli

#並列処理を行う
import asyncio
import paramiko 

def hostsCompute(IpAddress, USER_NAME, Password, PORT, numNode, nodeIndex):
    #管理ノード
    IP_ADDRESS1 = IpAddress
    PORT1 = PORT
    USER1 = USER_NAME
    PASSWORD1 = Password

    # Connect to Head Node
    headnode = paramiko.SSHClient()
    headnode.set_missing_host_key_policy(paramiko.WarningPolicy())
    print("hostnode connecting...")
    headnode.connect(hostname=IP_ADDRESS1, port=PORT1, username=USER1, password=PASSWORD1)
    print('hostnode connected')

    # Head Node --> Compute Node
    # Login Info
    IP_ADDRESS2 = '192.168.1.' + str (nodeIndex)
    PORT2 = PORT
    USER2 = USER_NAME
    PASSWORD2 = Password  

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
    for j in range(numNode + 1):
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

def editHost (IpAddress, Password, numNode):
    # ----------------------------------------------------------
    # サーバーへの接続情報を設定
    USER_NAME = 'root'
    PORT = 22
    # サーバー上で実行するコマンドを設定
    # ----------------------------------------------------------
    for nodeIndex in range (numNode+1):
        if nodeIndex == 0 :
            hostsHead(IpAddress, USER_NAME, Password, PORT, numNode)
        else :
            hostsCompute (IpAddress, USER_NAME, Password, PORT, numNode, nodeIndex)

if __name__ == '__main__':
     # authentication setting
    auth_res = authentication_cli(fp = '', info_list = [1,0,0,0], api_index = True)

    #set url
    url_list = {}
    head_zone = 'tk1b'
    zone      = 'tk1b'
    zone_list = ['tk1b']
    for zone in zone_list:
        url_list[zone] = "https://secure.sakura.ad.jp/cloud/zone/"+ zone +"/api/cloud/1.1"
    head_url = "https://secure.sakura.ad.jp/cloud/zone/"+ head_zone +"/api/cloud/1.1"
    sub_url = ["/server","/disk","/switch","/interface","/bridge","/tag","/appliance","/power"]

    # Read cluster infomation
    get_cluster_id_info = get(url_list[zone] + sub_url[0], auth_res)
    
    numNode = 1 # 辻さんのコードを利用して個数を取得する必要あり．
    IpAddress = '163.43.144.138'
    Password = 'test_passwd'
    editHost (IpAddress, Password, numNode)
