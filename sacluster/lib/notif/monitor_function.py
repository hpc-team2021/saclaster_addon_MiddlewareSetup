
import os
os.chdir(os.path.dirname(os.path.abspath(__file__)))
common_path = os.path.abspath("../../..")
import base64
import sys
sys.path.append(common_path + "/lib/others")
from info_print import printout
sys.path.append(common_path + "/lib/def_conf")
from config_function import set_parm, conf_pattern_main, conf_pattern_1, conf_pattern_2, conf_pattern_3, conf_pattern_4, conf_pattern_5
sys.path.append(common_path + "/lib/cls/construction")
import random
import requests
import json
import copy
import logging

logger = logging.getLogger("sacluster").getChild(os.path.basename(__file__))

#トークンの再定義
def redefine_monitor_token(token_name, info_list = [1,0,0,0], fp = ""):
    while(True):
        res = printout("Would you like to request a resend of the authorization code? (yes or no) >>", info_type = 1, info_list = info_list, fp = fp)
        if(res == "yes" or res == "no" or res == "y" or res == "n"):
            break
        else:
            logger.warning('Warning: response is wrong (selection is yes or no)')
            res = printout("Warning: Please select yes (y) or no (n).", info_type = 0, info_list = info_list, fp = fp)
    
    if(res == "yes" or res == "y"):
        logger.debug('resend authorization code')
        return "", True
    else:
        newer = str(printout("Please input new " + token_name + " >>", info_type = 1, info_list = info_list, fp = fp))
        logger.debug('Specify a new monitor space')
        return newer, False
    

def preparing_monitor(ext_info, config_param, api_index = True, f = "", info_list = [1,0,0,0]):
    info_list_temp = copy.deepcopy(info_list)
    if(api_index == True):
        if(config_param["Monitor"]["Monitor"] == True):
            while(True):
                #認証コードの生成
                logger.debug("Issuing an authorization code for moitor")
                _ = printout("Issuing an authorization code for moitor ...",info_type = 0 ,info_list = info_list, fp = f)
                authorization_code = random.randint(100000,999999)
            
                #通知方法がLINEの場合
                if(config_param["Monitor"]["Monitor type"] == "LINE"):
                    logger.debug("monitor type is LINE")
                    line_notify_token = str(config_param["Monitor"]["Monitor key"])
                    line_notify_api = 'https://notify-api.line.me/api/notify'
                    headers = {'Authorization': f'Bearer {line_notify_token}'}
                    data = {'message': f': authorization_code is {authorization_code}'}
                    logger.debug("sending authorization code to the LINE notify")
                    requests.post(line_notify_api, headers = headers, data = data)
                    input_authorization_code = conf_pattern_1("Authentication code", info_list = info_list, fp = f)
                
                    if(str(authorization_code) == str(input_authorization_code)):
                        info_list_temp[2] = 1
                        logger.debug("monitor space has been authenticated")
                        _ = printout("monitor space has been authenticated",info_type = 0 ,info_list = info_list_temp, fp = f, msg_token = line_notify_token)
                    #data = {'message': ': monitor space has been authenticated'}
                    #requests.post(line_notify_api, headers = headers, data = data)
                        return info_list_temp
                    else:
                        logger.error("MonitorError: failed to authenticate the monitor space")
                        _ = printout("MonitorError: failed to authenticate the monitor space",info_type = 0 ,info_list = info_list, fp = f)
                        new_token, index = redefine_monitor_token(ext_info["Monitor"][config_param["Monitor"]["Monitor type"]], info_list = info_list, fp = f)
                        if(index == False):
                            config_param["Monitor"]["Monitor key"] = new_token
                 
                #通知方法がslackの場合
                elif(config_param["Monitor"]["Monitor type"] == "slack"):
                    logger.debug("monitor type is slack")
                    slack_webhook_token = str(config_param["Monitor"]["Monitor key"])
                    data = {'text': f'authorization_code is {authorization_code}'}
                    while(True):
                        try:
                            logger.debug("sending authorization code to the slack channel")
                            requests.post(slack_webhook_token, data = json.dumps(data))
                            break
                        except:
                            logger.error("MonitorError: " + ext_info["Monitor"][config_param["Monitor"]["Monitor type"]] + " is wrong")
                            _ = printout("MonitorError: " + ext_info["Monitor"][config_param["Monitor"]["Monitor type"]] + " is wrong",info_type = 0 ,info_list = info_list, fp = f)
                            config_param["Monitor"]["Monitor key"] = str(printout("Please input new " + ext_info["Monitor"][config_param["Monitor"]["Monitor type"]] + " >>", info_type = 1, info_list = info_list, fp = f))
                            slack_webhook_token = str(config_param["Monitor"]["Monitor key"])
                    
                    input_authorization_code = conf_pattern_1("Authentication code", info_list = info_list, fp = f)
                
                    if(str(authorization_code) == str(input_authorization_code)):
                        info_list_temp[1] = 1
                        logger.debug("monitor space has been authenticated")
                        _ = printout("monitor space has been authenticated", info_type = 0, info_list = info_list_temp, fp = f, msg_token = slack_webhook_token)
                    #data = {'text': 'monitor space has been authenticated'}
                    #requests.post(slack_webhook_token, data = json.dumps(data))
                        return info_list_temp
                    else:
                        logger.error("MonitorError: failed to authenticate the monitor space")
                        _ = printout("Error: failed to authenticate the monitor space",info_type = 0 ,info_list = info_list, fp = f)
                        new_token, index = redefine_monitor_token(ext_info["Monitor"][config_param["Monitor"]["Monitor type"]], info_list = info_list, fp = f)
                        if(index == False):
                            config_param["Monitor"]["Monitor key"] = new_token
                
    #else:
    return info_list_temp
                
                















































