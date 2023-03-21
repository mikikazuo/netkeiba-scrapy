import pandas as pd

import mypath


# （注意）cudf上でdf.loc[<horse_id>,<race_id>]で取得する場合、
# horseDataと違いマルチインデックスがhorse_idでまとめられていないため毎回行順序がバラバラ
# horseDataでも<horse_id>ではなく<race_id>で取得した場合は順序がバラバラ
class RaceProcessing:
    def change_type(self, columns, to_type):
        for col in columns:
            self.df[col] = self.df[col].astype(to_type)

    def __init__(self):
        # １０万件でおおよそ4年くらいのレースが対象になる　２０万が限界 2past
        self.df = pd.read_csv(mypath.race_csv)

        # 不要列の削除
        self.df = self.df.drop(["owner", "trainer"], axis=1)

        time_list = self.df["start_time"].str.split(":")
        time_list = time_list.map(lambda x: list(map(float, x)))
        self.df["start_time"] = time_list.map(lambda x: x[0] * 60 + x[1])
        self.df["outside"] = time_list.map(lambda x: 1 if x == "True" else 0)
        self.change_type(["start_time"], "int16")

        self.change_type(["age", "outside"], "int8")

        self.change_type(["sex", "tresen", "trainer_id", "owner_id", "turn"], "category")

        # horse_processing.pyで取得される海外レースのidに英語が含まれていて自動的にstr型になっている。
        # マージでインデックス型を合わせるために変換 ex 2019J0033009
        self.change_type(["race_id"], "str")
        self.df = self.df.set_index(["race_id","horse_id"])
