

import sys
import json
import os
import random
import datetime
import ipaddress
import logging
from tqdm import tqdm
from concurrent import futures
import time
import pprint

logger = logging.getLogger("sacluster").getChild(os.path.basename(__file__))

path = "../../.."
os.chdir(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(path + "/lib/others")

from API_method import get, post, put, delete
from info_print import printout

sys.path.append(path + "/lib/def_conf")
from config_function import conf_pattern_2

sys.path.append("../delete")
import delete_class
class MulHelper(object):
    def __init__(self, cls, mtd_name):
        self.cls = cls
        self.mtd_name = mtd_name

    def __call__(self, *args, **kwargs):
        return getattr(self.cls, self.mtd_name)(*args, **kwargs)
    
def unwrap_self_f(cls, mtd_name, arg, **kwarg):
    return getattr(cls, mtd_name)(*arg, **kwarg)

class build_sacluster:
    def __init__(self, configuration_info, auth_res, max_workers, fp = "" , info_list = [1,0,0,0], monitor_info_list = [1,0,0,0], api_index = True):
        """
        Parameters
        ----------
        configuration_info : dict
            Parameters to build claster
        auth_res : dict
            Authentication information
        fp : file object, optional
            file object for standard file output. The default is "".
        info_list : list, optional
            Output flag for normal output. The default is [1,0,0,0].
        monitor_info_list : TYPE, optional
            Output flag for monitor output. The default is [1,0,0,0].
        api_index : TYPE, optional
            flag to decide whether or not use API. The default is True.

        Returns
        -------
        None.

        """
        self.configuration_info = configuration_info
        self.auth_res = auth_res
        self.fp = fp
        self.info_list = info_list
        self.monitor_info_list = monitor_info_list
        self.api_index = api_index
        
        if(self.configuration_info["monitor"] == True):
            #set moitor level
            self.set_monitor_level = self.configuration_info["monitor level"]
            #set monitor token
            self.msg_token = self.configuration_info["monitor token"]
            
        else:
            #set moitor level
            self.set_monitor_level = 0
            
        #set zone list
        self.zone_list = self.configuration_info["zone"]
        #set nfs zone
        if self.configuration_info["NFS"] == True:
            self.nfs_zone = self.configuration_info["NFS zone"]
        else:
            self.nfs_zone = []
            
        #set head zone
        self.head_zone = self.configuration_info["place of head node"]
        
        #set url
        self.url_list = {}
        for zone in self.zone_list:
            self.url_list[zone] = "https://secure.sakura.ad.jp/cloud/zone/"+ zone +"/api/cloud/1.1"
        self.head_url = "https://secure.sakura.ad.jp/cloud/zone/"+ self.head_zone +"/api/cloud/1.1"
        
        #set sub url
        self.sub_url = ["/server","/disk","/switch","/interface","/bridge","/tag","/appliance","/power"]
        
        #set tag shown modefied time
        self.date_modified = "Date modified:" + str(datetime.datetime.now().strftime("%Y_%m_%d"))
        
        #compute id at each zone
        self.compute_id_zone = {}
        
        #calculate the sum of the number of compute nodes
        self.compute_num = sum([self.configuration_info["the number of compute node in " + z] for z in self.zone_list if "the number of compute node in " + z in self.configuration_info])
        
        #se max worker
        self.max_workers = max_workers
        
        #id格納のためのdictの初期化
        self.all_id_dict = {}
        self.all_id_dict["clusterparams"] = {}
        self.all_id_dict["baseparams"] = {}
        self.all_id_dict["clusterparams"]["server"] = {}
        self.all_id_dict["clusterparams"]["switch"] = {}
        self.all_id_dict["clusterparams"]["bridge"] = {}
        self.all_id_dict["clusterparams"]["nfs"] = {}
        
    #クラスターの構築
    def __call__(self):
        self.printout_cluster("Start building the cluster", cls_monitor_level = 1)
        logger.debug("Start building the cluster")
        self.bar = tqdm(total = 100)
        #, ncols=90)
        self.bar.set_description('Progress rate')
        self.progress_sum = 0
            
        #set cluster id
        self.cluster_id_def(self.zone_list[0])
        logger.info("nunmber of zones: " + str(len(self.zone_list)))
        if len(self.zone_list) == 1:
            self.all_id_dict["clusterparams"]["bridge"]["front"] = None
            self.all_id_dict["clusterparams"]["bridge"]["back"] = None
            zone = self.zone_list[0]
            #id格納のためのdictの初期化
            self.initialize_id_params(zone)
            #クラスターの構築
            self.build_head_zone(zone)
            
            self.delete_id_params(zone)
                
        elif len(self.zone_list) >= 2:
            #ヘッドノードが存在するゾーンのクラスターの構築
            self.create_bridge("front")
            if self.configuration_info["compute network"] == True:
                self.create_bridge("back")
            else:
                self.all_id_dict["clusterparams"]["bridge"]["back"] = None
                
            self.progress_bar(30)
            
            for zone in self.zone_list:
                self.initialize_id_params(zone)
                self.printout_cluster("Start building cluster sites in " + zone, cls_monitor_level = 3, overwrite = True)
                #ヘッドノードが存在するゾーンの場合
                if(zone == self.head_zone):
                    self.build_head_zone(zone)
                    if(self.api_index == True):
                        self.connect_bridge_switch(zone, str(self.all_id_dict["clusterparams"]["switch"][zone]["front"]["id"]), "front")
                    else:
                        self.connect_bridge_switch(zone, str(0000), "front")
                    self.progress_bar(20)
                
                #ヘッドノードが存在しないゾーンの場合
                else:
                    self.build_peripheral_zone(zone)
                    
                self.delete_id_params(zone)
        
        self.bar.update(100 - self.progress_sum)
        self.bar.close()
        
        if(self.api_index == True):
            #各種IDの発行とDescriptionへの書き込み
            self.cluster_info()
            
        else:
            self.printout_cluster("This is trial mode.", cls_monitor_level = 1)
            #self.printout_cluster("", cls_monitor_level = 1)
            
        self.printout_cluster("Finished building the cluster", cls_monitor_level = 1)
        logger.debug("Finished building the cluster")
            
    #ヘッドゾーンの構築
    def build_head_zone(self, zone):
        logger.debug("start building head zone")
        #set head node name
        head_node_name = "headnode"
        #ヘッドノードの構築
        self.all_id_dict["clusterparams"]["server"][zone]["head"] = {}
        server_response,res_index = self.build_server(zone, head_node_name)
        self.progress_bar(int(25/(1 + self.compute_num)))
        
        if(self.api_index == True):
            self.global_ip_addr = server_response["Server"]["Interfaces"][0]["IPAddress"]
        
            self.all_id_dict["clusterparams"]["server"][zone]["head"]["node"] = {}
            self.all_id_dict["clusterparams"]["server"][zone]["head"]["node"]["id"] = int(server_response["Server"]["ID"])
            self.all_id_dict["clusterparams"]["server"][zone]["head"]["node"]["state"] = "down"
            self.all_id_dict["clusterparams"]["server"][zone]["head"]["node"]["core"] = int(server_response["Server"]["ServerPlan"]["CPU"])
            self.all_id_dict["clusterparams"]["server"][zone]["head"]["node"]["memory"] = int(server_response["Server"]["ServerPlan"]["MemoryMB"])
            self.all_id_dict["clusterparams"]["server"][zone]["head"]["nic"] = {}
            self.all_id_dict["clusterparams"]["server"][zone]["head"]["nic"]["global"] = {}
            self.all_id_dict["clusterparams"]["server"][zone]["head"]["nic"]["global"]["id"] = int(server_response["Server"]["Interfaces"][0]["ID"])
        else:
            self.global_ip_addr = "0.0.0.0"
        #ディスクの追加
        disk_res = self.add_disk(zone, head_node_name)
        self.progress_bar(int(20/(1 + self.compute_num)))
        #ディスクとサーバの接続
        if(self.api_index == True):
            head_server_disk_res = self.connect_server_disk(zone, disk_res["Disk"]["ID"], server_response["Server"]["ID"])
            self.progress_bar(int(20/(1 + self.compute_num)))
            self.all_id_dict["clusterparams"]["server"][zone]["head"]["disk"] = {}
            self.all_id_dict["clusterparams"]["server"][zone]["head"]["disk"][0] = {}
            self.all_id_dict["clusterparams"]["server"][zone]["head"]["disk"][0]["id"] = int(disk_res["Disk"]["ID"])
            self.all_id_dict["clusterparams"]["server"][zone]["head"]["disk"][0]["size"] = int(disk_res["Disk"]["SizeMB"])
        else:
            head_server_disk_res = self.connect_server_disk(zone, 0000,0000)
        #スイッチの作成
        head_switch_id = self.create_switch(zone, head_node_name)
        if(self.api_index == True):
            self.all_id_dict["clusterparams"]["switch"][zone]["front"] = {}
            self.all_id_dict["clusterparams"]["switch"][zone]["front"]["id"] = int(head_switch_id)
        self.progress_bar(10)
        #インターフェースの追加
        
        if(self.api_index == True):
            nic_id = self.add_interface(zone, server_response["Server"]["ID"])
            self.all_id_dict["clusterparams"]["server"][zone]["head"]["nic"]["front"] = {}
            self.all_id_dict["clusterparams"]["server"][zone]["head"]["nic"]["front"]["id"] = nic_id
        else:
            nic_id = self.add_interface(zone, 0000)
        self.progress_bar(5)
        #スイッチの接続
        connect_switch_response = self.connect_switch(zone, head_switch_id, nic_id)
        self.progress_bar(10)
        #コンピュートノードの作成
        self.build_compute_nodes(zone)
        #コンピュートノード間スイッチの作成と接続
        if self.configuration_info["compute network"] == True:
            self.compute_network(zone)
        else:
            self.all_id_dict["clusterparams"]["switch"][zone]["back"] = None
            for k in self.all_id_dict["clusterparams"]["server"][zone]["compute"].keys():
                self.all_id_dict["clusterparams"]["server"][zone]["compute"][k]["nic"]["back"] = None

        self.progress_bar(5)
        #self.call_delete(self.all_id_dict,self.auth_res,self.max_workers,self.fp,self.info_list,self.api_index)
        #sys.exit()
            
        #nfsの作成
        #if(self.configuration_info["NFS"] == True):
        if zone in self.nfs_zone:
            self.setting_nfs(zone, head_switch_id)
            self.shutdown_nfs(zone, self.all_id_dict["clusterparams"]["nfs"][zone]["id"])
        else:
            self.all_id_dict["clusterparams"]["nfs"][zone] = None
        self.progress_bar(5)
            
        logger.debug("finish building head zone")
    
    def build_peripheral_zone(self, zone):
        logger.debug("start building peripheral zone")
        #スイッチの作成
        self.all_id_dict["clusterparams"]["switch"][zone]["front"] = {}
        switch_id = self.create_switch(zone, switch_name = "peripheral_head")
        self.all_id_dict["clusterparams"]["switch"][zone]["front"]["id"] = int(switch_id)
        self.progress_bar(5)
        #スイッチとブリッジの連結
        self.connect_bridge_switch(zone, switch_id, "front")
        self.progress_bar(20)
        #コンピュートノードの作成
        self.build_compute_nodes(zone)
        #コンピュートノード間スイッチの作成と接続
        if self.configuration_info["compute network"] == True:
            self.compute_network(zone)
        else:
            self.all_id_dict["clusterparams"]["switch"][zone]["back"] = None
            for k in self.all_id_dict["clusterparams"]["server"][zone]["compute"].keys():
                self.all_id_dict["clusterparams"]["server"][zone]["compute"][k]["nic"]["back"] = None
        self.progress_bar(5)
        #nfsの作成
        #if(self.configuration_info["NFS"] == True):
        if zone in self.nfs_zone:
            self.setting_nfs(zone, switch_id)
            self.shutdown_nfs(zone, self.all_id_dict["clusterparams"]["nfs"][zone]["id"])
            
        else:
            self.all_id_dict["clusterparams"]["nfs"][zone] = None
        self.progress_bar(2)

        logger.debug("finish building peripheral zone")
        
        
    #コンピュートノードの構築
    def build_compute_nodes(self, zone):
        logger.debug("start building compute nodes in " + zone)
        self.all_id_dict["clusterparams"]["server"][zone]["compute"] = {}
        n = self.configuration_info["the number of compute node in " + zone]
            
        
        with futures.ThreadPoolExecutor(max_workers = self.max_workers, thread_name_prefix="thread") as executor:
        
            while(True):
                future = []
                for i in range(n):
                    #executor.submit(MulHelper(self, "build_one_compute_node"), kwargs={"zone": zone, "i": i})
                    future.append(executor.submit(self.build_one_compute_node, i, zone))

                future_result = [f.result()[0] for f in future]
                future_msg = [f.result()[1] for f in future if(f.result()[0] == False and f.result()[1] != "")]
                if(len(future_msg) > 0):
                    future_msg = future_msg[0]
                    
                if False in future_result:
                    #self.printout_cluster("", cls_monitor_level = 2, overwrite = True)
                    
                    #self.printout_cluster("\n".join(future_msg), cls_monitor_level = 2)
                    temp = conf_pattern_2("\n".join(future_msg) + "\nTry again??", ["yes", "no"], "no", info_list = self.info_list, fp = self.fp)
                    #self.printout_cluster("", cls_monitor_level = 2, overwrite = True)
                    if temp == "no":
                        self.printout_cluster("Delete the cluster that was constructed.", cls_monitor_level = 2, overwrite = True)
                        self.printout_cluster("Stop processing.", cls_monitor_level = 2, overwrite = True)
                        self.bar.close()
                        self.call_delete(self.all_id_dict,self.auth_res,self.max_workers,self.fp,self.info_list,self.api_index)
                        sys.exit()
                else:
                    break


    
    def build_one_compute_node(self, i, zone, res_index=False):
        if i < 9:
            compute_node_name = "compute_node_00"+str(i + 1)
        elif i >= 9:
            compute_node_name = "compute_node_0"+str(i + 1)

        #サーバの作成
        if not i in self.all_id_dict["clusterparams"]["server"][zone]["compute"].keys():
            #サーバの作成
            if(self.api_index == True):
                server_response,res_index = self.build_server(zone, compute_node_name, str(self.all_id_dict["clusterparams"]["switch"][zone]["front"]["id"]))
            else:
                server_response,res_index = self.build_server(zone, compute_node_name, 0000)
            
            if(self.api_index == True):
                if res_index == True:
                    self.progress_bar(int(25/(1 + self.compute_num)))
                    self.all_id_dict["clusterparams"]["server"][zone]["compute"][i] = {}
                    self.all_id_dict["clusterparams"]["server"][zone]["compute"][i]["node"] = {}
                    self.all_id_dict["clusterparams"]["server"][zone]["compute"][i]["node"]["name"] = compute_node_name
                    self.all_id_dict["clusterparams"]["server"][zone]["compute"][i]["node"]["id"] = int(server_response["Server"]["ID"])
                    self.all_id_dict["clusterparams"]["server"][zone]["compute"][i]["node"]["state"] = "down"
                    self.all_id_dict["clusterparams"]["server"][zone]["compute"][i]["node"]["core"] = int(server_response["Server"]["ServerPlan"]["CPU"])
                    self.all_id_dict["clusterparams"]["server"][zone]["compute"][i]["node"]["memory"] = int(server_response["Server"]["ServerPlan"]["MemoryMB"])

                    self.all_id_dict["clusterparams"]["server"][zone]["compute"][i]["nic"] = {}
                    self.all_id_dict["clusterparams"]["server"][zone]["compute"][i]["nic"]["front"] = {}
                    self.all_id_dict["clusterparams"]["server"][zone]["compute"][i]["nic"]["front"]["id"] = int(server_response["Server"]["Interfaces"][0]["ID"])


                    #ディスクの作成
                    disk_res = self.add_disk(zone, compute_node_name)
                    self.progress_bar(int(20/(1 + self.compute_num)))
                    #ディスクとサーバの接続
                    compute_server_disk_res = self.connect_server_disk(zone, disk_res["Disk"]["ID"], server_response["Server"]["ID"])
                    self.progress_bar(int(20/(1 + self.compute_num)))
                    self.all_id_dict["clusterparams"]["server"][zone]["compute"][i]["disk"] = {}
                    self.all_id_dict["clusterparams"]["server"][zone]["compute"][i]["disk"][0] = {}
                    self.all_id_dict["clusterparams"]["server"][zone]["compute"][i]["disk"][0]["id"] = int(disk_res["Disk"]["ID"])
                    self.all_id_dict["clusterparams"]["server"][zone]["compute"][i]["disk"][0]["size"] = int(disk_res["Disk"]["SizeMB"])

        else:
            server_response = ""
        
        return res_index, server_response
    
    #コンピュート間スイッチの作成・接続
    def compute_network(self, zone):
        logger.debug("start creating compute network")
        compute_node_list = [[str(v["node"]["id"]), k] for k,v in self.all_id_dict["clusterparams"]["server"][zone]["compute"].items()]
        name = "compute"
        #スイッチの作成
        self.all_id_dict["clusterparams"]["switch"][zone]["back"] = {}
        com_switch_id = self.create_switch(zone, switch_name = name)
        self.all_id_dict["clusterparams"]["switch"][zone]["back"]["id"] = int(com_switch_id)
        if self.configuration_info["compute network"] == True and len(self.zone_list) >= 2:
            self.connect_bridge_switch(zone, str(self.all_id_dict["clusterparams"]["switch"][zone]["back"]["id"]), "back")
        
        for com_id, num in compute_node_list:
            #インターフェースの追加
            com_nic_id = self.add_interface(zone, com_id)
            self.all_id_dict["clusterparams"]["server"][zone]["compute"][num]["nic"]["back"] = {}
            self.all_id_dict["clusterparams"]["server"][zone]["compute"][num]["nic"]["back"]["id"] = com_nic_id
            #スイッチの接続
            connect_switch_res = self.connect_switch(zone, com_switch_id, com_nic_id)
        
        
    #サーバーの追加
    def build_server(self, zone, node_name, head_switch_id = None, ind = 0):
        self.printout_cluster("constructing " + node_name + " ……", cls_monitor_level = 2, overwrite = True)
        logger.debug("constructing " + node_name + " ……")
        if "headnode" == node_name:
            node_planid = self.configuration_info["server plan ID for head node"]
            com_index = False
            #param = {"Server":{"Name":node_name,"ServerPlan":{"ID":node_planid},"Tags":[self.cluster_id, self.date_modified],"ConnectedSwitches":[{"Scope":"shared"}],"InterfaceDriver":self.configuration_info["connection type for head node"]},"Count":0}
            param = {
                "Server":{
                    "Name":node_name,
                    "ServerPlan":{
                        "ID":node_planid
                    },
                    "Tags":[self.cluster_id, self.date_modified],
                    "ConnectedSwitches":[{"Scope":"shared"}]
                },
                "Count":0
            }
        else:
            node_planid = self.configuration_info["server plan ID for compute node"]
            com_index = True
            #param = {"Server":{"Name":node_name,"ServerPlan":{"ID":node_planid},"Tags":[self.cluster_id, self.date_modified],"ConnectedSwitches":[{"ID": head_switch_id}],"InterfaceDriver": self.configuration_info["connection type for compute node"]},"Count":0}
            param = {
                "Server":{
                    "Name":node_name,
                    "ServerPlan":{
                        "ID":node_planid
                    },
                    "Tags":[self.cluster_id, self.date_modified],
                    "ConnectedSwitches":[{"ID": head_switch_id}]
                },
                "Count":0
            }
            
            
        if(self.api_index == True):
            while(True):
                logger.debug("build server")
                server_response = post(self.url_list[zone] + self.sub_url[0], self.auth_res, param)
                check, msg = self.res_check(server_response, "post", com_index)

                if check == True:
                    node_id = server_response["Server"]["ID"]
                    logger.info(node_name + " ID: " + node_id + "-Success")
                    logger.debug("constructed " + node_name)
                    res_index = True
                    break
                else:
                    if com_index == False:
                        logger.debug("Error:cannot build server")
                        res_index = False
                        self.build_error()
                    else:
                        logger.debug("Error:cannot build server")
                        res_index = False
                        return msg,res_index
            
        else:
            server_response = "API is not used."
            logger.debug("constructed " + node_name)
            res_index = True

        return server_response,res_index
    
    #NFSのシャットダウン
    def shutdown_nfs(self, zone, nfs_id):
        self.printout_cluster("Stopping nfs ……", cls_monitor_level = 2, overwrite = True)
        logger.debug("Stopping nfs: " + str(nfs_id))
        if (self.api_index == True):
            count = 0
            while(True):
                stop_res = delete(self.url_list[zone] + self.sub_url[6] + "/" + str(nfs_id) + self.sub_url[7], self.auth_res)
                
                if "error_code" in stop_res:
                    #if(stop_res["error_code"] == "still_creating"):
                    if count == 20:
                        self.build_error()
                        count = 0
                            
                    time.sleep(60)
                    count += 1
                    #else:
                        #self.build_error()
                else:
                    logger.debug("Stopped nfs: " + str(nfs_id))
                    break
        else:
            stop_res = "API is not used."
        
    #ディスクの追加
    def add_disk(self, zone, disk_name):
        self.printout_cluster("creating disk ……", cls_monitor_level = 2, overwrite = True)
        logger.debug("creating disk for " + disk_name)
        if "headnode" == disk_name:
            disk_type = self.configuration_info["disk type for head node"]
            disk_size = self.configuration_info["disk size for head node"]
            os_type = self.configuration_info["OS ID for head node"][zone]
        
        else:
            disk_type = self.configuration_info["disk type for compute node"]
            disk_size = self.configuration_info["disk size for compute node"]
            os_type = self.configuration_info["OS ID for compute node"][zone]

        if disk_type == "SSD":
            disk_type_id = 4
        elif disk_type == "HDD":
            disk_type_id = 2
        
        param = {
            "Disk":{
                "Name":disk_name,
                "Plan":{
                    "ID":disk_type_id}, 
                    "Connection":self.configuration_info["connection type for head node"] ,
                    "SizeMB":disk_size,
                    "SourceArchive":{
                        "Availability": "available",
                        "ID":os_type
                    },
                    "Tags":[self.cluster_id]},
                    "Config":{
                        "Password":self.configuration_info["password"],
                        "HostName":self.configuration_info["username"]
                    }
                }
    
        if (self.api_index == True):
            while(True):
                disk_res = post(self.url_list[zone] + self.sub_url[1], self.auth_res, param)
                check,msg = self.res_check(disk_res, "post")
                if check == True:
                    disk_id = disk_res["Disk"]["ID"]
                    logger.info("disk ID: " + disk_id + "-Success")
                    break
                else:
                    self.build_error()
            
        else:
            disk_res = "API is not used."
            disk_id = "0000"
    
        return disk_res
        
    #スイッチの追加
    def create_switch(self, zone, switch_name):
        if "head" in switch_name:
            self.printout_cluster("creating main switch in " + zone + " ……", cls_monitor_level = 2, overwrite = True)
            logger.debug("creating main switch")
            switch_name = "Switch for " + self.configuration_info["config name"]
                
        else:
            self.printout_cluster("creating shared switch ……", cls_monitor_level = 2, overwrite = True)
            logger.debug("creating shared switch")
            switch_name = "Switch for compute node"
    
        param = {
            "Switch":{
                "Name":switch_name,
                "Tags":[self.cluster_id]
            },
            "Count":0
        }
    
        if (self.api_index == True):
            while(True):
                switch_response = post(self.url_list[zone] + self.sub_url[2], self.auth_res, param)
                check,msg = self.res_check(switch_response, "post")
                if check == True:
                    switch_id = switch_response["Switch"]["ID"]
                    logger.info("switch ID: " + switch_id + "-Success")
                    break
                else:
                    self.build_error()
            
        else:
            switch_response = "API is not used."
            switch_id = "0000"
    
        return switch_id
        
    #NFSの作成
    def setting_nfs(self, zone, switch_id):
        self.printout_cluster("setting NFS ……", cls_monitor_level = 2, overwrite = True)
        logger.debug("setting NFS")
        nfs_name = "NFS"
        ip = str(ipaddress.ip_address('192.168.1.200'))
            
        param = {
            "Appliance":{
                "Class":"nfs",
                "Name":nfs_name,
                "Plan":{
                    "ID":self.configuration_info["NFS plan ID"][zone]
                },
                "Tags":[self.cluster_id],
                "Remark":{
                    "Network":{
                        "NetworkMaskLen":24
                    },
                    "Servers":[{"IPAddress":ip}],
                    "Switch":{"ID":switch_id}
                }
            }
        } 
    
        if (self.api_index == True):
            while(True):
                nfs_res = post(self.url_list[zone] + self.sub_url[6], self.auth_res, param)
                check,msg = self.res_check(nfs_res, "post")
                if check == True:
                    self.all_id_dict["clusterparams"]["nfs"][zone]["id"] = int(nfs_res["Appliance"]["ID"])
                    self.all_id_dict["clusterparams"]["nfs"][zone]["state"] = "up"
                    
                    break
                else:
                    self.build_error()
        else:
            nfs_res = "API is not used."
            self.all_id_dict["clusterparams"]["nfs"][zone]["id"] = 0000
            self.all_id_dict["clusterparams"]["nfs"][zone]["state"] = "down"
    
    def create_bridge(self, place):
        self.printout_cluster("creating bridge ……", cls_monitor_level = 2, overwrite = True)
        logger.debug("creating bridge")
        bridge_name = "Bridge for " + self.configuration_info["config name"]
        param = {"Bridge":{"Name":bridge_name}}
    
        if (self.api_index == True):
            while(True):
                bridge_res = post(self.head_url + self.sub_url[4], self.auth_res, param)
                check,msg = self.res_check(bridge_res, "post")
                if check == True:
                    self.all_id_dict["clusterparams"]["bridge"][place] = {}
                    self.all_id_dict["clusterparams"]["bridge"][place]["id"] = int(bridge_res["Bridge"]["ID"])
                    break
                else:
                    self.build_error()
                
        else:
            bridge_res = "API is not used."
            self.all_id_dict["clusterparams"]["bridge"][place] = {}
            self.all_id_dict["clusterparams"]["bridge"][place]["id"] = 0000
    
        
        
    #インターフェースの追加
    def add_interface(self, zone, node_id):
        self.printout_cluster("adding nic ……", cls_monitor_level = 3, overwrite = True)
        logger.debug("adding nic")

        add_nic_param = {
            "Interface":{
                "Server":{
                    "ID":node_id
                }
            },
            "Count":0
        }
    
        if (self.api_index == True):
            while(True):
                add_nic_response = post(self.url_list[zone] + self.sub_url[3], self.auth_res, add_nic_param)
                check,msg = self.res_check(add_nic_response, "post")
                if check == True:
                    nic_id = add_nic_response["Interface"]["ID"]
                    logger.info("nic ID: " + nic_id + "-Success")
                    break
                else:
                    self.build_error()
            
        else:
            add_nic_response = "API is not used."
            nic_id = "0000"
    
        return nic_id
        
    #サーバとディスクの接続
    def connect_server_disk(self, zone, disk_id, server_id):
        self.printout_cluster("connecting disk to server ……", cls_monitor_level = 3, overwrite = True)
        logger.debug("connecting disk to server")
        url_disk = "/disk/" + str(disk_id) + "/to/server/" + str(server_id)
        if (self.api_index == True):
            while(True):
                server_disk_res = put(self.url_list[zone] + url_disk, self.auth_res)
                check,msg = self.res_check(server_disk_res, "put")
                if check == True:
                    logger.debug("connected disk to server: " + server_id + "-" + disk_id)
                    break
                else:
                    self.build_error()
        else:
            server_disk_res = "API is not used."

        return server_disk_res
        
    #NICをスイッチに接続
    def connect_switch(self, zone, switch_id, nic_id):
        self.printout_cluster("connecting switch to nic ……", cls_monitor_level = 3, overwrite = True)
        logger.debug("connecting switch to nic")
        sub_url_con = "/interface/" + str(nic_id) + "/to/switch/" + str(switch_id)
        if (self.api_index == True):
            while(True):
                connect_switch_response = put(self.url_list[zone] + sub_url_con, self.auth_res)
                check,msg = self.res_check(connect_switch_response, "put")
                if check == True:
                    logger.debug("connected switch to nic: " + switch_id + "-" + nic_id)
                    break
                else:
                    self.build_error()
        else:
            connect_switch_response = "API is not used."

        return connect_switch_response
    
    #ブリッジをスイッチに連結
    def connect_bridge_switch(self, zone, switch_id, place):
        self.printout_cluster("connecting switch to bridge ……", cls_monitor_level = 3, overwrite = True)
        url_bridge = "/switch/" + switch_id + "/to/bridge/" + str(self.all_id_dict["clusterparams"]["bridge"][place]["id"])
        if (self.api_index == True):
            while(True):
                bridge_switch_res = put(self.url_list[zone] + url_bridge, self.auth_res)
                check,msg = self.res_check(bridge_switch_res, "put")
                if check == True:
                    logger.debug("connected switch to bridge: " + switch_id + "-" + str(self.all_id_dict["clusterparams"]["bridge"][place]["id"]))
                    break
                else:
                    self.build_error()
        else:
            bridge_switch_res = "API is not used."
    

    #コンソール及び通知のための経由関数
    def printout_cluster(self, comment, cls_monitor_level, overwrite = False):
        if(cls_monitor_level <= self.set_monitor_level):
            printout(comment, info_type = 0, info_list = self.monitor_info_list, fp = self.fp, msg_token = self.msg_token, overwrite = overwrite)
        
        else:
            printout(comment, info_type = 0, info_list = self.info_list, fp = self.fp, msg_token = "", overwrite = overwrite)
        
    def progress_bar(self, up):
        if len(self.zone_list) == 1:
            self.bar.update(int(up))
            self.progress_sum += int(up)
            
        elif len(self.zone_list) >= 2:
            self.bar.update(int(up/(len(self.zone_list) + 0.5)))
            self.progress_sum += int(up/(len(self.zone_list) + 0.5))
        
        
    #APIレスポンスの確認・処理
    def res_check(self, res, met,com_index=False):
        met_dict = {"get": "is_ok", "post": "is_ok", "put": "Success","delete": "Success"}
        index = met_dict[met]
        msg = ""
        logger.debug("confirm API request(" + str(met) + ")")
        if (index in res.keys()):
            if res[index] == True:
                logger.debug("API processing succeeded")
                check = True
                return check, msg
            else:
                logger.warning("API processing failed")
                if com_index == False:
                    self.printout_cluster("Error:", cls_monitor_level = 1)
                    check = False
                    return check, msg
                else:
                    msg = list("Error:")
                    check = False
                    return check, msg

        elif ("is_fatal" in res.keys()):
            logger.warning("API processing failed")
            if com_index == False:
                self.printout_cluster("Status:" + res["status"], cls_monitor_level = 1)
                self.printout_cluster("Error:" + res["error_msg"], cls_monitor_level = 1)
                check = False
                return check, msg
            else:
                msg = ["Status:" + res["status"], "Error:" + res["error_msg"]]
                check = False
                return check, msg
            
    def build_error(self):
        logger.debug("decision of repeating to request")
        while(True):
            conf = printout("Try again??(yes/no):", info_type = 2,info_list = self.info_list, fp = self.fp)
            #atexit.register(self.call_delete(self.all_id_dict,self.auth_res,self.max_workers,self.fp,self.info_list,self.api_index))
            if conf == "yes":
                break
            elif conf == "no":
                self.printout_cluster("Stop processing.", cls_monitor_level = 1)
                #sys.exit()
                
                self.call_delete(self.all_id_dict,self.auth_res,self.max_workers,self.fp,self.info_list,self.api_index)
                sys.exit()
                    
            else:
                _ = printout("Please answer yes or no.",info_list = self.info_list,fp = self.fp) 
            
    #クラスタIDの割り当て
    def cluster_id_def(self, zone):
        #APIを使用する場合
        if (self.api_index == True):
            while (True):
                #クラウド上の全てのクラスタIDの取得
                logger.debug("loading all cluster IDs")
                get_cluster_id_info = get(self.url_list[zone] + self.sub_url[0], self.auth_res)
                check,msg = self.res_check(get_cluster_id_info, "get")

                if check == True:
                    logger.debug("assign cluster ID")
                    cluster_id_info = get_cluster_id_info["Servers"]
                    cluster_id_list = [d.get('Tags') for d in cluster_id_info]
                    while (True):
                        cluster_id_temp = random.randint(100000,999999)
                        if not cluster_id_temp in cluster_id_list:
                            self.cluster_id = "cluster ID: " + str(cluster_id_temp)
                            logger.info("cluster ID: " + str(self.cluster_id) + "-Success")
                            break
                        else:
                            self.printout_cluster("Duplication of cluster ID.", cls_monitor_level = 3)
                            self.printout_cluster("Reissuing cluster ID.", cls_monitor_level = 3)
                        
                    break
                else:
                    self.build_error()
        
        else:
            get_cluster_id_info = "API is not used."
            self.cluster_id = "cluster ID:" + str(random.randint(100000,999999))
    
    #各種IDの格納とDescriptionへの書き込み
    def cluster_info(self):
        result_all = []
            
        cls_info = {}
        cls_info["config name"] = str(self.configuration_info["config name"])
        cls_info["cluster ID"] = self.cluster_id
        cls_info["head node ID"] = str(self.all_id_dict["clusterparams"]["server"][self.head_zone]["head"]["node"]["id"])
        cls_info["number of compute node"] = str(sum([len(self.all_id_dict["clusterparams"]["server"][zone]["compute"]) for zone in self.zone_list]))
        cls_info["Date modified"] = datetime.datetime.now().strftime("%Y/%m/%d")
        
        self.all_id_dict["baseparams"]["config name"] = cls_info["config name"]
        self.all_id_dict["baseparams"]["compute_number"] = int(cls_info["number of compute node"])
        self.all_id_dict["baseparams"]["state"] = "All down"
        self.all_id_dict["baseparams"]["modified_date"] = cls_info["Date modified"]
        self.all_id_dict["baseparams"]["global_ipaddress"] = self.global_ip_addr
        
        
        self.printout_cluster("", cls_monitor_level = 4)
        result_all.append("###Cluster Infomation###")
        result_all.append("config name: " + cls_info["config name"])
        
        result_all.append("global ipaddress in head node: " + self.global_ip_addr)
        result_all.append(cls_info["cluster ID"])
        result_all.append("head node ID: " + cls_info["head node ID"])
        for zone in self.zone_list:
            result_all.append("compute node ID: ")
            result_all.append(zone + ": " + ', '.join([str(v["node"]["id"]) for k,v in self.all_id_dict["clusterparams"]["server"][zone]["compute"].items()]))
        result_all.append("number of compute node: " + cls_info["number of compute node"])
        result_all.append("date modified: " + cls_info["Date modified"])
        result_all.append("########################")
        
        result_all = "\n".join(result_all)
        self.printout_cluster(result_all, cls_monitor_level = 1)
        self.printout_cluster("", cls_monitor_level = 4)
        
        logger.debug("writing cluster information to head node")
        desc_param = {
            "Server":{
                "Description":json.dumps(cls_info)
            }
        }
        if (self.api_index == True):
            while(True):
                cluster_info_res = put(self.head_url + self.sub_url[0] + "/" + str(self.all_id_dict["clusterparams"]["server"][self.head_zone]["head"]["node"]["id"]), self.auth_res, desc_param)
                check,msg = self.res_check(cluster_info_res, "put")
                if check == True:
                    break
                else:
                    self.build_error()
        else:
            cluster_info_res = "API is not used."
            
        
    
    #id格納のためのdictの初期化(各ゾーン)
    def initialize_id_params(self, zone):
        self.all_id_dict["clusterparams"]["server"][zone] = {}
        self.all_id_dict["clusterparams"]["switch"][zone] = {}
        self.all_id_dict["clusterparams"]["nfs"][zone] = {}
        
    def delete_id_params(self, zone):
        if(self.all_id_dict["clusterparams"]["nfs"][zone] == {}):
            self.all_id_dict["clusterparams"]["nfs"].pop(zone)
            
            
    def call_delete(self,cluster_info,auth_res,max_workers,fp,info_list,api_index):
        delete_obj = delete_class.delete_sacluster(cluster_info, auth_res,max_workers,fp=fp,info_list=info_list,api_index=api_index)
        delete_obj()
    
    





















































