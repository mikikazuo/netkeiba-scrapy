# -*- coding: utf-8 -*-

import scrapy

from . import mylib


class YosoCrawlerSpider(scrapy.Spider):
    name = 'yoso_crawler'
    allowed_domains = ["race.netkeiba.com"]
    base_url = "https://race.netkeiba.com/yoso/yoso_pro_opinion_list.html?race_id="

    # 調子偏差値htmlの出力先ディレクトリパス
    output_html_dir = 'D:/netkeiba/html_data/yoso/'

    def __init__(self, start_year=2011, *args, **kwargs):
        """
        起動コマンド　scrapy crawl yoso_crawler -a start_year=[開始年]

        予想は2011年4月23日から表示される

        :param start_year: 「取得」範囲の開始年度
        """
        super(YosoCrawlerSpider, self).__init__(*args, **kwargs)
        mylib.make_output_dir(self.output_html_dir)

        self.start_urls = mylib.make_urls_depend_race_id(self.base_url, start_year)
        print('クロール対象数:' + str(len(self.start_urls)))

    def parse(self, response):
        # 予想は2011年4月23日からで中途半端なので2011年度指定でも弾けるようにしている
        if not response.css('.Pro_Yoso_Detail'):
            print('クロール対象外', response.url)
            return

        yield scrapy.Request(url=response.url, callback=self.yoso_parse)

    def yoso_parse(self, response):
        mylib.write_html(self.output_html_dir, response.url.split('=')[-1], response)
