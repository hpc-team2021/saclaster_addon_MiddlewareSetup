def get_IP_list(cls_bil, ext_info):
    try:
        clusterID = cls_bil.cluster_id.split(": ")[1]
    except:
        clusterID = cls_bil["Temporary"]["clusterID"]
    base    = ext_info["IP_addr"]["base"]
    front   = ext_info["IP_addr"]["front"]
    back    = ext_info["IP_addr"]["back"]
    ip_zone = ext_info["IP_addr"]["zone_seg"]


    zone_list = list(cls_bil.all_id_dict["clusterparams"]["server"].keys())
    IP_front_list   = []
    IP_back_list    = []
    for zone in zone_list:
        for i in list(cls_bil.all_id_dict["clusterparams"]["server"][zone]["compute"].keys()):
            IP_front_list.append(str(base) + "." + str(front) + ".{}.{}".format(ip_zone[zone], i + 1))
            IP_back_list.append (str(base) + "." + str(back) + ".{}.{}".format(ip_zone[zone], i + 1))

    IP_list = {"front":IP_front_list, "back":IP_back_list}
    return IP_list
