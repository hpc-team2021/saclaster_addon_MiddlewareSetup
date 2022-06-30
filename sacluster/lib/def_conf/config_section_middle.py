
import os
os.chdir(os.path.dirname(os.path.abspath(__file__)))
path = os.path.abspath("../..")

import os
import sys
import json
from config_function import set_parm, conf_pattern_main, conf_pattern_1, conf_pattern_2, conf_pattern_3, conf_pattern_4, conf_pattern_5
sys.path.append(path + "/lib/others")
from API_method import get, post, put
from info_print import printout
import base64
import requests
import datetime
from load_external_data import external_data
import pandas as pd
import logging
logger = logging.getLogger("sacluster").getChild(os.path.basename(__file__))

#Config内容名を指定
def def_config_name(fp = "", info_list = [1,0,0,0]):
    logger.debug('Start to define config name')
    while(True):
        config_name = conf_pattern_1("Config name (Within 20 characters, default:config params)", info_list = info_list, fp = fp)
        if(config_name == ""):
            logger.debug('automatically config name is set to config prams')
            return "config params"
        elif(len(config_name) <= 20):
            logger.debug('config name is set')
            return config_name
        else:
            logger.debug('Character count over')
            printout("Warning: Please specify up to 20 characters.", info_type = 0, info_list = info_list, fp = fp)

def setting_monitor(ext_info, all_params, set_list, fp = "", info_list = [1,0,0,0]):
    param = {}
    logger.debug('start setting of Monitor')
    param["index"] = [False, True][conf_pattern_3("Monitor", ["False","True"], "False", info_list = info_list, fp = fp)]
    set_parm("Monitor", str(param["index"]), info_list = info_list, fp = fp)

    if(param["index"] == True):
        logger.debug('Monitor has been enabled')
        param["params"] = {}
        
        logger.debug('setting monitor type')
        candidate = list(ext_info["Monitor"].keys())
        param["type"] = candidate[conf_pattern_3("Monitor type", candidate, candidate[0], info_list = info_list, fp = fp)]
        set_parm("Monitor type", param["type"], info_list = info_list, fp = fp)
        
    all_params["Monitor"] = param
    set_list.loc["Monitor"] = ["Monitor".ljust(20), "already".ljust(7), "not-required".ljust(12)]

    return all_params, set_list

def setting_scheduler(ext_info, all_params, set_list, fp = "", info_list = [1,0,0,0]):
    param = {}
    logger.debug('start setting of Scheduler')
    param["index"] = [False, True][conf_pattern_3("Scheduler", ["False","True"], "False", info_list = info_list, fp = fp)]
    set_parm("Scheduler", str(param["index"]), info_list = info_list, fp = fp)

    if(param["index"] == True):
        logger.debug('Scheduler has been enabled')
        param["params"] = {}
        
        logger.debug('setting scheduler type')
        candidate = list(ext_info["Scheduler"].keys())
        param["type"] = candidate[conf_pattern_3("Scheduler type", candidate, candidate[0], info_list = info_list, fp = fp)]
        set_parm("Scheduler type", param["type"], info_list = info_list, fp = fp)
        
    all_params["Job_scheduler"] = param
    set_list.loc["Scheduler"] = ["Scheduler".ljust(20), "already".ljust(7), "not-required".ljust(12)]

    return all_params, set_list

def setting_parallelcomputing(ext_info, all_params, set_list, fp = "", info_list = [1,0,0,0]):
    param = {}
    logger.debug('start setting of ParallelComputing')
    param["index"] = [False, True][conf_pattern_3("ParallelComputing", ["False","True"], "False", info_list = info_list, fp = fp)]
    set_parm("ParallelComputing", str(param["index"]), info_list = info_list, fp = fp)

    if(param["index"] == True):
        logger.debug('ParallelComputing has been enabled')
        param["params"] = {}
        
        logger.debug('setting parallelComputing type')
        candidate = list(ext_info["ParallelComputing"].keys())
        param["type"] = candidate[conf_pattern_3("ParallelComputing type", candidate, candidate[0], info_list = info_list, fp = fp)]
        set_parm("ParallelComputing type", param["type"], info_list = info_list, fp = fp)
        
    all_params["ParallelComputing"] = param
    set_list.loc["ParallelComputing"] = ["ParallelComputing".ljust(20), "already".ljust(7), "not-required".ljust(12)]

    return all_params, set_list

                
def show_current_state(ext_info, all_params, set_list, fp = "", info_list = [1,0,0,0]):
    logger.debug('show current config setting')
    printout("", info_type = 0, info_list = info_list, fp = fp)
    
    printout("Current parameters========================", info_type = 0, info_list = info_list, fp = fp)
    printout("[[Monitor]]", info_type = 0, info_list = info_list, fp = fp)
    if("Monitor" in all_params):
        printout("{} : {}".format("Setting".ljust(32), all_params["Monitor"]["index"]), info_type = 0, info_list = info_list, fp = fp)
        if(all_params["Monitor"]["index"] == True):
            printout("{} : {}".format("Type".ljust(32), all_params["Monitor"]["type"]), info_type = 0, info_list = info_list, fp = fp)
        #else:
            #printout("Not set up", info_type = 0, info_list = info_list, fp = fp)
    else:
        printout("Not set up", info_type = 0, info_list = info_list, fp = fp)
    
    printout("", info_type = 0, info_list = info_list, fp = fp)
    printout("[[Scheduler]]", info_type = 0, info_list = info_list, fp = fp)
    if("Job_scheduler" in all_params):
        printout("{} : {}".format("Setting".ljust(32), all_params["Job_scheduler"]["index"]), info_type = 0, info_list = info_list, fp = fp)
        if(all_params["Job_scheduler"]["index"] == True):
            printout("{} : {}".format("Type".ljust(32), all_params["Job_scheduler"]["type"]), info_type = 0, info_list = info_list, fp = fp)
        #else:
            #printout("Not set up", info_type = 0, info_list = info_list, fp = fp)
    else:
        printout("Not set up", info_type = 0, info_list = info_list, fp = fp)
    
    printout("", info_type = 0, info_list = info_list, fp = fp)
    printout("[[ParallelComputing]]", info_type = 0, info_list = info_list, fp = fp)
    if("ParallelComputing" in all_params):
        printout("{} : {}".format("Setting".ljust(32), all_params["ParallelComputing"]["index"]), info_type = 0, info_list = info_list, fp = fp)
        if(all_params["ParallelComputing"]["index"] == True):
            printout("{} : {}".format("Type".ljust(32), all_params["ParallelComputing"]["type"]), info_type = 0, info_list = info_list, fp = fp)
        #else:
            #printout("Not set up", info_type = 0, info_list = info_list, fp = fp)
    else:
        printout("Not set up", info_type = 0, info_list = info_list, fp = fp)
        
    printout("", info_type = 0, info_list = info_list, fp = fp)
    return all_params, set_list
    







































































