#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Nov 12 11:50:03 2020

@author: tsukiyamashou
"""
import requests
import json

def printout(comment, info_type = 0, info_list = [1,0,0,1], fp = "", msg_token = ""):
    """

    Parameters
    ----------
    comment : TYPE
        DESCRIPTION. 出力コメント
    info_type : TYPE, optional
        DESCRIPTION. 読み込み変数なし:0、読み込み変数あり（通常時）:1、読み込み変数あり(認証時):0(The default is 0).
    info_list : TYPE, optional
        DESCRIPTION. [標準出力,slack通知、Line通知、ファイル出力]、機能あり:1、機能なし:0(The default is [1,0,0,1]).
    fp : TYPE, optional
        DESCRIPTION. ファイル出力用ファイルオブジェクト (The default is "").
        
    Returns
    -------
    val : TYPE
        DESCRIPTION.読み込み変数
    out_list : TYPE
        DESCRIPTION.ファイル出力用list

    """
    #読み込み変数がない場合
    if(info_type == 0):
        #コンソール標準出力
        if(info_list[0] == 1):
            print(comment)
        
        #slackの通知機能
        if(info_list[1] == 1):
            slack_webhook_token = msg_token
            data = {'text': str(comment)}
            requests.post(slack_webhook_token, data = json.dumps(data))
            
        #Lineの通知機能
        if(info_list[2] == 1):
            line_notify_token = msg_token
            line_notify_api = 'https://notify-api.line.me/api/notify'
            headers = {'Authorization': f'Bearer {line_notify_token}'}
            data = {'message': str(comment)}
            requests.post(line_notify_api, headers = headers, data = data)
            
        #出力ファイル
        if(info_list[3] == 1):
            print(comment, file = fp, flush=True)
            
        val = ""
            
    #読み込み変数がある場合（通常:info_type == 1、 認証時:info_type == 2）
    elif(info_type == 1 or info_type == 2):
        #コンソール標準出力and入力
        val = input(comment)
          
        #出力ファイル
        if(info_list[3] == 1 and info_type == 1):
            print(comment + val, file = fp, flush=True)
        elif(info_list[3] == 1 and info_type == 2):
            if(len(val) > 3):
                print(comment + val[0:3] + "".join(["*" for i in range(len(val)-3)]), file = fp, flush=True)
            else:
                print(comment + val, file = fp, flush=True)
            
    return val
            
def printout_cluster(comment, cls_monitor_level, set_monitor_level, info_list = [1,0,0,1], monitor_info_list = [1,0,0,1], fp = "", msg_token = ""):
    if(cls_monitor_level <= set_monitor_level):
        printout(comment, info_type = 0, info_list = monitor_info_list, fp = fp, msg_token = msg_token)
        
    else:
        printout(comment, info_type = 0, info_list = info_list, fp = fp, msg_token = "")
        
            



















































































