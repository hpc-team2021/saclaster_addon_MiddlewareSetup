import sys
import os
import json

os.chdir(os.path.dirname(os.path.abspath(__file__)))
common_path = os.path.abspath("../../..")

import logging
logger = logging.getLogger("addon").getChild(os.path.basename(__file__))

# #読みたいjsonファイルのパス
fileName = common_path + "/lib/addon/setupProxy/proxy.json"

sys.path.append (common_path + "/lib/addon/mylib")
from sshconnect_main import sshConnect_main, headConnect, computeConnect, computeConnect_IP
from get_cluster_info import get_cluster_info
from load_addon_params import load_addon_params
from pack_install import pack_install
from daemon_start import daemon_start

sys.path.append (common_path + "/lib/others")
from info_print import printout


def proxy_setup(addon_info, f, info_list, service_name):
    print ("\n")
    printout (
        comment = "(Start) : Setting Proxy",
        info_list = info_list,
        fp = f
    )

    # jsonファイる読み込み
    json_open = open(fileName, 'r')
    jsonFile = json.load(json_open)

    jsonFName = common_path + "/lib/addon/setupProxy/"+ jsonFile["conf"][service_name]
    json_open = open(jsonFName, 'r')
    jsonFile = json.load(json_open)

    # 今回の処理に必要な変数のみを取り出す
    clusterID           = addon_info["clusterID"]
    IP_list             = addon_info["IP_list"]
    params              = addon_info["params"]
    json_addon_params   = addon_info["json_addon_params"]
    nodePassword        = addon_info["node_password"]

    #クラスタ情報読み込み
    headInfo, OSType, nComputenode = sshConnect_main(clusterID, params, nodePassword)

    # head 実行コマンドの読み込み,実行
    logger.debug("Run proxy install CMD in headnode.")
    HEAD_CMD    = jsonFile [OSType]["command"]["Head"]["install"]
    headConnect(headInfo, HEAD_CMD)

    logger.debug("Run proxy port open CMD in headnode.")
    HEAD_CMD    = jsonFile [OSType]["command"]["Head"]["port"]
    headConnect(headInfo, HEAD_CMD)

    logger.debug("Run proxy setup CMD in headnode.")
    HEAD_CMD    = jsonFile [OSType]["command"]["Head"]["setup"]
    headConnect(headInfo, HEAD_CMD)

    # head 実行コマンドの読み込み,実行
    logger.debug("Run proxy install CMD in compute.")
    HEAD_CMD    = jsonFile [OSType]["command"]["Compute"]["install"]
    computeConnect(headInfo, IP_list, HEAD_CMD)
    
    logger.debug("Run proxy port open CMD in compute.")
    HEAD_CMD    = jsonFile [OSType]["command"]["Compute"]["port"]
    computeConnect(headInfo, IP_list, HEAD_CMD)
    
    logger.debug("Run proxy setup CMD in compute.")
    HEAD_CMD    = jsonFile [OSType]["command"]["Compute"]["setup"]
    computeConnect(headInfo, IP_list, HEAD_CMD)

    printout (
        comment = "(Done)  : Setting Proxy\n",
        info_list = info_list,
        fp = f
    )


# 単体テスト
if __name__ == "__main__":
    params              = get_cluster_info ()
    json_addon_params   = load_addon_params ()

    addon_info = {
        "clusterID"         : "849936",                 # !!! 任意のクラスターIDに変更 !!!
        "IP_list"           :{                          # コンピュートノードの数に合わせて変更
            "front" : ['192.168.4.1', '192.168.4.2'],
            "back"  : ['192.169.4.1', '192.169.4.2']
        },
        "params"            : params,
        "json_addon_params" : json_addon_params,
        "node_password"     : "test"                    # 設定したパスワードを入力
    }

    proxy_setup(addon_info, service_name="squid")
