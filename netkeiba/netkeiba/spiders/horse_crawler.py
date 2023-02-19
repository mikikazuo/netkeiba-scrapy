# -*- coding: utf-8 -*-
# race_scraper.pyで出力されたrace.csvにあるhorse_idを元にクロール
import pathlib

import pandas as pd
import scrapy

from . import mylib


class HorseCrawlerSpider(scrapy.Spider):
    name = 'horse_crawler'
    allowed_domains = ['db.netkeiba.com']
    start_urls = ['http://db.netkeiba.com/?pid=race_top']
    base_url = "https://db.netkeiba.com/horse/"

    # race_scraper.pyで作成したスクレイピングcsv
    input_csv_path = 'D:/netkeiba/csv_data/race.csv'
    # 馬データhtmlの出力先ディレクトリパス
    output_dir_path = 'D:/netkeiba/html_data/horse/'
    # get_raced_horse.pyで出力した馬id一覧csvファイル
    csv_path = 'D:/netkeiba/csv_data/all_horse_max_usable.csv'

    def __init__(self, *args, **kwargs):
        super(HorseCrawlerSpider, self).__init__(*args, **kwargs)
        mylib.make_output_dir(self.output_dir_path)

        horse_id_df = pd.read_csv(self.input_csv_path, dtype={"horse_id": str})
        horse_id_list = sorted(set(horse_id_df['horse_id']))

        # ダウンロード済みhtmlは除外する
        path_iter = pathlib.Path(self.output_dir_path).iterdir()
        downloaded_horse_id_list = [path.stem for path in path_iter]
        self.start_urls = [self.base_url + x for x in list(set(horse_id_list) - set(downloaded_horse_id_list))]
        print('クロール対象数:' + str(len(self.start_urls)))

    def parse(self, response):
        request = scrapy.Request(url=response.url, callback=self.horse_parse)
        yield request

    def horse_parse(self, response):
        mylib.write_html(self.output_dir_path, mylib.get_last_slash_word(response.url), response)
