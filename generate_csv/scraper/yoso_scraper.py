from generate_csv import mylib
from netkeiba.netkeiba.spiders import mylib as crawl_mylib


class YosoScraper(mylib.Scraper):
    def scrape_from_page(self, html_path):
        html = mylib.read_html(html_path)
        result_all = []

        for yosoka_row in html.xpath('//div[@class="YosoDeTailList"]'):
            yosoka = yosoka_row.xpath('div/div/p[@class="YosoDeTailName"]')[0].text
            yoso_rows = yosoka_row.xpath('div[contains(@class,"YosoDeTailItem2")]/table/tbody/tr')
            for yoso_row in yoso_rows:
                yoso = None
                for name in ['Honmei', 'Taikou', 'Kurosan', 'Hoshi', 'Osae']:
                    if yoso_row.xpath(f'th/span[contains(@class,"Icon_{name}")]'):
                        yoso = name
                        break
                horse_id = crawl_mylib.get_last_slash_word(yoso_row.xpath('td/a/@href')[0])
                result = {
                    "race_id": html_path.stem,
                    "horse_id": horse_id,
                    "yosoka": yosoka,
                    "yoso": yoso
                }
                result_all.append(result)
        return result_all


if __name__ == '__main__':
    input_html_dir = "D:/netkeiba/html_data/yoso/"
    # スクレイピング結果csvの出力先パス
    output_csv_path = "D:/netkeiba/csv_data/yoso.csv"

    # race_scraper.pyの取得範囲と合わせる
    YosoScraper(input_html_dir, output_csv_path, (2017, 2030))
