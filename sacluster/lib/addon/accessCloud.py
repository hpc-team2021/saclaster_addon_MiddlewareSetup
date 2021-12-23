import os
import sys
import time
import logging
import paramiko
import string

from numpy.lib.shape_base import tile

logger = logging.getLogger("sacluster").getChild(os.path.basename(__file__))

from os.path import expanduser
home_path = expanduser("~") + "/sacluster"
os.makedirs(home_path, exist_ok = True)

common_path = "../.."
os.chdir(os.path.dirname(os.path.abspath(__file__)))

sys.path.append(common_path + "/lib/others")
from API_method import get, post, put, delete
import get_params
import get_cluster_id
from info_print import printout

sys.path.append(common_path + "/lib/auth")
from auth_func_pro import authentication_cli

sys.path.append(common_path + "/lib/def_conf")
from load_external_data import external_data

def runCMD_PW(IP_ADDRESS, USER_NAME, PASSWORD, CMD):
    PORT = 22 # SFTPのポート        

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(IP_ADDRESS, PORT, USER_NAME, PASSWORD)

    # コマンド実行と結果の出力
    stdin, stdout, stderr = ssh.exec_command(CMD)

    cmd_result = ''     # コマンドの結果出力
    for line in stdout:
        for s in str(line).split(): 
            if '/24' in s:
                cmd_result += s
    print(cmd_result)
    print('Standard Input Fin')
    
    cmd_err = ''        # エラー出力
    for line in stdout:
        cmd_err += line
    print(cmd_err)

    ssh.close()
    del ssh, stdin, stdout, stderr

def main(argv):
    # 認証周り
    auth_res = authentication_cli(fp = '', info_list = [1,0,0,0], api_index = True)
    max_workers = 1
    fp = ""
    monitor_info_list = [1,0,0,0]

    # URLの設定
    url_list = {}
    head_zone = 'is1b'
    zone      = 'is1b'
    zone_list = ['is1b']
    for zone in zone_list:
        url_list[zone] = "https://secure.sakura.ad.jp/cloud/zone/"+ zone +"/api/cloud/1.1"
    head_url = "https://secure.sakura.ad.jp/cloud/zone/"+ head_zone +"/api/cloud/1.1"
    sub_url = ["/server","/disk","/switch","/interface","/bridge","/tag","/appliance","/power"]

    # クラスターのID情報を取得する
    # get_cluster_id_info = get(url_list[zone] + sub_url[0], auth_res)
    
    param = {
        "Filter":{
            "ServerPlan.ID":100001001
        }
    }

    res = get (url_list[zone] + sub_url[0], auth_res, param)

    #print (res)

    # ----------------------------------------------------------
    # サーバーへの接続情報を設定
    IP_ADDRESS = '153.125.129.109'
    USER_NAME = 'root'
    PORT = 22
    PASSWORD = 'test_passwd'
    # サーバー上で実行するコマンドを設定
    CMD = 'cd ~ ; ip -4 a | grep 153.125.*/24'
    # ----------------------------------------------------------
    runCMD_PW (IP_ADDRESS, USER_NAME, PASSWORD, CMD)
   
def res_check(res, met,com_index=False):
    met_dict = {"get": "is_ok", "post": "is_ok", "put": "Success","delete": "Success"}
    index = met_dict[met]
    msg = ""
    logger.debug("confirm API request(" + str(met) + ")")
    if (index in res.keys()):
        if res[index] == True:
            logger.debug("API processing succeeded")
            check = True
            return check, msg
        else:
            logger.warning("API processing failed")
            if com_index == False:
                check = False
                return check, msg
            else:
                msg = list("Error:")
                check = False
                return check, msg

    elif ("is_fatal" in res.keys()):
        logger.warning("API processing failed")
        if com_index == False:
            check = False
            return check, msg
        else:
            msg = ["Status:" + res["status"], "Error:" + res["error_msg"]]
            check = False
            return check, msg

if __name__ == '__main__':
    sys.exit(main(sys.argv))
