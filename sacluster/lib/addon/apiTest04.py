#### テストプログラム
#### 注意：windows環境のみで実行可能なコードになっています
#### 指定した名前の公開鍵が手元になければ，生成しさくらのクラウドに登録する
#### 登録した公開鍵を指定してサーバのディスク情報を書き換えする
#### ちなみに，うまく公開鍵の登録は行えていないので，誰か続き調査してほしい

from io import StringIO
import os
import sys
import time
import datetime
import logging
import subprocess

from numpy.lib.shape_base import tile

logger = logging.getLogger("sacluster").getChild(os.path.basename(__file__))

from os.path import expanduser
home_path = expanduser("~") + "/sacluster"
os.makedirs(home_path, exist_ok = True)

common_path = "../.."
os.chdir(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(common_path + "/lib/others")
from API_method import get, post, put, delete
sys.path.append(common_path + "/lib/auth")
from auth_func_pro import authentication_cli

def main(argv):
    # 認証周り
    auth_res = authentication_cli(fp = '', info_list = [1,0,0,0], api_index = True)
    max_workers = 1
    fp = ""
    monitor_info_list = [1,0,0,0]

    #set url
    url_list = {}
    head_zone = 'is1b'
    zone      = 'is1b'
    zone_list = ['is1b']
    for zone in zone_list:
        url_list[zone] = "https://secure.sakura.ad.jp/cloud/zone/"+ zone +"/api/cloud/1.1"
    head_url = "https://secure.sakura.ad.jp/cloud/zone/"+ head_zone +"/api/cloud/1.1"
    sub_url = ["/server","/disk","/switch","/interface","/bridge","/tag","/appliance","/power"]

    print('事前準備（認証，ゾーンのURLの指定）が完了')

    ######################################
    ############# SSHの生成 ##############
    ######################################

    # ローカルにカギがあるか確認
    sshkeyPath = os.path.expanduser('~/.ssh')
    sshkeyName = '/saclusterSshkey'

    get_cluster_sshkey_info = get(url_list[zone] + '/sshkey', auth_res)     # 登録された鍵とローカルのカギが同じ確認させる

    # 鍵がなければ生成して登録
    if(os.path.exists(sshkeyPath + sshkeyName) == False):
        proc = subprocess.run(['powershell', '-command', 'ssh-keygen -t rsa -b 4096 -f ' + sshkeyPath + sshkeyName], check=True)
        f = open(sshkeyPath + sshkeyName + '.pub', 'r')
        data = f.read()
        com_index = False
        dt_now_jst_aware = datetime.datetime.now(
            datetime.timezone(datetime.timedelta(hours=9))
        )
        param_SSHKeyName = 'saclusterSshkey' + str(dt_now_jst_aware)
        param = {
            "SSHKey":{
                "Name":param_SSHKeyName,
                "Description":"",
                "PublicKey":data
            }        
        }
        server_response = post(url_list[zone] + '/sshkey', auth_res, param)
        check, msg = res_check(server_response, "post", com_index)

    get_cluster_sshkey_info = get(url_list[zone] + '/sshkey', auth_res)     # 登録された鍵とローカルのカギが同じ確認させる
    # 使いたい鍵のIDを取得
    f       = open(sshkeyPath + sshkeyName + '.pub', 'r')
    data    = f.read()
    pubSSHKey_ID    = ''
    pubSSHKey_flag  = False
    for i, pubSSHKey in enumerate(get_cluster_sshkey_info['SSHKeys']):
        # print('ID: ' + pubSSHKey['ID'] + '   key: ' + pubSSHKey['PublicKey'])
        if(data == pubSSHKey['PublicKey']):
            pubSSHKey_ID    = pubSSHKey['ID']
            pubSSHKey_index = pubSSHKey['Index']
            pubSSHKey_flag  = True
    
    if(pubSSHKey_flag == False):
        com_index = False
        dt_now_jst_aware = datetime.datetime.now(
            datetime.timezone(datetime.timedelta(hours=9))
        )
        param_SSHKeyName = 'saclusterSshkey' + str(dt_now_jst_aware)
        param = {
            "SSHKey":{
                "Name":param_SSHKeyName,
                "Description":"",
                "PublicKey":data
            }        
        }
        server_response = post(url_list[zone] + '/sshkey', auth_res, param)
        check, msg = res_check(server_response, "post", com_index)


    ######################################
    ############ サーバの設置 ############
    ######################################

    # # スイッチの作成
    # param = {
    #     "Switch":{
    #         "Name":'testSwitch',
    #         "Tags":['tagInfo: cluster ID']
    #     },
    #     "Count":0
    # }
    # switch_response = post(url_list[zone] + sub_url[2], auth_res, param)
    # check,msg = res_check(switch_response, "post")
    # print('スイッチの作成')


    # サーバの設置
    com_index = False
    param = {
        "Server":{
            "Name":'testNode',
            "ServerPlan":{
                "ID":100001001
            },
            "Tags":['tagInfo: cluster ID', 'tagInfo: Data modified'],
            "ConnectedSwitches":[{"Scope":"shared"}]
            #  "ConnectedSwitches":[{"ID": switch_response['Switch']['ID']}]
        },
        "Count":0
    }
    server_response = post(url_list[zone] + sub_url[0], auth_res, param)
    check, msg = res_check(server_response, "post", com_index)
    print('サーバの作成（スイッチに接続する）')


    # ディスクの追加
    # paramIPAddr = '192.168.100.1'
    param_SSHKeys   = 'ID|SSHKeys[' + str(pubSSHKey_index) + ']'
    param = {
        "Disk":{
            "Name":'testNode',
            "Plan":{
                "ID":4},    # SSD:4, HHD:2
            "Connection":'virtio',
            "SizeMB":20480,     # ディスク容量(MB)
            "SourceArchive":{
                "Availability": "available",
                # "ID":'113200758639'     # OS のID(Cent7.8)
                # "ID":'113200980882'     # OS のID(Cent7.8)
                "ID":'113300112273'     # OS のID(Cent7.8)
            },
        },
        "Config":{
            "Password":'test',
            "HostName":'test',
            "SSHKey": {
                param_SSHKeys:{
                    "ID": pubSSHKey_ID
                }
            },
            # "UserIPAddress": paramIPAddr,
            # "UserSubnet": {
            #     "DefaultRoute": '192.168.100.254',
            #     "NetworkMaskLen": 24,
            # }
        }
    }
    disk_res = post(url_list[zone] + sub_url[1], auth_res, param)
    check,msg = res_check(disk_res, "post")
    print('ディスクの追加（オーダーを出しただけ）まで終了')


    # ディスクとサーバの接続
    url_disk = "/disk/" + str(disk_res["Disk"]["ID"]) + "/to/server/" + str(server_response["Server"]["ID"])
    server_disk_res = put(url_list[zone] + url_disk, auth_res)
    check,msg = res_check(server_disk_res, "put")
    print('サーバとディスクの接続')


    # ディスク状態が利用可能になるまで待ち続けるコード
    while True:
        get_cluster_disk_info = get(url_list[zone] + sub_url[1], auth_res)
        for i in range(len(get_cluster_disk_info['Disks'])):
            str_i = str(i)
            k = get_cluster_disk_info['Disks'][i]
            if k['ID'] == disk_res['Disk']['ID']:
                diskState = k['Availability']
                break

        if diskState == 'available':
            print("it's OK! Available!")
            break
        print('diskState is ' + diskState + ' ... Please wait...')
        time.sleep(10)
    print('ディスクの追加処理が完了')


    # ディスクの情報の書き換え（IPアドレス）
    paramIPAddr     = '192.168.100.1'
    param_SSHKeys   = 'ID|SSHKeys[' + str(pubSSHKey_index) + ']'
    param = {
        "SSHKey": {
            param_SSHKeys:{
                "ID": pubSSHKey_ID
            }
        },
    #     "UserIPAddress": paramIPAddr,
    #     "UserSubnet": {
    #         "DefaultRoute": '192.168.100.254',
    #         "NetworkMaskLen": 24
    #   }
    }
    diskID = disk_res["Disk"]['ID']
    putUrl = url_list[zone] + sub_url[1] + '/' + diskID + '/config'
    diskConf_res = put(putUrl, auth_res, param)
    check,msg = res_check(diskConf_res, "put")



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


