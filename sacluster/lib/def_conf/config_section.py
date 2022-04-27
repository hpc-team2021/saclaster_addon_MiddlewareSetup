
import os
os.chdir(os.path.dirname(os.path.abspath(__file__)))
path = os.path.abspath("../..")

import os
import sys
import json
from config_function import set_parm, conf_pattern_main, conf_pattern_1, conf_pattern_2, conf_pattern_3, conf_pattern_4, conf_pattern_5
sys.path.append(path + "/lib/others")
from API_method import get, post, put
from info_print import printout
import base64
import requests
import datetime
from load_external_data import external_data
import pandas as pd
import logging
logger = logging.getLogger("sacluster").getChild(os.path.basename(__file__))

#Config内容名を指定
def def_config_name(fp = "", info_list = [1,0,0,0]):
    logger.debug('Start to define config name')
    while(True):
        config_name = conf_pattern_1("Config name (Within 20 characters, default:config params)", info_list = info_list, fp = fp)
        if(config_name == ""):
            logger.debug('automatically config name is set to config prams')
            return "config params"
        elif(len(config_name) <= 20):
            logger.debug('config name is set')
            return config_name
        else:
            logger.debug('Character count over')
            printout("Warning: Please specify up to 20 characters.", info_type = 0, info_list = info_list, fp = fp)

def setting_server(ext_info, server_type, fp = "", info_list = [1,0,0,0]):
    #ノードにおけるCore数
    logger.debug('setting core number')
    param = {}
    param["Node"] = {}
    candidate = list(ext_info["Server"].keys())
    core_plan = int(conf_pattern_2("The number of core for " + str(server_type) + " node", candidate, candidate[0], info_list = info_list, fp = fp))
    set_parm("The number of cores for " + str(server_type) + " node", str(core_plan), info_list = info_list, fp = fp)
    param["Node"]["core"] = int(core_plan)
    
    #ノードにおけるメモリ容量
    logger.debug('setting memory size')
    candidate = [str(i) + " (" + str(int(round(int(i), -3)/1000)) + "GB)"  for i in list(ext_info["Server"][str(core_plan)].keys())]
    memory_plan = list(ext_info["Server"][str(core_plan)].keys())[conf_pattern_3("Size of memory for " + str(server_type) + " node", candidate, candidate[0], info_list = info_list, fp = fp)]
    set_parm("Size of memory for " + str(server_type) + " node", str(memory_plan), info_list = info_list, fp = fp)
    param["Node"]["memory"] = int(memory_plan)
    param["Node"]["NodePlan"] = ext_info["Server"][str(core_plan)][memory_plan]
    
    #ノードにおけるディスクの種類
    logger.debug('setting disk type')
    param["Disk"] = {}
    candidate = list(ext_info["Disk"].keys())
    param["Disk"]["Type"] = candidate[conf_pattern_3("Disk type for " + str(server_type) + " node", candidate, candidate[0], info_list = info_list, fp = fp)]
    set_parm("Disk type for " + str(server_type) + " node", param["Disk"]["Type"], info_list = info_list, fp = fp)
    
    #ノードにおけるディスクのサイズ
    logger.debug('setting disk size')
    candidate = [str(i) + " (" + str(int(round(int(i), -3)/1000)) + "GB)"  for i in ext_info["Disk"][param["Disk"]["Type"]]]
    param["Disk"]["Size"] = ext_info["Disk"][param["Disk"]["Type"]][conf_pattern_3("Disk size for " + str(server_type) + " node", candidate, candidate[0], info_list = info_list, fp = fp)]
    set_parm("Disk size for " + str(server_type) + " node", str(param["Disk"]["Size"]), info_list = info_list, fp = fp)

    #ノードにおけるサーバとディスク間接続方法
    logger.debug('setting connection type')
    candidate = ext_info["Connection"]
    param["Connection type"] = candidate[conf_pattern_3("Connection type between server and disk for " + str(server_type) + " node", candidate, candidate[0], info_list = info_list, fp = fp)]
    set_parm("Connection type between server and disk for " + str(server_type) + " node", param["Connection type"], info_list = info_list, fp = fp)
    
    #ノードのOS
    logger.debug('setting OS')
    param["OS"] = {}
    candidate = list(ext_info["OS"].keys())
    param["OS"]["name"] = candidate[conf_pattern_3("OS in " + str(server_type) + " node", candidate, candidate[0], info_list = info_list, fp = fp)]
    param["OS"]["OSPlan"] = ext_info["OS"][param["OS"]["name"]]
    set_parm("OS in " + str(server_type) + " node", param["OS"]["name"], info_list = info_list, fp = fp)
        
    return param

