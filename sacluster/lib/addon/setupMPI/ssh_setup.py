from ipaddress import ip_address
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
def ssh_setup (head_ip, ip_list, node_password, os_type):
    print ('Start: (SSH setting)')

    # Read json file for gaglia configuration 
    json_open = open(fileName, 'r')
    cmd_json = json.load(json_open)

    # Create SSH key
    sshkey_create (
        head_ip=head_ip,
        node_password=node_password,
        cmd_json=cmd_json[os_type]['command']['Head']['ssh']
        )
    
    # Copy public key to the compute nodes 
    send_sshkey (
        head_ip=head_ip,
        node_password=node_password,
        cmd_json=cmd_json[os_type]['command']['Head']['ssh'],
        ip_list = ip_list
    )

    # ssh Setting
    print (" Done: (SSH setting)")
# End of ssh_setup ()

####################################
# Creating SSH key on the headnode #
####################################
def sshkey_create (head_ip, node_password, cmd_json): 
    print ('Creating SSH key on the head node')
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
    headnode.connect(
        hostname=head_info['IP_ADDRESS'],
        port=head_info['PORT'], 
        username=head_info['USER'], 
        password=head_info['PASSWORD']
        )
    print('Connected')

    # Interacting to shell
    shell = headnode.invoke_shell ()

    # Send command
    cmd = cmd_json[0]
    shell.send(cmd)
    time.sleep (2)
    output=''
    while True:
        output = output + shell.recv(1000).decode('utf-8')
        if '#' in output:
            break
        print (output)
        if '#' not in output:
           shell.send("\n")
           time.sleep (2)
    
    headnode.close()
    del headnode
    print ('Disconnect from headnode')
    print ('Creating SSH key is done')

#################
# Share SSH key #
#################
def send_sshkey (head_ip, node_password, cmd_json, ip_list):
    print ('Creating SSH key on the head node')
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
    headnode.connect(
        hostname=head_info['IP_ADDRESS'],
        port=head_info['PORT'], 
        username=head_info['USER'], 
        password=head_info['PASSWORD']
        )
    print('Connected')

    # Interacting to shell
    shell = headnode.invoke_shell ()
    cmd_list = cmd_json[1:5]
    output = ""
    # Configuration Setting for Compute node
    for ip_compute in ip_list:
        for i, cmd in enumerate (cmd_list):

            if 'ssh-copy-id' in cmd:
                ipaddress_comp = ip_compute
                shell.send(cmd + ' ' + ipaddress_comp + '\n')
            else:
                shell.send(cmd + '\n')
            time.sleep (2)
            output = output + shell.recv(1000).decode('utf-8')
            print (output)
    
    headnode.close()
    del headnode
    print ('Disconnect from headnode')
    print ('Copying SSH key is done')


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
    ssh_setup (head_ip, n_computenode, node_password, json_addon_params, os_type)
