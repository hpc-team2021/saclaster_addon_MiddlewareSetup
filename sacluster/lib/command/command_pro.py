
import os
from re import A

from sacluster.lib.addon.setupIP.setupIpEth0 import setupIpEth0
os.chdir(os.path.dirname(os.path.abspath(__file__)))
common_path = os.path.abspath("../..")

from os.path import expanduser
home_path = expanduser("~") + "/sacluster"
os.makedirs(home_path, exist_ok = True)

import sys
import argparse
import os
sys.path.append(common_path + "/lib/auth")
import datetime
sys.path.append(common_path + "/lib/others")
from info_print import printout
sys.path.append(common_path + "/lib/cls/construction")
from build_main import build_main
sys.path.append(common_path + "/lib/cls/start")
from start_main import start_main
sys.path.append(common_path + "/lib/cls/stop")
from stop_main import stop_main
sys.path.append(common_path + "/lib/cls/modify")
from modify_main import modify_main
sys.path.append(common_path + "/lib/cls/delete")
from delete_main import delete_main
sys.path.append(common_path + "/lib/cls/config")
from def_config_main import def_config_main
sys.path.append(common_path + "/lib/cls/ps")
from ps_main import ps_main

sys.path.append(common_path + "/lib/addon")
from addon_main import addon_main, addon_start

sys.path.append(common_path + "/lib/addon/setupIP")
from setupIpEth0 import setupIpEth0



import logging

dt_now = datetime.datetime.now()
os.makedirs(home_path + "/log", exist_ok = True)
os.makedirs(home_path + "/res", exist_ok = True)
os.makedirs(home_path + "/setting", exist_ok = True)
os.makedirs(home_path + "/config", exist_ok = True)

log_filename = home_path + "/log/" + dt_now.strftime('%Y_%m_%d_%H_%M_%S.log')

logger = logging.getLogger("sacluster")
logger.setLevel(logging.DEBUG)
file_handler = logging.FileHandler(log_filename)
file_handler.setLevel(logging.WARNING)
handler_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(handler_format)
logger.addHandler(file_handler)


def prior_build(args):

    if(args.verbose == True):
        logger.debug('Change log level to debag')
        file_handler.setLevel(logging.DEBUG)
        logger.addHandler(file_handler)
        
    if(args.parents == True and args.dir == None):
        logger.error('--parents option [-p] requires --input option [-d]')
        print("error: --parents option [-p] requires --input option [-d] ")
        sys.exit()
        
    if(args.output == True):
        logger.debug('Create a file for standard output')
        dt_now = datetime.datetime.now()
        fp_filename = dt_now.strftime('%Y_%m_%d_%H_%M_%S.txt')
        #os.
        f = open(home_path + "/res/" + fp_filename, "w")
        info_list = [1,0,0,1]
    else:
        f = ""
        info_list = [1,0,0,0]
        
    if(args.input == None):
        args.input = ""
        logger.debug('Set config input path to None')
    else:
        logger.debug('Set config input path to ' + args.input)
        
    if(args.dir == None):
        args.dir = ""
        logger.debug('Set config output path to None')
    else:
        logger.debug('Set config output path to ' + args.dir)
        
    cls_bil = build_main(args.input, args.dir, args.parents, args.dryrun, f, info_list, args.auto, int(args.thread))
        
    if(args.output == True):
        printout("Processes for building the cluster were completed", info_type = 0, info_list = [1,0,0,1], fp = f)
        logger.debug('Close a file for standard output')
        f.close()
    else:
        printout("All processes were completed", info_type = 0, info_list = [1,0,0,0], fp = "")

    if (args.middle == True):
        setupIpEth0 (cls_bil)

        start_main(args.dryrun, f, info_list, int(args.thread))
        #eth1のIP設定の関数
        #ミドルウェアセットアップ
        addon_main()
    

def prior_start(args):
 
    if(args.verbose == True):
        logger.debug('Change log level to debag')
        file_handler.setLevel(logging.DEBUG)
        logger.addHandler(file_handler)

    if(args.output == True):
        logger.debug('Create a file for standard output')
        dt_now = datetime.datetime.now()
        fp_filename = dt_now.strftime('%Y_%m_%d_%H_%M_%S.txt')
        #os.
        f = open(home_path + "/res/" + fp_filename, "w")
        info_list = [1,0,0,1]
    else:
        f = ""
        info_list = [1,0,0,0]

    start_main(args.dryrun, f, info_list, int(args.thread))

    if(args.output == True):
        printout("Processes for building the cluster were completed", info_type = 0, info_list = [1,0,0,1], fp = f)
        logger.debug('Close a file for standard output')
        f.close()
    else:
        printout("All processes were completed", info_type = 0, info_list = [1,0,0,0], fp = "")
    
    if (args.middle == True):
        addon_start()  


