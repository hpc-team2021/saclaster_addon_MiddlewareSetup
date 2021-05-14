#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Feb  8 11:06:55 2021

@author: tsukiyamashou
"""

import os
os.chdir(os.path.dirname(os.path.abspath(__file__)))
common_path = os.path.abspath("../../..")

import base64
import sys
sys.path.append(common_path + "/lib/others")
from info_print import printout
sys.path.append(common_path + "/lib/def_conf")
from config_function import set_parm, conf_pattern_main, conf_pattern_1, conf_pattern_2, conf_pattern_3, conf_pattern_4, conf_pattern_5
sys.path.append(common_path + "/lib/cls/construction")
import logging

logger = logging.getLogger("sacluster").getChild(os.path.basename(__file__))


def set_app_params(config_param, api_index = True, f = "", info_list = [1,0,0,0]):
    logger.debug('setting username and password')
    username = conf_pattern_1("username", info_list = info_list, fp = f)
    password = conf_pattern_1("password", info_list = info_list, fp = f)
        
    if(username == ""):
        logger.info('username and password are automatically set to sacloud')
        username = "sacloud"
        password = "sacloud"

    config_param["application"] = {}
    config_param["application"]["username"] = username
    config_param["application"]["password"] = password
        
    return config_param
            
def config_transformation(ext_info, config_param, api_index = True, f = "", info_list = [1,0,0,0]):
    logger.info("Preparing to build the cluster")
    _ = printout("Preparing to build the cluster ...",info_list = info_list, fp = f)
    disk_plan_dict = {"SSDプラン":"SSD","標準プラン":"HDD"}
    build_params = {}
    #about config name
    build_params["config name"] = str(config_param["config_name"])
    
    #about zone
    build_params["zone"] = list(config_param["Zone"]["Zone"].keys())
    build_params["place of head node"] = config_param["Zone"]["Head Zone"]
    
    #about head node
    #build_params["the number of core for head node"] = config_param["Head"]["Node"]["core"]
    #build_params["size of memory for head node"] = config_param["Head"]["Node"]["memory"]
    build_params["server plan ID for head node"] = config_param["Head"]["Node"]["NodePlan"]
    build_params["disk type for head node"] = disk_plan_dict[config_param["Head"]["Disk"]["Type"]]
    build_params["disk size for head node"] = config_param["Head"]["Disk"]["Size"]
    build_params["connection type for head node"] = config_param["Head"]["Connection type"]
    build_params["OS for head node"] = config_param["Head"]["OS"]["name"]
    build_params["OS ID for head node"] = {}
    for zone in list(config_param["Zone"]["Zone"].keys()):
        build_params["OS ID for head node"][zone] = str(config_param["Head"]["OS"]["OSPlan"][zone])

    #about compute node
    for zone in list(config_param["Zone"]["Zone"].keys()):
        build_params["the number of compute node in " + str(zone)] = config_param["Zone"]["Zone"][zone]
        
    build_params["compute network"] = config_param["Compute"]["Compute switch"]
    #build_params["the number of core for compute node"] = config_param["Compute"]["Compute node"]["Node"]["core"]
    #build_params["size of memory for compute node"] = config_param["Compute"]["Compute node"]["Node"]["memory"]
    build_params["server plan ID for compute node"] = config_param["Compute"]["Compute node"]["Node"]["NodePlan"]
    build_params["disk type for compute node"] = disk_plan_dict[config_param["Compute"]["Compute node"]["Disk"]["Type"]]
    build_params["disk size for compute node"] = config_param["Compute"]["Compute node"]["Disk"]["Size"]
    build_params["connection type for compute node"] = config_param["Compute"]["Compute node"]["Connection type"]
    build_params["OS for compute node"] = config_param["Compute"]["Compute node"]["OS"]["name"]
    build_params["OS ID for compute node"] = {}
    for zone in list(config_param["Zone"]["Zone"].keys()):
        build_params["OS ID for compute node"][zone] = str(config_param["Compute"]["Compute node"]["OS"]["OSPlan"][zone])
    
    
    #about NFS
    build_params["NFS"] = config_param["NFS"]["NFS"]
    if(build_params["NFS"] == True):
        build_params["NFS zone"] = list(config_param["NFS"]["NFS zone"].keys())
        build_params["NFS plan ID"] = {}
        for zone, val in config_param["NFS"]["NFS zone"].items():
            build_params["NFS plan ID"][zone] = val["NFSPlan"]
        
    #about monitor
    build_params["monitor"] = config_param["Monitor"]["Monitor"]
    if(build_params["monitor"] == True):
        build_params["monitor method"] = config_param["Monitor"]["Monitor type"]
        build_params["monitor token"] = config_param["Monitor"]["Monitor key"]
        build_params["monitor level"] = config_param["Monitor"]["Monitor level"]
        
    build_params["username"] = config_param["application"]["username"]
    build_params["password"] = config_param["application"]["password"]
        
    return build_params
    

































