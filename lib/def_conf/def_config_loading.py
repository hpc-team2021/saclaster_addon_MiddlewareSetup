#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jan  7 14:32:45 2021

@author: kurata
"""

import json
import os
from info_print import printout
from load_external_data import external_data
from config_validation import config_validation
import logging

logger = logging.getLogger("sacluster").getChild(os.path.basename(__file__))

# Loading config parameters
def config_loading_main(ext_info, in_path = "", info_list = [1,0,0,0], fp = ""):
    logger.debug('loading config params')
    _ = printout("loading config params ...", info_list = info_list, fp = fp)
    
    while(True):
        _, ext = os.path.splitext(in_path)
            
        if(os.path.isfile(in_path) == True and (ext == ".json" or ext == ".js")):
            try:
                with open(in_path, 'r') as f:
                    json_f = json.load(f)
                break
                
            except PermissionError as e:
                logger.error('PermissionError: the specified path cannot be accessed')
                _ = printout("PermissionError: the specified path cannot be accessed.", info_type = 0, info_list = info_list, fp = fp)
                logger.debug('request new path')
                in_path = printout("New path >>", info_type = 1, info_list = info_list, fp = fp)
                   
        else:
            logger.error('FileImportError: the file did not load properly')
            _ = printout("FileImportError: config params can not be loaded. Please specify the json file.", info_list = info_list, fp = fp)
            in_path = printout("New path >>", info_type = 1, info_list = info_list, fp = fp)

    logger.debug('Start checking the config param')
    config_param = config_validation(ext_info, json_f, info_list = info_list, fp = fp)

    return config_param































































