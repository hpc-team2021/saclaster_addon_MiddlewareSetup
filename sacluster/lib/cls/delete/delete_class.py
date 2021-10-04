import sys
import os
import datetime
import logging
from tqdm import tqdm
from concurrent import futures
import signal

logger = logging.getLogger("sacluster").getChild(os.path.basename(__file__))

path = "../../.."
os.chdir(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(path + "/lib/others")

from API_method import delete,get
from info_print import printout
import pprint


class delete_sacluster:
    
    def __init__(self, cluster_info, auth_res, max_workers,fp='', info_list=[1,0,0,0], api_index=True):
        signal.signal(signal.SIGINT, self.handler)
        self.cluster_info = cluster_info
        #pprint.pprint(self.cluster_info)
        #sys.exit()
        self.auth_res = auth_res
        self.fp = fp
        self.info_list = info_list
        self.api_index = api_index
        #cluster_infoの中身をチェック
        self.contents_bool = self.validate_params(self.cluster_info)
        #pprint.pprint(self.contents_bool)
        #sys.exit()
        #self.cluster_id = [k for k in self.cluster_info.keys()]
        #if "server" in self.cluster_info["clusterparams"].keys():
        
        if self.contents_bool["server"] == True:
            #該当serverが存在するzoneを抽出
            self.zone_list = list(zone_list for zone_list in self.cluster_info["clusterparams"]["server"].keys())
            
        else:
            #bridgeのみのときにzoneはis1aに設定
            self.zone_list = ["is1a"]
        
        #If there is NFS, get NFS zone 
        self.nfs_zones = []
        #if "nfs" in self.cluster_info["clusterparams"].keys():
        if self.contents_bool["nfs"] == True:
            for zone in self.zone_list:
                if self.cluster_info["clusterparams"]["nfs"][zone] != None:
                    #self.nfs_zones = list(self.cluster_info["clusterparams"]["nfs"].keys())
                    self.nfs_zones.append(zone)
                #else:
                    #self.nfs_zones = []
        #else:
            #self.nfs_zones = []
            
        #Get head zone
        if self.contents_bool["server"] == True:
            for zone in self.zone_list:
                if "head" in self.cluster_info["clusterparams"]["server"][zone].keys():
                    self.head_zone = zone
                    break
        else:
            self.head_zone = None
        
        #if "front" in self.cluster_info["clusterparams"]["bridge"].keys():
        if self.contents_bool["bridge"] == True:
            #if self.cluster_info["clusterparams"]["bridge"]["front"] != None:
            #if len(self.zone_list) >= 2:
            self.bridge_front_id = self.cluster_info["clusterparams"]["bridge"]["front"]["id"]
            if self.cluster_info["clusterparams"]["bridge"]["back"] != None:
            #if "back" in self.cluster_info["clusterparams"]["bridge"].keys():
                self.bridge_back_id = self.cluster_info["clusterparams"]["bridge"]["back"]["id"]
            else:
                self.bridge_back_id = None
        
        self.front_switch_id_list = {}
        self.back_switch_id_list = {}
        
        #if "front" in self.cluster_info["clusterparams"]["switch"].keys():
        if self.contents_bool["switch"] == True:
            for zone in self.zone_list:
                self.front_switch_id_list[zone] = self.cluster_info["clusterparams"]["switch"][zone]["front"]["id"]
                if "back" in self.cluster_info["clusterparams"]["switch"][zone].keys():
                    if self.cluster_info["clusterparams"]["switch"][zone]["back"] != None:
                        self.back_switch_id_list[zone] = self.cluster_info["clusterparams"]["switch"][zone]["back"]["id"]
        #state check
        #self.validate_status(self.cluster_info)
        #Get URL
        self.url_list = {}
        for zone in self.zone_list:
            self.url_list[zone] = "https://secure.sakura.ad.jp/cloud/zone/"+ zone +"/api/cloud/1.1"

        if self.head_zone != None:
            self.head_url = "https://secure.sakura.ad.jp/cloud/zone/"+ self.head_zone +"/api/cloud/1.1"

        #Get sub URL
        self.sub_url = ["/server","/disk","/switch","/interface","/bridge","/tag","/appliance","/power"]
        
        self.date_modified = "Date modified:" + str(datetime.datetime.now().strftime("%Y_%m_%d"))
        
        self.max_workers = max_workers
        
        
    def __call__(self):
        #progress barの設定
        self.bar = tqdm(total = 100)
        self.bar.set_description('Progress rate')
        self.progress_sum = 0
        
        #2つ以上のゾーンを持つ時，ブリッジとスイッチの接続を切断
        #if len(self.zone_list) >= 2: 
        if self.contents_bool["bridge"] == True and self.contents_bool["switch"] == True:
            #if self.cluster_info["clusterparams"]["bridge"]["front"] != None:
            for zone in self.zone_list:
                connect_bool = self.get_bridge_info(zone,self.bridge_front_id)
                if connect_bool == True:
                    printout("Disconnect bridge and switch : " + zone + " zone", info_type = 0, info_list = self.info_list, fp = self.fp, overwrite=True)
                    self.disconnect_bridge_switch(zone,self.front_switch_id_list[zone])
                    if self.bridge_back_id != None:
                        connect_bool = self.get_bridge_info(zone,self.bridge_back_id)
                        if connect_bool == True:
                            self.disconnect_bridge_switch(zone,self.back_switch_id_list[zone])
                    self.progress_bar(int(20/len(self.zone_list)))
        
        if self.contents_bool["bridge"] == True:
            printout("Delete bridge: " + str(self.bridge_front_id) ,info_type = 0, info_list = self.info_list, fp = self.fp, overwrite=True)
            self.delete_bridge(self.zone_list[0],self.bridge_front_id)
            if self.bridge_back_id != None:
                printout("Delete bridge: " + str(self.bridge_back_id) ,info_type = 0, info_list = self.info_list, fp = self.fp, overwrite=True)
                self.delete_bridge(self.zone_list[0],self.bridge_back_id)
            self.progress_bar(10)
        
        #peripheral zone 削除
        for zone in self.zone_list:
            if zone != self.head_zone:
                self.delete_peripheral_zone(zone)
                
        if self.head_zone != None:
            self.delete_head_zone(self.head_zone)
            
        self.bar.update(100 - self.progress_sum)
        self.bar.close()
        
    def delete_head_zone(self,zone):
        logger.debug("Delete " + zone + " zone")
        if self.contents_bool["server"] == True:
            head_node_id = None
            head_disk_id = []
            compute_node_id_list = []
            disk_id_list = []
            if "head" in self.cluster_info["clusterparams"]["server"][zone].keys():
                head_node_id = self.cluster_info["clusterparams"]["server"][zone]["head"]["node"]["id"]
                logger.info("head node ID: " + str(head_node_id))
                #head_disk_id = []
                if "disk" in self.cluster_info["clusterparams"]["server"][zone]["head"].keys():
                    for i in self.cluster_info["clusterparams"]["server"][zone]["head"]["disk"].keys():
                        head_disk_id.append(self.cluster_info["clusterparams"]["server"][zone]["head"]["disk"][i]["id"])
                        logger.info("head node disk ID: " + str(head_disk_id))

            if "compute" in self.cluster_info["clusterparams"]["server"][zone].keys():
                #compute_node_id_list = []
                #disk_id_list = []
                for i in self.cluster_info["clusterparams"]["server"][zone]["compute"].keys():
                    compute_node_id_list.append(self.cluster_info["clusterparams"]["server"][zone]["compute"][i]["node"]["id"])
                    #print(self.cluster_info["clusterparams"]["server"][zone]["compute"][i]["disk"].keys())
                    if "disk" in self.cluster_info["clusterparams"]["server"][zone]["compute"][i].keys():
                        for j in self.cluster_info["clusterparams"]["server"][zone]["compute"][i]["disk"].keys():
                            disk_id_list.append(self.cluster_info["clusterparams"]["server"][zone]["compute"][i]["disk"][j]["id"])
                            logger.info("compute node disk ID: " + str(self.cluster_info["clusterparams"]["server"][zone]["compute"][i]["disk"][j]["id"]))

                #delete compute node
                if compute_node_id_list != []:
                    logger.info("Delete compute node")
                    with futures.ThreadPoolExecutor(max_workers = self.max_workers, thread_name_prefix="thread") as executor:
                        for compute_node_id in compute_node_id_list:
                        #executor.submit(MulHelper(self, "build_one_compute_node"), kwargs={"zone": zone, "i": i})
                            printout("Delete head zone(" + zone + ") : compute node(" + str(compute_node_id) + ")", info_type = 0, info_list = self.info_list, fp = self.fp, overwrite = True)
                            executor.submit(self.delete_server,zone,compute_node_id)
                            self.progress_bar(int(10/1+len(compute_node_id_list)))
                '''
                for compute_node_id in compute_node_id_list:
                    printout("Delete head zone(" + zone + ") : compute node(" + str(compute_node_id) + ")", info_type = 0, info_list = self.info_list, fp = self.fp, overwrite=True)
                    logger.debug('Previous: ' + str(compute_node_id))
                    self.delete_server(zone,compute_node_id)
                    logger.debug('After: ' + str(compute_node_id))
                    self.progress_bar(10/1+len(compute_node_id_list))
                logger.debug('finish deleting computenode in head zone')
                '''
            #delete compute disk

                if disk_id_list != []:
                    with futures.ThreadPoolExecutor(max_workers = self.max_workers, thread_name_prefix="thread") as executor:
                        for disk_id in disk_id_list:
                        #executor.submit(MulHelper(self, "build_one_compute_node"), kwargs={"zone": zone, "i": i})
                            printout("Delete head zone(" + zone + ") : compute disk(" + str(disk_id) + ")", info_type = 0, info_list = self.info_list, fp = self.fp, overwrite = True)
                            executor.submit(self.delete_disk,zone,disk_id)
                            self.progress_bar(int(10/1+len(disk_id_list)))

                    '''
                    for disk_id in disk_id_list:
                        printout("Delete head zone(" + zone + ") : compute disk(" + str(disk_id) + ")", info_type = 0, info_list = self.info_list, fp = self.fp, overwrite=True)
                        self.delete_disk(zone,disk_id)
                        self.progress_bar(10/1+len(disk_id_list))'''
        
        #delete NFS
        if self.contents_bool["nfs"] == True:
            if self.nfs_zones != []:
                if zone in self.nfs_zones:
                    nfs_id = self.cluster_info["clusterparams"]["nfs"][zone]["id"]
                    printout("Delete head zone(" + zone + ") : NFS(" + str(nfs_id) + ")", info_type = 0, info_list = self.info_list, fp = self.fp, overwrite=True)
                    self.delete_nfs(zone,nfs_id)
                    self.progress_bar(10)
        
        #if self.back_switch_id_list in locals():
        if self.contents_bool["switch"] == True:
            if self.back_switch_id_list != {}:
                if zone in self.back_switch_id_list.keys():
                    printout("Delete head zone(" + zone + ") : back switch(" + str(self.back_switch_id_list[zone]) + ")", info_type = 0, info_list = self.info_list, fp = self.fp, overwrite=True)
                    self.delete_switch(zone,self.back_switch_id_list[zone])
        
            #disconnect head node and switch
            if "nic" in self.cluster_info["clusterparams"]["server"][zone]["head"].keys() and self.front_switch_id_list != {}:
                head_node_nic_front_id = self.cluster_info["clusterparams"]["server"][zone]["head"]["nic"]["front"]["id"]
                printout("Disconnect server and switch: " + str(head_node_nic_front_id) + " and " + str(self.front_switch_id_list[zone]), info_type = 0, info_list = self.info_list, fp = self.fp, overwrite=True)
                self.disconnect_server_switch(zone,head_node_nic_front_id)
                self.progress_bar(5)
                #self.disconnect_server_switch(zone,head_node_id)

            #delete switch
            #if self.front_switch_id_list in locals():
            if self.front_switch_id_list != {}:
                printout("Delete head zone(" + zone + ") : front switch(" + str(self.front_switch_id_list[zone]) + ")", info_type = 0, info_list = self.info_list, fp = self.fp, overwrite=True)
                self.delete_switch(zone,self.front_switch_id_list[zone])
                self.progress_bar(5)
        logger.info("Delete head node")
        logger.info("head node ID: " + str(head_node_id))
        if self.contents_bool["server"] == True:
            if head_node_id != None:
                printout("Delete head zone(" + zone + ") : head node(" + str(head_node_id) + ")", info_type = 0, info_list = self.info_list, fp = self.fp, overwrite=True)
                self.delete_server(zone,head_node_id)
                self.progress_bar(10)

            #delete head disk
            #if head_disk_id in locals():
            logger.info("Delete head node disk")
            if head_disk_id != []:
                for disk_id in head_disk_id:
                    printout("Delete head zone(" + zone + ") : head disk(" + str(disk_id) + ")", info_type = 0, info_list = self.info_list, fp = self.fp, overwrite=True)
                    self.delete_disk(zone,disk_id)
                    self.progress_bar(int(10/1+len(head_disk_id)))

    def delete_peripheral_zone(self,zone):
        logger.debug("Delete " + zone + " zone")
        if self.contents_bool["server"] == True:
            if "compute" in self.cluster_info["clusterparams"]["server"][zone].keys():
                compute_node_id_list = []
                disk_id_list = []
                for i in self.cluster_info["clusterparams"]["server"][zone]["compute"].keys():
                    compute_node_id_list.append(self.cluster_info["clusterparams"]["server"][zone]["compute"][i]["node"]["id"])
                    #print(self.cluster_info["clusterparams"]["server"][zone]["compute"][i]["disk"].keys())
                    if "disk" in self.cluster_info["clusterparams"]["server"][zone]["compute"][i].keys():
                        for j in self.cluster_info["clusterparams"]["server"][zone]["compute"][i]["disk"].keys():
                            disk_id_list.append(self.cluster_info["clusterparams"]["server"][zone]["compute"][i]["disk"][j]["id"])
                            #print(self.cluster_info["clusterparams"]["server"][zone]["compute"][i]["disk"][j]["id"])

                #delete compute node
                if compute_node_id_list != []:
                    with futures.ThreadPoolExecutor(max_workers = self.max_workers, thread_name_prefix="thread") as executor:
                        for compute_node_id in compute_node_id_list:
                        #executor.submit(MulHelper(self, "build_one_compute_node"), kwargs={"zone": zone, "i": i})
                            printout("Delete compute zone(" + zone + ") : compute node(" + str(compute_node_id) + ")", info_type = 0, info_list = self.info_list, fp = self.fp, overwrite = True)
                            executor.submit(self.delete_server,zone,compute_node_id)
                            self.progress_bar(int(10/1+len(compute_node_id_list)))
                            '''
                    for compute_node_id in compute_node_id_list:
                        printout("Delete compute zone(" + zone + ") : compute node(" + str(compute_node_id) + ")", info_type = 0, info_list = self.info_list, fp = self.fp, overwrite=True)
                        self.delete_server(zone,compute_node_id)
                        self.progress_bar(10/1+len(compute_node_id_list))'''

                if disk_id_list != []:
                    with futures.ThreadPoolExecutor(max_workers = self.max_workers, thread_name_prefix="thread") as executor:
                        for disk_id in disk_id_list:
                        #executor.submit(MulHelper(self, "build_one_compute_node"), kwargs={"zone": zone, "i": i})
                            printout("Delete compute zone(" + zone + ") : compute disk(" + str(disk_id) + ")", info_type = 0, info_list = self.info_list, fp = self.fp, overwrite = True)
                            executor.submit(self.delete_disk,zone,disk_id)
                            self.progress_bar(int(10/1+len(disk_id_list)))
                            '''
                    for disk_id in disk_id_list:
                        printout("Delete compute zone(" + zone + ") : compute disk(" + str(disk_id) + ")", info_type = 0, info_list = self.info_list, fp = self.fp, overwrite=True)
                        self.delete_disk(zone,disk_id)
                        self.progress_bar(10/1+len(disk_id_list))'''
        
        if self.contents_bool["nfs"] == True:
            if self.nfs_zones != []:
                if zone in self.nfs_zones:
                    nfs_id = self.cluster_info["clusterparams"]["nfs"][zone]["id"]
                    printout("Delete compute zone(" + zone + ") : NFS(" + str(nfs_id) + ")", info_type = 0, info_list = self.info_list, fp = self.fp, overwrite=True)
                    self.delete_nfs(zone,nfs_id)
                    self.progress_bar(10)
        
        if self.contents_bool["switch"] == True:
            #if self.back_switch_id_list in locals():
            if self.back_switch_id_list != {}:
                if zone in self.back_switch_id_list.keys():
                    printout("Delete compute zone(" + zone + ") : back switch(" + str(self.back_switch_id_list[zone]) + ")", info_type = 0, info_list = self.info_list, fp = self.fp, overwrite=True)
                    self.delete_switch(zone,self.back_switch_id_list[zone])


            # if self.front_switch_id_list in locals():
            if self.front_switch_id_list != {}:
                printout("Delete compute zone(" + zone + ") : front switch(" + str(self.front_switch_id_list[zone]) + ")", info_type = 0, info_list = self.info_list, fp = self.fp, overwrite=True)
                self.delete_switch(zone,self.front_switch_id_list[zone])

                self.progress_bar(5)
        
    def delete_server(self,zone,node_id):
        if(self.api_index == True):
            while(True):
                delete_res = delete(self.url_list[zone] + self.sub_url[0] + "/" + str(node_id), self.auth_res)
                check = self.res_check(delete_res,"delete")
                if (check == True):
                    logger.debug("Delete this server:" + str(node_id))
                    break
                else:
                    self.delete_error()
        else:
            delete_res = "API is not used."
            

    def delete_disk(self,zone,disk_id):
        if(self.api_index == True):
            while(True):
                delete_res = delete(self.url_list[zone] + self.sub_url[1] + "/" + str(disk_id), self.auth_res)
                check = self.res_check(delete_res,"delete")
                if (check == True):
                    logger.debug("Delete this disk:" + str(disk_id))
                    break
                else:
                    self.delete_error()
        else:
            delete_res = "API is not used."

    def delete_switch(self,zone,switch_id):
        if(self.api_index == True):
            while(True):
                delete_res = delete(self.url_list[zone] + self.sub_url[2] + "/" + str(switch_id), self.auth_res)
                check = self.res_check(delete_res,"delete")
                if (check == True):
                    logger.debug("Delete this switch:" + str(switch_id))
                    break
                else:
                    self.delete_error()
        else:
            delete_res = "API is not used."
            
    def delete_bridge(self,zone,bridge_id):
        if(self.api_index == True):
            while(True):
                delete_res = delete(self.url_list[zone] + self.sub_url[4] + "/" + str(bridge_id), self.auth_res)
                check = self.res_check(delete_res,"delete")
                if (check == True):
                    logger.debug("Delete this bridge:" + str(bridge_id))
                    break
                else:
                    self.delete_error()
        else:
            delete_res = "API is not used."

    def delete_nfs(self,zone,nfs_id):
        if(self.api_index == True):
            while(True):
                delete_res = delete(self.url_list[zone] + self.sub_url[6] + "/" + str(nfs_id), self.auth_res)
                check = self.res_check(delete_res,"delete")
                if (check == True):
                    logger.debug("Delete this NFS:" + str(nfs_id))
                    break
                else:
                    self.delete_error()
        else:
            delete_res = "API is not used."
            
            
    def disconnect_bridge_switch(self,zone,switch_id):
        if(self.api_index == True):
            while(True):
                delete_res = delete(self.url_list[zone] + self.sub_url[2] + "/" + str(switch_id) + "/to" + self.sub_url[4], self.auth_res)
                check = self.res_check(delete_res, "delete")
                if (check == True):
                    logger.debug("Disconnect biridge and switch: " + str(switch_id))
                    break
                else:
                    self.delete_error()
        else:
            stop_res = "API is not used."
    
    def disconnect_server_switch(self,zone,nic_id):
        if(self.api_index == True):
            '''
            while(True):
                server_info = get(self.url_list[zone] + self.sub_url[0] + "/" + str(node_id), self.auth_res)
                check = self.res_check(server_info, "get")
                if(check == True): 
                    interface_info = server_info['Server']['Interfaces']
                    interface_id_list = []
                    for interface in interface_info:
                        if interface['Switch']['Scope'] == 'user':
                            interface_id_list.append(interface['ID'])
                    break
                else:
                    self.delete.error()
            '''
            while(True):
                delete_res = delete(self.url_list[zone] + self.sub_url[3] + "/" + str(nic_id) + "/to" + self.sub_url[2], self.auth_res)
                check = self.res_check(delete_res, "delete")
                if (check == True):
                    logger.debug("Disconnect server and switch(NIC ID): " + str(nic_id))
                    break
                else:
                    self.delete_error()
                '''
            if interface_id_list != []:
                for interface_id in interface_id_list:
                    while(True):
                        delete_res = delete(self.url_list[zone] + self.sub_url[1] + "/" + str(interface_id) + "/to" + self.sub_url[2], self.auth_res)
                        check = self.res_check(delete_res, "delete")
                        if (check == True):
                            logger.debug("Disconnect server and switch: " + str(node_id))
                            break
                        else:
                            self.delete_error()
            '''
        else:
            stop_res = "API is not used."
    
    def get_bridge_info(self,zone,bridge_id):
        if(self.api_index == True):
            while(True):
                get_res = get(self.url_list[zone] + self.sub_url[4] + "/" + str(bridge_id), self.auth_res)
                check = self.res_check(get_res, "get")
                if (check == True):
                    logger.debug("Get bridge infomation(bridge ID): " + str(bridge_id))
                    if get_res["Bridge"]["Info"] != None:
                        if "Switches" in get_res["Bridge"]["Info"].keys():
                            connect_bool = True
                        else:
                            connect_bool = False
                    else:
                        connect_bool = False
                    return connect_bool
                else:
                    self.delete_error()
        else:
            connect_bool = False
            return connect_bool
    
    
    
    
    def progress_bar(self, up):
        if len(self.zone_list) == 1:
            self.bar.update(int(up))
            self.progress_sum += int(up)
            
        elif len(self.zone_list) >= 2:
            self.bar.update(int(up)/(len(self.zone_list) + 0.5))
            self.progress_sum += int(up)/(len(self.zone_list) + 0.5)
        
    
#API response check
    def res_check(self, res, met):
        met_dict = {"get": "is_ok", "post": "is_ok", "put": "Success","delete": "Success"}
        index = met_dict[met]
                
        logger.debug("confirm API request(" + str(met) + ")")
        if (index in res.keys()):
            if res[index] == True:
                logger.debug("API processing succeeded")
                check = True
                return check
            else:
                logger.warning("API processing failed")
                printout("Error:",info_type = 0, info_list = self.info_list, fp = self.fp)
                check = False
                return check

        elif ("is_fatal" in res.keys()):
            logger.warning("API processing failed")
            printout("Status:" + res["status"],info_type = 0, info_list = self.info_list, fp = self.fp)
            printout("Error:" + res["error_msg"],info_type = 0, info_list = self.info_list, fp = self.fp)
            check = False
            return check
    
    

#API処理失敗時の処理
    def delete_error(self):
        logger.debug("decision of repeating to request")
        while(True):
            conf = printout("Try again??(yes/no):",info_type = 2, info_list = self.info_list, fp = self.fp)
            if conf == "yes":
                break
            elif conf == "no":
                printout("Stop processing.",info_type = 0, info_list = self.info_list, fp = self.fp)
                sys.exit()
            else:
                printout("Please answer yes or no.",info_list = self.info_list,fp = self.fp) 
                
    def handler(self, signal, frame):
        printout("Stop processing",info_type = 0, info_list = self.info_list, fp = self.fp)
        sys.exit()
        
    def validate_params(self,cluster_info):
        contents = [k for k in cluster_info["clusterparams"].keys()]
        contents_bool = {}
        zones = ["tk1a","tk1b","is1a","is1b","tk1v"]
        if "server" in contents:
            if cluster_info["clusterparams"]["server"] != {}:
                #zone = next(iter(cluster_info["clusterparams"]["server"]))
                #print(zone)
                server_zones = [zone for zone in cluster_info["clusterparams"]["server"].keys()]
                for zone in server_zones:
                    if "head" or "compute" in cluster_info["clusterparams"]["server"][zone].keys():
                        if "head" in cluster_info["clusterparams"]["server"][zone].keys():
                            if cluster_info["clusterparams"]["server"][zone]["head"] != {}:
                                contents_bool["server"] = True
                                break
                            else:
                                contents_bool["server"] = False
                        else:
                            if "compute" in cluster_info["clusterparams"]["server"][zone]["compute"]:
                                if cluster_info["clusterparams"]["server"][zone]["compute"] != {}:
                                    contents_bool["server"] = True
                                    break
                                else:
                                    contents_bool["server"] = False
                            else:
                                contents_bool["server"] = False
                        
                            
                    else:
                        contents_bool["server"] = False
            else:
                contents_bool["server"] = False
        else:
            contents_bool["server"] = False
            
        if "switch" in contents:
            if cluster_info["clusterparams"]["switch"] != {}:
                zone = next(iter(cluster_info["clusterparams"]["switch"]))
                if cluster_info["clusterparams"]["switch"][zone] != {}:
                    contents_bool["switch"] = True
                else:
                    contents_bool["switch"] = False
            else:
                contents_bool["switch"] = False
        else:
            contents_bool["switch"] = False
            
        if "bridge" in contents:
            if "front" in cluster_info["clusterparams"]["bridge"].keys():
                if cluster_info["clusterparams"]["bridge"]["front"] != None:
                    contents_bool["bridge"] = True
                else:
                    contents_bool["bridge"] = False
            else:
                contents_bool["bridge"] = False
        else:
            contents_bool["bridge"] = False
            
        if "nfs" in contents:
            if cluster_info["clusterparams"]["nfs"] != {}:
                zones = list(cluster_info["clusterparams"]["nfs"].keys())
                nfs_index_list =[]
                for zone in zones:
                    if cluster_info["clusterparams"]["nfs"][zone] != {}:
                        if cluster_info["clusterparams"]["nfs"][zone] != None:
                            #contents_bool["nfs"] = True
                            nfs_index_list.append(True)
                        else:
                            nfs_index_list.append(False)
                    else:
                        #contents_bool["nfs"] = False
                        nfs_index_list.append(False)
                if True in nfs_index_list:
                    contents_bool["nfs"] = True
                else:
                    contents_bool["nfs"] = False
            else:
                contents_bool["nfs"] = False
        else:
            contents_bool["nfs"] = False
        
        return contents_bool
    
