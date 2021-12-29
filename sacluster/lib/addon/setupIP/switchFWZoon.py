import os

os.chdir(os.path.dirname(os.path.abspath(__file__)))
common_path = os.path.abspath("../../..")

import paramiko 

#ローカルのネットワークのFireWallのzoonを指定したゾーンに変更する
def swhichFWZoom():
    #success = switchFWZoon("trusted")

    IP_ADDRESS = '133.242.50.16'
    PORT = 22
    USER = 'root'
    PRIVATE_KEY = 'test001pw'
   
    CMD1 = 'firewall-cmd --state'
    CMD2 = 'firewall-cmd --zone=<zoom名> --list-all'
    CMD3 = 'firewall-cmd --set-default-zone=<zoom名>'


#ホストサーバに接続
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.WarningPolicy())
#接続
    client.connect(IP_ADDRESS, PORT, USER, key_filename=PRIVATE_KEY)

# コマンドの実行
    stdin, stdout, stderr = client.exec_command(CMD1)
    stdin, stdout, stderr = client.exec_command(CMD2)
    stdin, stdout, stderr = client.exec_command(CMD3)

# ssh接続断
    client.close()
    del client, stdin, stdout, stderr

if __name__ == '__main__':
    swhichFWZoom ()

#FWサービスの有効化
#systemctl enable firewalld

#FWサービス起動
#systemctl start firewalld

#FW稼働状況
#firewall-cmd --state

#指定したzoonの設定確認
# firewall-cmd --zone=<zoom名> --list-all

#デフォルトゾーンの変更
#firewall-cmd --set-default-zone=<zoom名>