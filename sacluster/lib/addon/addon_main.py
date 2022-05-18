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
from editHost           import editHost
from getClusterInfo     import getClusterInfo
from loadAddonParams    import loadAddonParams
from portOpen           import portOpen
sys.path.append(common_path + "/lib/addon/setupIP")
from setupIpEth1        import setupIpEth1
from switchFWZone       import switchFWZone
sys.path.append(common_path + "/lib/addon/setupProxy")
from proxySetup         import proxySetup
sys.path.append(common_path + "/lib/addon/setupMoniter")
from monitorSetup       import monitorSetup

def addon_main(clusterID):
    params          = getClusterInfo ()
    jsonAddonParams = loadAddonParams ()
    nodePassword    = get_userPass()

    editHost    (clusterID, params, nodePassword, jsonAddonParams = jsonAddonParams)
    switchFWZone(clusterID, params, nodePassword, jsonAddonParams = jsonAddonParams)

    portOpen    (clusterID, params, nodePassword, jsonAddonParams = jsonAddonParams, serviceType="Proxy"  , serviceName="Squid")
    proxySetup  (clusterID, params, nodePassword, jsonAddonParams = jsonAddonParams, serviceType="Proxy"  , serviceName="Squid")

    portOpen    (clusterID, params, nodePassword, jsonAddonParams = jsonAddonParams, serviceType="Monitor", serviceName="Ganglia")
    monitorSetup(clusterID, params, nodePassword, jsonAddonParams = jsonAddonParams, serviceType="Monitor", serviceName="Ganglia")

def addon_start ():
    print ("ミドルウェアの起動")
    # daemonStart ()

def get_userPass():
    while True:
        Password = input('Enter cluster Password : ')
        Password = Password.strip()
        if Password != '':
            break
    return Password

if __name__ == '__main__':
    clusterID = "779987"
    sys.exit (addon_main (clusterID))
