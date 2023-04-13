from generate_csv import mylib


class JockeyProfileScraper(mylib.Scraper):
    def scrape_from_page(self, html_path):
        html = mylib.read_html(html_path)

        height = html.xpath('//th[contains(text(), "身長/体重")]/following-sibling::td')
        height = height[0].text if height else None
        height = height.split('/')[0] if height and '-' not in height else None

        jockey_from = html.xpath('//th[contains(text(), "出身地")]/following-sibling::td')[0].text
        jockey_from = jockey_from.split('/') if '-' not in jockey_from else None

        jockey_debut = html.xpath('//th[contains(text(), "デビュー年")]/following-sibling::td')[0].text
        jockey_debut = jockey_debut.split('(')[0] if '-' not in jockey_debut else None

        result = {
            "jockey_id": html_path.stem,
            "jockey_birth_date": html.xpath('//p[@class="txt_01"]')[0].text.split()[0],
            "jockey_height": height,
            "jockey_from": jockey_from[0] if jockey_from else None,
            "jockey_blood_type": jockey_from[1] if jockey_from and len(jockey_from) == 2 else None,
            "jockey_debut": jockey_debut
        }
        return [result]


if __name__ == '__main__':
    input_html_dir = "D:/netkeiba/html_data/jockey_profile/"
    # スクレイピング結果csvの出力先パス
    output_csv_path = "D:/netkeiba/csv_data/jockey_profile.csv"

    # race_scraper.pyの取得範囲と合わせる
    JockeyProfileScraper(input_html_dir, output_csv_path)