def setting_head(ext_info, all_params, set_list, fp = "", info_list = [1,0,0,0]):
    logger.debug('start setting of head node')
    param = setting_server(ext_info, "head", fp = fp, info_list = info_list)
    all_params["Head"] = param
    set_list.loc["Head"] = ["Head      ", "already", "required    "]
    
    return all_params, set_list

def setting_compute(ext_info, all_params, set_list, fp = "", info_list = [1,0,0,0]):
    logger.debug('start setting of compute node')
    param = {}
    #ノードの最大数と最小数を定義
    head_min = min([v["minimum"] for k,v in ext_info["Zone"].items()])
    head_max_list = [v["maximum"] for k,v in ext_info["Zone"].items() if v["Type"] == "practice"]
    head_max = sum(head_max_list)
    logger.debug('maximum and minimum number ')
    
    #コンピュートノード数の設定
    logger.debug('setting number of compute nodes')
    node_num = conf_pattern_4("The number of compute nodes", head_min, head_max - 1, head_min, info_list = info_list, fp = fp)
    
    #既にゾーンの設定がされている場合
    if("Zone" in all_params):
        logger.debug('zone has already been configured')
        #指定ゾーンが1つの場合
        if(len(all_params["Zone"]["Zone"]) == 1):
           logger.debug('single zone has been set up')
           current_zone = list(all_params["Zone"]["Zone"].keys())[0]
           #{(指定ゾーンのノード数が設定されていない) or (ゾーン指定時のコンピュートノード数が間違っている)} and (指定コンピュートノード数)>(1つのゾーンに設置できるコンピュートノード数)の場合
           if((all_params["Zone"]["Zone"][current_zone] == None or all_params["Zone"]["Zone"][current_zone] != node_num) and ext_info["Zone"][current_zone]["maximum"] - 1 < node_num):
               logger.info('The number of compute nodes does not match the zone info')
               if("NFS" in all_params):
                   printout("The number of compute nodes does not match the zone and nfs info (Please re-define the zone and nfs info)", info_type = 0, info_list = info_list, fp = fp)
                   set_list.loc["NFS"] = ["NFS       ", "auto   ", "not-required"]
                   all_params.pop("NFS")
                   logger.info('nfs setting was cleared')
               else:
                   printout("The number of compute nodes does not match the zone info (Please re-define the zone info)", info_type = 0, info_list = info_list, fp = fp)
               all_params.pop("Zone")
               set_list.loc["Zone"] = ["Zone      ", "yet    ", "required    "]
               logger.info('zone setting was cleared')
               
           #{(指定ゾーンのノード数が設定されていない) or (ゾーン指定時のコンピュートノード数が間違っている)} and (指定コンピュートノード数)<=(1つのゾーンに設置できるコンピュートノード数)の場合
           elif(all_params["Zone"]["Zone"][current_zone] != node_num and ext_info["Zone"][current_zone]["maximum"] - 1 >= node_num):
               logger.info("The number of compute node in " + current_zone + " was changed to " + str(node_num) + " from " + str(all_params["Zone"]["Zone"][current_zone]))
               printout("The number of compute node in " + current_zone + " was changed to " + str(node_num) + " from " + str(all_params["Zone"]["Zone"][current_zone]), info_type = 0, info_list = info_list, fp = fp)
               all_params["Zone"]["Zone"][current_zone] = node_num
               
           elif(all_params["Zone"]["Zone"][current_zone] == None and ext_info["Zone"][current_zone]["maximum"] - 1 >= node_num):
               logger.info("The number of compute node in " + current_zone + " was set to " + str(node_num))
               printout("The number of compute node in " + current_zone + " was set to " + str(node_num), info_type = 0, info_list = info_list, fp = fp)
               all_params["Zone"]["Zone"][current_zone] = node_num
               
           #上記のいずれでもない場合
           else:
               logger.debug('the number of nodes in the zone setting was automatically set')
               all_params["Zone"]["Zone"][current_zone] = node_num
           
        #指定ゾーンが複数の場合
        elif(len(all_params["Zone"]["Zone"]) > 1):
            logger.debug('multiple zones has been set up')
            current_node_sum = sum([i for i in list(all_params["Zone"]["Zone"].values())])
            #(ゾーン指定中に指定されていたコンピュートノード数の和)!=(指定したコンピュートノード数) 
            if(node_num != current_node_sum):
                logger.info('The number of compute nodes does not match the zone info')
                if("NFS" in all_params):
                    printout("the number of compute nodes does not match the zone and nfs info (Please re-define the zone and nfs info)", info_type = 0, info_list = info_list, fp = fp)
                    set_list.loc["NFS"] = ["NFS       ", "auto   ", "not-required"]
                    all_params.pop("NFS")
                    logger.info('nfs setting was cleared')
                else:
                    printout("the number of compute nodes does not match the zone info (Please re-define the zone info)", info_type = 0, info_list = info_list, fp = fp)
                all_params.pop("Zone")
                logger.info('zone setting was cleared')
                if(max(head_max_list) < node_num):
                    set_list.loc["Zone"] = ["Zone      ", "yet    ", "required    "]
                else:
                    set_list.loc["Zone"] = ["Zone      ", "auto   ", "not-required"]
                
    #ゾーンの設定がされていない場合
    else:
        logger.debug('zone has not been configured yet')
        if(max(head_max_list) - 1 < node_num):
            set_list.loc["Zone"] = ["Zone      ", "yet    ", "required    "]
            
    param["Compute number"] = node_num
    set_parm("The number of compute nodes", str(node_num), info_list = info_list, fp = fp)
    
    param["Compute node"] = setting_server(ext_info, "compute", fp = fp, info_list = info_list)
    all_params["Compute"] = param
    set_list.loc["Compute"] = ["Compute   ", "already", "required    "]
    
    if(param["Compute number"] > 1):
        candidate = ext_info["Compute switch"]
        param["Compute switch"] = ext_info["Compute switch"][conf_pattern_3("Compute switch", candidate, candidate[0], info_list = info_list, fp = fp)]
        set_parm("Compute switch", str(param["Compute switch"]), info_list = info_list, fp = fp)
        logger.debug('setting compute switch')
    else:
        param["Compute switch"] = False
        printout("Compute switch is automatically set to Flase", info_type = 0, info_list = info_list, fp = fp)
        logger.info('Compute switch is automatically set to Flase')
    
    return all_params, set_list

