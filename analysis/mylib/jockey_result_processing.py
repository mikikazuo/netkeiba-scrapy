import pandas as pd

import mypath
from analysis.mylib.general import *


class JockeyResultProcessing(DataframeProcessing):
    yoso_columns = []

    def __init__(self):
        print('jockey result start')
        # 海外のレースが含まれない範囲の場合、int型になってしまうため手動でstr化 ex.2019J0033009
        self.df = pd.read_csv(mypath.jockey_result_csv, dtype={'jockey_id': str}, index_col='jockey_id')
        # 不要行の削除 年度は端っこなので合計値の算出には特に影響しない　ex.00525
        self.df = self.df.dropna(subset=["jockey_result_order_1_cnt"])

        self.float_column = ["order_1_nor", "order_1_2_nor", "order_1_2_3_nor", "prize"]
        self.float_column = [f"jockey_result_{column}" for column in self.float_column]

        self.change_type(list(set(self.df.columns) - set(self.float_column)), "int16")

        self.df["jockey_result_prize"] = self.df["jockey_result_prize"].str.replace(',', '')
        self.change_type(["jockey_result_prize"], "float64")

    def merge(self, merged_df):
        """
        昨年成績データの抽出と結合
        """
        print('jockey_result_profile.merge')
        df_list = []
        for index, row in merged_df[['jockey_id', 'race_date']].iterrows():
            jockey_filtered = self.df[self.df.index == row['jockey_id']]
            date_filtered = jockey_filtered[jockey_filtered['jockey_result_year'] == row['race_date'].year - 1]
            # デビュー年前だとデータがないため0で埋めて仮で作成 ex.05619であれば2021年度分がない
            if date_filtered.empty:
                date_filtered = self.df[0:1]
                date_filtered.index = [row['jockey_id']]  # 前行で[0:1]の範囲で拾ってるため１行だとしてもリストにする
                date_filtered.iloc[0] = 0
                date_filtered.loc[row['jockey_id'], 'jockey_result_year'] = row['race_date'].year - 1
            df_list.append(date_filtered)
        picked_df = pd.concat(df_list)

        for column in ['grand', 'special', 'flat', 'grass', 'dirt']:
            picked_df[f'jockey_result_{column}_order_1_cnt'] /= picked_df[f'jockey_result_{column}_cnt']
            # 0/0の時にNanとなるため0に置き換え
            picked_df[f'jockey_result_{column}_order_1_cnt'] = picked_df[f'jockey_result_{column}_order_1_cnt'].fillna(
                0)

        # 不要列の削除
        picked_df = picked_df.drop(["jockey_result_year"], axis=1)

        picked_df.index = merged_df.index
        return pd.concat([merged_df, picked_df], axis=1)
