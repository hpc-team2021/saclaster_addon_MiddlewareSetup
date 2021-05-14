import os
import datetime
import json

def response_output(res_filename,response):
    dt_now = datetime.datetime.now()
    dt_ymd = dt_now.strftime("%Y_%m_%d")
    dt_now = dt_now.strftime("%Y_%m_%d_%H%M%S")
    os.makedirs("./response/" + dt_ymd, exist_ok=True)
    rf = open("./response/" + dt_ymd + "/" + dt_now + "_" + res_filename + ".txt", 'w', encoding = 'utf-8')
    json.dump(response, rf ,indent = 4,ensure_ascii=False)
    rf.close()

    return rf