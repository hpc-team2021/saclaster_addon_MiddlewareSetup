import json
from operator import index
import re
import string
import sys
import time
import logging
import os
import paramiko
from tqdm import tqdm

# User defined Library
os.chdir(os.path.dirname(os.path.abspath(__file__)))
common_path = os.path.abspath("../../..")
fileName = common_path + '\\lib\\addon\\setupMoniter\\gangliaConf.json'

sys.path.append(common_path + "/lib/addon/mylib")
from load_addon_params import load_addon_params

logger = logging.getLogger("addon").getChild(os.path.basename(__file__))


#################
# Main Programm #
#################
def gangliaSetup (head_ip, num_compute, node_password, os_type, ip_list):
    logger.debug ('Working on Ganglia Setting ...')

    # Read json file for gaglia configuration 
    json_open = open (fileName, 'r')
    json_ganglia = json.load (json_open)

    # Package Install
    gangliaInstall (
        head_ip = head_ip,
        num_compute = num_compute,
        node_password = node_password,
        cmd_list = json_ganglia[os_type]["install"],
        ip_list = ip_list
    )

    # Port Open
    gangliaPort (
        head_ip = head_ip,
        num_compute = num_compute,
        node_password = node_password,
        cmd_list = json_ganglia[os_type]["port"],
        ip_list = ip_list
    )

    # Ganglia Setting
    gangliaHead (
        head_ip = head_ip,
        num_compute = num_compute,
        node_password = node_password,
        json_ganglia = json_ganglia[os_type],
        ip_list = ip_list
    )
    
    gangliaComp (
        head_ip = head_ip,
        num_compute = num_compute,
        node_password = node_password,
        json_ganglia = json_ganglia[os_type],
        ip_list = ip_list
    )

    gangliaDaemon (
        head_ip = head_ip,
        num_compute = num_compute,
        node_password = node_password,
        cmd_list = json_ganglia[os_type]["daemon"],
        ip_list = ip_list
    )

    logger.debug ("Ganglia Setting is done")
# % End of gangliaSetup ()

##############################
# Ganglia Install
#############################
def gangliaInstall (head_ip, num_compute, node_password, cmd_list, ip_list):
    head_info = {
        'IP_ADDRESS':head_ip,
        'PORT'      :22,
        'USER'      :'root',
        'PASSWORD'  :node_password
        }

    head = (head_ip, head_info ['PORT'])
    headnode = paramiko.SSHClient ()
    headnode.set_missing_host_key_policy (paramiko.WarningPolicy())
    headnode.connect (
        hostname = head_info['IP_ADDRESS'],
        port = head_info['PORT'],
        username = head_info['USER'],
        password = head_info['PASSWORD']
        )
    
    # Exec Command
    for cmd in tqdm(cmd_list["head"]):
        stdin, stdout, stderr = headnode.exec_command (cmd)
        out = stdout.read().decode()
        logger.debug (out)
    
    transport1 = headnode.get_transport ()
    # Configuration Setting for Compute node
    for ip_compute in ip_list:
        comp_info = {
            'IP_ADDRESS':ip_compute,
            'PORT'      :22,
            'USER'      :'root',
            'PASSWORD'  :node_password
        }
        compute = (comp_info ['IP_ADDRESS'], comp_info ['PORT'])
        channel1 = transport1.open_channel("direct-tcpip", compute, head)
        computenode = paramiko.SSHClient()
        computenode.set_missing_host_key_policy(paramiko.WarningPolicy())
        logger.debug ("compurenode connecting...")
        computenode.connect(
            hostname = comp_info['IP_ADDRESS'],
            username = comp_info['USER'],
            password = comp_info['PASSWORD'],
            sock = channel1
        )
        logger.debug ('computenode connected')

        # Exec Command
        for cmd in cmd_list["compute"]:
            stdin, stdout, stderr = computenode.exec_command (cmd)

        computenode.close()
    
    headnode.close()
    computenode.close()
    del headnode, computenode

