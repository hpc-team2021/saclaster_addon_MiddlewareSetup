from distutils.log import info
from socket import IP_MULTICAST_LOOP
import sys
import os
import json

os.chdir(os.path.dirname(os.path.abspath(__file__)))
common_path = os.path.abspath("../../..")

# #読みたいjsonファイルのパス
fileName = common_path + "/lib/addon/satupIP/edit_host.json"

sys.path.append (common_path + "/lib/addon/satupIP")
from sshconnect_main import sshConnect_main, headConnect, computeConnect, computeConnect_IP
from get_cluster_info     import get_cluster_info
from load_addon_params    import load_addon_params

sys.path.append (common_path + "/lib/others")
from info_print import printout

def edit_host(addon_info, fp, info_list):
    print ("\n")
    printout (comment = "(Start) : Setting hosts file", info_list = info_list, fp = fp)

    # jsonファイル読み込み
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

    # コマンド作成
    CMD = [cmd_main + ' "' + '192.168.0.1  headnode' + clusterID + '" > ' + target_file]
    for i, IP in enumerate(IP_list["front"]):
        i = i+1
        if i < 10:
            index = '00' + str (i)
        elif (i > 10) & (i < 100):
            index = '0' + str (i)
        CMD.append(cmd_main + ' "' + IP + '  computenode' + str(index) +  '" >> ' + target_file)
        Comp_CMD = [cmd_main + ' "' + 'computenode' + str(index) +  '" > ' + '/etc/hostname']
        Comp_CMD.append('systemctl restart systemd-hostnamed')
        computeConnect_IP(headInfo,IP,Comp_CMD)

    # 各ノードにコマンドを送る
    headConnect     (headInfo, CMD)
    computeConnect  (headInfo, IP_list, CMD)
    
    #hostname変更
    Head_CMD = [cmd_main + ' "' + 'headnode' + clusterID +  '" > ' + '/etc/hostname']
    Head_CMD.append('systemctl restart systemd-hostnamed')

    # 各ノードにコマンドを送る
    print ("Change Hostname")
    printout (
        comment = "Change Hostname", 
        info_list = info_list, 
        fp = fp
    )
    headConnect (headInfo, Head_CMD)
    printout (
        comment = "(Done)  : Setting hosts file",
        info_list = info_list,
        fp = fp
    )
    print ("\n")


# 単体テストのコード
if __name__ == "__main__":
    params              = get_cluster_info ()
    json_addon_params   = load_addon_params ()

    cls_bil  = []
    ext_info = []
    info_list = [1,0,0,1]
    fp = []

    addon_info = {
        "clusterID"         : "993208",                 # !!! 任意のクラスターIDに変更 !!!
        "IP_list"           :{                          # コンピュートノードの数に合わせて変更
            "front" : ['192.168.3.1', '192.168.3.2'],
            "back"  : ['192.169.3.1', '192.169.3.2']
        },
        "params"            : params,
        "json_addon_params" : json_addon_params,
        "node_password"     : "test01pw"                    # 設定したパスワードを入力
    }

    edit_host    (addon_info, fp, info_list)
