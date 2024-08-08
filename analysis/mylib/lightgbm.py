import lightgbm as lgb
import optuna
import pandas as pd
from matplotlib import pyplot as plt
from sklearn.metrics import mean_squared_error
from sklearn.metrics import ndcg_score
from tqdm import tqdm

from analysis.mylib.general import *


def predict_convert_list(predict_df):
    df_val_list = []
    removed_ctn = 0
    for race_id, _df in predict_df.groupby("race_id"):
        # 1レースにおける全馬の過去データが存在している場合だけ抽出、過去データが不足している馬がいる場合除外。
        if len(_df) == _df.iloc[0]["horse_num"]:
            df_val_list.append(_df)
        else:
            removed_ctn = removed_ctn + 1
    print(f'過去データ不足のための除外したレース数：{removed_ctn}除外 / {len(df_val_list) + removed_ctn}中')
    return df_val_list


class LightGbm:
    # パラメータ改善用検証サイズ
    validation_size = 0.1
    # テストサイズ
    test_size = 0.1

    def training(self):
        def output_idx(ratio):
            """
            :param ratio: 割合
            :return: 割合一に応じて、レース単位で区切る行番号
            """
            idx = int(len(self.df) * (1 - ratio))
            _race_id = self.df.iloc[idx].name[0]
            # sort後だとget_locが使えなかったためlist型で対処
            return list(self.df.index.map(lambda x: x[0])).index(_race_id)

        def shuffle_df(target_df):
            """
            順位ソートされたままだとパラメータが改善されないため
            """
            shuffled = []
            for race_id, df in tqdm(target_df.groupby("race_id")):
                shuffled.append(df.sample(frac=1, random_state=0))
            return pd.concat(shuffled)

        def objective(trial):
            tree_learner = trial.suggest_categorical('tree_learner', ["serial", "feature", "data", "voting"])
            learning_rate = trial.suggest_float("learning_rate", 0.001, 0.2)
            max_depth = trial.suggest_int("max_depth", 5, 15)
            leaf_ratio = trial.suggest_float("leaf_ratio", 0.5, 0.9)
            min_data_in_leaf = trial.suggest_int("min_data_in_leaf", 3, 5000)
            min_gain_to_split = trial.suggest_float("min_gain_to_split", 0.0, 0.5)
            min_sum_hessian_in_leaf = trial.suggest_float("min_sum_hessian_in_leaf", 0.0001, 0.01)
            feature_fraction = trial.suggest_float("feature_fraction", 0.6, 1.0)
            bagging_fraction = trial.suggest_float('bagging_fraction', 0.01, 1.0)
            bagging_freq = trial.suggest_int("bagging_freq", 1, 1000)
            lambda_l1 = trial.suggest_int("lambda_l1", 0, 300)
            lambda_l2 = trial.suggest_int("lambda_l2", 0, 300)

            params = {
                'tree_learner': tree_learner,
                'learning_rate': learning_rate,
                'max_depth': max_depth,
                'num_leaves': int(pow(2, max_depth) * leaf_ratio),  # 1より大きく、131072より小さい必要がある
                'min_data_in_leaf': min_data_in_leaf,
                'min_gain_to_split': min_gain_to_split,
                'min_sum_hessian_in_leaf': min_sum_hessian_in_leaf,
                'bagging_fraction': bagging_fraction,
                'bagging_freq': bagging_freq,
                'lambda_l1': lambda_l1,
                'lambda_l2': lambda_l2,
                'feature_fraction': feature_fraction,
                "early_stopping_round": 30,
            }
            params.update(add_params)
            model = lgb.train(params, trains, valid_sets=[trains, valids])
            # 推論
            y_pred = model.predict(x_validation)
            # 評価
            ndcg = now_idx = 0
            for idx in y_cnt_for_study:
                ndcg += ndcg_score([y_val_for_study[now_idx:now_idx + idx]], [y_pred[now_idx:now_idx + idx]], k=3)
                now_idx += idx
            ndcg /= len(y_cnt_for_study)
            return ndcg

        validation_index = output_idx(self.validation_size + self.test_size)
        test_index = output_idx(self.test_size)

        print('テストデータシャッフル')
        train = shuffle_df(self.df[:validation_index])
        x_train, y_train = train[self.feature_cols], train[[self.target_col]]

        print('検証データシャッフル')
        validation = shuffle_df(self.df[validation_index:test_index])
        x_validation, y_validation = validation[self.feature_cols], validation[[self.target_col]]
        y_val_for_study = y_validation[self.target_col].values
        y_cnt_for_study = y_validation.groupby("race_id")[self.target_col].count().values

        test = self.df[test_index:]
        x_test, self.y_test = test[self.feature_cols], test[[self.target_col]]

        trains = lgb.Dataset(x_train, y_train, group=y_train.groupby("race_id")[self.target_col].count().values)
        valids = lgb.Dataset(x_validation, y_validation,
                             group=y_validation.groupby("race_id")[self.target_col].count().values)
        # ランキング予測
        # add_params = {
        #     'objective': 'lambdarank',
        #     "metric": "ndcg",
        #     'ndcg_eval_at': [1, 2, 3],
        #     "early_stopping_round": 30,
        #     'n_estimators': 1000,
        #     'feature_pre_filter': False,
        #     'seed': 1
        #     # gossではバギングが使えない(使う場合関連パラメータ除去が必要)
        #     # dartではearly_stoppingが使えない、必ずn_estimators回実行する
        #     # 'boosting': "dart",
        # }
        # 回帰
        add_params = {
            'boosting_type': 'gbdt',  # 勾配ブースティング
            'objective': 'regression',  # 目的関数：回帰
            'metric': 'rmse',  # 分類モデルの性能を測る指標
            'feature_pre_filter': False  # min_data_in_leafをチューニングする場合必要
        }
        self.study = optuna.create_study(direction='maximize')
        self.study.optimize(objective, n_trials=100)

        best_params = self.study.best_params
        best_params.update(add_params)
        best_params['num_leaves'] = int(pow(2, best_params['max_depth']) * best_params['leaf_ratio'])

        self.model = lgb.train(best_params, trains, valid_sets=[trains, valids])
        self.test_df = self.df[test_index:].copy()
        # lightgbmの予測値カラムの追加
        self.test_df["predict"] = self.model.predict(x_test)

    # 予測値を図で確認する関数の定義
    def predictionAccuracy(self, predicted_df):
        RMSE = np.sqrt(mean_squared_error(predicted_df["true"], predicted_df["predict"]))
        plt.figure(figsize=(7, 7))
        ax = plt.subplot(111)
        ax.scatter("true", "predict", data=predicted_df, alpha=self.plot_alpha)
        ax.set_xlabel("True Price", fontsize=20)
        ax.set_ylabel("Predicted Price", fontsize=20)
        plt.tick_params(labelsize=15)
        x = np.linspace(0, 1, 2)
        y = x
        ax.plot(x, y, "r-")
        plt.text(0.1, 0.9, "RMSE = {}".format(str(round(RMSE, 3))), transform=ax.transAxes, fontsize=15)

    def plot_data(self):
        lgb.plot_importance(self.model, height=0.5, figsize=(16, 12), ignore_zero=False)
        # テストデータを用いて予測精度を確認する)
        predicted_df = pd.concat([self.y_test.reset_index(drop=True), self.test_df["predict"].reset_index(drop=True)],
                                 axis=1)
        predicted_df.columns = ["true", "predict"]

        self.predictionAccuracy(predicted_df)

    def __init__(self, df):
        # 目的変数カラム
        self.target_col = "order"

        # 答えになってしまうカラム（レース後にわかるデータ）
        answer_col = [self.target_col] + ["time", "diff_from_top", "nobori", "pace_goal", "pace_start",
                                          "order_of_corners"]

        # payback検証用のため学習には使わない
        answer_col = answer_col + ["popularity", "odds"]

        # 説明変数カラム
        self.feature_cols = list(set(df.columns) - set(answer_col))

        # 過去レースとの差分日数を抽出したので用済み
        self.feature_cols.remove("race_date")

        self.plot_alpha = 0.01
        self.df = df
        self.training()
