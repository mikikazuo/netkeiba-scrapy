import pandas as pd

import mypath
from analysis.mylib.general import *


# （注意）cudf上でdf.loc[<horse_id>,<race_id>]で取得する場合、
# horseDataと違いマルチインデックスがhorse_idでまとめられていないため毎回行順序がバラバラ
# horseDataでも<horse_id>ではなく<race_id>で取得した場合は順序がバラバラ
class RaceProcessing(DataframeProcessing):
    def __init__(self):
        # １０万件でおおよそ4年くらいのレースが対象になる　２０万が限界 2past
        # 海外のレースが含まれない範囲の場合、int型になってしまうため手動でstr化 ex.2019J0033009。
        # マージでインデックス型を合わせる必要があるため変換 ex 2019J0033009
        self.df = pd.read_csv(mypath.race_csv, dtype={'race_id': str})

        # 不要列の削除
        self.df = self.df.drop(["owner", "trainer"], axis=1)

        time_list = self.df["start_time"].str.split(":")
        time_list = time_list.map(lambda x: list(map(float, x)))
        self.df["start_time"] = time_list.map(lambda x: x[0] * 60 + x[1])

        # 障害レースの時はNanになっている ex.202203010204
        self.df['turn'] = self.df['turn'].fillna('None')

        self.change_type(["start_time"], "int16")
        self.change_type(["age"], "int8")

        self.change_type(["sex", "tresen", "trainer_id", "owner_id", "turn", "outside"], "category")

        self.df = self.df.set_index(["race_id", "horse_id"])
