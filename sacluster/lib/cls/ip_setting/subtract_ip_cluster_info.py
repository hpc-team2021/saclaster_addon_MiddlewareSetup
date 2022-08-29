#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jun  9 10:13:18 2022

@author: kurata
"""

import os
os.chdir(os.path.dirname(os.path.abspath(__file__)))
common_path = os.path.abspath("../../..")

import copy


def subtract_cluster_info(cluster_info, cluster_info_new):
    cluster_info_temp = copy.deepcopy(cluster_info_new)
    zone_list = list(cluster_info["clusterparams"]["server"].keys())
    
    for zone in zone_list:
        if(len(cluster_info_temp["clusterparams"]["server"][zone]["compute"].keys()) > len(cluster_info["clusterparams"]["server"][zone]["compute"].keys())):
            for i in list(cluster_info["clusterparams"]["server"][zone]["compute"].keys()):
                cluster_info_temp["clusterparams"]["server"][zone]["compute"].pop(i)
        
        else:
            cluster_info_temp["clusterparams"]["server"][zone]["compute"] = {}
                
    return cluster_info_temp
        



























































