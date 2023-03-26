import lightgbm as lgb
import pandas as pd
from matplotlib import pyplot as plt
from sklearn.metrics import mean_squared_error
from sklearn.model_selection import train_test_split

from analysis.mylib.general import *


class LightGbm:
    test_size = 0.1

    def training(self):
        df_train, df_val = train_test_split(self.df[[self.target_col] + self.target_columns], shuffle=False,
                                            test_size=self.test_size)
        train_y = df_train[self.target_col]
        train_x = df_train.drop(self.target_col, axis=1)

        self.val_y = df_val[self.target_col]
        self.val_x = df_val.drop(self.target_col, axis=1)

        trains = lgb.Dataset(train_x, train_y)
        valids = lgb.Dataset(self.val_x, self.val_y)

        params = {"objective": "regression", "metrics": "mae"}

        self.model = lgb.train(params, trains, valid_sets=valids, num_boost_round=1000,
                               callbacks=[
                                   lgb.early_stopping(stopping_rounds=500, verbose=True),  # early_stopping用コールバック関数
                                   lgb.log_evaluation(0)],  # コマンドライン出力用コールバック関数
                               )
        self.test_predicted = self.model.predict(self.val_x)

    # 予測値を図で確認する関数の定義
    def predictionAccuracy(self, predicted_df):
        RMSE = np.sqrt(mean_squared_error(predicted_df["true"], predicted_df["predicted"]))
        plt.figure(figsize=(7, 7))
        ax = plt.subplot(111)
        ax.scatter("true", "predicted", data=predicted_df)
        ax.set_xlabel("True Price", fontsize=20)
        ax.set_ylabel("Predicted Price", fontsize=20)
        plt.tick_params(labelsize=15)
        x = np.linspace(0, 1, 2)
        y = x
        ax.plot(x, y, "r-")
        plt.text(0.1, 0.9, "RMSE = {}".format(str(round(RMSE, 3))), transform=ax.transAxes, fontsize=15)

    def protData(self):
        lgb.plot_importance(self.model, height=0.5, figsize=(16, 12), ignore_zero=False)
        # テストデータを用いて予測精度を確認する)
        predicted_df = pd.concat([self.val_y.reset_index(drop=True), pd.Series(self.test_predicted)], axis=1)
        predicted_df.columns = ["true", "predicted"]

        self.predictionAccuracy(predicted_df)

    # ペイバック計算用の予測値を付与したレースごとにまとめたデータリスト作成、他に必要なカラム(order, umabanなど)も追加
    def makePredictDataset(self):
        df_train, self.df_predict = train_test_split(self.df[self.target_columns + ["order"]], shuffle=False,
                                                     test_size=self.test_size)
        # lightgbmの予測値カラムの追加
        self.df_predict["predict"] = self.test_predicted
        df_val_list = []
        removed_ctn = 0
        for race_id, _df in self.df_predict.groupby("race_id"):
            # 1レースにおける全馬の過去データが存在している場合だけ抽出、過去データが不足している馬がいる場合除外。
            if len(_df) == _df.iloc[0]["horse_num"]:
                df_val_list.append(_df)
            else:
                removed_ctn = removed_ctn + 1
        print(f'過去データ不足のための除外したレース数：{removed_ctn}除外 / {len(df_val_list) + removed_ctn}中')
        return df_val_list

    def __init__(self, df):
        self.pastNum = 2
        # 目的変数カラム
        self.target_col = "order_normalize"

        # 答えになってしまうカラム（レース後にわかるデータ）
        answer_col = [self.target_col] + ["time", "diff_from_top", "nobori", "order", "pace_goal", "pace_start",
                                          "order_of_corners"]

        if DataframeProcessing.is_human:
            answer_col = answer_col + ["popularity", "odds"]

        # 説明変数カラム
        self.target_columns = list(set(df.columns) - set(answer_col))

        # 過去レースとの差分日数を抽出したので用済み
        self.target_columns.remove("race_date")

        # 特例 order_normalizeがあるので不要
        # for ranker in range(self.pastNum):
        # self.target_columns.remove("order_" + str(ranker + 1))
        # self.target_columns.remove('odds_'+str(ranker+1))
        self.df = df

        self.training()
