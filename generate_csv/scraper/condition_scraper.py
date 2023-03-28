import re

from generate_csv import mylib


class ConditionScraper(mylib.Scraper):
    def scrape_from_page(self, html_path):
        html = mylib.read_html(html_path)

        result_table_rows = html.xpath('//tr[contains(@class,"HorseList")]')
        result_all = []

        for result_table_row in result_table_rows:
            rank = result_table_row.xpath('td/span[@class="Value"]')

            race_id = html_path.stem
            horse_id = \
                re.findall('horse_id=(.*)&race_id', result_table_row.xpath('td/dl/dt[@class="Horse"]/a/@href')[0])[0]
            # horse_scraperでcondition(馬場状態)が使われているので注意
            # 過去データ欠けるパターンがある　ex.202306020701
            if len(rank) > 1:
                result = {
                    "race_id": race_id,
                    "horse_id": horse_id,
                    "condition_score": int(result_table_row.xpath('td/span[@class="Value_Num"]')[0].text),
                    # ハイフンがある場合を弾く
                    "condition_score_past": [int(past.text) for past in
                                             result_table_row.xpath('td/span[@class="Data03"]') if past.text.isdigit()],
                    "condition_rank": re.sub(r"\D", "", rank[0].text),
                    "rise_rank": re.sub(r"\D", "", rank[1].text) if rank[1].text else -1  # -1の場合は「初」
                }
            # データがそもそもないパターンがある ex.2019J003300
            # ただ、過去データが残ってるパターンもある ex.201805010601
            else:
                result = {
                    "race_id": race_id,
                    "horse_id": horse_id,
                    "condition_score": -1,
                    "condition_score_past": [int(past.text) for past in
                                             result_table_row.xpath('td/span[@class="Data03"]') if past.text.isdigit()],
                    "condition_rank": -1,
                    "rise_rank": -1
                }

            result_all.append(result)
        return result_all


if __name__ == '__main__':
    input_html_dir = "D:/netkeiba/html_data/condition/"
    # スクレイピング結果csvの出力先パス
    output_csv_path = "D:/netkeiba/csv_data/condition2.csv"

    # race_scraper.pyの取得範囲と合わせる
    ConditionScraper(input_html_dir, output_csv_path, (2017, 2030))
