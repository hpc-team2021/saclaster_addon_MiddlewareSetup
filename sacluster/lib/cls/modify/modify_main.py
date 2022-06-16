

import os
os.chdir(os.path.dirname(os.path.abspath(__file__)))
common_path = os.path.abspath("../../..")

import sys
sys.path.append(common_path + "/lib/auth")
from auth_func_pro import authentication_cli

sys.path.append(common_path + "/lib/def_conf")
from load_external_data import external_data
from check_cloud_state import check_cloud_state

sys.path.append(common_path + "/lib/cls/stop")
from stop_class import stop_sacluster

sys.path.append(common_path + "/lib/cls/modify")
from modify_class import modify_sacluster

sys.path.append(common_path + "/lib/notif")
from monitor_function import preparing_monitor

sys.path.append(common_path + "/lib/cls/ip_setting")
from setting_middleware import set_startup_scripts
from subtract_ip_cluster_info import subtract_cluster_info



sys.path.append(common_path + "/lib/others")
import get_params
import get_cluster_id
from info_print import printout
from confirm_stop_pros import conf_stop_process

import build_class
import logging
import copy
import pprint

logger = logging.getLogger("sacluster").getChild(os.path.basename(__file__))
#logger = logging.getLogger().getChild(os.path.basename(__file__))

def modify_main(api_index, f, info_list, max_workers):
    logger.debug('Setting authentication info')
    auth_info = authentication_cli(fp = f, info_list  = info_list, api_index = api_index)
    
    logger.debug('loading external data')
    ext_info = external_data(auth_info, info_list = info_list, fp = f)
    
    logger.debug('Checking cloud states')
    ext_info = check_cloud_state(ext_info, auth_info, info_list = info_list, fp = f, api_index = api_index)
    
    logger.debug('Getting cluster information')
    params = get_params.get_params(ext_info, auth_info, info_list = info_list, f = f, api_index = api_index)
    params()
    
    #import pprint
    #pprint.pprint(params.cluster_info_all)
    #sys.exit()
    
    params.show_cluster_info()
    
    index, cluster_id = get_cluster_id.get_cluster_id(params.cluster_info_all, info_list, f, api_index)
    
    state, obj = params.checking_status(cluster_id)
    if(state == False):
        conf_stop_process(info_list, f)
        
        logger.debug("Start stopping the cluster : " + str(cluster_id))
        printout("Start stopping the cluster : " + str(cluster_id), info_type = 0, info_list = info_list, fp = f)
        stop_obj = stop_sacluster(params.cluster_info_all[cluster_id], auth_info, max_workers, fp = f, info_list = info_list, api_index = api_index)
        stop_obj()
        logger.debug("Finished stopping the cluster : " + str(cluster_id))
        printout("Finished stopping the cluster : " + str(cluster_id), info_type = 0, info_list = info_list, fp = f)
        
    
    if(index == True):
        cluster_info_prior = copy.deepcopy(params.cluster_info_all[cluster_id])
        
        logger.debug("Starting to modify the cluster : " + str(cluster_id))
        printout("Starting to modify the cluster : " + str(cluster_id), info_type = 0, info_list = info_list, fp = f)
        mod_obj = modify_sacluster(params.cluster_info_all[cluster_id], cluster_id, auth_info, ext_info, fp = f, info_list = info_list, api_index = api_index, max_workers =max_workers)
        mod_obj()
        
        cluster_info_new = mod_obj.cluster_info
        cluster_info_ip = subtract_cluster_info(cluster_info_prior, cluster_info_new)
        
        cls_mid = set_startup_scripts(cluster_id = cluster_id, cluster_info = cluster_info_ip, ext_info = ext_info, auth_res = auth_info, m_index = True, fp = f , info_list = info_list, api_index = api_index)
        cls_mid()
        
        
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    