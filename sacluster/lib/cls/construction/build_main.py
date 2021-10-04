
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

def build_main(in_path, out_path, make_dir_index, api_index, f, info_list, auto_start, max_workers):
    logger.debug('Setting authentication info')
    auth_info = authentication_cli(fp = f, info_list  = info_list, api_index = api_index)
    
    logger.debug('loading external data')
    ext_info = external_data(auth_info, info_list = info_list, fp = f)
    
    logger.debug('Checking cloud states')
    ext_info = check_cloud_state(ext_info, auth_info, info_list = info_list, fp = f, api_index = api_index, func_type = "build")
    
    logger.debug('Start the process related to the config file')
    config_param = config_main(ext_info, in_path = in_path, out_path = out_path, make_dir_index = make_dir_index, info_list = info_list, fp = f)

    logger.debug('Start configuring the application')
    config_param = set_app_params(config_param, api_index = api_index, f = f, info_list = info_list)

    logger.debug('Convert config params into a format for building')
    build_params = config_transformation(ext_info, config_param, api_index = api_index, f = f, info_list = info_list)

    logger.debug('Preparing monitor info')
    info_list_cluster = preparing_monitor(ext_info, config_param, api_index = api_index, f = f, info_list = info_list)
    
    logger.debug('Starting main function to build')
    cls_bil = build_class.build_sacluster(build_params, auth_info, max_workers, fp = f , info_list = info_list, monitor_info_list = info_list_cluster, api_index = api_index)
    cls_bil()
    
    if(auto_start == True):
        str_cls = start_sacluster(cls_bil.all_id_dict, auth_info, fp = f, info_list = info_list, api_index = api_index)
        str_cls()
    
    #main(build_params, auth_info, fp = f , info_list = info_list, monitor_info_list = info_list_cluster, api_index = api_index)
    #logger.debug('Start building the cluster')
    #main(build_params, auth_info = auth_info, fp = f , info_list = info_list, api_index = api_index)















































