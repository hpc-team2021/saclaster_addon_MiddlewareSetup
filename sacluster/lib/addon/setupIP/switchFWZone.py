import sys
import os
import json

os.chdir(os.path.dirname(os.path.abspath(__file__)))
common_path = os.path.abspath("../../..")

#読みたいjsonファイルのパス
fileName = common_path + "/lib/addon/setupIP/switchFWZone.json"

sys.path.append(common_path + "/lib/addon/mylib")
from getClusterInfo import getClusterInfo

sys.path.append (common_path + "/lib/addon/mylib")
from getClusterInfo import getClusterInfo
from sshconnect_main import sshConnect_main, headConnect,computeConnect


#ローカルのネットワークのFireWallのゾーンを指定したゾーンに変更する
def switchFWZone(clusterID, params, nodePassword):
    #jsonファイる読み込み
    json_open = open(fileName, 'r')
    jsonFW = json.load(json_open)

    #クラスタ情報読み込み
    headInfo, OSType, nComputenode = sshConnect_main(clusterID, params, nodePassword)

    #実行コマンドの読み込み
    HEAD_CMD = jsonFW['Firewall'][OSType]['Head']
    COMPUTE_CMD = jsonFW["Firewall"][OSType]["Compute"] 

    #SSH接続
    headConnect(headInfo, HEAD_CMD)
    computeConnect(headInfo,nComputenode,COMPUTE_CMD)

if __name__ == '__main__':
    params = getClusterInfo ()
    switchFWZone(clusterID = '433442', params=params, nodePassword = 'test01pw')
