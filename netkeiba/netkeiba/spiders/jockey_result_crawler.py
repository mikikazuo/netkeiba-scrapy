# -*- coding: utf-8 -*-

import scrapy

from . import mylib


class JockeyResultCrawlerSpider(scrapy.Spider):
    name = 'jockey_result_crawler'
    allowed_domains = ['db.netkeiba.com']
    base_url = "https://db.netkeiba.com/jockey/result/"

    # get_jockey_id.pyで作成した騎手id一覧csv
    input_csv_path = 'D:/netkeiba/csv_data/common/all_jockey_id.csv'
    # 騎手実績htmlの出力先ディレクトリパス
    output_html_dir = 'D:/netkeiba/html_data/jockey_result/'

    def start_requests(self):
        """
        「更新」
        年度が変わったら全てのhtmlを削除し、クロールし直すこと
        """
        # 更新範囲の開始年度。過去の履歴が追加されているので、念のため最後にクロールしたタイミングの３年前から取得しなおしたほうがいい。
        mylib.make_output_dir(self.output_html_dir)

        start_urls = mylib.make_urls_depend_list_csv(self.base_url, self.input_csv_path, 'jockey_id',
                                                     self.output_html_dir)
        print('クロール対象数:' + str(len(start_urls)))
        for q in start_urls:
            yield scrapy.Request(q)

    def parse(self, response):
        yield scrapy.Request(url=response.url, callback=self.jockey_profile_parse)

    def jockey_profile_parse(self, response):
        mylib.write_html(self.output_html_dir, mylib.get_last_slash_word(response.url), response)
