import datetime
import re

import pandas as pd
from tqdm import tqdm

import mylib
import mypath


class HorseProcessing:
    def change_type(self, columns, to_type):
        for col in columns:
            self.df[col] = self.df[col].astype(to_type)

    # 代入先cudf型のdataframeならcudfに自動変換して代入される
    def processForPandas(self, column, func):
        # map関数はpandasでないと使えないため一時的に変換
        return self.df[column].map(func)

    def set_race_cnt(self, data):
        """
        過去のレース数カラムの追加
        :param data:
        """
        self.df.loc[self.df["horse_id"] == data[0], "race_cnt"] = list(reversed(range(0, data[1])))

    def set_order_cnt(self, data):
        """
        過去の上位順位回数カラムの追加
        :param data:
        """
        order_cnt = [[0], [0], [0]]  # 上位順位回数の遷移（最初は必ず０と分かっているため事前初期化）
        for idx, order in enumerate(self.df.loc[self.df["horse_id"] == data[0], "order"].iloc[
                                    :0:-1]):  # 対象レース以前の結果を使うため最後が不要 iloc[:0...　としている
            for target_order in range(3):
                cnt = order_cnt[target_order][0]
                if order == target_order + 1:  # 対応する順位が見つかった時(リストのインデックスにも使っているため +1している)
                    cnt += 1
                order_cnt[target_order].insert(0, cnt)

        for target_order in range(3):
            self.df.loc[self.df["horse_id"] == data[0], "order_" + str(target_order + 1) + "_cnt"] = order_cnt[
                target_order]

    def set_order_cnt_normalize(self):
        """
        過去の順位回数の正規化
        """
        for target_order in range(1, 4):
            self.df["order_" + str(target_order) + "_cnt_normalize"] = (self.df["order_" + str(
                target_order) + "_cnt"] / self.df["race_cnt"]).astype("float16")
            self.df = self.df.drop("order_" + str(target_order) + "_cnt", axis=1)

    def __init__(self):
        self.df = pd.read_csv(mypath.horse_csv)

        # 不要列の削除
        self.df = self.df.drop(
            ["race_name", "horse_name", "sell_price", "maker_name", "jockey", "reward"],
            axis=1,
        )
        # 不要行の削除
        # TODO 中央競馬のみに絞ればここで弾く必要もなくなるのでは
        self.df = self.df.dropna(subset=["order", "horse_weight", "pace", "nobori"])

        self.df["birth_date"] = self.processForPandas(
            "birth_date", lambda x: datetime.datetime.strptime(x, "%Y年%m月%d日").month
        )
        self.df["race_date"] = self.processForPandas(
            "race_date", lambda x: datetime.datetime.strptime(x, "%Y-%m-%d")
        )
        self.df["race_month"] = self.processForPandas("race_date", lambda x: x.month)
        self.df["venue"] = self.processForPandas(
            "venue", lambda x: re.sub(r"\d", "", x)
        )

        timeList = self.df["time"].str.split(":")
        timeList = timeList.map(lambda x: list(map(float, x)))
        self.df["time"] = timeList.map(lambda x: x[0] * 60 + x[1])

        cornerList = self.df["order_of_corners"].str.split("-")
        self.df["order_of_corners"] = cornerList.map(
            lambda x: list(map(int, x))
        )
        self.df["order_of_corners"] = (
            self.df["order_of_corners"].map(lambda x: x[0] - x[-1])
        )

        paceList = self.df["pace"].str.split("-")
        self.df = self.df.drop(["pace"], axis=1)
        paceList = paceList.map(lambda x: list(map(float, x)))
        self.df["pace_start"] = paceList.map(lambda x: x[0])
        self.df["pace_goal"] = paceList.map(lambda x: x[1])

        # TODO sell_priceが空のパターンがないことを確認したのち追加  reward  horssenumでorderを割る  rewardは現状すべて０
        self.change_type(
            [
                "birth_date",
                "race_month",
                "horse_num",
                "wakuban",
                "umaban",
                "popularity",
                "order",
                "add_horse_weight",
                "order_of_corners",
            ],
            "int8",
        )
        self.change_type(["length", "horse_weight"], "int16")

        # TODO rewardの桁数足りないが大丈夫か horseData.dfList.reward.map(float).max()
        # weightは端数(0.5)ありのためこっち
        self.change_type(
            [
                "odds",
                "time",
                "diff_from_top",
                "nobori",
                "weight",
                "pace_start",
                "pace_goal",
            ],
            "float64",
        )
        self.df["order_normalize"] = 1 - (self.df["order"] - 1) / (self.df["horse_num"] - 1).astype("float64")
        self.change_type(["from", "venue", "weather", "type", "condition", "maker_id", "jockey_id"], "category")

        # 加工カラムの追加
        cnt_data_list = [[_name, len(_df)] for _name, _df in self.df.groupby("horse_id")]
        self.df["race_cnt"] = 0
        self.df["race_cnt"] = self.df["race_cnt"].astype("uint8")

        print('race count adding')
        for cnt_data in tqdm(cnt_data_list):
            self.set_race_cnt(cnt_data)
            self.set_order_cnt(cnt_data)
        self.set_order_cnt_normalize()

        # 海外のレースが含まれない範囲の場合、int型になってしまうため手動でstr化 ex.2019J0033009
        self.change_type(["race_id"], "str")
        self.df = self.df.set_index(["race_id", "horse_id"])

        if not mylib.is_human:
            self.df = self.df.drop(["popularity", "odds"], axis=1)
