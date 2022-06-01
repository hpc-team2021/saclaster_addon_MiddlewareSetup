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
from get_cluster_info import get_cluster_info
from pack_install import pack_install
from load_addon_params import load_addon_params
from port_open import port_open
from daemon_start import daemon_start

def monitor_setup(cls_bil, clusterID, params, nodePassword, jsonAddonParams, serviceType, serviceName):

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
    monitor_daemon_start (headIp, nComputenode, nodePassword, serviceType, serviceName, OSType, addonJson = jsonAddonParams)

####################
#  Monitor Daemon  #
####################
def monitor_daemon_start (headIp, nComputenode, nodePassword, serviceType, serviceName, OSType, addonJson):

    for index in range(nComputenode+1):
        if index == 0:
            targetIp = headIp
            daemon_start (addonJson, headIp, targetIp, nodePassword, serviceType, serviceName, OSType)
        else:
            targetIp = '192.168.100.' + str(index)
            daemon_start (addonJson, headIp, targetIp, nodePassword, serviceType, serviceName, OSType)

if __name__ == '__main__':
    params = get_cluster_info()
    clusterID = '711333'

    # Read json file for gaglia configuration 
    jsonAddonParams = load_addon_params ()
    monitor_setup(clusterID, params, nodePassword = 'test', jsonAddonParams = jsonAddonParams, serviceType = 'Monitor', serviceName = 'Ganglia')

