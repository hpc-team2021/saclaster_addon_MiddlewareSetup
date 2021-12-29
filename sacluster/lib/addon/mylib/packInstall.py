#import subprocess
#subprocess.run(["ls"])

import os
os.chdir(os.path.dirname(os.path.abspath(__file__)))
common_path = os.path.abspath("../../..")

#import sys
#sys.path.append(common_path + "/lib/auth")
#from auth_func_pro import authentication_cli

#sys.path.append (common_path + "/lib/others")
#from API_method import get, post, put, delete
#from info_print import printout

import paramiko 

def packInstall():
    IP_ADDRESS = '133.242.50.16'
    PORT = 22
    USER = 'root'
    PASSWORD = 'test001pw'


    #ホストサーバに接続
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.WarningPolicy())

    #接続
    client.connect(IP_ADDRESS, PORT, USER, PASSWORD)

    #cmdの実行ここでインストール?
    stdin, stdout, stderr = client.exec_command('yum list')

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
    IP_ADDRESS = '153.125.129.109'
    packInstall ()