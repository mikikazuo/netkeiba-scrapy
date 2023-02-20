# -*- coding: utf-8 -*-

import scrapy

from . import mylib


class PillarCrawlerSpider(scrapy.Spider):
    name = 'pillar_crawler'
    allowed_domains = ["race.netkeiba.com"]

    # 馬柱htmlの出力先ディレクトリパス
    output_html_dir = 'D:/netkeiba/html_data/pillar/'

    # 馬柱は2007年7月28日から表示される
    base_url = "https://race.netkeiba.com/race/shutuba_past.html?race_id="
    start_urls = mylib.make_urls_depend_race_id(base_url, 2007)

    def __init__(self, *args, **kwargs):
        super(PillarCrawlerSpider, self).__init__(*args, **kwargs)
        mylib.make_output_dir(self.output_html_dir)

    def parse(self, response):
        if not response.css('.Waku1'):
            print('クロール対象外', response.url)
            return
        request = scrapy.Request(url=response.url, callback=self.pillar_parse)
        yield request

    def pillar_parse(self, response):
        mylib.write_html(self.output_html_dir, response.url.split('=')[-1], response)
