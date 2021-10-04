

import os
os.chdir(os.path.dirname(os.path.abspath(__file__)))
path = os.path.abspath("../..")

import os
import sys
import json
sys.path.append(path + "/lib/others")
from API_method import get, post, put
from info_print import printout
import base64
import requests
import datetime

#パラメータの設定時の出力
def set_parm(param_name, set_param, info_list = [1,0,0,1], fp = ""):
    if(isinstance(set_param, list) == True):
        _ = printout("Set " + str(param_name) + " to " + ",".join(set_param), info_type = 0, info_list = info_list, fp = fp)
        printout("", info_type = 0, info_list = info_list, fp = fp)
    else:
        _ = printout("Set " + str(param_name) + " to " + set_param, info_type = 0, info_list = info_list, fp = fp)
        printout("", info_type = 0, info_list = info_list, fp = fp)


def conf_pattern_1(comment, info_list = [1,0,0,1], fp = ""):
    val = printout("[" + str(comment) + "] >> ", info_type = 1, info_list = info_list, fp = fp).replace(" ","")
    
    return val

def conf_pattern_2(comment, candidates, default, info_list = [1,0,0,1], fp = ""):
    while(True):
        val = printout("[" + str(comment) + " {" + ",".join(candidates) + "}, (default: " + str(default) + ")] >> ", info_type = 1, info_list = info_list, fp = fp).replace(" ","")
        
        if(val == ""):
            return default
        
        else:
            if(val in candidates):
                return val
            
            else:
                _ = printout("Warning: " + comment + " must be selected one from " + ",".join(candidates), info_type = 0, info_list = info_list, fp = fp)
        

def conf_pattern_3(comment, candidate, default, info_list = [1,0,0,1], fp = ""):
    pos_index = 5
    if(len(candidate) <= pos_index):
        while(True):
            printout("[[" + str(comment) + "]]", info_type = 0, info_list = info_list, fp = fp)
            printout(str(0) + ": " + str(candidate[0]) + " (default)", info_type = 0, info_list = info_list, fp = fp)
            for i in range(1,len(candidate)):
                printout(str(i) + ": " + str(candidate[i]), info_type = 0, info_list = info_list, fp = fp)
            
            val = printout(">>>", info_type = 1, info_list = info_list, fp = fp)
            printout("", info_type = 0, info_list = info_list, fp = fp)
            if(val == ""):
                return 0
            elif(val.isdigit() != True):
                printout("Warning: Please specify in the index", info_type = 0, info_list = info_list, fp = fp)
            elif((int(val) < 0) or (int(val) >= len(candidate))):
                printout("Warning: An unexpected value", info_type = 0, info_list = info_list, fp = fp)
            else:
                return int(val)
    
    else:   
        while(True):
            printout("[[" + str(comment) + "]]", info_type = 0, info_list = info_list, fp = fp)
            printout(str(0) + ": " + str(candidate[0]) + " (default)", info_type = 0, info_list = info_list, fp = fp)
            for i in range(1, pos_index):
                printout(str(i) + ": " + str(candidate[i]), info_type = 0, info_list = info_list, fp = fp)
                
            if(pos_index < len(candidate)):
                printout(str(pos_index) + ": others", info_type = 0, info_list = info_list, fp = fp)
            
            val = printout(">>>", info_type = 1, info_list = info_list, fp = fp)
            printout("", info_type = 0, info_list = info_list, fp = fp)
            
            if(val == ""):
                return 0
            elif(val.isdigit() != True):
                printout("Warning: Please specify in the index", info_type = 0, info_list = info_list, fp = fp)
            elif(int(val) == pos_index):
                pos_index = len(candidate)
            elif((pos_index < len(candidate)) and ((int(val) < 0) or (int(val) > pos_index))):
                printout("Warning: An unexpected value", info_type = 0, info_list = info_list, fp = fp)
            elif((pos_index == len(candidate)) and ((int(val) < 0) or (int(val) >= pos_index))):
                printout("Warning: An unexpected value", info_type = 0, info_list = info_list, fp = fp)
            else:
                return int(val)
            
def conf_pattern_4(comment, min_val, max_val, default, info_list = [1,0,0,1], fp = ""):
    while(True):
        val = printout("[" + str(comment) + " {" + str(min_val) + "~" + str(max_val) + "}, (default: " + str(default) + ")] >> ", info_type = 1, info_list = info_list, fp = fp).replace(" ","")
        
        if(val == ""):
            return default
        
        elif(val.isdecimal() == False):
            _ = printout("Warning: " + comment + " must be number from " + str(min_val) + " to " + str(max_val), info_type = 0, info_list = info_list, fp = fp)

        elif(min_val <= int(val) <= max_val):
            return int(val)
            
        else: 
            _ = printout("Warning: " + comment + " must be number from " + str(min_val) + " to "+ str(max_val), info_type = 0, info_list = info_list, fp = fp)

def conf_pattern_5(comment, info_list = [1,0,0,1], fp = ""):
    val = printout("[" + str(comment) + "] >> ", info_type = 1, info_list = info_list, fp = fp).replace(" ","")
    
    return val
            
def conf_pattern_main(comment, candidate, info_list = [1,0,0,1], fp = ""):
    while(True):
        printout(str(comment), info_type = 0, info_list = info_list, fp = fp)
        for i in range(len(candidate)):
            printout(str(i) + ": " + str(candidate[i]), info_type = 0, info_list = info_list, fp = fp)
            
        val = printout(">>>", info_type = 1, info_list = info_list, fp = fp)
        printout("==========================================", info_type = 0, info_list = info_list, fp = fp)
        
        if(val.isdigit() != True):
            printout("Warning: Please specify in the index", info_type = 0, info_list = info_list, fp = fp)
        elif((int(val) < 0) or (int(val) >= len(candidate))):
            printout("Warning: An unexpected specification", info_type = 0, info_list = info_list, fp = fp)
        else:
            return candidate[int(val)]
        

















































































