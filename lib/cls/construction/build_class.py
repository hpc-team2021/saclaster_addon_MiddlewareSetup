#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Feb 12 20:06:15 2021

@author: tsukiyamashou
"""

import sys
import json
import os
import random
import datetime
import ipaddress
import logging

logger = logging.getLogger("sacluster").getChild(os.path.basename(__file__))

path = "../../.."
os.chdir(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(path + "/lib/others")

from API_method import get, post, put
from info_print import printout



class build_sacluster:
    def __init__(self, configuration_info, auth_res, fp = "" , info_list = [1,0,0,0], monitor_info_list = [1,0,0,0], api_index = True):
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
            
        #set head zone
        self.head_zone = self.configuration_info["place of head node"]
        
        #set url
        self.url_list = {}
        for zone in self.zone_list:
            self.url_list[zone] = "https://secure.sakura.ad.jp/cloud/zone/"+ zone +"/api/cloud/1.1"
        self.head_url = "https://secure.sakura.ad.jp/cloud/zone/"+ self.head_zone +"/api/cloud/1.1"
        
        #set sub url
        self.sub_url = ["/server","/disk","/switch","/interface","/bridge","/tag","/appliance"]
        
        #set tag shown modefied time
        self.date_modified = "Date modified:" + str(datetime.datetime.now().strftime("%Y_%m_%d"))
        
        #compute id at each zone
        self.compute_id_zone = {}
        
        #id格納のためのdictの初期化
        self.all_id_dict = {}
        self.all_id_dict["server"] = {}
        self.all_id_dict["switch"] = {}
        self.all_id_dict["bridge"] = {}
        self.all_id_dict["nfs"] = {}
        
    #クラスターの構築
    def __call__(self):
        self.printout_cluster("Start building the cluster", cls_monitor_level = 1)
        logger.debug("Start building the cluster")
            
        #set cluster id
        self.cluster_id_def(self.zone_list[0])
        logger.info("nunmber of zones: " + str(len(self.zone_list)))
        if len(self.zone_list) == 1:
            zone = self.zone_list[0]
            #id格納のためのdictの初期化
            self.initialize_id_params(zone)
            #クラスターの構築
            self.build_head_zone(zone)
                
        elif len(self.zone_list) >= 2 :
            #ヘッドノードが存在するゾーンのクラスターの構築
            self.create_bridge()
            
            for zone in self.zone_list:
                self.initialize_id_params(zone)
                self.printout_cluster("Start building cluster sites in " + zone, cls_monitor_level = 3)
                #ヘッドノードが存在するゾーンの場合
                if(zone == self.head_zone):
                    self.build_head_zone(zone)
                    self.connect_bridge_switch(zone, self.all_id_dict["switch"][zone]["head"]["id"])
                    
                #ヘッドノードが存在しないゾーンの場合
                else:
                    self.build_peripheral_zone(zone)
                    
        #各種IDの発行とDescriptionへの書き込み
        self.cluster_info()
            
        self.printout_cluster("Finished building the cluster", cls_monitor_level = 1)
        logger.debug("Finished building the cluster")
            
    #ヘッドゾーンの構築
    def build_head_zone(self, zone):
        logger.debug("start building head zone")
        #set head node name
        head_node_name = "headnode"
        #ヘッドノードの構築
        self.all_id_dict["server"][zone]["head"] = {}
        head_node_id = self.build_server(zone, head_node_name)
        
        if(self.api_index == True):
            self.global_ip_addr = self.server_response["Server"]["Interfaces"][0]["IPAddress"]
        else:
            self.global_ip_addr = "0.0.0.0"
            
        self.all_id_dict["server"][zone]["head"]["node"] = head_node_id
        #ディスクの追加
        head_disk_id = self.add_disk(zone, head_node_name)
        #ディスクとサーバの接続
        head_server_disk_res = self.connect_server_disk(zone, head_disk_id, head_node_id)
        self.all_id_dict["server"][zone]["head"]["disk"] = head_disk_id
        #スイッチの作成
        self.all_id_dict["switch"][zone]["head"] = {}
        head_switch_id = self.create_switch(zone, head_node_name)
        self.all_id_dict["switch"][zone]["head"]["id"] = head_switch_id
        #インターフェースの追加
        nic_id = self.add_interface(zone, head_node_id)
        #スイッチの接続
        connect_switch_response = self.connect_switch(zone, head_switch_id, nic_id)
        #コンピュートノードの作成
        self.build_compute_node(zone)
        #コンピュートノード間スイッチの作成と接続
        if self.configuration_info["compute network"] == True:
            com_network = self.compute_network(zone)
            
        #nfsの作成
        if(self.configuration_info["NFS"] == True):
            if zone in self.nfs_zone:
                self.setting_nfs(zone, head_switch_id)
            
        logger.debug("finish building head zone")
    
    def build_peripheral_zone(self, zone):
        logger.debug("start building peripheral zone")
        #スイッチの作成
        self.all_id_dict["switch"][zone]["head"] = {}
        switch_id = self.create_switch(zone, switch_name = "peripheral_head")
        self.all_id_dict["switch"][zone]["head"]["id"] = switch_id
        #スイッチとブリッジの連結
        self.connect_bridge_switch(zone, switch_id)
        #コンピュートノードの作成
        self.build_compute_node(zone)
        #コンピュートノード間スイッチの作成と接続
        if self.configuration_info["compute network"] == True:
            self.compute_network(zone)
        
        #nfsの作成
        if(self.configuration_info["NFS"] == True):
            if zone in self.nfs_zone:
                self.setting_nfs(zone, switch_id)

        logger.debug("finish building peripheral zone")
        
        
    #コンピュートノードの構築
    def build_compute_node(self, zone):
        logger.debug("start building compute nodes in " + zone)
        self.all_id_dict["server"][zone]["compute"] = {}
        n = self.configuration_info["the number of compute node in " + zone]
    
        for i in range(n):
            if i < 10:
                compute_node_name = "compute_node_00"+str(i + 1)
            elif i >= 10:
                compute_node_name = "compute_node_0"+str(i + 1)

            self.all_id_dict["server"][zone]["compute"][i] = {}
            #サーバの作成
            compute_node_id = self.build_server(zone, compute_node_name, self.all_id_dict["switch"][zone]["head"]["id"])
            self.all_id_dict["server"][zone]["compute"][i]["node"] = compute_node_id
            #ディスクの作成
            compute_disk_id = self.add_disk(zone, compute_node_name)
            #ディスクとサーバの接続
            compute_server_disk_res = self.connect_server_disk(zone, compute_disk_id, compute_node_id)
            self.all_id_dict["server"][zone]["compute"][i]["disk"] = compute_disk_id
            
    
    #コンピュート間スイッチの作成・接続
    def compute_network(self, zone):
        logger.debug("start creating compute network")
        compute_node_list = [v["node"] for k,v in self.all_id_dict["server"][zone]["compute"].items()]
        name = "compute"
        #スイッチの作成
        self.all_id_dict["switch"][zone]["shared"] = {}
        com_switch_id = self.create_switch(zone, switch_name = name)
        self.all_id_dict["switch"][zone]["shared"]["id"] = com_switch_id
        for com_id in compute_node_list:
            #インターフェースの追加
            com_nic_id = self.add_interface(zone, com_id)
            #スイッチの接続
            connect_switch_res = self.connect_switch(zone, com_switch_id, com_nic_id)
        
        
    #サーバーの追加
    def build_server(self, zone, node_name, head_switch_id = None):
        self.printout_cluster("constructing " + node_name, cls_monitor_level = 2)
        logger.debug("constructing " + node_name)
        if "headnode" == node_name:
            node_planid = self.configuration_info["server plan ID for head node"]
            param = {"Server":{"Name":node_name,"ServerPlan":{"ID":node_planid},"Tags":[self.cluster_id, self.date_modified],"ConnectedSwitches":[{"Scope":"shared"}],"InterfaceDriver":self.configuration_info["connection type for head node"]},"Count":0}
        
        else:
            node_planid = self.configuration_info["server plan ID for compute node"]
            param = {"Server":{"Name":node_name,"ServerPlan":{"ID":node_planid},"Tags":[self.cluster_id, self.date_modified],"ConnectedSwitches":[{"ID": head_switch_id}],"InterfaceDriver": self.configuration_info["connection type for compute node"]},"Count":0}
            
        if (self.api_index == True):
            while(True):
                logger.debug("build server")
                self.server_response = post(self.url_list[zone] + self.sub_url[0], self.auth_res, param)
                check = self.res_check(self.server_response, "post")

                if check == True:
                    node_id = self.server_response["Server"]["ID"]
                    logger.info(node_name + " ID: " + node_id + "-Success")
                    break
                else:
                    self.build_error()
            
        else:
            self.server_response = "API is not used."
            node_id = "000"
        
        logger.debug("constructed " + node_name)

        return node_id
        
    #ディスクの追加
    def add_disk(self, zone, disk_name):
        self.printout_cluster("creating disk ……", cls_monitor_level = 2)
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
            
    
        param = {"Disk":{"Name":disk_name,"Plan":{"ID":disk_type_id},"SizeMB":disk_size,"SourceArchive":{"Availability": "available","ID":os_type},"Tags":[self.cluster_id]},"Config":{"Password":self.configuration_info["password"],"HostName":self.configuration_info["username"]}}
    
        if (self.api_index == True):
            while(True):
                disk_res = post(self.url_list[zone] + self.sub_url[1], self.auth_res, param)
                check = self.res_check(disk_res, "post")
                if check == True:
                    disk_id = disk_res["Disk"]["ID"]
                    logger.info("disk ID: " + disk_id + "-Success")
                    break
                else:
                    self.build_error()
            
        else:
            disk_res = "API is not used."
            disk_id = "0000"
    
        return disk_id
        
    #スイッチの追加
    def create_switch(self, zone, switch_name):
        if "head" in switch_name:
            self.printout_cluster("creating main switch in " + zone + " ……", cls_monitor_level = 2)
            logger.debug("creating main switch")
            switch_name = "Switch for " + self.configuration_info["config name"]
                
        else:
            self.printout_cluster("creating shared switch ……", cls_monitor_level = 2)
            logger.debug("creating shared switch")
            switch_name = "Switch for compute node"
    
        param = {"Switch":{"Name":switch_name,"Tags":[self.cluster_id]},"Count":0}
    
        if (self.api_index == True):
            while(True):
                switch_response = post(self.url_list[zone] + self.sub_url[2], self.auth_res, param)
                check = self.res_check(switch_response, "post")
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
        self.printout_cluster("setting NFS ……", cls_monitor_level = 2)
        logger.debug("setting NFS")
        nfs_name = "NFS"
        ip = str(ipaddress.ip_address('192.168.1.200'))
            
        param = {"Appliance":{"Class":"nfs","Name":nfs_name,"Plan":{"ID":self.configuration_info["NFS plan ID"][zone]},"Tags":[self.cluster_id],"Remark":{"Network":{"NetworkMaskLen":24},"Servers":[{"IPAddress":ip}],"Switch":{"ID":switch_id}}}} 
    
        if (self.api_index == True):
            while(True):
                nfs_res = post(self.url_list[zone] + self.sub_url[6], self.auth_res, param)
                check = self.res_check(nfs_res, "post")
                if check == True:
                    self.all_id_dict["nfs"][zone]["id"] = nfs_res["Appliance"]["ID"]
                    
                    break
                else:
                    self.build_error()
        else:
            nfs_res = "API is not used."
            self.all_id_dict["nfs"][zone]["id"] = "0000"
    
    def create_bridge(self):
        self.printout_cluster("creating bridge ……", cls_monitor_level = 2)
        logger.debug("creating bridge")
        bridge_name = "Bridge for " + self.configuration_info["config name"]
        param = {"Bridge":{"Name":bridge_name}}
    
        if (self.api_index == True):
            while(True):
                bridge_res = post(self.head_url + self.sub_url[4], self.auth_res, param)
                check = self.res_check(bridge_res, "post")
                if check == True:
                    self.all_id_dict["bridge"]["id"] = bridge_res["Bridge"]["ID"]
                    break
                
        else:
            bridge_res = "API is not used."
            self.all_id_dict["bridge"]["id"] = "0000"
    
        
        
    #インターフェースの追加
    def add_interface(self, zone, node_id):
        self.printout_cluster("adding nic ……", cls_monitor_level = 3)
        logger.debug("adding nic")

        add_nic_param = {"Interface":{"Server":{"ID":node_id}}, "Count":0}
    
        if (self.api_index == True):
            while(True):
                add_nic_response = post(self.url_list[zone] + self.sub_url[3], self.auth_res, add_nic_param)
                check = self.res_check(add_nic_response, "post")
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
        self.printout_cluster("connecting disk to server ……", cls_monitor_level = 3)
        logger.debug("connecting disk to server")
        url_disk = "/disk/" + disk_id + "/to/server/" + server_id
        if (self.api_index == True):
            while(True):
                server_disk_res = put(self.url_list[zone] + url_disk, self.auth_res)
                check = self.res_check(server_disk_res, "put")
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
        self.printout_cluster("connecting switch to nic ……", cls_monitor_level = 3)
        logger.debug("connecting switch to nic")
        sub_url_con = "/interface/" + nic_id + "/to/switch/" + switch_id
        if (self.api_index == True):
            while(True):
                connect_switch_response = put(self.url_list[zone] + sub_url_con, self.auth_res)
                check = self.res_check(connect_switch_response, "put")
                if check == True:
                    logger.debug("connected switch to nic: " + switch_id + "-" + nic_id)
                    break
                else:
                    self.build_error()
        else:
            connect_switch_response = "API is not used."

        return connect_switch_response
    
    #ブリッジをスイッチに連結
    def connect_bridge_switch(self, zone, switch_id):
        self.printout_cluster("connecting switch to bridge ……", cls_monitor_level = 3)
        url_bridge = "/switch/" + switch_id + "/to/bridge/" + self.all_id_dict["bridge"]["id"]
        if (self.api_index == True):
            while(True):
                bridge_switch_res = put(self.url_list[zone] + url_bridge, self.auth_res)
                check = self.res_check(bridge_switch_res, "put")
                if check == True:
                    logger.debug("connected switch to bridge: " + switch_id + "-" + self.all_id_dict["bridge"]["id"])
                    break
                else:
                    self.build_error()
        else:
            bridge_switch_res = "API is not used."
    

    #コンソール及び通知のための経由関数
    def printout_cluster(self, comment, cls_monitor_level):
        if(cls_monitor_level <= self.set_monitor_level):
            printout(comment, info_type = 0, info_list = self.monitor_info_list, fp = self.fp, msg_token = self.msg_token)
        
        else:
            printout(comment, info_type = 0, info_list = self.info_list, fp = self.fp, msg_token = "")
        
    #APIレスポンスの確認・処理
    def res_check(self, res, met):
        met_dict = {"get": "is_ok", "post": "is_ok", "put": "Success"}
        index = met_dict[met]
                
        logger.debug("confirm API request(" + str(met) + ")")
        if (index in res.keys()):
            if res[index] == True:
                logger.debug("API processing succeeded")
                check = True
                return check
            else:
                logger.warning("API processing failed")
                self.printout_cluster("Error:", cls_monitor_level = 1)
                check = False
                return check

        elif ("is_fatal" in res.keys()):
            logger.warning("API processing failed")
            self.printout_cluster("Status:" + res["status"], cls_monitor_level = 1)
            self.printout_cluster("Error:" + res["error_msg"], cls_monitor_level = 1)
            check = False
            return check
            
    #API処理失敗時の処理
    def build_error(self):
        logger.debug("decision of repeating to request")
        while(True):
            conf = printout("Try again??(yes/no):",info_type = 2, info_list = self.info_list, fp = self.fp)
            if conf == "yes":
                break
            elif conf == "no":
                self.printout_cluster("Stop processing.", cls_monitor_level = 1)
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
                check = self.res_check(get_cluster_id_info, "get")

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
        cls_info["head node ID"] = str(self.all_id_dict["server"][self.head_zone]["head"]["node"])
        cls_info["number of compute node"] = str(sum([len(self.all_id_dict["server"][zone]["compute"]) for zone in self.zone_list]))
        cls_info["Date modified"] = datetime.datetime.now().strftime("%Y/%m/%d")
        
        self.printout_cluster("", cls_monitor_level = 4)
        result_all.append("###Cluster Infomation###")
        result_all.append("config name: " + cls_info["config name"])
        
        result_all.append("global ipaddress in head node: " + self.global_ip_addr)
        result_all.append(cls_info["cluster ID"])
        result_all.append("head node ID: " + cls_info["head node ID"])
        for zone in self.zone_list:
            result_all.append("compute node ID: ")
            result_all.append(zone + ": " + ', '.join([v["node"] for k,v in self.all_id_dict["server"][zone]["compute"].items()]))
        result_all.append("number of compute node: " + cls_info["number of compute node"])
        result_all.append("date modified: " + cls_info["Date modified"])
        result_all.append("########################")
        
        result_all = "\n".join(result_all)
        self.printout_cluster(result_all, cls_monitor_level = 1)
        self.printout_cluster("", cls_monitor_level = 4)
        
        
        #self.printout_cluster("###Cluster Infomation###", cls_monitor_level = 1)
        #self.printout_cluster("config name: " + cls_info["config name"], cls_monitor_level = 1)
        #self.printout_cluster(cls_info["cluster ID"], cls_monitor_level = 1)
        #self.printout_cluster("head node ID: " + cls_info["head node ID"], cls_monitor_level = 1)
        #for zone in self.zone_list:
            #self.printout_cluster("compute node ID: ", cls_monitor_level = 1)
            #self.printout_cluster(zone + ": " + ', '.join([v["node"] for k,v in self.all_id_dict["server"][zone]["compute"].items()]), cls_monitor_level = 1)
        #self.printout_cluster("number of compute node: " + cls_info["number of compute node"], cls_monitor_level = 1)
        #self.printout_cluster("Date modified: " + cls_info["Date modified"], cls_monitor_level = 1)
        #self.printout_cluster("########################", cls_monitor_level = 1)
        
        logger.debug("writing cluster information to head node")
        desc_param = {"Server":{"Description":json.dumps(cls_info)}}
        if (self.api_index == True):
            while(True):
                cluster_info_res = put(self.head_url + self.sub_url[0] + "/" + str(self.all_id_dict["server"][self.head_zone]["head"]["node"]), self.auth_res, desc_param)
                check = self.res_check(cluster_info_res, "put")
                if check == True:
                    break
                else:
                    self.build_error()
        else:
            cluster_info_res = "API is not used."
            
        
    
    #id格納のためのdictの初期化(各ゾーン)
    def initialize_id_params(self, zone):
        self.all_id_dict["server"][zone] = {}
        self.all_id_dict["switch"][zone] = {}
        self.all_id_dict["nfs"][zone] = {}
    
    
    





















































