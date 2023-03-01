"""
地方競馬のレースもスクレイピングされるので注意 ex.2018100059
"""
import re

import pandas as pd

from generate_csv import mylib
from netkeiba.netkeiba.spiders import mylib as crawl_mylib


def scrape_from_page(horse_html_path):
    html = mylib.read_html(horse_html_path)

    result_table_rows = html.xpath('//*[@id="contents"]/div[5]/div/table//tr[not(contains(@align, "center"))]')
    horse_result_all = []

    for result_table_row in result_table_rows:
        # 馬名が英語の場合がある ex 2012190002
        xpath_base = '//*[@id="db_main_box"]/div[1]/div[1]/div[1]/'
        horse_name = html.xpath(xpath_base + "h1/text()")
        horse_name = (
            horse_name[0].strip() if len(horse_name) else html.xpath(xpath_base + 'p[@class="eng_name"]/text()')[0])

        sell_price = html.xpath('//*[text() = "セリ取引価格"]/following-sibling::td')[0].text
        if "円" not in sell_price:
            sell_price = None

        # 生産者名のタグ構造が異なるパターンがある ex2000190013
        maker_name = html.xpath('//*[text() = "生産者"]/following-sibling::td/a')
        maker_name = (
            maker_name[0].text if len(maker_name) else html.xpath('//*[text() = "生産者"]/following-sibling::td')[0].text)
        # 生産者のidが存在しないパターンがある、あとtdタグになってる ex 2012190003
        maker_id = html.xpath('//*[text() = "生産者"]/following-sibling::td/a/@href')
        maker_id = crawl_mylib.get_last_slash_word(maker_id[0]) if maker_id else None

        # 空欄や「中」止のパターンがある ex.2018100059
        order = result_table_row.xpath("td[12]")[0].text
        if order:
            order = re.sub(r"\D", "", order)  # (降)の除去 ex.2015103057

        input_jockey = result_table_row.xpath("td[13]/a")
        jockey = (input_jockey[0].text if len(input_jockey) else result_table_row.xpath("td[13]")[0].text.strip())

        reward = result_table_row.xpath("td[28]")[0].text
        if result_table_row.xpath("td[28]")[0].text == "\xa0":
            reward = None

        horse_weight = result_table_row.xpath("td[24]")[0].text.split(r"(")
        horse_result = {
            "horse_id": horse_html_path.stem,
            "race_id": crawl_mylib.get_last_slash_word(result_table_row.xpath("td[5]/a/@href")[0]),  # 数字以外の文字を削除
            "horse_name": horse_name,  # stripを使う場合はtext()をxpathに埋め込む必要がある
            "birth_date": html.xpath('//*[@id="db_main_box"]/div[2]/div/div[2]/table//tr[1]/td')[0].text,
            "maker_name": maker_name,
            "maker_id": maker_id,
            "from": html.xpath('//*[text() = "産地"]/following-sibling::td')[0].text,
            "sell_price": sell_price,
            "race_date": result_table_row.xpath("td[1]/a")[0].text.replace("/", "-"),
            "venue": result_table_row.xpath("td[2]/a")[0].text,
            "weather": result_table_row.xpath("td[3]")[0].text,
            "race_name": result_table_row.xpath("td[5]/a")[0].text,
            "horse_num": result_table_row.xpath("td[7]")[0].text,
            "wakuban": result_table_row.xpath("td[8]")[0].text,
            "umaban": result_table_row.xpath("td[9]")[0].text,
            "odds": result_table_row.xpath("td[10]")[0].text,
            "popularity": result_table_row.xpath("td[11]")[0].text,
            "order": order,
            "jockey": jockey,
            "jockey_id": crawl_mylib.get_last_slash_word(result_table_row.xpath("td[13]/a/@href")[0]) if len(
                input_jockey) else None,
            "weight": result_table_row.xpath("td[14]")[0].text,
            "type": result_table_row.xpath("td[15]")[0].text[0],  # 障害レースは芝しかないっぽい
            "length": result_table_row.xpath("td[15]")[0].text[1:],
            "condition": result_table_row.xpath("td[16]")[0].text,
            "time": result_table_row.xpath("td[18]")[0].text,
            "diff_from_top": result_table_row.xpath("td[19]")[0].text,
            "order_of_corners": result_table_row.xpath("td[21]")[0].text,
            "pace": result_table_row.xpath("td[22]")[0].text,
            "nobori": result_table_row.xpath("td[23]")[0].text,
            "horse_weight": horse_weight[0] if len(horse_weight) >= 2 else None,
            "add_horse_weight": horse_weight[1][:-1] if len(horse_weight) >= 2 else None,
            "reward": reward
        }
        mylib.delete_space(horse_result)
        horse_result_all.append(horse_result)
    return horse_result_all


if __name__ == '__main__':
    input_html_dir = "D:/netkeiba/html_data/horse/"
    # スクレイピング結果csvの出力先パス
    output_csv_path = "D:/netkeiba/csv_data/horse.csv"

    # race_scraper.pyで作成したスクレイピングcsv
    input_csv_path = 'D:/netkeiba/csv_data/race.csv'
    # race_scraper.pyでの取得開始年度
    # この年度以降のレースに出場した馬を取得する
    start_year = 2018

    horse_id_df = pd.read_csv(input_csv_path, dtype={"horse_id": str, "race_id": str})
    horse_id_list = list(
        sorted(set(horse_id_df.loc[horse_id_df["race_id"] >= str(start_year) + '00000000', :]['horse_id'])))

    mylib.Scraper(input_html_dir, output_csv_path, scrape_from_page, horse_id_list)
