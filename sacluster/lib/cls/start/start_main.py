
import os
os.chdir(os.path.dirname(os.path.abspath(__file__)))
common_path = os.path.abspath("../../..")
import sys
sys.path.append(common_path + "/lib/auth")
from auth_func_pro import authentication_cli
import start_class
import logging
sys.path.append(common_path + "/lib/others")
import get_params
import get_cluster_id
from info_print import printout
sys.path.append(common_path + "/lib/def_conf")
from load_external_data import external_data

logger = logging.getLogger("sacluster").getChild(os.path.basename(__file__))

def start_main(api_index, f, info_list,max_workers, middle_index = False, cluster_id =""):
    logger.debug('Setting authentication info')
    auth_info = authentication_cli(fp = f, info_list  = info_list, api_index = api_index)
    
    logger.debug('loading external data')
    ext_info = external_data(auth_info, info_list = info_list, fp = f)
    
    logger.debug('Getting cluster information')
    params = get_params.get_params(ext_info, auth_info, info_list = info_list, f = f, api_index = api_index)
    params()
        
    if not middle_index:
        params.show_cluster_info()
        index, cluster_id = get_cluster_id.get_cluster_id(params.cluster_info_all, info_list, f, api_index)
    else:
        cluster_id  = cluster_id
        index       = True

    if(index == True):
        logger.debug("Starting up the cluster : " + str(cluster_id))
        printout("Starting up the cluster : " + str(cluster_id), info_type = 0, info_list = info_list, fp = f)
        start_obj = start_class.start_sacluster(params.cluster_info_all[cluster_id], auth_info, max_workers, fp = f, info_list = info_list, api_index = api_index)
        start_obj()
        logger.debug("Finished starting the cluster : " + str(cluster_id))
        printout("Finished starting the cluster : " + str(cluster_id), info_type = 0, info_list = info_list, fp = f)
    else:
        logger.debug('There are no clusters to start')
        
   
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    