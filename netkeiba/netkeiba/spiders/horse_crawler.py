# -*- coding: utf-8 -*-

import pandas as pd
import scrapy

from . import mylib


class HorseCrawlerSpider(scrapy.Spider):
    name = 'horse_crawler'
    allowed_domains = ['db.netkeiba.com']
    base_url = "https://db.netkeiba.com/horse/"

    # race_scraper.pyで作成したスクレイピングcsv
    input_csv_path = 'D:/netkeiba/csv_data/race.csv'
    # 馬データhtmlの出力先ディレクトリパス
    output_html_dir = 'D:/netkeiba/html_data/horse/'

    def __init__(self, start_year=1986, *args, **kwargs):
        """
        起動コマンド　scrapy crawl horse_crawler -a start_year=[開始年]

        :param start_year: 「更新」範囲の開始年度。この年度以降にレースに出場した馬データhtmlを取得し直す。
        """
        super(HorseCrawlerSpider, self).__init__(*args, **kwargs)
        mylib.make_output_dir(self.output_html_dir)

        horse_id_df = pd.read_csv(self.input_csv_path, dtype={"horse_id": str, "race_id": str})
        horse_id_list = list(
            sorted(set(horse_id_df.loc[horse_id_df["race_id"] >= str(start_year) + '00000000', :]['horse_id'])))
        self.start_urls = [self.base_url + x for x in horse_id_list]
        print('クロール対象数:' + str(len(self.start_urls)))

    def parse(self, response):
        yield scrapy.Request(url=response.url, callback=self.horse_parse)

    def horse_parse(self, response):
        mylib.write_html(self.output_html_dir, mylib.get_last_slash_word(response.url), response)
