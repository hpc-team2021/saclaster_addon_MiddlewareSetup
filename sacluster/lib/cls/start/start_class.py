
import sys
import os
import datetime
import logging
from tqdm import tqdm
from concurrent import futures
import pprint

logger = logging.getLogger("sacluster").getChild(os.path.basename(__file__))

path = "../../.."
os.chdir(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(path + "/lib/others")

from API_method import  put
from info_print import printout



class start_sacluster:
    
    def __init__(self, cluster_info, auth_res, max_workers, fp = "", info_list = [1,0,0,0], api_index = True):
        self.cluster_info = cluster_info
        self.auth_res = auth_res
        self.fp = fp
        self.info_list = info_list
        self.api_index = api_index
        #[k for k in self.cluster_info.keys()]
        self.zone_list = [zone_list for zone_list in self.cluster_info["clusterparams"]["server"].keys()]
        
        #pprint.pprint(self.cluster_info)
        #sys.exit()
        #if "nfs" in self.cluster_info[cluster_id]["cluster_params"]:
        self.nfs_zones = []
        for zone in self.zone_list:
                if self.cluster_info["clusterparams"]["nfs"][zone] != None:
                    self.nfs_zones.append(zone)
        
        for zone in self.zone_list:
            if "head" in self.cluster_info["clusterparams"]["server"][zone].keys():
                self.head_zone = zone
        
        self.url_list = {}
        for zone in self.zone_list:
            self.url_list[zone] = "https://secure.sakura.ad.jp/cloud/zone/"+ zone +"/api/cloud/1.1"

        self.head_url = "https://secure.sakura.ad.jp/cloud/zone/"+ self.head_zone +"/api/cloud/1.1"

        self.sub_url = ["/server","/disk","/switch","/interface","/bridge","/tag","/appliance","/power"]

        self.date_modified = "Date modified:" + str(datetime.datetime.now().strftime("%Y_%m_%d"))
        
        self.max_workers = max_workers
        
    def __call__(self):
        #printout("Starting up the cluster : " + str(self.cluster_id), info_type = 0, info_list = self.info_list, fp = self.fp)
        #logger.debug("Starting the cluster")
        self.bar = tqdm(total = 100)
        self.bar.set_description('Progress rate')
        self.progress_sum = 0
        
        self.start_up_head_zone(self.head_zone)
        for zone in self.zone_list:
            if not zone in self.head_zone:
                self.start_up_peripheral_zone(zone)
        
        self.bar.update(100 - self.progress_sum)
        self.bar.close()
        #printout("Finished starting the cluster : " + str(self.cluster_id), info_type = 0, info_list = self.info_list, fp = self.fp)
        #logger.debug("Finished starting the cluster")

    def start_up_head_zone(self,zone):
        logger.debug("Start up " + zone + " zone")
        head_node_id = self.cluster_info["clusterparams"]["server"][zone]["head"]["node"]["id"]

        compute_node_id_list = []
        for i in self.cluster_info["clusterparams"]["server"][zone]["compute"].keys():
            if self.cluster_info["clusterparams"]["server"][zone]["compute"][i]["node"]["state"] == "down":
                compute_node_id_list.append(self.cluster_info["clusterparams"]["server"][zone]["compute"][i]["node"]["id"])

        #compute_node_id_list =  [self.cluster_info[self.cluster_id[0]]["cluster_params"]["server"][zone]["compute"][i]["node"]["id"] for i in self.cluster_info[self.cluster_id[0]]["cluster_params"]["server"][zone]["compute"].keys()]
        if self.cluster_info["clusterparams"]["server"][zone]["head"]["node"]["state"] == "down":
            printout("Start up head zone(" + zone + ") : head node(" + str(head_node_id) + ")", info_type = 0, info_list = self.info_list, fp = self.fp, overwrite = True)
            self.start_up_server(zone,head_node_id)
            self.progress_bar(5)
            
        if not compute_node_id_list == []:
            with futures.ThreadPoolExecutor(max_workers = self.max_workers, thread_name_prefix="thread") as executor:
                for compute_node_id in compute_node_id_list:
                #executor.submit(MulHelper(self, "build_one_compute_node"), kwargs={"zone": zone, "i": i})
                    printout("Start up head zone(" + zone + ") : compute node(" + str(compute_node_id) + ")", info_type = 0, info_list = self.info_list, fp = self.fp, overwrite = True)
                    executor.submit(self.start_up_server, zone, compute_node_id)
                    self.progress_bar(20/1+len(compute_node_id_list))
                    
                    '''
            for compute_node_id in compute_node_id_list:
                printout("Start up head zone(" + zone + ") : compute node(" + str(compute_node_id) + ")", info_type = 0, info_list = self.info_list, fp = self.fp)
                self.start_up_server(zone,compute_node_id)
                '''

        if zone in self.nfs_zones:
            if self.cluster_info["clusterparams"]["nfs"][zone]["state"] == "down":
                nfs_id = self.cluster_info["clusterparams"]["nfs"][zone]["id"]
                printout("Start up head zone(" + zone + ") : NFS(" + str(nfs_id) + ")", info_type = 0, info_list = self.info_list, fp = self.fp, overwrite = True)
                self.start_up_nfs(zone,nfs_id)
                self.progress_bar(10)

            
    def start_up_peripheral_zone(self, zone):
        logger.debug("Start up " + zone + " zone")

        compute_node_id_list = []
        for i in self.cluster_info["clusterparams"]["server"][zone]["compute"].keys():
            if self.cluster_info["clusterparams"]["server"][zone]["compute"][i]["node"]["state"] == "down":
                compute_node_id_list.append(self.cluster_info["clusterparams"]["server"][zone]["compute"][i]["node"]["id"])

        #compute_node_id_list =  [self.cluster_info[self.cluster_id[0]]["cluster_params"]["server"][zone]["compute"][i]["node"]["id"] for i in self.cluster_info[self.cluster_id[0]]["cluster_params"]["server"][zone]["compute"].keys()]
        if not compute_node_id_list == []:
            with futures.ThreadPoolExecutor(max_workers = self.max_workers, thread_name_prefix="thread") as executor:
                for compute_node_id in compute_node_id_list:
                #executor.submit(MulHelper(self, "build_one_compute_node"), kwargs={"zone": zone, "i": i})
                    printout("Start up compute zone(" + zone + ") : compute node(" + str(compute_node_id) + ")", info_type = 0, info_list = self.info_list, fp = self.fp, overwrite=True)
                    executor.submit(self.start_up_server, zone, compute_node_id)
                    self.progress_bar(20/1+len(compute_node_id_list))
            '''
            for compute_node_id in compute_node_id_list:
                printout("Start up compute zone(" + zone + ") : compute node(" + str(compute_node_id) + ")", info_type = 0, info_list = self.info_list, fp = self.fp)
                self.start_up_server(zone,compute_node_id)
        '''
        
        if zone in self.nfs_zones:
            if self.cluster_info["clusterparams"]["nfs"][zone]["state"] == "down":
                nfs_id = self.cluster_info["clusterparams"]["nfs"][zone]["id"]
                printout("Start up compute zone(" + zone + ") : NFS(" + str(nfs_id) + ")", info_type = 0, info_list = self.info_list, fp = self.fp, overwrite = True)
                self.start_up_nfs(zone,nfs_id)
                self.progress_bar(10)
                
    def start_up_server(self, zone, node_id):
        if (self.api_index == True):
            while(True):
                #print(zone + ":" + str(node_id))
                stop_res = put(self.url_list[zone] + self.sub_url[0] + "/" + str(node_id) + self.sub_url[7], self.auth_res)
                check = self.res_check(stop_res, "put")
                if check == True:
                    logger.debug("Start up this server: " + str(node_id))
                    break
                else:
                    self.start_error()
        else:
            stop_res = "API is not used."

    def start_up_nfs(self,nfs_zone,nfs_id):
        if (self.api_index == True):
            while(True):
                #print(nfs_zone + ":" + str(nfs_id))
                stop_res = put(self.url_list[nfs_zone] + self.sub_url[6] + "/" + str(nfs_id) + self.sub_url[7], self.auth_res)
                #print(stop_res)
                check = self.res_check(stop_res, "put")
                if check == True:
                    logger.debug("Start up this nfs: " + str(nfs_id))
                    break
                else:
                    self.start_error()
        else:
            stop_res = "API is not used."

    def progress_bar(self, up):
        if len(self.zone_list) == 1:
            self.bar.update(up)
            self.progress_sum += up
        
        elif len(self.zone_list) >= 2:
            self.bar.update(up/(len(self.zone_list) + 0.5))
            self.progress_sum += up/(len(self.zone_list) + 0.5)

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
    def start_error(self):
        logger.debug("decision of repeating to request")
        while(True):
            #conf = "no"
            conf = printout("Try again??(yes/no):",info_type = 2, info_list = self.info_list, fp = self.fp)
            if conf == "yes":
                break
            elif conf == "no":
                printout("Stop processing.",info_type = 0, info_list = self.info_list, fp = self.fp)
                sys.exit()
            else:
                printout("Please answer yes or no.",info_list = self.info_list,fp = self.fp) 
