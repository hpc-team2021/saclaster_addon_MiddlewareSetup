import json
from operator import index
import re
import string
import sys
import time
import logging
import os
import paramiko

# User defined Library
os.chdir(os.path.dirname(os.path.abspath(__file__)))
common_path = os.path.abspath("../../..")
fileName = common_path + '\\lib\\addon\\setupMpi\\mpich.json'

sys.path.append(common_path + "/lib/addon/mylib")
from load_addon_params import load_addon_params
from get_cluster_info import get_cluster_info

#################
# Main Programm #
#################
def setup_mpi (head_ip, n_computenode, node_password, json_addon_params, os_type):
    print ('Working on MPI Setup ...')

    # Read json file for gaglia configuration 
    json_open = open(fileName, 'r')
    json_mpi = json.load(json_open)

    # Ganglia Setting
    mpi_head (head_ip, n_computenode, node_password, json_addon_params, json_mpi, os_type)
    mpi_comp (head_ip, n_computenode, node_password, json_addon_params, json_mpi, os_type)

    print ("MPI Setting is done")
# % End of setup_mpi ()

###########################
# MPI Setting on Headnode #
###########################
def mpi_head (head_ip, n_computenode, node_password, json_addon_params, json_mpi, os_type): 
    # Configuration Setting for Headnode
    head_info = {
        'IP_ADDRESS':head_ip,
        'PORT'      :22,
        'USER'      :'root',
        'PASSWORD'  :node_password
    }
    
    # Connect to Headnode
    headnode = paramiko.SSHClient()
    headnode.set_missing_host_key_policy(paramiko.WarningPolicy())
    print("Connecting to headnode...")
    headnode.connect(hostname=head_info['IP_ADDRESS'], port=head_info['PORT'], username=head_info['USER'], password=head_info['PASSWORD'])
    print('Connected')

    cmd_list = json_mpi[os_type]['command']['Head']
    for i, setting in enumerate(cmd_list):
        cmd = setting
        headnode.exec_command (cmd)

    headnode.close()
    del headnode
# % End of gangliaHead ()

##############################
# MPI Setting on computenode #
##############################
def mpi_comp (head_ip, n_computenode, node_password, json_addon_params, json_mpi, os_type):
     # Configuration Setting for Headnode
    head_info = {
        'IP_ADDRESS':head_ip,
        'PORT'      :22,
        'USER'      :'root',
        'PASSWORD'  :node_password
    }
    
    # Connect to Headnode
    headnode = paramiko.SSHClient()
    headnode.set_missing_host_key_policy(paramiko.WarningPolicy())
    print("Connecting to headnode...")
    headnode.connect(hostname=head_info['IP_ADDRESS'], port=head_info['PORT'], username=head_info['USER'], password=head_info['PASSWORD'])
    print('Connected')
    transport1 = headnode.get_transport()

    # Configuration Setting for Compute node
    for i_computenode in range(n_computenode):
        if i_computenode < 9:
            host = 'computenode00' + str(i_computenode)
        elif i_computenode < 99:
            host = 'computenode0' + str(i_computenode)
        else:
            host = 'computenode' + str(i_computenode)
        
        IP_ADDRESS2 = '192.168.100.' + str(i_computenode+1)
        comp_info = {
            'IP_ADDRESS':IP_ADDRESS2,
            'PORT'      :22,
            'USER'      :'root',
            'PASSWORD'  :node_password
        }

        # Connection to compute node
        compute = (comp_info ['IP_ADDRESS'], comp_info ['PORT'])
        channel1 = transport1.open_channel("direct-tcpip", compute, headnode)
        computenode = paramiko.SSHClient()
        computenode.set_missing_host_key_policy(paramiko.WarningPolicy())
        print("Connecting to compute node...")
        computenode.connect(hostname=comp_info['IP_ADDRESS'], username=comp_info['USER'], password=comp_info['PASSWORD'], sock=channel1)
        print('Connected')

        # Execute command
        cmd_list = json_mpi[os_type]['command']['Head']
        for i, setting in enumerate(cmd_list):
            cmd = setting
            computenode.exec_command (cmd)

        # close connection to compute node
        computenode.close()
        del computenode
    
    # close connection to head node
    headnode.close()
    del headnode

if __name__ == '__main__':
    params = get_cluster_info()
    clusterID = '711333'
    node_password = 'test'

    # Get headnode IP address & computenodes num
    head_ip  = "255.255.255.255"
    n_computenode = 0
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
                    os_type = params.cluster_info_all[clusterID]["clusterparams"]["server"][zone]["head"]["disk"][0]["os"]
                elif (clusterID in node_list[i]["Tags"][0]):
                    n_computenode += 1
                else:
                    pass
        else:
            pass

    # Read json file for gaglia configuration 
    json_addon_params = load_addon_params ()
    setup_mpi (head_ip, n_computenode, node_password, json_addon_params, os_type)
