import json
from operator import index
from platform import node
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

#################
# Main Programm #
#################
def munge_setup (head_ip, n_computenode, node_password, os_type, cmd_slurm):
    print ("(Start) Setup for mugnge")
    
    munge_user (
        head_ip = head_ip,
        n_computenode = n_computenode,
        node_password = node_password,
        cmd_head = cmd_slurm[os_type]["Head"]["munge"]["mungeuser"],
        cmd_compute = cmd_slurm[os_type]["Compute"]["munge"]["mungeuser"]
    )

    munge_install (
        head_ip = head_ip,
        n_computenode = n_computenode,
        node_password = node_password,
        cmd_head = cmd_slurm[os_type]["Head"]["munge"]["install"],
        cmd_compute = cmd_slurm[os_type]["Compute"]["munge"]["install"]
    )

    munge_key (
        head_ip = head_ip,
        n_computenode = n_computenode,
        node_password = node_password,
        cmd_head = cmd_slurm[os_type]["Head"]["munge"]["munge-key"],
        cmd_compute = cmd_slurm[os_type]["Compute"]["munge"]["munge-key"]
    )

    munge_daemon (
        head_ip = head_ip,
        n_computenode = n_computenode,
        node_password = node_password,
        cmd_head = cmd_slurm[os_type]["Head"]["munge"]["daemon"],
        cmd_compute = cmd_slurm[os_type]["Compute"]["munge"]["daemon"]
    )

    print ("(Done) Setup for mugnge")

def munge_user (head_ip, n_computenode, node_password, cmd_head, cmd_compute):
    print ("(Start) Create munge user")
    ####################
    #    Head Node     #
    ####################
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

    for i, cmd in enumerate(cmd_head):
        try:
            headnode.exec_command (cmd)
        except paramiko.SSHException as err:
            print (RED + "Failed to excute command on headnode")
            print ("Error Type: {}" .format (err))
            print ("Exit Programm" + END)
            sys.exit ()
    
    ####################################
    #         Compute Node             #
    ####################################
    # Configuration Setting for Compute node
    transport1 = headnode.get_transport()
    head = (head_info['IP_ADDRESS'], head_info['PORT'])
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
        try:
            channel1 = transport1.open_channel("direct-tcpip", compute, head)
        except Exception as err:
            print (RED + "Failed to open channel to compute_node" + str(i_computenode + 1))
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
            print (RED + "Failed to connect to compute_node" + str(i_computenode+1))
            print ("Error type {}" .format(err))
            print ("Exit programm" + END)
            sys.exit ()
        print('Connected')

        # Execute command
        for i, cmd in enumerate(cmd_compute):
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
    print ("(Done) Create munge user")

def munge_install (head_ip, n_computenode, node_password, cmd_head, cmd_compute):
    print ("(Start) Install packages for munge")
    ####################
    #    Head Node     #
    ####################
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

    for i, cmd in enumerate(cmd_head):
        try:
            headnode.exec_command (cmd)
        except paramiko.SSHException as err:
            print (RED + "Failed to excute command on headnode")
            print ("Error Type: {}" .format (err))
            print ("Exit Programm" + END)
            sys.exit ()
        time.sleep (5)
    
    ####################################
    #         Compute Node             #
    ####################################
    # Configuration Setting for Compute node
    transport1 = headnode.get_transport()
    head = (head_info['IP_ADDRESS'], head_info['PORT'])
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
        try:
            channel1 = transport1.open_channel("direct-tcpip", compute, head)
        except Exception as err:
            print (RED + "Failed to open channel to compute_node" + str(i_computenode + 1))
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
            print (RED + "Failed to connect to compute_node" + str(i_computenode+1))
            print ("Error type {}" .format(err))
            print ("Exit programm" + END)
            sys.exit ()
        print('Connected')

        # Execute command
        for i, cmd in enumerate(cmd_compute):
            try:
                computenode.exec_command (cmd)
            except paramiko.SSHException as err:
                print (RED + "Fialed to excute command '{}'" .format(cmd))
                print ("Error type: {}" .format(err))
                print ("Exit programm" + END)
                sys.exit ()
            time.sleep (5)
        # close connection to compute node
        computenode.close()
        del computenode
    
    # close connection to head node
    headnode.close()
    del headnode
    print ("(Done) Install packages for munge")

