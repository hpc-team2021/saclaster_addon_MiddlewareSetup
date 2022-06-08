def get_IP_list(cls_bil, ext_info, cls_mid):
    clusterID           = cls_bil.cluster_id.split(": ")[1]
    base    = ext_info["IP_addr"]["base"]
    front   = ext_info["IP_addr"]["front"]
    back    = ext_info["IP_addr"]["back"]
    ip_zone = ext_info["IP_addr"]["zone_seg"]


    zone_list = list(cls_bil.all_id_dict["clusterparams"]["server"].keys())
    IP_front_list   = []
    IP_back_list    = []
    for zone in zone_list:
        for i in list(cls_mid.cluster_info["clusterparams"]["server"][zone]["compute"].keys()):
            IP_front_list.append("192.168.{}.{}".format(ip_zone[zone], i + 1))
            IP_back_list.append ("192.169.{}.{}".format(ip_zone[zone], i + 1))

    IP_list = {"front":IP_front_list, "back":IP_back_list}
    return IP_list