##############################
#        Ganglia Port 
############################# 
def gangliaPort (head_ip, num_compute, node_password, cmd_list, ip_list):
    head_info = {
        'IP_ADDRESS':head_ip,
        'PORT'      :22,
        'USER'      :'root',
        'PASSWORD'  :node_password
    }

    head = (head_ip, head_info ['PORT'])
    headnode = paramiko.SSHClient ()
    headnode.set_missing_host_key_policy (paramiko.WarningPolicy())
    headnode.connect (
        hostname = head_info['IP_ADDRESS'],
        port = head_info['PORT'],
        username = head_info['USER'],
        password = head_info['PASSWORD']
    )
    
    # Exec Command
    for cmd in tqdm(cmd_list):
        stdin, stdout, stderr = headnode.exec_command (cmd)
        out = stdout.read().decode()
        logger.debug (out)
    
    transport1 = headnode.get_transport ()
    # Configuration Setting for Compute node
    for ip_compute in ip_list:
        comp_info = {
            'IP_ADDRESS':ip_compute,
            'PORT'      :22,
            'USER'      :'root',
            'PASSWORD'  :node_password
        }
        compute = (comp_info ['IP_ADDRESS'], comp_info ['PORT'])
        channel1 = transport1.open_channel("direct-tcpip", compute, head)
        computenode = paramiko.SSHClient()
        computenode.set_missing_host_key_policy(paramiko.WarningPolicy())
        logger.debug ("compurenode connecting...")
        computenode.connect(
            hostname = comp_info['IP_ADDRESS'],
            username = comp_info['USER'],
            password = comp_info['PASSWORD'],
            sock = channel1
        )
        logger.debug ('computenode connected')

        # Exec Command
        for cmd in tqdm(cmd_list):
            stdin, stdout, stderr = computenode.exec_command (cmd)
            out = stdout.read().decode()
            logger.debug (out)

        computenode.close()
    
    headnode.close()
    computenode.close()
    del headnode, computenode
# % End of gangliaPort ()

###############################
# Ganglia Setting on Headnode #
###############################
def gangliaHead (head_ip, num_compute, node_password, json_ganglia, ip_list): 
    # Configuration Setting for Headnode
    headInfo = {
        'IP_ADDRESS':head_ip,
        'PORT'      :22,
        'USER'      :'root',
        'PASSWORD'  :node_password
    }
    
    # Connect to Headnode
    headnode = paramiko.SSHClient()
    headnode.set_missing_host_key_policy(paramiko.WarningPolicy())
    logger.debug ("headnode connecting...")
    headnode.connect(
        hostname=headInfo['IP_ADDRESS'], 
        port=headInfo['PORT'], 
        username=headInfo['USER'], 
        password=headInfo['PASSWORD']
    )
    logger.debug ('headnode connected')

    # gmond.conf setting
    logger.debug ('(Start) Setting for gmond.conf')
    gmondConfSetup (
        json_ganglia = json_ganglia, 
        num_compute = num_compute,
        node_client = headnode,
    )
    logger.debug (' (Done) Setting for gmond.conf')

    # gmetad.conf setting
    logger.debug ('(Start) Setting for gmetad.conf')
    gmetadConfSetup (
        json_ganglia = json_ganglia,
        node_client = headnode
    )
    logger.debug (' (Done) Setting for gmetad.conf')

    # ganglia.conf setting
    logger.debug ('(Start) Setting for ganglia.conf')
    gangliaConfSetup (
        json_ganglia = json_ganglia,
        node_client = headnode
    )
    logger.debug (' (Done) Setting for ganglia.conf')
    
    # web monitor password setting 
    # webPasswdSetting (jsonGanglia[OSType], nodeClient = headnode)
    
    headnode.close()
    del headnode
# % End of gangliaHead ()

##################################
# Ganglia Setting on Compute node
###################################
def gangliaComp (head_ip, num_compute, node_password, json_ganglia, ip_list):
    headInfo = {
        'IP_ADDRESS':head_ip,
        'PORT'      :22,
        'USER'      :'root',
        'PASSWORD'  :node_password
    }

    head = (head_ip, headInfo ['PORT'])
    headnode = paramiko.SSHClient()
    headnode.set_missing_host_key_policy(paramiko.WarningPolicy())
    headnode.connect(hostname=headInfo['IP_ADDRESS'], port=headInfo['PORT'], username=headInfo['USER'], password=headInfo['PASSWORD'])
    transport1 = headnode.get_transport()
        
    # Configuration Setting for Compute node
    for ip_compute in ip_list:
        compInfo = {
            'IP_ADDRESS':ip_compute,
            'PORT'      :22,
            'USER'      :'root',
            'PASSWORD'  :node_password
        }
        compute = (compInfo ['IP_ADDRESS'], compInfo ['PORT'])
        channel1 = transport1.open_channel("direct-tcpip", compute, head)
        computenode = paramiko.SSHClient()
        computenode.set_missing_host_key_policy(paramiko.WarningPolicy())

        logger.debug ("computenode connecting...")
        computenode.connect(hostname=compInfo['IP_ADDRESS'],username=compInfo['USER'],password=compInfo['PASSWORD'],sock=channel1)
        logger.debug ('computenode connected')

        # gmond.conf setting on computenode
        gmondConfSetup (
            json_ganglia = json_ganglia,
            num_compute = num_compute,
            node_client = computenode,
        )

        computenode.close()
    
    headnode.close()
    computenode.close()
    del headnode, computenode
