
import os
os.chdir(os.path.dirname(os.path.abspath(__file__)))
common_path = os.path.abspath("../../..")
import sys
sys.path.append(common_path + "/lib/auth")
from auth_func_pro import authentication_cli
import stop_class
import logging
sys.path.append(common_path + "/lib/others")
import get_params
import get_cluster_id
from info_print import printout
sys.path.append(common_path + "/lib/def_conf")
from load_external_data import external_data

logger = logging.getLogger("sacluster").getChild(os.path.basename(__file__))

def stop_main(api_index, f, info_list,max_workers):
    logger.debug('Setting authentication info')
    auth_info = authentication_cli(fp = f, info_list  = info_list, api_index = api_index)
    
    logger.debug('loading external data')
    ext_info = external_data(auth_info, info_list = info_list, fp = f)
    
    logger.debug('Getting cluster information')
    params = get_params.get_params(ext_info, auth_info, info_list = info_list, f = f, api_index = api_index)
    params()
    params.show_cluster_info()
    
    index, cluster_id = get_cluster_id.get_cluster_id(params.cluster_info_all, info_list, f, api_index)
    
    if(index == True):
        logger.debug("Start stopping the cluster : " + str(cluster_id))
        printout("Start stopping the cluster : " + str(cluster_id), info_type = 0, info_list = info_list, fp = f)
        stop_obj = stop_class.stop_sacluster(params.cluster_info_all[cluster_id], auth_info, max_workers,fp = f, info_list = info_list, api_index = api_index)
        stop_obj()
        logger.debug("Finished stopping the cluster : " + str(cluster_id))
        printout("Finished stopping the cluster : " + str(cluster_id), info_type = 0, info_list = info_list, fp = f)
        
    else:
        logger.debug('There are no clusters to stop')
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        