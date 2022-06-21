

import os
os.chdir(os.path.dirname(os.path.abspath(__file__)))
common_path = os.path.abspath("../..")

from os.path import expanduser
home_path = expanduser("~") + "/sacluster"

import sys
import json
sys.path.append(common_path + "/lib/others")
from config_function import set_parm, conf_pattern_main, conf_pattern_1, conf_pattern_2
from info_print import printout
from def_config_middle import def_config_main
#from config_validation import config_validation
import logging
logger = logging.getLogger("sacluster").getChild(os.path.basename(__file__))


def make_dirs(path, filename, info_list = [1,0,0,0], fp = ""):
    
    while(True):
        #ディレクトリの作成
        try:
            logger.debug('Making directories to save config file')
            _ = printout("Making a directory to save config file...", info_type = 0, info_list = info_list, fp = fp)
            os.makedirs(path, exist_ok = True)
            break
            
        #ディレクトリにアクセスできない場合（認証設定がされている場合）
        except PermissionError as e:
            logger.error('PermissionError: the specified directory cannot be accessed')
            _ = printout("PermissionError: the specified directory cannot be accessed.", info_type = 0, info_list = info_list, fp = fp)
            
            #再度pathを要求
            logger.debug('re-difine the path to output config params')
            out_path = printout("Please specify the other directory >>>", info_type = 1, info_list = info_list, fp = fp)
            
            #config fileの拡張子を確認
            logger.debug('Checking the extension of the config file')
            #パス内にファイル名が含まれている場合
            if((".js" in out_path.split("/")[-1]) or (".json" in out_path.split("/")[-1])):
                filename = os.path.basename(out_path)
                path = os.path.dirname(out_path)
                logger.debug('Directory and filename are set')
            #パス内にファイル名が含まれていない場合
            else:
                filename = "config.json"
                path = out_path
                logger.debug('New directory is set')
                logger.debug('The config filename is automatically set to config.json')
               
    return path, filename

def check_dir_existence(path, filename, info_list = [1,0,0,0], fp = ""):
    while(True):
        logger.debug('Checking the output directory')
        _ = printout("Checking the output directory...", info_type = 0, info_list = info_list, fp = fp)
        #ディレクトリの存在を確認
        index = os.path.exists(path)
        #ディレクトリが存在しない場合
        if(index == False):
            logger.error('DirNotFoundError: the specified directory cannot be found')
            _ = printout("DirNotFoundError: the specified directory cannot be found.", info_type = 0, info_list = info_list, fp = fp)
            temp = conf_pattern_2("Do you want to change the directory?? (if you choose no, the specified directory will be created)", ["yes", "no"], "no", info_list = info_list, fp = fp)
            
            #パスの再定義
            if(temp == "yes"):
                out_path = printout("Please specify the other directory >>>", info_type = 1, info_list = info_list, fp = fp)
                logger.debug('New Path was entered')
                logger.debug('Checking the extension of the config file')
                
                #パス内にファイル名が含まれている場合
                if((".js" in out_path.split("/")[-1]) or (".json" in out_path.split("/")[-1])):
                    filename = os.path.basename(out_path)
                    path = os.path.dirname(out_path)
                    logger.debug('New directory and filename are set')
                    
                #パス内にファイル名が含まれていない場合
                else:
                    filename = "config.json"
                    path = out_path 
                    logger.debug('New directory is set')
                    logger.debug('The config filename is automatically set to config.json')
               
            #ディレクトリを生成
            else:
                path, filename = make_dirs(path, filename, info_list = info_list, fp = fp)
        #ディレクトリが存在する場合
        else:
            logger.debug('Existence of specified file has been confirmed')
            return path, filename
    

def check_dir(path, filename, info_list = [1,0,0,0], fp = ""):
    #パスとファイルの存在確認
    path, filename = check_dir_existence(path = path, filename = filename, info_list = info_list, fp = fp)
    
    #パスのアクセス確認
    while(True):
        index_1 = os.access(path,os.R_OK)
        index_2 = os.access(path,os.W_OK)
        index_3 = os.access(path,os.X_OK)
        
        if(index_1 == False or index_2 == False or index_3 == False):
            logger.error('PermissionError: the specified directory cannot be accessed')
            _ = printout("PermissionError: the specified directory cannot be accessed.", info_type = 0, info_list = info_list, fp = fp)
            out_path = printout("Please specify the other directory >>>", info_type = 1, info_list = info_list, fp = fp)
            if((".js" in out_path.split("/")[-1]) or (".json" in out_path.split("/")[-1])):
                filename = os.path.basename(out_path)
                out_path = os.path.dirname(out_path)
                logger.debug('New directory and filename are set')
                
            else:
                filename = "config.json"
                path = out_path
                logger.debug('New directory is set')
                logger.debug('The config filename is automatically set to config.json')
                
            #パスとファイルの存在確認
            path, filename = check_dir_existence(path = path, filename = filename, info_list = info_list, fp = fp)
               
        else:
            return path, filename
    
            
def check_filename(path, filename, info_list = [1,0,0,0], fp = ""):
    index = 0
    file_list = os.listdir(path)
    
    logger.debug('Checking filename')
    printout("Checking filename...", info_type = 0, info_list = info_list, fp = fp)
    if(filename in file_list):
        if(filename != "config.json"):
            index = 1
            filename = "config.json"
            logger.warining("the specified filename exists in the directory")
            _ = printout("Warning: the specified filename exists in the directory.", info_type = 0, info_list = info_list, fp = fp)
            
        count = 2
        while(True):
            if(filename not in file_list):
                break
            filename = "config_" + str(count) + "_middle.json"
            count += 1
        
        if(index == 1):
            logger.info("filename changed to " + filename)
            _ = printout("INFO:filename change to " + filename, info_type = 0, info_list = info_list, fp = fp)
            
    return path, filename

def out_config(filename, path, config_param):
    with open(path + "/" + filename, 'w') as f:
        json.dump(config_param, f, indent=4, ensure_ascii=False)
    

def config_making_main(ext_info, out_path = "", make_dir_index = False, info_list = [1,0,0,0], fp = ""):
    
    if(out_path != ""):
        #configファイルの拡張子の確認
        logger.debug('Checking the extension of the config file')
        if((".js" in out_path.split("/")[-1]) or (".json" in out_path.split("/")[-1])):
            filename = os.path.basename(out_path)
            out_path = os.path.dirname(out_path)
            
            if(out_path == ""):
                logger.debug('The directory to be saved is automatically set to /config')
                out_path = common_path + "/config"
        else:
            logger.debug('The config filename was automatically set to config.json')
            filename = "config.json"
        
        #config file出力のためのディレクトリの作成
        if(make_dir_index == True):
            out_path, filename = make_dirs(out_path, filename, info_list = info_list, fp = fp)
        out_path, filename = check_dir(out_path, filename, info_list = info_list, fp = fp)
        out_path, filename = check_filename(out_path, filename, info_list = info_list, fp = fp)
        
    else:
        filename = "config.json"
        out_path = home_path + "/config"
        out_path, filename = check_filename(out_path, filename, info_list = info_list, fp = fp)
        
    _ = printout("Out directory:: " + str(out_path), info_type = 0, info_list = info_list, fp = fp)
    _ = printout("Out filename :: " + str(filename), info_type = 0, info_list = info_list, fp = fp)
    logger.debug('Out directory:: ' + str(out_path))
    logger.debug('Out filename ::' + str(filename))
    
    config_param = def_config_main(ext_info, fp = fp, info_list = info_list)
        
    logger.debug('save config params')
    out_config(filename, out_path, config_param)
        
    return config_param























































