def setting_monitor(ext_info, all_params, set_list, fp = "", info_list = [1,0,0,0]):
    param = {}
    logger.debug('start setting of monitor')
    param["Monitor"] = [False, True][conf_pattern_3("Monitor", ["False","True"], "False", info_list = info_list, fp = fp)]
    set_parm("monitor", str(param["Monitor"]), info_list = info_list, fp = fp)

    if(param["Monitor"] == True):
        logger.debug('monitor has been enabled')
        
        logger.debug('setting monitor type')
        candidate = list(ext_info["Monitor"].keys())
        param["Monitor type"] = candidate[conf_pattern_3("Monitor type", candidate, candidate[0], info_list = info_list, fp = fp)]
        set_parm("monitor type", param["Monitor type"], info_list = info_list, fp = fp)
        
        logger.debug('setting monitor key')
        candidate = list(ext_info["Monitor"].values())
        param["Monitor key"] = conf_pattern_5(ext_info["Monitor"][param["Monitor type"]], info_list = info_list, fp = fp)
        set_parm(ext_info["Monitor"][param["Monitor type"]], param["Monitor key"], info_list = info_list, fp = fp)
        
        logger.debug('setting monitor level')
        candidate = ["level_" + str(ext_info["Monitor_level"]["level"][i]) + " (" + ext_info["Monitor_level"]["level_explanation"][i] + ")" for i in range(len(ext_info["Monitor_level"]["level"]))]
        param["Monitor level"] = ext_info["Monitor_level"]["level"][conf_pattern_3("Monitor level", candidate, candidate[0], info_list = info_list, fp = fp)]
        set_parm("monitor level", "level_" + str(param["Monitor level"]), info_list = info_list, fp = fp)

    all_params["Monitor"] = param
    set_list.loc["Monitor"] = ["Monitor   ", "already", "not-required"]

    return all_params, set_list

