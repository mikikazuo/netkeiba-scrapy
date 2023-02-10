# scrapyによるクローリング（netkeibaフォルダ下）
htmlの保存だけを行う。途中、[データ抽出しcsv化](https://github.com/mikikazuo/netkeiba-scrapy/blob/master/README.md#lxml%E3%81%AB%E3%82%88%E3%82%8B%E3%82%B9%E3%82%AF%E3%83%AC%E3%82%A4%E3%83%94%E3%83%B3%E3%82%B0generate_csv%E3%83%95%E3%82%A9%E3%83%AB%E3%83%80)する必要がある。

## 最初に実行すべきもの
#### １．レースデータhtml([例](https://db.netkeiba.com/race/202205050511/))の収集（race_crawler.py）
#### ２．レースデータhtmlをスクレイピング（race_scraper.py）⇒これだけ[generate_csvフォルダ下](https://github.com/mikikazuo/netkeiba-scrapy/blob/master/README.md#lxml%E3%81%AB%E3%82%88%E3%82%8B%E3%82%B9%E3%82%AF%E3%83%AC%E3%82%A4%E3%83%94%E3%83%B3%E3%82%B0generate_csv%E3%83%95%E3%82%A9%E3%83%AB%E3%83%80)
#### ３．馬id一覧csvから馬データhtml([例](https://db.netkeiba.com/horse/2020103656/))の収集（horse_crawler.py）
３を実行するにあたって、１⇒２⇒３の手順を踏むこと。<br>

## １で保存したレースデータhtmlのファイル名に基づく処理
#### ４．レースデータhtmlのファイル名から調子偏差値html([例](https://race.sp.netkeiba.com/barometer/score.html?race_id=202310020103))の収集（condition_crawler.py）
#### ５．レースデータhtmlのファイル名から馬柱(5走)html([例](https://race.netkeiba.com/race/shutuba_past.html?race_id=202305010809))の収集（pillar_crawler.py）
#### ６．レースデータhtmlのファイル名から予想html([例](https://race.netkeiba.com/yoso/yoso_pro_opinion_list.html?race_id=202309010103))の収集（yoso.py）

## Splashについて
javascriptで動的に取得したいときに使うものらしい。
競馬新聞([例](https://race.netkeiba.com/race/newspaper.html?race_id=202305010809&rf=shutuba_submenu))の取得で使おうと試したが上手くいかなかった。
[参考サイト](https://masalabo.blog/2022/03/04/scrapy-splash/)

# 経緯
[ベースとなったソースコード](https://github.com/watanta/netkeiba-scrapy)

spiderフォルダ下について引っ張ってこなかったコード　※（）はスクレイピング対象例

#### add_horse_crawler.py（馬データhtml）
add_race_id_list.csvが謎。

おそらく馬id一覧csvを挟まず、add_race_id_list.csvで対象となるレースデータから馬データhtmlを直接取得するためのものと思われる。

#### condition_crawler.py
([対象URL例](https://race.sp.netkeiba.com/barometer/score.html?race_id=202102011001&rf=race_list)）
調子偏差値が2017年１月から導入。調子偏差値は、枠順確定後から順次公開される。
[調子偏差値について](https://race.sp.netkeiba.com/barometer/about.html)レース結果の履歴データについては次のpredict_crawler.pyのほうが詳細に出ている。
予想データで表示される予想主は必ずしも、次のpredict_crawler.pyの参照先のものと一致するとは限らない。
⇒「本紙」は確定？次に「CP予想」、「大石川」が確定っぽい？

#### predict_crawler.py（[対象URL例](https://race.sp.netkeiba.com/barometer/score.html?race_id=202102011001&rf=race_list)）
# 必要ライブラリ
* scrapy
* pandas

# インストール方法
Pycharm(IDE)にならってライブラリインストール。

# 流れ
scrapyのプロジェクト作成(https://scrapy-ja.readthedocs.io/ja/latest/intro/tutorial.html)
```bash
scrapy startproject netkeiba
```
get_raced_horse.pyはscrapyに依存していないため、scrapy関連フォルダ外に配置している。

ターミナルでcdコマンドでnetkeiba\netkeiba\spidersフォルダ下に移動。
## スクレイピング開始コマンド
#### race_crawler.py
```bash
scrapy crawl race_crawler -a start_year=[開始年] -a end_year=[終了年]
```
#### horse_crawler.py
```bash
scrapy crawl horse_crawler
```

期間が１年の場合は開始年と終了年に同じ値を入れる

# 注意
1985年以前のレースデータには１着の馬しか記載されていないためrace_crawlerで取得できないようにしている。

race_crawlerで一度にスクレイピングする範囲は４年以下に抑えたほうがいい。多すぎると途中でPCが勝手に再起動した。
horse_crawlerでは、そのようなことはなかった謎。

[有料厩舎コメント](https://race.netkeiba.com/race/comment.html?race_id=201208020302&rf=race_submenu)

厩舎コメント公開の対象は新馬戦と特別レースです。（プレミアムコース対象サービス）

また、新馬だったとしても３つしか見られない[新馬有料例](https://race.netkeiba.com/race/comment.html?race_id=201205010103&rf=race_submenu)

馬柱は２００７年７月２８日（"200702020501"）から表示される

予想は2011年4月23日（"201104010101"）から表示される

<br><br><br><br><br>
# lxmlによるスクレイピング（generate_csvフォルダ）
[冒頭で取得](https://github.com/mikikazuo/netkeiba-scrapy/blob/master/README.md#scrapy%E3%81%AB%E3%82%88%E3%82%8B%E3%82%AF%E3%83%AD%E3%83%BC%E3%83%AA%E3%83%B3%E3%82%B0netkeiba%E3%83%95%E3%82%A9%E3%83%AB%E3%83%80%E4%B8%8B)したhtmlを解析し、csvの出力を行う。

１．レースデータ（）

２．馬データ（）

# 経緯
当初はデータベース(SQLite)を利用していたが、cuDFでの並列処理での取得が難しいため簡単なCSVに移行した。
[ベースとなったソースコード](https://github.com/watanta/netkeiba-scrapy/tree/master/netkeiba/netkeiba/spiders)
 
# 必要ライブラリ
* lxml

# インストール方法
Pycharm(IDE)にならってライブラリインストール。

# 流れ

 
# 注意

<br><br><br><br><br>
# 著者
* mikikazuo
* booster515ezweb@gmail.com
 
# License
非公開
