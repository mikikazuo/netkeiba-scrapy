import pandas as pd
from tqdm import tqdm

import mypath
from analysis.mylib.general import *


class GenerateOrderCnt:
    """
    順位カウント（フィルターなし）
    """

    def __init__(self, df, grouped_df):
        self.df = df
        self.col_total_cnt = "race_cnt"
        self.df[self.col_total_cnt] = 0
        self.df[self.col_total_cnt] = self.df[self.col_total_cnt].astype("uint8")
        self.grouped_df = grouped_df

        self.col_tuple = lambda target_order: {'cnt': f"order_{target_order + 1}_cnt",
                                               'nor': f"order_{target_order + 1}_cnt_nor"}

    def set_race_cnt(self, data):
        """
        過去のレース数カラムの追加
        """
        self.df.loc[self.df["horse_id"] == data[0], self.col_total_cnt] = list(reversed(range(0, len(data[1]))))

    def set_order_cnt(self, data):
        """
        過去の上位順位回数カラムの追加
        """
        order_cnt = [[0], [0], [0]]  # 上位順位回数の遷移（最初は必ず０と分かっているため事前初期化）
        # 対象レース以前の結果を使うため最後が不要 iloc[:0...　としている
        for order in data[1]["order"].iloc[:0:-1]:
            for target_order in range(len(order_cnt)):
                cnt = order_cnt[target_order][0]
                if order == target_order + 1:  # 対応する順位が見つかった時(リストのインデックスにも使っているため +1している)
                    cnt += 1
                order_cnt[target_order].insert(0, cnt)

        for target_order in range(len(order_cnt)):
            self.df.loc[self.df["horse_id"] == data[0], self.col_tuple(target_order)['cnt']] = order_cnt[target_order]

    def normalize(self):
        """
        過去の順位回数の正規化
        """
        for target_order in range(3):
            cnt_column, nor_column = self.col_tuple(target_order).values()
            self.df[nor_column] = self.df[cnt_column] / self.df[self.col_total_cnt].astype("float64")
            self.df = self.df.drop(cnt_column, axis=1)
            # 0/0の時にNanとなるため0に置き換え
            self.df[nor_column] = self.df[nor_column].fillna(0)
        # 指定順位以上を集計
        for target_order in range(3 - 1):
            self.df[self.col_tuple(target_order + 1)['nor']] += self.df[self.col_tuple(target_order)['nor']]

    def set_cnt(self):
        """
        過去の上位順位回数＆レース総数カラムの追加
        """
        for cnt_data in tqdm(self.grouped_df):
            self.set_race_cnt(cnt_data)
            self.set_order_cnt(cnt_data)
        self.normalize()
        return self.df


class GenerateFilterCnt:
    """
    順位カウント（フィルター版）
    """

    def __init__(self, df, grouped_df, filter_col, filter_dict):
        self.df = df
        self.grouped_df = grouped_df
        # 順位取得前のフィルタカラム
        self.filter_col = filter_col
        self.filter_dict = filter_dict

        self.col_total_cnt = lambda filter_state: f"{self.filter_col}_{filter_state}_cnt"
        self.col_tuple = lambda filter_state, target_order: {
            'cnt': f"{self.filter_col}_{filter_state}_order_{target_order + 1}_cnt",
            'nor': f"{self.filter_col}_{filter_state}_order_{target_order + 1}_cnt_nor"}

    def normalize(self):
        """
        正規化
        """
        for filter_state in self.filter_dict.values():
            for target_order in range(3):
                cnt_column, nor_column = self.col_tuple(filter_state, target_order).values()
                self.df[nor_column] = self.df[cnt_column] / self.df[self.col_total_cnt(filter_state)].astype("float64")
                self.df = self.df.drop(cnt_column, axis=1)
                # 0/0の時にNanとなるため0に置き換え
                self.df[nor_column] = self.df[nor_column].fillna(0)
            # 指定順位以上を集計
            for target_order in range(3 - 1):
                self.df[self.col_tuple(filter_state, target_order + 1)['nor']] += self.df[
                    self.col_tuple(filter_state, target_order)['nor']]
        return self.df

    def change_astype(self):
        for key, filter_state in self.filter_dict.items():
            self.df[self.col_total_cnt(filter_state)] = self.df[self.col_total_cnt(filter_state)].astype('uint8')

    def set_cnt(self):
        """
        過去の上位順位回数＆レース総数カラムの追加
        """

        def add_latest_cnt(cnt, is_match):
            """
            :param cnt: 最新のカウント値
            :param is_match: 条件フィルタ
            """
            cnt.insert(0, (cnt[0] + 1) if is_match else cnt[0])

        for data in tqdm(self.grouped_df):
            race_cnt = {}
            order_cnt = {}
            for key in self.filter_dict:
                # レース総数
                race_cnt[key] = [0]
                # 上位順位回数の遷移（最初は必ず０と分かっているため事前初期化）
                order_cnt[key] = [[0], [0], [0]]

            target_col = ["order"] + [self.filter_col]
            # 対象レース以前の結果を使うため最後が不要 iloc[:0...　としている
            for idx, d in data[1][target_col].iloc[:0:-1].iterrows():
                for key in self.filter_dict:
                    is_filter_match = d[self.filter_col] == key
                    add_latest_cnt(race_cnt[key], is_filter_match)

                    # 順位検証
                    filtered_order_cnt = order_cnt[key]
                    for target_order in range(3):
                        add_latest_cnt(filtered_order_cnt[target_order],
                                       is_filter_match and d['order'] == target_order + 1)

            # カウントの反映
            for key, filter_state in self.filter_dict.items():
                self.df.loc[self.df["horse_id"] == data[0], self.col_total_cnt(filter_state)] = race_cnt[key]
                for target_order in range(3):
                    self.df.loc[self.df["horse_id"] == data[0], self.col_tuple(filter_state, target_order)['cnt']] = \
                        order_cnt[key][target_order]

        self.normalize()
        self.change_astype()
        return self.df


