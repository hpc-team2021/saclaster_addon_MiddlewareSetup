
import os
os.chdir(os.path.dirname(os.path.abspath(__file__)))
path = os.path.abspath("../..")

import sys
import json
from jsonschema import validate, ValidationError
from load_external_data import external_data
from info_print import printout
from def_config_making import config_making_main
import logging

logger = logging.getLogger("sacluster").getChild(os.path.basename(__file__))

def load_config(filename, path):
    with open(path + "/" + filename) as f:
        data = json.load(f)
        
    return data

def load_config_checker(info_list = [1,0,0,0], fp = ""):
    _ = printout("loading config checker ...", info_type = 0, info_list = info_list, fp = fp)
    try:
        with open(path + "/lib/.Ex_info/config_checker.json", "r") as f:
            data = json.load(f)
    
    except FileNotFoundError as e:
        _ = printout("EnvironmentalError: config_checker.json does not exist under sacluster/lib/.Ex_info\nYou should install sacluster from url", info_type = 0, info_list = info_list, fp = fp)
        sys.exit()
        
    return data

#再定義するかどうかの確認（再定義しない場合は強制終了）
def redefine_config(ext_info, info_list = [1,0,0,0], fp = ""):
    while(True):
        res = printout("Do you want to redefine new config params (yes or no) >>", info_type = 1, info_list = info_list, fp = fp)
        if(res == "yes" or res == "no" or res == "y" or res == "n"):
            break
        else:
            res = printout("Warning: Please select yes (y) or no (n).", info_type = 0, info_list = info_list, fp = fp)
    
    if(res == "yes" or res == "y"):
        out_path = printout("Output path >>", info_type = 1, info_list = info_list, fp = fp)
        config_param = config_making_main(ext_info, out_path = out_path, info_list = info_list, fp = fp)
        return config_param
    else:
        _ = printout("ConfigError: config params cannot be loaded.", info_type = 0, info_list = info_list, fp = fp)
        sys.exit()
        
