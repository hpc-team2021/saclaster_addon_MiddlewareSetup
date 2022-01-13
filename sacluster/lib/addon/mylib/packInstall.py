
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

def packInstall():
    #管理ノード
    IP_ADDRESS1 = '133.242.50.16'
    PORT1 = 22
    USER1 = 'root'
    PASSWORD1 = 'test01pw'
    KYE='~/.ssh/id_rsa.pub'


    #管理ノードに接続
    headnode = paramiko.SSHClient()
    headnode.set_missing_host_key_policy(paramiko.WarningPolicy())

    print("hostnode connecting...")
    headnode.connect(hostname=IP_ADDRESS1, port=PORT1, username=USER1, password=PASSWORD1)
    print('hostnode connected')

#コマンド実行
    stdin, stdout, stderr = headnode.exec_command('hostname')
    time.sleep(1)
    hostname = stdout.read().decode()
    print('hostname_head = %s' % hostname)

    #管理->計算ノード
    #計算ノード
    IP_ADDRESS2 = '192.168.100.1'
    PORT2 = 22
    USER2 = 'root'
    PASSWORD2 = 'test01pw'

    head = (IP_ADDRESS1,PORT1)
    compute = (IP_ADDRESS2, PORT2)
    transport1 = headnode.get_transport()
    channel1 = transport1.open_channel("direct-tcpip", compute, head)
    computenode = paramiko.SSHClient()
    computenode.set_missing_host_key_policy(paramiko.WarningPolicy())

    print("compurenode connecting...")
    computenode.connect(hostname=IP_ADDRESS2,username=USER2,password=PASSWORD2,sock=channel1)
    print('computenode connected')

#コマンド実行
    (stdin, stdout, stderr) = computenode.exec_command('yum -y install ypbind')
    time.sleep(1)
    hostname = stdout.read().decode()
    print('hostname_compute = %s' % hostname)

    # コマンド実行結果を変数に格納
    #cmd_result = ''
    #for line in stdout:
     #   cmd_result += line

    # 実行結果を出力
    #print(cmd_result)

    #コネクションを閉じる
    headnode.close()
    computenode.close()
    del headnode, computenode, stdin, stdout, stderr

if __name__ == '__main__':
    packInstall ()

