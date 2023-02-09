# netkeiba-notebook
１．レースデータhtmlの収集（race_crawler.py）

２．レースデータhtmlから馬id一覧csv出力（get_raced_horse.py）

３．馬id一覧csvから馬データhtmlの収集（horse_crawler.py）

１⇒２⇒３の手順を踏むこと。
# 経緯
[ベースとなったソースコード](https://github.com/watanta/netkeiba-scrapy)

spiderフォルダ下について引っ張ってこなかったコード　※（）はスクレイピング対象例

add_horse_crawler.py（馬データhtml）・・・add_race_id_list.csvが謎。
おそらく馬id一覧csvを挟まず、add_race_id_list.csvで対象となるレースデータから馬データhtmlを直接取得するためのものと思われる。

condition_crawler.py（[対象URL例](https://race.sp.netkeiba.com/barometer/score.html?race_id=202102011001&rf=race_list)）・・・
いつから調子偏差値が導入されたのか不明（おおよそ2017年から？）。調子偏差値は、枠順確定後から順次公開される。
[調子偏差値について](https://race.sp.netkeiba.com/barometer/about.html)レース結果の履歴データについては次のpredict_crawler.pyのほうが詳細に出ている。
予想データで表示される予想主は必ずしも、次のpredict_crawler.pyの参照先のものと一致するとは限らない。
⇒「本紙」は確定？次に「CP予想」、「大石川」が確定っぽい？

 predict_crawler.py（[対象URL例](https://race.sp.netkeiba.com/barometer/score.html?race_id=202102011001&rf=race_list)）
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

# 著者
* mikikazuo
* booster515ezweb@gmail.com
 
# License
非公開