# % End of gangliaComp ()

########################
# gmond.conf setting   #
########################
def gmondConfSetup (json_ganglia, num_compute, node_client):
    cmdMain = json_ganglia['command'][0]
    targetFile = json_ganglia['targetFile']['gmond']

    conf = json_ganglia['gmond']

    # Clear the Target File
    cmd = cmdMain + str (" ' ' > ") + targetFile
    node_client.exec_command (cmd)

    # global conf
    confVal = conf['global']
    for i, setting in enumerate(confVal):
        cmd = cmdMain + str (" '") + setting \
            + str ("' >> ") + targetFile
        stdin, stdout, stderr = node_client.exec_command (cmd)

    cmd = cmdMain + str (" ' ' >> ") + targetFile
    node_client.exec_command (cmd)

    # clustre conf
    confVal = conf['cluster']
    for i, setting in enumerate(confVal):
        cmd = cmdMain + str (" '") + setting \
            + str ("' >> ") + targetFile
        stdin, stdout, stderr = node_client.exec_command (cmd)
    
    cmd = cmdMain + str (" ' ' >> ") + targetFile
    node_client.exec_command (cmd)
    
    # host conf
    confVal = conf['host']
    for i, setting in enumerate(confVal):
        cmd = cmdMain + str ("'") + setting \
            + str ("' >> ") + targetFile
        stdin, stdout, stderr = node_client.exec_command (cmd)
       
    cmd = cmdMain + str (" ' ' >> ") + targetFile
    node_client.exec_command (cmd)

    # udp_send_channel conf
    confVal = conf['udp_send_channel']
    host = "computenode001"
   
    for j, setting in enumerate(confVal):
        if 'host = ' in setting:
            cmd = cmdMain + str (" '") \
                + setting + host \
                + str ("' >> ") + targetFile
            stdin, stdout, stderr = node_client.exec_command (cmd)
        else:
            cmd = cmdMain + str (" '") + setting \
                + str ("' >> ") + targetFile
            stdin, stdout, stderr = node_client.exec_command (cmd)
        
        cmd = cmdMain + str (" ' ' >> ") + targetFile
        node_client.exec_command (cmd)
        
    # udp_recv_channel conf
    confVal = conf['udp_recv_channel']
    for i, setting in enumerate(confVal):
        cmd = cmdMain + str (" '") + setting \
            + str ("' >> ") + targetFile
        stdin, stdout, stderr = node_client.exec_command (cmd)


    # tcp_recv_channel conf
    confVal = conf['tcp_accept_channel']
    for i, setting in enumerate(confVal):
        cmd = cmdMain + str (" '") + setting \
            + str ("' >> ") + targetFile
        stdin, stdout, stderr = node_client.exec_command (cmd)

    # collection_group conf
    for index in range(1, 11):
        group_name = 'collection_group_' + str (index)
        confVal = conf[group_name]
        for i, setting in enumerate(confVal):
            cmd = cmdMain + str (" '") + setting \
                + str ("' >> ") + targetFile
            stdin, stdout, stderr = node_client.exec_command (cmd)
    
    # include conf
    confVal = conf['include']
    for i, setting in enumerate(confVal):
        cmd = cmdMain + str (" '") + setting \
            + str ("' >> ") + targetFile
        stdin, stdout, stderr = node_client.exec_command (cmd)
# End of gmondConfSetup ()

