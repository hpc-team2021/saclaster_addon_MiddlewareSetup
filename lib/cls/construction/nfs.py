import sys
import json
import os
import base64
import requests
import pandas as pd
import ipaddress
import logging

logger = logging.getLogger("sacluster").getChild(os.path.basename(__file__))

from res_out import response_output
from build_error import build_error, res_check_post,res_check_put

path = "../../.."
os.chdir(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(path + "/lib/others")

from API_method import get, post, put
from info_print import printout, printout_cluster

def setting_nfs(url,sub_url,zone,switch_id,cluster_id,auth_res,configuration_info,fp = "", info_list = [1,0,0,0], monitor_info_list = [1,0,0,0], api_index = True):
    _ = printout_cluster("setting NFS ……", cls_monitor_level = 2, set_monitor_level = configuration_info["monitor level"], info_list = info_list, monitor_info_list = monitor_info_list, fp = fp, msg_token = configuration_info["monitor token"])
    logger.debug("setting NFS")
    #_ = printout("setting NFS ……",fp = fp ,info_list = info_list,msg_token = msg_token)
    nfs_name = "NFS"
    #nfs_plan = configuration_info["NFS plan ID in " + zone]
    ip = str(ipaddress.ip_address('192.168.1.200'))
    nfs_param = {"Appliance":{"Class":"nfs","Name":nfs_name,"Plan":{"ID":configuration_info["NFS plan ID"][zone]},"Tags":[cluster_id],"Remark":{"Network":{"NetworkMaskLen":24},"Servers":[{"IPAddress":ip}],"Switch":{"ID":switch_id}}}} 
    #nfs_param = {"Appliance":{"Class":"nfs","Name":nfs_name,"Plan":{"ID":nfs_plan},"Switch":{"ID":switch_id}}} 

    if (api_index == True):
        while(True):
            nfs_res = post(url+sub_url[6],auth_res,nfs_param)
            check = res_check_post(configuration_info, nfs_res,fp = fp, info_list = info_list,monitor_info_list = monitor_info_list)
            if check == True:
                nfs_id = nfs_res["Appliance"]["ID"]
                logger.info("NFS ID: " + nfs_id + "-Success")
                break
            else:
                build_error(configuration_info, fp = fp, info_list = info_list,monitor_info_list = monitor_info_list)
                '''
            if ("is_ok" in nfs_res.keys()):
                if nfs_res["is_ok"] == True:
                    nfs_id = nfs_res["Appliance"]["ID"]
                    break
                else:
                    _ = printout("Error:",fp = fp, info_list = info_list)
                    rf = response_output("Error_setting_nfs",nfs_res)
                    build_error(info_list = info_list,fp = fp)
            elif ("is_fatal" in nfs_res.keys()):
                _ = printout("Status:" + nfs_res["status"], info_list = info_list , fp = fp)
                _ = printout("Error:" + nfs_res["error_msg"],fp = fp, info_list = info_list)
                rf = response_output("Error_setting_nfs",nfs_res)
                build_error(info_list = info_list,fp = fp)
                '''
    else:
        nfs_res = "API is not used."
        nfs_id = "0000"
    
    #rf = response_output("setting_nfs",nfs_res)

    return nfs_res,nfs_id