def checking_config_details(ext_info, config_param, info_list = [1,0,0,0], fp = ""):
    
    #NFSに関するcheck
    #NFSの設定がなされている場合
    logger.debug('Checking params of nfs')
    if("NFS" in config_param):
        #NFSがTrueである場合
        if(config_param["NFS"]["NFS"] == True):
            #NFS zoneの設定があるかどうか確認
            if("NFS zone" not in config_param["NFS"]):
                logger.error('ConfigError: If NFS is True, configure the NFS settings for each zone')
                _ = printout("ConfigError: If NFS is True, configure the NFS settings for each zone", info_type = 0, info_list = info_list, fp = fp)
                config_param = redefine_config(ext_info, info_list = info_list, fp = fp)
                return config_param
            else:
                if(len(config_param["NFS"]["NFS zone"]) == 0):
                    _ = printout("ConfigError: NFS setting at each zone is empty", info_type = 0, info_list = info_list, fp = fp)
                    config_param = redefine_config(ext_info, info_list = info_list, fp = fp)
                    return config_param
            
            #Zoneの指定がされていない場合
            if("Zone" not in config_param):
                logger.error('ConfigError: NFS must be set with Zone')
                _ = printout("ConfigError: NFS must be set with Zone", info_type = 0, info_list = info_list, fp = fp)
                config_param = redefine_config(ext_info, info_list = info_list, fp = fp)
                return config_param
            #Zoneの指定がされている場合
            else:
                #nfsで指定されたzoneがZoneの設定に含まれているかどうかを確認
                config_zones = list(set(config_param["Zone"]["Zone"].keys()))
                nfs_zones = list(set(config_param["NFS"]["NFS zone"].keys()))
            
                if(len(list(set(nfs_zones) & set(config_zones))) != len(nfs_zones)):
                    logger.error('ConfigError: The zone setting in NFS params does not mutch to the zone setting in Zone params')
                    _ = printout("ConfigError: The zone setting in NFS params does not mutch to the zone setting in Zone params", info_type = 0, info_list = info_list, fp = fp)
                    config_param = redefine_config(ext_info, info_list = info_list, fp = fp)
                    return config_param
                
            #指定ゾーンがNFSを設置できるゾーンであるかを確認 & NFS typeとNFS sizeの設定の確認
            nfs_all_zone = list(ext_info["NFS zone"])
            nfs_all_type = list(ext_info["NFS"].keys())
            for k,v in config_param["NFS"]["NFS zone"].items():
                #指定ゾーンがNFSを設置できるゾーンであるかを確認
                if(k not in nfs_all_zone):
                    logger.error("ConfigError: NFS cannot be installed on " + str(k))
                    _ = printout("ConfigError: NFS cannot be installed on " + str(k), info_type = 0, info_list = info_list, fp = fp)
                    config_param = redefine_config(ext_info, info_list = info_list, fp = fp)
                    return config_param
                
                #NFS typeの設定の確認
                if(v["NFS type"] not in nfs_all_type):
                    logger.error("ConfigError: NFS type should be select from " + ", ".join(nfs_all_type))
                    _ = printout("ConfigError: NFS type should be select from " + ", ".join(nfs_all_type), info_type = 0, info_list = info_list, fp = fp)
                    config_param = redefine_config(ext_info, info_list = info_list, fp = fp)
                    return config_param
                
                #NFS sizeの設定の確認
                nfs_all_size_str = list(ext_info["NFS"][v["NFS type"]].keys())
                nfs_all_size_int = [int(nfs_all_size_str[i]) for i in range(len(nfs_all_size_str))]
                if(v["NFS size"] not in nfs_all_size_int):
                    logger.error("ConfigError: NFS size should be select from " + ", ".join(nfs_all_size_str))
                    _ = printout("ConfigError: NFS size should be select from " + ", ".join(nfs_all_size_str), info_type = 0, info_list = info_list, fp = fp)
                    config_param = redefine_config(ext_info, info_list = info_list, fp = fp)
                    return config_param
                
                #NFSPlanが設定されていない場合は自動設定
                if("NFSPlan" not in v):
                    logger.debug("Automatic configuration of nfs")
                    config_param["NFS"]["NFS zone"][k]["NFSPlan"] = ext_info["NFS"][v["NFS type"]][str(v["NFS size"])]
                #NFSPlanが設定されている場合は、NFSのsizeとtypeの設定とmatchしているかどうかを確認
                else:
                    if(v["NFSPlan"] != ext_info["NFS"][v["NFS type"]][str(v["NFS size"])]):
                        logger.error("ConfigError: NFSPlan does not match to NFS type and size. Please confirm NFS info")
                        _ = printout("ConfigError: NFSPlan does not match to NFS type and size. Please confirm NFS info", info_type = 0, info_list = info_list, fp = fp)
                        config_param = redefine_config(ext_info, info_list = info_list, fp = fp)
                        return config_param, 1
    
    #NFSの設定がされていない場合
    else:
        config_param["NFS"]["NFS"] = False
        logger.info("Info: NFS is automatically set to " + str(config_param["NFS"]["NFS"]))
        _ = printout("Info: NFS is automatically set to " + str(config_param["NFS"]["NFS"]), info_type = 0, info_list = info_list, fp = fp)
        
    #Zoneに関するcheck
    #Zoneの設定がされている場合
    logger.debug('Checking params of zone')
    if("Zone" in config_param):
        
        #指定zoneを取得
        config_zones = list(set(config_param["Zone"]["Zone"].keys()))
        
        #head nodeのzoneが指定zoneに含まれているかどうか確認
        if(config_param["Zone"]["Head Zone"] not in config_zones):
            logger.error("ConfigError: specification of Head Zone is wrong (You should choose Head Zone from " + ",".join(config_zones) + ")")
            _ = printout("ConfigError: specification of Head Zone is wrong (You should choose Head Zone from " + ",".join(config_zones) + ")", info_type = 0, info_list = info_list, fp = fp)
            config_param = redefine_config(ext_info, info_list = info_list, fp = fp)
            return config_param
        
        #Zone数が複数の場合
        if(len(config_zones) > 1):
            #全てのゾーンが本番ゾーンであるかどうか確認
            for i in range(len(config_zones)):
                if(ext_info["Zone"][config_zones[i]]["Type"] != "practice"):
                    logger.error("ConfigError: " + config_zones[i] + " is test zone (Multiple zones must be selected from the practice zones)")
                    _ = printout("ConfigError: " + config_zones[i] + " is test zone (Multiple zones must be selected from the practice zones)", info_type = 0, info_list = info_list, fp = fp)
                    config_param = redefine_config(ext_info, info_list = info_list, fp = fp)
                    return config_param
        
        
        #各ゾーンのコンピュートノードの数が範囲に収まっているかどうか確認 & コンピュートノードの合計数を取得
        node_sum = 0
        for i in range(len(config_zones)):
            #コンピュートノード数が最小値以上になっているかどうか確認
            #ヘッドノードがあるゾーンの場合は、maximum-1以上
            if(config_zones[i] == config_param["Zone"]["Head Zone"]):
                max_node = ext_info["Zone"][config_zones[i]]["maximum"] - 1
            #ヘッドノードがないゾーンの場合は、maximum以上
            else:
                max_node = ext_info["Zone"][config_zones[i]]["maximum"]
                
            #コンピュートノード数が最大値以下になっているかどうか確認
            min_node = ext_info["Zone"][config_zones[i]]["minimum"]
            nodes = config_param["Zone"]["Zone"][config_zones[i]]
            if(min_node > nodes or nodes > max_node):
                logger.error("ConfigError: number of compute nodes in " + config_zones[i] + " must be set from " + str(min_node) + " to " + str(max_node))
                _ = printout("ConfigError: number of compute nodes in " + config_zones[i] + " must be set from " + str(min_node) + " to " + str(max_node), info_type = 0, info_list = info_list, fp = fp)
                config_param = redefine_config(ext_info, info_list = info_list, fp = fp)
                return config_param
            
            #各ゾーンのコンピュートノードの合計数を取得
            node_sum += nodes
            
        #各ゾーンのコンピュートノードの合計数とComputeの設定におけるコンピュートノードの数が一致しているかどうか確認
        if(config_param["Compute"]["Compute number"] != node_sum):
            logger.error("ConfigError: number of compute nodes in Zone params does not match to that in Compute params")
            _ = printout("ConfigError: number of compute nodes in Zone params does not match to that in Compute params", info_type = 0, info_list = info_list, fp = fp)
            config_param = redefine_config(ext_info, info_list = info_list, fp = fp)
            return config_param
    
    #zoneが設定がされていない場合
    else:
        #本番ゾーンの中で設置できるノードの数が最大のゾーンと最大ノード数を取得
        max_zone_node = 0
        for k,v in ext_info["Zone"].items():
            if(max_zone_node < v["maximum"]-1 and v["Type"] == "practice"):
                max_zone_node = v["maximum"]-1
                max_zone = k
        
        #Computeに設定されたノード数が単一ゾーンに設置できるゾーン数であるかどうか確認
        if(max_zone_node < config_param["Compute"]["Compute number"]):
            logger.error("ConfigError: specified number of compute nodes (" + str(config_param["Compute"]["Compute number"]) + ") must be lower than " + str(max_zone_node))
            _ = printout("ConfigError: specified number of compute nodes (" + str(config_param["Compute"]["Compute number"]) + ") must be lower than " + str(max_zone_node), info_type = 0, info_list = info_list, fp = fp)
            config_param = redefine_config(ext_info, info_list = info_list, fp = fp)
            return config_param
        else:
            config_param["Zone"] = {}
            config_param["Zone"]["Zone"] = {}
            config_param["Zone"]["Zone"][max_zone] = config_param["Compute"]["Compute number"]
            config_param["Zone"]["Head Zone"] = max_zone
            logger.info("Info: Zone and Head Zone is automatically set to " + str(max_zone))
            _ = printout("Info: Zone and Head Zone is automatically set to " + str(max_zone), info_type = 0, info_list = info_list, fp = fp)
    
    #Monitorに関するcheck
    #Monitorが設定されているかどうか
    logger.debug('Checking params of monitor')
    if("Monitor" in config_param):
        #Monitorを使用する場合
        if(config_param["Monitor"]["Monitor"] == True):
            #Monitor typeが指定されているか確認
            if("Monitor type" not in config_param["Monitor"]):
                logger.error("ConfigError: monitor type must be specified")
                _ = printout("ConfigError: monitor type must be specified", info_type = 0, info_list = info_list, fp = fp)
                config_param = redefine_config(ext_info, info_list = info_list, fp = fp)
                return config_param
            
            #Monitor levelが指定されているか確認
            if("Monitor level" not in config_param["Monitor"]):
                logger.error("ConfigError: monitor level must be specified")
                _ = printout("ConfigError: monitor level must be specified", info_type = 0, info_list = info_list, fp = fp)
                config_param = redefine_config(ext_info, info_list = info_list, fp = fp)
                return config_param
            
            #Monitor方法の指定を確認
            opt_list = list(ext_info["Monitor"].keys())
            if(config_param["Monitor"]["Monitor type"] not in opt_list):
                logger.error("ConfigError: monitor method must be select from " + ",".join(opt_list))
                _ = printout("ConfigError: monitor method must be select from " + ",".join(opt_list), info_type = 0, info_list = info_list, fp = fp)
                config_param = redefine_config(ext_info, info_list = info_list, fp = fp)
                return config_param
            
            #Monitorレベルの指定を確認
            opt_list = list(ext_info["Monitor_level"]["level"])
            if(config_param["Monitor"]["Monitor level"] not in opt_list):
                logger.error("ConfigError: monitor level must be select a value between " + str(min(opt_list)) + " and " + str(max(opt_list)))
                _ = printout("ConfigError: monitor level must be select a value between " + str(min(opt_list)) + " and " + str(max(opt_list)), info_type = 0, info_list = info_list, fp = fp)
                config_param = redefine_config(ext_info, info_list = info_list, fp = fp)
                return config_param
    #Monitorが設定されていない場合は自動指定
    else:
        config_param["Monitor"] = {}
        config_param["Monitor"]["Monitor"] = False
        logger.info("Info: monitor is automatically set to " + str(config_param["Monitor"]["Monitor"]))
        _ = printout("Info: monitor is automatically set to " + str(config_param["Monitor"]["Monitor"]), info_type = 0, info_list = info_list, fp = fp)
    
    
    #Computeに関するCheck
    logger.debug('Checking params of Compute')
    zone_list = config_param["Zone"]["Zone"]
    config_param_temp, index = server_val(config_param["Compute"]["Compute node"], ext_info, zone_list, info_list = [1,0,0,0], fp = "")
    if(index == 1):
        return config_param_temp
    else:
        config_param["Compute"]["Compute node"] = config_param_temp
        
    #Compute switchの自動設定
    if("Compute switch" not in config_param["Compute"]):
        config_param["Compute"]["Compute switch"] == False
        
    #コンピュートノード数が1の場合にCompute switchが指定されていないかどうかの確認
    if(config_param["Compute"]["Compute number"] == 1 and config_param["Compute"]["Compute switch"] == True):
        logger.error("ConfigError: compute switch cannot be specify if the number of compute nodes is 1")
        _ = printout("ConfigError: compute switch cannot be specify if the number of compute nodes is 1", info_type = 0, info_list = info_list, fp = fp)
        config_param = redefine_config(ext_info, info_list = info_list, fp = fp)
        return config_param
    
    logger.debug('Checking params of Head')
    #Headに関するCheck
    config_param_temp, index = server_val(config_param["Head"], ext_info, zone_list, info_list = [1,0,0,0], fp = "")
    if(index == 1):
        return config_param_temp
    else:
        config_param["Head"] = config_param_temp
    
        
    return config_param
        
    
    
    
