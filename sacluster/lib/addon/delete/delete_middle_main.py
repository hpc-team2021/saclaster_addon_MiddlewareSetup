import sys
import json
import os
import datetime
import logging
from tabnanny import check
from tqdm import tqdm
from concurrent import futures
from os.path import expanduser

home_path = expanduser("~") + "/sacluster"

logger = logging.getLogger("addon").getChild(os.path.basename(__file__))

os.chdir(os.path.dirname(os.path.abspath(__file__)))
common_path = os.path.abspath("../../..")
sys.path.append(common_path + "/lib/auth")
from auth_func_pro import authentication_cli
sys.path.append(common_path + "/lib/def_conf")
from load_external_data import external_data
from config_function import conf_pattern_2
sys.path.append(common_path + "/lib/others")
from info_print import printout
sys.path.append (common_path + "/lib/addon/mylib")
from sshconnect_main import sshConnect_main, headConnect, computeConnect, computeConnect_IP
from get_cluster_info     import get_cluster_info
from load_addon_params    import load_addon_params

# #読みたいjsonファイルのパス
fileName = common_path + "/lib/addon/delete/delete.json"

def delete_middle_main(cluster_id, info_list, f):

    logger.debug("check MPI state of the cluster : " + str(cluster_id))
    middle_state = get_middle_state(cluster_id)

    if middle_state == True:
        ans = conf_pattern_2("Force MPI calculation to abort?", ["yes", "no"], "no", info_list = info_list, fp = f)
        if ans == "yes":
            print("計算を中断させるコマンドがあればそれを送る")
            pass
        else:
            printout("Stop processing.", info_type = 0, info_list = info_list, fp = f)
            sys.exit()

#############################################################
########################## methods ##########################
#############################################################

def get_middle_state(cluster_id):
    # json読み込み
    json_open = open(fileName, 'r')
    jsonFile = json.load(json_open)

    params = get_cluster_info ()

    # printout("Cluster ID:%s is now operational. Please enter the following information." % cluster_id)
    nodePassword = get_user_pass()
    headInfo, OSType, nComputenode = sshConnect_main(cluster_id, params, nodePassword)
    
    print("MPIのコマンドで計算途中かどうか確認する")
    logger.debug("MPI command to check if the calculation is in progress.")
    HEAD_CMD    = jsonFile ["MPI"]
    headConnect(headInfo, HEAD_CMD)
    
    temp = False # 仮置き、標準出力から判断する変数にしたい

    if temp:
        print("計算途中の場合、経過時間と推定必要時間の提示")
        print("標準出力の内容が欲しいけど、現状ない...")
        middle_state = True
    else:
        middle_state = False

    return middle_state


def get_user_pass():
    while True:
        password = input('Enter cluster Password : ')
        password = password.strip()
        if password != '':
            break
    return password


#############################################################
######################### Test code #########################
#############################################################

if __name__ == '__main__':
    # パラメータ作成
    cluster_id = ""
    info_list = [1,0,0,1]
    fp_filename = "test.txt"
    f = open(home_path + "/res/" + fp_filename, "w")

    # テストコード
    delete_middle_main(cluster_id, info_list, f)