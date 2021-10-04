
import requests
import json
from tqdm import tqdm
from tqdm._utils import _term_move_up
import sys

class Color:
    NORMAL    = ''
    BLACK     = '\033[30m'
    RED       = '\033[31m'
    GREEN     = '\033[32m'
    YELLOW    = '\033[33m'
    BLUE      = '\033[34m'
    PURPLE    = '\033[35m'
    CYAN      = '\033[36m'
    WHITE     = '\033[37m'
    END       = '\033[0m'
    BOLD      = '\038[1m'
    UNDERLINE = '\033[4m'
    INVISIBLE = '\033[08m'
    REVERCE   = '\033[07m'
    
color_dict = {"": Color.NORMAL, "red": Color.RED, "green": Color.GREEN, "yellow": Color.YELLOW, "blue": Color.BLUE, "cyan": Color.CYAN, "purple": Color.PURPLE}

def printout(comment, info_type = 0, info_list = [1,0,0,1], fp = "", msg_token = "", color = "", end = None, overwrite = False):
    #print(overwrite)
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
            if(overwrite == True):
                #print("aaa")
                border = "="*100
                prefix = _term_move_up() + '\r' + " "*len(border) + "\r"
                tqdm.write(prefix + comment)
                #print(color_dict[color] + '\r' + comment + Color.END, end = '')
            else:
                print(color_dict[color] + comment + Color.END, end = end)
        
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
            print(color_dict[color] + comment + Color.END, end = end, file = fp, flush=True)
            
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
        
            



















































































