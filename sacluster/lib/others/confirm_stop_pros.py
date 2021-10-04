
import sys
import os

path = "../../.."
os.chdir(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(path + "/lib/others")

from info_print import printout

def conf_stop_process(info_list, f):
    while(True):
        printout("INFO: instruments are not stopped", info_type = 0, info_list = info_list, fp = f)
        val = printout("[Can instruments be stopped? {yes(y) / no(n)}] >> ", info_type = 1, info_list = info_list, fp = f).replace(" ","")
        if(val == "yes" or val == "y"):
            return True
        elif(val == "no" or val == "n"):
            printout("Warning: instruments must be stopped. This process is stopped.", info_type = 0, info_list = info_list, fp = f)
            sys.exit()
        else:
            printout("Warning: The input is an unexpected value", info_type = 0, info_list = info_list, fp = f)





