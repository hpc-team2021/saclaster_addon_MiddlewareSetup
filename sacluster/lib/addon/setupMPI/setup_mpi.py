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

# Changing standard output color for exception error
RED = '\033[31m'
END = '\033[0m'

sys.path.append(common_path + "/lib/addon/mylib")
from load_addon_params import load_addon_params
from get_cluster_info import get_cluster_info

sys.path.append(common_path + "/lib/addon/setypMpi")
from add_user import add_user_main
from ssh_setup import ssh_setup

############
#   MPI    #
############
def setup_mpi (addon_info, f, info_list, mpi_info):
    if (mpi_info["index"] == True):
        if (mpi_info["type"] == "mpich"):
            setup_mpich (
                addon_info = addon_info,
                f = f,
                info_list = info_list,
                service_name = mpi_info["type"]   
            )

#################
# MPICH Programm #
#################
def setup_mpich (addon_info, f, info_list, service_name):
    print ('Start: (MPI Setting)')
    # Variable
    cluster_id           = addon_info["clusterID"]
    params              = addon_info["params"]
    node_password        = addon_info["node_password"]
    ip_list         = addon_info["IP_list"]

    # Get info
    head_ip, os_type, n_computenode = get_info (cluster_id = cluster_id, params = params)

    # Read json file for gaglia configuration 
    try:
        json_open = open(fileName, 'r')
    except OSError as err:
        print (RED + "Fialed to open file: {}" .format(fileName))
        print ("Error type: {}" .format(err))
        print ("Exit rogramm" + END)
        sys.exit ()
    try:
        cmd_mpi = json.load(json_open)
    except json.JSONDecodeError as err:
        print (RED + "Fialed to decode JSON file: {}" .format(fileName))
        print ("Error type: {}" .format(err))
        print ("Exit programm" + END)
        sys.exit ()

    # Creating a new user for mpi
    add_user_main (
        head_ip = head_ip, 
        n_computenode = n_computenode, 
        node_password = node_password, 
        ip_list = ip_list,
        os_type = os_type
        )
        
    # SSH key seting for inter connection
    ssh_setup(
        head_ip = head_ip,
        ip_list = ip_list, 
        node_password = node_password,
        os_type = os_type
        )
    
    # Ganglia Setting for the head node
    mpi_head (
        head_ip = head_ip,
        node_password = node_password,
        cmd_mpi = cmd_mpi,
        os_type = os_type
        )
    
    # Ganglia Setting for the compute nodes
    mpi_comp (
        head_ip = head_ip,
        ip_list = ip_list,
        node_password = node_password,
        cmd_mpi = cmd_mpi,
        os_type = os_type
        )

    print (" Done: (MPI setting)")
# % End of setup_mpi ()

###########################
# MPI Setting on Headnode #
###########################
def mpi_head (head_ip, node_password, cmd_mpi, os_type): 
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
    print("Connecting to headnode ...")
    try:
        headnode.connect(
            hostname = head_info['IP_ADDRESS'],
            port = head_info['PORT'],
            username = head_info['USER'],
            password = head_info['PASSWORD']
        )
    except Exception as err:
        print (RED + "Fialed to connect to headnode")
        print ("Error type: {}" .format(err))
        print ("Exit programm" + END)
        sys.exit ()
    print('Connected')

    cmd_list = cmd_mpi[os_type]['command']['Head']['rep']
    for i, cmd in enumerate(cmd_list):
        try:
            headnode.exec_command (cmd)
        except paramiko.SSHException as err:
            print (RED + "Failed to excute command on headnode")
            print ("Error Type: {}" .format (err))
            print ("Exit Programm" + END)
            sys.exit ()
    headnode.close()
    del headnode
# % End of gangliaHead ()

