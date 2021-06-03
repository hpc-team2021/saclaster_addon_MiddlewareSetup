# sacluster

クラスタ構築に特化したクラスタ構築時にユーザの手間を軽減するスクリプトシステム


# DEMO

"sacluster"の魅力が直感的に伝えわるデモ動画や図解を載せる

# Features

"sacluster"のセールスポイントや差別化などを説明する

# Requirement

"sacluster"を動かすのに必要なライブラリなどを列挙する

* OS: macOS Big Sur、macOS Catalina
* Python 3.7.7
* pip 20.1.1 

自動インストールされるpythonパッケージ
* json 0.1.1
* json schema 3.2.0
* requests 2.23.0
* pandas 1.0.3

# Installation

pythonパッケージの自動インストール

```bash
pip install Mockup-0.0.1.tar.gz
```

# Usage

プロトタイプの実行方法

```bash
git clone https://github.com/hpc-team2020/sacluster.git
python lib/command/command_pro.py [オプション]
```


オプション一覧
| オプション | パラメータの有無 | パラメータ（有の場合） | 説明 |
| ------------- | ------------- | ------------- | ------------- |
| -i  | 有 | 読み込みconfigファイルのディレクトリ | configファイルを sacluster/config/config.json 以外のファイルを読み込む |
| -d | 有 | configファイル出力のためのディレクトリ | configファイルを sacluster/config 以外のディレクトリに出力する |
| -p | 無 | - | configファイルを sacluster/config 以外のディレクトリに出力する際、親ディレクトリを作成する |
| -o | 無 | - | 標準ファイル出力を行う |
| -v | 無 | - | dedugレベル以上のログ出力を行う |
| -a | 無 | - | クラスタ作成後、自動起動を行う |
| -dryrun | 無 | - | 試運転モード(API を仕様しない処理のみ実行) |


config パラメータ定義について
config パラメータ定義時は config パラメータ名に加えて、5 つの section のパラメータ定 義する必要がある。5 つのセクションとその概要を以下に示す。
| セッション名 | 区分 | 説明 |
| ------------- | ------------- | ------------- |
| Compute  | 必須 | コンピュートノードに関する設定 |
| Head| 必須 | ヘッドノードに関する設定 |
| NFS | 任意 | NFSに関する設定 |
| Zone | *必須 | Zoneに関する設定 |
| Monitor | 任意 | 通知機能に関する設定 |

- Compute section

| パラメータ名 | 説明 |
| ------------- | ------------- |
| The number of compute nodes | クラスタ内のコンピュートノードの数 |
| The number of cores for compute node| コンピュートノードの core 数 |
| Size of memory for compute node | コンピュートノードの memory 数 |
| Disk type for compute node | コンピュートノードのディスクの種類 |
| Disk size for compute node | コンピュートノードのディスクのサイズ |
| Connection type between server and disk for compute node | コンピュートノードのディスク接続方法 |
| OS in compute node | コンピュートノードの OS |
| Compute switch | コンピュート switch の有無 |

# Note

注意点などがあれば書く

# Author

* 作成者： Sho Tsukiyama（＠ShoTsukiyama）, Keigo Takahira（@k-takahi）
* 広報： Saki Masui（＠saki0311）
* 所属： Kyushu Institute of Technology
* E-mail:

* About us: https://qiita.com/hpc2020

# License

"sacluster" is under [Appach2.0 license](https://ja.wikipedia.org/wiki/Apache_License).
