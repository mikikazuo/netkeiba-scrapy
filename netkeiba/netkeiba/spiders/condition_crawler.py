# -*- coding: utf-8 -*-
import scrapy

from . import mylib


class ConditionCrawlerSpider(scrapy.Spider):
    name = 'condition_crawler'
    allowed_domains = ["race.sp.netkeiba.com"]

    # 調子偏差値htmlの出力先ディレクトリパス
    output_dir_path = 'D:/netkeiba/html_data/condition/'

    # 調子偏差値は2017年1月から導入されている。区切りがいい1月からなのでparseで弾く条件文は必要はない。
    base_url = "https://race.sp.netkeiba.com/barometer/score.html?race_id="
    start_urls = mylib.make_urls_depend_race_id(base_url, 2017)

    def __init__(self, *args, **kwargs):
        super(ConditionCrawlerSpider, self).__init__(*args, **kwargs)
        mylib.make_output_dir(self.output_dir_path)

    def parse(self, response):
        request = scrapy.Request(url=response.url, callback=self.condition_parse)
        yield request

    def condition_parse(self, response):
        mylib.write_html(self.output_dir_path, response.url.split('=')[-1], response)
