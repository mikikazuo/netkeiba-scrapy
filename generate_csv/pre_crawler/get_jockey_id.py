"""
race_htmlから騎手のidを抽出する
"""

import os
import pathlib
from multiprocessing import Pool

import pandas as pd
from tqdm import tqdm

from generate_csv import mylib
from netkeiba.netkeiba.spiders import mylib as crawl_mylib


def get_all_jockey_crawled(path):
    html = mylib.read_html(path)
    result_table_rows = html.xpath('//table[@class="race_table_01 nk_tb_common"]//tr[position()>1]')
    jockey_list = []
    for result_table_row in result_table_rows:
        jockey_list.append(crawl_mylib.get_last_slash_word(result_table_row.xpath('td[7]/a/@href')[0]))
    return jockey_list


# マルチプロセスでは以下if文必要
if __name__ == '__main__':
    # レースデータのディレクトリパス
    input_html_dir = 'D:/netkeiba/html_data/race/'
    # レースデータhtmlの参照年度の指定
    # レースが最小条件で1986年1月からなので、1986年1月からにした,
    race_path_list = sum([list(pathlib.Path(input_html_dir).glob(year + '*')) for year in map(str, range(1986, 2050))],
                         [])
    # 出力する馬id一覧csvファイル
    output_csv_path = 'D:/netkeiba/csv_data/all_jockey_id.csv'

    all_jockey_set = set()
    mylib.confirm_exist_file_delete(output_csv_path)

    with Pool() as pool:
        features = []
        for i, race_path in enumerate(tqdm(race_path_list)):
            features.append(race_path)
            if i > 0 and i % os.cpu_count() == 0:
                features = pool.map(get_all_jockey_crawled, features)
                # sum関数で二次リストを一次にしたほうがfeaturesのリスト回すより早い
                all_jockey_set = all_jockey_set | set(sum(features, []))
                features = []
        features = pool.map(get_all_jockey_crawled, features)
        # 終盤端数分のレースデータ収集
        all_jockey_set = all_jockey_set | set(sum(features, []))

    all_horse_df = pd.DataFrame(all_jockey_set)
    all_horse_df.columns = ["jockey_id"]
    # 昇順で出力する
    all_horse_df = all_horse_df.sort_values("jockey_id", ascending=True)
    all_horse_df.to_csv(output_csv_path, index=False)
