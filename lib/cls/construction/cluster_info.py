import sys
import json
import os
import base64
import requests
import pandas as pd
import ipaddress
import datetime
import json
import logging

logger = logging.getLogger("sacluster").getChild(os.path.basename(__file__))

from server import cluster_id_def
from res_out import response_output
from build_error import build_error,res_check_put

path = "../../.."
os.chdir(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(path + "/lib/others")

from API_method import get, post, put
from info_print import printout, printout_cluster


def cluster_info(url_list,sub_url, head_id_list,compute_node_id_list,compute_id_zone,cluster_id,auth_res,configuration_info,fp = "", info_list = [1,0,0,0], monitor_info_list = [1,0,0,0] ,api_index = True):
    _ = printout_cluster("###Cluster Infomation###", cls_monitor_level = 1, set_monitor_level = configuration_info["monitor level"], info_list = info_list, monitor_info_list = monitor_info_list, fp = fp, msg_token = configuration_info["monitor token"])
    #_ = printout("###Cluster Infomation###" , info_list = info_list, fp = fp,msg_token = msg_token)
    cls_info = {}
    cls_info["config name"] = configuration_info["config name"]
    
    _ = printout_cluster("config name:" + cls_info["config name"], cls_monitor_level = 1, set_monitor_level = configuration_info["monitor level"], info_list = info_list, monitor_info_list = monitor_info_list, fp = fp, msg_token = configuration_info["monitor token"])
    #_ = printout("config name:" + cls_info["config name"], info_list = info_list, fp = fp,msg_token = msg_token)
    
    #cluster_id = cluster_id_def(url_list[-1],sub_url,auth_res = auth_res,fp = fp, info_list = info_list , api_index = api_index)
    #cluster_id = "cluster ID:" + str(cluster_id)
    cls_info["cluster ID"] = str(cluster_id)
    _ = printout_cluster("cluster ID:" + cls_info["cluster ID"], cls_monitor_level = 1, set_monitor_level = configuration_info["monitor level"], info_list = info_list, monitor_info_list = monitor_info_list, fp = fp, msg_token = configuration_info["monitor token"])
    #_ = printout("cluster ID:" + cls_info["cluster ID"], info_list = info_list, fp = fp,msg_token = msg_token)
    
    cls_info["head node ID"] = head_id_list[0]
    _ = printout_cluster("head node ID:" + cls_info["head node ID"], cls_monitor_level = 1, set_monitor_level = configuration_info["monitor level"], info_list = info_list, monitor_info_list = monitor_info_list, fp = fp, msg_token = configuration_info["monitor token"])
    _ = printout_cluster("compute node ID:", cls_monitor_level = 1, set_monitor_level = configuration_info["monitor level"], info_list = info_list, monitor_info_list = monitor_info_list, fp = fp, msg_token = configuration_info["monitor token"])
    #_ = printout("head node ID:" + cls_info["head node ID"],info_list = info_list, fp = fp,msg_token = msg_token)
    #_ = printout("compute node ID:" ,info_list = info_list, fp = fp,msg_token = msg_token)
    for k in compute_id_zone.keys():
        id_list = ','.join(compute_id_zone[k])
        _ = printout_cluster(k + ":" + id_list, cls_monitor_level = 1, set_monitor_level = configuration_info["monitor level"], info_list = info_list, monitor_info_list = monitor_info_list, fp = fp, msg_token = configuration_info["monitor token"])
        #_ = printout( k + ":" + id_list,info_list = info_list, fp = fp,msg_token = msg_token)
    zone_list = configuration_info["zone"]
    #zone_list = zone_list.split(',')
    if len(zone_list) == 1:
        #number_of_compute_node = "number of compute node:" + str(configuration_info["the number of compute node in " + zone[0]])
        cls_info["number of compute node"] = str(configuration_info["the number of compute node in " + zone_list[0]])
        _ = printout_cluster("number of compute node:" + cls_info["number of compute node"], cls_monitor_level = 1, set_monitor_level = configuration_info["monitor level"], info_list = info_list, monitor_info_list = monitor_info_list, fp = fp, msg_token = configuration_info["monitor token"])
        #_ = printout("number of compute node:" + cls_info["number of compute node"], info_list = info_list, fp = fp,msg_token = msg_token)
    elif len(zone_list) >= 2 :
        number_of_compute_node = 0
        for i in zone_list:
            number_of_compute_node += int(configuration_info["the number of compute node in " + i])
        #number_of_compute_node = "number of compute node:" + str(number_of_compute_node)
        cls_info["number of compute node"] = str(number_of_compute_node)
        _ = printout_cluster("number of compute node:" + cls_info["number of compute node"], cls_monitor_level = 1, set_monitor_level = configuration_info["monitor level"], info_list = info_list, monitor_info_list = monitor_info_list, fp = fp, msg_token = configuration_info["monitor token"])
        #_ = printout("number of compute node:" + cls_info["number of compute node"], info_list = info_list, fp = fp,msg_token = msg_token)
    #compute_node_id_lists = ",".join(compute_node_id_list)
    #compute_node_id_lists = "compute ID list:" + compute_node_id_list
    #cls_info["compute ID list"] = compute_node_id_lists
    dt_now = datetime.datetime.now()
    dt_ymd = dt_now.strftime("%Y_%m_%d")
    cls_info["Date modified"] = dt_ymd
    _ = printout_cluster("Date modified:" + cls_info["Date modified"], cls_monitor_level = 1, set_monitor_level = configuration_info["monitor level"], info_list = info_list, monitor_info_list = monitor_info_list, fp = fp, msg_token = configuration_info["monitor token"])
    #_ = printout("Date modified:" + cls_info["Date modified"], info_list = info_list, fp = fp,msg_token = msg_token)
    #url_tag = sub_url[0] + "/" + head_id_list[0] + sub_url[5]
    url_des = sub_url[0] + "/" + head_id_list[0]
    #param = {"Server":{"Tags":[compute_node_id_lists]}}
    cls_info_str = json.dumps(cls_info)
    cls_info_list = [str(k) + " : " + str(v) for k,v in cls_info.items()]
    #cluster_id = cls_info_list[1]
    #date_modified = cls_info_list[-1]
    #param = {"Tags":cls_info_list}
    logger.debug("describe cluster information in head node")
    desc_param = {"Server":{"Description":cls_info_str}}
    #param = {"Tags":[cluster_id,date_modified]}
    if (api_index == True):
        while(True):
            #cluster_tags_res = put(url_list[-1]+url_tag,auth_res,param)
            cluster_info_res = put(url_list[-1]+url_des,auth_res,desc_param)
            check = res_check_put(configuration_info, cluster_info_res,fp = fp, info_list = info_list, monitor_info_list = monitor_info_list)
            if check == True:
                break
            else:
                build_error(configuration_info, fp = fp, info_list = info_list, monitor_info_list = monitor_info_list)
                '''
            if ("Success" in cluster_info_res.keys()):
                if cluster_info_res["Success"] == True:
                    break
                else:
                    _ = printout("Error:",fp = fp, info_list = info_list)
                    rf = response_output("Error_Description",cluster_info_res)
                    build_error(info_list = info_list,fp = fp)
            elif ("is_fatal" in cluster_info_res.keys()):
                _ = printout("Status:" + cluster_info_res["status"], info_list = info_list , fp = fp)
                _ = printout("Error:" + cluster_info_res["error_msg"],fp = fp, info_list = info_list)
                rf = response_output("Error_Description",cluster_info_res)
                build_error(info_list = info_list,fp = fp)'''
    else:
        #cluster_tags_res = "API is not used."
        cluster_info_res = "API is not used."
    
    
    #rf = response_output("cluster_tags",cluster_tags_res)
    #rf = response_output("cluster_info",cluster_info_res)
    return cluster_info_res