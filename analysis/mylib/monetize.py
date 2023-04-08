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


class Monetize:
    """
    [payback_dataの扱い]
    キーがstr型なので各々で加工して使う
    """

    def get_dict(self, df, col):
        return self.df_payback.loc[df.index.get_level_values("race_id")[0]][col]

    def getmax_rev(self, df, top_limit=4, getmin=True):
        """
        上位のindexを取得
        :param df
        :param top_limit: 取得数
        :param getmin: 少ないほうをとるのかどうか
        """
        return df.nsmallest(top_limit, "predict") if getmin else df.nlargest(top_limit, "predict")

    def print_result(self, title, win_count, sum_payback, sum_race):
        print(f'\n---------{title}({sum_race}/{len(self.df_predict)})---------')
        try:
            print("勝率: " + str(win_count) + "/" + str(sum_race), str(win_count / sum_race * 100) + "%")
        except ZeroDivisionError:
            print("データ不足")

        try:
            print("回収率: " + str(sum_payback) + "/" + str(sum_race * 100), str(sum_payback / sum_race) + "%")
        except ZeroDivisionError:
            pass

    def check_payback(self, column_list, order_fix, ranker_list, payback_border=100):
        """
        :param column_list:
        :param order_fix: 順不同ではないかどうか
        :param ranker_list: 順位リスト 0が１位　int型（単勝用など）とlist型（三連単用など）の２パターン存在
        :param payback_border: オッズが指定値以上の場合に買う（オッズを確認してから馬券購入するという流れを踏まえたもの）
        """
        for column in column_list:
            for ranker in ranker_list:
                win_count = 0
                sum_payback = 0
                # 枠連では販売していないパターンがあるため専用のカウンター
                sum_race = 0

                for df in self.df_predict:
                    higher_rank_df = self.getmax_rev(df)
                    if isinstance(ranker, int):
                        # 上位馬番の取得
                        target_umaban = str(higher_rank_df["umaban"].iloc[ranker])
                    elif isinstance(ranker, list):
                        try:
                            target_umaban = [higher_rank_df["wakuban" if column == 'wakuren' else 'umaban'][index] for
                                             index in ranker]
                        except IndexError:  # 馬数不足 ex.202207010608
                            continue
                        if order_fix:
                            target_umaban = ' → '.join(list(map(str, target_umaban)))
                        else:
                            target_umaban.sort()
                            target_umaban = ' - '.join(list(map(str, target_umaban)))

                    data = self.get_dict(df, column)
                    if not data:  # 枠連では販売していないパターンがあるため
                        continue
                    sum_race = sum_race + 1
                    # どんな結果でも最低100払い戻しは保証されているらしい
                    if target_umaban in data and data[target_umaban] > payback_border:
                        win_count = win_count + 1
                        sum_payback = sum_payback + data[target_umaban]

                self.print_result(column, win_count, sum_payback, sum_race)

    def __init__(self, df_predict, df_payback):
        self.df_predict = df_predict
        self.df_payback = df_payback

        predict_mergin_list = [0, 0, 0]
        for df in self.df_predict:
            higher_rank_df = self.getmax_rev(df)
            for i in range(len(predict_mergin_list)):
                predict_mergin_list[i] += abs(higher_rank_df["predict"].iloc[i] - higher_rank_df["predict"].iloc[i + 1])

        for i in range(len(predict_mergin_list)):
            print(f'mergin {i}-{i + 1} ave: {predict_mergin_list[i] / len(self.df_predict)}')
