# IP Address Setting

from posixpath import commonpath
import sys
import json
import os
import datetime
import ipaddress
import logging
from tqdm import tqdm
from concurrent import futures
import time
import pprint

logger = logging.getLogger("sacluster").getChild(os.path.basename(__file__))

os.chdir(os.path.dirname(os.path.abspath(__file__)))
common_path = os.path.abspath ("../../..")
sys.path.append(common_path + "/lib/others")

from API_method import get, post, put, delete
from info_print import printout

def assign_ipaddress (cls_bil):
    assign_ipaddress_head (cls_bil)
    n = cls_bil.compute_num
    for i in range (n):
        if i < 9:
            compute_node_name = "computenode00"+str(i + 1)
        elif 9 <= i and i < 99:
            compute_node_name = "computenode0"+str(i + 1)
        elif 99 <= i:
            compute_node_name = "computenode"+str(i + 1)
        
        print ("Setting IP Address to disk for " + compute_node_name)
        disk_id = cls_bil.all_id_dict["clusterparams"]["server"][cls_bil.head_zone]["compute"][i]["disk"][0]["id"]
        wait_disk (cls_bil, disk_id)
        update_disk (cls_bil, i, disk_id)

def assign_ipaddress_head (cls_bil):
    zone = cls_bil.head_zone
    nic_id = cls_bil.all_id_dict["clusterparams"]["server"][zone]["head"]["nic"]["front"]["id"]

    param = {
            "Interface":{
                "UserIpAddress":"192.168.1.254"
        }
    }

    update_nic_response = put(cls_bil.url_list[zone] + cls_bil.sub_url[3] + '/' + nic_id, cls_bil.auth_res, param)
    

def wait_disk (cls_bil, disk_id):
    #print ('Disk ID:', disk_id)
    #print (type(disk_id))
    disk_state = 'uploading'
    index = 0
    flag = 0
    zone = cls_bil.head_zone
    # ディスク状態が利用可能になるまで待ち続けるコード
    get_cluster_disk_info = get(cls_bil.url_list[zone] + cls_bil.sub_url[1], cls_bil.auth_res)
    for i in range(len(get_cluster_disk_info['Disks'])):
            str_i = str(i)
            k = get_cluster_disk_info['Disks'][i]
            #print(k['ID'])
            #print(type(k['ID']))
            if k['ID'] == str (disk_id):
                print ('Target disk exists in this zone')
                disk_state = k['Availability']
                index = i
                flag = 1
                break
    if flag == 0:
        print ('No matching to the taget disk in this zone')
        print ('Setting IP address is failed')
        sys.exit ()
    while True:
        get_cluster_disk_info = get(cls_bil.url_list[zone] + cls_bil.sub_url[1], cls_bil.auth_res)
        disk_state = get_cluster_disk_info['Disks'][index]['Availability']
        if disk_state == 'available':
            print("it's OK! Available!")
            break
        print('disk state is ' + disk_state + ' ... Please wait...')
        time.sleep(10)

    print('ディスクの追加が完了するまで終了')

def update_disk (cls_bil, ipaddress_sequence, disk_id):
    ipaddress = "192.168.1." + str (ipaddress_sequence + 1)
    param = {
        "UserIPAddress": ipaddress,
        "UserSubnet": {
            "DefaultRoute": '192.168.100.254',
            "NetworkMaskLen": 24
      }
    }

    zone = cls_bil.head_zone
    put_url = cls_bil.url_list[zone] + cls_bil.sub_url[1] + '/' + str (disk_id) + '/config'
    disk_res = put (put_url, cls_bil.auth_res, param)
    check, msg = cls_bil.res_check (disk_res, "put")
    return 0