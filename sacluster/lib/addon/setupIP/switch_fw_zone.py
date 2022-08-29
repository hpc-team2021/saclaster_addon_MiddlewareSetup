import json
import sys
import time
import logging
import os
os.chdir(os.path.dirname(os.path.abspath(__file__)))
common_path = os.path.abspath("../../..")

# 読みたいjsonファイルのパス
fileName = common_path + '/lib/addon/setupIP/switch_fw_zone.json'

sys.path.append (common_path + "/lib/addon/mylib")
from sshconnect_main import sshConnect_main, headConnect, computeConnect, computeConnect_IP
from get_cluster_info     import get_cluster_info
from load_addon_params    import load_addon_params

sys.path.append (common_path + "/lib/addon/others")
from info_print import printout

#ローカルのネットワークのFireWallのゾーンを指定したゾーンに変更する
def switch_fw_zone(addon_info, fp, info_list):
    printout (
        comment = "(Start) : Setting Firewall",
        info_list = info_list,
        fp = fp
    )

    # jsonファイる読み込み
    json_open = open(fileName, 'r')
    jsonFile = json.load(json_open)

    # 今回の処理に必要な変数のみを取り出す
    clusterID       = addon_info["clusterID"]
    IP_list         = addon_info["IP_list"]
    params          = addon_info["params"]
    nodePassword    = addon_info["node_password"]

    #クラスタ情報読み込み
    headInfo, OSType, nComputenode = sshConnect_main(clusterID, params, nodePassword)

    #実行コマンドの読み込み
    HEAD_CMD = jsonFile['Firewall'][OSType]['Head']
    COMPUTE_CMD = jsonFile["Firewall"][OSType]["Compute"] 

    #SSH接続
    headConnect(headInfo, HEAD_CMD)
    computeConnect(headInfo,IP_list,COMPUTE_CMD)

    printout (
        comment = "(Done)  : Setting Firewall",
        info_list = info_list,
        fp = fp
    )
if __name__ == '__main__':
    params              = get_cluster_info ()
    json_addon_params   = load_addon_params ()

    cls_bil  = []
    ext_info = []
    info_list = [1,0,0,1]
    fp = []

    addon_info = {
        "clusterID"         : "997684",                 # !!! 任意のクラスターIDに変更 !!!
        "IP_list"           :{                          # コンピュートノードの数に合わせて変更
            "front" : ['192.168.3.1', '192.168.3.2'],
            "back"  : ['192.169.3.1', '192.169.3.2']
        },
        "params"            : params,
        "json_addon_params" : json_addon_params,
        "node_password"     : "test01pw"                    # 設定したパスワードを入力
    }

    switch_fw_zone  (addon_info, fp, info_list)