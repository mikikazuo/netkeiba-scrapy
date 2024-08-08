import optuna
import itertools


def check_stable(ranker, higher_rank_df, need_predict_margin_list):
    """
    予測値の確度が高いかどうかの検証(不採用)
    """
    predict_margin_list = [abs(higher_rank_df["predict"].iloc[i] - higher_rank_df["predict"].iloc[i + 1])
                           for i in range(3)]

    if isinstance(ranker, int):
        # １着との差
        diff_top = predict_margin_list[0]
        if ranker == 0:  # １着予想の場合、2着候補と（テスト：3着候補と）のマージンが大きい場合True
            if diff_top > need_predict_margin_list[0] and \
                    diff_top + predict_margin_list[1] > need_predict_margin_list[1]:
                return True
        else:
            for i in range(1, ranker):
                diff_top += predict_margin_list[i]
            # 2着の予想の場合、1着候補とのマージンが小さい場合かつ3着候補とのマージンが大きい場合はTrue
            # 3着の予想の場合、1着候補とのマージンが小さい場合かつ4着候補とのマージンが大きい場合はTrue（1着との差なので注意）
            if diff_top < need_predict_margin_list[0] and predict_margin_list[ranker] > \
                    need_predict_margin_list[1]:
                return True
    elif isinstance(ranker, list):
        pass
    return False


def print_result(headline, top, bottom):
    return f"{headline}: {top}/{bottom}  {top / bottom * 100}%"


class TicketRule:
    """
    is_fix 順序必須かどうか
    order_sum 順序数
    """

    def __init__(self, ticket_type):
        """
          :param ticket_type: 馬券種
        """
        if ticket_type in ['tanshou', 'fukushou']:
            self.is_fix = False
            self.order_sum = 1
        elif ticket_type in ['wakuren', 'umaren', 'wide']:
            self.is_fix = False
            self.order_sum = 2
        elif ticket_type == 'umatan':
            self.is_fix = True
            self.order_sum = 2
        elif ticket_type == 'sanrenpuku':
            self.is_fix = False
            self.order_sum = 3
        elif ticket_type == 'sanrentan':
            self.is_fix = True
            self.order_sum = 3


