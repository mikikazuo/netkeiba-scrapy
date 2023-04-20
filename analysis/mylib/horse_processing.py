import pandas as pd
from tqdm import tqdm

import mypath
from analysis.mylib.general import *


class HorseProcessing(DataframeProcessing):
    def set_race_cnt(self, data):
        """
        過去のレース数カラムの追加
        """
        self.df.loc[self.df["horse_id"] == data[0], "race_cnt"] = list(reversed(range(0, data[1])))

    def set_order_cnt(self, data):
        """
        過去の上位順位回数カラムの追加
        """
        order_cnt = [[0], [0], [0]]  # 上位順位回数の遷移（最初は必ず０と分かっているため事前初期化）

        # 対象レース以前の結果を使うため最後が不要 iloc[:0...　としている
        for order in self.df.loc[self.df["horse_id"] == data[0], "order"].iloc[:0:-1]:
            for target_order in range(len(order_cnt)):
                cnt = order_cnt[target_order][0]
                if order == target_order + 1:  # 対応する順位が見つかった時(リストのインデックスにも使っているため +1している)
                    cnt += 1
                order_cnt[target_order].insert(0, cnt)

        for target_order in range(len(order_cnt)):
            self.df.loc[self.df["horse_id"] == data[0], "order_" + str(target_order + 1) + "_cnt"] = order_cnt[
                target_order]

    def set_order_cnt_normalize(self):
        """
        過去の順位回数の正規化
        """
        for target_order in range(1, 4):
            cnt_column = "order_" + str(target_order) + "_cnt"
            self.df["order_" + str(target_order) + "_cnt_normalize"] = self.df[cnt_column] / self.df["race_cnt"].astype(
                "float64")
            self.df = self.df.drop(cnt_column, axis=1)

        # 指定順位以上を集計
        self.df["order_2_cnt_normalize"] += self.df["order_1_cnt_normalize"]
        self.df["order_3_cnt_normalize"] += self.df["order_2_cnt_normalize"]

    def __init__(self):
        # 海外のレースが含まれない範囲の場合、int型になってしまうため手動でstr化 ex.2019J0033009
        self.df = pd.read_csv(mypath.horse_csv, dtype={'race_id': str})

        # 不要列の削除
        self.df = self.df.drop(["horse_name", "sell_price", "maker_name", "jockey", "reward"], axis=1)
        # 不要行の削除
        # TODO 中央競馬のみに絞ればここで弾く必要もなくなるのでは？ただその場合過去参照でレースが飛ぶ場合が発生する
        self.df = self.df.dropna(subset=["order", "horse_weight", "pace", "nobori"])

        self.df["birth_date"] = pd.to_datetime(self.df["birth_date"], format="%Y年%m月%d日").map(lambda x: x.month)
        self.df["race_date"] = pd.to_datetime(self.df["race_date"], format="%Y/%m/%d")
        self.df["race_month"] = self.df["race_date"].map(lambda x: x.month)

        time_list = self.df["time"].str.split(":")
        time_list = time_list.map(lambda x: list(map(float, x)))
        self.df["time"] = time_list.map(lambda x: x[0] * 60 + x[1])

        corner_list = self.df["order_of_corners"].str.split("-")
        self.df["order_of_corners"] = corner_list.map(lambda x: list(map(int, x)))
        self.df["order_of_corners"] = self.df["order_of_corners"].map(lambda x: x[0] - x[-1])

        pace_list = self.df["pace"].str.split("-")
        self.df = self.df.drop(["pace"], axis=1)
        pace_list = pace_list.map(lambda x: list(map(float, x)))
        self.df["pace_start"] = pace_list.map(lambda x: x[0])
        self.df["pace_goal"] = pace_list.map(lambda x: x[1])

        # TODO sell_priceが空のパターンがないことを確認したのち追加  rewardは現状すべて０
        self.change_type(["birth_date", "race_month", "horse_num", "wakuban", "umaban",
                          "popularity", "order", "add_horse_weight", "order_of_corners"], "int8")
        self.change_type(["length", "horse_weight"], "int16")

        # TODO rewardの桁数足りないが大丈夫か horse_data.dfList.reward.map(float).max()
        # jockey_weightは端数(0.5)ありのためこっち
        self.change_type(["odds", "time", "diff_from_top", "nobori", "jockey_weight", "pace_start", "pace_goal"],
                         "float64")

        # 順位の標準化
        self.df["order_normalize"] = (self.df["order"] - 1) / (self.df["horse_num"] - 1).astype("float64")

        self.change_type(
            ["race_name", "from", "venue", "weather", "race_type", "race_condition", "maker_id", "color"],
            "category")

        # 加工カラムの追加
        self.df["race_cnt"] = 0
        self.df["race_cnt"] = self.df["race_cnt"].astype("uint8")
        cnt_data_list = [[_name, len(_df)] for _name, _df in self.df.groupby("horse_id")]

        print('race count adding')
        for cnt_data in tqdm(cnt_data_list):
            self.set_race_cnt(cnt_data)
            self.set_order_cnt(cnt_data)
        self.set_order_cnt_normalize()

        self.df = self.df.set_index(["race_id", "horse_id"])

        # set_order_cnt関数で使い終わった後で削除する
        self.df = self.df.drop("order", axis=1)
        if not self.is_human:
            self.df = self.df.drop(["popularity", "odds"], axis=1)