def setting_nfs(ext_info, all_params, set_list, fp = "", info_list = [1,0,0,0]):
    logger.debug('start setting of nfs')
    param = {}
    param["NFS"] = [False, True][conf_pattern_3("NFS", ["False","True"], "False", info_list = info_list, fp = fp)]
    set_parm("NFS", str(param["NFS"]), info_list = info_list, fp = fp)
    
    if(param["NFS"] == True):
        #もしゾーンの設定がなされていなければ、ゾーンの設定を優先させる。
        if("Zone" not in all_params):
            printout("Setting of zone are need to set before setting of nfs", info_type = 0, info_list = info_list, fp = fp)
            printout("Start setting of zone", info_type = 0, info_list = info_list, fp = fp)
            all_params, set_list = setting_zone(ext_info, all_params, set_list, fp = fp, info_list = info_list)
            
        if(all_params["Zone"]["Head Zone"] in ext_info["NFS zone"]):
            param["NFS zone"] = {}
            logger.debug("Start setting of nfs in " + str(all_params["Zone"]["Head Zone"]))
            printout("Start setting of nfs in " + str(all_params["Zone"]["Head Zone"]), info_type = 0, info_list = info_list, fp = fp)
            param["NFS zone"][all_params["Zone"]["Head Zone"]] = {}
        
            candidate = list(ext_info["NFS"].keys())
            param["NFS zone"][all_params["Zone"]["Head Zone"]]["NFS type"] = candidate[conf_pattern_3("NFS type", candidate, candidate[0], info_list = info_list, fp = fp)]
            set_parm("NFS type", param["NFS zone"][all_params["Zone"]["Head Zone"]]["NFS type"], info_list = info_list, fp = fp)
            logger.debug('setting nfs type')
        
            candidate_temp = list(ext_info["NFS"][param["NFS zone"][all_params["Zone"]["Head Zone"]]["NFS type"]].keys())
            candidate = [str(i) + " GB" for i in candidate_temp]
            num = conf_pattern_3("NFS size", candidate, candidate[0], info_list = info_list, fp = fp)
            param["NFS zone"][all_params["Zone"]["Head Zone"]]["NFS size"] = int(candidate_temp[num])
            set_parm("NFS size", candidate[num], info_list = info_list, fp = fp)
            logger.debug('setting nfs size')
        
            param["NFS zone"][all_params["Zone"]["Head Zone"]]["NFSPlan"] = ext_info["NFS"][param["NFS zone"][all_params["Zone"]["Head Zone"]]["NFS type"]][str(param["NFS zone"][all_params["Zone"]["Head Zone"]]["NFS size"])]
            
        else:
            printout("INFO: NFS can not be supported in " + str(all_params["Zone"]["Head Zone"]), info_type = 0, info_list = info_list, fp = fp)
            set_parm("NFS in " + str(all_params["Zone"]["Head Zone"]), "False", info_list = info_list, fp = fp)
            param["NFS"] = False
        
        """
        #複数ゾーン指定の場合
        if(len(all_params["Zone"]["Zone"]) > 1):
            logger.debug('multiple zones has been set up')
            zone = list(all_params["Zone"]["Zone"].keys())
            param["NFS zone"] = {}
            for i in range(len(zone)):
                if(zone[i] in ext_info["NFS zone"]):
                    ind = [False, True][conf_pattern_3("NFS in " + str(zone[i]), ["False","True"], "False", info_list = info_list, fp = fp)]
                    set_parm("NFS in " + str(zone[i]), str(ind), info_list = info_list, fp = fp)
                
                    if(ind == True):
                        logger.debug("Start setting of nfs in " + str(zone[i]))
                        printout("Start setting of nfs in " + str(zone[i]), info_type = 0, info_list = info_list, fp = fp)
                        param["NFS zone"][zone[i]] = {}
                    
                        candidate = list(ext_info["NFS"].keys())
                        param["NFS zone"][zone[i]]["NFS type"] = candidate[conf_pattern_3("NFS type", candidate, candidate[0], info_list = info_list, fp = fp)]
                        set_parm("NFS type", param["NFS zone"][zone[i]]["NFS type"], info_list = info_list, fp = fp)
                        logger.debug('setting nfs type')
                    
                        candidate_temp = list(ext_info["NFS"][param["NFS zone"][zone[i]]["NFS type"]].keys())
                        candidate = [str(i) + " GB" for i in candidate_temp]
                        num = conf_pattern_3("NFS size", candidate, candidate[0], info_list = info_list, fp = fp)
                        param["NFS zone"][zone[i]]["NFS size"] = int(candidate_temp[num])
                        set_parm("NFS size", candidate[num], info_list = info_list, fp = fp)
                        logger.debug('setting nfs size')
            
                        param["NFS zone"][zone[i]]["NFSPlan"] = ext_info["NFS"][param["NFS zone"][zone[i]]["NFS type"]][str(param["NFS zone"][zone[i]]["NFS size"])]
            
                else:
                    printout("INFO: NFS can not be supported in " + str(zone[i]), info_type = 0, info_list = info_list, fp = fp)
                    set_parm("NFS in " + str(zone[i]), "False", info_list = info_list, fp = fp)
            
            if(len(param["NFS zone"]) == 0):
                logger.info("The configuration has been changed to not install nfs")
                printout("The configuration has been changed to not install nfs", info_type = 0, info_list = info_list, fp = fp)
                param["NFS"] = False
                param.pop("NFS zone")
            
        else:
            logger.debug('single zones has been set up')
            zone = list(all_params["Zone"]["Zone"].keys())[0]
            if(zone in ext_info["NFS zone"]):
                param["NFS zone"] = {}
                logger.debug("Start setting of nfs in ")
                printout("Start setting of nfs", info_type = 0, info_list = info_list, fp = fp)
                
                param["NFS zone"][zone] = {}
                candidate = list(ext_info["NFS"].keys())
                param["NFS zone"][zone]["NFS type"] = candidate[conf_pattern_3("NFS type", candidate, candidate[0], info_list = info_list, fp = fp)]
                set_parm("NFS type", param["NFS zone"][zone]["NFS type"], info_list = info_list, fp = fp)
                logger.debug('setting nfs type')
        
                candidate_temp = list(ext_info["NFS"][param["NFS zone"][zone]["NFS type"]].keys())
                candidate = [str(i) + " GB" for i in candidate_temp]
                num = conf_pattern_3("NFS size", candidate, candidate[0], info_list = info_list, fp = fp)
                param["NFS zone"][zone]["NFS size"] = int(candidate_temp[num])
                set_parm("NFS size", candidate[num], info_list = info_list, fp = fp)
                logger.debug('setting nfs size')
                
                param["NFS zone"][zone]["NFSPlan"] = ext_info["NFS"][param["NFS zone"][zone]["NFS type"]][str(param["NFS zone"][zone]["NFS size"])]
        
            else:
                printout("INFO: NFS can not be supported in " + str(zone), info_type = 0, info_list = info_list, fp = fp)
                logger.info("nfs can not be supported in " + str(zone))
                param["NFS"] = False
                set_parm("NFS", "False", info_list = info_list, fp = fp)
        """
    
    all_params["NFS"] = param
    set_list.loc["NFS"] = ["NFS       ", "already", "not-required"]
        
    return all_params, set_list
        
