import sys
import os
import logging

logger = logging.getLogger("sacluster").getChild(os.path.basename(__file__))

from res_out import response_output

path = "../../.."
os.chdir(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(path + "/lib/others")

from info_print import printout, printout_cluster


def res_check_post(configuration_info, res,info_list,fp, monitor_info_list):
    logger.debug("confirm API request(post)")
    if ("is_ok" in res.keys()):
        if res["is_ok"] == True:
            logger.debug("API processing succeeded")
            check = True
            return check
        else:
            logger.warning("API processing failed")
            _ = printout_cluster("Error:", cls_monitor_level = 1, set_monitor_level = configuration_info["monitor level"], info_list = info_list, monitor_info_list = monitor_info_list, fp = fp, msg_token = configuration_info["monitor token"])
            #rf = response_output("Error_post" ,res)
            check = False
            return check

    elif ("is_fatal" in res.keys()):
        logger.warning("API processing failed")
        _ = printout_cluster("Status:" + res["status"], cls_monitor_level = 1, set_monitor_level = configuration_info["monitor level"], info_list = info_list, monitor_info_list = monitor_info_list, fp = fp, msg_token = configuration_info["monitor token"])
        _ = printout_cluster("Error:" + res["error_msg"], cls_monitor_level = 1, set_monitor_level = configuration_info["monitor level"], info_list = info_list, monitor_info_list = monitor_info_list, fp = fp, msg_token = configuration_info["monitor token"])
        #_ = printout("Status:" + res["status"], info_list = info_list , fp = fp,msg_token = msg_token)
        #_ = printout("Error:" + res["error_msg"], info_list = info_list,fp = fp,msg_token = msg_token)
        #rf = response_output("Error_post" ,res)
        check = False
        return check

def res_check_get(configuration_info, res,info_list,fp, monitor_info_list):
    logger.debug("confirm API request(get)")
    if ("is_ok" in res.keys()):
        if res["is_ok"] == True:
            logger.debug("API processing succeeded")
            check = True
            return check
        else:
            logger.warning("API processing failed")
            _ = printout_cluster("Error:", cls_monitor_level = 1, set_monitor_level = configuration_info["monitor level"], info_list = info_list, monitor_info_list = monitor_info_list, fp = fp, msg_token = configuration_info["monitor token"])
            #_ = printout("Error:", info_list = info_list,fp = fp,msg_token = msg_token)
            #rf = response_output("Error_get" ,res)
            check = False
            return check

    elif ("is_fatal" in res.keys()):
        logger.warning("API processing failed")
        _ = printout_cluster("Status:" + res["status"], cls_monitor_level = 1, set_monitor_level = configuration_info["monitor level"], info_list = info_list, monitor_info_list = monitor_info_list, fp = fp, msg_token = configuration_info["monitor token"])
        _ = printout_cluster("Error:" + res["error_msg"], cls_monitor_level = 1, set_monitor_level = configuration_info["monitor level"], info_list = info_list, monitor_info_list = monitor_info_list, fp = fp, msg_token = configuration_info["monitor token"])
        #_ = printout("Status:" + res["status"], info_list = info_list , fp = fp,msg_token = msg_token)
        #_ = printout("Error:" + res["error_msg"], info_list = info_list,fp = fp,msg_token = msg_token)
        #rf = response_output("Error_get" ,res)
        check = False
        return check

def res_check_put(configuration_info, res, info_list, fp, monitor_info_list):
    logger.debug("confirm API request(put)")
    if ("Success" in res.keys()):
        if res["Success"] == True:
            logger.debug("API processing succeeded")
            check = True
            return True
        else:
            logger.warning("API processing failed")
            _ = printout_cluster("Error:", cls_monitor_level = 1, set_monitor_level = configuration_info["monitor level"], info_list = info_list, monitor_info_list = monitor_info_list, fp = fp, msg_token = configuration_info["monitor token"])
            #_ = printout("Error:",fp = fp, info_list = info_list,msg_token = msg_token)
            #rf = response_output("Error_put",res)
            check = False
            return check

    elif ("is_fatal" in res.keys()):
        logger.warning("API processing failed")
        _ = printout_cluster("Status:" + res["status"], cls_monitor_level = 1, set_monitor_level = configuration_info["monitor level"], info_list = info_list, monitor_info_list = monitor_info_list, fp = fp, msg_token = configuration_info["monitor token"])
        _ = printout_cluster("Error:" + res["error_msg"], cls_monitor_level = 1, set_monitor_level = configuration_info["monitor level"], info_list = info_list, monitor_info_list = monitor_info_list, fp = fp, msg_token = configuration_info["monitor token"])
        #_ = printout("Status:" + res["status"], info_list = info_list , fp = fp,msg_token = msg_token)
        #_ = printout("Error:" + res["error_msg"],fp = fp, info_list = info_list,msg_token = msg_token)
        #rf = response_output("Error_put",res)
        check = False
        return check

def build_error(configuration_info, info_list, fp, monitor_info_list):
    logger.debug("decision of repeating to request")
    while(True):
        conf = printout("Try again??(yes/no):",info_type = 2, info_list = info_list, fp = fp)
        if conf == "yes":
            break
        elif conf == "no":
            _ = printout_cluster("Stop processing.", cls_monitor_level = 1, set_monitor_level = configuration_info["monitor level"], info_list = info_list, monitor_info_list = monitor_info_list, fp = fp, msg_token = configuration_info["monitor token"])
            #_ = printout("Stop processing.", info_list = info_list,fp = fp,msg_token = msg_token)
            sys.exit()
        else:
            _ = printout("Please answer yes or no.",info_list = info_list,fp = fp)
    return 











