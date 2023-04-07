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

    def check_pattern_payback(self, column_list, ranker_list, payback_border=100):
        for column in column_list:
            for ranker in ranker_list:
                self.check_payback(column, ranker, payback_border)

    # paybackBorderは実際、オッズを確認してから馬券購入するという流れを踏まえたもの
    def check_payback(self, column, ranker, payback_border):
        win_count = 0
        sum_payback = 0
        # 枠連では販売していないパターンがあるため専用のカウンター
        sum_race = 0

        for df in self.df_predict:
            data = self.get_dict(df, column)
            if not data:
                continue
            if isinstance(ranker, int):
                # 上位馬番の取得
                target_umaban = str(self.getmax_rev(df)["umaban"].iloc[ranker])
            elif isinstance(ranker, list):
                # 順不同ではない買い方
                arrow_column = ['umatan', 'sanrentan']
                try:
                    target_umaban = [self.getmax_rev(df)["wakuban" if column == 'wakuren' else 'umaban'][index] for
                                     index in ranker]
                except IndexError:  # 馬数不足 ex.202207010608
                    continue
                if column in arrow_column:
                    target_umaban = ' → '.join(list(map(str, target_umaban)))
                else:
                    target_umaban.sort()
                    target_umaban = ' - '.join(list(map(str, target_umaban)))
            sum_race = sum_race + 1

            # どんな結果でも最低100払い戻しは保証されているらしい
            if target_umaban in data and data[target_umaban] > payback_border:
                win_count = win_count + 1
                sum_payback = sum_payback + data[target_umaban]

        self.print_result(column, win_count, sum_payback, sum_race)

    def __init__(self, df_predict, df_payback):
        self.df_predict = df_predict
        self.df_payback = df_payback
