import os

os.chdir(os.path.dirname(os.path.abspath(__file__)))
common_path = os.path.abspath("../../..")

def addon_main():
    print("アドオンの関数")

def addon_start():
    print("ミドルウェアの起動")