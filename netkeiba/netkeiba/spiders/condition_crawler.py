# -*- coding: utf-8 -*-
import scrapy

from . import mylib


class ConditionCrawlerSpider(scrapy.Spider):
    name = 'condition_crawler'
    allowed_domains = ["race.sp.netkeiba.com"]
    base_url = "https://race.sp.netkeiba.com/barometer/score.html?race_id="

    # 調子偏差値htmlの出力先ディレクトリパス
    output_html_dir = 'D:/netkeiba/html_data/condition/'

    def start_requests(self):
        """
        「取得」
        調子偏差値は2017年1月から導入されている。区切りがいい1月からなのでparseで弾く条件文は書いていない。
        """
        start_year = 2017
        mylib.make_output_dir(self.output_html_dir)

        start_urls = mylib.make_urls_depend_race_id(self.base_url, start_year)
        print('クロール対象数:' + str(len(start_urls)))
        for q in start_urls:
            yield scrapy.Request(q)

    def parse(self, response):
        yield scrapy.Request(url=response.url, callback=self.condition_parse)

    def condition_parse(self, response):
        mylib.write_html(self.output_html_dir, response.url.split('=')[-1], response)
