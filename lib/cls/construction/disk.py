import sys
import json
import os
import base64
import requests
import pandas as pd
import logging

logger = logging.getLogger("sacluster").getChild(os.path.basename(__file__))

from res_out import response_output
from build_error import build_error, res_check_post, res_check_put

path = "../../.."
os.chdir(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(path + "/lib/others")

from API_method import get, post, put
from info_print import printout, printout_cluster

def add_disk(url,sub_url,zone,disk_name,cluster_id,auth_res,configuration_info,fp = "", info_list = [1,0,0,0], monitor_info_list = [1,0,0,0],api_index = True):
    _ = printout_cluster("creating disk ……", cls_monitor_level = 2, set_monitor_level = configuration_info["monitor level"], info_list = info_list, monitor_info_list = monitor_info_list, fp = fp, msg_token = configuration_info["monitor token"])
    #_ = printout("creating disk ……", fp = fp, info_list = info_list,msg_token = msg_token)
    logger.debug("creating disk for " + disk_name)
    if disk_name in "head":
        disk_type = configuration_info["disk type for head node"]
        disk_size = configuration_info["disk size for head node"]
        os_type = configuration_info["OS ID for head node"][zone]
        
    else:
        disk_type = configuration_info["disk type for compute node"]
        disk_size = configuration_info["disk size for compute node"]
        os_type = configuration_info["OS ID for compute node"][zone]

    while (True):
        if disk_type == "SSD":
            disk_type_id = 4
            break
        elif disk_type == "HDD":
            disk_type_id = 2
            break
        #else:
            #_ = printout_cluster("creating disk ……", cls_monitor_level = 2, set_monitor_level = configuration_info["monitor level"], info_list = info_list, monitor_info_list = monitor_info_list, fp = fp, msg_token = configuration_info["monitor token"])
            #_ = printout("not disk type",fp = fp , info_list = info_list,msg_token = msg_token)
            #disk_type = printout("Disk type(SSD or HDD):",info_type = 2, info_list = info_list, fp = fp,msg_token = msg_token)
    
    
    param = {"Disk":{"Name":disk_name,"Plan":{"ID":disk_type_id},"SizeMB":disk_size,"SourceArchive":{"Availability": "available","ID":os_type},"Tags":[cluster_id]},"Config":{"Password":configuration_info["password"],"HostName":configuration_info["username"]}}
    #param = {"Disk":{"Name":disk_name,"Plan":{"ID":3},"SizeMB":disk_size,"SourceArchive":{"Availability": "available","ID":os_type}},"Config":{"Password":"takahira","Notes":{"ID":"112900860243"}}}
    if (api_index == True):
        while(True):
            disk_res = post(url+sub_url[1], auth_res,param)
            check = res_check_post(configuration_info, disk_res,fp = fp, info_list = info_list, monitor_info_list = monitor_info_list)
            if check == True:
                disk_id = disk_res["Disk"]["ID"]
                logger.info("disk ID: " + disk_id + "-Success")
                break
            else:
                build_error(configuration_info, fp = fp, info_list = info_list,monitor_info_list = monitor_info_list)
            '''
            if ("is_ok" in disk_res.keys()):
                if disk_res["is_ok"] == True:
                    disk_id = disk_res["Disk"]["ID"]
                    break
                else:
                    _ = printout("Error:",fp = fp, info_list = info_list)
                    rf = response_output("Error_create_disk",disk_res)
                    build_error(info_list = info_list,fp = fp)
            elif ("is_fatal" in disk_res.keys()):
                _ = printout("Status:" + disk_res["status"], info_list = info_list , fp = fp)
                _ = printout("Error:" + disk_res["error_msg"],fp = fp, info_list = info_list)
                rf = response_output("Error_create_disk",disk_res)
                build_error(info_list = info_list,fp = fp)'''
    else:
        disk_res = "API is not used."
        disk_id = "0000"
    logger.debug("created disk for " + disk_name)
    #rf = response_output("create_disk",disk_res)
    
    return disk_res,disk_id


def connect_server_disk(url,disk_id,server_id, configuration_info, auth_res,fp = "", info_list = [1,0,0,0],monitor_info_list = [1,0,0,0],api_index = True):
    _ = printout_cluster("connecting disk to server ……", cls_monitor_level = 3, set_monitor_level = configuration_info["monitor level"], info_list = info_list, monitor_info_list = monitor_info_list, fp = fp, msg_token = configuration_info["monitor token"])
    logger.debug("connecting disk to server")
    url_disk = "/disk/" + disk_id + "/to/server/" + server_id
    if (api_index == True):
        while(True):
            server_disk_res = put(url+url_disk,auth_res)
            check = res_check_put(configuration_info, server_disk_res, fp = fp, info_list = info_list,monitor_info_list = monitor_info_list)
            if check == True:
                logger.debug("connected disk to server: " + server_id + "-" + disk_id)
                break
            else:
                build_error(configuration_info, fp = fp,info_list = info_list,monitor_info_list = monitor_info_list)
            '''
            if ("Success" in server_disk_res.keys()):
                if server_disk_res["Success"] == True:
                    break
                else:
                    _ = printout("Error:",fp = fp, info_list = info_list)
                    rf = response_output("Error_connect_disk",server_disk_res)
                    build_error(info_list = info_list,fp = fp)
            elif ("is_fatal" in server_disk_res.keys()):
                _ = printout("Status:" + server_disk_res["status"], info_list = info_list , fp = fp)
                _ = printout("Error:" + server_disk_res["error_msg"],fp = fp, info_list = info_list)
                rf = response_output("Error_connect_disk",server_disk_res)
                build_error(info_list = info_list,fp = fp)'''
    else:
        server_disk_res = "API is not used."

    
    #rf = response_output("connect_disk",server_disk_res)
    #_ = printout("connecting disk ……", info_list = info_list, fp = fp)

    return server_disk_res