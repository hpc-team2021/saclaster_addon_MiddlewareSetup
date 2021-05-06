import sys
import json
import os
import base64
import requests
import pandas as pd
import ipaddress
import logging

logger = logging.getLogger("sacluster").getChild(os.path.basename(__file__))

from interface import add_interface
from res_out import response_output
from build_error import build_error, res_check_post, res_check_put

path = "../../.."
os.chdir(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(path + "/lib/others")

from API_method import get, post, put
from info_print import printout, printout_cluster

def create_switch(url,sub_url,cluster_id,auth_res,configuration_info,name = "",fp = "", info_list = [1,0,0,0], monitor_info_list = [1,0,0,0] ,api_index = True):
    #_ = printout("creating switch ……", fp = fp , info_list = info_list)

    if name == "compute":
        _ = printout_cluster("creating shared switch ……", cls_monitor_level = 2, set_monitor_level = configuration_info["monitor level"], info_list = info_list, monitor_info_list = monitor_info_list, fp = fp, msg_token = configuration_info["monitor token"])
        logger.debug("creating shared switch")
        #_ = printout("creating shared switch ……", fp = fp , info_list = info_list,msg_token = msg_token)
        switch_name = "Switch for compute node"
    else:
        _ = printout_cluster("creating main switch ……", cls_monitor_level = 2, set_monitor_level = configuration_info["monitor level"], info_list = info_list, monitor_info_list = monitor_info_list, fp = fp, msg_token = configuration_info["monitor token"])
        logger.debug("creating main switch")
        #_ = printout("creating main switch ……", fp = fp , info_list = info_list,msg_token = msg_token)
        switch_name = "Switch for " + configuration_info["config name"]
    
    switch_param = {"Switch":{"Name":switch_name,"Tags":[cluster_id]},"Count":0}
    
    if (api_index == True):
        while(True):
            switch_response = post(url+sub_url[2],auth_res,switch_param)
            check = res_check_post(configuration_info, switch_response,fp = fp, info_list = info_list, monitor_info_list = monitor_info_list)
            if check == True:
                switch_id = switch_response["Switch"]["ID"]
                logger.info("switch ID: " + switch_id + "-Success")
                break
            else:
                build_error(configuration_info, info_list = info_list,fp = fp, monitor_info_list = monitor_info_list)
            
            '''
            if ("is_ok" in switch_response.keys()):
                if switch_response["is_ok"] == True:
                    switch_id = switch_response["Switch"]["ID"]
                    break
                else:
                    _ = printout("Error:",fp = fp, info_list = info_list)
                    rf = response_output("Error_create_switch",switch_response)
                    build_error(info_list = info_list,fp = fp)
            elif ("is_fatal" in switch_response.keys()):
                _ = printout("Status:" + switch_response["status"], info_list = info_list , fp = fp)
                _ = printout("Error:" + switch_response["error_msg"],fp = fp, info_list = info_list)
                rf = response_output("Error_create_switch",switch_response)
                build_error(info_list = info_list,fp = fp)
                '''
    else:
        switch_response = "API is not used."
        switch_id = "0000"

    #rf = response_output("create_switch",switch_response)
    
    return switch_response,switch_id

def connect_switch(url,switch_id,nic_id, configuration_info,auth_res,fp = "", info_list = [1,0,0,0],monitor_info_list = [1,0,0,0], api_index = True):
    _ = printout_cluster("connecting switch to nic ……", cls_monitor_level = 3, set_monitor_level = configuration_info["monitor level"], info_list = info_list, monitor_info_list = monitor_info_list, fp = fp, msg_token = configuration_info["monitor token"])
    logger.debug("connecting switch to nic")
    sub_url_con = "/interface/" + nic_id + "/to/switch/" + switch_id
    if (api_index == True):
        while(True):
            connect_switch_response = put(url+sub_url_con,auth_res)
            check = res_check_put(configuration_info, connect_switch_response,fp = fp, info_list = info_list,monitor_info_list = monitor_info_list,)
            if check == True:
                logger.debug("connected switch to nic: " + switch_id + "-" + nic_id)
                break
            else:
                build_error(configuration_info, info_list = info_list,fp = fp,monitor_info_list = monitor_info_list,)
            '''
            if ("Success" in connect_switch_response.keys()):
                if connect_switch_response["Success"] == True:
                    break
                else:
                    _ = printout("Error:",fp = fp, info_list = info_list)
                    rf = response_output("Error_connect_switch",connect_switch_response)
                    build_error(info_list = info_list,fp = fp)
            elif ("is_fatal" in connect_switch_response.keys()):
                _ = printout("Status:" + connect_switch_response["status"], info_list = info_list , fp = fp)
                _ = printout("Error:" + connect_switch_response["error_msg"],fp = fp, info_list = info_list)
                rf = response_output("Error_connect_switch",connect_switch_response)
                build_error(info_list = info_list,fp = fp)
                '''
    else:
        connect_switch_response = "API is not used."

    #rf = response_output("connect_switch",connect_switch_response)

    return connect_switch_response

def compute_network(url, sub_url, compute_node_list, cluster_id, configuration_info, auth_res,fp = "", info_list = [1,0,0,0],monitor_info_list = [1,0,0,0], api_index = True):
    logger.debug("start creating compute network")
    name = "compute"
    com_switch_res,com_switch_id = create_switch(url,sub_url,cluster_id,name = name,auth_res = auth_res, configuration_info = configuration_info, fp = fp, info_list  = info_list, monitor_info_list = monitor_info_list, api_index = api_index)
    com_nic_list = []
    for com_id in compute_node_list:
        com_nic_res, com_nic_id = add_interface(url,sub_url,com_id,auth_res = auth_res, configuration_info = configuration_info, fp = fp, info_list  = info_list, monitor_info_list = monitor_info_list, api_index = api_index)
        connect_switch_res = connect_switch(url,com_switch_id,com_nic_id, configuration_info = configuration_info, auth_res  = auth_res,fp = fp, info_list  = info_list, monitor_info_list = monitor_info_list, api_index = api_index)
        com_nic_list.append(com_nic_id)
    return connect_switch_res,com_nic_list