def prior_stop(args):
    if(args.verbose == True):
        logger.debug('Change log level to debag')
        file_handler.setLevel(logging.DEBUG)
        logger.addHandler(file_handler)

    if(args.output == True):
        logger.debug('Create a file for standard output')
        dt_now = datetime.datetime.now()
        fp_filename = dt_now.strftime('%Y_%m_%d_%H_%M_%S.txt')
        #os.
        f = open(home_path + "/res/" + fp_filename, "w")
        info_list = [1,0,0,1]
    else:
        f = ""
        info_list = [1,0,0,0]

    stop_main(args.dryrun, f, info_list, int(args.thread))

    if(args.output == True):
        printout("Processes for building the cluster were completed", info_type = 0, info_list = [1,0,0,1], fp = f)
        logger.debug('Close a file for standard output')
        f.close()
    else:
        printout("All processes were completed", info_type = 0, info_list = [1,0,0,0], fp = "")

def prior_modify(args):
    if(args.verbose == True):
        logger.debug('Change log level to debag')
        file_handler.setLevel(logging.DEBUG)
        logger.addHandler(file_handler)

    if(args.output == True):
        logger.debug('Create a file for standard output')
        dt_now = datetime.datetime.now()
        fp_filename = dt_now.strftime('%Y_%m_%d_%H_%M_%S.txt')
        #os.
        f = open(home_path + "/res/" + fp_filename, "w")
        info_list = [1,0,0,1]
    else:
        f = ""
        info_list = [1,0,0,0]

    modify_main(args.dryrun, f, info_list, int(args.thread))

    if(args.output == True):
        printout("Processes for building the cluster were completed", info_type = 0, info_list = [1,0,0,1], fp = f)
        logger.debug('Close a file for standard output')
        f.close()
    else:
        printout("All processes were completed", info_type = 0, info_list = [1,0,0,0], fp = "")


def prior_delete(args):
    if(args.verbose == True):
        logger.debug('Change log level to debag')
        file_handler.setLevel(logging.DEBUG)
        logger.addHandler(file_handler)

    if(args.output == True):
        logger.debug('Create a file for standard output')
        dt_now = datetime.datetime.now()
        fp_filename = dt_now.strftime('%Y_%m_%d_%H_%M_%S.txt')
        #os.
        f = open(home_path + "/res/" + fp_filename, "w")
        info_list = [1,0,0,1]
    else:
        f = ""
        info_list = [1,0,0,0]

    delete_main(args.dryrun, f, info_list, int(args.thread))

    if(args.output == True):
        printout("Processes for building the cluster were completed", info_type = 0, info_list = [1,0,0,1], fp = f)
        logger.debug('Close a file for standard output')
        f.close()
    else:
        printout("All processes were completed", info_type = 0, info_list = [1,0,0,0], fp = "")

def prior_config(args):

    if(args.verbose == True):
        logger.debug('Change log level to debag')
        file_handler.setLevel(logging.DEBUG)
        logger.addHandler(file_handler)

    if(args.parents == True and args.dir == None):
        logger.error('--parents option [-p] requires --input option [-d]')
        print("error: --parents option [-p] requires --input option [-d] ")
        sys.exit()

    if(args.output == True):
        logger.debug('Create a file for standard output')
        dt_now = datetime.datetime.now()
        fp_filename = dt_now.strftime('%Y_%m_%d_%H_%M_%S.txt')
        #os.
        f = open(home_path + "/res/" + fp_filename, "w")
        info_list = [1,0,0,1]
    else:
        f = ""
        info_list = [1,0,0,0]

    if(args.dir == None):
        args.dir = ""
        logger.debug('Set config output path to None')
    else:
        logger.debug('Set config output path to ' + args.dir)

    def_config_main(args.dir, args.parents, args.dryrun, f, info_list)

    if(args.output == True):
        printout("Processes for building the cluster were completed", info_type = 0, info_list = [1,0,0,1], fp = f)
        logger.debug('Close a file for standard output')
        f.close()
    else:
        printout("All processes were completed", info_type = 0, info_list = [1,0,0,0], fp = "")

def prior_ps(args):
    if(args.verbose == True):
        logger.debug('Change log level to debag')
        file_handler.setLevel(logging.DEBUG)
        logger.addHandler(file_handler)

    if(args.output == True):
        logger.debug('Create a file for standard output')
        dt_now = datetime.datetime.now()
        fp_filename = dt_now.strftime('%Y_%m_%d_%H_%M_%S.txt')
        #os.
        f = open(home_path + "/res/" + fp_filename, "w")
        info_list = [1,0,0,1]
    else:
        f = ""
        info_list = [1,0,0,0]

    ps_main(args.dryrun, f, info_list)

    if(args.output == True):
        printout("Processes for building the cluster were completed", info_type = 0, info_list = [1,0,0,1], fp = f)
        logger.debug('Close a file for standard output')
        f.close()


