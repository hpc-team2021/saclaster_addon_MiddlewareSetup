# System
### sacluster

さくらのクラウドを使用したクラスタ構築に特化したユーザの手間を軽減するスクリプトシステム<br>
__現在はクラスタ構築の機能のみ公開中__

<br>利用料等はさくらのクラウドを使用するため、さくらインターネットの規約に依存します。<br>
[さくらのクラウド利用料について](https://cloud.sakura.ad.jp/payment/)<br>
※_ユーザーの誤操作により料金が発生した場合、または第三者によりユーザーのアカウントが使用された場合にも我々は一切の責任を負いかねますのでご了承ください。_<br>

### Sakura HPC Manager

Saclusterの機能にHPCとして使用できる環境構築を追加したシステム<br>

Sakura HPC ManagerではSaclusterと同様にユーザによるコマンド入力のみで、IPアドレスの自動割り当て・SSH環境の自動構築・ 並列計算環境・ジョブスケジューリング環境・モニタリング環境の自動構築を行うことができます。<br>


# Features
現在前年度チームにより、どんな人でも簡単にクラスタの自動構築を行うsaclusterが開発されています。<br>
ユーザーがクラスタ構築のためのパラメータを指定するとsaclusterはAPIを生成し、実行します。<br>
設定はテンプレート化されるため、同じ構造のクラスタを構築する際はパラメータを再度指定する必要はありません。<br>

### Pros of Sacluster
- 少数のパラメータで簡単にクラスタ構築が可能
- 構築の際、画面に向き合う必要がない
- 何度も同じ設定を行う必要がない

### Main Functions in Sacluster
- クラスタ構築
- クラスタ起動
- クラスタ停止
- クラスタ削除
- クラスタ変更

<br>

今年度チームは、saclusterにHPCの機能を追加したSakura HPC Managerの開発を進めました。<br>
追加した機能は以下４点です。<br>
- ローカルIPアドレス自動割り当て
- 監視モニタ(Ganglia)
- 並列計算機能(mpich)
- リソース自動管理(slurm)

<br>


# Quick Start
__How to Run Prototype__

```bash
git clone https://github.com/hpc-team2021/saclaster_addon_MiddlewareSetup.git
# pythonパッケージの自動インストール
pip install Mockup-0.0.1.tar.gz
# クラスタ構築
python lib/command/command_pro.py [saclasterのオプション] [Sakura HPC Managerのオプション]
```

<br>

__Options in Saclaster__


| オプション | パラメータの有無 | パラメータ（有の場合） | 説明 |
| ------------- | ------------- | ------------- | ------------- |
| -i  | 有 | 読み込みconfigファイルのディレクトリ | configファイルを sacluster/config/config.json 以外のファイルを読み込む |
| -d | 有 | configファイル出力のためのディレクトリ | configファイルを sacluster/config 以外のディレクトリに出力する |
| -p | 無 | - | configファイルを sacluster/config 以外のディレクトリに出力する際、親ディレクトリを作成する |
| -o | 無 | - | 標準ファイル出力を行う |
| -v | 無 | - | dedugレベル以上のログ出力を行う |
| -a | 無 | - | クラスタ作成後、自動起動を行う |
| -dryrun | 無 | - | 試運転モード(API を仕様しない処理のみ実行) |

<br>

<br>

__Option in Sakura HPC Manager__

| オプション | パラメータの有無 | 説明 | 
| --- | --- | --- | 
| -m | 無 | ミドルウェアの構築を行う | 


<br>




# Demo
詳しい使い方は [Wiki](https://github.com/hpc-team2020/sacluster/wiki) をご覧ください。
### デモ動画

<br>

![名称未設定](https://user-images.githubusercontent.com/32956197/121409560-9f528a80-c99c-11eb-9967-7e092c406f56.gif)



<br>

# Author
2021
* 作成者： Kousuke Tsuji , Daiki Murayama , Ayumi Moriyasu
* 所属： Kyushu Institute of Technology
* E-mail:sakura.hpc2021@gmail.com
* About us: https://qiita.com/sakura_hpc2021

2020
* 作成者： Sho Tsukiyama（＠ShoTsukiyama）, Keigo Takahira（@k-takahi）, Saki Masui（＠saki0311）
* 所属： Kyushu Institute of Technology
* E-mail:sakura.hpc2020@gmail.com

* About us: https://qiita.com/hpc2020

# License

sacluster is under [Appach2.0 license](https://www.apache.org/licenses/LICENSE-2.0).
