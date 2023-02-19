# -*- coding: utf-8 -*-

import scrapy

from . import mylib


class YosoCrawlerSpider(scrapy.Spider):
    name = 'yoso_crawler'
    allowed_domains = ["race.netkeiba.com"]

    # 調子偏差値htmlの出力先ディレクトリパス
    output_dir_path = 'D:/netkeiba/html_data/yoso/'

    # 予想は2011年4月23日から表示される
    base_url = "https://race.netkeiba.com/yoso/yoso_pro_opinion_list.html?race_id="
    start_urls = mylib.make_urls_depend_race_id(base_url, 2011)

    def __init__(self, *args, **kwargs):
        super(YosoCrawlerSpider, self).__init__(*args, **kwargs)
        mylib.make_output_dir(self.output_dir_path)

    def parse(self, response):
        if not response.css('.Pro_Yoso_Detail'):
            print('クロール対象外', response.url)
            return
        request = scrapy.Request(url=response.url, callback=self.yoso_parse)
        yield request

    def yoso_parse(self, response):
        mylib.write_html(self.output_dir_path, response.url.split('=')[-1], response)
