import mypath
from generate_csv import mylib


class PaybackScraper(mylib.Scraper):
    def scrape_from_page(self, html_path):
        """
        三連単（全レース実装）はざっくり2009年以降。※正確には2008年7月19日以降
        """

        # 同着のパターンがあるためこの形　202009050712
        def split_data(data):
            if not data:  # 馬連は9頭以上の場合ににしか発売されないため、ない場合ここで弾く
                return None

            key_size = int(len(data) / 3)
            return {'umaban': data[0:key_size], 'payback': data[key_size:key_size * 2], 'ninki': data[key_size * 2:]}

        html = mylib.read_html(html_path)

        tanshou_data = html.xpath('//th[@class="tan"]/following-sibling::td/text()')
        fukushou_data = html.xpath('//th[@class="fuku"]/following-sibling::td/text()')
        # 出走する馬が9頭以上の場合に発売  枠は同じ番号の馬がいる場合がある
        wakuren_data = html.xpath('//th[@class="waku"]/following-sibling::td/text()')
        # TODO 例外　raceId 200409050105
        umaren_data = html.xpath('//th[@class="uren"]/following-sibling::td/text()')
        wide_data = html.xpath('//th[@class="wide"]/following-sibling::td/text()')
        # TODO 2003年以降発売
        umatan_data = html.xpath('//th[@class="utan"]/following-sibling::td/text()')
        # TODO 2003年以降発売
        sanrenpuku_data = html.xpath('//th[@class="sanfuku"]/following-sibling::td/text()')
        # 三連単（全レース実装）はざっくり2009年以降。※正確には2008年7月19日以降
        sanrentan_data = html.xpath('//th[@class="santan"]/following-sibling::td/text()')

        lap_data = html.xpath('//th[contains(text(), "ラップ")]/following-sibling::td/text()')
        base_data = html.xpath('//th[contains(text(), "ペース")]/following-sibling::td/text()')

        result = {
            'race_id': html_path.stem,
            'tanshou': split_data(tanshou_data),
            'fukushou': split_data(fukushou_data),
            'wakuren': split_data(wakuren_data),
            'umaren': split_data(umaren_data),
            'wide': split_data(wide_data),
            'umatan': split_data(umatan_data),
            'sanrenpuku': split_data(sanrenpuku_data),
            'sanrentan': split_data(sanrentan_data),
            # 'lap_time': lap_data[0],
            # 'base_time': base_data[0],
        }
        return [result]


if __name__ == '__main__':
    input_html_dir = "D:/netkeiba/html_data/race/"
    # スクレイピング結果csvの出力先パス
    output_csv_path = "D:/netkeiba/csv_data/payback.csv"

    # race_scraper.pyの取得範囲と合わせる
    PaybackScraper(input_html_dir, output_csv_path, (mypath.start_year, mypath.end_year))
