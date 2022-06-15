#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Apr 23 23:58:47 2022

@author: sho
"""
import os
import json
import sys
import base64
import pprint
import logging

logger = logging.getLogger("sacluster").getChild(os.path.basename(__file__))

path = "../../.."
path = os.path.abspath("../..")
os.chdir(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(path + "/lib/others")

from API_method import get, post, put, delete
from info_print import printout

script_path = path + "/lib/.Ex_info/script"

class set_startup_scripts:
    def __init__(self, cluster_id, cluster_info, ext_info, auth_res, delete_note = 1, fp = "" , info_list = [1,0,0,0], api_index = True):
        
        self.ext_info = ext_info
        self.auth_res = auth_res
        self.cluster_info = cluster_info
        
        self.delete_note = delete_note
        self.fp = fp
        self.info_list = info_list
        self.api_index = api_index
        
        self.cluster_id = cluster_id
        self.head_zone = [zone for zone in list(self.cluster_info["clusterparams"]["server"].keys()) if "head" in self.cluster_info["clusterparams"]["server"][zone]][0]
        self.zone_list = list(self.cluster_info["clusterparams"]["server"].keys())
        
        self.url_list = {}
        for zone in self.zone_list:
            self.url_list[zone] = "https://secure.sakura.ad.jp/cloud/zone/"+ zone +"/api/cloud/1.1"
        self.head_url = "https://secure.sakura.ad.jp/cloud/zone/"+ self.head_zone +"/api/cloud/1.1"
        
        self.sub_url = ["/server","/disk","/switch","/interface","/bridge","/tag","/appliance","/power", "/note"]

        self.setting_contents = []

        self.target_scripts = {}
        self.target_scripts["head"] = []
        self.target_scripts["compute"] = []
        
        self.script_variables = {}
        self.script_variables["head"] = {}
        self.script_variables["compute"] = {}
        
        #各コンピュートノードについて設定を格納する変数を準備
        for zone in self.zone_list:
            self.script_variables["compute"][zone] = {}
            for i in list(self.cluster_info["clusterparams"]["server"][zone]["compute"].keys()):
                self.script_variables["compute"][zone][i] = {}

    #main関数
    def __call__(self):
        if(self.api_index == True):
        
            #IPアドレスの設定
            self.setting_ip()
            
            #追加処理
            
            #ヘッドノードのスタートアップスクリプトを生成
            script_head = self.get_scripts(node_type = "head")
            #ヘッドノードのスタートアップスクリプトを登録
            note_res = self.make_notes(script_head, "head")
            head_note_id = note_res['Note']['ID']
            
            #ヘッドノードのスタートアップスクリプトのリクエストボディを生成
            param = self.generate_params(note_res['Note']['ID'], self.script_variables["head"])
            
            if(len(self.script_variables["head"]) != 0):
                #スタートアップスクリプトをヘッドノードのディスクに設定
                disk_id = str(self.cluster_info["clusterparams"]["server"][self.head_zone]["head"]["disk"][0]["id"])
                self.set_scripts(disk_id, param)
            
    
            #コンピュートノードのスタートアップスクリプトの生成
            script_compute = self.get_scripts(node_type = "compute")
            #コンピュートノードのスタートアップスクリプトの登録
            note_res = self.make_notes(script_compute, "compute")
            compute_note_id = note_res['Note']['ID']
    
            #スタートアップスクリプトをコンピュートノードのディスクに設定
            for zone in self.zone_list:
                for i in list(self.cluster_info["clusterparams"]["server"][zone]["compute"].keys()):
                    if(len(self.script_variables["compute"][zone][i]) != 0):
                        #コンピュートノードのスタートアップスクリプトのリクエストボディを生成
                        param = self.generate_params(note_res['Note']['ID'], self.script_variables["compute"][zone][i])
                        #スタートアップスクリプトをコンピュートノードのディスクに設定
                        disk_id = str(self.cluster_info["clusterparams"]["server"][zone]["compute"][i]["disk"][0]["id"])
                        self.set_scripts(disk_id, param)

            if(self.delete_note == 1):
                self.delete_notes(head_note_id)
                self.delete_notes(compute_note_id)
            
        
    def generate_params(self, note_id, variables):
        param ={
                "Notes":[{
                        "ID": note_id,
                        "Variables":variables
                        
                        }]
                }
        return param
        
    #スタートアップスクリプトを登録
    def make_notes(self, script, node_type):
        
        param = {
            "Note": {
            "Name": "script in {} for {}".format(self.cluster_id, node_type),
            "Content": script
            }
        }
        
        if(self.api_index == True):
            while(True):
                res = post(self.url_list[self.head_zone] + self.sub_url[8], self.auth_res, param)
                check, msg = self.res_check(res, "post")
                
                if check == True:
                    return res
                else:
                    self.build_error()
                    
        else:
            res = "API is not used."

    def delete_notes(self, note_id):
        if(self.api_index == True):
            while(True):
                res = delete(self.url_list[self.head_zone] + self.sub_url[8] + "/{}".format(note_id), self.auth_res)
                check, msg = self.res_check(res, "delete")

                if check == True:
                    return res
                else:
                    self.build_error()
                    
        else:
            res = "API is not used."
            
    #ヘッドノードのディスクへのスクリプトの組み込み
    def set_scripts(self, disk_id, param):
        if(self.api_index == True):
            while(True):
                res = put(self.head_url + self.sub_url[1]  + "/" + disk_id + "/config", self.auth_res, param)
            
                check, msg = self.res_check(res, "put")
                
                if check == True:
                    return res
                else:
                    self.build_error()
                
        else:
            res = "API is not used."
            
    
    #APIレスポンスの確認・処理
    def res_check(self, res, met, com_index=False):
        met_dict = {"get": "is_ok", "post": "is_ok", "put": "Success","delete": "Success"}
        index = met_dict[met]
        msg = ""
        logger.debug("confirm API request(" + str(met) + ")")
        logger.debug(",".join(list(res.keys())))
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
        
    #API処理時の例外処理
    def build_error(self):
        logger.debug("decision of repeating to request")
        while(True):
            conf = printout("Try again??(yes/no):", info_type = 2, info_list = self.info_list, fp = self.fp)
            #atexit.register(self.call_delete(self.all_id_dict,self.auth_res,self.max_workers,self.fp,self.info_list,self.api_index))
            if conf == "yes":
                break
            elif conf == "no":
                self.printout_cluster("Stop processing.", cls_monitor_level = 1)
                sys.exit()
            else:
                _ = printout("Please answer yes or no.",info_list = self.info_list,fp = self.fp) 
                
    #IPアドレスの変数の設定
    def setting_ip(self):
        base = self.ext_info["IP_addr"]["base"]
        front = self.ext_info["IP_addr"]["front"]
        back = self.ext_info["IP_addr"]["back"]
        ip_zone = self.ext_info["IP_addr"]["zone_seg"]

        #ヘッドノードにおけるeth1のIPアドレスを割り当てるためのパラメータを設定
        head_ip = "{}.{}.{}.{}/16".format(base, front, ip_zone["head"], 1)
        
        # OSの名前・バージョンの取得
        os_type = self.ext_info["OS"]
        for os in os_type:
            if 'CentOS' in os:
                break
        

        if(self.cluster_info["clusterparams"]["server"][self.head_zone]["head"]["disk"][0]["os"] 
            in (list(self.ext_info["OS"][os].values()))
         ):
            self.script_variables["head"]["addresses_ip_head_centos"] = head_ip
            self.target_scripts["head"].append("ip_head_centos")
        
        #コンピュートノードにおけるeth1のIPアドレスを割り当てるためのパラメータを設定
        for zone in self.zone_list:
            if("back" in self.cluster_info["clusterparams"]["switch"][zone]):
                for i in list(self.cluster_info["clusterparams"]["server"][zone]["compute"].keys()):
                    if(self.cluster_info["clusterparams"]["server"][zone]["compute"][i]["disk"][0]["os"]
                        in list(self.ext_info["OS"][os].values()) 
                    ):
                        self.target_scripts["compute"].append("ip_compute_centos")
                        self.script_variables["compute"][zone][i]["addresses_ip_compute_centos"] = "{}.{}.{}.{}/16".format(base, back, ip_zone[zone], i + 1)
                    
    #テキストファイルの読み込み
    def open_txt(self, filename):
        with open(filename, encoding="utf-8") as f:
            contents = f.read()
        return contents
        
    #スタートアップスクリプトの生成
    def get_scripts(self, node_type):
        scripts_info = ""
        variable_info = ""
        os_info = []
    
        #ヘッダーの読み込み
        header_part = self.open_txt(script_path + "/header_script.txt")
    
        #コメント部分の定義
        target_scripts_list = ["# " + script for script in self.target_scripts[node_type]]
        comment_part = ["# @sacloud-desc-begin", "# used scripts"] + target_scripts_list + ["# @sacloud-desc-end"]
        comment_part = "\n".join(comment_part)
    
        #ログ機能部分の読み込み
        log_part = self.open_txt(script_path + "/log_script.txt")
    
        #フッター部分の読み込み
        footer_part = self.open_txt(script_path + "/footer_script.txt")
    
        #スクリプト部分の定義
        for target_script in self.target_scripts[node_type]:
            scripts_info_temp = self.open_txt(script_path + "/{}/{}_script.txt".format(target_script, target_script))
            variable_info_temp = self.open_txt(script_path + "/{}/{}_variable.txt".format(target_script, target_script))
            os_info_temp = self.open_txt(script_path + "/{}/{}_os.txt".format(target_script, target_script))
        
            scripts_info = scripts_info + "\n" + scripts_info_temp
            variable_info = variable_info + variable_info_temp
        
            os_info_temp = os_info_temp.strip().split("\n")
            if(os_info == []):
                os_info = os_info_temp
            else:
                os_info = list(set(os_info) & set(os_info_temp)) 
            
            os_info = "\n".join(os_info)
            
        #全部分を連結し、スクリプトを生成
        res_scripts = "\n".join([header_part, comment_part, variable_info, os_info, log_part, scripts_info, footer_part])
            
        return res_scripts
    
    
    







































