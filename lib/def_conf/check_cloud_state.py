#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jan 28 15:13:58 2021

@author: tsukiyamashou
"""

import os
os.chdir(os.path.dirname(os.path.abspath(__file__)))
path = os.path.abspath("../../..")

import sys
sys.path.append(path + "/lib/others")
from API_method import get
sys.path.append(path + "/lib/cls/construction")
import logging

logger = logging.getLogger("sacluster").getChild(os.path.basename(__file__))

# Checking cloud states
def check_cloud_state(ext_info, auth_info, info_list = [1,0,0,0], fp = "", api_index = True):
    if(api_index == True):
        all_zone = list(ext_info["Zone"].keys())
        for zone in all_zone:
            logger.debug('Checking the state in ' + zone)
            url = "https://secure.sakura.ad.jp/cloud/zone/"+ zone +"/api/cloud/1.1"
            while(True):
                exist_server_all = get(url + "/server", auth_info)
                if ("is_ok" in exist_server_all.keys()):
                    if exist_server_all["is_ok"] == True:
                        break
                
            logger.debug('Calculating the number of nodes that can be installed in ' + zone)
            exist_server_all = exist_server_all["Count"]
            ext_info["Zone"][zone]["maximum"] = ext_info["Zone"][zone]["maximum"] - exist_server_all
            
            if(ext_info["Zone"][zone]["maximum"] <= ext_info["Zone"][zone]["minimum"]):
                logger.info("nodes cannot install in " + zone)
                logger.info(zone + " was deleted from external info")
                ext_info["Zone"].pop(zone)
            
        return ext_info
        
    else:
        return ext_info








































