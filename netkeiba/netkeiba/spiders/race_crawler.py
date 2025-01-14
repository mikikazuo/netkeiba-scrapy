# -*- coding: utf-8 -*-

import numpy as np
import scrapy
from datetime import datetime
from . import mylib


class RaceCrawlerSpider(scrapy.Spider):
    name = 'race_crawler'
    allowed_domains = ['db.netkeiba.com']
    base_url = "https://db.netkeiba.com/"

    # レースデータhtml出力先ディレクトリパス
    #output_html_dir = 'D:/netkeiba/html_data/race/'
    output_html_dir = 'D:/netkeiba/html_data/testrace/'
    dt_now = datetime.now()
    def start_requests(self):
        """
        「取得」

        開始年と終了年の差は４以下に抑えたほうがいい。多すぎると途中でPCが勝手に再起動した。

        start_yearからend_yearまでの年度データを取得
        期間が１年の場合は開始年と終了年に同じ値を入れる

        レースは1986年1月から
        """
        start_year = 2005
        end_year = 2010
        start_year = end_year = 2023
        mylib.make_output_dir(self.output_html_dir)

        # 1985年以前はレースデータに１着の馬しか記載されていないため、ここで切り上げる
        start_year_formed = np.clip(start_year, 1986, None)
        # rangeで含まれるようにint(start) - 1にしている
        # start_urls = [self.base_url + '?pid=race_top&date=' + str(i) + str(j).zfill(2) + '01' for i in
        #               range(int(end_year), int(start_year_formed) - 1, -1) for j in range(1, 13)]'
        print(self.dt_now)
        start_urls = [f'{self.base_url}?pid=race_top&date={self.dt_now.year}{str(self.dt_now.month).zfill(2)}']
        print(start_urls)
        print('クロール対象数:' + str(len(start_urls)))
        for q in start_urls:
            yield scrapy.Request(q)

    def parse(self, response):
        # 月～金の祝日開催の場合でもsunクラスが割り当てられている。
        race_list = response.xpath(
            '//td[contains(@class,"sat") or contains(@class,"sun") or contains(@class,"selected")]/a/@href').extract()
        #race_list = [self.base_url + x for x in race_list]
        race_list = [self.base_url + x for x in race_list if (self.dt_now-datetime.strptime(mylib.get_last_slash_word(x), '%Y%m%d')).days<14]

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
        mylib.write_html(self.output_html_dir, mylib.get_last_slash_word(response.url), response)
