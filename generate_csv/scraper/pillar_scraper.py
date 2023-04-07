import re

from generate_csv import mylib
from netkeiba.netkeiba.spiders import mylib as crawl_mylib


class PillarScraper(mylib.Scraper):
    def scrape_from_page(self, html_path):
        html = mylib.read_html(html_path)
        result_all = []

        for horse_row in html.xpath('//tbody')[0].xpath('tr[@class="HorseList"]'):
            result = {
                "race_id": html_path.stem,
                "horse_id": crawl_mylib.get_last_slash_word(horse_row.xpath('td/div/div[@class="Horse02"]/a/@href')[0]),
                "run_type": re.findall('horse_race_type0(.)\.png',
                                       horse_row.xpath('td/div/div[@class="Horse06 fc"]/img/@src')[0])[0]
            }

            # 初期化
            past_columns = ['race_date', 'venue', 'race_name', 'order', 'kakko', 'outside', 'race_type', 'length',
                            'time', 'race_condition', 'horse_num', 'umaban', 'popularity', 'jockey', 'jockey_weight',
                            'order_of_corners', 'nobori', 'horse_weight', 'add_horse_weight', 'diff_from_top']
            for i in range(1, 6):
                for column in past_columns:
                    result[f'{column}_{i}'] = None
                result[f'outside_{i}'] = False

            for i, past_row in enumerate(horse_row.xpath('td[contains(@class,"Past")]/div')):
                idx = i + 1
                row_1 = past_row.xpath('div[@class="Data01"]/span')[0].text.split()
                result[f'race_date_{idx}'] = row_1[0]
                # 海外レースだとないパターンがある ex.201805050811 ストックホ
                result[f'venue_{idx}'] = row_1[1] if len(row_1) == 2 else None

                result[f'race_name_{idx}'] = past_row.xpath('div[@class="Data02"]/a')[0].text.strip()
                result[f'order_{idx}'] = past_row.xpath('div[@class="Data01"]/span[@class="Num"]')[0].text

                row_3 = past_row.xpath('div[@class="Data05"]')[0].text
                # 例外表記 ex.201701010110 (芝 外-内)
                kakko_list = re.findall('\((.*?)\)', row_3)
                if len(kakko_list) == 1:
                    result[f'kakko_{idx}'] = kakko_list[0]
                    result[f'outside_{idx}'] = '外' in kakko_list[0]
                row_3 = re.sub(r"\(.*?\)", "", row_3).split()
                result[f'race_type_{idx}'] = row_3[0][0]
                result[f'length_{idx}'] = re.sub(r"\D", "", row_3[0])

                if len(row_3) == 2:
                    result[f'time_{idx}'] = row_3[1]
                result[f'race_condition_{idx}'] = past_row.xpath('div[@class="Data05"]/strong')[0].text

                row_4 = past_row.xpath('div[@class="Data03"]')[0].text.split()
                result[f'horse_num_{idx}'] = re.sub(r"\D", "", row_4[0])
                result[f'umaban_{idx}'] = re.sub(r"\D", "", row_4[1])
                result[f'popularity_{idx}'] = re.sub(r"\D", "", row_4[2])
                result[f'jockey_{idx}'] = row_4[3]
                result[f'jockey_weight_{idx}'] = row_4[4]

                row_5 = past_row.xpath('div[@class="Data06"]')[0].text
                not_kakko_list = re.sub(r"\(.*?\)", "", row_5).split()
                kakko_list = re.findall('\((.*?)\)', row_5)
                # 直線だとコーナー判定は1つのみでハイフンがない ex.201704010111 邁進特別
                # 出馬中止だとコーナー表示がないが、上りは(0.0)で必ず表示される ex.201701010110 障害4歳以上未勝利
                # 海外レースだと表記がおかしい、順位がついているのに馬体重の計測ができていない
                result[f'order_of_corners_{idx}'] = not_kakko_list[0] if len(not_kakko_list) == 2 else None
                result[f'nobori_{idx}'] = kakko_list[0]
                horse_weight = re.findall('(\d\d\d)\(', row_5)
                result[f'horse_weight_{idx}'] = horse_weight[0] if horse_weight else None
                if result[f'horse_weight_{idx}']:
                    result[f'add_horse_weight_{idx}'] = kakko_list[1]
                # テキストがタグの後ろにくる場合　（参考）https://zenn.dev/hashito/articles/e47166c4a0bfd0
                result[f'diff_from_top_{idx}'] = \
                    re.findall('\((.*)\)', past_row.xpath('div[@class="Data07"]')[0].xpath("string()"))[0]
            result_all.append(result)
        return result_all


if __name__ == '__main__':
    input_html_dir = "D:/netkeiba/html_data/pillar/"
    # スクレイピング結果csvの出力先パス
    output_csv_path = "D:/netkeiba/csv_data/pillar.csv"

    # race_scraper.pyの取得範囲と合わせる
    PillarScraper(input_html_dir, output_csv_path, (2017, 2030))
