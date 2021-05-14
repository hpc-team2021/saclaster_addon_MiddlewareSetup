import sys
import json
import os
import base64
import requests
import pandas as pd
import logging

logger = logging.getLogger("sacluster").getChild(os.path.basename(__file__))

from res_out import response_output
from build_error import build_error, res_check_post, res_check_get

path = "../../.."
os.chdir(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(path + "/lib/others")

from API_method import get, post, put
from info_print import printout, printout_cluster

def add_interface(url,sub_url,node_id,configuration_info, auth_res,fp = "", info_list = [1,0,0,0], monitor_info_list = [1,0,0,0], api_index = True):
    _ = printout_cluster("adding nic ……", cls_monitor_level = 3, set_monitor_level = configuration_info["monitor level"], info_list = info_list, monitor_info_list = monitor_info_list, fp = fp, msg_token = configuration_info["monitor token"])
    logger.debug("adding nic")
    add_nic_param = {"Interface":{"Server":{"ID":node_id}}, "Count":0}
    #add_nic_param = {"Interface":{"Server":{"ID":"123456"}}, "Count":0}
    if (api_index == True):
        while(True):
            add_nic_response = post(url+sub_url[3],auth_res,add_nic_param)
            check = res_check_post(configuration_info, add_nic_response,fp = fp, info_list = info_list,monitor_info_list = monitor_info_list)
            if check == True:
                nic_id = add_nic_response["Interface"]["ID"]
                logger.info("nic ID: " + nic_id + "-Success")
                break
            else:
                build_error(configuration_info, fp = fp, info_list = info_list,monitor_info_list = monitor_info_list)
            '''
            if ("is_ok" in add_nic_response.keys()):
                if add_nic_response["is_ok"] == True:
                    nic_id = add_nic_response["Interface"]["ID"]
                    break
                else:
                    _ = printout("Error:",fp = fp, info_list = info_list)
                    rf = response_output("Error_add_interface",add_nic_response)
                    build_error(info_list = info_list,fp = fp)
            elif ("is_fatal" in add_nic_response.keys()):
                _ = printout("Status:" + add_nic_response["status"], info_list = info_list , fp = fp)
                _ = printout("Error:" + add_nic_response["error_msg"],fp = fp, info_list = info_list)
                rf = response_output("Error_add_interface",add_nic_response)
                build_error(info_list = info_list,fp = fp)
                '''
    else:
        add_nic_response = "API is not used."
        nic_id = "0000"
    
    #rf = response_output("add_interface",add_nic_response)

    return add_nic_response,nic_id

'''
def interface_info(url,sub_url,node_id,configuration_info, auth_res,fp = "", info_list = [1,0,0,0], monitor_info_list = [1,0,0,0], api_index = True):
    url_interface = sub_url[0] + "/" + node_id + sub_url[3]
    if (api_index == True):
        while(True):
            interface_info = get(url+url_interface,auth_res)
            check = res_check_get(configuration_info, interface_info,fp = fp, info_list = info_list, monitor_info_list = monitor_info_list)
            if check == True:
                interface_info_list = interface_info["Interfaces"]
                l_id = [d.get('ID') for d in interface_info_list]
                break
            else:
                build_error(configuration_info, fp = fp, info_list = info_list, monitor_info_list = monitor_info_list)
            
            if ("is_ok" in interface_info.keys()):
                if interface_info["is_ok"] == True:
                    interface_info_list = interface_info["Interfaces"]
                    l_id = [d.get('ID') for d in interface_info_list]
                    break
                else:
                    _ = printout("Error:",fp = fp, info_list = info_list)
                    rf = response_output("Error_interface_info",interface_info)
                    build_error(info_list = info_list,fp = fp)
            elif ("is_fatal" in interface_info.keys()):
                _ = printout("Status:" + interface_info["status"], info_list = info_list , fp = fp)
                _ = printout("Error:" + interface_info["error_msg"],fp = fp, info_list = info_list)
                rf = response_output("Error_interface_info",interface_info)
                build_error(info_list = info_list,fp = fp)
                
    else:
        interface_info = "API is not used."
        l_id = ["00","00"]

    #rf = response_output("interface_info_" + node_id , interface_info)

    return l_id
    '''