def setting_zone(ext_info, all_params, set_list, fp = "", info_list = [1,0,0,0]):
    logger.debug('start setting of zone')
    param = {}
    if("Compute" in all_params):
        logger.debug('Compute nodes are configured')
        #1つのゾーンに設置できるコンピュートノードの数を超えている場合
        if(all_params["Compute"]["Compute number"] > (max([v["maximum"] for k,v in ext_info["Zone"].items()]) - 1)):
            logger.debug('multiple zones are used')
            zone_list = []
            node_sum = 0
            count = 1
            candidate = [k for k,v in ext_info["Zone"].items() if(v["Type"] == "practice")]
            
            #指定されたコンピュートノード数が全てのゾーンのmaximumの合計値である場合
            if(sum([v["maximum"] for k,v in ext_info["Zone"].items() if(v["Type"] == "practice")]) - 1 == all_params["Compute"]["Compute number"]):
                logger.debug('The maximum number of nodes that can be installed has been set')
                zone_list = candidate
                printout("All zones are used", info_type = 0, info_list = info_list, fp = fp)
                printout("", info_type = 0, info_list = info_list, fp = fp)
            
            #指定されたコンピュートノード数が全てのゾーンのmaximumの合計値より少ない場合
            else:
                #(コンピュートノード数<=各ゾーンのmaximumの和)となるようまでゾーンをユーザーに定義させる
                logger.debug('Selecting zones')
                while(True):
                    zone_param = candidate[conf_pattern_3("Zone_" + str(count), candidate, candidate[0], info_list = info_list, fp = fp)]
                    zone_list.append(zone_param)
                    set_parm("Zone_" + str(count), zone_param, info_list = info_list, fp = fp)
        
                    node_sum += ext_info["Zone"][zone_param]["maximum"]
                    if(node_sum-1 >= all_params["Compute"]["Compute number"]):
                        logger.debug('sufficient number of zones have been set up for the installation of compute nodes')
                        break
                    else:
                        logger.debug('sufficient number of zones have not been set up for the installation of compute nodes')
                        candidate.remove(zone_param)
                    count += 1
                
            #ヘッドノードのゾーンの設定
            logger.debug('Selecting head zones')
            node_num_list = []
            param["Zone"] = {}
            param["Head Zone"] = zone_list[conf_pattern_3("Zone in head node", zone_list, zone_list[0], info_list = info_list, fp = fp)]
            set_parm("Zone in head node", param["Head Zone"], info_list = info_list, fp = fp)  
            
            logger.debug('Setting the number of nodes in each zone')
            #それぞれのゾーンのコンピュートノード数の設定(一番最後に登録されているゾーン以外)
            node_all = all_params["Compute"]["Compute number"]
            for i in range(len(zone_list) - 1):
                #指定可能な最小値を算出
                min_val = node_all - sum([ext_info["Zone"][zone_list[j]]["maximum"] - 1 if zone_list[j] == param["Head Zone"] else ext_info["Zone"][zone_list[j]]["maximum"] for j in range(i+1,len(zone_list))])
                if(min_val < 1):
                    min_val = 1
                
                #ヘッドノードがあるゾーンのコンピュートノード数の設定
                if(zone_list[i] == param["Head Zone"]):
                    logger.debug('Setting the number of nodes in head zone')
                    #(指定可能最小値!=指定可能最大値)の場合
                    if(min_val != ext_info["Zone"][zone_list[i]]["maximum"] - 1):
                        node_num = conf_pattern_4("The number of compute nodes in " + str(zone_list[i]), min_val, ext_info["Zone"][zone_list[i]]["maximum"] - 1, min_val, info_list = info_list, fp = fp)
                        param["Zone"][zone_list[i]] = node_num
                        set_parm("The number of compute nodes in " + str(zone_list[i]), str(node_num), info_list = info_list, fp = fp)
                    #(指定可能最小値==指定可能最大値)の場合
                    else:
                        node_num = min_val
                        param["Zone"][zone_list[i]] = min_val
                        set_parm("The number of compute nodes in " + str(zone_list[i]), str(node_num), info_list = info_list, fp = fp)
                
                #ヘッドノードがないゾーンのコンピュートノード数の設定
                else:
                    logger.debug('Setting the number of nodes in peripheral zone')
                    #(指定可能最小値!=指定可能最大値)の場合
                    if(min_val != ext_info["Zone"][zone_list[i]]["maximum"]):
                        node_num = conf_pattern_4("The number of compute nodes in " + str(zone_list[i]), min_val, ext_info["Zone"][zone_list[i]]["maximum"], min_val, info_list = info_list, fp = fp)
                        param["Zone"][zone_list[i]] = node_num
                        set_parm("The number of compute nodes in " + str(zone_list[i]), str(node_num), info_list = info_list, fp = fp)
                    #(指定可能最小値==指定可能最大値)の場合
                    else:
                        node_num = min_val
                        param["Zone"][zone_list[i]] = min_val
                        set_parm("The number of compute nodes in " + str(zone_list[i]), str(node_num), info_list = info_list, fp = fp)
                
                node_num_list.append(node_num)
                node_all = node_all - node_num
            
            #最後に設定されているゾーンを自動的に決定
            logger.debug('Automatic allocation of the number of compute nodes')
            node_num = all_params["Compute"]["Compute number"] - sum(node_num_list)
            param["Zone"][zone_list[-1]] = node_num
            set_parm("The number of compute nodes in " + str(zone_list[-1]), str(node_num), info_list = info_list, fp = fp)
            set_list.loc["Zone"] = ["Zone      ", "already", "required    "]
        
        #コンピュートノード数が単一ノードに設置できる場合
        else:
            logger.debug('single zones are used')
            candidate = [k for k,v in ext_info["Zone"].items() if(v["maximum"] > all_params["Compute"]["Compute number"])]
            zone_param = candidate[conf_pattern_3("Zone", candidate, candidate[0], info_list = info_list, fp = fp)]
            param["Zone"] = {}
            param["Zone"][zone_param] = all_params["Compute"]["Compute number"]
            param["Head Zone"] = zone_param
            set_parm("Zone", zone_param, info_list = info_list, fp = fp)
            set_list.loc["Zone"] = ["Zone      ", "already", "not-required"]
    
    #コンピュートノード数が設定されていない場合
    else:
        logger.debug('Compute nodes are not configured')
        candidate = [k for k,v in ext_info["Zone"].items()]
        zone_param = candidate[conf_pattern_3("Zone", candidate, candidate[0], info_list = info_list, fp = fp)]
        param["Zone"] = {}
        param["Zone"][zone_param] = None
        param["Head Zone"] = zone_param
        set_parm("Zone", zone_param, info_list = info_list, fp = fp)
        set_list.loc["Zone"] = ["Zone      ", "already", "not-required"]
        
    #指定ゾーンにnfs設定ゾーンが含まれていない場合は、nfsの設定を初期化
    all_params["Zone"] = param
    if("NFS" in all_params):
        if(all_params["NFS"]["NFS"] == True):
            nfs_zone_all = list(all_params["NFS"]["NFS zone"].keys())
            for i in range(len(nfs_zone_all)):
                if(nfs_zone_all[i] not in all_params["Zone"]["Zone"].keys()):
                    printout("nfs info does not match the zone info (Please re-define nfs info)", info_type = 0, info_list = info_list, fp = fp)
                    set_list.loc["NFS"] = ["NFS       ", "auto   ", "not-required"]
                    all_params.pop("NFS")
                    break
                
    return all_params, set_list
                