def server_val(config_param, ext_info, zone_list, info_list = [1,0,0,0], fp = ""):
    opt_list_str = list(ext_info["Server"].keys())
    opt_list = [int(opt_list_str[i]) for i in range(len(opt_list_str))]
    if(config_param["Node"]["core"] not in opt_list):
        logger.error("ConfigError: server core must be select from " + ",".join(opt_list_str))
        _ = printout("ConfigError: server core must be select from " + ",".join(opt_list_str), info_type = 0, info_list = info_list, fp = fp)
        config_param = redefine_config(ext_info, info_list = info_list, fp = fp)
        return config_param, 1
    
    #memory数が候補値から選択されているかどうかの確認
    opt_list_str = list(ext_info["Server"][str(config_param["Node"]["core"])].keys())
    opt_list = [int(opt_list_str[i]) for i in range(len(opt_list_str))]
    if(config_param["Node"]["memory"] not in opt_list):
        logger.error("ConfigError: server memory must be select from " + ",".join(opt_list_str))
        _ = printout("ConfigError: server memory must be select from " + ",".join(opt_list_str), info_type = 0, info_list = info_list, fp = fp)
        config_param = redefine_config(ext_info, info_list = info_list, fp = fp)
        return config_param, 1
    
    #ノードPlanIDが設定されていない場合は、memoryとcore数から指定する
    if("NodePlan" not in config_param["Node"]):
        config_param["Node"]["NodePlan"] = ext_info["Server"][str(config_param["Node"]["core"])][str(config_param["Node"]["memory"])]
    
    #Diskのtypeが候補値から選択されているかどうかの確認
    opt_list = list(ext_info["Disk"].keys())
    if(config_param["Disk"]["Type"] not in opt_list):
        logger.error("ConfigError: disk type must be select from " + ",".join(opt_list))
        _ = printout("ConfigError: disk type must be select from " + ",".join(opt_list), info_type = 0, info_list = info_list, fp = fp)
        config_param = redefine_config(ext_info, info_list = info_list, fp = fp)
        return config_param, 1
        
    #DiskのSizeが候補値から選択されているかどうかの確認
    opt_list = ext_info["Disk"][config_param["Disk"]["Type"]]
    opt_list_str = [str(opt_list[i]) for i in range(len(opt_list))]
    if(config_param["Disk"]["Size"] not in opt_list):
        logger.error("ConfigError: disk size must be select from " + ",".join(opt_list_str))
        _ = printout("ConfigError: disk size must be select from " + ",".join(opt_list_str), info_type = 0, info_list = info_list, fp = fp)
        config_param = redefine_config(ext_info, info_list = info_list, fp = fp)
        return config_param, 1
    
    #Connection typeが候補値から選択されているかどうかの確認
    opt_list = ext_info["Connection"]
    if(config_param["Connection type"] not in opt_list):
        logger.error("ConfigError: connection type must be select from " + ",".join(opt_list))
        _ = printout("ConfigError: connection type must be select from " + ",".join(opt_list), info_type = 0, info_list = info_list, fp = fp)
        config_param = redefine_config(ext_info, info_list = info_list, fp = fp)
        return config_param, 1
    
    #OSが候補値から選択されているかどうかの確認
    opt_list = list(ext_info["OS"].keys())
    if(config_param["OS"]["name"] not in opt_list):
        logger.error("ConfigError: os must be select from " + ",".join(opt_list))
        _ = printout("ConfigError: os must be select from " + ",".join(opt_list), info_type = 0, info_list = info_list, fp = fp)
        config_param = redefine_config(ext_info, info_list = info_list, fp = fp)
        return config_param, 1
        
    #OSPlanが設定されていな場合は、自動設定
    if("OSPlan" not in config_param["OS"].keys()):
        config_param["OS"]["OSPlan"] = {}
        for zone in zone_list:
            config_param["OS"]["OSPlan"][zone] = ext_info["OS"][config_param["OS"]["name"]][zone]
    #設定されている場合は、OS nameとmatchしているかを確認
    else:
        for zone in zone_list:
            if(zone in config_param["OS"]["OSPlan"]):
                if(ext_info["OS"][config_param["OS"]["name"]][zone] != config_param["OS"]["OSPlan"][zone]):
                    logger.error("ConfigError: OSPlan does not match to OS. Please confirm os info")
                    _ = printout("ConfigError: OSPlan does not match to OS. Please confirm os info", info_type = 0, info_list = info_list, fp = fp)
                    config_param = redefine_config(ext_info, info_list = info_list, fp = fp)
                    return config_param, 1
        
            else:
                config_param["OS"]["OSPlan"][zone] = ext_info["OS"][config_param["OS"]["name"]][zone]
    
    return config_param, 0
    
    

