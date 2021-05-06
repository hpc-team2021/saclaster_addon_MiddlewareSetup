#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jul  1 01:36:42 2020

@author: tsukiyamashou
"""

import os
os.chdir(os.path.dirname(os.path.abspath(__file__)))
common_path = os.path.abspath("../..")

import sys
import argparse
import os
sys.path.append(common_path + "/lib/auth")
import datetime
sys.path.append(common_path + "/lib/others")
from info_print import printout
sys.path.append(common_path + "/lib/cls/construction")
from build_main import build_main
import logging


dt_now = datetime.datetime.now()
log_filename = common_path + "/log/" + dt_now.strftime('%Y_%m_%d_%H_%M_%S.log')

logger = logging.getLogger("sacluster")
logger.setLevel(logging.DEBUG)
file_handler = logging.FileHandler(log_filename)
file_handler.setLevel(logging.WARNING)
handler_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(handler_format)
logger.addHandler(file_handler)

##
def prior_build(opp_auto, opp_input, opp_dir, opp_parents, opp_dryrun, opp_output, opp_verbose):
    
    # verbose:option to output detailed log
    if(opp_verbose == True):
        logger.debug('Change log level to debag')
        file_handler.setLevel(logging.DEBUG)
        logger.addHandler(file_handler)
    
    # parents:option to generate output config directories, dir:option to specify an output config path
    if(opp_parents == True and opp_dir == None):
        logger.error('--parents option [-p] requires --input option [-d]')
        print("error: --parents option [-p] requires --input option [-d] ")
        sys.exit()
        
    # output:option to provide standard file output in addition to the standard console output
    if(opp_output == True):
        logger.debug('Create a file for standard output')
        dt_now = datetime.datetime.now()
        fp_filename = dt_now.strftime('%Y_%m_%d_%H_%M_%S.txt')
        f = open(common_path + "/res/" + fp_filename, "w")
        info_list = [1,0,0,1]
    else:
        f = ""
        info_list = [1,0,0,0]
        
    # input:option to specify an input config path
    if(opp_input == None):
        opp_input = ""
        logger.debug('Set config input path to None')
    else:
        logger.debug('Set config input path to ' + opp_input)
        
    # dir:option to specify an output config path
    if(opp_dir == None):
        opp_dir = ""
        logger.debug('Set config output path to None')
    else:
        logger.debug('Set config output path to ' + opp_dir)

    #   
    build_main(opp_input, opp_dir, opp_parents, opp_dryrun, f, info_list, opp_auto)
        
    # output:option to provide standard file output in addition to the standard console output
    if(opp_output == True):
        printout("Processes for building the cluster were completed", info_type = 0, info_list = [1,0,0,1], fp = f)
        logger.debug('Close a file for standard output')
        f.close()
    else:
        printout("All processes were completed", info_type = 0, info_list = [1,0,0,0], fp = "")
        


def command_main():
    
    logger.debug('Input command')
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="sub_command", help="sacluster: this system is to build and modify the cluster on the sakura cloud")
    subparsers.required = True
    
    build_parser = subparsers.add_parser("build", help = "sub-command <build> is used to build cluster")
    build_group = build_parser.add_mutually_exclusive_group()
    
    build_parser.add_argument("-a", "--auto", action='store_true', help = "option to start automatically")
    build_group.add_argument("-i", "--input", help = "option to specify an input config path")
    build_group.add_argument("-d", "--dir", help = "option to specify an output config path")
    build_parser.add_argument("-p", "--parents", action='store_true', help = "option to generate output config directories")
    build_parser.add_argument("--dryrun", action='store_false', help = "option to run in trial mode")
    build_parser.add_argument("-o", "--output", action='store_true', help = "option to provide standard file output in addition to the standard console output")
    build_parser.add_argument("-v", "--verbose", action='store_true', help = "option to output detailed log")
    build_parser.set_defaults(fn=prior_build)
    
    args = parser.parse_args()
    if args.fn == prior_build:
        logger.debug('Execute the construction function')
        prior_build(args.auto, args.input, args.dir, args.parents, args.dryrun, args.output, args.verbose)
    
command_main()



