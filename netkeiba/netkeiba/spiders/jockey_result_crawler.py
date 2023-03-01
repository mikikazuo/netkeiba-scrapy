# -*- coding: utf-8 -*-

import scrapy

from . import mylib


class JockeyResultCrawlerSpider(scrapy.Spider):
    name = 'jockey_result_crawler'
    allowed_domains = ['db.netkeiba.com']
    base_url = "https://db.netkeiba.com/jockey/result/"

    # get_jockey_id.pyで作成した騎手id一覧csv
    input_csv_path = 'D:/netkeiba/csv_data/all_jockey_id.csv'
    # 騎手実績htmlの出力先ディレクトリパス
    output_html_dir = 'D:/netkeiba/html_data/jockey_result/'

    def __init__(self, *args, **kwargs):
        """
        「更新」

        年度が変わったら全てのhtmlを削除し、クロールし直すこと
        """
        super(JockeyResultCrawlerSpider, self).__init__(*args, **kwargs)
        mylib.make_output_dir(self.output_html_dir)

        self.start_urls = mylib.make_urls_depend_list_csv(self.base_url, self.input_csv_path, 'jockey_id',
                                                          self.output_html_dir)
        print('クロール対象数:' + str(len(self.start_urls)))

    def parse(self, response):
        yield scrapy.Request(url=response.url, callback=self.jockey_profile_parse)

    def jockey_profile_parse(self, response):
        mylib.write_html(self.output_html_dir, mylib.get_last_slash_word(response.url), response)
