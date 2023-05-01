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

    def start_requests(self):
        """
        __init__でのself.start_urls指定では、referer参照で二重にクロールされていたが、本関数ではそれが解消できた。
        TODO 他のクロールではどうなのか再検証
        """
        start_year = 2009
        mylib.make_output_dir(self.output_html_dir)

        race_df = pd.read_csv(self.input_csv_path, dtype={"horse_id": str, "race_id": str})
        horse_id_list = list(
            sorted(set(race_df.loc[race_df["race_id"] >= str(start_year) + '00000000', :]['horse_id'])))

        start_urls = [self.base_url + x for x in horse_id_list]
        print('クロール対象数:' + str(len(start_urls)))
        for q in start_urls:
            yield scrapy.Request(q)

    def parse(self, response):
        yield scrapy.Request(url=response.url, callback=self.horse_parse)

    def horse_parse(self, response):
        mylib.write_html(self.output_html_dir, mylib.get_last_slash_word(response.url), response)
