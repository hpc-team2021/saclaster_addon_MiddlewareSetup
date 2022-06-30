

import os
os.chdir(os.path.dirname(os.path.abspath(__file__)))
path = os.path.abspath("../..")
import sys
from config_function import set_parm, conf_pattern_main, conf_pattern_1, conf_pattern_2
sys.path.append(path + "/lib/others")
#from API_method import get, post, put
import pandas as pd
from config_section_middle import setting_monitor, setting_scheduler, setting_parallelcomputing, show_current_state, def_config_name
import logging
logger = logging.getLogger("sacluster").getChild(os.path.basename(__file__))

def def_config_main_middle(ext_info, fp = "", info_list = [1,0,0,0]):
    logger.debug('start to define config params for middle ware')
    setting_sec_func = {"Monitor":setting_monitor, "Scheduler":setting_scheduler, "ParallelComputing": setting_parallelcomputing, "Current": show_current_state}
    #Config内容名を指定
    config_param = {}
    config_param["config_name"] = def_config_name(fp = fp, info_list = info_list)
    set_parm("Config name", config_param["config_name"], info_list = info_list, fp = fp)
    logger.debug('defined config name')
    
    set_list = pd.DataFrame([["Monitor".ljust(20),"yet".ljust(7), "not-required".ljust(12)], ["Scheduler".ljust(20),"yet".ljust(7), "not-required".ljust(12)], ["ParallelComputing".ljust(20), "yet".ljust(7), "not-required".ljust(12)], ["Current".ljust(20), "-".center(7), "-".center(12)]], index = ["Monitor", "Scheduler", "ParallelComputing","Current"], columns = ["name", "state", "request"])
    
    while(True):
        if(len(set_list[(set_list["state"] == "already") & (set_list["request"] == "required".ljust(12))]) == len(set_list[set_list["request"] == "required".ljust(12)])):
            logger.debug('config parameter definition can be terminated')
            set_list.loc["Done"] = ["Done".ljust(20), "-".center(7), "-".center(12)]
        elif(len(set_list[(set_list["state"] == "already") & (set_list["request"] == "required".ljust(12))]) < len(set_list[set_list["request"] == "required".ljust(12)]) and "Done" in list(set_list.index)):
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
                logger.debug('Automatic configuration of Monitor params')
                if("Monitor" not in config_param):
                    config_param["Monitor"] = {}
                    config_param["Monitor"]["index"] = False
                    #config_param["Monitor"]["type"] = None
                    #config_param["Monitor"]["params"] = {}
                    
                logger.debug('Automatic configuration of Scheduler params')
                if("Job_scheduler" not in config_param):
                    config_param["Job_scheduler"] = {}
                    config_param["Job_scheduler"]["index"] = False
                    #config_param["Job_scheduler"]["type"] = None
                    #config_param["Job_scheduler"]["params"] = {}
                    
                logger.debug('Automatic configuration of ParallelComputing params')
                if("ParallelComputing" not in config_param):
                    config_param["ParallelComputing"] = {}
                    config_param["ParallelComputing"]["index"] = False
                    #config_param["ParallelComputing"]["type"] = None
                    #config_param["ParallelComputing"]["params"] = {}
                    
                return config_param
        
        else:
            logger.debug('show section table')
            config_param, set_list = setting_sec_func[setting_ind.split("|")[0].replace(" ","")](ext_info, config_param, set_list, fp = fp, info_list = info_list)













































