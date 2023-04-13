import pandas as pd

import mypath
from analysis.mylib.general import *


class JockeyProfileProcessing(DataframeProcessing):
    def __init__(self):
        # 地方競馬メインの騎手だとアルファベットが入りstr型になるが中央のみの場合int型になるためstrで明示
        self.df = pd.read_csv(mypath.jockey_profile_csv, dtype={'jockey_id': object})

        self.df[f'jockey_height'] = self.df[f'jockey_height'].fillna('-1')
        self.df[f'jockey_from'] = self.df[f'jockey_from'].fillna('None')
        self.df[f'jockey_blood_type'] = self.df[f'jockey_blood_type'].fillna('None')
        self.df[f'jockey_debut'] = self.df[f'jockey_debut'].fillna('-10000')

        self.df["jockey_birth_date"] = pd.to_datetime(self.df["jockey_birth_date"], format="%Y/%m/%d")
        self.df["jockey_birth_month"] = self.df["jockey_birth_date"].map(lambda x: x.month)
        self.df["jockey_height"] = self.df["jockey_height"].str.replace('cm', '')
        self.df["jockey_debut"] = self.df["jockey_debut"].str.replace('年', '')

        self.change_type(['jockey_birth_month', 'jockey_height'], "uint8")
        self.change_type(['jockey_debut'], "int16")

        self.change_type(['jockey_from', 'jockey_blood_type'], "category")

        self.df = self.df.set_index(["jockey_id"])

    def update_date(self, merged_df):
        """
        日付差へ更新
        """
        merged_df['jockey_age'] = (merged_df['race_date'] - merged_df['jockey_birth_date']).map(
            lambda x: x.days / 365).astype('int8')

        merged_df['jockey_debut'] = merged_df['race_date'].map(lambda x: x.year) - merged_df['jockey_debut'].astype(
            'int16')
        merged_df['jockey_debut'] = merged_df['jockey_debut'].map(lambda x: -1 if x < 0 else x).astype('int8')

        merged_df["jockey_birth_date"] = self.df["jockey_birth_date"].map(lambda x: x.month).astype('int8')