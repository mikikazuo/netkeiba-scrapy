"""
地方競馬のレースもスクレイピングされるので注意 ex.2018100059
"""
import re

import pandas as pd

from generate_csv import mylib
from netkeiba.netkeiba.spiders import mylib as crawl_mylib


class HorseScraper(mylib.Scraper):
    def scrape_from_page(self, html_path):
        html = mylib.read_html(html_path)
        result_all = []

        # 馬名が英語の場合がある ex 2012190002
        # かつては冒頭に「〇外」がついてた。今はコメントに埋め込まれている。 ex 2019110130
        xpath_base = '//*[@id="db_main_box"]/div[1]/div[1]/div[1]/'
        horse_name = html.xpath(xpath_base + "h1/text()")
        horse_name = horse_name[0].strip() if len(horse_name) else \
            html.xpath(xpath_base + 'p[@class="eng_name"]/text()')[0]
        color = html.xpath(xpath_base + 'p[@class="txt_01"]/text()')[0].split()[-1]

        sell_price = html.xpath('//*[text() = "セリ取引価格"]/following-sibling::td')[0].text
        if "円" not in sell_price:
            sell_price = None

        # 生産者名のタグ構造が異なるパターンがある ex2000190013
        maker_name = html.xpath('//*[text() = "生産者"]/following-sibling::td/a')
        maker_name = maker_name[0].text if len(maker_name) else \
            html.xpath('//*[text() = "生産者"]/following-sibling::td')[0].text
        # 生産者のidが存在しないパターンがある、あとtdタグになってる ex 2012190003
        maker_id = html.xpath('//*[text() = "生産者"]/following-sibling::td/a/@href')
        maker_id = crawl_mylib.get_last_slash_word(maker_id[0]) if maker_id else None

        for race_row in html.xpath('//*[@id="contents"]/div[5]/div/table//tr[not(contains(@align, "center"))]'):
            # 空欄や「中」止のパターンがある ex.2018100059
            order = race_row.xpath("td[12]")[0].text
            if order:
                order = re.sub(r"\D", "", order)  # (降)の除去 ex.2015103057

            input_jockey = race_row.xpath("td[13]/a")
            jockey = input_jockey[0].text if len(input_jockey) else race_row.xpath("td[13]")[0].text.strip()

            reward = race_row.xpath("td[28]")[0].text
            if race_row.xpath("td[28]")[0].text == "\xa0":
                reward = None

            horse_weight = race_row.xpath("td[24]")[0].text.split(r"(")
            result = {
                "horse_id": html_path.stem,
                "race_id": crawl_mylib.get_last_slash_word(race_row.xpath("td[5]/a/@href")[0]),  # 数字以外の文字を削除
                "horse_name": horse_name,  # stripを使う場合はtext()をxpathに埋め込む必要がある
                "color": color,
                "birth_date": html.xpath('//*[@id="db_main_box"]/div[2]/div/div[2]/table//tr[1]/td')[0].text,
                "maker_name": maker_name,
                "maker_id": maker_id,
                "from": html.xpath('//*[text() = "産地"]/following-sibling::td')[0].text,
                "sell_price": sell_price,
                "race_date": race_row.xpath("td[1]/a")[0].text,
                "venue": re.sub(r"\d", "", race_row.xpath("td[2]/a")[0].text),
                "weather": race_row.xpath("td[3]")[0].text,
                "race_name": race_row.xpath("td[5]/a")[0].text,
                "horse_num": race_row.xpath("td[7]")[0].text,
                "wakuban": race_row.xpath("td[8]")[0].text,
                "umaban": race_row.xpath("td[9]")[0].text,
                "odds": race_row.xpath("td[10]")[0].text,
                "popularity": race_row.xpath("td[11]")[0].text,
                "order": order,
                "jockey": jockey,
                "jockey_id": crawl_mylib.get_last_slash_word(race_row.xpath("td[13]/a/@href")[0]) if len(
                    input_jockey) else None,
                "jockey_weight": race_row.xpath("td[14]")[0].text,
                "race_type": race_row.xpath("td[15]")[0].text[0],  # 障害レースは芝とダートが共存するパターンもある？ ex.201609050804
                "length": race_row.xpath("td[15]")[0].text[1:],
                "race_condition": race_row.xpath("td[16]")[0].text,
                "time": race_row.xpath("td[18]")[0].text,
                "diff_from_top": race_row.xpath("td[19]")[0].text,
                "order_of_corners": race_row.xpath("td[21]")[0].text,
                "pace": race_row.xpath("td[22]")[0].text,
                "nobori": race_row.xpath("td[23]")[0].text,
                "horse_weight": horse_weight[0] if len(horse_weight) >= 2 else None,
                "add_horse_weight": horse_weight[1][:-1] if len(horse_weight) >= 2 else None,
                "reward": reward
            }
            mylib.delete_space(result)
            result_all.append(result)
        return result_all


if __name__ == '__main__':
    input_html_dir = "D:/netkeiba/html_data/horse/"
    # スクレイピング結果csvの出力先パス
    output_csv_path = "D:/netkeiba/csv_data/horse.csv"

    # race_scraper.pyで作成したスクレイピングcsv
    input_csv_path = 'D:/netkeiba/csv_data/race.csv'

    race_df = pd.read_csv(input_csv_path, dtype={"horse_id": str, "race_id": str})
    horse_id_list = list(sorted(set(race_df['horse_id'])))

    HorseScraper(input_html_dir, output_csv_path, horse_id_list)
