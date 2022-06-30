
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
        with open(path + "/lib/.Ex_info/config_checker_middle.json", "r") as f:
            data = json.load(f)
    
    except FileNotFoundError as e:
        _ = printout("EnvironmentalError: config_checker.json does not exist under sacluster/lib/.Ex_info\nYou should install sacluster from url", info_type = 0, info_list = info_list, fp = fp)
        sys.exit()
        
    return data

#再定義するかどうかの確認（再定義しない場合は強制終了）
def redefine_config(ext_info, info_list = [1,0,0,0], fp = ""):
    while(True):
        res = printout("Do you want to redefine new config params (yes or no) >>", info_type = 1, info_list = info_list, fp = fp)
        if(res == "yes" or res == "no" or res == "y" or res == "n"):
            break
        else:
            res = printout("Warning: Please select yes (y) or no (n).", info_type = 0, info_list = info_list, fp = fp)
    
    if(res == "yes" or res == "y"):
        out_path = printout("Output path >>", info_type = 1, info_list = info_list, fp = fp)
        config_param = config_making_main(ext_info, out_path = out_path, info_list = info_list, fp = fp, m_index = True)
        return config_param
    else:
        _ = printout("ConfigError: config params cannot be loaded.", info_type = 0, info_list = info_list, fp = fp)
        sys.exit()
        
def checking_config_details(ext_info, config_param, info_list = [1,0,0,0], fp = ""):
    base_checker = [["Moniter", "Moniter"], ["Job_scheduler", "Scheduler"], ["ParallelComputing", "ParallelComputing"]]
    
    for param_key, ext_param in base_checker:
        if(config_param[param_key]["index"] == True):
            if("type" not in config_param[param_key]):
                logger.error("ConfigError: If {} is True, setting of the {} type is needed".format(param_key + " index", param_key + " type"))
                _ = printout("ConfigError: If {} is True, setting of the {} type is needed".format(param_key + " index", param_key + " type"), info_type = 0, info_list = info_list, fp = fp)
                config_param = redefine_config(ext_info, info_list = info_list, fp = fp)
                if(config_param[param_key]["type"] not in list(ext_info[ext_param].keys())):
                    logger.error("ConfigError: {} should be selected from ".format(param_key + " type") + ", ".join(list(ext_info[ext_param].keys())))
                    _ = printout("ConfigError: {} should be selected from ".format(param_key + " type") + ", ".join(list(ext_info[ext_param].keys())), info_type = 0, info_list = info_list, fp = fp)
                    config_param = redefine_config(ext_info, info_list = info_list, fp = fp)
            
    return config_param
        

def config_validation_middle(ext_info, config_param, info_list = [1,0,0,0], fp = ""):
    logger.debug('load config checker')
    checker = load_config_checker(info_list = info_list, fp = fp)
    main_checker = checker["main checker"]
    
    try:
        logger.debug('Checking config params (middle ware)')
        _ = printout("Checking config params (middle ware)...", info_type = 0, info_list = info_list, fp = fp)
        logger.debug('Checking the type and existence of config params (middle ware)')
        validate(config_param, main_checker)
        logger.debug('Checking details of config params')
        #checking_config_details(ext_info, config_param, info_list = info_list, fp = fp)
        
    except ValidationError as e:
        logger.error('ConfigError: definition of config parameters is wrong')
        logger.error(e.message)
        
        _ = printout("ConfigError: definition of config parameters is wrong", info_type = 0, info_list = info_list, fp = fp)
        _ = printout(e.message, info_type = 0, info_list = info_list, fp = fp)
        
        config_param = redefine_config(ext_info, info_list = info_list, fp = fp)
    
    return config_param







































