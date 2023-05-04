# -*- coding: utf-8 -*-

import scrapy

from . import mylib


class PillarCrawlerSpider(scrapy.Spider):
    name = 'pillar_crawler'
    allowed_domains = ["race.netkeiba.com"]
    base_url = "https://race.netkeiba.com/race/shutuba_past.html?race_id="

    # 馬柱htmlの出力先ディレクトリパス
    output_html_dir = 'D:/netkeiba/html_data/pillar/'

    def start_requests(self):
        """
        「更新」
        馬柱は2007年7月28日から表示される

        過去の履歴が追加されているので、念のため最後にクロールしたタイミングの３年前から取得しなおしたほうがいい。
        """
        start_year = 2007
        mylib.make_output_dir(self.output_html_dir)

        start_urls = mylib.make_urls_depend_race_id(self.base_url, start_year)
        print('クロール対象数:' + str(len(start_urls)))
        for q in start_urls:
            yield scrapy.Request(q)

    def parse(self, response):
        # 馬柱は2007年7月28日からで中途半端なので2007年度指定でも弾けるようにしている
        if not response.css('.Waku1'):
            print('クロール対象外', response.url)
            return

        yield scrapy.Request(url=response.url, callback=self.pillar_parse)

    def pillar_parse(self, response):
        mylib.write_html(self.output_html_dir, response.url.split('=')[-1], response)
