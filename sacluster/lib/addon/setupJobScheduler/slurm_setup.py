import json
from operator import index
from platform import node
import re
import string
import sys
import time
import logging
import os
from pandas import concat
import paramiko
#from sacluster.lib.addon.setupIP.switch_fw_zone import ssh_connect

# User defined Library
os.chdir(os.path.dirname(os.path.abspath(__file__)))
common_path = os.path.abspath("../../..")
fileName = common_path + '/lib/addon/setupJobScheduler/slurm.json'
ConfigFile = common_path + '/lib/addon/setupJobScheduler/slurmconf.json'

sys.path.append (common_path + "/lib/addon/mylib")
from sshconnect_main import sshConnect_main, headConnect, computeConnect, computeConnect_IP
from get_cluster_info     import get_cluster_info
from load_addon_params    import load_addon_params

# Changing standard output color for exception error
RED = '\033[31m'
END = '\033[0m'

#################
# Main Programm #
#################
def slurm_setup (node_password,os_type,cmd_slurm,ip_list,cluster_id):
    print ("(Start) Setup for slurm")
    
    params = get_cluster_info ()
    head_list, os_type, computememory = sshConnect_main(cluster_id,params,node_password)

    slurm_user (
        head_list = head_list,
        ip_list = ip_list, 
        cmd_head = cmd_slurm[os_type]["Head"]["slurm"]["slurmuser"],
        cmd_compute = cmd_slurm[os_type]["Compute"]["slurm"]["slurmuser"]
    )

    slurm_install (
        head_list = head_list,
        ip_list = ip_list,
        cmd_head = cmd_slurm[os_type]["Head"]["slurm"]["install"],
        cmd_compute = cmd_slurm[os_type]["Compute"]["slurm"]["install"]
    )

    slurm_conf (
        head_list = head_list,
        ip_list = ip_list,
        cmd_head = cmd_slurm[os_type]["Head"]["slurm"]["conf"],
        cmd_compute = cmd_slurm[os_type]["Compute"]["slurm"]["conf"]
    )

    send_slurm_conf (
        head_list = head_list,
        ip_list = ip_list,
        clusterID = cluster_id,
        compnum = computememory
    )

    slurm_deamon (
        head_list = head_list,
        ip_list = ip_list, 
        cmd_head = cmd_slurm[os_type]["Head"]["slurm"]["daemon"],
        cmd_compute = cmd_slurm[os_type]["Compute"]["slurm"]["daemon"]
    )

    print ("(Done) Setup for slurm")

def slurm_user (head_list, ip_list, cmd_head, cmd_compute):
    print ("(Start) Create slurmuser")
    
    headConnect(head_list, cmd_head)
    computeConnect(head_list, ip_list, cmd_compute)

    print ("(Done) Create slurm user")

def slurm_install (head_list, ip_list, cmd_head, cmd_compute):
    print ("(Start) Install packages for slurm")

    headConnect(head_list, cmd_head)
    computeConnect(head_list, ip_list, cmd_compute)

    print ("(Done) Install packages for slurm")

def slurm_conf (head_list, ip_list, cmd_head, cmd_compute):
    print ("(Start) Setting for slurm conf")

    headConnect(head_list, cmd_head)
    computeConnect(head_list, ip_list, cmd_compute)

    print ("(Done) Setting for slurm conf")

