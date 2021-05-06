import sys
import json
import os
import base64
import requests
import pandas as pd
import random
import pprint
import datetime
import time
import ipaddress
import logging

logger = logging.getLogger("sacluster").getChild(os.path.basename(__file__))
#from server import build_server, Serverplan, build_compute_node, cluster_id_def
from server import build_server, build_compute_node, cluster_id_def
from switch import create_switch, connect_switch, compute_network
from interface import add_interface
from disk import add_disk, connect_server_disk
from bridge import create_bridge,connect_bridge_switch
from nfs import setting_nfs
from cluster_info import cluster_info
from res_out import response_output

path = "../../.."
os.chdir(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(path + "/lib/others")

from API_method import get, post, put
from info_print import printout, printout_cluster


def json_input(filename):
    with open(filename, 'r') as f:
        json_f = json.load(f)
    return json_f


def main(configuration_info, auth_res, fp = "" , info_list = [1,0,0,0], monitor_info_list = [1,0,0,0], api_index = True):
    #filename = "Setting.json"

    #if(os.path.exists(path + "/setting/" + filename) == True):
        #setting_info = json_input(path + "/setting/" + filename)
        #global auth_res
        #auth_res = base64.b64encode('{}:{}'.format(setting_info["access token"], setting_info["access token secret"]).encode('utf-8'))
    #else:
        #_ = printout("Error: Setting.json does not exist in sacluster/setting",info_list = [1,0,0,0], fp = '')
        #sys.exit()
    #while (True):
        #config_file = printout("Configuration File Name:",info_type = 2, info_list = [1,0,0,0], fp = '')
        #configuration_info = json_input("./trial_configfile2.json")
        #if(os.path.exists("./" + config_file ) == True):
            #global configuration_info
            #configuration_info = json_input("./" + config_file)
            #break
        #else:
            #_ = printout("INFO: " + config_file + " does not exist. ",info_list = [1,0,0,0], fp = '')
    
    #starttime = time.time()
    #クラスタの構築
    _ = printout_cluster("Start building the cluster", cls_monitor_level = 1, set_monitor_level = configuration_info["monitor level"], info_list = info_list, monitor_info_list = monitor_info_list, fp = fp, msg_token = configuration_info["monitor token"])
    logger.debug("Start building the cluster")
    auth_res = build_cluster(configuration_info, auth_res, fp = fp, info_list  = info_list, monitor_info_list = monitor_info_list, api_index = api_index)
    _ = printout_cluster("Finished building the cluster", cls_monitor_level = 1, set_monitor_level = configuration_info["monitor level"], info_list = info_list, monitor_info_list = monitor_info_list, fp = fp, msg_token = configuration_info["monitor token"])
    logger.debug("Finished building the cluster")
    #elapsed_time = time.time() - starttime

    #_ = printout("elapsed_time:{0}".format(elapsed_time) + "[sec]" , info_list = [1,0,0,0], fp = '')

    return auth_res

def build_cluster(configuration_info, auth_res, fp = "", info_list = [1,0,0,0], monitor_info_list = [1,0,0,0], api_index = True):
    zone_list = configuration_info["zone"]
    #zone_list = zone_list.split(',')
    
    #nfs_zone = []
    if configuration_info["NFS"] == True:
        nfs_zone = configuration_info["NFS zone"]
        #.split(",")
    head_zone = configuration_info["place of head node"]
    
    url_list = []
    for i in zone_list:
        url_list.append("https://secure.sakura.ad.jp/cloud/zone/"+ i +"/api/cloud/1.1")
    head_url = "https://secure.sakura.ad.jp/cloud/zone/"+ head_zone +"/api/cloud/1.1"
    url_list.append(head_url)
    sub_url = ["/server","/disk","/switch","/interface","/bridge","/tag","/appliance"]
    
    
    compute_id_zone = {}
    cluster_id = "cluster ID:" + str(cluster_id_def(configuration_info, url_list[0],sub_url,auth_res,fp = fp, info_list = info_list, monitor_info_list = monitor_info_list, api_index = api_index))
    logger.info("nunmber of zones: " + len(zone_list))
    if len(zone_list) == 1:
        head_id_list,l_compute_node_id = build_head_zone(url_list[0],sub_url,zone_list[0],cluster_id,auth_res = auth_res,configuration_info = configuration_info,fp = fp, info_list  = info_list, monitor_info_list = monitor_info_list, api_index = api_index)
        compute_node_id_list = l_compute_node_id
        compute_id_zone[zone_list[0]] = compute_node_id_list
        nfs_bool = zone_list[0] in nfs_zone
        if nfs_bool == True:
            #nfs_plan = configuration_info["NFS plan ID"][zone_list[0]] 
            nfs_res,nfs_id = setting_nfs(url_list[0],sub_url,zone_list[0],head_id_list[2],cluster_id,auth_res = auth_res,configuration_info = configuration_info,fp = fp, info_list  = info_list, monitor_info_list = monitor_info_list, api_index = api_index)
    elif len(zone_list) >= 2 :
        #config_name = configuration_info["config name"]
        bridge_res,bridge_id = create_bridge(url_list[-1],sub_url,auth_res = auth_res,configuration_info = configuration_info, fp = fp, info_list = info_list, monitor_info_list = monitor_info_list, api_index = api_index)
        compute_node_id_list = []
        
        i = 0
        for zone in zone_list:
            #url = "https://secure.sakura.ad.jp/cloud/zone/"+ zone[i] +"/api/cloud/1.1"
            if url_list[i] == url_list[-1]:
                head_id_list,l_compute_node_id = build_head_zone(url_list[i],sub_url,zone,cluster_id,auth_res = auth_res,configuration_info = configuration_info,fp = fp, info_list  = info_list, monitor_info_list = monitor_info_list, api_index = api_index)
                #connect bridge to switch
                bridge_switch_res = connect_bridge_switch(url_list[i],head_id_list[2],bridge_id,configuration_info = configuration_info,auth_res = auth_res,fp = fp, info_list  = info_list,monitor_info_list = monitor_info_list, api_index = api_index)
                compute_node_id_list.extend(l_compute_node_id)
                compute_id_zone[zone] = l_compute_node_id
                nfs_bool = zone in nfs_zone
                if nfs_bool == True:
                    #nfs_plan = configuration_info["NFS plan ID"][zone]
                    nfs_res,nfs_id = setting_nfs(url_list[i],sub_url,zone,head_id_list[2],cluster_id,auth_res = auth_res,configuration_info = configuration_info,fp = fp, monitor_info_list = monitor_info_list, info_list  = info_list, api_index = api_index)

            elif url_list[i] != url_list[-1]:
                logger.debug("start building compute zone")
                compute_switch_response,compute_switch_id = create_switch(url_list[i],sub_url,cluster_id,auth_res = auth_res,configuration_info = configuration_info,fp = fp, info_list  = info_list,monitor_info_list = monitor_info_list, api_index = api_index)
                bridge_switch_res = connect_bridge_switch(url_list[i],compute_switch_id,bridge_id,configuration_info = configuration_info, auth_res = auth_res,fp = fp, info_list  = info_list,monitor_info_list = monitor_info_list ,api_index = api_index)
                #number_of_compute_node = int(configuration_info["the number of compute node in " + zone])
                compute_server_response,l_compute_node_id = build_compute_node(url_list[i],sub_url,compute_switch_id,zone,cluster_id,auth_res = auth_res,configuration_info = configuration_info,fp = fp, info_list  = info_list,monitor_info_list = monitor_info_list ,api_index = api_index)
                if configuration_info["compute network"] == "True":
                    com_network,com_nic_list = compute_network(url_list[i],sub_url,l_compute_node_id,cluster_id,auth_res = auth_res,fp = fp, info_list  = info_list, api_index = api_index)
                compute_node_id_list.extend(l_compute_node_id)
                compute_id_zone[zone] = l_compute_node_id
                nfs_bool = zone in nfs_zone
                if nfs_bool == True:
                    #nfs_plan = configuration_info["NFS plan ID"][zone]
                    nfs_res,nfs_id = setting_nfs(url_list[i],sub_url,zone,compute_switch_id,cluster_id,auth_res = auth_res,configuration_info = configuration_info,fp = fp, monitor_info_list = monitor_info_list, info_list  = info_list, api_index = api_index)
                logger.debug("finish building compute zone")
            i += 1
    cluster_info_res = cluster_info(url_list,sub_url,head_id_list,compute_node_id_list,compute_id_zone,cluster_id,auth_res = auth_res,configuration_info = configuration_info,fp = fp, info_list  = info_list, monitor_info_list = monitor_info_list,api_index = api_index)
    return auth_res

def build_head_zone(url,sub_url,zone,cluster_id,auth_res,configuration_info,fp = "", info_list = [1,0,0,0], monitor_info_list = [1,0,0,0],api_index = True):
    logger.debug("start building head zone")
    head_node_name = "headnode"
    #core = configuration_info["the number of core for head node"]
    #memory = configuration_info["size of memory for head node"]
    #interfacedriver = configuration_info["connection type for head node"]
    server_response,head_node_id = build_server(url,sub_url,head_node_name,cluster_id, auth_res = auth_res,configuration_info = configuration_info,fp = fp, info_list  = info_list, monitor_info_list = monitor_info_list,api_index = api_index)
    #add disk headnode
    #disk_type = configuration_info["disk type for head node"]
    #disk_size = configuration_info["disk size for head node"]
    #os_type = configuration_info["OS ID for head node"]
    head_disk_res,head_disk_id = add_disk(url,sub_url,zone,head_node_name,cluster_id,auth_res = auth_res,configuration_info = configuration_info,fp = fp, info_list  = info_list,monitor_info_list = monitor_info_list,api_index = api_index)
    head_server_disk_res = connect_server_disk(url, head_disk_id, head_node_id, configuration_info, auth_res = auth_res,fp = fp, info_list  = info_list,monitor_info_list = monitor_info_list,api_index = api_index)
    #add iso image headnode
    #head_iso_image_res = iso_image_insert(url,head_node_name,head_node_id,zone,fp = fp, info_list  = info_list, api_index = api_index)
    #create switch
    head_switch_response,head_switch_id = create_switch(url,sub_url,cluster_id,auth_res = auth_res,configuration_info = configuration_info,fp = fp, info_list  = info_list,monitor_info_list = monitor_info_list ,api_index = api_index)
    
    #add interface in head node
    add_nic_response,nic_id = add_interface(url,sub_url,head_node_id,auth_res = auth_res, configuration_info = configuration_info,fp = fp, info_list  = info_list, monitor_info_list = monitor_info_list,api_index = api_index)

    #interface to switch
    connect_switch_response = connect_switch(url,head_switch_id,nic_id,auth_res = auth_res, configuration_info = configuration_info,fp = fp, info_list  = info_list, monitor_info_list = monitor_info_list, api_index = api_index)
    #create compute node
    #number_of_compute_node = int(configuration_info["the number of compute node in " + zone])
    compute_server_response,l_compute_node_id = build_compute_node(url,sub_url,head_switch_id,zone,cluster_id,auth_res = auth_res,configuration_info = configuration_info,fp = fp, info_list  = info_list,monitor_info_list = monitor_info_list ,api_index = api_index)
    if configuration_info["compute network"] == "True":
        com_network,com_nic_list = compute_network(url,sub_url,l_compute_node_id,cluster_id, configuration_info = configuration_info, auth_res = auth_res,fp = fp, info_list  = info_list,monitor_info_list = monitor_info_list ,api_index = api_index)
    id_list = [head_node_id , head_disk_id , head_switch_id , nic_id , l_compute_node_id]
    logger.debug("finish building head zone")
    return id_list,l_compute_node_id


#dt_now = datetime.datetime.now()
#dt_now = dt_now.strftime("%Y_%m_%d_%H%M%S")
#f = open(path + "/res/res_" + dt_now + ".txt", 'w')
#info_list = [1,0,0,1]


#auth_res = build_cluster(fp = f, info_list  = info_list, api_index = True)
#main(fp= f , info_list = info_list , api_index = True)
#server_power_res = starting_server(url)
#main(fp = "", info_list = [1,0,0,0],api_index=True)
#f.close()