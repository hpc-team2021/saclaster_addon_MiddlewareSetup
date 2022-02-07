import sys
import json
import os
import datetime
import ipaddress
import logging
from tqdm import tqdm
from concurrent import futures
import time
import pprint

logger = logging.getLogger("sacluster").getChild(os.path.basename(__file__))

os.chdir(os.path.dirname(os.path.abspath(__file__)))
common_path = os.path.abspath("../..")
sys.path.append(common_path + "/lib/others")

from API_method import get, post, put, delete
from info_print import printout

sys.path.append(common_path + "/lib/addon/mylib")
from editHost import editHost
from getClusterInfo import getClusterInfo
from loadAddonParams import loadAddonParams
sys.path.append(common_path + "/lib/addon/setupIP")
from setupIpEth1 import setupIpEth1
import switchFWZone
sys.path.append(common_path + "/lib/addon/setupProxy")
from proxySetup import proxySetup


def addon_main(clusterID):

    print("アドオンの関数")
    params = getClusterInfo ()                                              # メモ：クラスター情報を取得して変数に入れました
    jsonAddonParams = loadAddonParams ()
    setupIpEth1 (clusterID, params, nodePassword = 'test')                  # メモ：コンピュートノードに対する操作確認できないから誰か確認お願いします
    editHost (clusterID, params, jsonAddonParams, nodePassword = 'test')
    # swhichFWZone ()                                                       # <-- 森保さん，これ関数名変じゃないですか？インポート文も修正しておいてください
    # portOpen (jsonAddonParams)
    proxySetup (clusterID, params, nodePassword = 'test')                   # メモ：ファイアウォールの設定してないとコンピュートノードから外部に通信できないので注意
    # monitorSetup ()

def addon_start ():
    print ("ミドルウェアの起動")
    # daemonStart ()

if __name__ == '__main__':
    clusterID = "983867"
    sys.exit ( addon_main (clusterID) )
