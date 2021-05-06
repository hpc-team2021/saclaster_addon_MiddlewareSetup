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

def create_bridge(url,sub_url,auth_res,configuration_info,fp = "", info_list = [1,0,0,0], monitor_info_list = [1,0,0,0], api_index = True):
    _ = printout_cluster("creating bridge ……", cls_monitor_level = 2, set_monitor_level = configuration_info["monitor level"], info_list = info_list, monitor_info_list = monitor_info_list, fp = fp, msg_token = configuration_info["monitor token"])
    logger.debug("creating bridge")
    #_ = printout("creating bridge ……", fp = fp ,info_list = info_list,msg_token = msg_token)
    bridge_name = "Bridge for " + configuration_info["config name"]
    param = {"Bridge":{"Name":bridge_name}}
    

    if (api_index == True):
        while(True):
            bridge_res = post(url+sub_url[4],auth_res,param)
            check = res_check_post(configuration_info, bridge_res, fp = fp, info_list = info_list, monitor_info_list = monitor_info_list)
            if check == True:
                bridge_id = bridge_res["Bridge"]["ID"]
                logger.info("bridge ID: " + bridge_id + "-Success")
                break
            else:
                build_error(configuration_info, fp = fp, info_list = info_list, monitor_info_list = monitor_info_list)
                '''
            if ("is_ok" in bridge_res.keys()):
                if bridge_res["is_ok"] == True:
                    bridge_id = bridge_res["Bridge"]["ID"]
                    break
                else:
                    _ = printout("Error:",fp = fp, info_list = info_list)
                    rf = response_output("Error_create_bridge",bridge_res)
                    build_error(info_list = info_list,fp = fp)
            elif ("is_fatal" in bridge_res.keys()):
                _ = printout("Status:" + bridge_res["status"], info_list = info_list , fp = fp)
                _ = printout("Error:" + bridge_res["error_msg"],fp = fp, info_list = info_list)
                rf = response_output("Error_create_bridge",bridge_res)
                build_error(info_list = info_list,fp = fp)
                '''
    else:
        bridge_res = "API is not used."
        bridge_id = "0000"

    #rf = response_output("create_bridge",bridge_res)
    
    return bridge_res,bridge_id

def connect_bridge_switch(url,switch_id,bridge_id, configuration_info,auth_res,fp = "", info_list = [1,0,0,0], monitor_info_list = [1,0,0,0], api_index = True):
    _ = printout_cluster("connecting switch to bridge ……", cls_monitor_level = 3, set_monitor_level = configuration_info["monitor level"], info_list = info_list, monitor_info_list = monitor_info_list, fp = fp, msg_token = configuration_info["monitor token"])
    logger.debug("connecting switch to bridge")
    url_bridge = "/switch/" + switch_id + "/to/bridge/" + bridge_id
    if (api_index == True):
        while(True):
            bridge_switch_res = put(url+url_bridge,auth_res)
            check = res_check_put(configuration_info, bridge_switch_res,fp = fp, info_list = info_list,monitor_info_list = monitor_info_list)
            if check == True:
                logger.debug("connected switch to bridge: " + switch_id + "-" + bridge_id)
                break
            else:
                build_error(configuration_info, fp = fp, info_list = info_list,monitor_info_list = monitor_info_list)
                '''
            if ("Success" in bridge_switch_res.keys()):
                if bridge_switch_res["Success"] == True:
                    break
                else:
                    _ = printout("Error:",fp = fp, info_list = info_list)
                    rf = response_output("Error_connect_bridge",bridge_switch_res)
                    build_error(info_list = info_list,fp = fp)
            elif ("is_fatal" in bridge_switch_res.keys()):
                _ = printout("Status:" + bridge_switch_res["status"], info_list = info_list , fp = fp)
                _ = printout("Error:" + bridge_switch_res["error_msg"],fp = fp, info_list = info_list)
                rf = response_output("Error_connect_bridge",bridge_switch_res)
                build_error(info_list = info_list,fp = fp)
                '''
    else:
        bridge_switch_res = "API is not used."
    
    #rf = response_output("connect_bridge",bridge_switch_res)
    return bridge_switch_res