def config_validation(ext_info, config_param, info_list = [1,0,0,0], fp = ""):
    logger.debug('load config checker')
    checker = load_config_checker(info_list = info_list, fp = fp)
    all_zone = list(ext_info["Zone"].keys())
    main_checker = checker["main checker"]
    
    main_checker["properties"]["NFS"]["properties"]["NFS zone"]["properties"] = dict(zip(all_zone, [checker["NFS_zone_checker"] for i in range(len(all_zone))]))
    main_checker["properties"]["Zone"]["properties"]["Zone"]["properties"] = dict(zip(all_zone, [checker["Zone_checker"] for i in range(len(all_zone))]))
    main_checker["properties"]["Compute"]["properties"]["Compute node"]["properties"]["OS"]["properties"]["OSPlan"]["properties"] = dict(zip(all_zone, [checker["OS_checker"] for i in range(len(all_zone))]))
    main_checker["properties"]["Head"]["properties"]["OS"]["properties"]["OSPlan"]["properties"] = dict(zip(all_zone, [checker["OS_checker"] for i in range(len(all_zone))]))
    
    try:
        logger.debug('Checking config params')
        _ = printout("Checking config params ...", info_type = 0, info_list = info_list, fp = fp)
        logger.debug('Checking the type and existence of config params')
        validate(config_param, main_checker)
        logger.debug('Checking details of config params')
        checking_config_details(ext_info, config_param, info_list = info_list, fp = fp)
        
        
    except ValidationError as e:
        logger.error('ConfigError: definition of config parameters is wrong')
        logger.error(e.message)
        
        _ = printout("ConfigError: definition of config parameters is wrong", info_type = 0, info_list = info_list, fp = fp)
        _ = printout(e.message, info_type = 0, info_list = info_list, fp = fp)
        
        config_param = redefine_config(ext_info, info_list = info_list, fp = fp)
    
    return config_param







