class Monetize:
    """
    [payback_dataの扱い]
    キーがstr型なので各々で加工して使う
    """

    def get_payback_dict(self, df, ticket_type):
        """
        ペイバック読み込み
        """
        return self.df_payback.loc[df.index.get_level_values("race_id")[0]][ticket_type]

    def getmax_rev(self, df, target_col="predict", getmin=False, top_limit=4):
        """
        上位のindexを取得
        参考　https://qiita.com/nkay/items/3a1252311d5c258484d4
        :param df
        :param target_col 大小チェック対象カラム
        :param getmin: 少ないほうをとるのかどうか
        :param top_limit: 取得数
        """
        return df.nsmallest(top_limit, target_col) if getmin else df.nlargest(top_limit, target_col)

    def print_result(self, ranker, win_count, sum_payback, sum_race):
        # self.df_predict前半は閾値チューニングで使用済み
        half_idx = int(len(self.df_predict) / 2)
        print(f'---------{ranker}({sum_race}/{len(self.df_predict[half_idx:])})---------')
        try:
            print(print_result('勝率', win_count, sum_race))
            print(print_result('回収率', sum_payback, sum_race * 100))
        except ZeroDivisionError:
            print("データ不足")
        print('')

    def check_payback_popularity_base(self, column, order_fix, ranker_list):
        """
        人気ベースのペイバック
        """

        def calc(min_list, is_tune=False):
            # 枠連では販売していないパターンがあるため専用のカウンター
            sum_race = win_count = sum_payback = 0
            half_idx = int(len(self.df_predict) / 2)
            for idx, df in enumerate(self.df_predict[:half_idx] if is_tune else self.df_predict[half_idx:]):
                higher_rank_df = self.getmax_rev(df, 'popularity', True)
                if isinstance(ranker, int):
                    target_row = higher_rank_df.iloc[ranker]
                    # 上位馬番の取得
                    target_umaban = str(target_row["umaban"])
                    target_odds = target_row["odds"]

                    if min_list[0] > target_odds:
                        continue
                elif isinstance(ranker, list):
                    try:
                        target_umaban = [higher_rank_df.iloc[index]["wakuban" if column == 'wakuren' else 'umaban']
                                         for index in ranker]
                        target_odds = [higher_rank_df.iloc[index]["odds"] for index in ranker]

                        flag = False
                        for i, val in enumerate(min_list):
                            if val > target_odds[i]:
                                flag = True
                                break
                        if flag:
                            continue
                    except IndexError:  # 馬数不足 ex.202207010608
                        continue
                    if order_fix:
                        target_umaban = ' → '.join(list(map(str, target_umaban)))
                    else:
                        target_umaban.sort()
                        target_umaban = ' - '.join(list(map(str, target_umaban)))
                data = self.get_payback_dict(df, column)
                if not data:  # 枠連では販売していないパターンがあるため
                    continue
                sum_race += 1
                if target_umaban in data:
                    win_count += 1
                    sum_payback += data[target_umaban]
            return sum_race, win_count, sum_payback

        def tuning(trial):
            """
            閾値チューニング
            :return:
            """
            # 最大は第1四分位数以下にした  確認法：df.quantile(0.25)
            min_list = [trial.suggest_float("first_min", 1, 8)]
            if isinstance(ranker, list):
                if len(ranker_list[0]) > 1:
                    min_list.append(trial.suggest_float("second_min", 1, 8))
                if len(ranker_list[0]) > 2:
                    min_list.append(trial.suggest_float("third_min", 1, 8))
            sum_race, win_count, sum_payback = calc(min_list, True)
            return sum_payback / (sum_race * 100) if sum_race else 0

        def validation(best_params):
            """
            確定パラメータによる結果
            :return:
            """
            print(best_params)
            min_list = [best_params["first_min"]]
            if isinstance(ranker, list):
                if len(ranker_list[0]) > 1:
                    min_list.append(best_params["second_min"])
                if len(ranker_list[0]) > 2:
                    min_list.append(best_params["third_min"])
            sum_race, win_count, sum_payback = calc(min_list)
            self.print_result(ranker, win_count, sum_payback, sum_race)

        def no_tuning_validation():
            print('  ・チューニングなし')
            min_list = [1]
            if isinstance(ranker, list):
                for i in range(len(ranker_list[0]) - 1):
                    min_list.append(1)
            sum_race, win_count, sum_payback = calc(min_list)
            self.print_result(ranker, win_count, sum_payback, sum_race)

        print('  ◆ 人気ベース')
        for ranker in ranker_list:
            # 人気ベースのチューニングは効果なし
            # study = optuna.create_study(direction='maximize')
            # study.optimize(tuning, n_trials=100)
            # validation(study.best_params)
            no_tuning_validation()

    def check_payback_predict_base(self, ticket_type):
        def predict_param_name(x):
            return f"need_predict_{x}"

        def odds_param_name(x):
            return f"need_odds_{x}"

        """
        予想ベースのペイバック
        """

        def calc(need_min_predict_dict, need_min_odds_dict, is_tune=False):
            """
            :param need_min_predict_dict: 必要な予測最低値
            :param need_min_odds_dict: 必要なオッズ最低値
            :param is_tune: 閾値調整かどうか
            :return: チューニング時に最大化すべき計算式（回収率など）
            """

            # 枠連では販売していないパターンがあるため専用のカウンター
            sum_race = sum_ticket = win_race_cnt = win_ticket_cnt = sum_payback = 0
            half_idx = int(len(self.df_predict) / 2)
            for idx, df in enumerate(self.df_predict[:half_idx] if is_tune else self.df_predict[half_idx:]):
                ban_list = []
                for rank in range(ticket_rule.order_sum):
                    filtered_df = df[
                        (df['predict'] > need_min_predict_dict[rank]) & (df['odds'] > need_min_odds_dict[rank])]
                    ban_list.append(list(filtered_df['wakuban' if ticket_type == 'wakuren' else 'umaban']))

                # 順位組み合わせ作成
                ban_combination_list = list(map(list, list(itertools.product(*ban_list))))
                if not ticket_rule.is_fix:  # ソート
                    ban_combination_list = list(map(lambda x: sorted(x), ban_combination_list))
                ban_combination_list = list(map(lambda x: list(map(str, x)), ban_combination_list))
                ban_combination_list = list(
                    map(lambda x: (' → ' if ticket_rule.is_fix else ' - ').join(x), ban_combination_list))

                payback_umaban = self.get_payback_dict(df, ticket_type)
                if not payback_umaban:  # 枠連では販売していないパターンがあるため
                    continue
                if len(ban_combination_list) > 0:
                    sum_race += 1
                    sum_ticket += len(ban_combination_list)
                is_win = False
                # どんな結果でも最低100払い戻しは保証されているらしい
                for ban_combination in ban_combination_list:
                    if ban_combination in payback_umaban:
                        win_ticket_cnt += 1
                        sum_payback += payback_umaban[ban_combination]
                        if not is_win:
                            is_win = True
                            win_race_cnt += 1
            if not is_tune:
                print(f'---------({sum_race}/{len(self.df_predict[half_idx:])})---------')
                try:
                    print(print_result('勝レース率', win_race_cnt, sum_race))
                    print(print_result('勝馬券率', win_ticket_cnt, sum_ticket))
                    print(print_result('回収率', sum_payback, sum_ticket * 100))
                except ZeroDivisionError:
                    print("データ不足")

            return sum_payback / (sum_ticket * 100) + win_ticket_cnt / sum_ticket if sum_ticket else 0

        def tuning(trial):
            """
            閾値チューニング
            :return:
            """
            # 最大は第1四分位数以下にした  確認法：df.quantile(0.25)
            need_min_predict_list = [trial.suggest_float(predict_param_name(i), 0, 1) for i in
                                     range(ticket_rule.order_sum)]
            need_min_odds_list = [trial.suggest_float(odds_param_name(i), 1, 30) for i in
                                  range(ticket_rule.order_sum)]
            return calc(need_min_predict_list, need_min_odds_list, True)

        def validation(best_params):
            """
            確定パラメータによる結果
            :return:
            """
            print(best_params)
            need_min_predict_list = [best_params[predict_param_name(i)] for i in range(ticket_rule.order_sum)]
            need_min_odds_list = [best_params[odds_param_name(i)] for i in range(ticket_rule.order_sum)]
            calc(need_min_predict_list, need_min_odds_list)

        def no_tuning_validation():
            print('  ・全買いの場合')
            need_min_predict_list = [0 for i in range(ticket_rule.order_sum)]
            need_min_odds_list = [0 for i in range(ticket_rule.order_sum)]
            calc(need_min_predict_list, need_min_odds_list)

        print('  ◆ 予想ベース')
        ticket_rule = TicketRule(ticket_type)
        study = optuna.create_study(direction='maximize')
        study.optimize(tuning, n_trials=30)
        validation(study.best_params)
        no_tuning_validation()

    def check_payback(self, ticket_type, order_fix, ranker_list):
        """
        :param ticket_type:
        :param order_fix: 順不同ではないかどうか
        :param ranker_list: 順位リスト 0が１位　int型（単勝用など）とlist型（三連単用など）の２パターン存在
        """
        print(f'=============[ {ticket_type} ]=============')
        self.check_payback_popularity_base(ticket_type, order_fix, ranker_list)
        self.check_payback_predict_base(ticket_type)

    def __init__(self, df_predict, df_payback):
        """
        :param df_predict:
        :param df_payback:
        """
        self.df_predict = df_predict
        self.df_payback = df_payback

        # 次順との予想値幅平均
        predict_margin_list = [0, 0, 0]
        # 人気と予想の一致検証
        match_popularity_list = [[0, 0, 0], [0, 0, 0], [0, 0, 0]]
        for df in self.df_predict:
            higher_rank_df = self.getmax_rev(df)
            for i in range(3):
                predict_margin_list[i] += abs(higher_rank_df["predict"].iloc[i] - higher_rank_df["predict"].iloc[i + 1])
                for j in range(3):
                    if j + 1 == higher_rank_df["popularity"].iloc[i]:
                        match_popularity_list[i][j] += 1

        # 人気一致率検証（勝ったかどうかは別の話で、以降に出力される）
        length = len(self.df_predict)
        for i in range(3):
            print(f'margin {i + 1}-{i + 2} ave: {predict_margin_list[i] / length}')
            for j in range(3):
                print(
                    f'match popularity [predict]-[real] {i + 1}-{j + 1} : {match_popularity_list[i][j]}/{length} {match_popularity_list[i][j] / length * 100}%')
