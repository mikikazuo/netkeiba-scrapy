# -*- coding: utf-8 -*-

import numpy as np
import scrapy

from . import mylib


class RaceCrawlerSpider(scrapy.Spider):
    name = 'race_crawler'
    allowed_domains = ['db.netkeiba.com']
    base_url = "https://db.netkeiba.com/"

    # レースデータhtml出力先ディレクトリパス
    output_html_dir = 'D:/netkeiba/html_data/race/'

    # start_yearからend_yearまでの年度データを取得
    def __init__(self, start_year, end_year, *args, **kwargs):
        """
        起動コマンド　scrapy crawl race_crawler -a start_year=[開始年] -a end_year=[終了年]

        開始年と終了年の差は４以下に抑えたほうがいい。多すぎると途中でPCが勝手に再起動した。

        期間が１年の場合は開始年と終了年に同じ値を入れる

        レースは1986年1月から

        :param start_year: 「取得」対象の開始年度
        :param end_year: 「取得」対象の終了年度
        """
        super(RaceCrawlerSpider, self).__init__(*args, **kwargs)
        mylib.make_output_dir(self.output_html_dir)

        # 1985年以前はレースデータに１着の馬しか記載されていないため、ここで切り上げる
        start_year_formed = np.clip(start_year, 1986, None)
        # rangeで含まれるようにint(start) - 1にしている
        self.start_urls = [self.base_url + '?pid=race_top&date=' + str(i) + str(j).zfill(2) + '01' for i in
                           range(int(end_year), int(start_year_formed) - 1, -1) for j in range(1, 13)]
        print('クロール対象数:' + str(len(self.start_urls)))

    def parse(self, response):
        race_list = response.xpath(
            '//td[contains(@class,"sat") or contains(@class,"sun") or contains(@class,"selected")]/a/@href').extract()
        race_list = [self.base_url + x for x in race_list]

        # カレンダーから各日に開催されたレースの一覧へ
        for race_url in race_list:
            if race_url is not None:
                yield scrapy.Request(url=race_url, callback=self.racelist_parse)

    def racelist_parse(self, response):
        race_url_list = response.xpath('//dl[@class="race_top_data_info fc"]/dd/a/@href').extract()
        race_url_list = [self.base_url + x for x in race_url_list]

        # 各レースページヘ
        for race_url in race_url_list:
            if race_url is not None:
                yield scrapy.Request(url=race_url, callback=self.race_parse)

    def race_parse(self, response):
        # filterはリスト内の空文字を除去する
        mylib.write_html(self.output_html_dir, mylib.get_last_slash_word(response.url), response)
