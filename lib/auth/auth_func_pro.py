#!/usr/bin/env python3
# -*- coding: utf-8 -*-

zone="tk1v"
url="https://secure.sakura.ad.jp/cloud/zone/"+zone+"/api/cloud/1.1"

import sys
import json
import os
from jsonschema import validate, ValidationError
import base64

os.chdir(os.path.dirname(os.path.abspath(__file__)))
path = os.path.abspath("../..")
sys.path.append(path + "/lib/others")

from API_method import get, post, put
from info_print import printout
import datetime
import logging

logger = logging.getLogger("sacluster").getChild(os.path.basename(__file__))

jsa_auth = {
       "type": "object",
       "required": [
        "access token",
        "access token secret"
        ],
       "properties": {
           "access token": {
               "type": "string"
               },
           "access token secret": {
               "type": "string"
               }
           }
       }

def check_json_file(item, json_schema):
    try:
        validate(item, json_schema)
        return True, ""
    except ValidationError as e:
        return False, e.message
    
def json_input(filename):
    with open(filename, 'r') as f:
        json_f = json.load(f)
    return json_f
    
def json_output(json_f, filename):
    with open(filename, 'w') as f:
        json.dump(json_f, f, indent=4)


def define_auth_info(path, info_list, api_index = True, fp = ""):
    
    while(True):
        token = printout('[access token] >> ', info_type = 2, info_list = info_list, fp = fp)
        token_secret = printout('[access token secret] >> ', info_type = 2, info_list = info_list, fp = fp)
        logger.debug('Redifined authentication information')
        
        basic_user_and_pasword = base64.b64encode('{}:{}'.format(token, token_secret).encode('utf-8'))
        
        if(api_index == True):
            _ = printout("Checking the authentication information ...", info_list = info_list, fp = fp)
            logger.debug('Checking the authentication information')
            res = get(url + "/auth-status", basic_user_and_pasword)
        
            if("Account" in res):
                break
            else:
                _ = printout("AuthenticationError: cannot access", info_list = info_list, fp = fp)
                logger.error('AuthenticationError: cannot access')
        else:
            break
        
    auth_res = basic_user_and_pasword
    _ = printout("Saving Setting.json ...", info_list = info_list, fp = fp)
    logger.debug('Saving the authentication information to Setting.json')
    json_output({"access token": token, "access token secret": token_secret}, path)
    
    return auth_res


def authentication_cli(fp = "", info_list = [1,0,0,1], api_index = True):
    filename = "Setting.json"
    if(os.path.exists(path + "/setting/" + filename) == True):   #There is a change in Windows
        #Read the authentication information from the Setting.json
        _ = printout("loading Setting.json ...", info_list = info_list, fp = fp)
        logger.debug('loading Setting.json')
        setting_info = json_input(path + "/setting/" + filename)
        
        #Check the Setting.json
        _ = printout("Checking the contents in Setting.json ...", info_list = info_list, fp = fp)
        logger.debug('Checking the contents in Setting.json')
        res, e_message = check_json_file(setting_info, jsa_auth)
        
        if(res == True):
            auth_res = base64.b64encode('{}:{}'.format(setting_info["access token"], setting_info["access token secret"]).encode('utf-8'))
            
            if(api_index == True):
                _ = printout("Checking the authentication information ...", info_list = info_list, fp = fp)
                logger.debug('Checking the authentication information ...')
                res = get(url + "/auth-status", auth_res)
                
                if("Account" not in res):
                    _ = printout("AuthenticationError: cannot access", info_list = info_list, fp = fp)
                    logger.error('AuthenticationError: cannot access')
                    auth_res = define_auth_info(path + "/setting/Setting.json", info_list = info_list, api_index = api_index, fp = fp)
                
        else:
            _ = printout("AuthenticationError: Elements in Setting.json are wrong", info_list = info_list, fp = fp)
            logger.error('AuthenticationError: Elements in Setting.json are wrong \n' + e_message)
            auth_res = define_auth_info(path + "/setting/Setting.json", info_list = info_list, api_index = api_index, fp = fp)
            
    else:
        _ = printout("AuthenticationError: Setting.json does not exist in sacluster/setting", info_list = info_list, fp = fp)
        logger.error('AuthenticationError: Setting.json does not exist in sacluster/setting')
        auth_res = define_auth_info(path + "/setting/Setting.json", info_list = info_list, api_index = api_index, fp = fp)
    
    _ = printout("Certified authentication information", info_list = info_list, fp = fp)
    logger.debug('Certified authentication information')
    
    return auth_res


























































































