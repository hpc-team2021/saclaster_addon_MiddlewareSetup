
import os
os.chdir(os.path.dirname(os.path.abspath(__file__)))
common_path = os.path.abspath("../..")

import sys
sys.path.append(common_path + "/lib/others")
from def_config_making_middle import config_making_main
from def_config_loading import config_loading_main
import logging

logger = logging.getLogger("sacluster").getChild(os.path.basename(__file__))

def config_main_middle(ext_info, in_path = "", out_path = "", make_dir_index = False, info_list = [1,0,0,0], fp = ""):
    if(in_path == ""):
        logger.debug('config defined mode')
        config_param = config_making_main(ext_info, out_path = out_path, make_dir_index = make_dir_index, info_list = info_list, fp = fp)

    else:
        logger.debug('config read mode')
        config_param = config_loading_main(ext_info, in_path = in_path, info_list = info_list, fp = fp)
    
    return config_param














