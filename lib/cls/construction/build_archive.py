import sys
import json
import os
import base64
import requests
import pandas as pd
import random
import pprint
import datetime
import time
import ipaddress


path = "../../.."
os.chdir(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(path + "/lib/others")
pprint.pprint(sys.path)
from API_method import get, post, put
from info_print import printout

def json_input(filename):
    with open(filename, 'r') as f:
        json_f = json.load(f)
    return json_f


zone = "tk1v"    
url = "https://secure.sakura.ad.jp/cloud/zone/"+ zone +"/api/cloud/1.1"

def main(fp = "" , info_list = [1,0,0,0] , api_index = True):
    filename = "Setting.json"

    if(os.path.exists(path + "/setting/" + filename) == True):
        setting_info = json_input(path + "/setting/" + filename)
        global auth_res
        auth_res = base64.b64encode('{}:{}'.format(setting_info["access token"], setting_info["access token secret"]).encode('utf-8'))
    else:
        _ = printout("Error: Setting.json does not exist in sacluster/setting",info_list = [1,0,0,0], fp = '')
        sys.exit()
    while (True):
        config_file = printout("Configuration File Name:",info_type = 2, info_list = [1,0,0,0], fp = '')
        #configuration_info = json_input("./trial_configfile2.json")
        if(os.path.exists("./" + config_file ) == True):
            global configuration_info
            configuration_info = json_input("./" + config_file)
            break
        else:
            _ = printout("INFO: " + config_file + " does not exist. ",info_list = [1,0,0,0], fp = '')

    starttime = time.time()
    auth_res = build_cluster(fp = fp, info_list  = info_list, api_index = api_index)

    elapsed_time = time.time() - starttime

    _ = printout("elapsed_time:{0}".format(elapsed_time) + "[sec]" , info_list = [1,0,0,0], fp = '')


def build_server(url,sub_url,node_name,switch_id = 0,fp = "", info_list = [1,0,0,0], api_index = True):
    _ = printout(node_name ,info_list = info_list,fp = fp)
    if "head" in node_name:
        node_planid = Serverplan(configuration_info["the number of core for head node"],configuration_info["size of memory for head node"])
        param = {"Server":{"Name":node_name,"ServerPlan":{"ID":node_planid},"ConnectedSwitches":[{"Scope":"shared"}]},"Count":0}
        #param = {"Server":{"Name":node_name,"ServerPlan":{"ID":"123456"},"ConnectedSwitches":[{"Scope":"shared"}]},"Count":0}
    elif "compute" in node_name:
        node_planid = Serverplan(configuration_info["the number of core for compute node"],configuration_info["size of memory for compute node"])
        param = {"Server":{"Name":node_name,"ServerPlan":{"ID":node_planid},"ConnectedSwitches":[{"ID":switch_id}]},"Count":0}
    if (api_index == True):
        while(True):
            server_response = post(url+sub_url[0],auth_res,param)
            if ("is_ok" in server_response.keys()):
                if server_response["is_ok"] == True:
                    node_id = server_response["Server"]["ID"]
                    break
                else:
                    _ = printout("Error:", info_list = info_list,fp = fp)
                    rf = response_output("Error_build_" + node_name ,server_response)
                    while(True):
                        conf = printout("Try again??(yes/no):",info_type = 2, info_list = [1,0,0,0], fp = '')
                        if conf == "yes":
                            break
                        elif conf == "no":
                            _ = printout("Stop processing.", info_list = info_list,fp = fp)
                            sys.exit()
                        else:
                            _ = printout("Please answer yes or no.",info_list = info_list,fp = fp)

            elif ("is_fatal" in server_response.keys()):
                _ = printout("Error:" + server_response["error_msg"], info_list = info_list,fp = fp)
                rf = response_output("Error_build_" + node_name ,server_response)
                while(True):
                        conf = printout("Try again??(yes/no):",info_type = 2, info_list = [1,0,0,0], fp = '')
                        if conf == "yes":
                            break
                        elif conf == "no":
                            _ = printout("Stop processing.", info_list = info_list,fp = fp)
                            sys.exit()
                        else:
                            _ = printout("Please answer yes or no.",info_list = info_list,fp = fp)
    else:
        server_response = "API is not used."
        node_id = "000"

    rf = response_output("build_" + node_name ,server_response)

    return server_response,node_id

def create_switch(url,sub_url,node = "",fp = "", info_list = [1,0,0,0], api_index = True):
    #sub_url = "/switch"
    _ = printout("creating switch ……", fp = fp , info_list = info_list)
    #switch_info = get(url+sub_url[2],auth_res)
    #switch_number = int(switch_info["Count"]) + 1
    if node == "compute":
        switch_name = "Switch for compute node"
    else:
        switch_name = "Switch for " + configuration_info["config name"]
    #switch_name = "switch"
    ip = str(ipaddress.ip_address('192.168.1.254'))
    networkmask = 24
    switch_param = {"Switch":{"Name":switch_name,"UserSubnet":{"DefaultRoute":ip,"NetworkMaskLen":networkmask}},"Count":0}
    
    if (api_index == True):
        while(True):
            switch_response = post(url+sub_url[2],auth_res,switch_param)
            if ("is_ok" in switch_response.keys()):
                if switch_response["is_ok"] == True:
                    switch_id = switch_response["Switch"]["ID"]
                    break
                else:
                    _ = printout("Error:",fp = fp, info_list = info_list)
                    rf = response_output("Error_create_switch",switch_response)
                    while(True):
                            conf = printout("Try again??(yes/no):",info_type = 2, info_list = [1,0,0,0], fp = '')
                            if conf == "yes":
                                break
                            elif conf == "no":
                                _ = printout("Stop processing.", info_list = info_list,fp = fp)
                                sys.exit()
                            else:
                                _ = printout("Please answer yes or no.",info_list = info_list,fp = fp)
            elif ("is_fatal" in switch_response.keys()):
                _ = printout("Error:" + switch_response["error_msg"],fp = fp, info_list = info_list)
                rf = response_output("Error_create_switch",switch_response)
                while(True):
                            conf = printout("Try again??(yes/no):",info_type = 2, info_list = [1,0,0,0], fp = '')
                            if conf == "yes":
                                break
                            elif conf == "no":
                                _ = printout("Stop processing.", info_list = info_list,fp = fp)
                                sys.exit()
                            else:
                                _ = printout("Please answer yes or no.",info_list = info_list,fp = fp)
    else:
        switch_response = "API is not used."
        switch_id = "0000"

    rf = response_output("create_switch",switch_response)
    
    return switch_response,switch_id

def add_interface(url,sub_url,node_id,fp = "", info_list = [1,0,0,0], api_index = True):
    #sub_url = "/interface"
    '''
    ip = ipaddress.ip_address('192.168.1.0')
    interface_info = get(url+sub_url[3],auth_res)
    interface_number = int(interface_info["Count"])
    ip += interface_number
    str_ip = str(ip)
    '''
    #add_nic_param = {"Interface":{"UserIPAddress":str_ip ,"Server":{"ID":node_id}}, "Count":0}
    add_nic_param = {"Interface":{"Server":{"ID":node_id}}, "Count":0}
    #add_nic_param = {"Interface":{"Server":{"ID":"123456"}}, "Count":0}
    if (api_index == True):
        while(True):
            add_nic_response = post(url+sub_url[3],auth_res,add_nic_param)
            if ("is_ok" in add_nic_response.keys()):
                if add_nic_response["is_ok"] == True:
                    nic_id = add_nic_response["Interface"]["ID"]
                    break
                else:
                    _ = printout("Error:",fp = fp, info_list = info_list)
                    rf = response_output("Error_add_interface",add_nic_response)
                    while(True):
                            conf = printout("Try again??(yes/no):",info_type = 2, info_list = [1,0,0,0], fp = '')
                            if conf == "yes":
                                break
                            elif conf == "no":
                                _ = printout("Stop processing.", info_list = info_list,fp = fp)
                                sys.exit()
                            else:
                                _ = printout("Please answer yes or no.",info_list = info_list,fp = fp)
            elif ("is_fatal" in add_nic_response.keys()):
                _ = printout("Error:" + add_nic_response["error_msg"],fp = fp, info_list = info_list)
                rf = response_output("Error_add_interface",add_nic_response)
                while(True):
                            conf = printout("Try again??(yes/no):",info_type = 2, info_list = [1,0,0,0], fp = '')
                            if conf == "yes":
                                break
                            elif conf == "no":
                                _ = printout("Stop processing.", info_list = info_list,fp = fp)
                                sys.exit()
                            else:
                                _ = printout("Please answer yes or no.",info_list = info_list,fp = fp)
    else:
        add_nic_response = "API is not used."
        nic_id = "0000"
    
    rf = response_output("add_interface",add_nic_response)

    return add_nic_response,nic_id

def connect_switch(url,switch_id,nic_id,fp = "", info_list = [1,0,0,0], api_index = True):
    sub_url_con = "/interface/" + nic_id + "/to/switch/" + switch_id
    if (api_index == True):
        while(True):
            connect_switch_response = put(url+sub_url_con,auth_res)
            if ("Success" in connect_switch_response.keys()):
                if connect_switch_response["Success"] == True:
                    break
                else:
                    _ = printout("Error:",fp = fp, info_list = info_list)
                    rf = response_output("Error_connect_switch",connect_switch_response)
                    while(True):
                            conf = printout("Try again??(yes/no):",info_type = 2, info_list = [1,0,0,0], fp = '')
                            if conf == "yes":
                                break
                            elif conf == "no":
                                _ = printout("Stop processing.", info_list = info_list,fp = fp)
                                sys.exit()
                            else:
                                _ = printout("Please answer yes or no.",info_list = info_list,fp = fp)
            elif ("is_fatal" in connect_switch_response.keys()):
                _ = printout("Error:" + connect_switch_response["error_msg"],fp = fp, info_list = info_list)
                rf = response_output("Error_connect_switch",connect_switch_response)
                while(True):
                            conf = printout("Try again??(yes/no):",info_type = 2, info_list = [1,0,0,0], fp = '')
                            if conf == "yes":
                                break
                            elif conf == "no":
                                _ = printout("Stop processing.", info_list = info_list,fp = fp)
                                sys.exit()
                            else:
                                _ = printout("Please answer yes or no.",info_list = info_list,fp = fp)
    else:
        connect_switch_response = "API is not used."

    rf = response_output("connect_switch",connect_switch_response)

    return connect_switch_response


def add_disk(url,sub_url,disk_name,zone,fp = "", info_list = [1,0,0,0], api_index = True):
    _ = printout("creating disk ……", fp = fp, info_list = info_list)
    if "head" in disk_name:
        disk_type = configuration_info["disk type for head node"]
        disk_size = configuration_info["disk size for head node"]
        os_type = configuration_info["OS ID for head node"]
    elif "compute" in disk_name:
        disk_type = configuration_info["disk type for compute node"]
        disk_size = configuration_info["disk size for compute node"]
        os_type = configuration_info["OS ID for compute node"][zone]
    if disk_type == "SSD":
        disk_type_id = 4
    elif disk_type == "HDD":
        disk_type_id = 2
    else:
        _ = printout("not disk type",fp = fp , info_list = info_list)

    param = {"Disk":{"Name":disk_name,"Plan":{"ID":disk_type_id},"SizeMB":disk_size,"SourceArchive":{"Availability": "available","ID":os_type}},"Config":{"Password":"takahira","Notes":{"ID":"112900860243"}}}
    #param = {"Disk":{"Name":disk_name,"Plan":{"ID":3},"SizeMB":disk_size,"SourceArchive":{"Availability": "available","ID":os_type}},"Config":{"Password":"takahira","Notes":{"ID":"112900860243"}}}
    if (api_index == True):
        while(True):
            disk_res = post(url+sub_url[1], auth_res,param)
            if ("is_ok" in disk_res.keys()):
                if disk_res["is_ok"] == True:
                    disk_id = disk_res["Disk"]["ID"]
                    break
                else:
                    _ = printout("Error:",fp = fp, info_list = info_list)
                    rf = response_output("Error_create_disk",disk_res)
                    while(True):
                            conf = printout("Try again??(yes/no):",info_type = 2, info_list = [1,0,0,0], fp = '')
                            if conf == "yes":
                                break
                            elif conf == "no":
                                _ = printout("Stop processing.", info_list = info_list,fp = fp)
                                sys.exit()
                            else:
                                _ = printout("Please answer yes or no.",info_list = info_list,fp = fp)
            elif ("is_fatal" in disk_res.keys()):
                _ = printout("Error:" + disk_res["error_msg"],fp = fp, info_list = info_list)
                rf = response_output("Error_create_disk",disk_res)
                while(True):
                            conf = printout("Try again??(yes/no):",info_type = 2, info_list = [1,0,0,0], fp = '')
                            if conf == "yes":
                                break
                            elif conf == "no":
                                _ = printout("Stop processing.", info_list = info_list,fp = fp)
                                sys.exit()
                            else:
                                _ = printout("Please answer yes or no.",info_list = info_list,fp = fp)
    else:
        disk_res = "API is not used."
        disk_id = "0000"
    
    rf = response_output("create_disk",disk_res)
    
    return disk_res,disk_id

def connect_server_disk(url,disk_id ,server_id, fp = "", info_list = [1,0,0,0], api_index = True):
    url_disk = "/disk/" + disk_id + "/to/server/" + server_id
    if (api_index == True):
        while(True):
            server_disk_res = put(url+url_disk,auth_res)
            if ("Success" in server_disk_res.keys()):
                if server_disk_res["Success"] == True:
                    break
                else:
                    _ = printout("Error:",fp = fp, info_list = info_list)
                    rf = response_output("Error_connect_disk",server_disk_res)
                    while(True):
                            conf = printout("Try again??(yes/no):",info_type = 2, info_list = [1,0,0,0], fp = '')
                            if conf == "yes":
                                break
                            elif conf == "no":
                                _ = printout("Stop processing.", info_list = info_list,fp = fp)
                                sys.exit()
                            else:
                                _ = printout("Please answer yes or no.",info_list = info_list,fp = fp)
            elif ("is_fatal" in server_disk_res.keys()):
                _ = printout("Error:" + server_disk_res["error_msg"],fp = fp, info_list = info_list)
                rf = response_output("Error_connect_disk",server_disk_res)
                while(True):
                            conf = printout("Try again??(yes/no):",info_type = 2, info_list = [1,0,0,0], fp = '')
                            if conf == "yes":
                                break
                            elif conf == "no":
                                _ = printout("Stop processing.", info_list = info_list,fp = fp)
                                sys.exit()
                            else:
                                _ = printout("Please answer yes or no.",info_list = info_list,fp = fp)
    else:
        server_disk_res = "API is not used."

    
    rf = response_output("connect_disk",server_disk_res)
    #_ = printout("connecting disk ……", info_list = info_list, fp = fp)

    return server_disk_res

'''

def iso_image_insert(url,node_name,server_id,zone,fp = "", info_list = [1,0,0,0], api_index = True):
    _ = printout("inserting OS image ……", info_list = info_list, fp = fp)
    if "head" in node_name:
        iso_image = configuration_info["OS ID for head node"]
    elif "compute" in node_name:
        iso_image = configuration_info["OS ID for compute node in " + zone]
    
    url_iso_image = "/server/" + server_id +"/cdrom"
    param = {"CDROM":{"ID":iso_image},"Count":0}
    if (api_index == True):
        iso_image_res = put(url+url_iso_image, auth_res,param)
        if ("Success" in iso_image_res.keys()):
            if iso_image_res["Success"] == True:
                pass
            else:
                _ = printout("Error:",fp = fp, info_list = info_list)
                rf = response_output("Error_insert_iso_image",iso_image_res)
                sys.exit()
        elif ("is_fatal" in iso_image_res.keys()):
            _ = printout("Error:" + iso_image_res["error_msg"],fp = fp, info_list = info_list)
            rf = response_output("Error_insert_iso_image",iso_image_res)
            sys.exit()
    else:
        iso_image_res = "API is not used."

    rf = response_output("insert_iso_image",iso_image_res)
    
    return iso_image_res
'''

def interface_info(url,sub_url,node_id,fp = "", info_list = [1,0,0,0], api_index = True):
    url_interface = sub_url[0] + "/" + node_id + sub_url[3]
    if (api_index == True):
        while(True):
            interface_info = get(url+url_interface,auth_res)
            if ("is_ok" in interface_info.keys()):
                if interface_info["is_ok"] == True:
                    interface_info_list = interface_info["Interfaces"]
                    l_id = [d.get('ID') for d in interface_info_list]
                    break
                else:
                    _ = printout("Error:",fp = fp, info_list = info_list)
                    rf = response_output("Error_interface_info",interface_info)
                    while(True):
                            conf = printout("Try again??(yes/no):",info_type = 2, info_list = [1,0,0,0], fp = '')
                            if conf == "yes":
                                break
                            elif conf == "no":
                                _ = printout("Stop processing.", info_list = info_list,fp = fp)
                                sys.exit()
                            else:
                                _ = printout("Please answer yes or no.",info_list = info_list,fp = fp)
            elif ("is_fatal" in interface_info.keys()):
                _ = printout("Error:" + interface_info["error_msg"],fp = fp, info_list = info_list)
                rf = response_output("Error_interface_info",interface_info)
                while(True):
                            conf = printout("Try again??(yes/no):",info_type = 2, info_list = [1,0,0,0], fp = '')
                            if conf == "yes":
                                break
                            elif conf == "no":
                                _ = printout("Stop processing.", info_list = info_list,fp = fp)
                                sys.exit()
                            else:
                                _ = printout("Please answer yes or no.",info_list = info_list,fp = fp)
    else:
        interface_info = "API is not used."
        l_id = ["00","00"]

    rf = response_output("interface_info_" + node_id , interface_info)

    return l_id


def setting_ip(url,sub_url,interface_id,fp = "", info_list = [1,0,0,0], api_index = True):
    ip = ipaddress.ip_address('192.168.1.0')
    interface_info = get(url+sub_url[3],auth_res)
    interface_number = int(interface_info["Count"])
    ip += interface_number
    str_ip = str(ip)
    url_interface = sub_url[3] + "/" + interface_id
    param = {"Interface":{"UserIPAddress":str_ip},"Count":0}
    set_ip_res = put(url+url_interface,auth_res,param)
    rf = response_output("setting_ipaddress",set_ip_res)
    return set_ip_res

def build_compute_node(url,sub_url,switch_id,n,zone,fp = "", info_list = [1,0,0,0], api_index = True):
    i = 0
    l_compute_node_id = []
    for i in range(n):
        i += 1
        compute_node_name = "compute_node_00"+str(i)
        compute_server_response,compute_node_id = build_server(url,sub_url,compute_node_name,switch_id ,fp = fp, info_list  = info_list, api_index = api_index)
        '''
        #setting private IPAddress
        l_id = interface_info(url,sub_url,compute_node_id,fp = fp, info_list  = info_list, api_index = api_index)
        for j in l_id:
            set_ip_res = setting_ip(url,sub_url,j,fp = fp, info_list  = info_list, api_index = api_index)
        '''
        #add disk in compute node
        compute_disk_res , compute_disk_id = add_disk(url,sub_url,compute_node_name,zone,fp = fp, info_list  = info_list, api_index = api_index)
        #compute_disk_id = compute_disk["Disk"]["ID"]
        compute_server_disk_res = connect_server_disk(url,compute_disk_id,compute_node_id,fp = fp, info_list  = info_list, api_index = api_index)

        #add iso image computenode
        #iso_imege_res = iso_image_insert(url,compute_node_name,compute_node_id,zone,fp = fp, info_list  = info_list, api_index = api_index)
        l_compute_node_id.append(compute_node_id)
    return compute_server_response,l_compute_node_id

def create_bridge(url,sub_url,fp = "", info_list = [1,0,0,0], api_index = True):
    _ = printout("creating bridge ……", fp = fp ,info_list = info_list)
    #bridge_info = get(url+sub_url[4],auth_res)
    #bridge_number = int(bridge_info["Count"]) + 1
    bridge_name = "Bridge for " + configuration_info["config name"]
    param = {"Bridge":{"Name":bridge_name}}

    if (api_index == True):
        while(True):
            bridge_res = post(url+sub_url[4],auth_res,param)
            if ("is_ok" in bridge_res.keys()):
                if bridge_res["is_ok"] == True:
                    bridge_id = bridge_res["Bridge"]["ID"]
                    break
                else:
                    _ = printout("Error:",fp = fp, info_list = info_list)
                    rf = response_output("Error_create_bridge",bridge_res)
                    while(True):
                            conf = printout("Try again??(yes/no):",info_type = 2, info_list = [1,0,0,0], fp = '')
                            if conf == "yes":
                                break
                            elif conf == "no":
                                _ = printout("Stop processing.", info_list = info_list,fp = fp)
                                sys.exit()
                            else:
                                _ = printout("Please answer yes or no.",info_list = info_list,fp = fp)
            elif ("is_fatal" in bridge_res.keys()):
                _ = printout("Error:" + bridge_res["error_msg"],fp = fp, info_list = info_list)
                rf = response_output("Error_create_bridge",bridge_res)
                while(True):
                            conf = printout("Try again??(yes/no):",info_type = 2, info_list = [1,0,0,0], fp = '')
                            if conf == "yes":
                                break
                            elif conf == "no":
                                _ = printout("Stop processing.", info_list = info_list,fp = fp)
                                sys.exit()
                            else:
                                _ = printout("Please answer yes or no.",info_list = info_list,fp = fp)
    else:
        bridge_res = "API is not used."
        bridge_id = "0000"

    rf = response_output("create_bridge",bridge_res)
    
    return bridge_res,bridge_id

def connect_bridge_switch(url,switch_id,bridge_id,fp = "", info_list = [1,0,0,0], api_index = True):
    url_bridge = "/switch/" + switch_id + "/to/bridge/" + bridge_id
    if (api_index == True):
        while(True):
            bridge_switch_res = put(url+url_bridge,auth_res)
            if ("Success" in bridge_switch_res.keys()):
                if bridge_switch_res["Success"] == True:
                    break
                else:
                    _ = printout("Error:",fp = fp, info_list = info_list)
                    rf = response_output("Error_connect_bridge",bridge_switch_res)
                    while(True):
                            conf = printout("Try again??(yes/no):",info_type = 2, info_list = [1,0,0,0], fp = '')
                            if conf == "yes":
                                break
                            elif conf == "no":
                                _ = printout("Stop processing.", info_list = info_list,fp = fp)
                                sys.exit()
                            else:
                                _ = printout("Please answer yes or no.",info_list = info_list,fp = fp)
            elif ("is_fatal" in bridge_switch_res.keys()):
                _ = printout("Error:" + bridge_switch_res["error_msg"],fp = fp, info_list = info_list)
                rf = response_output("Error_connect_bridge",bridge_switch_res)
                while(True):
                            conf = printout("Try again??(yes/no):",info_type = 2, info_list = [1,0,0,0], fp = '')
                            if conf == "yes":
                                break
                            elif conf == "no":
                                _ = printout("Stop processing.", info_list = info_list,fp = fp)
                                sys.exit()
                            else:
                                _ = printout("Please answer yes or no.",info_list = info_list,fp = fp)
    else:
        bridge_switch_res = "API is not used."
    
    rf = response_output("connect_bridge",bridge_switch_res)
    return bridge_switch_res


def setting_nfs(url,sub_url,zone,switch_id,fp = "", info_list = [1,0,0,0], api_index = True):
    _ = printout("setting NFS ……",fp = fp ,info_list = info_list)
    nfs_name = "NFS"
    nfs_plan = configuration_info["NFS plan ID in " + zone]
    ip = ipaddress.ip_address('192.168.1.200')
    str_ip = str(ip)
    nfs_param = {"Appliance":{"Class":"nfs","Name":nfs_name,"Plan":{"ID":nfs_plan},"Remark":{"Network":{"NetworkMaskLen":24},"Servers":[{"IPAddress":str_ip}],"Switch":{"ID":switch_id}}}} 
    if (api_index == True):
        while(True):
            nfs_res = post(url+sub_url[6],auth_res,nfs_param)
            if ("is_ok" in nfs_res.keys()):
                if nfs_res["is_ok"] == True:
                    nfs_id = nfs_res["Appliance"]["ID"]
                    break
                else:
                    _ = printout("Error:",fp = fp, info_list = info_list)
                    rf = response_output("Error_setting_nfs",nfs_res)
                    while(True):
                            conf = printout("Try again??(yes/no):",info_type = 2, info_list = [1,0,0,0], fp = '')
                            if conf == "yes":
                                break
                            elif conf == "no":
                                _ = printout("Stop processing.", info_list = info_list,fp = fp)
                                sys.exit()
                            else:
                                _ = printout("Please answer yes or no.",info_list = info_list,fp = fp)
            elif ("is_fatal" in nfs_res.keys()):
                _ = printout("Error:" + nfs_res["error_msg"],fp = fp, info_list = info_list)
                rf = response_output("Error_setting_nfs",nfs_res)
                while(True):
                            conf = printout("Try again??(yes/no):",info_type = 2, info_list = [1,0,0,0], fp = '')
                            if conf == "yes":
                                break
                            elif conf == "no":
                                _ = printout("Stop processing.", info_list = info_list,fp = fp)
                                sys.exit()
                            else:
                                _ = printout("Please answer yes or no.",info_list = info_list,fp = fp)
    else:
        nfs_res = "API is not used."
        inf_id = "0000"
    
    rf = response_output("setting_nfs",nfs_res)

    return nfs_res,nfs_id


def response_output(res_filename,response):
    dt_now = datetime.datetime.now()
    dt_ymd = dt_now.strftime("%Y_%m_%d")
    dt_now = dt_now.strftime("%Y_%m_%d_%H%M%S")
    os.makedirs("./response/" + dt_ymd, exist_ok=True)
    rf = open("./response/" + dt_ymd + "/" + dt_now + "_" + res_filename + ".txt", 'w', encoding = 'utf-8')
    json.dump(response, rf ,indent = 4,ensure_ascii=False)
    rf.close()

    return rf

def Serverplan(core, memory):
    #csvファイルがある時ない時
    serverplan_df = pd.read_csv(path + '/../../temp/serverplan_2.csv')
    serverplan = serverplan_df[(serverplan_df["Core"] == core) & (serverplan_df["Memory"] == memory)]
    if serverplan.empty:
        _ = printout("Error:ServerPlan does not exist. There is an error in core or memory.",info_list = [1,0,0,0], fp = '')
        sys.exit()
    else:
        serverplan_id = int(serverplan.iat[0,0])

    return serverplan_id


def starting_server(url,fp = "", info_list = [1,0,0,0], api_index = True):
    server_res = get(url+"/server",auth_res)
    cluster_name = configuration_info["config name"]
    tags_info = server_res["Servers"]
    l_index = [d.get('Index') for d in tags_info]
    l_name = [d.get('Name') for d in tags_info]
    l_tags = [d.get('Tags') for d in tags_info]
    l_id = [d.get('ID') for d in tags_info]

    count = 0 
    while count < len(l_tags):
        if not l_tags[count]:
            l_tags[count] = "none"
        count += 1

    tags_df = pd.DataFrame({'Index': l_index,
                            'Name': l_name,
                            'ID': l_id,
                            'Tag': l_tags})

    tag_info_df = pd.concat(tags_df.apply(flatten, axis=1).values).loc[:, ['Name', 'ID', 'Tag']]
    tag = tag_info_df[(tag_info_df["Tag"] == cluster_name)]
    cluster_id_list = tag["ID"].tolist()
    for cluster_id in cluster_id_list:
        sub_url_power = "/server/" + cluster_id + "/power"
        server_power_res = put(url+sub_url_power, auth_res)
        rf = response_output("starting_server",server_power_res)
    
    return server_power_res

def flatten(row):
    df1 = pd.Series(row['Name']).to_frame(name='Name')
    df2 = pd.DataFrame([{'ID': row['ID']}])
    df3 = pd.Series(row['Tag']).to_frame(name='Tag')
    df1['key'] = df2['key'] = df3['key'] = 0
    return df1.merge(df2, how='outer').merge(df3, how='outer').drop(columns='key')


def cluster_id_def(url,sub_url,fp = "", info_list = [1,0,0,0], api_index = True):
    if (api_index == True):
        get_cluster_id_info = get(url+sub_url[0],auth_res)
        while (True):
            if ("is_ok" in get_cluster_id_info.keys()):
                if get_cluster_id_info["is_ok"] == True:
                    cluster_id_info = get_cluster_id_info["Servers"]
                    cluster_id_list = [d.get('Tags') for d in cluster_id_info]
                    while (True):
                        cluster_id = random.randint(100000,999999)
                        if not cluster_id in cluster_id_list:
                            cluster_id_list.append(cluster_id)
                            break
                        else:
                            _ = printout("Duplication of cluster ID.", info_list = info_list, fp = fp)
                            _ = printout("Reissuing cluster ID.", info_list = info_list, fp = fp)
                    break
                else:
                    _ = printout("Error:",fp = fp, info_list = info_list)
                    rf = response_output("Error_get_cluster_id_info",get_cluster_id_info)
                    while(True):
                        conf = printout("Try again??(yes/no):",info_type = 2, info_list = [1,0,0,0], fp = '')
                        if conf == "yes":
                            break
                        elif conf == "no":
                            _ = printout("Stop processing.", info_list = info_list,fp = fp)
                            sys.exit()
                        else:
                            _ = printout("Please answer yes or no.",info_list = info_list,fp = fp)
            elif ("is_fatal" in get_cluster_id_info.keys()):
                _ = printout("Error:" + get_cluster_id_info["error_msg"],fp = fp, info_list = info_list)
                rf = response_output("Error_get_cluster_id_info",get_cluster_id_info)
                while(True):
                    conf = printout("Try again??(yes/no):",info_type = 2, info_list = [1,0,0,0], fp = '')
                    if conf == "yes":
                        break
                    elif conf == "no":
                        _ = printout("Stop processing.", info_list = info_list,fp = fp)
                        sys.exit()
                    else:
                        _ = printout("Please answer yes or no.",info_list = info_list,fp = fp)
    else:
        get_cluster_id_info = "API is not used."
        cluster_id = random.randint(100000,999999)
    
    rf = response_output("get_cluster_id_info",get_cluster_id_info)
    return cluster_id

def build_head_zone(url,sub_url,zone,bridge_id = "",fp = "", info_list = [1,0,0,0], api_index = True):
    head_node_name = "headnode"
    server_response,head_node_id = build_server(url,sub_url,head_node_name, fp = fp, info_list  = info_list, api_index = api_index)
    #add disk headnode
    head_disk_res,head_disk_id = add_disk(url,sub_url,head_node_name,zone,fp = fp, info_list  = info_list, api_index = api_index)
    head_server_disk_res = connect_server_disk(url,head_disk_id,head_node_id,fp = fp, info_list  = info_list, api_index = api_index)
    #add iso image headnode
    #head_iso_image_res = iso_image_insert(url,head_node_name,head_node_id,zone,fp = fp, info_list  = info_list, api_index = api_index)
    #create switch
    head_switch_response,head_switch_id = create_switch(url,sub_url,fp = fp, info_list  = info_list, api_index = api_index)
    #connect bridge to switch
    
    #add interface in head node
    add_nic_response,nic_id = add_interface(url,sub_url,head_node_id,fp = fp, info_list  = info_list, api_index = api_index)

    #interface to switch
    connect_switch_response = connect_switch(url,head_switch_id,nic_id,fp = fp, info_list  = info_list, api_index = api_index)
    #create compute node
    number_of_compute_node = int(configuration_info["the number of compute node in " + zone])
    compute_server_response,l_compute_node_id = build_compute_node(url,sub_url,head_switch_id,number_of_compute_node,zone,fp = fp, info_list  = info_list, api_index = api_index)
    if configuration_info["compute network"] == "True":
        com_network,com_nic_list = compute_network(url,sub_url,l_compute_node_id,fp = fp, info_list  = info_list, api_index = api_index)
    id_list = [head_node_id , head_disk_id , head_switch_id , nic_id , l_compute_node_id]

    return id_list,l_compute_node_id

def compute_network(url,sub_url,compute_node_list,fp = "", info_list = [1,0,0,0], api_index = True):
    com_switch_res,com_switch_id = create_switch(url,sub_url,"compute",fp = fp, info_list  = info_list, api_index = api_index)
    com_nic_list = []
    for com_id in compute_node_list:
        com_nic_res, com_nic_id = add_interface(url,sub_url,com_id,fp = fp, info_list  = info_list, api_index = api_index)
        connect_switch_res = connect_switch(url,com_switch_id,com_nic_id,fp = fp, info_list  = info_list, api_index = api_index)
        com_nic_list.append(com_nic_id)
    return connect_switch_res,com_nic_list


def build_cluster(fp = "", info_list = [1,0,0,0], api_index = True):
    #configuration_info = json_input("./trial_configfile.json")
    zone_list = configuration_info["zone"]
    zone_list = zone_list.split(',')
    nfs_zone = []
    if configuration_info["NFS"] == "True":
        
        nfs_zone = configuration_info["NFS zone"].split(",")
    head_zone = configuration_info["place of head node"]
    url_list = []
    for i in zone_list:
        url_list.append("https://secure.sakura.ad.jp/cloud/zone/"+ i +"/api/cloud/1.1")
    head_url = "https://secure.sakura.ad.jp/cloud/zone/"+ head_zone +"/api/cloud/1.1"
    url_list.append(head_url)
    sub_url = ["/server","/disk","/switch","/interface","/bridge","/tag",'/appliance']
    compute_id_zone = {}

    if len(zone_list) == 1:
        head_id_list,l_compute_node_id = build_head_zone(url_list[0],sub_url,zone_list[0],fp = fp, info_list  = info_list, api_index = api_index)
        compute_node_id_list = l_compute_node_id
        compute_id_zone[zone_list[0]] = compute_node_id_list
        nfs_bool = zone_list[0] in nfs_zone
        if nfs_bool == True:
            nfs_res,nfs_id = setting_nfs(url_list[0],sub_url,zone_list[0],head_id_list[2],fp = fp, info_list  = info_list, api_index = api_index)
    elif len(zone_list) >= 2 :
        #head_url = "https://secure.sakura.ad.jp/cloud/zone/"+ head_zone +"/api/cloud/1.1"
        bridge_res,bridge_id = create_bridge(url_list[-1],sub_url,fp = fp, info_list  = info_list, api_index = api_index)
        compute_node_id_list = []
        
        i = 0
        for zone in zone_list:
            #url = "https://secure.sakura.ad.jp/cloud/zone/"+ zone[i] +"/api/cloud/1.1"
            if url_list[i] == url_list[-1]:
                head_id_list,l_compute_node_id = build_head_zone(url_list[i],sub_url,zone_list[i],fp = fp, info_list  = info_list, api_index = api_index)
                #connect bridge to switch
                bridge_switch_res = connect_bridge_switch(url_list[i],head_id_list[2],bridge_id,fp = fp, info_list  = info_list, api_index = api_index)
                compute_node_id_list.extend(l_compute_node_id)
                compute_id_zone[zone] = l_compute_node_id
                nfs_bool = zone_list[i] in nfs_zone
                if nfs_bool == True:
                    nfs_res,nfs_id = setting_nfs(url_list[i],sub_url,zone_list[i],head_id_list[2],fp = fp, info_list  = info_list, api_index = api_index)

            elif url_list[i] != url_list[-1]:
                compute_switch_response,compute_switch_id = create_switch(url_list[i],sub_url,fp = fp, info_list  = info_list, api_index = api_index)
                bridge_switch_res = connect_bridge_switch(url_list[i],compute_switch_id,bridge_id,fp = fp, info_list  = info_list, api_index = api_index)
                number_of_compute_node = int(configuration_info["the number of compute node in " + zone_list[i]])
                compute_server_response,l_compute_node_id = build_compute_node(url_list[i],sub_url,compute_switch_id,number_of_compute_node,zone_list[i],fp = fp, info_list  = info_list, api_index = api_index)
                if configuration_info["compute network"] == "True":
                    com_network,com_nic_list = compute_network(url_list[i],sub_url,l_compute_node_id,fp = fp, info_list  = info_list, api_index = api_index)
                compute_node_id_list.extend(l_compute_node_id)
                compute_id_zone[zone] = l_compute_node_id
                nfs_bool = zone_list[i] in nfs_zone
                if nfs_bool == True:
                    nfs_res,nfs_id = setting_nfs(url_list[i],sub_url,zone_list[i],compute_switch_id,fp = fp, info_list  = info_list, api_index = api_index)
            i += 1
    cluster_info_res = cluster_info(url_list,sub_url,head_id_list,compute_node_id_list,compute_id_zone,fp = fp, info_list  = info_list, api_index = api_index)
    return auth_res

def cluster_info(url_list,sub_url,head_id_list,compute_node_id_list,compute_id_zone,fp = "", info_list = [1,0,0,0], api_index = True):
    _ = printout("###Cluster Infomation###" , info_list = info_list, fp = fp)
    cls_info = {}
    cls_info["config name"] = configuration_info["config name"]
    _ = printout("config name:" + cls_info["config name"], info_list = info_list, fp = fp)
    cluster_id = cluster_id_def(url_list[-1],sub_url,fp = fp, info_list = info_list , api_index = api_index)
    #cluster_id = "cluster ID:" + str(cluster_id)
    cls_info["cluster ID"] = str(cluster_id)
    _ = printout("cluster ID:" + cls_info["cluster ID"], info_list = info_list, fp = fp)
    cls_info["head node ID"] = head_id_list[0]
    _ = printout("head node ID:" + cls_info["head node ID"],info_list = info_list, fp = fp)
    _ = printout("compute node ID:" ,info_list = info_list, fp = fp)
    for k in compute_id_zone.keys():
        id_list = ','.join(compute_id_zone[k])
        _ = printout( k + ":" + id_list,info_list = info_list, fp = fp)
    zone_list = configuration_info["zone"]
    zone_list = zone_list.split(',')
    if len(zone_list) == 1:
        #number_of_compute_node = "number of compute node:" + str(configuration_info["the number of compute node in " + zone[0]])
        cls_info["number of compute node"] = str(configuration_info["the number of compute node in " + zone_list[0]])
        _ = printout("number of compute node:" + cls_info["number of compute node"], info_list = info_list, fp = fp)
    elif len(zone_list) >= 2 :
        number_of_compute_node = 0
        for i in zone_list:
            number_of_compute_node += int(configuration_info["the number of compute node in " + i])
        #number_of_compute_node = "number of compute node:" + str(number_of_compute_node)
        cls_info["number of compute node"] = str(number_of_compute_node)
        _ = printout("number of compute node:" + cls_info["number of compute node"], info_list = info_list, fp = fp)
    #compute_node_id_lists = ",".join(compute_node_id_list)
    #compute_node_id_lists = "compute ID list:" + compute_node_id_list
    #cls_info["compute ID list"] = compute_node_id_lists
    dt_now = datetime.datetime.now()
    dt_ymd = dt_now.strftime("%Y_%m_%d")
    cls_info["Date modified"] = dt_ymd
    _ = printout("Date modified:" + cls_info["Date modified"], info_list = info_list, fp = fp)
    url_tag = sub_url[0] + "/" + head_id_list[0] + sub_url[5]
    url_des = sub_url[0] + "/" + head_id_list[0]
    #param = {"Server":{"Tags":[compute_node_id_lists]}}
    cls_info_str = json.dumps(cls_info)
    cls_info_list = [str(k) + " : " + str(v) for k,v in cls_info.items()]
    cluster_id = cls_info_list[1]
    date_modified = cls_info_list[-1]
    #param = {"Tags":cls_info_list}
    desc_param = {"Server":{"Description":cls_info_str}}
    param = {"Tags":[cluster_id,date_modified]}
    if (api_index == True):
        while(True):
            cluster_tags_res = put(url_list[-1]+url_tag,auth_res,param)
            cluster_info_res = put(url_list[-1]+url_des,auth_res,desc_param)
            if ("Success" in cluster_tags_res.keys() and "Success" in cluster_info_res.keys()):
                if (cluster_tags_res["Success"] == True and cluster_info_res["Success"] == True):
                    for zone in zone_list:
                        compute_list = compute_id_zone[zone]
                        for url in url_list:
                            if zone in url:
                                for com_id in compute_list:
                                    url_ctag = sub_url[0] + "/" + com_id + sub_url[5]
                                    ctag_param = {"Tags":[cluster_id]}
                                    compute_tag_res = put(url+url_ctag,auth_res,ctag_param)
                                    if ("Success" in compute_tag_res.keys()):
                                        if (compute_tag_res["Success"] == True):
                                            break
                                        else:
                                            _ = printout("Error:",fp = fp, info_list = info_list)
                                            rf = response_output("Error_compute_tag_info",compute_tag_res)
                                            while(True):
                                                conf = printout("Try again??(yes/no):",info_type = 2, info_list = [1,0,0,0], fp = '')
                                                if conf == "yes":
                                                    break
                                                elif conf == "no":
                                                    _ = printout("Stop processing.", info_list = info_list,fp = fp)
                                                    sys.exit()
                                                else:
                                                    _ = printout("Please answer yes or no.",info_list = info_list,fp = fp)
                                    elif ("is_fatal" in compute_tag_res.keys()):
                                        _ = printout("Error:" + compute_tag_res["error_msg"],fp = fp, info_list = info_list)
                                        rf = response_output("Error_compute_tag",compute_tag_res)
                                        while(True):
                                            conf = printout("Try again??(yes/no):",info_type = 2, info_list = [1,0,0,0], fp = '')
                                            if conf == "yes":
                                                break
                                            elif conf == "no":
                                                _ = printout("Stop processing.", info_list = info_list,fp = fp)
                                                sys.exit()
                                            else:
                                                _ = printout("Please answer yes or no.",info_list = info_list,fp = fp)

                                    rf = response_output("compute_tag_info",compute_tag_res)
                    break

                elif (cluster_tags_res["Success"] == True and cluster_info_res["Success"] == False):
                    _ = printout("Error:can not add Description",fp = fp, info_list = info_list)
                    rf = response_output("cluster_tags",cluster_tags_res)
                    rf = response_output("Error_cluster_info",cluster_info_res)
                    while(True):
                            conf = printout("Try again??(yes/no):",info_type = 2, info_list = [1,0,0,0], fp = '')
                            if conf == "yes":
                                break
                            elif conf == "no":
                                _ = printout("Stop processing.", info_list = info_list,fp = fp)
                                sys.exit()
                            else:
                                _ = printout("Please answer yes or no.",info_list = info_list,fp = fp)
                elif (cluster_tags_res["Success"] == False and cluster_info_res["Success"] == True):
                    _ = printout("Error:can not add Tags",fp = fp, info_list = info_list)
                    rf = response_output("Error_cluster_tags",cluster_tags_res)
                    while(True):
                            conf = printout("Try again??(yes/no):",info_type = 2, info_list = [1,0,0,0], fp = '')
                            if conf == "yes":
                                break
                            elif conf == "no":
                                _ = printout("Stop processing.", info_list = info_list,fp = fp)
                                sys.exit()
                            else:
                                _ = printout("Please answer yes or no.",info_list = info_list,fp = fp)
                elif (cluster_tags_res["Success"] == False and cluster_info_res["Success"] == False):
                    _ = printout("Error:can not add Tags",fp = fp, info_list = info_list)
                    _ = printout("Error:can not add Description",fp = fp, info_list = info_list)
                    rf = response_output("Error_cluster_tags",cluster_tags_res)
                    rf = response_output("Error_cluster_info",cluster_info_res)
                    while(True):
                            conf = printout("Try again??(yes/no):",info_type = 2, info_list = [1,0,0,0], fp = '')
                            if conf == "yes":
                                break
                            elif conf == "no":
                                _ = printout("Stop processing.", info_list = info_list,fp = fp)
                                sys.exit()
                            else:
                                _ = printout("Please answer yes or no.",info_list = info_list,fp = fp)

            elif ("is_fatal" in cluster_tags_res.keys() or "is_fatal" in cluster_info_res.keys()):
                if ("is_fatal" in cluster_tags_res.keys()):
                    _ = printout("Error:" + cluster_tags_res["error_msg"],fp = fp, info_list = info_list)
                    rf = response_output("Error_cluster_tags",cluster_tags_res)
                    if ("is_fatal" in cluster_info_res.keys()):
                        _ = printout("Error:" + cluster_info_res["error_msg"],fp = fp, info_list = info_list)
                        rf = response_output("Error_cluster_info",cluster_info_res)
                    rf = response_output("cluster_info",cluster_info_res)
                    while(True):
                            conf = printout("Try again??(yes/no):",info_type = 2, info_list = [1,0,0,0], fp = '')
                            if conf == "yes":
                                break
                            elif conf == "no":
                                _ = printout("Stop processing.", info_list = info_list,fp = fp)
                                sys.exit()
                            else:
                                _ = printout("Please answer yes or no.",info_list = info_list,fp = fp)

                else:
                    _ = printout("Error:" + cluster_info_res["error_msg"],fp = fp, info_list = info_list)
                    rf = response_output("Error_cluster_info",cluster_info_res)
                    rf = response_output("cluster_tags",cluster_tags_res)
                    while(True):
                            conf = printout("Try again??(yes/no):",info_type = 2, info_list = [1,0,0,0], fp = '')
                            if conf == "yes":
                                break
                            elif conf == "no":
                                _ = printout("Stop processing.", info_list = info_list,fp = fp)
                                sys.exit()
                            else:
                                _ = printout("Please answer yes or no.",info_list = info_list,fp = fp)
    else:
        cluster_tags_res = "API is not used."
        cluster_info_res = "API is not used."
    
    
    rf = response_output("cluster_tags",cluster_tags_res)
    rf = response_output("clister_info",cluster_info_res)
    return cluster_info_res

dt_now = datetime.datetime.now()
dt_now = dt_now.strftime("%Y_%m_%d_%H%M%S")
f = open(path + "/res/res_" + dt_now + ".txt", 'w')
info_list = [1,0,0,1]


#auth_res = build_cluster(fp = f, info_list  = info_list, api_index = True)
main(fp= f , info_list = info_list , api_index = True)
#server_power_res = starting_server(url)
#main(fp = "", info_list = [1,0,0,0],api_index=True)
f.close()

