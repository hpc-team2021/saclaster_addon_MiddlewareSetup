

import os
os.chdir(os.path.dirname(os.path.abspath(__file__)))
path = os.path.abspath("../..")
import sys
from config_function import set_parm, conf_pattern_main, conf_pattern_1, conf_pattern_2
sys.path.append(path + "/lib/others")
#from API_method import get, post, put
import pandas as pd
from config_section import setting_head, setting_compute, setting_monitor, setting_zone, setting_nfs, show_current_state, def_config_name
import logging
logger = logging.getLogger("sacluster").getChild(os.path.basename(__file__))

def def_config_main(ext_info, fp = "", info_list = [1,0,0,0]):
    logger.debug('start to define config params')
    setting_sec_func = {"Head":setting_head, "Compute":setting_compute, "Monitor": setting_monitor, "Zone": setting_zone, "NFS": setting_nfs, "Current": show_current_state}
    #Config内容名を指定
    config_param = {}
    config_param["config_name"] = def_config_name(fp = fp, info_list = info_list)
    set_parm("Config name", config_param["config_name"], info_list = info_list, fp = fp)
    logger.debug('defined config name')
    
    set_list = pd.DataFrame([["Compute   ","yet    ", "required    "], ["Head      ", "yet    ", "required    "], ["NFS       ", "auto   ", "not-required"], ["Zone      ", "auto   ", "not-required"], ["Monitor   ", "auto   ", "not-required"], ["Current   ", "-      ", "-           "]], index = ["Compute", "Head", "NFS", "Zone", "Monitor","Current"], columns = ["name", "state", "request"])
    
    max_node = 0
    for k,v in ext_info["Zone"].items():
        if(v["maximum"] > max_node):
            max_node = v["maximum"]
            max_zone = k
    ext_info["max_zone"] = max_zone
    logger.debug('Configured the maximum installable nodes and their zones.')
    
    while(True):
        if(len(set_list[(set_list["state"] == "already") & (set_list["request"] == "required    ")]) == len(set_list[set_list["request"] == "required    "])):
            logger.debug('config parameter definition can be terminated')
            set_list.loc["Done"] = ["Done      ", "-      ", "-           "]
        elif(len(set_list[(set_list["state"] == "already") & (set_list["request"] == "required    ")]) < len(set_list[set_list["request"] == "required    "]) and "Done" in list(set_list.index)):
            logger.debug('config parameter definition cannot be terminated')
            set_list = set_list.drop(index='Done')
        
        logger.debug('creat section table')
        set_list_tabel = [set_list.loc[label, "name"] + "|" + set_list.loc[label, "state"] + "|" + set_list.loc[label, "request"] for label in list(set_list.index)]
        setting_ind = conf_pattern_main("Please select a setting section===========", set_list_tabel, info_list = info_list, fp = fp)
        
        if(setting_ind.split("|")[0].replace(" ","") == "Done"):
            logger.debug('show final config param')
            config_param, set_list = show_current_state(ext_info, config_param, set_list, fp = fp, info_list = info_list)
            logger.debug('finally confirmed')
            temp = conf_pattern_2("Are the above setting correct", ["yes", "no"], "no", info_list = info_list, fp = fp)
            if(temp == "yes"):
                logger.debug('Automatic configuration of zone')
                if("Zone" not in config_param):
                    config_param["Zone"] = {}
                    config_param["Zone"]["Zone"] = {}
                    config_param["Zone"]["Zone"][max_zone] = config_param["Compute"]["Compute number"]
                    config_param["Zone"]["Head Zone"] = max_zone
                    
                logger.debug('Automatic configuration of nfs')
                if("NFS" not in config_param):
                    config_param["NFS"] = {}
                    config_param["NFS"]["NFS"] = False
                    
                logger.debug('Automatic configuration of monitor')
                if("Monitor" not in config_param):
                    config_param["Monitor"] = {}
                    config_param["Monitor"]["Monitor"] = False
                    
                return config_param
        
        else:
            logger.debug('show section table')
            config_param, set_list = setting_sec_func[setting_ind.split("|")[0].replace(" ","")](ext_info, config_param, set_list, fp = fp, info_list = info_list)













































