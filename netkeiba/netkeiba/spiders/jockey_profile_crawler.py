# -*- coding: utf-8 -*-

import pathlib

import pandas as pd
import scrapy

from . import mylib


class JockeyProfileCrawlerSpider(scrapy.Spider):
    name = 'jockey_profile_crawler'
    allowed_domains = ['db.netkeiba.com']
    base_url = "https://db.netkeiba.com/jockey/"

    # get_jockey_id.pyで作成した騎手id一覧csv
    input_csv_path = 'D:/netkeiba/csv_data/all_jockey_id.csv'
    # 騎手プロフィールhtmlの出力先ディレクトリパス
    output_html_dir = 'D:/netkeiba/html_data/jockey_profile/'

    def __init__(self, *args, **kwargs):
        """
        「取得」

        年度指定なしで実行
        """
        super(JockeyProfileCrawlerSpider, self).__init__(*args, **kwargs)
        mylib.make_output_dir(self.output_html_dir)

        jockey_id_df = pd.read_csv(self.input_csv_path, dtype={"jockey_id": str})
        jockey_id_list = sorted(set(jockey_id_df['jockey_id']))

        # ダウンロード済みhtmlは除外する
        path_iter = pathlib.Path(self.output_html_dir).iterdir()
        downloaded_jockey_id_list = [path.stem for path in path_iter]
        self.start_urls = [self.base_url + x for x in list(set(jockey_id_list) - set(downloaded_jockey_id_list))]
        print('クロール対象数:' + str(len(self.start_urls)))

    def parse(self, response):
        yield scrapy.Request(url=response.url, callback=self.jockey_profile_parse)

    def jockey_profile_parse(self, response):
        mylib.write_html(self.output_html_dir, mylib.get_last_slash_word(response.url), response)