##############################
# MPI Setting on computenode #
##############################
def mpi_comp (head_ip, ip_list, node_password, cmd_mpi, os_type):
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
    print("Connecting to headnode ...")
    try:
        headnode.connect(
            hostname = head_info['IP_ADDRESS'],
            port = head_info['PORT'],
            username = head_info['USER'],
            password = head_info['PASSWORD']
        )
    except Exception as err:
        print (RED + "Fialed to connect to headnode")
        print ("Error type: {}" .format(err))
        print ("Exit programm")
        sys.exit ()
    print('Connected')
    
    # Configuration Setting for Compute node
    transport1 = headnode.get_transport()
    head = (head_info['IP_ADDRESS'], head_info['PORT'])
    for ip_compute in ip_list["front"]:
        IP_ADDRESS2 = ip_compute
        comp_info = {
            'IP_ADDRESS':IP_ADDRESS2,
            'PORT'      :22,
            'USER'      :'root',
            'PASSWORD'  :node_password
        }

        # Connection to compute node
        compute = (comp_info ['IP_ADDRESS'], comp_info ['PORT'])
        try:
            channel1 = transport1.open_channel("direct-tcpip", compute, head)
        except Exception as err:
            print (RED + "Failed to open channel to compute_node " + str(ip_compute))
            print ("Error type: {}" .format(err))
            print ("Exit programm" + END)
            sys.exit ()
        computenode = paramiko.SSHClient()
        computenode.set_missing_host_key_policy(paramiko.WarningPolicy())
        print("Connecting to compute node...")
        try:
            computenode.connect(
                hostname = comp_info['IP_ADDRESS'],
                username = comp_info['USER'],
                password = comp_info['PASSWORD'],
                sock = channel1,
                auth_timeout = 300
                )
        except Exception as err:
            print (RED + "Failed to connect to compute_node " + str(ip_compute))
            print ("Error type {}" .format(err))
            print ("Exit programm" + END)
            sys.exit ()
        print('Connected')

        # Execute command
        cmd_list = cmd_mpi[os_type]['command']['Compute']['rep']
        for i, cmd in enumerate(cmd_list):
            try:
                computenode.exec_command (cmd)
            except paramiko.SSHException as err:
                print (RED + "Fialed to excute command '{}'" .format(cmd))
                print ("Error type: {}" .format(err))
                print ("Exit programm" + END)
                sys.exit ()
        # close connection to compute node
        computenode.close()
        del computenode
    
    # close connection to head node
    headnode.close()
    del headnode

############
# get info #
############
def get_info (cluster_id, params):
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
                print(cluster_id + ':' + node_list[i]["Tags"][0] + ' | ' + node_list[i]['Name'])
                if (cluster_id in node_list[i]["Tags"][0] and 'headnode' in node_list[i]['Name']):
                    head_ip = node_list[i]['Interfaces'][0]['IPAddress']
                    os_type = params.cluster_info_all[cluster_id]["clusterparams"]["server"][zone]["head"]["disk"][0]["os"]
                elif (cluster_id in node_list[i]["Tags"][0]):
                    n_computenode += 1
                else:
                    pass
        else:
            pass
    
    if head_ip == "255.255.255.255":
        try:
            raise ValueError (RED + "Failed to get IP address of head node")
        except:
            print ("Exit programm" + END)
            sys.exit ()
    return head_ip, os_type, n_computenode


if __name__ == '__main__':
    params = get_cluster_info()
    cluster_id = '290516'
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
                print(cluster_id + ':' + node_list[i]["Tags"][0] + ' | ' + node_list[i]['Name'])
                if (cluster_id in node_list[i]["Tags"][0] and 'headnode' in node_list[i]['Name']):
                    headIp = node_list[i]['Interfaces'][0]['IPAddress']
                    os_type = params.cluster_info_all[cluster_id]["clusterparams"]["server"][zone]["head"]["disk"][0]["os"]
                elif (cluster_id in node_list[i]["Tags"][0]):
                    n_computenode += 1
                else:
                    pass
        else:
            pass

    # Read json file for gaglia configuration 
    json_addon_params = load_addon_params ()
    setup_mpi (
        cluster_id = cluster_id,
        params = params,
        node_password = node_password,
        json_addon_params = json_addon_params,
        service_type="MPI",
        service_name="mpich"
    )