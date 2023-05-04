# -*- coding: utf-8 -*-
import scrapy

from . import mylib


class PedigreeCrawlerSpider(scrapy.Spider):
    name = 'pedigree_crawler'
    allowed_domains = ["db.netkeiba.com"]
    base_url = "https://db.netkeiba.com/horse/ped/"

    # 血統htmlの出力先ディレクトリパス
    output_html_dir = 'D:/netkeiba/html_data/pedigree/'

    def start_requests(self):
        """
        「取得」
        """
        mylib.make_output_dir(self.output_html_dir)

        start_urls = mylib.make_urls_depend_horse_id(self.base_url, self.output_html_dir)
        print('クロール対象数:' + str(len(start_urls)))
        for q in start_urls:
            yield scrapy.Request(q)

    def parse(self, response):
        yield scrapy.Request(url=response.url, callback=self.pedigree_parse)

    def pedigree_parse(self, response):
        mylib.write_html(self.output_html_dir, mylib.get_last_slash_word(response.url), response)
