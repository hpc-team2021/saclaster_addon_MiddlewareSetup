## 現在のクラスター情報を取得して，そのデータを返すメソッド（関数）

import os
import sys
import time
import logging
import ast

from numpy.lib.shape_base import tile

logger = logging.getLogger("sacluster").getChild(os.path.basename(__file__))

from os.path import expanduser
home_path = expanduser("~") + "/sacluster"
os.makedirs(home_path, exist_ok = True)

os.chdir(os.path.dirname(os.path.abspath(__file__)))
common_path = os.path.abspath("../../..")

sys.path.append(common_path + "/lib/others")
from API_method import get, post, put, delete
import get_params
import get_cluster_id
sys.path.append(common_path + "/lib/auth")
from auth_func_pro import authentication_cli
sys.path.append(common_path + "/lib/def_conf")
from load_external_data import external_data

def getClusterInfo():
    # 認証周り
    auth_res = authentication_cli(fp = '', info_list = [1,0,0,0], api_index = True)

    # 同一IDのホスト名のリストをとってくる
    ext_info = external_data(auth_res, info_list = [1,0,0,0], fp = '')
    params = get_params.get_params(ext_info, auth_res, info_list = [1,0,0,0], f = '', api_index = True)
    params()

    return params



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
    sys.exit(getClusterInfo())
