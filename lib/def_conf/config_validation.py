#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Dec 27 20:17:36 2020

@author: sho
"""
import os
os.chdir(os.path.dirname(os.path.abspath(__file__)))
path = os.path.abspath("../..")

import sys
import json
from jsonschema import validate, ValidationError
from load_external_data import external_data
from info_print import printout
from def_config_making import config_making_main
import logging

logger = logging.getLogger("sacluster").getChild(os.path.basename(__file__))

def load_config(filename, path):
    with open(path + "/" + filename) as f:
        data = json.load(f)
        
    return data

def load_config_checker(info_list = [1,0,0,0], fp = ""):
    _ = printout("loading config checker ...", info_type = 0, info_list = info_list, fp = fp)
    try:
        with open(path + "/lib/.Ex_info/config_checker.json", "r") as f:
            data = json.load(f)
    
    except FileNotFoundError as e:
        _ = printout("EnvironmentalError: config_checker.json does not exist under sacluster/lib/.Ex_info\nYou should install sacluster from url", info_type = 0, info_list = info_list, fp = fp)
        sys.exit()
        
    return data

#Check if config parameter should be redefined（Force close if not redefined）
def redefine_config(ext_info, info_list = [1,0,0,0], fp = ""):
    while(True):
        res = printout("Do you want to redefine new config params (yes or no) >>", info_type = 1, info_list = info_list, fp = fp)
        if(res == "yes" or res == "no" or res == "y" or res == "n"):
            break
        else:
            res = printout("Warning: Please select yes (y) or no (n).", info_type = 0, info_list = info_list, fp = fp)
    
    if(res == "yes" or res == "y"):
        out_path = printout("Output path >>", info_type = 1, info_list = info_list, fp = fp)
        config_param = config_making_main(ext_info, out_path = out_path, info_list = info_list, fp = fp)
        return config_param
    else:
        _ = printout("ConfigError: config params cannot be loaded.", info_type = 0, info_list = info_list, fp = fp)
        sys.exit()
        
def checking_config_details(ext_info, config_param, info_list = [1,0,0,0], fp = ""):
    
    ## NFS
    # If NFS has been configured
    logger.debug('Checking params of nfs')
    if("NFS" in config_param):
        # When NFS is True
        if(config_param["NFS"]["NFS"] == True):
            # Check if the NFS zone is set.
            if("NFS zone" not in config_param["NFS"]):
                logger.error('ConfigError: If NFS is True, configure the NFS settings for each zone')
                _ = printout("ConfigError: If NFS is True, configure the NFS settings for each zone", info_type = 0, info_list = info_list, fp = fp)
                config_param = redefine_config(ext_info, info_list = info_list, fp = fp)
                return config_param
            else:
                if(len(config_param["NFS"]["NFS zone"]) == 0):
                    _ = printout("ConfigError: NFS setting at each zone is empty", info_type = 0, info_list = info_list, fp = fp)
                    config_param = redefine_config(ext_info, info_list = info_list, fp = fp)
                    return config_param
            
            # If the zone is not specified
            if("Zone" not in config_param):
                logger.error('ConfigError: NFS must be set with Zone')
                _ = printout("ConfigError: NFS must be set with Zone", info_type = 0, info_list = info_list, fp = fp)
                config_param = redefine_config(ext_info, info_list = info_list, fp = fp)
                return config_param
            # If a zone is specified
            else:
                # Check if the zone specified by nfs is included in the zone configuration.
                config_zones = list(set(config_param["Zone"]["Zone"].keys()))
                nfs_zones = list(set(config_param["NFS"]["NFS zone"].keys()))
            
                if(len(list(set(nfs_zones) & set(config_zones))) != len(nfs_zones)):
                    logger.error('ConfigError: The zone setting in NFS params does not mutch to the zone setting in Zone params')
                    _ = printout("ConfigError: The zone setting in NFS params does not mutch to the zone setting in Zone params", info_type = 0, info_list = info_list, fp = fp)
                    config_param = redefine_config(ext_info, info_list = info_list, fp = fp)
                    return config_param

            # Verify that the specified zone is a zone where NFS can be installed
            # Check the NFS type and NFS size settings
            nfs_all_zone = list(ext_info["NFS zone"])
            nfs_all_type = list(ext_info["NFS"].keys())
            for k,v in config_param["NFS"]["NFS zone"].items():
                # Verify that the specified zone is a zone where NFS can be installed
                if(k not in nfs_all_zone):
                    logger.error("ConfigError: NFS cannot be installed on " + str(k))
                    _ = printout("ConfigError: NFS cannot be installed on " + str(k), info_type = 0, info_list = info_list, fp = fp)
                    config_param = redefine_config(ext_info, info_list = info_list, fp = fp)
                    return config_param
                
                # Check the NFS type settings
                if(v["NFS type"] not in nfs_all_type):
                    logger.error("ConfigError: NFS type should be select from " + ", ".join(nfs_all_type))
                    _ = printout("ConfigError: NFS type should be select from " + ", ".join(nfs_all_type), info_type = 0, info_list = info_list, fp = fp)
                    config_param = redefine_config(ext_info, info_list = info_list, fp = fp)
                    return config_param
                
                # Check the NFS size setting
                nfs_all_size_str = list(ext_info["NFS"][v["NFS type"]].keys())
                nfs_all_size_int = [int(nfs_all_size_str[i]) for i in range(len(nfs_all_size_str))]
                if(v["NFS size"] not in nfs_all_size_int):
                    logger.error("ConfigError: NFS size should be select from " + ", ".join(nfs_all_size_str))
                    _ = printout("ConfigError: NFS size should be select from " + ", ".join(nfs_all_size_str), info_type = 0, info_list = info_list, fp = fp)
                    config_param = redefine_config(ext_info, info_list = info_list, fp = fp)
                    return config_param
                
                # Automatic setting if NFSPlan is not set
                if("NFSPlan" not in v):
                    logger.debug("Automatic configuration of nfs")
                    config_param["NFS"]["NFS zone"][k]["NFSPlan"] = ext_info["NFS"][v["NFS type"]][str(v["NFS size"])]
                # If NFSPlan is set, check if it matches the NFS size and type settings
                else:
                    if(v["NFSPlan"] != ext_info["NFS"][v["NFS type"]][str(v["NFS size"])]):
                        logger.error("ConfigError: NFSPlan does not match to NFS type and size. Please confirm NFS info")
                        _ = printout("ConfigError: NFSPlan does not match to NFS type and size. Please confirm NFS info", info_type = 0, info_list = info_list, fp = fp)
                        config_param = redefine_config(ext_info, info_list = info_list, fp = fp)
                        return config_param, 1
    
    # If NFS is not configured
    else:
        config_param["NFS"]["NFS"] = False
        logger.info("Info: NFS is automatically set to " + str(config_param["NFS"]["NFS"]))
        _ = printout("Info: NFS is automatically set to " + str(config_param["NFS"]["NFS"]), info_type = 0, info_list = info_list, fp = fp)
        
    # Check about Zone
    # If the zone is configured
    logger.debug('Checking params of zone')
    if("Zone" in config_param):
        
        # Get the specified zone
        config_zones = list(set(config_param["Zone"]["Zone"].keys()))
        
        # Check if the zone of the head node is included in the specified zone
        if(config_param["Zone"]["Head Zone"] not in config_zones):
            logger.error("ConfigError: specification of Head Zone is wrong (You should choose Head Zone from " + ",".join(config_zones) + ")")
            _ = printout("ConfigError: specification of Head Zone is wrong (You should choose Head Zone from " + ",".join(config_zones) + ")", info_type = 0, info_list = info_list, fp = fp)
            config_param = redefine_config(ext_info, info_list = info_list, fp = fp)
            return config_param
        
        # If the number of zones is more than one
        if(len(config_zones) > 1):
            # Verify that all zones are production zones
            for i in range(len(config_zones)):
                if(ext_info["Zone"][config_zones[i]]["Type"] != "practice"):
                    logger.error("ConfigError: " + config_zones[i] + " is test zone (Multiple zones must be selected from the practice zones)")
                    _ = printout("ConfigError: " + config_zones[i] + " is test zone (Multiple zones must be selected from the practice zones)", info_type = 0, info_list = info_list, fp = fp)
                    config_param = redefine_config(ext_info, info_list = info_list, fp = fp)
                    return config_param
        
        
        # Verify that the number of compute nodes in each zone is within the range
        # Get the total number of compute nodes
        node_sum = 0
        for i in range(len(config_zones)):
            # Check if the number of compute nodes is greater than or equal to the minimum value
            # For a zone with a head node, maximum-1 or higher
            if(config_zones[i] == config_param["Zone"]["Head Zone"]):
                max_node = ext_info["Zone"][config_zones[i]]["maximum"] - 1
            # For zones with no head node, maximum or greater
            else:
                max_node = ext_info["Zone"][config_zones[i]]["maximum"]
                
            # Check if the number of compute nodes is below the maximum value
            min_node = ext_info["Zone"][config_zones[i]]["minimum"]
            nodes = config_param["Zone"]["Zone"][config_zones[i]]
            if(min_node > nodes or nodes > max_node):
                logger.error("ConfigError: number of compute nodes in " + config_zones[i] + " must be set from " + str(min_node) + " to " + str(max_node))
                _ = printout("ConfigError: number of compute nodes in " + config_zones[i] + " must be set from " + str(min_node) + " to " + str(max_node), info_type = 0, info_list = info_list, fp = fp)
                config_param = redefine_config(ext_info, info_list = info_list, fp = fp)
                return config_param
            
            # Get the total number of compute nodes in each zone
            node_sum += nodes
            
        # Verify that the total number of compute nodes in each zone matches the number of compute nodes in the compute configuration
        if(config_param["Compute"]["Compute number"] != node_sum):
            logger.error("ConfigError: number of compute nodes in Zone params does not match to that in Compute params")
            _ = printout("ConfigError: number of compute nodes in Zone params does not match to that in Compute params", info_type = 0, info_list = info_list, fp = fp)
            config_param = redefine_config(ext_info, info_list = info_list, fp = fp)
            return config_param
    
    # If the zone is not configured
    else:
        # Get the zone with the maximum number of nodes that can be installed in the production zone and the maximum number of nodes
        max_zone_node = 0
        for k,v in ext_info["Zone"].items():
            if(max_zone_node < v["maximum"]-1 and v["Type"] == "practice"):
                max_zone_node = v["maximum"]-1
                max_zone = k
        
        # Verify that the number of nodes configured for Compute is the number of zones that can be installed in a single zone
        if(max_zone_node < config_param["Compute"]["Compute number"]):
            logger.error("ConfigError: specified number of compute nodes (" + str(config_param["Compute"]["Compute number"]) + ") must be lower than " + str(max_zone_node))
            _ = printout("ConfigError: specified number of compute nodes (" + str(config_param["Compute"]["Compute number"]) + ") must be lower than " + str(max_zone_node), info_type = 0, info_list = info_list, fp = fp)
            config_param = redefine_config(ext_info, info_list = info_list, fp = fp)
            return config_param
        else:
            config_param["Zone"] = {}
            config_param["Zone"]["Zone"] = {}
            config_param["Zone"]["Zone"][max_zone] = config_param["Compute"]["Compute number"]
            config_param["Zone"]["Head Zone"] = max_zone
            logger.info("Info: Zone and Head Zone is automatically set to " + str(max_zone))
            _ = printout("Info: Zone and Head Zone is automatically set to " + str(max_zone), info_type = 0, info_list = info_list, fp = fp)
    
    # Monitor
    # Whether Monitor is set or not
    logger.debug('Checking params of monitor')
    if("Monitor" in config_param):
        # When using Monitor
        if(config_param["Monitor"]["Monitor"] == True):
            # Check if the Monitor type is specified
            if("Monitor type" not in config_param["Monitor"]):
                logger.error("ConfigError: monitor type must be specified")
                _ = printout("ConfigError: monitor type must be specified", info_type = 0, info_list = info_list, fp = fp)
                config_param = redefine_config(ext_info, info_list = info_list, fp = fp)
                return config_param
            
            # Check if the monitor level is specified
            if("Monitor level" not in config_param["Monitor"]):
                logger.error("ConfigError: monitor level must be specified")
                _ = printout("ConfigError: monitor level must be specified", info_type = 0, info_list = info_list, fp = fp)
                config_param = redefine_config(ext_info, info_list = info_list, fp = fp)
                return config_param
            
            # Check the Monitor method specification
            opt_list = list(ext_info["Monitor"].keys())
            if(config_param["Monitor"]["Monitor type"] not in opt_list):
                logger.error("ConfigError: monitor method must be select from " + ",".join(opt_list))
                _ = printout("ConfigError: monitor method must be select from " + ",".join(opt_list), info_type = 0, info_list = info_list, fp = fp)
                config_param = redefine_config(ext_info, info_list = info_list, fp = fp)
                return config_param
            
            # Check the Monitor level specification
            opt_list = list(ext_info["Monitor_level"]["level"])
            if(config_param["Monitor"]["Monitor level"] not in opt_list):
                logger.error("ConfigError: monitor level must be select a value between " + str(min(opt_list)) + " and " + str(max(opt_list)))
                _ = printout("ConfigError: monitor level must be select a value between " + str(min(opt_list)) + " and " + str(max(opt_list)), info_type = 0, info_list = info_list, fp = fp)
                config_param = redefine_config(ext_info, info_list = info_list, fp = fp)
                return config_param
    # If Monitor is not set, specify it automatically
    else:
        config_param["Monitor"] = {}
        config_param["Monitor"]["Monitor"] = False
        logger.info("Info: monitor is automatically set to " + str(config_param["Monitor"]["Monitor"]))
        _ = printout("Info: monitor is automatically set to " + str(config_param["Monitor"]["Monitor"]), info_type = 0, info_list = info_list, fp = fp)
    
    
    # Compute
    logger.debug('Checking params of Compute')
    zone_list = config_param["Zone"]["Zone"]
    config_param_temp, index = server_val(config_param["Compute"]["Compute node"], ext_info, zone_list, info_list = [1,0,0,0], fp = "")
    if(index == 1):
        return config_param_temp
    else:
        config_param["Compute"]["Compute node"] = config_param_temp
        
    # Automatic configuration of Compute switch
    if("Compute switch" not in config_param["Compute"]):
        config_param["Compute"]["Compute switch"] == False
        
    # Check if compute switch is not specified when the number of compute nodes is 1
    if(config_param["Compute"]["Compute number"] == 1 and config_param["Compute"]["Compute switch"] == True):
        logger.error("ConfigError: compute switch cannot be specify if the number of compute nodes is 1")
        _ = printout("ConfigError: compute switch cannot be specify if the number of compute nodes is 1", info_type = 0, info_list = info_list, fp = fp)
        config_param = redefine_config(ext_info, info_list = info_list, fp = fp)
        return config_param
    
    logger.debug('Checking params of Head')
    # Head
    config_param_temp, index = server_val(config_param["Head"], ext_info, zone_list, info_list = [1,0,0,0], fp = "")
    if(index == 1):
        return config_param_temp
    else:
        config_param["Head"] = config_param_temp
    
        
    return config_param
        
    
    
    
def server_val(config_param, ext_info, zone_list, info_list = [1,0,0,0], fp = ""):
    opt_list_str = list(ext_info["Server"].keys())
    opt_list = [int(opt_list_str[i]) for i in range(len(opt_list_str))]
    if(config_param["Node"]["core"] not in opt_list):
        logger.error("ConfigError: server core must be select from " + ",".join(opt_list_str))
        _ = printout("ConfigError: server core must be select from " + ",".join(opt_list_str), info_type = 0, info_list = info_list, fp = fp)
        config_param = redefine_config(ext_info, info_list = info_list, fp = fp)
        return config_param, 1
    
    # Check if the memory number is selected from the candidate values
    opt_list_str = list(ext_info["Server"][str(config_param["Node"]["core"])].keys())
    opt_list = [int(opt_list_str[i]) for i in range(len(opt_list_str))]
    if(config_param["Node"]["memory"] not in opt_list):
        logger.error("ConfigError: server memory must be select from " + ",".join(opt_list_str))
        _ = printout("ConfigError: server memory must be select from " + ",".join(opt_list_str), info_type = 0, info_list = info_list, fp = fp)
        config_param = redefine_config(ext_info, info_list = info_list, fp = fp)
        return config_param, 1
    
    # If the node PlanID is not set, specify it from the number of memory and core
    if("NodePlan" not in config_param["Node"]):
        config_param["Node"]["NodePlan"] = ext_info["Server"][str(config_param["Node"]["core"])][str(config_param["Node"]["memory"])]
    
    # Check if the Disk type is selected from the candidate values
    opt_list = list(ext_info["Disk"].keys())
    if(config_param["Disk"]["Type"] not in opt_list):
        logger.error("ConfigError: disk type must be select from " + ",".join(opt_list))
        _ = printout("ConfigError: disk type must be select from " + ",".join(opt_list), info_type = 0, info_list = info_list, fp = fp)
        config_param = redefine_config(ext_info, info_list = info_list, fp = fp)
        return config_param, 1
        
    # Check if Disk Size is selected from the candidate values.
    opt_list = ext_info["Disk"][config_param["Disk"]["Type"]]
    opt_list_str = [str(opt_list[i]) for i in range(len(opt_list))]
    if(config_param["Disk"]["Size"] not in opt_list):
        logger.error("ConfigError: disk size must be select from " + ",".join(opt_list_str))
        _ = printout("ConfigError: disk size must be select from " + ",".join(opt_list_str), info_type = 0, info_list = info_list, fp = fp)
        config_param = redefine_config(ext_info, info_list = info_list, fp = fp)
        return config_param, 1
    
    # Check if the Connection type is selected from the candidate values
    opt_list = ext_info["Connection"]
    if(config_param["Connection type"] not in opt_list):
        logger.error("ConfigError: connection type must be select from " + ",".join(opt_list))
        _ = printout("ConfigError: connection type must be select from " + ",".join(opt_list), info_type = 0, info_list = info_list, fp = fp)
        config_param = redefine_config(ext_info, info_list = info_list, fp = fp)
        return config_param, 1
    
    # Check if the OS is selected from the candidate values
    opt_list = list(ext_info["OS"].keys())
    if(config_param["OS"]["name"] not in opt_list):
        logger.error("ConfigError: os must be select from " + ",".join(opt_list))
        _ = printout("ConfigError: os must be select from " + ",".join(opt_list), info_type = 0, info_list = info_list, fp = fp)
        config_param = redefine_config(ext_info, info_list = info_list, fp = fp)
        return config_param, 1
        
    # If OSPlan is not set, set it automatically
    if("OSPlan" not in config_param["OS"].keys()):
        config_param["OS"]["OSPlan"] = {}
        for zone in zone_list:
            config_param["OS"]["OSPlan"][zone] = ext_info["OS"][config_param["OS"]["name"]][zone]
    # If it is set, check if it matches the OS name
    else:
        for zone in zone_list:
            if(zone in config_param["OS"]["OSPlan"]):
                if(ext_info["OS"][config_param["OS"]["name"]][zone] != config_param["OS"]["OSPlan"][zone]):
                    logger.error("ConfigError: OSPlan does not match to OS. Please confirm os info")
                    _ = printout("ConfigError: OSPlan does not match to OS. Please confirm os info", info_type = 0, info_list = info_list, fp = fp)
                    config_param = redefine_config(ext_info, info_list = info_list, fp = fp)
                    return config_param, 1
        
            else:
                config_param["OS"]["OSPlan"][zone] = ext_info["OS"][config_param["OS"]["name"]][zone]
    
    return config_param, 0
    
    
# Validate config parameters
def config_validation(ext_info, config_param, info_list = [1,0,0,0], fp = ""):
    logger.debug('load config checker')
    checker = load_config_checker(info_list = info_list, fp = fp)
    all_zone = list(ext_info["Zone"].keys())
    main_checker = checker["main checker"]
    
    main_checker["properties"]["NFS"]["properties"]["NFS zone"]["properties"] = dict(zip(all_zone, [checker["NFS_zone_checker"] for i in range(len(all_zone))]))
    main_checker["properties"]["Zone"]["properties"]["Zone"]["properties"] = dict(zip(all_zone, [checker["Zone_checker"] for i in range(len(all_zone))]))
    main_checker["properties"]["Compute"]["properties"]["Compute node"]["properties"]["OS"]["properties"]["OSPlan"]["properties"] = dict(zip(all_zone, [checker["OS_checker"] for i in range(len(all_zone))]))
    main_checker["properties"]["Head"]["properties"]["OS"]["properties"]["OSPlan"]["properties"] = dict(zip(all_zone, [checker["OS_checker"] for i in range(len(all_zone))]))
    
    try:
        logger.debug('Checking config params')
        _ = printout("Checking config params ...", info_type = 0, info_list = info_list, fp = fp)
        logger.debug('Checking the type and existence of config params')
        validate(config_param, main_checker)
        logger.debug('Checking details of config params')
        checking_config_details(ext_info, config_param, info_list = info_list, fp = fp)
        
        
    except ValidationError as e:
        logger.error('ConfigError: definition of config parameters is wrong')
        logger.error(e.message)
        
        _ = printout("ConfigError: definition of config parameters is wrong", info_type = 0, info_list = info_list, fp = fp)
        _ = printout(e.message, info_type = 0, info_list = info_list, fp = fp)
        
        config_param = redefine_config(ext_info, info_list = info_list, fp = fp)
    
    return config_param

