import pandas as pd

import mypath
from analysis.mylib.general import *


class PillarProcessing(DataframeProcessing):
    # 参照過去数　最大5
    past_max = 5

    def __init__(self):
        print('pillar start')
        # 海外のレースが含まれない範囲の場合、int型になってしまうため手動でstr化 ex.2019J0033009
        self.df = pd.read_csv(mypath.pillar_csv, dtype={'race_id': str})
        self.change_type([f'run_type'], 'int8')

        for i in range(self.past_max + 1, 6):
            for column in self.df.columns:
                if str(i) in column:
                    self.df = self.df.drop(column, axis=1)

        # 馬柱のページでは順位が分からない場合がある　⇒　本当はレースページから取得した方がよい
        for i in range(1, self.past_max + 1):
            self.df[f'order_{i}'] = self.df[f'order_{i}'].replace('除', -100).replace('中', -100) \
                .replace('取', -100).replace('降', -100).replace('失', -100)

            # 空白埋め １月をnull時の値としてしまっている
            self.df[f'race_date_{i}'] = self.df[f'race_date_{i}'].fillna('1900.01.01')
            self.df[f'time_{i}'] = self.df[f'time_{i}'].fillna('0:0')
            # タイムにコロン(:)がないパターンがあるため修正 人的表記ミス ex.201901010311 チャンピオ
            self.df[f'time_{i}'] = self.df[f'time_{i}'].map(lambda x: x.replace('.', ':', 1) if ':' not in x else x)

            # 後々ハイフンで分割するため負の数はNG
            self.df[f'order_of_corners_{i}'] = self.df[f'order_of_corners_{i}'].fillna('0')
            # 通常で-1が起こりうるため極端にマイナスにした
            self.df[f'add_horse_weight_{i}'] = self.df[f'add_horse_weight_{i}'].fillna(-100)

            for column in ['order', 'length', 'horse_num', 'umaban', 'popularity', 'jockey_weight', 'nobori',
                           'horse_weight', 'diff_from_top']:
                self.df[column + f'_{i}'] = self.df[column + f'_{i}'].fillna(-1)
            for column in ['venue', 'race_name', 'kakko', 'race_type', 'race_condition', 'jockey']:
                self.df[column + f'_{i}'] = self.df[column + f'_{i}'].fillna('None')

            self.df[f'race_date_{i}'] = pd.to_datetime(self.df[f'race_date_{i}'], format='%Y.%m.%d')
            self.df[f'race_month_{i}'] = self.df[f'race_date_{i}'].map(lambda x: x.month)

            time_list = self.df[f'time_{i}'].str.split(':')
            time_list = time_list.map(lambda x: list(map(float, x)))
            self.df[f'time_{i}'] = time_list.map(lambda x: x[0] * 60 + x[1])

            corner_list = self.df[f'order_of_corners_{i}'].str.split('-')
            self.df[f'order_of_corners_{i}'] = corner_list.map(lambda x: list(map(int, x)))
            self.df[f'order_of_corners_{i}'] = self.df[f'order_of_corners_{i}'].map(lambda x: x[0] - x[-1])

            self.change_type([f'race_month_{i}', f'order_{i}', f'horse_num_{i}', f'umaban_{i}',
                              f'popularity_{i}', f'order_of_corners_{i}', f'add_horse_weight_{i}'], 'int8')
            self.change_type([f'length_{i}', f'horse_weight_{i}'], 'int16')
            self.change_type([f'time_{i}', f'jockey_weight_{i}', f'nobori_{i}', f'diff_from_top_{i}'], 'float64')

            self.df[f'speed_{i}'] = self.df[f'length_{i}'] / self.df[f'time_{i}']
            # 未登録の場合（length_{i}が-1でtime_{i}が0）のときinf、（length_{i}が正常値でtime_{i}が取得不能を表す0）のときinfとなるため置き換える
            # なお、infを変えても結果は特に変わらなかった
            self.df[f'speed_{i}'] = self.df[f'speed_{i}'].replace(-np.inf, -1).replace(np.inf, -1)

            # 順位の標準化
            self.df[f'order_nor_{i}'] = (self.df[f'order_{i}'] - 1) / (self.df[f'horse_num_{i}'] - 1).astype('float64')
            self.df = self.df.drop(f'order_{i}', axis=1)

            self.change_type([f'venue_{i}', f'race_name_{i}', f'kakko_{i}', f'outside_{i}', f'race_type_{i}',
                              f'race_condition_{i}', f'jockey_{i}'], 'category')

            if not DataframeProcessing.is_human:
                self.df = self.df.drop(f'popularity_{i}', axis=1)

        self.df = self.df.set_index(['race_id', 'horse_id'])

    def update_race_date(self, merged_df_cp):
        """
        日付差へ更新
        """
        print('pillar_data.update_race_date')
        # 不要レース馬柱一式の削除
        index_list = merged_df_cp[merged_df_cp["race_date_1"].isnull()]["race_date_1"].index.map(lambda x: x[0])
        merged_df = merged_df_cp.drop(index_list)
        # 馬柱で欠けているパターンがある（取得データが2009年からの場合） ex.201005050810 馬番12
        for i in range(1, self.past_max + 1):
            merged_df[f'race_date_{i}'] = (merged_df["race_date"] - merged_df[f'race_date_{i}']).map(
                lambda x: x.days).astype("int16")
        return merged_df
