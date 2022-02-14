import json
import string
import sys
import time
import logging
import os
import paramiko 

# from sacluster.lib.addon.mylib.editHost import Password
os.chdir(os.path.dirname(os.path.abspath(__file__)))
common_path = os.path.abspath("../../..")
from gangliaSetup import gangliaSetup

sys.path.append(common_path + "/lib/others")
from API_method import get, post, put, delete
sys.path.append(common_path + "/lib/auth")
from auth_func_pro import authentication_cli
sys.path.append(common_path + "/lib/addon/mylib")
from getClusterInfo import getClusterInfo
from packInstall import packInstall
from loadAddonParams import loadAddonParams
from portOpen import portOpen
from daemonStart import daemonStart

def monitorSetup(clusterID, params, nodePassword, jsonAddonParams, serviceType, serviceName):

    # Install Packege
    print ("Install " + serviceName + " packege")
    # packInstall (clusterID, params, nodePassword, jsonAddonParams, serviceType, serviceName)

    # Open Port
    print ("Open " + serviceName + "Port")
    # portOpen (clusterID, params, nodePassword, jsonAddonParams, serviceType, serviceName)
    
    # Get headnode IP address & computenodes num
    headIp  = "255.255.255.255"
    nComputenode = 0
    node_dict = params.get_node_info()
    disk_dict = params.get_disk_info()

    for zone, url in params.url_list.items():
        node_list = node_dict[zone]
        disk_list = list(disk_dict[zone].keys())
        if(len(node_list) != 0):
            for i in range(len(node_list)):
                print(clusterID + ':' + node_list[i]["Tags"][0] + ' | ' + node_list[i]['Name'])
                if (clusterID in node_list[i]["Tags"][0] and 'headnode' in node_list[i]['Name']):
                    headIp = node_list[i]['Interfaces'][0]['IPAddress']
                    OSType = params.cluster_info_all[clusterID]["clusterparams"]["server"][zone]["head"]["disk"][0]["os"]
                elif (clusterID in node_list[i]["Tags"][0]):
                    nComputenode += 1
                else:
                    pass
        else:
            pass

    # Setitng to the Selected Service
    if serviceName == 'Ganglia':
        gangliaSetup (headIp, nComputenode, nodePassword, jsonAddonParams, OSType)
    else:
        print ('Skip Monitor Tool Setting')
        return 0

    # Start & Enable Ganglia Daemon
    print ("Start & Enable Daemon")
    monitorDaemonStart (headIp, nComputenode, nodePassword, serviceType, serviceName, OSType, addonJson = jsonAddonParams)

####################
#  Monitor Daemon  #
####################
def monitorDaemonStart (headIp, nComputenode, nodePassword, serviceType, serviceName, OSType, addonJson):

    for index in range(nComputenode+1):
        if index == 0:
            targetIp = headIp
            daemonStart (addonJson, headIp, targetIp, nodePassword, serviceType, serviceName, OSType)
        else:
            targetIp = '192.168.100.' + str(index)
            daemonStart (addonJson, headIp, targetIp, nodePassword, serviceType, serviceName, OSType)

if __name__ == '__main__':
    params = getClusterInfo()
    clusterID = '983867'

    # Read json file for gaglia configuration 
    jsonAddonParams = loadAddonParams ()
    monitorSetup(clusterID, params, nodePassword = 'test', jsonAddonParams = jsonAddonParams, serviceType = 'Monitor', serviceName = 'Ganglia')

