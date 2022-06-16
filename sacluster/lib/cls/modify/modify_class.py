
import sys
import os
import datetime
import logging
from tqdm import tqdm
import copy
import numpy as np
import time
import re
from concurrent import futures

logger = logging.getLogger("sacluster").getChild(os.path.basename(__file__))

path = "../../.."
os.chdir(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(path + "/lib/others")
from API_method import get, post, put, delete
from info_print import printout

sys.path.append(path + "/lib/def_conf")
from config_function import conf_pattern_2

class modify_sacluster:
    
    def __init__(self, cluster_info, cluster_id, auth_res, ext_info, fp = "", info_list = [1,0,0,0], api_index = True, max_workers = 1):
        self.cluster_info = cluster_info
        self.cluster_id = cluster_id
        self.auth_res = auth_res
        self.ext_info = ext_info
        self.fp = fp
        self.info_list = info_list
        self.api_index = api_index
        self.max_workers = max_workers
        #[k for k in self.cluster_info.keys()]
        self.zone_list = [zone_list for zone_list in self.cluster_info["clusterparams"]["server"].keys()]
        
        #if "nfs" in self.cluster_info[cluster_id]["cluster_params"]:
        if self.cluster_info["clusterparams"]["nfs"] != None:
            self.nfs_zones = list(self.cluster_info["clusterparams"]["nfs"].keys())
        
        self.max_node_num = 0
        self.proactice_zones = []
        for zone in ext_info["Zone"]:
            if(self.ext_info["Zone"][zone]["Type"] == "practice" and self.ext_info["Zone"][zone]["maximum"] > 0):
                self.max_node_num += self.ext_info["Zone"][zone]["maximum"]
                self.proactice_zones.append(zone)
        
        self.current_zone_max_num = 0
        self.head_zone_num = 0
        for zone in self.zone_list:
            self.current_zone_max_num += self.ext_info["Zone"][zone]["maximum"]
            if "head" in self.cluster_info["clusterparams"]["server"][zone].keys():
                self.head_zone = zone
                self.head_zone_num = self.ext_info["Zone"][zone]["maximum"]
        
        self.url_list = {}
        for zone in ext_info["Zone"]:
            self.url_list[zone] = "https://secure.sakura.ad.jp/cloud/zone/"+ zone +"/api/cloud/1.1"

        self.head_url = "https://secure.sakura.ad.jp/cloud/zone/"+ self.head_zone +"/api/cloud/1.1"

        self.sub_url = ["/server","/disk","/switch","/interface","/bridge","/tag","/appliance","/power"]

        self.date_modified = "Date modified:" + str(datetime.datetime.now().strftime("%Y_%m_%d"))
        
    def __call__(self):
        
        self.show_current_states()
        if(self.mod_type == "1"):
            self.modify_compute_node_number()
        elif(self.mod_type == "2"):
            self.modify_back_switch()
        elif(self.mod_type == "3"):
            self.modify_core_and_memory()
        else:
            _ = printout("Warning: the input must be a number from 1 to 3.", info_type = 0, info_list = self.info_list, fp = self.fp)
            
        printout("Finished modifying the cluster", info_type = 0, info_list = self.info_list, fp = self.fp)
        
            
    def show_current_states(self):
        printout('' , info_type = 0, info_list = self.info_list, fp = self.fp)
        text_len = len('#' *25 + ' current state ' + '#' *25)
        printout('#' *25 + ' current state ' + '#' *25, info_type = 0, info_list = self.info_list, fp = self.fp)
        
        compute_number = sum([len(val["compute"]) for key, val in self.cluster_info["clusterparams"]["server"].items()])
        printout(' ' * 10 + 'The number of compute node:'.ljust(35, ' ') + str(compute_number), info_type = 0, info_list = self.info_list, fp = self.fp)
        
        switch_back_zone = []
        for key, val in self.cluster_info["clusterparams"]["switch"].items():
            #if("back" in val):
            if(self.cluster_info["clusterparams"]["switch"][key]["back"] != None):
                switch_back_zone.append(key)
        
        printout('' , info_type = 0, info_list = self.info_list, fp = self.fp)
        if(len(switch_back_zone) == 0):
            printout(' ' * 10 +'Switch of back area:'.ljust(35, ' ') + 'False', info_type = 0, info_list = self.info_list, fp = self.fp)
        elif(len(self.cluster_info["clusterparams"]["switch"]) == len(switch_back_zone)):
            printout(' ' * 10 +'Switch of back area:'.ljust(35, ' ') + 'True', info_type = 0, info_list = self.info_list, fp = self.fp)
        elif(len(self.cluster_info["clusterparams"]["switch"]) > len(switch_back_zone)):
            printout(' ' * 10 +'Switch of back area:'.ljust(35, ' ') + 'Some zones are True', info_type = 0, info_list = self.info_list, fp = self.fp)
            printout(' ' * 10 +'(' + ",".join(switch_back_zone) + ')', info_type = 0, info_list = self.info_list, fp = self.fp)
           
        node_plan = {}
        for zone, val in self.cluster_info["clusterparams"]["server"].items():
           if("head" in val):
               head_zone = zone
               head_core = val["head"]["node"]["core"]
               head_memory = val["head"]["node"]["memory"]
        
           for num, val_comp in val["compute"].items():
               if(str(val_comp["node"]["core"]) + "-" + str(val_comp["node"]["memory"]) not in node_plan):
                   node_plan[str(val_comp["node"]["core"]) + "-" + str(val_comp["node"]["memory"])] = 0
               else:
                   node_plan[str(val_comp["node"]["core"]) + "-" + str(val_comp["node"]["memory"])] += 1
        
            
        printout('' , info_type = 0, info_list = self.info_list, fp = self.fp)
        printout(' ' * 10 + 'Node information' , info_type = 0, info_list = self.info_list, fp = self.fp)
        printout(' ' * 10 + '((Head node))' , info_type = 0, info_list = self.info_list, fp = self.fp)
        printout(' ' * 10 + 'Core:'.ljust(35, ' ') + str(head_core), info_type = 0, info_list = self.info_list, fp = self.fp)
        printout(' ' * 10 +'Memory:'.ljust(35, ' ') + str(head_memory), info_type = 0, info_list = self.info_list, fp = self.fp)
        
        printout('' , info_type = 0, info_list = self.info_list, fp = self.fp)
        printout(' ' * 10 + '((Compute node))' , info_type = 0, info_list = self.info_list, fp = self.fp)
        
        if(len(node_plan) == 1):
            for key, val in node_plan.items():
                text = ' ' * 10 +'Core:'.ljust(35, ' ') + str(key.split("-")[0])
                printout(text, info_type = 0, info_list = self.info_list, fp = self.fp)
                text = ' ' * 10 +'Memory:'.ljust(35, ' ') + str(key.split("-")[1])
                printout(text, info_type = 0, info_list = self.info_list, fp = self.fp)
        else:
            count = 0
            for key, val in node_plan.items():
                printout(' ' * 10 +'compute node type ' + str(count), info_type = 0, info_list = self.info_list, fp = self.fp)
                printout(' ' * 10 +'Core:'.ljust(35, ' ') + str(key.split("-")[0]) , info_type = 0, info_list = self.info_list, fp = self.fp)
                printout(' ' * 10 +'Memory:'.ljust(35, ' ') + str(key.split("-")[1]), info_type = 0, info_list = self.info_list, fp = self.fp)
                count += 1
        
        printout('#' * text_len, info_type = 0, info_list = self.info_list, fp = self.fp)
        
        self.mod_type = self.answer_response(' \n<<Contents to modify>>\n1. The number of compute node\n2. Switch of back area\n3. Core or memory of nodes', ["1", "2", "3"], "1 to 3", input_comment = "Please input a content number", opp = 1)
        
    
    def modify_back_switch(self):
        switch_back_zone = []
        for key, val in self.cluster_info["clusterparams"]["switch"].items():
            #if("back" in val):
            if(self.cluster_info["clusterparams"]["switch"][key]["back"] != None):
                switch_back_zone.append(key)
        
        printout('' , info_type = 0, info_list = self.info_list, fp = self.fp)
        if(len(switch_back_zone) == 0):
            printout('Switch of back area is False in the current state', info_type = 0, info_list = self.info_list, fp = self.fp)
            input_val = self.answer_response("Can a switch be installed in the back area?", ["yes", "y", "no", "n"], "yes/y or no/n")
            
            if(input_val == "yes" or input_val == "y"):
                self.bar = tqdm(total = 100)
                self.bar.set_description('Progress rate')
                self.progress_sum = 0
                if(len(self.zone_list) > 1):
                    progress_val = 20
                else:
                    progress_val = 35
                
                for zone in self.zone_list:
                    self.cluster_info["clusterparams"]["switch"][zone]["back"] = {}
                    self.cluster_info["clusterparams"]["switch"][zone]["back"]["id"] = self.create_switch(zone)
                    self.progress_bar(int(30 / len(self.zone_list)))
                    node_num = len(self.cluster_info["clusterparams"]["server"][zone]["compute"])
                    for key, val in self.cluster_info["clusterparams"]["server"][zone]["compute"].items():
                        nic_id = self.add_interface(zone, val["node"]["id"])
                        self.progress_bar(int(progress_val / (len(zone) * node_num)))
                            
                        self.cluster_info["clusterparams"]["server"][zone]["compute"][key]["nic"]["back"] = {}
                        self.cluster_info["clusterparams"]["server"][zone]["compute"][key]["nic"]["back"]["id"] = nic_id
                        self.connect_switch(zone, self.cluster_info["clusterparams"]["switch"][zone]["back"]["id"], self.cluster_info["clusterparams"]["server"][zone]["compute"][key]["nic"]["back"]["id"])
                        self.progress_bar(int(progress_val / (len(zone) * node_num)))
                        
                if(len(self.zone_list) > 1):
                    bridge_id = self.create_bridge()
                    self.progress_bar(10)
                    self.cluster_info["clusterparams"]["bridge"]["back"] = {}
                    self.cluster_info["clusterparams"]["bridge"]["back"]["id"] = bridge_id
                    
                    for zone in self.zone_list:
                        self.progress_bar(int(20/len(self.zone_list)))
                        _ = self.connect_bridge_switch(zone, self.cluster_info["clusterparams"]["switch"][zone]["back"]["id"], self.cluster_info["clusterparams"]["bridge"]["back"]["id"])
                        
                self.bar.update(100 - self.progress_sum)
                self.bar.close()
                        
            else:
                printout('Please start the operation over from the beginning.', info_type = 0, info_list = self.info_list, fp = self.fp)
                sys.exit()
            
            
        elif(len(self.cluster_info["clusterparams"]["switch"]) == len(switch_back_zone)):
            printout('Switch of back area is True in the current state', info_type = 0, info_list = self.info_list, fp = self.fp)
            input_val = self.answer_response("Can a switch be deleted in the back area?", ["yes", "y", "no", "n"], "yes/y or no/n")
            
            if(input_val == "yes" or input_val == "y"):
                self.bar = tqdm(total = 100)
                self.bar.set_description('Progress rate')
                self.progress_sum = 0
                if(len(self.zone_list) > 1):
                    progress_val = 20
                else:
                    progress_val = 50
                    
                for zone in self.zone_list:
                    node_num = len(self.cluster_info["clusterparams"]["server"][zone]["compute"])
                    for key, val in self.cluster_info["clusterparams"]["server"][zone]["compute"].items():
                        self.dis_connect_server_switch(zone, self.cluster_info["clusterparams"]["server"][zone]["compute"][key]["nic"]["back"]["id"])
                        self.progress_bar(int(progress_val / (len(zone) * node_num)))
                            
                        self.delete_interface(zone, self.cluster_info["clusterparams"]["server"][zone]["compute"][key]["nic"]["back"]["id"])
                        self.progress_bar(int(progress_val / (len(zone) * node_num)))
                        self.cluster_info["clusterparams"]["server"][zone]["compute"][key]["nic"]["back"] = None
                        
                for zone in self.zone_list:
                    if(len(self.zone_list) > 1):
                        self.disconnect_bridge_switch(zone, self.cluster_info["clusterparams"]["switch"][zone]["back"]["id"])
                        self.progress_bar(int(20/len(self.zone_list)))
                    self.delete_switch(zone, self.cluster_info["clusterparams"]["switch"][zone]["back"]["id"])
                    self.cluster_info["clusterparams"]["switch"][zone]["back"] = None
                    self.progress_bar(int(30 / len(self.zone_list)))
                      
                if(len(self.zone_list) > 1):
                    self.delete_bridge(self.cluster_info["clusterparams"]["bridge"]["back"]["id"])
                    self.cluster_info["clusterparams"]["bridge"]["back"] = None
                    self.progress_bar(10)
                    
                self.bar.update(100 - self.progress_sum)
                self.bar.close()
                    
            else:
                printout('Please start the operation over from the beginning.', info_type = 0, info_list = self.info_list, fp = self.fp)
                sys.exit()
            
        elif(len(self.cluster_info["clusterparams"]["switch"]) > len(switch_back_zone)):
            printout('This cluster is not a target of sacluster operation', info_type = 0, info_list = self.info_list, fp = self.fp)
            #input_val = self.mod_type = self.answer_response(" \n<<select option>>\n1. Delete the switch of back area in " + ",".join(switch_back_zone) + "\n2. Add switches in areas other than " + ",".join(switch_back_zone), ["1", "2"], "1 or 2", input_comment = "Please input a opption number", opp = 1)
        
    #CoreとMemory数の変更
    def modify_core_and_memory(self):
        node_type = ["head node", "compute nodes"][int(self.answer_response(' \nPlease select the node type to modify the setting\n1. Head node\n2. Compute nodes', ["1", "2"], "1 or 2", input_comment = "Please input a number", opp = 1)) - 1]
        node_plan, core_plan, memory_plan = self.core_memory_setting(node_type)
        
        if(node_type == "head node"):
            self.bar = tqdm(total = 100)
            self.bar.set_description('Progress rate')
            self.progress_sum = 0
            
            self.change_node_plan(self.head_zone, self.cluster_info["clusterparams"]["server"][self.head_zone]["head"]["node"]["id"], node_plan)
            
            self.bar.update(100)
            self.bar.close()
        else:
            while(True):
                self.bar = tqdm(total = 100)
                self.bar.set_description('Progress rate')
                self.progress_sum = 0
                future = []
                with futures.ThreadPoolExecutor(max_workers = self.max_workers, thread_name_prefix="thread") as executor:
                    for zone in self.zone_list:
                        for i in self.cluster_info["clusterparams"]["server"][zone]["compute"].keys():
                            logger.debug(self.cluster_info["clusterparams"]["server"][zone]["compute"][i]["node"]["id"])
                            logger.debug(node_plan)
                            future.append(executor.submit(self.change_node_plan, zone, self.cluster_info["clusterparams"]["server"][zone]["compute"][i]["node"]["id"], node_plan, ind = 1))
                    
                    future_result = []
                    for f in futures.as_completed(future):
                        if(f.result()[0] == True):
                            self.progress_bar(int(100/(len(self.zone_list) * len(self.cluster_info["clusterparams"]["server"][zone]["compute"].keys()))))
                        #self.cluster_info["clusterparams"]["server"][zone]["compute"][i]["node"]["id"] = f.result()[2]
                            
                        future_result.append(f.result()[0])
                        
                    future_msg = [f.result()[1] for f in future if(f.result()[0] == False and f.result()[1] != "")]
                    if(len(future_msg) > 0):
                        future_msg = future_msg[0]
                    
                    if False in future_result:
                        printout("\n".join(future_msg), info_type = 0, info_list = self.info_list, fp = self.fp)
                        temp = conf_pattern_2("Try again??", ["y", "n", "yes", "no"], "no", info_list = self.info_list, fp = self.fp)
                        printout("", info_type = 0, info_list = self.info_list, fp = self.fp)
                        logger.info(temp)
                        if temp == "no" or temp == "n":
                            printout("Stop processing.", info_type = 0, info_list = self.info_list, fp = self.fp, overwrite = True)
                            self.bar.close()
                            sys.exit()
                        else:
                            self.bar.close()
                    else:
                        break
                    
            self.bar.update(100 - self.progress_sum)
            self.bar.close()
            
    def modify_compute_node_number(self):
        while(True):
            new_compute_setting, num_comp = self.setting_compute_node()
           
            printout('', info_type = 0, info_list = self.info_list, fp = self.fp)
            printout('#' * 10 + ' Setting the number of compute node ' + '#' *10, info_type = 0, info_list = self.info_list, fp = self.fp)
            printout(' ' * 5 + 'The number of compute nodes: ' + str(num_comp) + ' ' * 5, info_type = 0, info_list = self.info_list, fp = self.fp)
            for k,v in new_compute_setting.items():
                printout(' ' * 5 + 'The number of compute nodes in ' + str(k) + ': ' + str(v) + ' ' * 5, info_type = 0, info_list = self.info_list, fp = self.fp)
            printout('#' *10 + '#' *len(' Setting the number of compute nodes ') + '#' *10, info_type = 0, info_list = self.info_list, fp = self.fp)
           
            res = self.answer_response("Are the above settings correct?", ["yes", "y", "no", "n"], "yes/y or no/n")
            
            if(res == "yes" or res == "y"):
                username, password = self.setting_middle(new_compute_setting)
                break
            
        self.bar = tqdm(total = 100)
        self.bar.set_description('Progress rate')
        self.progress_sum = 0
        self.change_compute_number(new_compute_setting, username, password)
        self.bar.update(100 - self.progress_sum)
        self.bar.close()
           
            
    
    def setting_compute_node(self):
        node_number = {}
        printout('', info_type = 0, info_list = self.info_list, fp = self.fp)
        if(self.ext_info["Zone"][self.head_zone]["Type"] == "practice"):
            new_node_number = self.answer_response_node_number("Please input the number of compute nodes", 1, self.max_node_num + self.cluster_info["baseparams"]["compute_number"], self.cluster_info["baseparams"]["compute_number"], sp_type = 1)
        else:
            new_node_number = self.answer_response_node_number("Please input the number of compute nodes", 1, self.current_zone_max_num + self.cluster_info["baseparams"]["compute_number"], self.cluster_info["baseparams"]["compute_number"], sp_type = 1)
        
        
        if(new_node_number > self.cluster_info["baseparams"]["compute_number"]):
            if(new_node_number > self.current_zone_max_num + self.cluster_info["baseparams"]["compute_number"]):
                select_zones = list(set(self.proactice_zones) - set(self.zone_list))
                if(self.max_node_num + self.cluster_info["baseparams"]["compute_number"] == new_node_number):
                    for zone in self.proactice_zones:
                        node_number[zone] = self.ext_info["Zone"][zone]["maximum"]
                        
                else:
                    #ゾーンの追加
                    select_zones = list(set(self.proactice_zones) - set(self.zone_list))
                    printout('', info_type = 0, info_list = self.info_list, fp = self.fp)
                    printout('Info: the specified number of nodes cannot be installed in the current zone. Additional zones are needed', info_type = 0, info_list = self.info_list, fp = self.fp)
                    current_zone_node_num = self.current_zone_max_num + self.cluster_info["baseparams"]["compute_number"]
                    add_zone_list = []
                    count = 1
                    rem_min_node_num = min([self.ext_info["Zone"][zone]["maximum"] for zone in select_zones])
                    if((self.max_node_num + self.cluster_info["baseparams"]["compute_number"] - rem_min_node_num) < new_node_number):
                        add_zone_list.extend(select_zones)
                        for add_zone in add_zone_list:
                            current_zone_node_num += self.ext_info["Zone"][add_zone]["maximum"]
                        _ = printout("Info: Additional zones is automatically set to " + ",".join(add_zone_list), info_type = 0, info_list = self.info_list, fp = self.fp)
                        
                    else:
                        printout('', info_type = 0, info_list = self.info_list, fp = self.fp)
                        while(True):
                            add_zone = select_zones[int(self.answer_response_memory("Please select an additional zone " + str(count), select_zones, select_zones[0]))]
                            current_zone_node_num += self.ext_info["Zone"][add_zone]["maximum"]
                            add_zone_list.append(add_zone)
                            
                            if(current_zone_node_num >= new_node_number):
                                break
                    
                            select_zones = list(set(select_zones) - set([add_zone]))
                            count += 1
                    
                    zone_compute_num = {}
                    if(current_zone_node_num == new_node_number):
                        for zone in self.zone_list:
                            zone_compute_num[zone] = self.ext_info["Zone"][zone]["maximum"]
                            _ = printout("Info: The number of compute nodes in " + zone + " is automatically set to " + str(self.ext_info["Zone"][zone]["maximum"]), info_type = 0, info_list = self.info_list, fp = self.fp)
                             
                        for zone in add_zone_list:
                            zone_compute_num[zone] = self.ext_info["Zone"][zone]["maximum"]
                            _ = printout("Info: The number of compute nodes in " + zone + " is automatically set to " + str(self.ext_info["Zone"][zone]["maximum"]), info_type = 0, info_list = self.info_list, fp = self.fp)
                                
                
                    #for key, val in self.ext_info["Zone"].items():
                        #print(key + str(val["maximum"]))
                
                    else:
                        remain_node_num = new_node_number
                        for i in range(len(self.zone_list)):
                            min_val = remain_node_num - (sum([self.ext_info["Zone"][self.zone_list[j]]["maximum"] + len(self.cluster_info["clusterparams"]["server"][self.zone_list[j]]["compute"]) for j in range(i+1, len(self.zone_list))]) + sum([self.ext_info["Zone"][zone]["maximum"] for zone in add_zone_list]))
                            
                            if(min_val < 1):
                                min_val = 1
                            
                            max_val = self.ext_info["Zone"][self.zone_list[i]]["maximum"] + len(self.cluster_info["clusterparams"]["server"][self.zone_list[i]]["compute"])
                        
                            if(min_val != max_val):
                                node_number[self.zone_list[i]] = self.answer_response_node_number("Please input the number of compute nodes in " + str(self.zone_list[i]), min_val, max_val)
                            else:
                                node_number[self.zone_list[i]] = min_val
                                _ = printout("Info: The number of compute nodes in " + self.zone_list[i] + " is automatically set to " + str(node_number[self.zone_list[i]]), info_type = 0, info_list = self.info_list, fp = self.fp)
                                
                        
                            remain_node_num = remain_node_num - int(node_number[self.zone_list[i]])
                            
                        for i in range(len(add_zone_list)):
                            min_val = remain_node_num - sum([self.ext_info["Zone"][add_zone_list[j]]["maximum"] for j in range(i+1, len(add_zone_list))])
                            if(min_val < 1):
                                min_val = 1
                            
                            if(remain_node_num > self.ext_info["Zone"][add_zone_list[i]]["maximum"]):
                                max_val = self.ext_info["Zone"][add_zone_list[i]]["maximum"]
                            else:
                                max_val = remain_node_num
                            
                            if(min_val != max_val):
                                node_number[add_zone_list[i]] = self.answer_response_node_number("Please input the number of compute nodes in " + str(add_zone_list[i]), min_val, max_val)
                            else:
                                node_number[add_zone_list[i]] = min_val
                                _ = printout("Info: The number of compute nodes in " + add_zone_list[i] + " is automatically set to " + str(node_number[add_zone_list[i]]), info_type = 0, info_list = self.info_list, fp = self.fp)
                                
                            remain_node_num = remain_node_num - int(node_number[add_zone_list[i]])
            
            else:
                remain_node_num = new_node_number
                for i in range(len(self.zone_list)):
                    min_val = remain_node_num - sum([self.ext_info["Zone"][self.zone_list[j]]["maximum"] + len(self.cluster_info["clusterparams"]["server"][self.zone_list[j]]["compute"]) for j in range(i+1, len(self.zone_list))])
                    
                    if(min_val < 1):
                        min_val = 1
                    
                    if(remain_node_num > self.ext_info["Zone"][self.zone_list[i]]["maximum"]):
                        max_val = self.ext_info["Zone"][self.zone_list[i]]["maximum"]
                    else:
                        if(i +1 == len(self.zone_list)):
                            max_val = remain_node_num
                        else:
                            max_val = remain_node_num - 1
                        
                    if(min_val != max_val):
                        node_number[self.zone_list[i]] = self.answer_response_node_number("Please input the number of compute nodes in " + str(self.zone_list[i]), min_val, max_val)
                    else:
                        node_number[self.zone_list[i]] = min_val
                        _ = printout("Info: The number of compute nodes in " + self.zone_list[i] + " is automatically set to " + str(node_number[self.zone_list[i]]), info_type = 0, info_list = self.info_list, fp = self.fp)
                        
                    remain_node_num = remain_node_num - int(node_number[self.zone_list[i]])
                                
        elif(new_node_number < self.cluster_info["baseparams"]["compute_number"]):
            if(len(self.zone_list) == 1):
                node_number[self.zone_list[0]] = new_node_number
            else:
                order_zone = []
                order_num = []
                for zone in self.zone_list:
                    if(zone != self.head_zone and self.cluster_info["clusterparams"]["nfs"][zone] == None):
                        order_zone.append(zone)
                        order_num.append(self.ext_info["Zone"][zone]["maximum"] + len(self.cluster_info["clusterparams"]["server"][zone]["compute"]))
                        
                order_zone = [order_zone[i] for i in np.argsort(order_num)]
                order_num = np.sort(order_num)
                
                nfs_head_num = self.ext_info["Zone"][self.head_zone]["maximum"] + len(self.cluster_info["clusterparams"]["server"][self.head_zone]["compute"])
                nfs_zones = []
                for zone in list(self.cluster_info["clusterparams"]["nfs"].keys()):
                    if(zone != self.head_zone and self.cluster_info["clusterparams"]["nfs"][zone] != None):
                        nfs_head_num += self.ext_info["Zone"][zone]["maximum"] + len(self.cluster_info["clusterparams"]["server"][zone]["compute"])
                        nfs_zones.append(zone + " (nfs exists)")
                
                _ = printout("", info_type = 0, info_list = self.info_list, fp = self.fp) 
                if(nfs_head_num >= new_node_number):
                #if(self.ext_info["Zone"][self.head_zone]["maximum"] + len(self.cluster_info["clusterparams"]["server"][self.head_zone]["compute"]) >= new_node_number):
                    delete_zone = order_zone
                    if(delete_zone != []):
                        _ = printout("Info: The following zones will be deleted (" + ",".join(delete_zone) + ")", info_type = 0, info_list = self.info_list, fp = self.fp)
                    
                    use_zone = list(set(self.zone_list) - set(delete_zone))
                    
                    if(len(nfs_zones) != 0):
                        _ = printout("Info: The zone is automatically set to the following zones: " + self.head_zone + " (head zone)" + ", "  + ", ".join(nfs_zones), info_type = 0, info_list = self.info_list, fp = self.fp)
                    else:
                        _ = printout("Info: The zone is automatically set to the following zones: " + self.head_zone + " (head zone)", info_type = 0, info_list = self.info_list, fp = self.fp) 
                
                else:
                    count = 1
                    while(True):
                        if(sum(order_num[count:]) + nfs_head_num < new_node_number):
                            break
                        count += 1 
                
                    delete_zone = order_zone[:count - 1]
                    use_zone = list(set(self.zone_list) - set(delete_zone))
                    other_zone = list(set(use_zone) - set(nfs_zones) - set([self.head_zone]))
                    
                    if(delete_zone != []):
                        _ = printout("Info: The following zones will be deleted (" + ",".join(delete_zone) + ")", info_type = 0, info_list = self.info_list, fp = self.fp)
                    if(len(nfs_zones) != 0):
                        if(len(other_zone) != 0):
                            _ = printout("Info: The zone is automatically set to the following zones: " + self.head_zone + " (head zone)" + ", "  + ", ".join(nfs_zones) + "," + ",".join(other_zone), info_type = 0, info_list = self.info_list, fp = self.fp)
                        else:
                            _ = printout("Info: The zone is automatically set to the following zones: " + self.head_zone + " (head zone)" + ", "  + ", ".join(nfs_zones), info_type = 0, info_list = self.info_list, fp = self.fp)                       
                    else:
                        if(len(other_zone) != 0):
                            _ = printout("Info: The zone is automatically set to the following zones: " + self.head_zone + " (head zone)" + "," + ",".join(other_zone), info_type = 0, info_list = self.info_list, fp = self.fp) 
                        else:
                            _ = printout("Info: The zone is automatically set to the following zones: " + self.head_zone + " (head zone)", info_type = 0, info_list = self.info_list, fp = self.fp) 
                    
                remain_node_num = new_node_number
                
                for zone in delete_zone:
                    node_number[zone] = 0
                    
                for i in range(len(use_zone)):
                    if(remain_node_num == 0):
                        node_number[use_zone[i]] = 0
                        _ = printout("Info: The number of compute nodes in " + use_zone[i] + " is automatically set to " + str(node_number[use_zone[i]]), info_type = 0, info_list = self.info_list, fp = self.fp)
                    else:
                        min_val = remain_node_num - sum([self.ext_info["Zone"][use_zone[j]]["maximum"] + len(self.cluster_info["clusterparams"]["server"][use_zone[j]]["compute"]) for j in range(i+1, len(use_zone))])
                        if(min_val < 1):
                            min_val = 1
                    
                        if(remain_node_num > self.ext_info["Zone"][use_zone[i]]["maximum"]):
                            max_val = self.ext_info["Zone"][use_zone[i]]["maximum"]
                        else:
                            max_val = remain_node_num
        
                        if(min_val != max_val):
                            node_number[use_zone[i]] = self.answer_response_node_number("Please input the number of compute nodes in " + str(use_zone[i]), min_val, max_val)
                        else:
                            node_number[use_zone[i]] = min_val
                            _ = printout("Info: The number of compute nodes in " + use_zone[i] + " is automatically set to " + str(node_number[use_zone[i]]), info_type = 0, info_list = self.info_list, fp = self.fp)
                                
                        remain_node_num = remain_node_num - int(node_number[use_zone[i]])
                    
        #self.change_compute_number_zone(node_number)
        return node_number, new_node_number
    
    def setting_middle(self, new_compute_setting):
        username = None
        password = None
        inc_zones = []
        for zone, comp_num in new_compute_setting.items():
            if(zone not in self.cluster_info["clusterparams"]["server"] and comp_num > 0):
                inc_zones.append(zone)
            else:
                if(len(self.cluster_info["clusterparams"]["server"][zone]["compute"]) < comp_num):
                    inc_zones.append(zone)
                
        if(len(inc_zones) != 0):
            _ = printout("In the following zones, the number of compute nodes will increase, so please specify the password and username for the new compute nodes. (" + ", ".join(inc_zones) + ")", info_type = 0, info_list = self.info_list, fp = self.fp)
            username, password = self.set_app_params()
                
        return username, password
    
    def input_username(self):
        re_alnum = re.compile(r'^[a-z]{1}[-a-z0-9]{0,30}$')
    
        while(True): 
            username = printout("[username] >> ", info_type = 1, info_list = self.info_list, fp = self.fp)
            ans = re.search(re_alnum, username)
            
            if(ans != None):
                return username
                
            else:
                logger.debug('The username is wrong')
                printout('The username is wrong. Username must be 32 characters long and consist of numbers, lowercase letters, and hyphens (Initial is a lowercase letter).', info_type = 0, info_list = self.info_list, fp = self.fp)

    
    def set_app_params(self):
        logger.debug('setting username and password')
        
        username = self.input_username()
        #username = printout("[username] >> ", info_type = 1, info_list = self.info_list, fp = self.fp).replace(" ","")
        password = printout("[password] >> ", info_type = 1, info_list = self.info_list, fp = self.fp).replace(" ","")
        printout("", info_type = 0, info_list = self.info_list, fp = self.fp).replace(" ","")
        printout("", info_type = 0, info_list = self.info_list, fp = self.fp).replace(" ","")
            
        if(username == ""):
            logger.info('username and password are automatically set to sacloud')
            username = "sacloud"
            password = "sacloud"
        
        return username, password
                
                
    def change_compute_number(self, new_setting, username, password):
        if(len(new_setting) > len(self.zone_list)):
            if(len(self.zone_list) == 1 and len(new_setting) == 2 and self.cluster_info["clusterparams"]["bridge"]["front"] == None):
                self.cluster_info["clusterparams"]["bridge"]["front"] = {}
                self.cluster_info["clusterparams"]["bridge"]["front"]["id"] = self.create_bridge()
                self.progress_bar(3)
                self.connect_bridge_switch(self.head_zone, self.cluster_info["clusterparams"]["switch"][self.head_zone]["front"]["id"], self.cluster_info["clusterparams"]["bridge"]["front"]["id"])
                self.progress_bar(4)
                
                if(self.cluster_info["clusterparams"]["switch"][self.zone_list[0]]["back"] != None and self.cluster_info["clusterparams"]["bridge"]["back"] == None):
                    self.cluster_info["clusterparams"]["bridge"]["back"] = {}
                    self.cluster_info["clusterparams"]["bridge"]["back"]["id"] = self.create_bridge()
                    self.progress_bar(3)
                    self.connect_bridge_switch(self.head_zone, self.cluster_info["clusterparams"]["switch"][self.head_zone]["back"]["id"], self.cluster_info["clusterparams"]["bridge"]["back"]["id"])
                    self.progress_bar(4)
                    
            self.progress_bar(14 - self.progress_sum)
                
            for zone in new_setting.keys():
                if(zone not in self.cluster_info["clusterparams"]["switch"]):
                    self.cluster_info["clusterparams"]["server"][zone] = {}
                    self.cluster_info["clusterparams"]["server"][zone]["compute"] = {}
                    self.cluster_info["clusterparams"]["switch"][zone] = {}
                    self.cluster_info["clusterparams"]["switch"][zone]["front"] = {}
                    self.cluster_info["clusterparams"]["switch"][zone]["front"]["id"] = self.create_switch(zone)
                    self.progress_bar(int(4/len(new_setting)))
                    self.connect_bridge_switch(zone, self.cluster_info["clusterparams"]["switch"][zone]["front"]["id"], self.cluster_info["clusterparams"]["bridge"]["front"]["id"])
                    self.progress_bar(int(4/len(new_setting)))
                    
                    if(self.cluster_info["clusterparams"]["bridge"]["back"] != None):
                        self.cluster_info["clusterparams"]["switch"][zone]["back"] = {}
                        self.cluster_info["clusterparams"]["switch"][zone]["back"]["id"] = self.create_switch(zone)
                        self.progress_bar(int(4/len(new_setting)))
                        self.connect_bridge_switch(zone, self.cluster_info["clusterparams"]["switch"][zone]["back"]["id"], self.cluster_info["clusterparams"]["bridge"]["back"]["id"])
                        self.progress_bar(int(4/len(new_setting)))
            
        self.progress_bar(30 - self.progress_sum)
        
        count = 0
        for zone, comp_num in new_setting.items():
            
            current_comp_num = len(self.cluster_info["clusterparams"]["server"][zone]["compute"])
            
            if(current_comp_num > comp_num):
                with futures.ThreadPoolExecutor(max_workers = self.max_workers, thread_name_prefix="thread") as executor:
                    while(True):
                        future = [] 
                        for i in range(current_comp_num -1, comp_num - 1, -1):
                            future.append(executor.submit(self.red_comp_server, zone, i, comp_num, current_comp_num, new_setting))
                            
                        future_result = [f.result()[0] for f in future]
                        future_msg = [f.result()[1] for f in future if(f.result()[0] == False and f.result()[1] != "")]
                        
                        if(len(future_msg) > 0):
                            future_msg = future_msg[0]
                            
                        if False in future_result:
                            temp = conf_pattern_2("\n".join(future_msg) + "\nTry again??", ["yes", "no"], "no", info_list = self.info_list, fp = self.fp)
                            
                            if temp == "no":
                                self.bar.close()
                                printout("Stop processing." , info_type = 0, info_list = self.info_list, fp = self.fp, overwrite = True)
                                sys.exit()
                            
                        else:
                            break
                        
                            #self.red_comp_server(zone, i, comp_num, current_comp_num, new_setting)
                    """
                    self.dis_connect_server_switch(zone, self.cluster_info["clusterparams"]["server"][zone]["compute"][i]["nic"]["front"]["id"])
                    
                    if(self.cluster_info["clusterparams"]["server"][zone]["compute"][i]["nic"]["back"] != None):
                        self.dis_connect_server_switch(zone, self.cluster_info["clusterparams"]["server"][zone]["compute"][i]["nic"]["back"]["id"])
                        
                    self.delete_server(zone, self.cluster_info["clusterparams"]["server"][zone]["compute"][i]["node"]["id"], self.cluster_info["clusterparams"]["server"][zone]["compute"][i]["node"]["name"])
                    for j in range(len(self.cluster_info["clusterparams"]["server"][zone]["compute"][i]["disk"])):
                        self.delete_disk(zone, self.cluster_info["clusterparams"]["server"][zone]["compute"][i]["disk"][j]["id"], self.cluster_info["clusterparams"]["server"][zone]["compute"][i]["node"]["name"])
                    
                    self.progress_bar(50/(len(new_setting) * (len(self.cluster_info["clusterparams"]["server"][zone]["compute"]) - comp_num)))
                    """
                        
            elif(len(self.cluster_info["clusterparams"]["server"][zone]["compute"]) < comp_num):
                server_disk_config = {}
                server_disk_config["node_planid"] = int(self.ext_info["Server"][str(self.cluster_info["clusterparams"]["server"][self.head_zone]["compute"][0]["node"]["core"])][str(self.cluster_info["clusterparams"]["server"][self.head_zone]["compute"][0]["node"]["memory"])])
                server_disk_config["disk_type_id"] = int(self.cluster_info["clusterparams"]["server"][self.head_zone]["compute"][0]["disk"][0]["type"])
                server_disk_config["disk_connection_type"] = self.cluster_info["clusterparams"]["server"][self.head_zone]["compute"][0]["disk"][0]["connection"]
                server_disk_config["os_id"] = self.cluster_info["clusterparams"]["server"][self.head_zone]["compute"][0]["disk"][0]["os"]
                server_disk_config["disk_size"] = int(self.cluster_info["clusterparams"]["server"][self.head_zone]["compute"][0]["disk"][0]["size"])
                server_disk_config["password"] = password
                server_disk_config["username"] = username
                
                with futures.ThreadPoolExecutor(max_workers = self.max_workers, thread_name_prefix="thread") as executor:
                    while(True):
                        future = [] 
                        for i in range(current_comp_num, comp_num):
                            future.append(executor.submit(self.add_comp_server, i, zone, server_disk_config, comp_num, current_comp_num, new_setting))
                            
                        future_result = [f.result()[0] for f in future]
                        future_msg = [f.result()[1] for f in future if(f.result()[0] == False and f.result()[1] != "")]
                        
                        if(len(future_msg) > 0):
                            future_msg = future_msg[0]
                            
                        if False in future_result:
                            temp = conf_pattern_2("\n".join(future_msg) + "\nTry again??", ["yes", "no"], "no", info_list = self.info_list, fp = self.fp)
                            
                            if temp == "no":
                                self.bar.close()
                                printout("Stop processing." , info_type = 0, info_list = self.info_list, fp = self.fp, overwrite = True)
                                sys.exit()
                            
                        else:
                            break
                    #self.add_comp_server(i, zone, server_disk_config, comp_num, current_comp_num, new_setting)
                    #if i < 9:
                        #compute_node_name = "compute_node_00"+str(i + 1)
                    #elif i >= 9:
                        #compute_node_name = "compute_node_0"+str(i + 1)
                        
                    #server_response = self.build_server(zone, compute_node_name, node_planid, self.cluster_info["clusterparams"]["switch"][zone]["front"]["id"])
                    #disk_res = self.add_disk(zone, compute_node_name, disk_type_id, disk_connection_type, disk_size, os_name, password, username)
                    #self.connect_server_disk(zone, disk_res["Disk"]["ID"], server_response["Server"]["ID"])
                    #if(self.cluster_info["clusterparams"]["switch"][zone]["back"] != None):
                        #nic_id = self.add_interface(zone, server_response["Server"]["ID"])
                        #self.connect_switch(zone, self.cluster_info["clusterparams"]["switch"][zone]["back"]["id"], nic_id)
                        
                    #self.progress_bar(50/(len(new_setting) * (comp_num - len(self.cluster_info["clusterparams"]["server"][zone]["compute"]))))
            
            count += 1
            self.progress_bar(int(50 - int(50/len(new_setting))))
            
            
        new_zones = [k for k, v in new_setting.items() if v != 0]
        if(len(new_zones) != len(self.zone_list)):
            delete_zone = list(set(self.zone_list) - set(new_zones))
            for zone in delete_zone:
                self.disconnect_bridge_switch(zone, self.cluster_info["clusterparams"]["switch"][zone]["front"]["id"])
                self.delete_switch(zone, self.cluster_info["clusterparams"]["switch"][zone]["front"]["id"])
                self.progress_bar(int(5/len(delete_zone)))
                
                if(self.cluster_info["clusterparams"]["switch"][zone]["back"] != None):
                    self.disconnect_bridge_switch(zone, self.cluster_info["clusterparams"]["switch"][zone]["back"]["id"])
                    self.delete_switch(zone, self.cluster_info["clusterparams"]["switch"][zone]["back"]["id"])
                self.progress_bar(int(4/len(delete_zone)))
            
            if(len(self.zone_list) == 2 and len(new_zones) == 1 and self.cluster_info["clusterparams"]["bridge"]["front"] != None):
                self.disconnect_bridge_switch(self.head_zone, self.cluster_info["clusterparams"]["switch"][self.head_zone]["front"]["id"])
                self.delete_bridge(self.cluster_info["clusterparams"]["bridge"]["front"]["id"])
                self.progress_bar(int(5/len(delete_zone)))
                
                if(self.cluster_info["clusterparams"]["bridge"]["back"] != None):
                    self.disconnect_bridge_switch(self.head_zone, self.cluster_info["clusterparams"]["switch"][self.head_zone]["back"]["id"])
                    self.delete_bridge(self.cluster_info["clusterparams"]["bridge"]["back"]["id"])
                self.progress_bar(int(4/len(delete_zone)))
                
    def red_comp_server(self, zone, number, comp_num, current_comp_num, new_setting):
        if(number in self.cluster_info["clusterparams"]["server"][zone]["compute"]):
            if(self.cluster_info["clusterparams"]["server"][zone]["compute"][number]["nic"]["front"]["id"] != None):
                res, ind = self.dis_connect_server_switch(zone, self.cluster_info["clusterparams"]["server"][zone]["compute"][number]["nic"]["front"]["id"], com_index = True)
                if(ind == False):
                    return ind, res
                else:
                    self.cluster_info["clusterparams"]["server"][zone]["compute"][number]["nic"]["front"]["id"] = None
                    
            if(self.cluster_info["clusterparams"]["server"][zone]["compute"][number]["nic"]["back"] != None):
                if(self.cluster_info["clusterparams"]["server"][zone]["compute"][number]["nic"]["back"]["id"] != None):
                    res, ind = self.dis_connect_server_switch(zone, self.cluster_info["clusterparams"]["server"][zone]["compute"][number]["nic"]["back"]["id"], com_index = True)
                    if(ind == False):
                        return ind, res
                    else:
                        self.cluster_info["clusterparams"]["server"][zone]["compute"][number]["nic"]["back"]["id"] = None
                        
            if(self.cluster_info["clusterparams"]["server"][zone]["compute"][number]["node"]["id"] != None):
                res, ind = self.delete_server(zone, self.cluster_info["clusterparams"]["server"][zone]["compute"][number]["node"]["id"], self.cluster_info["clusterparams"]["server"][zone]["compute"][number]["node"]["name"], com_index = True)
                if(ind == False):
                    return ind, res
                else:
                    self.cluster_info["clusterparams"]["server"][zone]["compute"][number]["node"]["id"] = None
            
            if(self.cluster_info["clusterparams"]["server"][zone]["compute"][number]["disk"] != None):
                for j in range(len(self.cluster_info["clusterparams"]["server"][zone]["compute"][number]["disk"])):
                    if(self.cluster_info["clusterparams"]["server"][zone]["compute"][number]["disk"][j]["id"] != None):
                        res, ind = self.delete_disk(zone, self.cluster_info["clusterparams"]["server"][zone]["compute"][number]["disk"][j]["id"], self.cluster_info["clusterparams"]["server"][zone]["compute"][number]["node"]["name"], com_index = True)
                        if(ind == False):
                            return ind, res
                        else:
                            self.cluster_info["clusterparams"]["server"][zone]["compute"][number]["disk"][j]["id"] = None
                self.cluster_info["clusterparams"]["server"][zone]["compute"][number]["disk"] = None
                    
            self.cluster_info["clusterparams"]["server"][zone]["compute"].pop(number)
            self.progress_bar(int(50/(len(new_setting) * (current_comp_num - comp_num))))
            
        return True, ""
        
    def add_comp_server(self, number, zone, server_disk_config, comp_num, current_comp_num, new_setting):
        if number < 9:
            compute_node_name = "compute_node_00"+str(number + 1)
        elif number >= 9:
            compute_node_name = "compute_node_0"+str(number + 1)
            
        if not number in self.cluster_info["clusterparams"]["server"][zone]["compute"].keys():
            server_response,res_index = self.build_server(zone, compute_node_name, server_disk_config["node_planid"], self.cluster_info["clusterparams"]["switch"][zone]["front"]["id"])
        
            self.cluster_info["clusterparams"]["server"][zone]["compute"][number] = {}
            self.cluster_info["clusterparams"]["server"][zone]["compute"][number]["node"] = {}
            self.cluster_info["clusterparams"]["server"][zone]["compute"][number]["disk"] = {}
            self.cluster_info["clusterparams"]["server"][zone]["compute"][number]["disk"][0] = {}
            self.cluster_info["clusterparams"]["server"][zone]["compute"][number]["nic"] = {}
            
            if res_index == True:
                if(self.api_index == True):
                    server_id = server_response["Server"]["ID"]
                    server_core = server_response["Server"]["ServerPlan"]["CPU"]
                    server_memory = server_response["Server"]["ServerPlan"]["MemoryMB"]
                    server_status = server_response["Server"]["Instance"]["Status"]
                    front_nic_id = server_response["Server"]["Interfaces"][0]["ID"]
                else:
                    server_id = 000000000000
                    server_core = 1
                    server_memory = 1024
                    server_status = "down"
                    front_nic_id = 000000000000
                    
                self.cluster_info["clusterparams"]["server"][zone]["compute"][number]["node"]["id"] = int(server_id)
                self.cluster_info["clusterparams"]["server"][zone]["compute"][number]["node"]["name"] = compute_node_name
                self.cluster_info["clusterparams"]["server"][zone]["compute"][number]["node"]["core"] = int(server_core)
                self.cluster_info["clusterparams"]["server"][zone]["compute"][number]["node"]["memory"] = int(server_memory)
                self.cluster_info["clusterparams"]["server"][zone]["compute"][number]["node"]["state"] = server_status
                self.cluster_info["clusterparams"]["server"][zone]["compute"][number]["nic"]["front"] = int(front_nic_id)
                
                disk_res = self.add_disk(zone, compute_node_name, number, server_disk_config["disk_type_id"], server_disk_config["disk_connection_type"], server_disk_config["disk_size"], server_disk_config["os_id"], server_disk_config["password"], server_disk_config["username"])
                
                if(self.api_index == True):
                    disk_id = disk_res["Disk"]["ID"]
                    disk_connection = disk_res["Disk"]["Connection"]
                    disk_size = disk_res["Disk"]["SizeMB"]
                    disk_os = disk_res["Disk"]["SourceArchive"]["ID"]
                    disk_type = disk_res["Disk"]["Plan"]["ID"]
                else:
                    disk_id = 000000000000
                    disk_connection = "virtio"
                    disk_size = 20480
                    disk_os = "CentOS Stream 8 (20201203) 64bit"
                    disk_type = 1
                    
                self.cluster_info["clusterparams"]["server"][zone]["compute"][number]["disk"][0]["id"] = int(disk_id)
                self.cluster_info["clusterparams"]["server"][zone]["compute"][number]["disk"][0]["connection"] = disk_connection
                self.cluster_info["clusterparams"]["server"][zone]["compute"][number]["disk"][0]["size"] = int(disk_size)
                self.cluster_info["clusterparams"]["server"][zone]["compute"][number]["disk"][0]["os"] = int(disk_os)
                self.cluster_info["clusterparams"]["server"][zone]["compute"][number]["disk"][0]["type"] = int(disk_type)
                
                    
                self.connect_server_disk(zone, disk_id, server_id)
                
                if(self.cluster_info["clusterparams"]["switch"][zone]["back"] != None):
                    nic_id = self.add_interface(zone, server_id)
                    self.cluster_info["clusterparams"]["server"][zone]["compute"][number]["nic"]["back"] = int(nic_id)
                    self.connect_switch(zone, self.cluster_info["clusterparams"]["switch"][zone]["back"]["id"], nic_id)
                else:
                    self.cluster_info["clusterparams"]["server"][zone]["compute"][number]["nic"]["back"] = None
        
                self.progress_bar(int(50/(len(new_setting) * (comp_num - current_comp_num))))
                
        else:
            res_index = True
            server_response = ""
            
        return res_index, server_response
        
    #新規CoreとMemory数の指定
    def core_memory_setting(self, server_type):
        
        while(True):
            printout('' , info_type = 0, info_list = self.info_list, fp = self.fp)
            #ノードにおけるCore数
            logger.debug('setting core number')
            candidate = list(self.ext_info["Server"].keys())
            core_plan = int(self.answer_response_core("The number of core for " + str(server_type), candidate, candidate[0]))
            
            #ノードにおけるメモリ容量
            logger.debug('setting memory size')
            candidate = [str(i) + " (" + str(int(round(int(i), -3)/1000)) + "GB)"  for i in list(self.ext_info["Server"][str(core_plan)].keys())]
            memory_plan = list(self.ext_info["Server"][str(core_plan)].keys())[self.answer_response_memory("Size of memory for " + str(server_type), candidate, candidate[0])]
            node_plan = self.ext_info["Server"][str(core_plan)][memory_plan]
            
            printout('#' *5 + ' New ' + server_type + ' setting ' + '#' *5, info_type = 0, info_list = self.info_list, fp = self.fp)
            core_comment = 'Core:' + str(core_plan)
            printout(core_comment.center(len('#' *5 + ' New ' + server_type + ' setting ' + '#' *5)) , info_type = 0, info_list = self.info_list, fp = self.fp)
            memory_comment = 'Memory:' + str(memory_plan)
            printout(memory_comment.center(len('#' *5 + ' New ' + server_type + ' setting ' + '#' *5)) , info_type = 0, info_list = self.info_list, fp = self.fp)
            printout('#' * len('#' *5 + ' New ' + server_type + ' setting ' + '#' *5), info_type = 0, info_list = self.info_list, fp = self.fp)
            
            printout('', info_type = 0, info_list = self.info_list, fp = self.fp)
            res = self.answer_response("Are the above settings correct?", ["yes", "y", "no", "n"], "yes/y or no/n")
            
            if(res == "yes" or res == "y"):
                break
        
        return node_plan, core_plan, memory_plan
    
    
    #サーバーの追加
    def build_server(self, zone, node_name, node_planid, head_switch_id):
        printout("constructing " + node_name + " ……", info_type = 0, info_list = self.info_list, fp = self.fp, overwrite = True)
        logger.debug("constructing " + node_name + " ……")
        
        param = {"Server":{"Name":node_name,"ServerPlan":{"ID":node_planid},"Tags":["cluster ID: " +self.cluster_id, self.date_modified],"ConnectedSwitches":[{"ID": head_switch_id}]},"Count":0}
            
        if (self.api_index == True):
            while(True):
                logger.debug("build server")
                server_response = post(self.url_list[zone] + self.sub_url[0], self.auth_res, param)
                check, msg = self.res_check(server_response, "post", com_index = True)

                if check == True:
                    node_id = server_response["Server"]["ID"]
                    logger.info(node_name + " ID: " + node_id + "-Success")
                    res_index = True
                    break
                else:
                    logger.debug("Error:cannot build server")
                    res_index = False
                    return msg,res_index
            
        else:
            server_response = "API is not used."
            node_id = "000"
            logger.debug("constructed " + node_name)
            res_index = True

        return server_response, res_index
    
    #ディスクの追加
    def add_disk(self, zone, disk_name, ip_index, disk_type_id, disk_connection_type, disk_size, os_id, password, username):
        printout("creating disk ……", info_type = 0, info_list = self.info_list, fp = self.fp, overwrite = True)
        logger.debug("creating disk for " + disk_name)

        #param = {"Disk":{"Name":disk_name,"Plan":{"ID": disk_type_id}, "Connection": disk_connection_type ,"SizeMB":disk_size,"SourceArchive":{"Availability": "available","ID": int(self.ext_info["OS"][os_name][zone])},"Tags":["cluster ID: " + str(self.cluster_id)]},"Config":{"Password": str(password), "HostName": str(username)}}
        param = {"Disk":{"Name":disk_name,"Plan":{"ID": disk_type_id}, "Connection": disk_connection_type ,"SizeMB":disk_size,"SourceArchive":{"Availability": "available","ID": int(os_id)},"Tags":["cluster ID: " + str(self.cluster_id)]},"Config":{"Password": str(password), "HostName": str(username)}}
    
        if (self.api_index == True):
            while(True):
                disk_res = post(self.url_list[zone] + self.sub_url[1], self.auth_res, param)
                check, msg = self.res_check(disk_res, "post")
                if check == True:
                    disk_id = disk_res["Disk"]["ID"]
                    logger.info("disk ID: " + disk_id + "-Success")
                    self.waitDisk(zone, disk_id)
                    if "headnode" != disk_name:
                        disk_res["Disk"]["ip_addr"] = self.assign_ip(zone, ip_index, disk_id)
                    break
                else:
                    self.build_error()
            
        else:
            disk_res = "API is not used."
            disk_id = "0000"
    
        return disk_res
    
    # ディスク状態が利用可能になるまで待ち続けるコード
    def waitDisk (self, zone, diskId):
        logger.debug("Waiting disc creation ……")
        diskState = 'uploading'
        
        while True:
            printout("waiting disk ……", info_type = 0, info_list = self.info_list, fp = self.fp, overwrite = True)
            disk_info = get(self.url_list[zone] + self.sub_url[1]  + "/" + str(diskId), self.auth_res)
            diskState = disk_info['Disk']['Availability']
            check, msg = self.res_check (disk_info, "get")

            while(True):
                if check == True:
                    break
                else:
                    self.build_error()

            if diskState == 'available':
                logger.debug("Finish creation of disc ……")
                break
            time.sleep(10)
            
    #Eth0のIPアドレスの割当
    def assign_ip(self, zone, ipAddressSequense, diskId):
        logger.debug("Assigning ip addr to dist ……")
        
        base = self.ext_info["IP_addr"]["base"]
        front = self.ext_info["IP_addr"]["front"]
        ip_zone = self.ext_info["IP_addr"]["zone_seg"]
        
        #compute_ip_zone = {"tk1a": "192.168.1.", "tk1b": "192.168.2.", "is1a": "192.168.3.", "is1b": "192.168.4."}
        ipAddress = "{}.{}.{}.{}".format(base, front, ip_zone[zone], ipAddressSequense + 1)
        
        #str(compute_ip_zone[zone]) + str(ipAddressSequense + 1)
        
        param = {
            "UserIPAddress": ipAddress,
            "UserSubnet": {
                "DefaultRoute": '{}.{}.254.254'.format(base, front),
                "NetworkMaskLen": 16
        }
        }
        printout("assigning IP address ……", info_type = 0, info_list = self.info_list, fp = self.fp, overwrite = True)
        putUrl = self.url_list[zone] + self.sub_url[1] + '/' + str (diskId) + '/config'
        logger.debug(putUrl)
        disk_res = put(putUrl, self.auth_res, param)
        check, msg = self.res_check (disk_res, "put")

        while(True):
            if check == True:
                break
            else:
                self.build_error()
        
        return ipAddress
    
    #サーバとディスクの接続
    def connect_server_disk(self, zone, disk_id, server_id):
        printout("connecting disk to server ……", info_type = 0, info_list = self.info_list, fp = self.fp, overwrite = True)
        logger.debug("connecting disk to server")
        url_disk = "/disk/" + str(disk_id) + "/to/server/" + str(server_id)
        if (self.api_index == True):
            while(True):
                server_disk_res = put(self.url_list[zone] + url_disk, self.auth_res)
                check, msg = self.res_check(server_disk_res, "put")
                if check == True:
                    logger.debug("connected disk to server: " + server_id + "-" + disk_id)
                    break
                else:
                    self.build_error()
        else:
            server_disk_res = "API is not used."

        return server_disk_res
    
    def delete_server(self,zone,node_id, node_name, com_index = False):
        printout("deleting " + node_name + " ……", info_type = 0, info_list = self.info_list, fp = self.fp, overwrite = True)
        if(self.api_index == True):
            while(True):
                delete_res = delete(self.url_list[zone] + self.sub_url[0] + "/" + str(node_id), self.auth_res)
                check, msg = self.res_check(delete_res,"delete", com_index = True)
                if (check == True):
                    logger.debug("Delete a server:" + str(node_id))
                    res_index = True
                    break
                else:
                    if com_index == False:
                        logger.debug("Error:cannot delete a server")
                        res_index = False
                        self.build_error()
                    else:
                        logger.debug("Error:cannot delete a server")
                        res_index = False
                        return msg,res_index
        else:
            delete_res = "API is not used."
            node_id = "000"
            logger.debug("Deleted a server")
            res_index = True
            
        return delete_res, res_index
            

    def delete_disk(self,zone,disk_id, node_name, com_index = False):
        printout("deleting disk of " + node_name + " ……", info_type = 0, info_list = self.info_list, fp = self.fp, overwrite = True)
        if(self.api_index == True):
            while(True):
                delete_res = delete(self.url_list[zone] + self.sub_url[1] + "/" + str(disk_id), self.auth_res)
                check, msg = self.res_check(delete_res,"delete", com_index = True)
                if (check == True):
                    logger.debug("Delete this disk:" + str(disk_id))
                    res_index = True
                    break
                else:
                    if com_index == False:
                        logger.debug("Error:cannot delete a disk")
                        res_index = False
                        self.build_error()
                    else:
                        logger.debug("Error:cannot delete a disk")
                        res_index = False
                        return msg,res_index
        else:
            delete_res = "API is not used."
            node_id = "000"
            logger.debug("Deleted a disk")
            res_index = True
            
        return delete_res, res_index
        
        
    #ノードプランの変更
    def change_node_plan(self, zone, server_id, plan_id, ind = 0, node_num = "*"):
        ind_dic = {0: False, 1:True}
        printout("changing node plan ……", info_type = 0, info_list = self.info_list, fp = self.fp, overwrite = True)
        logger.debug("changing node plan")
        url = self.url_list[zone] + self.sub_url[0] + "/" + str(server_id) + "/to/plan/" + str(plan_id)
        
        if (self.api_index == True):
            while(True):
                response = put(url, self.auth_res)
                check, msg = self.res_check(response, "put", com_index = ind_dic[ind])
                if check == True:
                    res = response["Server"]["ID"]
                    break
                else:
                    if(ind == 0):
                        self.build_error()
                    else:
                        return False, msg, ""
        else:
            res = "API is not used."
            msg = ""
            
        #if(ind == 1):
            #self.cluster_info["clusterparams"]["server"][zone]["compute"][node_num]["node"]["id"] = 
        
        #import random
        #temp = random.randint(0, 1)
        #if(temp == 0):
            #logger.debug("True")
            #return True, msg, response["Server"]["ID"]
        #else:
            #logger.debug("False")
            #return False, msg, response["Server"]["ID"]
        
        return True, msg, res
        
    #スイッチの追加
    def create_switch(self, zone):
        printout("creating a switch in back area ……", info_type = 0, info_list = self.info_list, fp = self.fp, overwrite = True)
        logger.debug("creating a switch in back area")
        switch_name = "Switch in back area"
    
        param = {"Switch":{"Name":switch_name,"Tags":["cluster ID: " + self.cluster_id]},"Count":0}
    
        if (self.api_index == True):
            while(True):
                switch_response = post(self.url_list[zone] + self.sub_url[2], self.auth_res, param)
                check, msg = self.res_check(switch_response, "post")
                if check == True:
                    switch_id = int(switch_response["Switch"]["ID"])
                    logger.info("switch ID: " + str(switch_id) + "-Success")
                    break
                else:
                    self.build_error()
            
        else:
            switch_response = "API is not used."
            switch_id = 0000
    
        return switch_id  
    
    #スイッチの削除
    def delete_switch(self, zone, switch_id):
        printout("deleting a switch in back area ……", info_type = 0, info_list = self.info_list, fp = self.fp, overwrite = True)
        logger.debug("deleting a switch in back area")
        sub_url = self.sub_url[2] + "/" + str(switch_id)
    
        if (self.api_index == True):
            while(True):
                switch_response = delete(self.url_list[zone] + sub_url, self.auth_res)
                check, msg = self.res_check(switch_response, "delete")
                if check == True:
                    break
                else:
                    self.build_error()
            
        else:
            switch_response = "API is not used."
    
        return switch_response
    
    #NICをスイッチに接続
    def connect_switch(self, zone, switch_id, nic_id):
        printout("connecting switch to nic ……", info_type = 0, info_list = self.info_list, fp = self.fp, overwrite = True)
        logger.debug("connecting switch to nic")
        sub_url_con = self.sub_url[3] + "/" + str(nic_id) + "/to/switch/" + str(switch_id)
        if (self.api_index == True):
            while(True):
                connect_switch_response = put(self.url_list[zone] + sub_url_con, self.auth_res)
                check, msg = self.res_check(connect_switch_response, "put")
                if check == True:
                    logger.debug("connected switch to nic: " + str(switch_id) + "-" + str(nic_id))
                    break
                else:
                    self.build_error()
        else:
            connect_switch_response = "API is not used."

        return connect_switch_response
    
    """
    #NICとスイッチの接続を解除
    def dis_connect_switch(self, zone, nic_id):
        printout("disconnecting switch from nic ……", info_type = 0, info_list = self.info_list, fp = self.fp, overwrite = True)
        logger.debug("disconnecting switch to nic")
        sub_url_con = self.sub_url[3] + "/" + str(nic_id) + "/to/switch"
        if (self.api_index == True):
            while(True):
                disconnect_switch_response = delete(self.url_list[zone] + sub_url_con, self.auth_res)
                check, msg = self.res_check(disconnect_switch_response, "delete")
                if check == True:
                    logger.debug("disconnected switch to nic: " + str(nic_id))
                    break
                else:
                    self.build_error()
        else:
            disconnect_switch_response = "API is not used."

        return disconnect_switch_response
    """
    
    def dis_connect_server_switch(self,zone, nic_id, com_index = False):
        printout("disconnecting server from switch ……", info_type = 0, info_list = self.info_list, fp = self.fp, overwrite = True)
        if(self.api_index == True):
            while(True):
                delete_res = delete(self.url_list[zone] + self.sub_url[3] + "/" + str(nic_id) + "/to" + self.sub_url[2], self.auth_res)
                if(com_index == False):
                    check, msg = self.res_check(delete_res, "delete")
                else:
                    check, msg = self.res_check(delete_res, "delete", com_index = True)
                if (check == True):
                    logger.debug("Disconnect server and switch(NIC ID): " + str(nic_id))
                    res_index = True
                    break
                else:
                    if com_index == False:
                        logger.debug("Error:cannot disconnect switch from server")
                        res_index = False
                        self.build_error()
                    else:
                        logger.debug("Error:cannot disconnect switch from server")
                        res_index = False
                        return msg,res_index
        else:
            delete_res = "API is not used."
            node_id = "000"
            logger.debug("Disconnect switch from server")
            res_index = True
            
        return delete_res, res_index
    
    #NICを追加
    def add_interface(self, zone, node_id):
        printout("adding nic ……", info_type = 0, info_list = self.info_list, fp = self.fp, overwrite = True)
        logger.debug("adding nic")

        add_nic_param = {"Interface":{"Server":{"ID":str(node_id)}}, "Count":0}
    
        if (self.api_index == True):
            while(True):
                add_nic_response = post(self.url_list[zone] + self.sub_url[3], self.auth_res, add_nic_param)
                check, msg = self.res_check(add_nic_response, "post")
                if check == True:
                    nic_id = int(add_nic_response["Interface"]["ID"])
                    logger.info("nic ID: " + str(nic_id) + "-Success")
                    break
                else:
                    self.build_error()
            
        else:
            add_nic_response = "API is not used."
            nic_id = 000000000000
    
        return nic_id
    
    #NICを削除
    def delete_interface(self, zone, nic_id):
        printout("deleting nic ……", info_type = 0, info_list = self.info_list, fp = self.fp, overwrite = True)
        logger.debug("deleting nic")

        sub_url_con = self.sub_url[3] + "/" + str(nic_id)
    
        if (self.api_index == True):
            while(True):
                del_nic_response = delete(self.url_list[zone] + sub_url_con, self.auth_res)
                check, msg = self.res_check(del_nic_response, "delete")
                if check == True:
                    logger.info("delelte nic ID: " + str(nic_id) + "-Success")
                    break
                else:
                    self.build_error()
            
        else:
            del_nic_response = "API is not used."
    
        return del_nic_response
    
    #ブリッジを作成
    def create_bridge(self):
        printout("creating bridge ……", info_type = 0, info_list = self.info_list, fp = self.fp, overwrite = True)
        logger.debug("creating bridge")
        bridge_name = "Bridge for " + self.cluster_info["baseparams"]["config_name"]
        param = {"Bridge":{"Name":bridge_name}}
    
        if (self.api_index == True):
            while(True):
                bridge_res = post(self.head_url + self.sub_url[4], self.auth_res, param)
                check, msg = self.res_check(bridge_res, "post")
                if check == True:
                    bridge_id = int(bridge_res["Bridge"]["ID"])
                    break
                else:
                    self.build_error()
                
        else:
            bridge_res = "API is not used."
            bridge_id = 0000
        return bridge_id
    
    #ブリッジを削除
    def delete_bridge(self, bridge_id):
        printout("deleting bridge ……", info_type = 0, info_list = self.info_list, fp = self.fp, overwrite = True)
        logger.debug("deleting bridge")
        sub_url = self.sub_url[4] + "/" + str(bridge_id)
    
        if (self.api_index == True):
            while(True):
                bridge_res = delete(self.head_url + sub_url, self.auth_res)
                check, msg = self.res_check(bridge_res, "delete")
                if check == True:
                    break
                else:
                    self.build_error()
        else:
            bridge_res = "API is not used."
        return bridge_res
    
    #スイッチをブリッジに接続
    def connect_bridge_switch(self, zone, switch_id, bridge_id):
        printout("connecting switch to bridge ……", info_type = 0, info_list = self.info_list, fp = self.fp, overwrite = True)
        url_bridge = self.sub_url[2] + "/" + str(switch_id) + "/to/bridge/" + str(bridge_id)
        if (self.api_index == True):
            while(True):
                bridge_switch_res = put(self.url_list[zone] + url_bridge, self.auth_res)
                check, msg = self.res_check(bridge_switch_res, "put")
                if check == True:
                    logger.debug("connected switch to bridge: " + str(switch_id) + "-" + str(bridge_id))
                    break
                else:
                    self.build_error()
        else:
            bridge_switch_res = "API is not used."
            
        return bridge_switch_res
            
    #ブリッジとスイッチの接続を解除
    def disconnect_bridge_switch(self, zone, switch_id):
        printout("disconnecting switch from bridge ……", info_type = 0, info_list = self.info_list, fp = self.fp, overwrite = True)
        url_bridge = self.sub_url[2] + "/" + str(switch_id) + "/to/bridge"
        if (self.api_index == True):
            while(True):
                bridge_switch_res = delete(self.url_list[zone] + url_bridge, self.auth_res)
                check, msg = self.res_check(bridge_switch_res, "delete")
                if check == True:
                    logger.debug("disconnected switch to bridge: " + str(switch_id))
                    break
                else:
                    self.build_error()
        else:
            bridge_switch_res = "API is not used."
            
        return bridge_switch_res
    
    #APIのエラー処理
    def build_error(self):
        logger.debug("decision of repeating to request")
        while(True):
            conf = printout("Try again??(yes/no):", info_type = 2,info_list = self.info_list, fp = self.fp)
            if conf == "yes":
                break
            elif conf == "no":
                printout("Stop processing.", info_type = 0, info_list = self.info_list, fp = self.fp)
                sys.exit()
            else:
                _ = printout("Please answer yes or no.",info_list = self.info_list,fp = self.fp) 
                
    #APIレスポンスの確認・処理
    def res_check(self, res, met, com_index = False):
        met_dict = {"get": "is_ok", "post": "is_ok", "put": "Success", "delete": "is_ok"}
        index = met_dict[met]
        msg = ""
                
        logger.debug("confirm API request(" + str(met) + ")")
        if (index in res.keys()):
            if res[index] == True:
                logger.debug("API processing succeeded")
                check = True
                return check, msg
            else:
                logger.warning("API processing failed")
                if com_index == False:
                    check = False
                    return check, msg
                else:
                    msg = list("Error:")
                    check = False
                    return check, msg

        elif ("is_fatal" in res.keys()):
            logger.warning("API processing failed")
            if com_index == False:
                printout("Status:" + res["status"], info_type = 0, info_list = self.info_list, fp = self.fp)
                printout("Error:" + res["error_msg"], info_type = 0, info_list = self.info_list, fp = self.fp)
                check = False
                return check, msg
            else:
                msg = ["Status:" + res["status"], "Error:" + res["error_msg"]]
                check = False
                return check, msg
        
    def progress_bar(self, up):
        self.bar.update(int(up))
        self.progress_sum += int(up)
    
    def answer_response(self, comment, candidate, candidate_comment, input_comment = "", opp = 0):
        if(opp == 0):
            while(True):
                input_val = printout(comment + "(" + candidate_comment + ") >>", info_type = 1, info_list = self.info_list, fp = self.fp)
            
                if(input_val in candidate):
                    return input_val
                else:
                    printout('' , info_type = 0, info_list = self.info_list, fp = self.fp)
                    _ = printout("Warning: the input must be selected from " + candidate_comment, info_type = 0, info_list = self.info_list, fp = self.fp)
            
        elif(opp == 1):
            while(True):
                printout(comment, info_type = 0, info_list = self.info_list, fp = self.fp)
                input_val = printout("[[" + input_comment + "]]>>" , info_type = 1, info_list = self.info_list, fp = self.fp)
                
                if(input_val in candidate):
                    return input_val
                else:
                    printout('' , info_type = 0, info_list = self.info_list, fp = self.fp)
                    _ = printout("Warning: the input must be selected from " + candidate_comment, info_type = 0, info_list = self.info_list, fp = self.fp)
    
    def answer_response_memory(self, comment, candidate, default):
        pos_index = 5
        if(len(candidate) <= pos_index):
            while(True):
                printout("[[" + str(comment) + "]]", info_type = 0, info_list = self.info_list, fp = self.fp)
                printout(str(0) + ": " + str(candidate[0]) + " (default)", info_type = 0, info_list = self.info_list, fp = self.fp)
                for i in range(1,len(candidate)):
                    printout(str(i) + ": " + str(candidate[i]), info_type = 0, info_list = self.info_list, fp = self.fp)
            
                val = printout(">>>", info_type = 1, info_list = self.info_list, fp = self.fp)
                printout("", info_type = 0, info_list = self.info_list, fp = self.fp)
                if(val == ""):
                    return 0
                elif(val.isdigit() != True):
                    printout("Warning: Please specify in the index", info_type = 0, info_list = self.info_list, fp = self.fp)
                elif((int(val) < 0) or (int(val) >= len(candidate))):
                    printout("Warning: An unexpected value", info_type = 0, info_list = self.info_list, fp = self.fp)
                else:
                    return int(val)
    
        else:   
            while(True):
                printout("[[" + str(comment) + "]]", info_type = 0, info_list = self.info_list, fp = self.fp)
                printout(str(0) + ": " + str(candidate[0]) + " (default)", info_type = 0, info_list = self.info_list, fp = self.fp)
                for i in range(1, pos_index):
                    printout(str(i) + ": " + str(candidate[i]), info_type = 0, info_list = self.info_list, fp = self.fp)
                
                if(pos_index < len(candidate)):
                    printout(str(pos_index) + ": others", info_type = 0, info_list = self.info_list, fp = self.fp)
            
                val = printout(">>>", info_type = 1, info_list = self.info_list, fp = self.fp)
                printout("", info_type = 0, info_list = self.info_list, fp = self.fp)
            
                if(val == ""):
                    return 0
                elif(val.isdigit() != True):
                    printout("Warning: Please specify in the index", info_type = 0, info_list = self.info_list, fp = self.fp)
                elif(int(val) == pos_index):
                    pos_index = len(candidate)
                elif((pos_index < len(candidate)) and ((int(val) < 0) or (int(val) > pos_index))):
                    printout("Warning: An unexpected value", info_type = 0, info_list = self.info_list, fp = self.fp)
                elif((pos_index == len(candidate)) and ((int(val) < 0) or (int(val) >= pos_index))):
                    printout("Warning: An unexpected value", info_type = 0, info_list = self.info_list, fp = self.fp)
                else:
                    return int(val)
                
    def answer_response_core(self, comment, candidates, default):
        while(True):
            val = printout("[" + str(comment) + " {" + ",".join(candidates) + "}, (default: " + str(default) + ")] >> ", info_type = 1, info_list = self.info_list, fp = self.fp).replace(" ","")
        
            if(val == ""):
                return default
        
            else:
                if(val in candidates):
                    return val
            
                else:
                    _ = printout("Warning: " + comment + " must be selected one from " + ",".join(candidates), info_type = 0, info_list = self.info_list, fp = self.fp)
        
    def answer_response_node_number(self, comment, min_val, max_val, current_val = 0, sp_type = 0):
        while(True):
            val = printout("[[" + str(comment) + " {" + str(min_val) + "~" + str(max_val) + "}]]>> ", info_type = 1, info_list = self.info_list, fp = self.fp).replace(" ","")
        
            if(val.isdecimal() == False):
                _ = printout("Warning: " + comment + " must be number from " + str(min_val) + " to " + str(max_val), info_type = 0, info_list = self.info_list, fp = self.fp)

            elif(current_val == int(val) and sp_type == 1):
                _ = printout("Warning: the specified number is the same as the current compute number", info_type = 0, info_list = self.info_list, fp = self.fp)

            elif(min_val <= int(val) <= max_val):
                return int(val)
            
            else: 
                _ = printout("Warning: " + comment + " must be number from " + str(min_val) + " to "+ str(max_val), info_type = 0, info_list = self.info_list, fp = self.fp)
  
           








































