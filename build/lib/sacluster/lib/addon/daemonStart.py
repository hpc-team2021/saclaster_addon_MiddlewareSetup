import os
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

common_path = "../.."
os.chdir (os.path.dirname (os.path.abspath (__file__)))

sys.path.append (common_path + "/lib/others")
from API_method import get, post, put, delete
import get_params
import get_cluster_id
from info_print import printout

sys.path.append (common_path + "/lib/auth")
from auth_func_pro import authentication_cli

sys.path.append (common_path + "/lib/def_conf")
from load_external_data import external_data

# login to node via SSH, run command & write into /etc/hosts 
def runCMD_PW (IP_ADDRESS, USER_NAME, PASSWORD, PORT, CMD):
    # Create SSH client
    ssh = paramiko.SSHClient ()
    ssh.set_missing_host_key_policy (paramiko.AutoAddPolicy())
    ssh.connect (IP_ADDRESS, PORT, USER_NAME, PASSWORD)

    # Execute command & store the result
    stdin, stdout, stderr = ssh.exec_command (CMD)

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
    ssh.close ()
    del ssh, stdin, stdout, stderr


def daemonStart (IP_ADDRESS, daemonName):
    # ----------------------------------------------------------
    # サーバーへの接続情報を設定
    USER_NAME = 'root'
    PORT = 22
    PASSWORD = 'test_passwd'
    # サーバー上で実行するコマンドを設定
    # ----------------------------------------------------------
    CMD = "ssh 192.168.1.2 | systemctl status" + str(daemonName)
    runCMD_PW (IP_ADDRESS, USER_NAME, PASSWORD, PORT, CMD)



if __name__ == '__main__':
     # authentication setting
    auth_res = authentication_cli(fp = '', info_list = [1,0,0,0], api_index = True)

    #set url
    url_list = {}
    head_zone = 'is1b'
    zone      = 'is1b'
    zone_list = ['is1b']
    for zone in zone_list:
        url_list[zone] = "https://secure.sakura.ad.jp/cloud/zone/"+ zone +"/api/cloud/1.1"
    head_url = "https://secure.sakura.ad.jp/cloud/zone/"+ head_zone +"/api/cloud/1.1"
    sub_url = ["/server","/disk","/switch","/interface","/bridge","/tag","/appliance","/power"]

    # Read cluster infomation
    get_cluster_id_info = get(url_list[zone] + sub_url[0], auth_res)
    
    s = str (get_cluster_id_info).split ()
    i = 0
    while not ('testNode2' in s[i]) :
        i += 1
    print (s[i])

    while not ('Interfaces' in s[i]) :
        i += 1
    print (s[i])

    while not ('IPAddress' in s[i]) :
        i += 1
    print (s[i+1].replace ("'", ""))

    # Set argument
    IP_ADDRESS = s[i+1].replace (",", "").replace("'", "")
    daemonName = "squid"
    daemonStart (IP_ADDRESS, daemonName)
