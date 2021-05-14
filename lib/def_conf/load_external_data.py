#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Nov 24 17:03:36 2020

@author: tsukiyamashou
"""

import os
os.chdir(os.path.dirname(os.path.abspath(__file__)))
path = os.path.abspath("../..")
import sys
import json
sys.path.append(path + "/lib/others")
from API_method import get, post, put
from info_print import printout
import base64
import requests
import datetime
import logging

logger = logging.getLogger("sacluster").getChild(os.path.basename(__file__))
    
# loading external data 
def external_data(auth_info, info_list = [1,0,0,0], fp = ""):
    
    _ = printout("loading external information ...", info_type = 0, info_list = info_list, fp = fp)
    logger.debug('loading external information')
    
    # Load the External_info.json file              
    try:
        with open(path + "/lib/.Ex_info/External_info.json", "r") as f:
            data = json.load(f)
    
    except FileNotFoundError as e:
        _ = printout("EnvironmentalError: External_info.json does not exist under sacluster/lib/.Ex_info", info_type = 0, info_list = info_list, fp = fp)
        logger.critical('EnvironmentalError: External_info.json does not exist under sacluster/lib/.Ex_info')
        sys.exit()
    
    return data

















