def command_main():

    logger.debug('Input command')
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="sub_command", help="sacluster: this system is to build and modify the cluster on the sakura cloud")
    subparsers.required = True

    build_parser = subparsers.add_parser("build", help = "sub-command <build> is used to build cluster")
    start_parser = subparsers.add_parser("start", help = "sub-command <start> is used to start cluster")
    stop_parser = subparsers.add_parser("stop", help = "sub-command <stop> is used to start cluster")
    modify_parser = subparsers.add_parser("modify", help = "sub-command <modify> is used to start cluster")
    delete_parser = subparsers.add_parser("delete", help = "sub-command <delete> is used to delete cluster")
    config_parser = subparsers.add_parser("config", help = "sub-command <config> is used to define a config file")
    ps_parser = subparsers.add_parser("ps", help = "sub-command <ps> is used to confirm clusters on the sakura cloud")


    build_group = build_parser.add_mutually_exclusive_group()
    build_parser.add_argument("-a", "--auto", action='store_true', help = "option to start automatically")
    build_group.add_argument("-i", "--input", help = "option to specify an input config path")
    build_group.add_argument("-d", "--dir", help = "option to specify an output config path")
    build_parser.add_argument("-p", "--parents", action='store_true', help = "option to generate output config directories")
    build_parser.add_argument("--dryrun", action='store_false', help = "option to run in trial mode")
    build_parser.add_argument("-o", "--output", action='store_true', help = "option to provide standard file output in addition to the standard console output")
    build_parser.add_argument("-v", "--verbose", action='store_true', help = "option to output detailed log")
    build_parser.add_argument("-t", "--thread", type=int, default = 1, help = "the number of max threads")
    build_parser.add_argument("-m", "--middle", action='store_true', help = "middle")
    build_parser.set_defaults(handler = prior_build)

    start_parser.add_argument("--dryrun", action='store_false', help = "option to run in trial mode")
    start_parser.add_argument("-o", "--output", action='store_true', help = "option to provide standard file output in addition to the standard console output")
    start_parser.add_argument("-v", "--verbose", action='store_true', help = "option to output detailed log")
    start_parser.add_argument("-t", "--thread", type=int, default = 1, help = "the number of max threads")
    start_parser.add_argument("-m", "--middle", action='store_true', help = "middle setup")
    start_parser.set_defaults(handler = prior_start)

    stop_parser.add_argument("--dryrun", action='store_false', help = "option to run in trial mode")
    stop_parser.add_argument("-o", "--output", action='store_true', help = "option to provide standard file output in addition to the standard console output")
    stop_parser.add_argument("-v", "--verbose", action='store_true', help = "option to output detailed log")
    stop_parser.add_argument("-t", "--thread", type=int, default = 1, help = "the number of max threads")
    stop_parser.set_defaults(handler = prior_stop)

    modify_parser.add_argument("--dryrun", action='store_false', help = "option to run in trial mode")
    modify_parser.add_argument("-o", "--output", action='store_true', help = "option to provide standard file output in addition to the standard console output")
    modify_parser.add_argument("-v", "--verbose", action='store_true', help = "option to output detailed log")
    modify_parser.add_argument("-t", "--thread", type=int, default = 1, help = "the number of max threads")
    modify_parser.set_defaults(handler = prior_modify)

    delete_parser.add_argument("--dryrun", action='store_false', help = "option to run in trial mode")
    delete_parser.add_argument("-o", "--output", action='store_true', help = "option to provide standard file output in addition to the standard console output")
    delete_parser.add_argument("-v", "--verbose", action='store_true', help = "option to output detailed log")
    delete_parser.add_argument("-t", "--thread", type=int, default = 1, help = "the number of max threads")
    delete_parser.set_defaults(handler = prior_delete)

    config_parser.add_argument("--dryrun", action='store_false', help = "option to run in trial mode")
    config_parser.add_argument("-d", "--dir", help = "option to specify an output config path")
    config_parser.add_argument("-p", "--parents", action='store_true', help = "option to generate output config directories")
    config_parser.add_argument("-o", "--output", action='store_true', help = "option to provide standard file output in addition to the standard console output")
    config_parser.add_argument("-v", "--verbose", action='store_true', help = "option to output detailed log")
    config_parser.set_defaults(handler = prior_config)

    ps_parser.add_argument("--dryrun", action='store_false', help = "option to run in trial mode")
    ps_parser.add_argument("-o", "--output", action='store_true', help = "option to provide standard file output in addition to the standard console output")
    ps_parser.add_argument("-v", "--verbose", action='store_true', help = "option to output detailed log")
    ps_parser.set_defaults(handler = prior_ps)

    args = parser.parse_args()
    if hasattr(args, 'handler'):
        args.handler(args)

if __name__ == "__main__":
    command_main()
