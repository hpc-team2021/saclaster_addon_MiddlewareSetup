import os
import sys
import time
import logging

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
    # クラスターのID情報を取得する
    get_cluster_serever_info    = get(url_list[zone] + sub_url[0], auth_res)
    get_cluster_disk_info       = get(url_list[zone] + sub_url[1], auth_res)
    get_cluster_switch_info     = get(url_list[zone] + sub_url[2], auth_res)
    get_cluster_interface_info  = get(url_list[zone] + sub_url[3], auth_res)
    get_cluster_bridge_info     = get(url_list[zone] + sub_url[4], auth_res)
    get_cluster_tag_info        = get(url_list[zone] + sub_url[5], auth_res)
    get_cluster_appliance_info  = get(url_list[zone] + sub_url[6], auth_res)
    get_cluster_power_info      = get(url_list[zone] + sub_url[7], auth_res)


    # スイッチの作成
    param = {
        "Switch":{
            "Name":'testSwitch',
            "Tags":['tagInfo: cluster ID']
        },
        "Count":0
    }
    switch_response = post(url_list[zone] + sub_url[2], auth_res, param)
    check,msg = res_check(switch_response, "post")

    print('スイッチの作成')

    # サーバの設置
    com_index = False
    param = {
        "Server":{
            "Name":'testNode',
            "ServerPlan":{
                "ID":100001001
            },
            "Tags":['tagInfo: cluster ID', 'tagInfo: Data modified'],
            # "ConnectedSwitches":[{"Scope":"shared"}]
             "ConnectedSwitches":[{"ID": switch_response['Switch']['ID']}]
        },
        "Count":0
    }
    server_response = post(url_list[zone] + sub_url[0], auth_res, param)
    check, msg = res_check(server_response, "post", com_index)

    print('サーバの作成（スイッチに接続する）')

    # ディスクの追加
    paramIPAddr = '192.168.100.1'
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
            "UserIPAddress": paramIPAddr,
            "UserSubnet": {
                "DefaultRoute": '192.168.100.254',
                "NetworkMaskLen": 24,
            }
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

    # # インターフェースの追加
    # add_nic_param = {
    #     "Interface":{
    #         "Server":{
    #             "ID":str(server_response["Server"]["ID"])
    #         }
    #     },
    #     "Count":0
    # }
    # add_nic_response = post(url_list[zone] + sub_url[3], auth_res, add_nic_param)
    # check,msg = res_check(add_nic_response, "post")

    # print('インターフェースを追加（使わないからこの処理なくしてもいいかも）')

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

    print('ディスクの追加が完了するまで終了')


    # ディスクの情報の書き換え（IPアドレス）
    paramIPAddr = '192.168.100.1'
    param = {
        "UserIPAddress": paramIPAddr,
        "UserSubnet": {
            "DefaultRoute": '192.168.100.254',
            "NetworkMaskLen": 24
      }
    }
    diskID = disk_res["Disk"]['ID']
    putUrl = url_list[zone] + sub_url[1] + '/' + diskID + '/config'
    diskConf_res = put(putUrl, auth_res, param)
    check,msg = res_check(diskConf_res, "put")

    # クラスターのID情報を取得する
    get_cluster_serever_info    = get(url_list[zone] + sub_url[0], auth_res)
    get_cluster_disk_info       = get(url_list[zone] + sub_url[1], auth_res)
    get_cluster_switch_info     = get(url_list[zone] + sub_url[2], auth_res)
    get_cluster_interface_info  = get(url_list[zone] + sub_url[3], auth_res)
    get_cluster_bridge_info     = get(url_list[zone] + sub_url[4], auth_res)
    get_cluster_tag_info        = get(url_list[zone] + sub_url[5], auth_res)
    get_cluster_appliance_info  = get(url_list[zone] + sub_url[6], auth_res)
    get_cluster_power_info      = get(url_list[zone] + sub_url[7], auth_res)
    print('ディスクの書き換えによりIPアドレスを割り振り')


    # # スイッチの作成
    # del param
    # param = {
    #     "Switch":{
    #         "Name":'testSwitch',
    #         "Tags":['tagInfo: cluster ID']
    #     },
    #     "Count":0
    # }
    # switch_response = post(url_list[zone] + sub_url[2], auth_res, param)
    # check,msg = res_check(switch_response, "post")

    # # スイッチの接続
    # sub_url_con = "/interface/" + str(add_nic_response["Interface"]["ID"]) + "/to/switch/" + str(switch_response["Switch"]["ID"])
    # connect_switch_response = put(url_list[zone] + sub_url_con, auth_res)
    # check,msg = res_check(connect_switch_response, "put")




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