def send_slurm_conf (head_list, ip_list, clusterID, compnum):
    print ("(Start) Sending slurm config to compute node")
   
    json_open = open(ConfigFile, 'r')
    config_slurm = json.load(json_open)
    target_file = "/etc/slurm/slurm.conf"
    config = "CPUs=" + str(compnum['CPU'])+ " RealMemory=" + str(compnum['REAL_MEMORY']) + " CoresPerSocket=" + str(compnum['CPU'])+ " ThreadsPerCore=1 State=UNKNOWN"
    #NodeHostname= computenodeでhostnameで出てくるもの

    #コマンド作成
    cmd = ["echo" + '"#SlurmConfig" > ' + target_file]
    cmd.append("echo" + ' "' + 'SlurmctldHost=headnode' + clusterID +  '" >> ' + target_file)
    conf = config_slurm["conf"]
    for config_slurm_val in conf:
        cmd.append("echo" + ' "' + config_slurm_val + '" >>' + target_file)
    cmd.append("echo" + ' "' + 'NodeName=computenode00[1-' + str(compnum['COMPUTE_NUM']) + '] ' + config + '" >> ' + target_file)
    #cmd.append("echo" + ' "' + 'NodeName=computenode001 ' + config + '" >> ' + target_file)

    cmd.append("echo" + ' "' + 'PartitionName=test Nodes=ALL Default=YES MaxTime=INFINITE State=UP' + '" >> ' + target_file)
    #cmd.append("echo" + ' "' + 'PartitionName=demo Nodes=computenode001 Default=YES MaxTime=INFINITE State=UP' + '" >> ' + target_file)
    headConnect(head_list, cmd)


    # Interacting to shell
    ssh_client = paramiko.SSHClient()
    ssh_client.set_missing_host_key_policy(paramiko.WarningPolicy())
    print("Connecting to headnode ...")
    ssh_client.connect(hostname=head_list['IP_ADDRESS'], port=head_list['PORT'], username=head_list['USER'], password=head_list['PASSWORD'])
    try:
        shell = ssh_client.invoke_shell () 
    except paramiko.SSHException as err:
        print (RED +"Error Occured")
        print ("Error type] {}" .format(err))
        print ("Exit prigramm" + END)
        sys.exit ()

    for IP in ip_list["front"]:
        IP_ADDRESS2 = IP
        compInfo = {
            'IP_ADDRESS':IP_ADDRESS2,
            'PORT'      :22,
            'USER'      :'root',
            'PASSWORD'  :head_list['PASSWORD']
        }
        cmd = "scp /etc/slurm/slurm.conf " + compInfo['IP_ADDRESS'] + ":/etc/slurm/"
        
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
                    shell.send(str(head_list['PASSWORD']) + "\n")
                except paramiko.socket.timeout as err:
                    print (RED +"Error Occured")
                    print ("Error type] {}" .format(err))
                    print ("Exit prigramm" + END)
                    sys.exit ()
                time.sleep (2)
                break

    # Close channel to shell
    shell.close ()
    print ("(Done) Sending  slurm config to compute node")

def slurm_deamon (head_list, ip_list, cmd_head, cmd_compute):
    print ("(Start) Enable slurm daemon")

    headConnect(head_list, cmd_head)
    computeConnect  (head_list, ip_list, cmd_compute)

    print ("(Done) Enable slurm daemon")


if __name__ == '__main__':
    params              = get_cluster_info ()
    json_addon_params   = load_addon_params ()

    cls_bil  = []
    ext_info = []
    info_list = [1,0,0,1]
    f = []

    addon_info = {
        "clusterID"         : "594970",                 # !!! 任意のクラスターIDに変更 !!!
        "IP_list"           :{                          # コンピュートノードの数に合わせて変更
            "front" : ['192.168.2.1', '192.168.2.2'],
            "back"  : ['192.169.2.1', '192.169.2.2']
        },
        "params"            : params,
        "json_addon_params" : json_addon_params,
        "node_password"     : "test"                    # 設定したパスワードを入力
    }
    cluster_id       = addon_info["clusterID"]
    ip_list         = addon_info["IP_list"]
    params          = addon_info["params"]
    node_password    = addon_info["node_password"]
   
    head_ip, os_type, computememory = sshConnect_main(cluster_id, params,  node_password)
    
    try:
        json_open = open(fileName, 'r')
    except OSError as err:
        print (RED + "Fialed to open file: {}" .format(fileName))
        print ("Error type: {}" .format(err))
        print ("Exit rogramm" + END)
        sys.exit ()
    try:
        cmd_slurm = json.load(json_open)
    except json.JSONDecodeError as err:
        print (RED + "Fialed to decode JSON file: {}" .format(fileName))
        print ("Error type: {}" .format(err))
        print ("Exit programm" + END)
        sys.exit ()

    slurm_setup (node_password,os_type,cmd_slurm,ip_list,cluster_id)
