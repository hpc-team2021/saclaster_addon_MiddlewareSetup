
import sys
import time
import logging
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
    #ヘッドノード
    IP_ADDRESS = '133.242.50.16'
    PORT = 22
    USER = 'root'
    PASSWORD = 'test001pw'


    #ホストサーバに接続
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.WarningPolicy())

    #接続
    client.connect(IP_ADDRESS, PORT, USER, PASSWORD)

    #cmdの実行ここでインストール
    stdin, stdout, stderr = client.exec_command('yum -y install nfs-utils')
    #次の処理まで待機(一秒待つ)
    #time.sleep(5)
    #stdin, stdout, stderr = client.exec_command('yum -y remove nfs-utils')
    #time.sleep(5)
    #stdin, stdout, stderr = client.exec_command('yum list')

    print(stdout)

    # コマンド実行結果を変数に格納
    cmd_result = ''
    for line in stdout:
        cmd_result += line

    # 実行結果を出力
    print(cmd_result)

    #コネクションを閉じる
    client.close()
    del client, stdin, stdout, stderr

if __name__ == '__main__':
    packInstall ()

#プログレスバー
import time
from tqdm import tqdm
 
for i in tqdm(range(100)):
    time.sleep(0.01)
