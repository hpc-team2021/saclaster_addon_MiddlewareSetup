import imp
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
def add_user_main (head_ip, n_computenode, node_password, json_addon_params, os_type):
    print ('Start: (Adding a new user for MPI)')

    # Read json file for gaglia configuration 
    json_open = open(fileName, 'r')
    cmd_json = json.load(json_open)
    
    # Add a common user
    add_user_head (
        head_ip =head_ip,
        node_password = node_password,
        cmd_json = cmd_json[os_type]["command"]
        )
    
    add_user_compute (
        head_ip =head_ip,
        n_computenode = n_computenode,
        node_password = node_password,
        cmd_json = cmd_json[os_type]["command"]
        )

    print (' Done: (Adding a new user for MPI)')
# % End of add_user_main ()

#####################################
# Adding a new user on the Headnode #
#####################################
def add_user_head (head_ip, node_password, cmd_json): 
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
    print('Connecting to headnode...')
    headnode.connect(
        hostname=head_info['IP_ADDRESS'],
        port=head_info['PORT'], 
        username=head_info['USER'], 
        password=head_info['PASSWORD']
        )
    print('Connected')

    # Interacting to shell
    shell = headnode.invoke_shell ()
    shell.recv (1000)
    pattern = re.compile(r'password|Password|パスワード')

    cmd_list = cmd_json['Head']['mpiuser']
    for i, setting in enumerate(cmd_list):
        cmd = setting
        output=''
        shell.send(cmd + '\n')
        time.sleep (2)
        output = output + shell.recv(1000).decode('utf-8')
        print (output)
        
        if pattern.search (output):
            cnt = 0
            # Enter Password for a new user
            while True:
                if cnt > 1:
                    break
                elif pattern.search (output):
                    shell.send('test' + '\n')
                    time.sleep (2)
                    cnt = cnt + 1
                    output = output + shell.recv(1000).decode('utf-8')
                    print (output)
                else:
                    output = output + shell.recv(1000).decode('utf-8')
                    print (output)

    headnode.close()
    del headnode

########################################
# Adding a new user on the computenode #
########################################
def add_user_compute (head_ip, n_computenode, node_password, cmd_json):
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
    print('Connecting to headnode...')
    headnode.connect(
        hostname=head_info['IP_ADDRESS'],
        port=head_info['PORT'], 
        username=head_info['USER'], 
        password=head_info['PASSWORD']
        )
    print('Connected')
    transport1 = headnode.get_transport()
    head = (head_info['IP_ADDRESS'], head_info['PORT'])

    # Configuration Setting for Compute node
    for i_computenode in range(n_computenode):
        IP_ADDRESS2 = '192.168.2.' + str(i_computenode+1)
        comp_info = {
            'IP_ADDRESS':IP_ADDRESS2,
            'PORT'      :22,
            'USER'      :'root',
            'PASSWORD'  :node_password
        }

        # Connection to compute node
        compute = (comp_info ['IP_ADDRESS'], comp_info ['PORT'])
        channel1 = transport1.open_channel("direct-tcpip", compute, head)
        computenode = paramiko.SSHClient()
        computenode.set_missing_host_key_policy(paramiko.WarningPolicy())
        print("Connecting to compute node...")
        computenode.connect(hostname=comp_info['IP_ADDRESS'], username=comp_info['USER'], password=comp_info['PASSWORD'], sock=channel1, auth_timeout=300)
        print('Connected')

        # Interacting to shell
        shell = computenode.invoke_shell ()
        shell.recv (1000)
        pattern = re.compile(r'password|Password|パスワード')

        cmd_list = cmd_json['Compute']['mpiuser']
        for i, setting in enumerate(cmd_list):
            cmd = setting
            output=''
            shell.send(cmd + '\n')
            time.sleep (2)
            output = output + shell.recv(1000).decode('utf-8')
            print (output)
            
            if pattern.search (output):
                cnt = 0
                # Enter Password for a new user
                while True:
                    if cnt > 1:
                        break
                    elif pattern.search (output):
                        shell.send('test' + '\n')
                        time.sleep (2)
                        cnt = cnt + 1
                        output = output + shell.recv(1000).decode('utf-8')
                        print (output)
                    else:
                        output = output + shell.recv(1000).decode('utf-8')
                        print (output)
        computenode.close ()
        del computenode
    headnode.close()
    del headnode

if __name__ == '__main__':
    """
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
    """

    # Read json file for gaglia configuration 
    json_addon_params = load_addon_params ()
    head_ip ="163.43.140.240"
    n_computenode = 0
    node_password = "test_passwd"
    os_type = "CentOS 7.9 (2009) 64bit"

    add_user_main (head_ip, n_computenode, node_password, json_addon_params, os_type)
