
import sys
import os
import datetime
import logging
from tqdm import tqdm
from concurrent import futures

logger = logging.getLogger("sacluster").getChild(os.path.basename(__file__))

path = "../../.."
os.chdir(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(path + "/lib/others")

from API_method import delete
from info_print import printout



class stop_sacluster:
    
    def __init__(self, cluster_info, auth_res, max_workers, fp = "", info_list = [1,0,0,0], api_index = True):
        self.cluster_info = cluster_info
        self.auth_res = auth_res
        self.fp = fp
        self.info_list = info_list
        self.api_index = api_index
        #self.cluster_id = [k for k in self.cluster_info.keys()]
        self.zone_list = [zone_list for zone_list in self.cluster_info["clusterparams"]["server"].keys()]
        
        #If there is NFS, get NFS zone 
        self.nfs_zones = []
        for zone in self.zone_list:
                if self.cluster_info["clusterparams"]["nfs"][zone] != None:
                    self.nfs_zones.append(zone)
            
        #Get head zone
        for zone in self.zone_list:
            if "head" in self.cluster_info["clusterparams"]["server"][zone].keys():
                self.head_zone = zone
        
        #Get URL
        self.url_list = {}
        for zone in self.zone_list:
            self.url_list[zone] = "https://secure.sakura.ad.jp/cloud/zone/"+ zone +"/api/cloud/1.1"

        self.head_url = "https://secure.sakura.ad.jp/cloud/zone/"+ self.head_zone +"/api/cloud/1.1"

        #Get sub URL
        self.sub_url = ["/server","/disk","/switch","/interface","/bridge","/tag","/appliance","/power"]

        self.date_modified = "Date modified:" + str(datetime.datetime.now().strftime("%Y_%m_%d"))
        
        self.max_workers = max_workers

    def __call__(self):
        #printout("Start stopping the cluster : " + str(self.cluster_id[0]), info_type = 0, info_list = self.info_list, fp = self.fp)
        #logger.debug("Start stopping the cluster")
        self.bar = tqdm(total = 100)
        self.bar.set_description('Progress rate')
        self.progress_sum = 0
        
        for zone in self.zone_list:
            if not zone in self.head_zone:
                self.shutdown_peripheral_zone(zone)
                
        
        self.shutdown_head_zone(self.head_zone)
        self.bar.update(100 - self.progress_sum)
        self.bar.close()
        
        #printout("Finished stopping the cluster : " + str(self.cluster_id[0]), info_type = 0, info_list = self.info_list, fp = self.fp)
        #logger.debug("Finished stopping the cluster")

    def shutdown_head_zone(self,zone):
        logger.debug("Shutdown " + zone + " zone")
        head_node_id = self.cluster_info["clusterparams"]["server"][zone]["head"]["node"]["id"]

        compute_node_id_list = []
        for i in self.cluster_info["clusterparams"]["server"][zone]["compute"].keys():
            if self.cluster_info["clusterparams"]["server"][zone]["compute"][i]["node"]["state"] == "up":
                compute_node_id_list.append(self.cluster_info["clusterparams"]["server"][zone]["compute"][i]["node"]["id"])

        #compute_node_id_list =  [self.cluster_info[self.cluster_id[0]]["cluster_params"]["server"][zone]["compute"][i]["node"]["id"] for i in self.cluster_info[self.cluster_id[0]]["cluster_params"]["server"][zone]["compute"].keys()]
        if not compute_node_id_list == []:
            with futures.ThreadPoolExecutor(max_workers = self.max_workers, thread_name_prefix="thread") as executor:
                for compute_node_id in compute_node_id_list:
                #executor.submit(MulHelper(self, "build_one_compute_node"), kwargs={"zone": zone, "i": i})
                    printout("Shutdown head zone(" + zone + ") : compute node(" + str(compute_node_id) + ")", info_type = 0, info_list = self.info_list, fp = self.fp,overwrite = True)
                    executor.submit(self.shutdown_server, zone, compute_node_id)
                    self.progress_bar(25/1+len(compute_node_id_list))
            '''
            for compute_node_id in compute_node_id_list:
                printout("Shutdown head zone(" + zone + ") : compute node(" + str(compute_node_id) + ")", info_type = 0, info_list = self.info_list, fp = self.fp,overwrite = True)
                self.shutdown_server(zone,compute_node_id)
                self.progress_bar(25/1+len(compute_node_id_list))
                '''
        
        if self.cluster_info["clusterparams"]["server"][zone]["head"]["node"]["state"] == "up":
            printout("Shutdown head zone(" + zone + ") : head node(" + str(head_node_id) + ")", info_type = 0, info_list = self.info_list, fp = self.fp, overwrite = True)
            self.shutdown_server(zone,head_node_id)
            self.progress_bar(10)
        
        
        if zone in self.nfs_zones:
            if self.cluster_info["clusterparams"]["nfs"][zone]["state"] == "up":
                nfs_id = self.cluster_info["clusterparams"]["nfs"][zone]["id"]
                printout("Shutdown head zone(" + zone + ") : NFS(" + str(nfs_id) + ")", info_type = 0, info_list = self.info_list, fp = self.fp, overwrite = True)
                self.shutdown_nfs(zone,nfs_id)
                self.progress_bar(10)

            
    def shutdown_peripheral_zone(self, zone):
        logger.debug("Shutdown " + zone + " zone")

        compute_node_id_list = []
        for i in self.cluster_info["clusterparams"]["server"][zone]["compute"].keys():
            if self.cluster_info["clusterparams"]["server"][zone]["compute"][i]["node"]["state"] == "up":
                compute_node_id_list.append(self.cluster_info["clusterparams"]["server"][zone]["compute"][i]["node"]["id"])

        #compute_node_id_list =  [self.cluster_info[self.cluster_id[0]]["cluster_params"]["server"][zone]["compute"][i]["node"]["id"] for i in self.cluster_info[self.cluster_id[0]]["cluster_params"]["server"][zone]["compute"].keys()]
        
        if not compute_node_id_list == []:
            with futures.ThreadPoolExecutor(max_workers = self.max_workers, thread_name_prefix="thread") as executor:
                for compute_node_id in compute_node_id_list:
                #executor.submit(MulHelper(self, "build_one_compute_node"), kwargs={"zone": zone, "i": i})
                    printout("Shutdown compute zone(" + zone + ") : compute node(" + str(compute_node_id) + ")", info_type = 0, info_list = self.info_list, fp = self.fp, overwrite = True)
                    executor.submit(self.shutdown_server, zone, compute_node_id)
                    self.progress_bar(25/1+len(compute_node_id_list))
            '''
            for compute_node_id in compute_node_id_list:
                printout("Shutdown compute zone(" + zone + ") : compute node(" + str(compute_node_id) + ")", info_type = 0, info_list = self.info_list, fp = self.fp, overwrite = True)
                self.shutdown_server(zone,compute_node_id)
                self.progress_bar(25/1+len(compute_node_id_list))
        '''
        
        if zone in self.nfs_zones:
            if(self.cluster_info["clusterparams"]["nfs"][zone] != None):
                if self.cluster_info["clusterparams"]["nfs"][zone]["state"] == "up":
                    nfs_id = self.cluster_info["clusterparams"]["nfs"][zone]["id"]
                    printout("Shutdown compute zone(" + zone + ") : NFS(" + str(nfs_id) + ")", info_type = 0, info_list = self.info_list, fp = self.fp, overwrite = True)
                    self.shutdown_nfs(zone,nfs_id)
                    self.progress_bar(10)
    
    def shutdown_server(self, zone, node_id):
        if (self.api_index == True):
            while(True):
                #print(zone + ":" + str(node_id))
                stop_res = delete(self.url_list[zone] + self.sub_url[0] + "/" + str(node_id) + self.sub_url[7], self.auth_res)
                check = self.res_check(stop_res, "delete")
                if (check == True):
                    logger.debug("Shutdown this server: " + str(node_id))
                    break
                else:
                    self.stop_error()
        else:
            stop_res = "API is not used."

    def shutdown_nfs(self,nfs_zone,nfs_id):
        if (self.api_index == True):
            while(True):
                #print(nfs_zone + ":" + str(nfs_id))
                stop_res = delete(self.url_list[nfs_zone] + self.sub_url[6] + "/" + str(nfs_id) + self.sub_url[7], self.auth_res)
                #print(stop_res)
                check = self.res_check(stop_res, "delete")
                if check == True:
                    logger.debug("Shutdown this nfs: " + str(nfs_id))
                    break
                else:
                    self.stop_error()
        else:
            stop_res = "API is not used."
            
    def progress_bar(self, up):
        if len(self.zone_list) == 1:
            self.bar.update(up)
            self.progress_sum += up
            
        elif len(self.zone_list) >= 2:
            self.bar.update(up/(len(self.zone_list) + 0.5))
            self.progress_sum += up/(len(self.zone_list) + 0.5)

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
    def stop_error(self):
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
