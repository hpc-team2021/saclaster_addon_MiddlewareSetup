

import sys
import json
import os
import random
import datetime
import ipaddress
import logging
import ast
import copy
from pprint import pprint
import numpy as np
import pandas as pd
import time
pd.set_option('display.max_rows', 1000)
pd.get_option("display.max_columns", 1000)

logger = logging.getLogger("sacluster").getChild(os.path.basename(__file__))

path = "../../.."
os.chdir(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(path + "/lib/others")

from API_method import get, post, put, delete
from info_print import printout

class get_params:
    def __init__(self, ext_info, auth_res , info_list = [1,0,0,0], f = "", api_index = True):
        self.auth_res   = auth_res
        self.info_list  = info_list
        self.api_index  = api_index
        self.ext_info   = ext_info
        self.f          = f
        
        #set url
        self.url_list = {}
        for zone in list(self.ext_info["Zone"].keys()):
            self.url_list[zone] = "https://secure.sakura.ad.jp/cloud/zone/"+ zone +"/api/cloud/1.1"
        
        self.sub_url = ["/server", "/switch", "/appliance", "/disk"]
        self.delete_ids = []
        
    def __call__(self):
        self.cluster_info_all = {}
        if(self.api_index == True):
            printout('Getting cluster information ...', info_type = 0, info_list = self.info_list, fp = self.f)
            self.get_head_info()
        else:
            self.generate_sample_params()
            
    def get_head_info(self):
        #self.temp_list = []
        #self.temp = []
        #self.cluster_info_all = {}
        #ノードの情報を取得
        node_dict = self.get_node_info()
        disk_dict = self.get_disk_info()
        self.temp = disk_dict
        #NFSの情報を取得
        nfs_dict = self.get_nfs_info()
        for zone, url in self.url_list.items():
            node_list = node_dict[zone]
            if(len(node_list) != 0):
                for i in range(len(node_list)):
                    desp = node_list[i]["Description"]
                    #インターフェース数:2、Tagにcluster IDとData modifiedを含む
                    if(len(node_list[i]["Interfaces"]) == 2):
                        if(node_list[i]["Interfaces"][0]["IPAddress"] != None or node_list[i]["Interfaces"][0]["IPAddress"] != None):
                            try:
                                info = ast.literal_eval(node_list[i]["Description"])
                            except:
                                info = ""
                                logger.info('Description of the server is not dict type')
                            if(isinstance(info, dict) == True):    
                                if("Date modified" in info and "cluster ID" in info and "config name" in info and "head node ID" in info and "number of compute node" in info):
                                    cluster_id = self.get_cluster_id(info)
                                    if(len(cluster_id) == 6):
                                        #辞書型オブジェクトを生成
                                        self.initialize_params(cluster_id)
                                        #baseparams.config_nameとbaseparams.modified_dateを設定
                                        self.set_base_params(cluster_id, info)
                                        #baseparams.global_ipaddressとclusterparams.switch.{ヘッドノードのゾーン}.front.idを設定
                                        self.set_switch_info(node_list[i], cluster_id, zone)
                                        #clusterparams.server.{ヘッドノードのゾーン}.head.node.id、clusterparams.server.{ヘッドノードのゾーン}.head.node.state、clusterparams.server.{ヘッドノードのゾーン}.head.disk.{number}.idを設定
                                        self.set_head_node_info(node_list[i], cluster_id, zone, disk_dict)
                                        #ヘッドノードのゾーンにおけるfrontエリアのswitchの情報を取得
                                        head_switch_info = self.get_switch_info(zone, str(self.cluster_info_all[cluster_id]["clusterparams"]["switch"][zone]["front"]["id"]))
                                        #ヘッドノードのゾーン以外のゾーンのブリッジに連結したswitchの情報を取得(clusterparams.switch.{ヘッドノードのゾーン以外のゾーン}.front.idを設定)
                                        self.get_bridge_info(head_switch_info, cluster_id)
                                        #compute nodeの情報を設定し、compute nodeとhead nodeの状態からクラスターの状態を決定
                                        self.set_compute_node_info(cluster_id, node_dict, zone, disk_dict)
                                        #switchに連結したNFSの情報を設定
                                        self.set_nfs_info(cluster_id, nfs_dict)
            else:
                pass
                #print("Count zero")
                
        # self.check_parameters()
            
            
    def get_node_info(self):
        node_dict = {}
        try:
            for zone in list(self.ext_info["Zone"].keys()):
                logger.debug('Getting server information in ' + str(zone))
                node_list = get(self.url_list[zone] + self.sub_url[0], self.auth_res)
                if(node_list["is_ok"] == True):
                    node_dict[zone] = node_list["Servers"]
                else:
                    printout('APIResponseError: Information about servers was not obtained', info_type = 0, info_list = self.info_list, fp = self.f)
                    logger.error('APIResponseError: Information about servers was not obtained')
                    sys.exit()
        except:
            printout('ConnectionError: API request could not be sent', info_type = 0, info_list = self.info_list, fp = self.f)
            logger.error('ConnectionError: API request could not be sent')
            sys.exit()
                
        return node_dict
    
    def get_disk_info(self):
        disk_dict = {}
        try:
            for zone in list(self.ext_info["Zone"].keys()):
                disk_dict[zone] = {}
                logger.debug('Getting disk information in ' + str(zone))
                disk_list = get(self.url_list[zone] + self.sub_url[3], self.auth_res)
                if(disk_list["is_ok"] == True):
                    for i in range(len(disk_list["Disks"])):
                        disk_dict[zone][int(disk_list["Disks"][i]["ID"])] = disk_list["Disks"][i]
                else:
                    printout('APIResponseError: Information about disks was not obtained', info_type = 0, info_list = self.info_list, fp = self.f)
                    logger.error('APIResponseError: Information about disks was not obtained')
                    sys.exit()
            
        except:
            printout('ConnectionError: API request could not be sent', info_type = 0, info_list = self.info_list, fp = self.f)
            logger.error('ConnectionError: API request could not be sent')
            sys.exit()
            
        return disk_dict
                
    
    def get_nfs_info(self):
        nfs_dict = {}
        try:
            for zone in list(self.ext_info["Zone"].keys()):
                logger.debug('Getting NFS information in ' + str(zone))
                nfs_list = get(self.url_list[zone] + self.sub_url[2], self.auth_res)
                if(nfs_list["is_ok"] == True):
                    nfs_dict[zone] = nfs_list["Appliances"]
                else:
                    printout('APIResponseError: Information about NFSs was not obtained', info_type = 0, info_list = self.info_list, fp = self.f)
                    logger.error('APIResponseError: Information about NFSs was not obtained')
                    sys.exit()
        except:
            printout('ConnectionError: API request could not be sent', info_type = 0, info_list = self.info_list, fp = self.f)
            logger.error('ConnectionError: API request could not be sent')
            sys.exit()
                
        return nfs_dict
             
    def get_switch_info(self, zone, switch_id):
        try:
            logger.debug('Getting switch information in ' + str(zone))
            switch_list = get(self.url_list[zone] + self.sub_url[1] + "/" + str(switch_id), self.auth_res)
            if(switch_list["is_ok"] == True):
                return switch_list["Switch"]
            else:
                printout('APIResponseError: Information about switches was not obtained', info_type = 0, info_list = self.info_list, fp = self.f)
                logger.error('APIResponseError: Information about switches was not obtained')
                sys.exit()
        except:
            printout('ConnectionError: API request could not be sent', info_type = 0, info_list = self.info_list, fp = self.f)
            logger.error('ConnectionError: API request could not be sent')
            sys.exit()
                
            
    def get_cluster_id(self, info):
        logger.debug('Getting cluster id')
        return info["cluster ID"].split(":")[1].replace(" ", "")
    
    def initialize_params(self, cluster_id):
        logger.debug('Initializing a dict object (' + cluster_id + ")")
        self.cluster_info_all[cluster_id]                               = {}
        self.cluster_info_all[cluster_id]["baseparams"]                 = {}
        self.cluster_info_all[cluster_id]["clusterparams"]              = {}
        self.cluster_info_all[cluster_id]["clusterparams"]["server"]    = {}
        self.cluster_info_all[cluster_id]["clusterparams"]["switch"]    = {}
        self.cluster_info_all[cluster_id]["clusterparams"]["bridge"]    = {}
        self.cluster_info_all[cluster_id]["clusterparams"]["nfs"]       = {}
    
    def set_base_params(self, cluster_id, info):
        logger.debug("Setting baseparams.config_name (" + cluster_id + ")")
        self.cluster_info_all[cluster_id]["baseparams"]["config_name"] = info["config name"]
        logger.debug("Setting baseparams.modified_date (" + cluster_id + ")")
        self.cluster_info_all[cluster_id]["baseparams"]["modified_date"] = info["Date modified"]
        #self.cluster_info_all[cluster_id]["baseparams"]["number_of_compute_node"] = int(info["number of compute node"])
        
    def set_switch_info(self, node_info, cluster_id, zone):
        self.cluster_info_all[cluster_id]["clusterparams"]["switch"][zone]          = {}
        self.cluster_info_all[cluster_id]["clusterparams"]["switch"][zone]["front"] = {}
        
        if(node_info["Interfaces"][0]["IPAddress"] != None):
            logger.debug("Setting baseparams.global_ipaddress (" + cluster_id + ")")
            self.cluster_info_all[cluster_id]["baseparams"]["global_ipaddress"] = node_info["Interfaces"][0]["IPAddress"]
            logger.debug("Setting clusterparams.switch.{zone}.front.id (" + cluster_id + ")")
            self.cluster_info_all[cluster_id]["clusterparams"]["switch"][zone]["front"]["id"] = int(node_info["Interfaces"][1]["Switch"]["ID"])
        else:
            logger.debug("Setting baseparams.global_ipaddress (" + cluster_id + ")")
            self.cluster_info_all[cluster_id]["baseparams"]["global_ipaddress"] = node_info["Interfaces"][1]["IPAddress"]
            logger.debug("Setting clusterparams.switch.{zone}.front.id (" + cluster_id + ")")
            self.cluster_info_all[cluster_id]["clusterparams"]["switch"][zone]["front"]["id"] = int(node_info["Interfaces"][0]["Switch"]["ID"])
        
    def set_head_node_info(self, node_info, cluster_id, head_zone, disk_dict):
        self.cluster_info_all[cluster_id]["clusterparams"]["server"][head_zone]                             = {}
        self.cluster_info_all[cluster_id]["clusterparams"]["server"][head_zone]["head"]                     = {}
        self.cluster_info_all[cluster_id]["clusterparams"]["server"][head_zone]["head"]["node"]             = {}
        logger.debug("Setting clusterparams.server.{head zone}.head.node.id (" + cluster_id + ")")
        self.cluster_info_all[cluster_id]["clusterparams"]["server"][head_zone]["head"]["node"]["id"]       = int(node_info["ID"])
        logger.debug("Setting clusterparams.server.{head zone}.head.node.core (" + cluster_id + ")")
        self.cluster_info_all[cluster_id]["clusterparams"]["server"][head_zone]["head"]["node"]["core"]     = int(node_info["ServerPlan"]["CPU"])
        logger.debug("Setting clusterparams.server.{head zone}.head.node.memory (" + cluster_id + ")")
        self.cluster_info_all[cluster_id]["clusterparams"]["server"][head_zone]["head"]["node"]["memory"]   = int(node_info["ServerPlan"]["MemoryMB"])
        logger.debug("Setting clusterparams.server.{head zone}.head.node.state (" + cluster_id + ")")
        self.cluster_info_all[cluster_id]["clusterparams"]["server"][head_zone]["head"]["node"]["state"]    = node_info["Instance"]["Status"]
        self.cluster_info_all[cluster_id]["clusterparams"]["server"][head_zone]["head"]["nic"]              = {}
        if(node_info["Interfaces"][0]["IPAddress"] == None):
            self.cluster_info_all[cluster_id]["clusterparams"]["server"][head_zone]["head"]["nic"]["front"]         = {}
            self.cluster_info_all[cluster_id]["clusterparams"]["server"][head_zone]["head"]["nic"]["front"]["id"]   = int(node_info["Interfaces"][0]["ID"])
            self.cluster_info_all[cluster_id]["clusterparams"]["server"][head_zone]["head"]["nic"]["global"]        = {}
            self.cluster_info_all[cluster_id]["clusterparams"]["server"][head_zone]["head"]["nic"]["global"]["id"]  = int(node_info["Interfaces"][1]["ID"])
        else:
            self.cluster_info_all[cluster_id]["clusterparams"]["server"][head_zone]["head"]["nic"]["front"]         = {}
            self.cluster_info_all[cluster_id]["clusterparams"]["server"][head_zone]["head"]["nic"]["front"]["id"]   = int(node_info["Interfaces"][1]["ID"])
            self.cluster_info_all[cluster_id]["clusterparams"]["server"][head_zone]["head"]["nic"]["global"]        = {}
            self.cluster_info_all[cluster_id]["clusterparams"]["server"][head_zone]["head"]["nic"]["global"]["id"]  = int(node_info["Interfaces"][0]["ID"])
        
        self.cluster_info_all[cluster_id]["clusterparams"]["server"][head_zone]["head"]["disk"] = {}
        if(node_info["Disks"] != []):
            for i in range(len(node_info["Disks"])):
                self.cluster_info_all[cluster_id]["clusterparams"]["server"][head_zone]["head"]["disk"][i]                  = {}
                logger.debug("Setting clusterparams.server.{head zone}.head.disk." + str(i) + ".id (" + cluster_id + ")")
                self.cluster_info_all[cluster_id]["clusterparams"]["server"][head_zone]["head"]["disk"][i]["id"]            = int(node_info["Disks"][i]["ID"])
                self.cluster_info_all[cluster_id]["clusterparams"]["server"][head_zone]["head"]["disk"][i]["size"]          = int(node_info["Disks"][i]["SizeMB"])
                self.cluster_info_all[cluster_id]["clusterparams"]["server"][head_zone]["head"]["disk"][i]["connection"]    = node_info["Disks"][i]["Connection"]
                self.cluster_info_all[cluster_id]["clusterparams"]["server"][head_zone]["head"]["disk"][i]["type"]          = int(node_info["Disks"][i]["Plan"]["ID"])
                if(disk_dict[head_zone][int(node_info["Disks"][i]["ID"])]["SourceArchive"] != None):
                    if(disk_dict[head_zone][int(node_info["Disks"][i]["ID"])]["SourceArchive"]["Name"] in list(self.ext_info["OS"].keys())):
                        self.cluster_info_all[cluster_id]["clusterparams"]["server"][head_zone]["head"]["disk"][i]["os"] = disk_dict[head_zone][int(node_info["Disks"][i]["ID"])]["SourceArchive"]["Name"]
                    else:
                        logger.info("The cluster with cluster id of " + cluster_id + " cannot be operated by sacluster. OS does not support in sacluster. (" + cluster_id + ")")
                        self.delete_ids.append(cluster_id)
                        
                else:
                    logger.info("The cluster with cluster id of " + cluster_id + " cannot be operated by sacluster. The disk of head node are not set the specific archive. (" + cluster_id + ")")
                    self.delete_ids.append(cluster_id)
        else:
            logger.debug("Setting clusterparams.server.{head zone}.head.disk." + str(i) + ".id (" + cluster_id + ") to None")
            self.cluster_info_all[cluster_id]["clusterparams"]["server"][head_zone]["head"]["disk"]["id"] = None
    
    def get_bridge_info(self, switch_info, cluster_id):
        self.cluster_info_all[cluster_id]["clusterparams"]["bridge"] = {}
        if(switch_info["Bridge"] != None):
            logger.debug("Setting clusterparams.bridge.front.id (" + cluster_id + ")")
            self.cluster_info_all[cluster_id]["clusterparams"]["bridge"]["front"]           = {}
            self.cluster_info_all[cluster_id]["clusterparams"]["bridge"]["front"]["id"]     = int(switch_info["Bridge"]["ID"])
            logger.debug("Getting switch informations from bridge information (" + cluster_id + ")")
            switch_list = switch_info["Bridge"]["Info"]["Switches"]
            for sw in switch_list:
                logger.debug("Setting clusterparams.switch.{zone}.front.id (" + cluster_id + ")")
                self.cluster_info_all[cluster_id]["clusterparams"]["switch"][sw['Zone']['Name']]                = {}
                self.cluster_info_all[cluster_id]["clusterparams"]["switch"][sw['Zone']['Name']]["front"]       = {}
                self.cluster_info_all[cluster_id]["clusterparams"]["switch"][sw['Zone']['Name']]["front"]["id"] = int(sw['ID'])
        else:
            logger.debug("Switch in front area does not connect to bridge (" + cluster_id + ")")
            logger.debug("Setting clusterparams.bridge.front.id (" + cluster_id + ") to None")
            self.cluster_info_all[cluster_id]["clusterparams"]["bridge"]["front"] = None
            
    def set_compute_node_info(self, cluster_id, node_dict, head_zone, disk_dict):
        all_com_count = 0
        status_all = []
        index_all_list = []
        for zone, switch_info in self.cluster_info_all[cluster_id]["clusterparams"]["switch"].items():
            node_name_number = []
            count = 0
            for node in node_dict[zone]:
                logger.debug("Counting the number of interfaces connected to the front switch. (" + cluster_id + ")")
                
                index = 0
                interface_num = 0
                for i in range(len(node["Interfaces"])):
                    if(node["Interfaces"][i]["Switch"] != None):
                        interface_num += 1
                        if(node["Interfaces"][i]["Switch"]["ID"] == str(switch_info["front"]["id"])):
                            index += 1
                
                #index = sum([1 if node["Interfaces"][i]["Switch"]["ID"] == str(switch_info["front"]["id"]) else 0 for i in range(len(node["Interfaces"]))])
                if(index > 0 and int(node["ID"]) != self.cluster_info_all[cluster_id]["clusterparams"]["server"][head_zone]["head"]["node"]["id"]):
                    logger.debug("The node is regarded as compute node. (" + cluster_id + ")")
                    if(zone not in self.cluster_info_all[cluster_id]["clusterparams"]["server"]):
                        logger.debug("Initializing clusterparams.server.{zone} (" + cluster_id + ")")
                        self.cluster_info_all[cluster_id]["clusterparams"]["server"][zone]              = {}
                    if("compute" not in self.cluster_info_all[cluster_id]["clusterparams"]["server"][zone]):
                        logger.debug("Initializing clusterparams.server.{zone}.compute (" + cluster_id + ")")
                        self.cluster_info_all[cluster_id]["clusterparams"]["server"][zone]["compute"]   = {}
                        
                    self.cluster_info_all[cluster_id]["clusterparams"]["server"][zone]["compute"][count]                = {}
                    self.cluster_info_all[cluster_id]["clusterparams"]["server"][zone]["compute"][count]["node"]        = {}
                    self.cluster_info_all[cluster_id]["clusterparams"]["server"][zone]["compute"][count]["disk"]        = {}
                    logger.debug("Setting clusterparams.server.{zone}.compute.{number}.node.id (" + cluster_id + ")")
                    self.cluster_info_all[cluster_id]["clusterparams"]["server"][zone]["compute"][count]["node"]["id"]  = int(node["ID"])
                    
                    if("compute_node_" in node["Name"]):
                        if(node["Name"].replace("compute_node_", "").isdecimal() == True and len(node["Name"].replace("compute_node_", "")) == 3):
                            logger.debug("Setting clusterparams.server.{zone}.compute.{number}.node.core (" + cluster_id + ")")
                            self.cluster_info_all[cluster_id]["clusterparams"]["server"][zone]["compute"][count]["node"]["name"] = node["Name"]
                            name_number = node["Name"].replace("compute_node_", "")
                            if(name_number[0] == "0"):
                                if(name_number[1] == "0"):
                                    node_name_number.append(int(node["Name"].replace("compute_node_", "")[2:]))
                                else:
                                    node_name_number.append(int(node["Name"].replace("compute_node_", "")[1:]))
                            else:
                                node_name_number.append(int(node["Name"].replace("compute_node_", "")))
                        else:
                            logger.info("The cluster with cluster id of " + cluster_id + " cannot be operated by sacluster. The name of compute nodes is wrong. (" + cluster_id + ")")
                            self.delete_ids.append(cluster_id)
                    else:
                        logger.info("The cluster with cluster id of " + cluster_id + " cannot be operated by sacluster. The name of compute nodes is wrong. (" + cluster_id + ")")
                        self.delete_ids.append(cluster_id)
                    
                    logger.debug("Setting clusterparams.server.{zone}.compute.{number}.node.core (" + cluster_id + ")")
                    self.cluster_info_all[cluster_id]["clusterparams"]["server"][zone]["compute"][count]["node"]["name"]    = node["Name"]
                    logger.debug("Setting clusterparams.server.{zone}.compute.{number}.node.name (" + cluster_id + ")")
                    self.cluster_info_all[cluster_id]["clusterparams"]["server"][zone]["compute"][count]["node"]["core"]    = int(node["ServerPlan"]["CPU"])
                    logger.debug("Setting clusterparams.server.{zone}.compute.{number}.node.memory (" + cluster_id + ")")
                    self.cluster_info_all[cluster_id]["clusterparams"]["server"][zone]["compute"][count]["node"]["memory"]  = int(node["ServerPlan"]["MemoryMB"])
                    self.cluster_info_all[cluster_id]["clusterparams"]["server"][zone]["compute"][count]["nic"]             = {}
                    
                    index_all_list.append(interface_num)
                    if(interface_num == 1):
                        self.cluster_info_all[cluster_id]["clusterparams"]["server"][zone]["compute"][count]["nic"]["front"]        = {}
                        self.cluster_info_all[cluster_id]["clusterparams"]["server"][zone]["compute"][count]["nic"]["front"]["id"]  = int(node["Interfaces"][0]["ID"])
                        self.cluster_info_all[cluster_id]["clusterparams"]["server"][zone]["compute"][count]["nic"]["back"]         = None
                        self.cluster_info_all[cluster_id]["clusterparams"]["switch"][zone]["back"]                                  = None
                        self.cluster_info_all[cluster_id]["clusterparams"]["bridge"]["back"]                                        = None
                    elif(interface_num == 2): 
                        #if("back" not in self.cluster_info_all[cluster_id]["clusterparams"]["switch"][zone]):
                            #self.cluster_info_all[cluster_id]["clusterparams"]["switch"][zone]["back"] = {}
                            
                        if(int(node["Interfaces"][0]["Switch"]["ID"]) == switch_info["front"]["id"]):
                            if("back" not in self.cluster_info_all[cluster_id]["clusterparams"]["switch"][zone] or self.cluster_info_all[cluster_id]["clusterparams"]["switch"][zone]["back"] == None):
                                self.cluster_info_all[cluster_id]["clusterparams"]["switch"][zone]["back"]          = {}
                                logger.debug("Setting clusterparams.switch.{zone}.back.id (" + cluster_id + ")")
                                self.cluster_info_all[cluster_id]["clusterparams"]["switch"][zone]["back"]["id"]    = int(node["Interfaces"][1]["Switch"]["ID"])
                            else:
                                if(int(node["Interfaces"][1]["Switch"]["ID"]) != self.cluster_info_all[cluster_id]["clusterparams"]["switch"][zone]["back"]["id"]):
                                    logger.info("The cluster with cluster id of " + cluster_id + " cannot be operated by sacluster. The network structure is wrong (switch).")
                                    self.delete_ids.append(cluster_id)
                                    
                            if(self.cluster_info_all[cluster_id]["clusterparams"]["bridge"]["front"] != None):
                                back_switch_info = self.get_switch_info(zone, self.cluster_info_all[cluster_id]["clusterparams"]["switch"][zone]["back"]["id"])
                                if("back" not in self.cluster_info_all[cluster_id]["clusterparams"]["bridge"] or self.cluster_info_all[cluster_id]["clusterparams"]["bridge"]["back"] == None):
                                    logger.debug("Setting clusterparams.bridge.back.id (" + cluster_id + ")")
                                    self.cluster_info_all[cluster_id]["clusterparams"]["bridge"]["back"]        = {}
                                    self.cluster_info_all[cluster_id]["clusterparams"]["bridge"]["back"]["id"]  = int(back_switch_info["Bridge"]["ID"])
                                else:
                                    if(self.cluster_info_all[cluster_id]["clusterparams"]["bridge"]["back"]["id"] != int(back_switch_info["Bridge"]["ID"])):
                                        logger.info("The cluster with cluster id of " + cluster_id + " cannot be operated by sacluster. The network structure is wrong (bridge).")
                                        self.delete_ids.append(cluster_id)
                            else:
                                self.cluster_info_all[cluster_id]["clusterparams"]["bridge"]["back"] = None
                                    
                        elif(int(node["Interfaces"][1]["Switch"]["ID"]) == switch_info["front"]["id"]):
                            if("back" not in self.cluster_info_all[cluster_id]["clusterparams"]["switch"][zone] or self.cluster_info_all[cluster_id]["clusterparams"]["switch"][zone]["back"] == None):
                                self.cluster_info_all[cluster_id]["clusterparams"]["switch"][zone]["back"] = {}
                                logger.debug("Setting clusterparams.switch.{zone}.back.id (" + cluster_id + ")")
                                self.cluster_info_all[cluster_id]["clusterparams"]["switch"][zone]["back"]["id"] = int(node["Interfaces"][0]["Switch"]["ID"])
                            else:
                                if(int(node["Interfaces"][0]["Switch"]["ID"]) != self.cluster_info_all[cluster_id]["clusterparams"]["switch"][zone]["back"]["id"]):
                                    logger.info("The cluster with cluster id of " + cluster_id + " cannot be operated by sacluster. The network structure is wrong (switch).")
                                    self.delete_ids.append(cluster_id)
                                        
                            if(self.cluster_info_all[cluster_id]["clusterparams"]["bridge"]["front"] != None):
                                back_switch_info = self.get_switch_info(zone, self.cluster_info_all[cluster_id]["clusterparams"]["switch"][zone]["back"]["id"])
                                if("back" not in self.cluster_info_all[cluster_id]["clusterparams"]["bridge"] or self.cluster_info_all[cluster_id]["clusterparams"]["bridge"]["back"] == None):                            
                                    logger.debug("Setting clusterparams.bridge.back.id (" + cluster_id + ")")
                                    self.cluster_info_all[cluster_id]["clusterparams"]["bridge"]["back"]        = {}
                                    self.cluster_info_all[cluster_id]["clusterparams"]["bridge"]["back"]["id"]  = int(back_switch_info["Bridge"]["ID"])
                                else:
                                    if(self.cluster_info_all[cluster_id]["clusterparams"]["bridge"]["back"]["id"] != int(back_switch_info["Bridge"]["ID"])):
                                        logger.info("The cluster with cluster id of " + cluster_id + " cannot be operated by sacluster. The network structure is wrong (bridge).")
                                        self.delete_ids.append(cluster_id)
                            else:
                                self.cluster_info_all[cluster_id]["clusterparams"]["bridge"]["back"]            = None
                            
                        if(int(node["Interfaces"][0]["Switch"]["ID"]) == switch_info["front"]["id"]):
                            self.cluster_info_all[cluster_id]["clusterparams"]["server"][zone]["compute"][count]["nic"]["front"]        = {}
                            self.cluster_info_all[cluster_id]["clusterparams"]["server"][zone]["compute"][count]["nic"]["front"]["id"]  = int(node["Interfaces"][0]["ID"])
                            self.cluster_info_all[cluster_id]["clusterparams"]["server"][zone]["compute"][count]["nic"]["back"]         = {}
                            self.cluster_info_all[cluster_id]["clusterparams"]["server"][zone]["compute"][count]["nic"]["back"]["id"]   = int(node["Interfaces"][1]["ID"])
                        else:
                            self.cluster_info_all[cluster_id]["clusterparams"]["server"][zone]["compute"][count]["nic"]["front"]        = {}
                            self.cluster_info_all[cluster_id]["clusterparams"]["server"][zone]["compute"][count]["nic"]["front"]["id"]  = int(node["Interfaces"][1]["ID"])
                            self.cluster_info_all[cluster_id]["clusterparams"]["server"][zone]["compute"][count]["nic"]["back"]         = {}
                            self.cluster_info_all[cluster_id]["clusterparams"]["server"][zone]["compute"][count]["nic"]["back"]["id"]   = int(node["Interfaces"][0]["ID"])
                    else:
                        logger.info("The cluster with cluster id of " + cluster_id + " cannot be operated by sacluster. Some nodes have interfaces > 2")
                        self.delete_ids.append(cluster_id)
                    
                    if(node["Disks"] != []):
                        for i in range(len(node["Disks"])):
                            self.cluster_info_all[cluster_id]["clusterparams"]["server"][zone]["compute"][count]["disk"][i]                 = {}
                            logger.debug("Setting clusterparams.server.{zone}.compute.{number_1}.disk.{number_2}.id (" + cluster_id + ")")
                            self.cluster_info_all[cluster_id]["clusterparams"]["server"][zone]["compute"][count]["disk"][i]["id"]           = int(node["Disks"][i]["ID"])
                            self.cluster_info_all[cluster_id]["clusterparams"]["server"][zone]["compute"][count]["disk"][i]["size"]         = int(node["Disks"][i]["SizeMB"])
                            self.cluster_info_all[cluster_id]["clusterparams"]["server"][zone]["compute"][count]["disk"][i]["connection"]   = node["Disks"][i]["Connection"]
                            self.cluster_info_all[cluster_id]["clusterparams"]["server"][zone]["compute"][count]["disk"][i]["type"]         = int(node["Disks"][i]["Plan"]["ID"])
                            if(disk_dict[zone][int(node["Disks"][i]["ID"])]["SourceArchive"] != None):
                                if(disk_dict[zone][int(node["Disks"][i]["ID"])]["SourceArchive"]["Name"] in list(self.ext_info["OS"].keys())):
                                    self.cluster_info_all[cluster_id]["clusterparams"]["server"][zone]["compute"][count]["disk"][i]["os"]   = disk_dict[zone][int(node["Disks"][i]["ID"])]["SourceArchive"]["Name"]
                                else:
                                    logger.info("The cluster with cluster id of " + cluster_id + " cannot be operated by sacluster. OS does not support in sacluster. (" + cluster_id + ")")
                                    self.delete_ids.append(cluster_id)
                            else:
                                logger.info("The cluster with cluster id of " + cluster_id + " cannot be operated by sacluster. The disk of compute node are not set the specific archive. (" + cluster_id + ")")
                                self.delete_ids.append(cluster_id)
                            
                    else:
                        logger.debug("Setting clusterparams.server.{zone}.compute.{number_1}.disk.{number_2}.id (" + cluster_id + ") to None")
                        self.cluster_info_all[cluster_id]["clusterparams"]["server"][zone]["compute"][count]["disk"] = None
                        
                    logger.debug("Setting clusterparams.server.{zone}.compute.{number_1}.disk.{number_2}.state (" + cluster_id + ")")
                    self.cluster_info_all[cluster_id]["clusterparams"]["server"][zone]["compute"][count]["node"]["state"] = node["Instance"]["Status"]
                    status_all.append(node["Instance"]["Status"])
                    node_info_spare = node
                    count += 1
                    all_com_count += 1
         
            if(len(node_name_number) != 0 and len(node_name_number) == len(self.cluster_info_all[cluster_id]["clusterparams"]["server"][zone]["compute"])):
                new_index_list      = np.argsort(node_name_number)
                new_compute_info    = {}
                count_name          = 0
                for i in new_index_list:
                    new_compute_info[count_name] = self.cluster_info_all[cluster_id]["clusterparams"]["server"][zone]["compute"][i]
                    count_name += 1
                self.cluster_info_all[cluster_id]["clusterparams"]["server"][zone]["compute"] = new_compute_info
            else:
                logger.info("The cluster with cluster id of " + cluster_id + " cannot be operated by sacluster. The name of compute nodes is wrong. (" + cluster_id + ")")
                self.delete_ids.append(cluster_id)
            
        logger.debug("Setting baseparams.compute_number (" + cluster_id + ")")
        self.cluster_info_all[cluster_id]["baseparams"]["compute_number"] = all_com_count
        if(all_com_count == 0):
            logger.info("The cluster with cluster id of " + cluster_id + " cannot be operated by sacluster.This cluster do not have compute nodes.")
            self.delete_ids.append(cluster_id)
            
        if(len(list(set(index_all_list))) != 1):
            logger.info("The cluster with cluster id of " + cluster_id + " cannot be operated by sacluster. The number of interfaces of all computenades is not same.")
            self.delete_ids.append(cluster_id)
        
        logger.debug("Counting the number of running compute nodes. (" + cluster_id + ")")
        index = sum([1 if(st == "up") else 0 for st in status_all])
        if(self.cluster_info_all[cluster_id]["clusterparams"]["server"][head_zone]["head"]["node"]["state"] == "up" and index == len(status_all)):
            logger.debug("Setting baseparams.state to All up. (" + cluster_id + ")")
            self.cluster_info_all[cluster_id]["baseparams"]["state"] = "All up"
        elif(self.cluster_info_all[cluster_id]["clusterparams"]["server"][head_zone]["head"]["node"]["state"] != "up" and index == 0):
            logger.debug("Setting baseparams.state to All down. (" + cluster_id + ")")
            self.cluster_info_all[cluster_id]["baseparams"]["state"] = "All down"
        else:
            logger.debug("Setting baseparams.state to Partially up. (" + cluster_id + ")")
            self.cluster_info_all[cluster_id]["baseparams"]["state"] = "Partially up"
        
    def set_nfs_info(self, cluster_id, nfs_info):
        for zone in list(self.ext_info["Zone"].keys()):
            if(zone in self.cluster_info_all[cluster_id]["clusterparams"]["switch"]):
                head_switch_id = self.cluster_info_all[cluster_id]["clusterparams"]["switch"][zone]["front"]["id"]
                nfs_list = nfs_info[zone]
                for val in nfs_list:
                    if(val["Switch"] != None):
                        if(int(val["Switch"]["ID"]) == head_switch_id):
                            if(zone not in self.cluster_info_all[cluster_id]["clusterparams"]["nfs"]):
                                self.cluster_info_all[cluster_id]["clusterparams"]["nfs"][zone] = {}
                            self.cluster_info_all[cluster_id]["clusterparams"]["nfs"][zone]["id"] = val["ID"]
                            try:
                                self.cluster_info_all[cluster_id]["clusterparams"]["nfs"][zone]["state"] = val["Instance"]["Status"]
                            except TypeError as e:
                                printout('Warning: NFS is starting. Please wait a few moments and try again.', info_type = 0, info_list = self.info_list, fp = self.f)
                                logger.warning("Waiting for nfs to start. (" + cluster_id + ")")
                                sys.exit()
                
                if(zone not in self.cluster_info_all[cluster_id]["clusterparams"]["nfs"]):
                    self.cluster_info_all[cluster_id]["clusterparams"]["nfs"][zone] = None
                else:
                    if(len(self.cluster_info_all[cluster_id]["clusterparams"]["nfs"][zone]) == 0):
                        self.cluster_info_all[cluster_id]["clusterparams"]["nfs"][zone] = None
                        
        #if(self.cluster_info_all[cluster_id]["clusterparams"]["nfs"] == {}):
            #self.cluster_info_all[cluster_id]["clusterparams"]["nfs"] = None
            
    def generate_sample_params(self):
        self.cluster_info_all["000000"]                                     = {}
        self.cluster_info_all["000000"]["baseparams"]                       = {}
        self.cluster_info_all["000000"]["baseparams"]['compute_number']     = 2
        self.cluster_info_all["000000"]["baseparams"]['config_name']        = "dryrun_mode"
        self.cluster_info_all["000000"]["baseparams"]['global_ipaddress']   = "000.000.000.000"
        self.cluster_info_all["000000"]["baseparams"]['modified_date']      = str(datetime.datetime.now().strftime("%Y_%m_%d"))
        self.cluster_info_all["000000"]["baseparams"]['state']              = 'All down'
        self.cluster_info_all["000000"]["clusterparams"]                                = {}
        self.cluster_info_all["000000"]["clusterparams"]['bridge']                      = {'back': {'id': 000000000000}, 'front': {'id': 000000000000}}
        self.cluster_info_all["000000"]["clusterparams"]['nfs']                         = {'is1b': {'id': '000000000000', 'state': 'down'}, 'is1a': {'id': '000000000000', 'state': 'down'}}
        self.cluster_info_all["000000"]["clusterparams"]['server']                      = {}
        self.cluster_info_all["000000"]["clusterparams"]['server']['is1b']              = {}
        self.cluster_info_all["000000"]["clusterparams"]['server']['is1a']              = {}
        self.cluster_info_all["000000"]["clusterparams"]['server']['is1b']['compute']   = {0: {'disk': {0:{'connection': 'virtio', 'id': 000000000000, 'os': 'Ubuntu Server 18.04.5 LTS 64bit', 'size': 20480, 'type': 4}}, 'nic':{'back': {'id': 000000000000}, 'front': {'id': 000000000000}}, 'node': {'core': 1, 'id': 000000000000, 'memory': 1024, 'name': 'compute_node_001', 'state': 'down'}}}
        self.cluster_info_all["000000"]["clusterparams"]['server']['is1a']['compute']   = {0: {'disk': {0:{'connection': 'virtio', 'id': 000000000000, 'os': 'Ubuntu Server 18.04.5 LTS 64bit', 'size': 20480, 'type': 4}}, 'nic':{'back': {'id': 000000000000}, 'front': {'id': 000000000000}}, 'node': {'core': 1, 'id': 000000000000, 'memory': 1024, 'name': 'compute_node_001', 'state': 'down'}}}
        self.cluster_info_all["000000"]["clusterparams"]['server']['is1a']['head']      = {'disk': {0:{'connection': 'virtio', 'id': 000000000000, 'os': 'Ubuntu Server 18.04.5 LTS 64bit', 'size': 20480, 'type': 4}}, 'nic':{'back': {'id': 000000000000}, 'front': {'id': 000000000000}}, 'node': {'core': 1, 'id': 000000000000, 'memory': 1024, 'name': 'compute_node_001', 'state': 'down'}}
        self.cluster_info_all["000000"]["clusterparams"]['switch']                      = {}
        self.cluster_info_all["000000"]["clusterparams"]['switch']                      = {'is1a': {'front': {'id': 000000000000},'back': {'id': 000000000000}}, 'is1b': {'front': {'id': 000000000000},'back': {'id': 000000000000}}}
        
            
    def check_parameters(self):
        self.delete_ids = list(set(self.delete_ids))
        if(self.delete_ids != []):
            for i in self.delete_ids:
                self.cluster_info_all.pop(i)
        
    def show_cluster_info(self):
        #if(self.api_index == True and len(self.cluster_info_all) != 0):
        if(len(self.cluster_info_all) != 0):
            col                 = ["id"]
            index               = []
            df                  = []
            count               = 1
            config_name_max_len = 0
            for key, val in self.cluster_info_all.items():
                index.append(count)
                df_temp  = []
                df_temp.append(key)
            
                if(len(val["baseparams"]["config_name"]) > config_name_max_len):
                    config_name_max_len = len(val["baseparams"]["config_name"])
            
                for b_key, b_val in val["baseparams"].items():
                    df_temp.append(b_val)
                
                    if(count == 1):
                        col.append(b_key)
            
                df.append(df_temp)
                count += 1
            
            if(config_name_max_len > 20):
                config_name_max_len = 20
        
            color_dict = {"All down" : "red", "All up": "green", "Partially up": "yellow"}
        
            printout(str(col[0]).center(10) + str(col[1]).center(config_name_max_len + 4) + str(col[2]).center(14) + str(col[3]).center(19) + str(col[4]).center(15) + str(col[5]).center(13), info_type = 0, info_list = self.info_list, fp = self.f)
            for i in range(len(df)):
                printout(str(df[i][0]).center(10) + str(str(df[i][1])[: 20]).center(config_name_max_len + 4) + str(df[i][2]).center(14) + str(df[i][3]).center(19) + str(df[i][4]).center(15), info_type = 0, info_list = self.info_list, fp = self.f, end = " ")
                printout(str(df[i][5]).center(12), info_type = 0, info_list = self.info_list, fp = self.f, color = color_dict[str(df[i][5])])
        
        #elif(self.api_index == False):
            #logger.debug("This is execution with dryrun")
            #printout('This is execution with dryrun', info_type = 0, info_list = self.info_list, fp = self.f)
        else:
            logger.debug("There are no clusters in the cloud")
            printout('There are no clusters in the cloud', info_type = 0, info_list = self.info_list, fp = self.f)
            
    
    def extract_id_info(self, cluster_id):
        if(cluster_id in self.cluster_info_all):
            return True, self.cluster_info_all[cluster_id]
        else:
            return False, {}
        
    def checking_status(self, cluster_id):
        index = True
        obj = []
        #head_zone = [k for k, v in self.cluster_info_all[cluster_id]["clusterparams"]["server"].items() if "head" in v][0]
        
        #for zone, value in self.cluster_info_all[cluster_id]["clusterparams"]["server"].items():
            #if("head" in value):
                #if(value["head"]["node"]["state"] == "up"):
                    #index = False
            
            #for num, node in value["compute"].items():
                #if(node["node"]["state"] == "up"):
                    #index = False
        
        
        if(self.cluster_info_all[cluster_id]["baseparams"]["state"] != "All down"):
            obj.append("server")
            index = False
                    
        for zone, value in self.cluster_info_all[cluster_id]["clusterparams"]["nfs"].items():
            obj.append("nfs")
            if(value != None):
                if(value["state"] == "up"):
                    index = False
                
        return index, obj