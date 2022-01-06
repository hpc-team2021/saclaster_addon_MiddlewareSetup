
import sys
import time
import logging
import os
os.chdir(os.path.dirname(os.path.abspath(__file__)))
common_path = os.path.abspath("../../..")

import paramiko 

#ローカルのネットワークのFireWallのゾーンを指定したゾーンに変更する
def swhichFWZoom():
    
    IP_ADDRESS = '133.242.50.16'
    PORT = 22
    USER = 'root'
    PASSWORD = 'test001pw'

    CMD1 = 'firewall-cmd --state'
    CMD2 = 'firewall-cmd --get-active-zones'
    CMD3 = 'firewall-cmd --zone=trusted --change-interface=eth1'


#ホストサーバに接続
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.WarningPolicy())

#接続
    client.connect(IP_ADDRESS, PORT, USER, PASSWORD)

# コマンドの実行
#FW稼働状況
    #stdin, stdout, stderr = client.exec_command(CMD1)

#アクティブzoneの設定確認 
    #stdin, stdout, stderr = client.exec_command(CMD2)

#インターフェースのzone変更
    stdin, stdout, stderr = client.exec_command(CMD3)

# コマンド実行結果を変数に格納
    cmd_result = ''
    for line in stdout:
        cmd_result += line

# 実行結果を出力
    print(cmd_result)

# ssh接続断
    client.close()
    del client, stdin, stdout, stderr

if __name__ == '__main__':
    swhichFWZoom ()

#FW稼働状況
#firewall-cmd --state

#指定したzoonの設定確認
# firewall-cmd --zone=<zoom名> --list-all

#デフォルトゾーンの変更
#firewall-cmd --set-default-zone=<zoom名>