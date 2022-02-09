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


def addon_main(clusterID):
    params = getClusterInfo ()
    jsonAddonParams = loadAddonParams ()

    setupIpEth1 (clusterID, params, nodePassword = 'test')
    editHost    (clusterID, params, nodePassword = 'test', jsonAddonParams = jsonAddonParams)
    swhichFWZone()
    portOpen    (clusterID, params, nodePassword = 'test', jsonAddonParams = jsonAddonParams, serviceType="Proxy"  , serviceName="Squid")
    proxySetup  (clusterID, params, nodePassword = 'test', jsonAddonParams = jsonAddonParams)
    # portOpen    (clusterID, params, nodePassword = 'test', jsonAddonParams = jsonAddonParams, serviceType="Monitor", serviceName="Ganglia")
    # monitorSetup ()

def addon_start ():
    print ("ミドルウェアの起動")
    # daemonStart ()

if __name__ == '__main__':
    clusterID = "927941"
    sys.exit (addon_main (clusterID))