#######################
# Web Monitor Setting #
#######################
def webPasswdSetting (jsonGanglia, nodeClient):
    cmdMain = jsonGanglia['gangliaWeb'][0]
    logger.debug ("Setting for Web Monitoring Service")
    userName = input ("Enter User Name for Web Login -->")
    command = cmdMain + str(" ") + userName + '\n'
    
    shell = nodeClient.invoke_shell ()
    shell.recv (1000)
    shell.send(command)
    output=''
    while True:
        output = output + shell.recv(1000).decode('utf-8')
        if(re.search('[Pp]assword',output)):
            output=''
            break
    
    # Enter Password
    monitorPassword = input ('Enter web monitor password to login --> ')
    shell.send(monitorPassword + "\n")

    while True:
        output = output + shell.recv(1000).decode('utf-8')
        if(re.search('[Pp]assword',output)):
            output=''
            break
    
    # Enter Password Again
    shell.send(monitorPassword + "\n")

    while True:
        output = shell.recv(1000).decode('utf-8')
        if(re.search('#',output)):
            logger.debug (output)
            output=''
            break

    # Enter password
    #while len(stdout.channel.in_buffer) == 0:
        # Wait until getting password prompt
    #    print ("Getting password prompt ...")
    #    time.sleep(1)
    #monitorPassword = input ('Enter web monitor password to login --> ')
    #stdin.channel.send(monitorPassword + "\n")
            
    # Enter passwd again
    """
    while len(stdout.channel.in_buffer) == 0:
        # Wait until getting password prompt
        print ("Getting password prompt")
        time.sleep(1)
    # monitorPassword = input ('Enter web monitor password to login  -->')
    stdin.channel.send(monitorPassword + "\n")
    """

    # out = stdout.read().decode()
    # print('head_stdout = %s' % out)
# % End of webMonitorSetting ()

#######################
# gmetad.conf setting
########################
def gmetadConfSetup (json_ganglia, node_client):
    cmdMain = json_ganglia["command"][0]
    targetFile = json_ganglia["targetFile"]["gmetad"]
    confSetting = json_ganglia["gmetad"]

    for i, setting in tqdm (enumerate (confSetting)):
        cmd = cmdMain + str(" '") \
            + setting + str("' >> ") \
            + targetFile
        stdin, stdout, stderr = node_client.exec_command (cmd)
        out = stdout.read().decode()
        logger.debug (out)

#######################
# ganglia.conf setting
#######################
def gangliaConfSetup (json_ganglia, node_client):
    cmdMain = json_ganglia["command"][0]
    targetFile = json_ganglia["targetFile"]["gangliaConf"]
    confSetting = json_ganglia["gangliaConf"]

    cmd = cmdMain + str (" ' ' > ") + targetFile
    stdin, stdout, stderr = node_client.exec_command (cmd)
    out = stdout.read().decode()
    logger.debug (out)

    for i, setting in tqdm (enumerate (confSetting)):
        cmd = cmdMain + str (" '") \
            + setting + str ("' >> ") \
            + targetFile
        stdin, stdout, stderr = node_client.exec_command (cmd)
        out = stdout.read().decode()
        logger.debug (out)

def gangliaDaemon (head_ip, num_compute, node_password, cmd_list, ip_list):
    head_info = {
        'IP_ADDRESS':head_ip,
        'PORT'      :22,
        'USER'      :'root',
        'PASSWORD'  :node_password
        }

    head = (head_ip, head_info ['PORT'])
    headnode = paramiko.SSHClient ()
    headnode.set_missing_host_key_policy (paramiko.WarningPolicy())
    headnode.connect (
        hostname = head_info['IP_ADDRESS'],
        port = head_info['PORT'],
        username = head_info['USER'],
        password = head_info['PASSWORD']
        )
    
    # Exec Command
    for cmd in tqdm(cmd_list["head"]):
        stdin, stdout, stderr = headnode.exec_command (cmd)
        out = stdout.read().decode()
        logger.debug (out)
    
    transport1 = headnode.get_transport ()
    # Configuration Setting for Compute node
    for ip_compute in ip_list:
        comp_info = {
            'IP_ADDRESS':ip_compute,
            'PORT'      :22,
            'USER'      :'root',
            'PASSWORD'  :node_password
        }
        compute = (comp_info ['IP_ADDRESS'], comp_info ['PORT'])
        channel1 = transport1.open_channel("direct-tcpip", compute, head)
        computenode = paramiko.SSHClient()
        computenode.set_missing_host_key_policy(paramiko.WarningPolicy())
        logger.debug ("computenode connecting...")
        computenode.connect(
            hostname = comp_info['IP_ADDRESS'],
            username = comp_info['USER'],
            password = comp_info['PASSWORD'],
            sock = channel1
        )
        logger.debug ('computenode connected')

        # Exec Command
        for cmd in cmd_list["compute"]:
            stdin, stdout, stderr = computenode.exec_command (cmd)

        computenode.close()
    
    headnode.close()
    computenode.close()
    del headnode, computenode