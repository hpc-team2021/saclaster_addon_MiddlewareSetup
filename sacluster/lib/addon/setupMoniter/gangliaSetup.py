import json
from operator import index
import string
import sys
import time
import logging
import os
import paramiko

# User defined Library
os.chdir(os.path.dirname(os.path.abspath(__file__)))
common_path = os.path.abspath("../../..")
fileName = common_path + '\\lib\\addon\\setupMoniter\\gangliaConf.json'

sys.path.append(common_path + "/lib/addon/mylib")
from loadAddonParams import loadAddonParams

#################
# Main Programm #
#################
def gangliaSetup (headIp, nComputenode, nodePassword, jsonAddonParams, OSType):
    print ('Working on Ganglia Setting ...')

    # Read json file for gaglia configuration 
    json_open = open(fileName, 'r')
    jsonGanglia = json.load(json_open)

    # Ganglia Setting
    gangliaHead (headIp, nComputenode, nodePassword, jsonAddonParams, jsonGanglia, OSType)
    # gangliaComp (headIp, nComputenode, nodePassword, jsonAddonParams, jsonGanglia, OSType)

    print ("Ganglia Setting is done")
# % End of gangliaSetup ()   

###############################
# Ganglia Setting on Headnode #
###############################
def gangliaHead (headIp, nComputenode, nodePassword, jsonAddonParams, jsonGanglia, OSType): 
    # Configuration Setting for Headnode
    headInfo = {
        'IP_ADDRESS':headIp,
        'PORT'      :22,
        'USER'      :'root',
        'PASSWORD'  :nodePassword
    }
    
    # Connect to Headnode
    headnode = paramiko.SSHClient()
    headnode.set_missing_host_key_policy(paramiko.WarningPolicy())
    print("hostnode connecting...")
    headnode.connect(hostname=headInfo['IP_ADDRESS'], port=headInfo['PORT'], username=headInfo['USER'], password=headInfo['PASSWORD'])
    print('hostnode connected')

    # gmond.conf setting
    gmondConfSetup (jsonGanglia[OSType], nComputenode, nodeClient = headnode, hostname = 'headnode')

    # gmetad.conf setting
    #gmetadConfSetup (jsonGanglia[OSType], nodeClient = headnode)

    # ganglia.conf setting
    #gangliaConfSetup (jsonGanglia[OSType], nodeClient = headnode)
    
    # web monitor password setting 
    #webPasswdSetting (jsonGanglia[OSType], nodeClient = headnode)
    
    headnode.close()
    del headnode
# % End of gangliaHead ()

##################################
# Ganglia Setting on Compute node
###################################
def gangliaComp (headIp, nComputenode, nodePassword, jsonAddonParams, jsonGanglia, OSType):
    headInfo = {
        'IP_ADDRESS':headIp,
        'PORT'      :22,
        'USER'      :'root',
        'PASSWORD'  :nodePassword
    }

    head = (headIp, headInfo ['PORT'])
    headnode = paramiko.SSHClient()
    headnode.set_missing_host_key_policy(paramiko.WarningPolicy())
    headnode.connect(hostname=headInfo['IP_ADDRESS'], port=headInfo['PORT'], username=headInfo['USER'], password=headInfo['PASSWORD'])
    transport1 = headnode.get_transport()
        
    # Configuration Setting for Compute node
    for iComputenode in range(nComputenode):
        if iComputenode < 9:
            host = 'computenode00' + str(iComputenode)
        elif iComputenode < 99:
            host = 'computenode0' + str(iComputenode)
        else:
            host = 'computenode' + str(iComputenode)
        
        IP_ADDRESS2 = '192.168.100.' + str(iComputenode+1)
        compInfo = {
            'IP_ADDRESS':IP_ADDRESS2,
            'PORT'      :22,
            'USER'      :'root',
            'PASSWORD'  :nodePassword
        }
        compute = (compInfo ['IP_ADDRESS'], compInfo ['PORT'])
        channel1 = transport1.open_channel("direct-tcpip", compute, head)
        computenode = paramiko.SSHClient()
        computenode.set_missing_host_key_policy(paramiko.WarningPolicy())

        print("compurenode connecting...")
        computenode.connect(hostname=compInfo['IP_ADDRESS'],username=compInfo['USER'],password=compInfo['PASSWORD'],sock=channel1)
        print('computenode connected')

        # gmond.conf setting on computenode
        gmondConfSetup (jsonGanglia[OSType], nComputenode, nodeClient = computenode, hostname = host)

        computenode.close()
    
    headnode.close()
    computenode.close()
    del headnode, computenode
