import sys
import os
import json

os.chdir(os.path.dirname(os.path.abspath(__file__)))
common_path = os.path.abspath("../../..")

# #読みたいjsonファイルのパス
fileName = common_path + "/lib/addon/mylib/edit_host.json"

sys.path.append (common_path + "/lib/addon/mylib")
from sshconnect_main import sshConnect_main, headConnect, computeConnect, computeConnect_IP
from get_cluster_info     import get_cluster_info
from load_addon_params    import load_addon_params

def edit_host(cls_bil, ext_info, cls_mid, addon_info):
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
    if 'CentOS' in OSType:
        os_name = 'CentOS'
    elif 'Ubuntu' in OSType:
        os_name = 'Ubuntu'
    cmd_main    = jsonFile ['hosts']['cmd']
    target_file = jsonFile ['hosts'][os_name]

    # headノードにコマンドを送る
    HEAD_CMD = [
        cmd_main + ' "' + '192.168.0.1  headnode" > ' + target_file,
        ]
    headConnect(headInfo, HEAD_CMD)

    # computeノードにコマンドを送る
    for i, IP in enumerate(IP_list["front"]):
        i = i+1
        if i < 10:
            index = '00' + str (i)
        elif (i > 10) & (i < 100):
            index = '0' + str (i)
        COMPUTE_CMD =  [
            cmd_main + ' "' + IP + '  computenode' + str(index) +  '" >> ' + target_file
            ]
        computeConnect_IP(headInfo,IP,COMPUTE_CMD)

# 単体テストのコード
if __name__ == "__main__":
    params              = get_cluster_info ()
    json_addon_params   = load_addon_params ()

    cls_bil = []
    ext_info = []
    cls_mid = []

    addon_info = {
        "clusterID"         : "534802",                 # 任意のクラスターIDに変更
        "IP_list"           :{                          # コンピュートノードの数に合わせて変更
            "front" : ['168.192.4.1', '168.192.4.2'],
            "back"  : ['169.192.4.1', '169.192.4.2']
        },
        "params"            : params,
        "json_addon_params" : json_addon_params,
        "node_password"     : "test"                    # 設定したパスワードを入力
    }
    edit_host    (cls_bil, ext_info, cls_mid, addon_info)
