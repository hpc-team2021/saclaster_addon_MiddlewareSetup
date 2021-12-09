import os
os.chdir(os.path.dirname(os.path.abspath(__file__)))
common_path = os.path.abspath("../../..")


def prepare_main():
    print("""起動直後、addOnの機能が有効なら、クラスター構築のjsonファイルを書き換える必要あり
    """)