# % End of gangliaComp ()

########################
# gmond.conf setting   #
########################
def gmondConfSetup (jsonGanglia, nComputenode, nodeClient, hostname):
    cmdMain = jsonGanglia['command'][0]
    targetFile = jsonGanglia['targetFile']['gmond']

    conf = jsonGanglia['gmond']

    # Clear the Target File
    cmd = cmdMain + str (" ' ' > ") + targetFile
    nodeClient.exec_command (cmd)

    # clustre conf
    confVal = conf['cluster']
    for i, setting in enumerate(confVal):
        cmd = cmdMain + str (" '") + setting \
            + str ("' >> ") + targetFile
        nodeClient.exec_command (cmd)
    
    # host conf
    confVal = conf['host']
    for i, setting in enumerate(confVal):
        cmd = cmdMain + str ("'") + setting \
            + str ("' >> ") + targetFile
        nodeClient.exec_command (cmd)
    
    # udp_send_channel conf
    confVal = conf['udp_send_channel']
    for i in range (nComputenode + 1):
        # Setting Appropriate Hostname
        if i==0:
            host = 'headnode'
        elif i < 10:
            host = 'computenode00' + str (i)
        elif i < 100:
            host = 'computenode0' + str (i)
        else:
            host = 'computenode' + str(i)

        for j, setting in enumerate(confVal):
            if 'host = ' in setting:
                cmd = cmdMain + str (" '") \
                    + setting + host \
                    + str ("' >> ") + targetFile
                nodeClient.exec_command (cmd)
            else:
                cmd = cmdMain + str (" '") + setting \
                    + str ("' >> ") + targetFile
                nodeClient.exec_command (cmd)
    
    # recv_channel conf
    if hostname == 'headnode':
        
        # udp_recv_channel conf
        confVal = conf['udp_recv_channel']
        for i, setting in enumerate(confVal):
            cmd = cmdMain + str (" '") + setting \
                + str ("' >> ") + targetFile
            nodeClient.exec_command (cmd)

        # tcp_recv_channel conf
        confVal = conf['tcp_accept_channel']
        for i, setting in enumerate(confVal):
            cmd = cmdMain + str (" '") + setting \
                + str ("' >> ") + targetFile
            nodeClient.exec_command (cmd)
# End of gmondConfSetup ()

#######################
# Web Monitor Setting #
#######################
def webPasswdSetting (jsonGanglia, nodeClient):
    cmdMain = jsonGanglia['gangliaWeb'][0]
    print ("Setting for Web Monitoring Service")
    userName = input ("Enter User Name for Web Login -->")
    command = cmdMain + str("" ) + userName
    stdin, stdout, stderr = nodeClient.exec_command(command, get_pty = True)
            
    # Enter password
    while len(stdout.channel.in_buffer) == 0:
        # Wait until getting password prompt
        print ("Getting password prompt ...")
        time.sleep(1)
    monitorPassword = input ('Enter web monitor password to login -->')
    stdin.channel.send(monitorPassword + "\n")
            
    # Enter passwd again
    while len(stdout.channel.in_buffer) == 0:
        # Wait until getting password prompt
        print ("Getting password prompt")
        time.sleep(1)
    # monitorPassword = input ('Enter web monitor password to login  -->')
    stdin.channel.send(monitorPassword + "\n")

    out = stdout.read().decode()
    print('head_stdout = %s' % out)
# % End of webMonitorSetting ()

#######################
# gmetad.conf setting
########################
def gmetadConfSetup (jsonGanglia, nodeClient):
    cmdMain = jsonGanglia["command"][0]
    targetFile = jsonGanglia["targetFile"]["gmetad"]
    confSetting = jsonGanglia["gmetad"]

    for i, setting in enumerate (confSetting):
        cmd = cmdMain + str(" '") \
            + setting + str("' >> ") \
            + targetFile
        nodeClient.exec_command (cmd)

#######################
# ganglia.conf setting
#######################
def gangliaConfSetup (jsonGanglia, nodeClient):
    cmdMain = jsonGanglia["command"][0]
    targetFile = jsonGanglia["targetFile"]["gangliaConf"]
    confSetting = jsonGanglia["gangliaConf"]

    for i, setting in enumerate (confSetting):
        cmd = cmdMain + str (" '") \
            + setting + str ("' >> ") \
            + targetFile
        nodeClient.exec_command (cmd)