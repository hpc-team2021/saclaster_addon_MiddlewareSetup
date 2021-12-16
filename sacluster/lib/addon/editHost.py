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
    # open /etc/host to write hostname & IP address
    f = open('hosts', 'a' )

    # Create SSH client
    ssh = paramiko.SSHClient ()
    ssh.set_missing_host_key_policy (paramiko.AutoAddPolicy())
    ssh.connect (IP_ADDRESS, PORT, USER_NAME, PASSWORD)

    # Execute command & store the result
    stdin, stdout, stderr = ssh.exec_command (CMD)

    # Store standard output
    cmd_result = ''

    # store command result
    if 'hostname' in CMD : # hostname
        for line in stdout:
            cmd_result += line
    else:                  # IP address
        for line in stdout:
            for s in str(line).split (): 
                if '/24' in s:
                    cmd_result += s 
    print (cmd_result, end = ' ')
    f.write (str(cmd_result))

    f.close ()
    
    # Store error output
    cmd_err = ''
    for line in stdout:
        cmd_err += line
    if cmd_err == '' :
        print(end = '') # output nothing. 
    else :
        print (cmd_err)

    # close connection
    ssh.close ()
    del ssh, stdin, stdout, stderr


def editHost(IP_ADDRESS):
    # ----------------------------------------------------------
    # サーバーへの接続情報を設定
    IP_ADDRESS = '153.125.129.109'
    USER_NAME = 'root'
    PORT = 22
    PASSWORD = 'test_passwd'
    # サーバー上で実行するコマンドを設定
    CMD = 'cd ~ ; ip -4 a'
    # ----------------------------------------------------------
    runCMD_PW (IP_ADDRESS, USER_NAME, PASSWORD, PORT, CMD)

    CMD = 'hostname'
    runCMD_PW (IP_ADDRESS, USER_NAME, PASSWORD, PORT, CMD)

if __name__ == '__main__':
    IP_ADDRESS = '153.125.129.109'
    editHost (IP_ADDRESS)