def munge_key (head_ip, n_computenode, node_password, cmd_head, cmd_compute):
    print ("(Start) Setting for munge key")
    ####################
    #    Head Node     #
    ####################
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

    for i, cmd in enumerate(cmd_head):
        try:
            if "scp" in cmd: # Breadcast the mugne key
                send_munge_key (
                    ssh_client = headnode,
                    node_password = node_password,
                    n_computenode = n_computenode,
                    cmd_base = cmd
                )
            else:
                headnode.exec_command (cmd)
        except paramiko.SSHException as err:
            print (RED + "Failed to excute command on headnode")
            print ("Error Type: {}" .format (err))
            print ("Exit Programm" + END)
            sys.exit ()
    
    ####################################
    #         Compute Node             #
    ####################################
    # Configuration Setting for Compute node
    transport1 = headnode.get_transport()
    head = (head_info['IP_ADDRESS'], head_info['PORT'])
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
        try:
            channel1 = transport1.open_channel("direct-tcpip", compute, head)
        except Exception as err:
            print (RED + "Failed to open channel to compute_node" + str(i_computenode + 1))
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
            print (RED + "Failed to connect to compute_node" + str(i_computenode+1))
            print ("Error type {}" .format(err))
            print ("Exit programm" + END)
            sys.exit ()
        print('Connected')

        # Execute command
        for i, cmd in enumerate(cmd_compute):
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
    print ("(Done) Setting for munge key")

def munge_daemon (head_ip, n_computenode, node_password, cmd_head, cmd_compute):
    print ("(Start) Enable munge daemon")
    ####################
    #    Head Node     #
    ####################
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

    for i, cmd in enumerate(cmd_head):
        try:
            headnode.exec_command (cmd)
        except paramiko.SSHException as err:
            print (RED + "Failed to excute command on headnode")
            print ("Error Type: {}" .format (err))
            print ("Exit Programm" + END)
            sys.exit ()
    
    ####################################
    #         Compute Node             #
    ####################################
    # Configuration Setting for Compute node
    transport1 = headnode.get_transport()
    head = (head_info['IP_ADDRESS'], head_info['PORT'])
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
        try:
            channel1 = transport1.open_channel("direct-tcpip", compute, head)
        except Exception as err:
            print (RED + "Failed to open channel to compute_node" + str(i_computenode + 1))
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
            print (RED + "Failed to connect to compute_node" + str(i_computenode+1))
            print ("Error type {}" .format(err))
            print ("Exit programm" + END)
            sys.exit ()
        print('Connected')

        # Execute command
        for i, cmd in enumerate(cmd_compute):
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
    print ("(Done) Enable munge daemon")

def send_munge_key (ssh_client, node_password, n_computenode, cmd_base):
    print ("    (Start) Sending munge key to compute node")
    # Interacting to shell
    try:
        shell = ssh_client.invoke_shell ()
    except paramiko.SSHException as err:
        print (RED +"Error Occured")
        print ("Error type] {}" .format(err))
        print ("Exit prigramm" + END)
        sys.exit ()
    
    for i in range (n_computenode):
        ip_compute = " 192.168.2." + str (i+1)
        cmd = cmd_base + ip_compute + ":/etc/munge"
        
        # Send command
        try:
            shell.send(cmd + "\n")
        except paramiko.socket.timeout as err:
            print (RED +"Error Occured")
            print ("Error type] {}" .format(err))
            print ("Exit prigramm" + END)
            sys.exit ()
        
        time.sleep (2)
        output = ''
        while True:
            output = shell.recv(1000).decode('utf-8')
            print (output)
            if 'Are you sure' in output:
                try:
                    shell.send ("yes\n")
                except paramiko.socket.timeout as err:
                    print (RED +"Error Occured")
                    print ("Error type] {}" .format(err))
                    print ("Exit prigramm" + END)
                    sys.exit ()
                time.sleep (2)
                output = ''
            if 'password' in output:
                try:
                    shell.send(str(node_password) + "\n")
                except paramiko.socket.timeout as err:
                    print (RED +"Error Occured")
                    print ("Error type] {}" .format(err))
                    print ("Exit prigramm" + END)
                    sys.exit ()
                time.sleep (2)
                break

    # Close channel to shell
    shell.close ()
    print ("    (Done) Sending munge key to compute node")

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
                    head_ip = node_list[i]['Interfaces'][0]['IPAddress']
                    os_type = params.cluster_info_all[cluster_id]["clusterparams"]["server"][zone]["head"]["disk"][0]["os"]
                elif (cluster_id in node_list[i]["Tags"][0]):
                    n_computenode += 1
                else:
                    pass
        else:
            pass

    # Read json file for gaglia configuration 
    json_addon_params = load_addon_params ()
    munge_setup (
        head_ip = head_ip,
        n_computenode = n_computenode,
        node_password = node_password,
        json_addon_params = json_addon_params,
        os_type = os_type
    )