def show_current_state(ext_info, all_params, set_list, fp = "", info_list = [1,0,0,0]):
    logger.debug('show current config setting')
    printout("", info_type = 0, info_list = info_list, fp = fp)
    printout("Current parameters========================", info_type = 0, info_list = info_list, fp = fp)
    printout("[[Compute]]", info_type = 0, info_list = info_list, fp = fp)
    if("Compute" in all_params):
        printout("[NUMBER]", info_type = 0, info_list = info_list, fp = fp)
        printout("Number of total compute nodes    : " + str(all_params["Compute"]["Compute number"]), info_type = 0, info_list = info_list, fp = fp)
        printout("[CPU]", info_type = 0, info_list = info_list, fp = fp)
        printout("Core                             : " + str(all_params["Compute"]["Compute node"]["Node"]["core"]), info_type = 0, info_list = info_list, fp = fp)
        printout("Memory                           : " + str(int(round(int(all_params["Compute"]["Compute node"]["Node"]["memory"]), -3)/1000)) + "GB", info_type = 0, info_list = info_list, fp = fp)
        printout("[OS]", info_type = 0, info_list = info_list, fp = fp)
        printout("OS                               : " + str(all_params["Compute"]["Compute node"]["OS"]["name"]), info_type = 0, info_list = info_list, fp = fp)
        printout("[DISK]", info_type = 0, info_list = info_list, fp = fp)
        printout("Type                             : " + str(all_params["Compute"]["Compute node"]["Disk"]["Type"]), info_type = 0, info_list = info_list, fp = fp)
        printout("Size                             : " + str(int(round(int(all_params["Compute"]["Compute node"]["Disk"]["Size"]), -3)/1000)) + "GB", info_type = 0, info_list = info_list, fp = fp)
        printout("Connection                       : " + str(all_params["Compute"]["Compute node"]["Connection type"]), info_type = 0, info_list = info_list, fp = fp)
        printout("[SWITCH]", info_type = 0, info_list = info_list, fp = fp)
        printout("Switch                           : " + str(all_params["Compute"]["Compute switch"]), info_type = 0, info_list = info_list, fp = fp)
        
    else:
        printout("Not set up", info_type = 0, info_list = info_list, fp = fp)
    
    printout("", info_type = 0, info_list = info_list, fp = fp)
    printout("[[Head]]", info_type = 0, info_list = info_list, fp = fp)
    if("Head" in all_params):
        printout("[CPU]", info_type = 0, info_list = info_list, fp = fp)
        printout("Core                             : " + str(all_params["Head"]["Node"]["core"]), info_type = 0, info_list = info_list, fp = fp)
        printout("Memory                           : " + str(int(round(int(all_params["Head"]["Node"]["memory"]), -3)/1000)) + "GB", info_type = 0, info_list = info_list, fp = fp)
        printout("[OS]", info_type = 0, info_list = info_list, fp = fp)
        printout("OS                               : " + str(all_params["Head"]["OS"]["name"]), info_type = 0, info_list = info_list, fp = fp)
        printout("[DISK]", info_type = 0, info_list = info_list, fp = fp)
        printout("Type                             : " + str(all_params["Head"]["Disk"]["Type"]), info_type = 0, info_list = info_list, fp = fp)
        printout("Size                             : " + str(int(round(int(all_params["Head"]["Disk"]["Size"]), -3)/1000)) + "GB", info_type = 0, info_list = info_list, fp = fp)
        printout("Connection                       : " + str(all_params["Head"]["Connection type"]), info_type = 0, info_list = info_list, fp = fp)
        
    else:
        printout("Not set up", info_type = 0, info_list = info_list, fp = fp)
        
    printout("", info_type = 0, info_list = info_list, fp = fp)
    printout("[[NFS]]", info_type = 0, info_list = info_list, fp = fp)
    if("NFS" in all_params):
        printout("NFS                              : " + str(all_params["NFS"]["NFS"]), info_type = 0, info_list = info_list, fp = fp)
        if(all_params["NFS"]["NFS"] == True):
            for k,v in all_params["NFS"]["NFS zone"].items():
                printout("[" + str(k) + "]", info_type = 0, info_list = info_list, fp = fp)
                printout("Type                             : " + str(all_params["NFS"]["NFS zone"][k]["NFS type"]), info_type = 0, info_list = info_list, fp = fp)
                printout("Size                             : " + str(all_params["NFS"]["NFS zone"][k]["NFS size"]) + "GB", info_type = 0, info_list = info_list, fp = fp)
    else:
        printout("NFS                              : " + "False", info_type = 0, info_list = info_list, fp = fp)
        
    printout("", info_type = 0, info_list = info_list, fp = fp)
    printout("[[Zone]]", info_type = 0, info_list = info_list, fp = fp)
    if("Zone" in all_params):
        printout("Head zone                        : " + str(all_params["Zone"]["Head Zone"]), info_type = 0, info_list = info_list, fp = fp)
        for k,v in all_params["Zone"]["Zone"].items():
            printout("[" + str(k) + "]", info_type = 0, info_list = info_list, fp = fp)
            printout("Number of total compute nodes    : " + str(v), info_type = 0, info_list = info_list, fp = fp)
    else:
        printout("Zone                             : " + str(ext_info["max_zone"]), info_type = 0, info_list = info_list, fp = fp)
        #printout("Not set up", info_type = 0, info_list = info_list, fp = fp)
        
    printout("", info_type = 0, info_list = info_list, fp = fp)
    printout("[[Monitor]]", info_type = 0, info_list = info_list, fp = fp)
    if("Monitor" in all_params):
        printout("Monitor                          : " + str(all_params["Monitor"]["Monitor"]), info_type = 0, info_list = info_list, fp = fp)
        if(all_params["Monitor"]["Monitor"] == True):
            printout("Monitor type                     : " + str(all_params["Monitor"]["Monitor type"]), info_type = 0, info_list = info_list, fp = fp)
            if(len(all_params["Monitor"]["Monitor key"]) > 5):
                printout("Monitor key                      : " + str(all_params["Monitor"]["Monitor key"][:5]) + "".join(["*" for i in range(len(all_params["Monitor"]["Monitor key"]) - 5)]) , info_type = 0, info_list = info_list, fp = fp)
            else:
                printout("Monitor key                      : " + "".join(["*" for i in range(len(all_params["Monitor"]["Monitor key"]))]) , info_type = 0, info_list = info_list, fp = fp)
            printout("Monitor level                    : " + str(all_params["Monitor"]["Monitor level"]), info_type = 0, info_list = info_list, fp = fp)
        
    else:
        printout("Monitor                          : " + "False", info_type = 0, info_list = info_list, fp = fp)
        
    printout("", info_type = 0, info_list = info_list, fp = fp)
    return all_params, set_list
    











































































