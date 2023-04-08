import pandas as pd
from tqdm import tqdm

import mypath
from analysis.mylib.general import *


class YosoProcessing(DataframeProcessing):
    yoso_columns = []

    def __init__(self):
        # 海外のレースが含まれない範囲の場合、int型になってしまうため手動でstr化 ex.2019J0033009
        self.df = pd.read_csv(mypath.yoso_csv, dtype={'race_id': str}, index_col=["race_id", "horse_id"])

        print(f"予想家index: {self.df['yosoka'].unique()}")
        merged_df = None
        for index, yosoka in enumerate(self.df['yosoka'].unique()):
            filtered_yosoka_df = self.df.loc[self.df['yosoka'] == yosoka]
            filtered_yosoka_df = filtered_yosoka_df.drop('yosoka', axis=1)
            filtered_yosoka_df = filtered_yosoka_df.rename(columns={'yoso': f'yoso_{index + 1}'})
            self.yoso_columns.append(f'yoso_{index + 1}')
            merged_df = filtered_yosoka_df if merged_df is None else merged_df.merge(filtered_yosoka_df,
                                                                                     on=["race_id", "horse_id"],
                                                                                     how='outer')
        self.df = merged_df

    def categorize(self, merged_df):
        """
        元々予想家がいなかったのか外れ予想なのかを区別し、dtypeを変更する
        """
        print('yoso categorizing')
        for race_id, df in tqdm(merged_df.groupby("race_id")):
            for column in self.yoso_columns:
                merged_df.loc[race_id, column] = df[column].fillna(
                    'None' if merged_df.loc[race_id, column].isnull().all() else 'Hazure')

        for col in self.yoso_columns:
            merged_df[col] = merged_df[col].astype("category")
