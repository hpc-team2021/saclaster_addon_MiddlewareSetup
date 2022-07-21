
import os
os.chdir(os.path.dirname(os.path.abspath(__file__)))
common_path = os.path.abspath("../../..")
import sys
sys.path.append(common_path + "/lib/auth")
from auth_func_pro import authentication_cli

#import stop_class
import delete_class
import logging
sys.path.append(common_path + "/lib/cls/stop")
from stop_class import stop_sacluster
sys.path.append(common_path + "/lib/others")
import get_params
import get_cluster_id
from info_print import printout
from confirm_stop_pros import conf_stop_process
sys.path.append(common_path + "/lib/def_conf")
from load_external_data import external_data
from config_function import conf_pattern_2
sys.path.append(common_path + "/lib/addon/delete")
from delete_middle_main import delete_middle_main


logger = logging.getLogger("sacluster").getChild(os.path.basename(__file__))

def delete_main(api_index, f, info_list,max_workers):
    logger.debug('Setting authentication info')
    auth_info = authentication_cli(fp = f, info_list  = info_list, api_index = api_index)
    
    logger.debug('loading external data')
    ext_info = external_data(auth_info, info_list = info_list, fp = f)
    
    logger.debug('Getting cluster information')
    params = get_params.get_params(ext_info, auth_info, info_list = info_list, f = f, api_index = api_index)
    params()
    params.show_cluster_info()
    
    index, cluster_id = get_cluster_id.get_cluster_id(params.cluster_info_all, info_list, f, api_index)
    
    temp = conf_pattern_2("Delete the selected cluster?", ["yes", "no"], "no", info_list = info_list, fp = f)
    
    
    state, obj = params.checking_status(cluster_id)
    
    if temp == "yes":
        if(state == False):
            delete_middle_main(cluster_id, info_list, f)
            conf_stop_process(info_list, f)

            logger.debug("Start stopping the cluster : " + str(cluster_id))
            printout("Start stopping the cluster : " + str(cluster_id), info_type = 0, info_list = info_list, fp = f)
            stop_obj = stop_sacluster(params.cluster_info_all[cluster_id], auth_info, max_workers, fp = f, info_list = info_list, api_index = api_index)
            stop_obj()
            logger.debug("Finished stopping the cluster : " + str(cluster_id))
            printout("Finished stopping the cluster : " + str(cluster_id), info_type = 0, info_list = info_list, fp = f)

        if(index == True):
            logger.debug("Start deleting the cluster : " + str(cluster_id))
            printout("Start deleting the cluster : " + str(cluster_id), info_type = 0, info_list = info_list, fp = f)
            delete_obj = delete_class.delete_sacluster(params.cluster_info_all[cluster_id], auth_info, max_workers, fp = f, info_list = info_list, api_index = api_index)
            delete_obj()
            logger.debug("Finished deleting the cluster : " + str(cluster_id))
            printout("Finished deleting the cluster : " + str(cluster_id), info_type = 0, info_list = info_list, fp = f)
        else:
            logger.debug('There are no clusters to stop')
    else:
        printout("Stop processing.", info_type = 0, info_list = info_list, fp = f)
        sys.exit()