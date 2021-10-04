

import sys
import os
import logging
path = "../../.."
os.chdir(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(path + "/lib/others")
from info_print import printout

logger = logging.getLogger("sacluster").getChild(os.path.basename(__file__))


def get_cluster_id(params, info_list, f, api_index = True):
    if(len(params) != 0):
        while(True):
            cluster_id = printout('[id] >>', info_type = 1, info_list = info_list, fp = f)
            if(cluster_id in params):
                index = True
                break
            if(api_index == False):
                index = False
                break
            else:
                printout('InputError: the specified cluster id does not exist', info_type = 0, info_list = info_list, fp = f)
    else:
        cluster_id = ""
        index = False
        
    return index, cluster_id
        



