class HorseProcessing(DataframeProcessing):
    def __init__(self):
        # 海外のレースが含まれない範囲の場合、int型になってしまうため手動でstr化 ex.2019J0033009
        self.df = pd.read_csv(mypath.horse_csv, dtype={'race_id': str})

        # 不要列の削除
        self.df = self.df.drop(["horse_name", "sell_price", "maker_name", "jockey", "reward"], axis=1)
        # 不要行の削除
        # TODO 中央競馬のみに絞ればここで弾く必要もなくなるのでは？ただその場合過去参照でレースが飛ぶ場合が発生する
        self.df = self.df.dropna(subset=["order", "horse_weight", "pace", "nobori", "horse_num"])

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

        self.df['popularity'] = self.df['popularity'].fillna('-1')

        # TODO sell_priceが空のパターンがないことを確認したのち追加  rewardは現状すべて０
        self.change_type(["birth_date", "race_month", "horse_num", "wakuban", "umaban",
                          "popularity", "order", "add_horse_weight", "order_of_corners"], "int8")
        self.change_type(["length", "horse_weight"], "int16")

        # TODO rewardの桁数足りないが大丈夫か horse_data.dfList.reward.map(float).max()
        # jockey_weightは端数(0.5)ありのためこっち
        self.change_type(["odds", "time", "diff_from_top", "nobori", "jockey_weight", "pace_start", "pace_goal"],
                         "float64")

        #self.df["order"] = self.df["horse_num"] - self.df["order"]
        # 順位の標準化
        self.df["order"] = ((self.df["horse_num"] - self.df["order"]) / (self.df["horse_num"] - 1)).astype("float64")

        # 名前は存在するがリンク先idがないパターン ex.2019190004
        self.df['maker_id'] = self.df['maker_id'].fillna('None')
        self.change_type(
            ["race_name", "from", "venue", "weather", "race_type", "race_condition", "maker_id", "color"], "category")

        # 加工カラムの追加
        print('race count adding')
        grouped_df = [[_name, _df] for _name, _df in self.df.groupby("horse_id")]
        self.df = GenerateOrderCnt(self.df, grouped_df).set_cnt()
        # self.df = GenerateFilterCnt(self.df, grouped_df, 'race_condition',
        #                             {'良': 'good', '稍': 'normal', '重': 'bad', '不': 'poor'}).set_cnt()
        # self.df = GenerateFilterCnt(self.df, grouped_df, 'weather',
        #                             {'晴': 'sunny', '曇': 'cloudy', '小雨': 'litrainy', '雨': 'rainy',
        #                              '小雪': 'litsnowy', '雪': 'snowy'}).set_cnt()

        self.df = self.df.set_index(["race_id", "horse_id"])