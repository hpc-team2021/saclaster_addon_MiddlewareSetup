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
common_path = os.path.abspath("../..")
sys.path.append(common_path + "/lib/others")

from API_method import get, post, put, delete
from info_print import printout

sys.path.append(common_path + "/lib/addon/setupIP")
from assignIp import assignIpAddress

def addon_main():
    print("アドオンの関数")

def setIp (cls_bil):
    print ("Set Private IP Address")
    assignIpAddress (cls_bil)

def addon_start():
    print("ミドルウェアの起動")