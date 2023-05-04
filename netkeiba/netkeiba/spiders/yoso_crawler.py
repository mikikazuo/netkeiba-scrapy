# -*- coding: utf-8 -*-

import scrapy

from . import mylib


class YosoCrawlerSpider(scrapy.Spider):
    name = 'yoso_crawler'
    allowed_domains = ["race.netkeiba.com"]
    base_url = "https://race.netkeiba.com/yoso/yoso_pro_opinion_list.html?race_id="

    # 予想htmlの出力先ディレクトリパス
    output_html_dir = 'D:/netkeiba/html_data/yoso/'

    def start_requests(self):
        """
        「取得」
        予想は2011年4月23日から表示される
        """
        start_year = 2011
        mylib.make_output_dir(self.output_html_dir)

        start_urls = mylib.make_urls_depend_race_id(self.base_url, start_year)
        print('クロール対象数:' + str(len(start_urls)))
        for q in start_urls:
            yield scrapy.Request(q)

    def parse(self, response):
        # 予想は2011年4月23日からで中途半端なので2011年度指定でも弾けるようにしている
        if not response.css('.Pro_Yoso_Detail'):
            print('クロール対象外', response.url)
            return

        yield scrapy.Request(url=response.url, callback=self.yoso_parse)

    def yoso_parse(self, response):
        mylib.write_html(self.output_html_dir, response.url.split('=')[-1], response)
