# -*- coding: utf-8 -*-
import scrapy

from . import mylib


class ConditionCrawlerSpider(scrapy.Spider):
    name = 'condition_crawler'
    allowed_domains = ["race.sp.netkeiba.com"]
    base_url = "https://race.sp.netkeiba.com/barometer/score.html?race_id="

    # 調子偏差値htmlの出力先ディレクトリパス
    output_html_dir = 'D:/netkeiba/html_data/condition/'

    def __init__(self, start_year=2017, *args, **kwargs):
        """
        起動コマンド　scrapy crawl condition_crawler -a start_year=[開始年]

        調子偏差値は2017年1月から導入されている。区切りがいい1月からなのでparseで弾く条件文は書いていない。

        :param start_year: 「取得」範囲の開始年度。
        """
        super(ConditionCrawlerSpider, self).__init__(*args, **kwargs)
        mylib.make_output_dir(self.output_html_dir)

        self.start_urls = mylib.make_urls_depend_race_id(self.base_url, start_year)
        print('クロール対象数:' + str(len(self.start_urls)))

    def parse(self, response):
        yield scrapy.Request(url=response.url, callback=self.condition_parse)

    def condition_parse(self, response):
        mylib.write_html(self.output_html_dir, response.url.split('=')[-1], response)
