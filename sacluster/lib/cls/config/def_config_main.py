
import os
os.chdir(os.path.dirname(os.path.abspath(__file__)))
common_path = os.path.abspath("../../..")

import sys
sys.path.append(common_path + "/lib/auth")
from auth_func_pro import authentication_cli

sys.path.append(common_path + "/lib/def_conf")
from load_external_data import external_data
from check_cloud_state import check_cloud_state
from config_main import config_main

sys.path.append(common_path + "/lib/cls/construction")
from preparing_build_params import set_app_params
from preparing_build_params import config_transformation

sys.path.append(common_path + "/lib/cls/start")
from start_class import start_sacluster

sys.path.append(common_path + "/lib/notif")
from monitor_function import preparing_monitor

import build_class
import logging

logger = logging.getLogger("sacluster").getChild(os.path.basename(__file__))
#logger = logging.getLogger().getChild(os.path.basename(__file__))

def def_config_main(out_path, make_dir_index, api_index, f, info_list):
    logger.debug('Setting authentication info')
    auth_info = authentication_cli(fp = f, info_list  = info_list, api_index = api_index)
    
    logger.debug('loading external data')
    ext_info = external_data(auth_info, info_list = info_list, fp = f)
    
    logger.debug('Checking cloud states')
    ext_info = check_cloud_state(ext_info, auth_info, info_list = info_list, fp = f, api_index = api_index, func_type = "build")
    
    logger.debug('Start the process related to the config file')
    config_param = config_main(ext_info, in_path = "", out_path = out_path, make_dir_index = make_dir_index, info_list = info_list, fp = f)
















































