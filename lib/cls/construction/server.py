import sys
import json
import os
import base64
import requests
import pandas as pd
import random
import datetime
import logging

logger = logging.getLogger("sacluster").getChild(os.path.basename(__file__))

from disk import add_disk, connect_server_disk
from res_out import response_output
from build_error import build_error, res_check_post, res_check_get

path = "../../.."
os.chdir(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(path + "/lib/others")
from API_method import get, post, put
from info_print import printout, printout_cluster


def build_server(url,sub_url,node_name,cluster_id,auth_res,configuration_info,switch_id = 0,fp = "", info_list = [1,0,0,0], monitor_info_list = [1,0,0,0],api_index = True):
    #_ = printout("constructing " + node_name + "node" ,info_list = info_list, monitor_info_list = monitor_info_list, fp = fp)
    _ = printout_cluster("constructing " + node_name, cls_monitor_level = 2, set_monitor_level = configuration_info["monitor level"], info_list = info_list, monitor_info_list = monitor_info_list, fp = fp, msg_token = configuration_info["monitor token"])
    logger.debug("constructing " + node_name)
    dt_now = datetime.datetime.now()
    dt_ymd = dt_now.strftime("%Y_%m_%d")
    date_modified = "Date modified:" + str(dt_ymd)
    
    if "head" in node_name:
        #node_planid = Serverplan(configuration_info["the number of core for head node"],configuration_info["size of memory for head node"])
        node_planid = configuration_info["server plan ID for head node"]
        param = {"Server":{"Name":node_name,"ServerPlan":{"ID":node_planid},"Tags":[cluster_id,date_modified],"ConnectedSwitches":[{"Scope":"shared"}],"InterfaceDriver":configuration_info["connection type for head node"]},"Count":0}
        #param = {"Server":{"Name":node_name,"ServerPlan":{"ID":"123456"},"ConnectedSwitches":[{"Scope":"shared"}]},"Count":0}
    elif "compute" in node_name:
        node_planid = configuration_info["server plan ID for compute node"]
        param = {"Server":{"Name":node_name,"ServerPlan":{"ID":node_planid},"Tags":[cluster_id,date_modified],"ConnectedSwitches":[{"ID":switch_id}],"InterfaceDriver":configuration_info["connection type for compute node"]},"Count":0}
    if (api_index == True):
        while(True):
            logger.debug("build server")
            server_response = post(url+sub_url[0],auth_res,param)
            check = res_check_post(configuration_info,server_response,info_list = info_list,fp = fp, monitor_info_list = monitor_info_list)

            if check == True:
                node_id = server_response["Server"]["ID"]
                logger.info(node_name + " ID: " + node_id + "-Success")
                break
            else:
                build_error(configuration_info, info_list = info_list,fp = fp, monitor_info_list = monitor_info_list)
            '''
            if ("is_ok" in server_response.keys()):
                if server_response["is_ok"] == True:
                    node_id = server_response["Server"]["ID"]
                    break
                else:
                    _ = printout("Error:", info_list = info_list,fp = fp)
                    rf = response_output("Error_build_" + node_name ,server_response)
                    build_error(info_list = info_list,fp = fp)

            elif ("is_fatal" in server_response.keys()):
                _ = printout("Status:" + server_response["status"], info_list = info_list , fp = fp)
                _ = printout("Error:" + server_response["error_msg"], info_list = info_list,fp = fp)
                rf = response_output("Error_build_" + node_name ,server_response)
                build_error(info_list = info_list,fp = fp)
                '''
    else:
        server_response = "API is not used."
        node_id = "000"
    logger.debug("constructed " + node_name)
    #rf = response_output("build_" + node_name ,server_response)

    return server_response,node_id


def cluster_id_def(configuration_info, url,sub_url,auth_res,fp = "", info_list = [1,0,0,0], monitor_info_list = [1,0,0,0],api_index = True):
    #APIを使用する場合
    if (api_index == True):
        while (True):
            #クラウド上の全てのクラスタIDの取得
            logger.debug("loading all cluster IDs")
            get_cluster_id_info = get(url+sub_url[0], auth_res)
            check = res_check_get(configuration_info, get_cluster_id_info,info_list = info_list, fp = fp, monitor_info_list = monitor_info_list)

            if check == True:
                logger.debug("assign cluster ID")
                cluster_id_info = get_cluster_id_info["Servers"]
                cluster_id_list = [d.get('Tags') for d in cluster_id_info]
                while (True):
                    cluster_id = random.randint(100000,999999)
                    if not cluster_id in cluster_id_list:
                        cluster_id_list.append(cluster_id)
                        logger.info("cluster ID: " + cluster_id + "-Success")
                        break
                    else:
                        logger.warning("Duplication of cluster ID")
                        _ = printout_cluster("Duplication of cluster ID", cls_monitor_level = 3, set_monitor_level = configuration_info["monitor level"], info_list = info_list, monitor_info_list = monitor_info_list, fp = fp, msg_token = configuration_info["monitor token"])
                        _ = printout_cluster("Reissuing cluster ID", cls_monitor_level = 3, set_monitor_level = configuration_info["monitor level"], info_list = info_list, monitor_info_list = monitor_info_list, fp = fp, msg_token = configuration_info["monitor token"])
                        #_ = printout("Duplication of cluster ID.", info_list = info_list, fp = fp,msg_token = msg_token)
                        #_ = printout("Reissuing cluster ID.", info_list = info_list, fp = fp,msg_token = msg_token)
                break
            else:
                build_error(configuration_info, info_list = info_list,fp = fp, monitor_info_list = monitor_info_list)
        '''
            if ("is_ok" in get_cluster_id_info.keys()):
                if get_cluster_id_info["is_ok"] == True:
                    cluster_id_info = get_cluster_id_info["Servers"]
                    cluster_id_list = [d.get('Tags') for d in cluster_id_info]
                    while (True):
                        cluster_id = random.randint(100000,999999)
                        if not cluster_id in cluster_id_list:
                            cluster_id_list.append(cluster_id)
                            break
                        else:
                            _ = printout("Duplication of cluster ID.", info_list = info_list, fp = fp)
                            _ = printout("Reissuing cluster ID.", info_list = info_list, fp = fp)
                    break
                else:
                    _ = printout("Error:",fp = fp, info_list = info_list)
                    rf = response_output("Error_get_cluster_id_info",get_cluster_id_info)
                    build_error(info_list = info_list,fp = fp)
            elif ("is_fatal" in get_cluster_id_info.keys()):
                _ = printout("Status:" + get_cluster_id_info["status"], info_list = info_list , fp = fp)
                _ = printout("Error:" + get_cluster_id_info["error_msg"],fp = fp, info_list = info_list)
                rf = response_output("Error_get_cluster_id_info",get_cluster_id_info)
                build_error(info_list = info_list,fp = fp)
                '''
    else:
        get_cluster_id_info = "API is not used."
        cluster_id = random.randint(100000,999999)
    
    #rf = response_output("get_cluster_id_info",get_cluster_id_info)
    return cluster_id

def build_compute_node(url,sub_url,switch_id,zone,cluster_id,auth_res,configuration_info,fp = "", info_list = [1,0,0,0],monitor_info_list = [1,0,0,0] ,api_index = True):
    logger.debug("start building compute nodes in " + zone)
    i = 0
    l_compute_node_id = []
    n = configuration_info["the number of compute node in " + zone]
    #core = configuration_info["the number of core for compute node"]
    #memory = configuration_info["size of memory for compute node"]
    #interfacedriver = configuration_info["connection type for compute node"]
    for i in range(n):
        i += 1
        if i < 10:
            compute_node_name = "compute_node_00"+str(i)
        elif i >= 10:
            compute_node_name = "compute_node_0"+str(i)
        
        compute_server_response,compute_node_id = build_server(url,sub_url,compute_node_name,cluster_id,auth_res,configuration_info,switch_id = switch_id ,fp = fp, info_list  = info_list, monitor_info_list = monitor_info_list,api_index = api_index)
        '''
        #setting private IPAddress
        l_id = interface_info(url,sub_url,compute_node_id,fp = fp, info_list  = info_list, api_index = api_index)
        for j in l_id:
            set_ip_res = setting_ip(url,sub_url,j,fp = fp, info_list  = info_list, api_index = api_index)
        '''
        #add disk in compute node
        #disk_type = configuration_info["disk type for compute node"]
        #disk_size = configuration_info["disk size for compute node"]
        #os_type = configuration_info["OS ID for compute node"][zone]
        logger.debug("add disk for compute node in " + zone)
        compute_disk_res , compute_disk_id = add_disk(url,sub_url,zone,compute_node_name,cluster_id,auth_res = auth_res,configuration_info = configuration_info,fp = fp, info_list  = info_list, monitor_info_list = monitor_info_list,api_index = api_index)
        #compute_disk_id = compute_disk["Disk"]["ID"]
        compute_server_disk_res = connect_server_disk(url,compute_disk_id,compute_node_id,configuration_info = configuration_info, auth_res = auth_res,fp = fp, info_list  = info_list, monitor_info_list = monitor_info_list, api_index = api_index)

        #add iso image computenode
        #iso_imege_res = iso_image_insert(url,compute_node_name,compute_node_id,zone,fp = fp, info_list  = info_list, api_index = api_index)
        l_compute_node_id.append(compute_node_id)
    return compute_server_response,l_compute_node_id

"""
def Serverplan(core, memory):
    #csvファイルがある時ない時
    serverplan_df = pd.read_csv(path + '/../../temp/serverplan_2.csv')
    serverplan = serverplan_df[(serverplan_df["Core"] == core) & (serverplan_df["Memory"] == memory)]
    if serverplan.empty:
        _ = printout("Error:ServerPlan does not exist. There is an error in core or memory.",info_list = [1,0,0,0], fp = '')
        sys.exit()
    else:
        serverplan_id = int(serverplan.iat[0,0])

    return serverplan_id
"""
