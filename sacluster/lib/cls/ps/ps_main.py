

import os
os.chdir(os.path.dirname(os.path.abspath(__file__)))
common_path = os.path.abspath("../../..")

import sys
sys.path.append(common_path + "/lib/auth")
from auth_func_pro import authentication_cli

sys.path.append(common_path + "/lib/def_conf")
from load_external_data import external_data
from check_cloud_state import check_cloud_state

sys.path.append(common_path + "/lib/others")
import get_params

import logging

logger = logging.getLogger("sacluster").getChild(os.path.basename(__file__))
#logger = logging.getLogger().getChild(os.path.basename(__file__))

def ps_main(api_index, f, info_list):
    logger.debug('Setting authentication info')
    auth_info = authentication_cli(fp = f, info_list  = info_list, api_index = api_index)
    
    logger.debug('loading external data')
    ext_info = external_data(auth_info, info_list = info_list, fp = f)
    
    logger.debug('Checking cloud states')
    ext_info = check_cloud_state(ext_info, auth_info, info_list = info_list, fp = f, api_index = api_index)
    
    logger.debug('Getting cluster information')
    params = get_params.get_params(ext_info, auth_info, info_list = info_list, f = f, api_index = api_index)
    params()
    params.show_cluster_info()
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    