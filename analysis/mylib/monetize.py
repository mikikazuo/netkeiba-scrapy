# TODO 辞書に変換されるようにキーをstr型でスクレイピング側で統一するようにする
class Monetize:
    """
    [payback_dataの扱い]
    キーがstr型なので各々で加工して使う
    """

    def get_dict(self, df, col):
        return self.paybackData.df.loc[df.index.get_level_values("race_id")[0]][col]

    # 上位のindexを取得
    def getmax_rev(self, df, topnum=5, getmin=False):
        return df.nsmallest(topnum, "predict") if getmin else df.nlargest(topnum, "predict")

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
        # 枠連を販売していないパターンがあるため専用のカウンター
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

    def sanrentan(self, ranker=[0, 1, 2], payback_border=100):
        win_count = 0
        sum_payback = 0
        race_count = 0

        for df in self.df_predict:
            data = self.get_dict(df, "sanrentan")
            # 上位馬番の取得
            try:
                target_umaban = [self.getmax_rev(df)["umaban"][index] for index in ranker]
            except IndexError:
                continue
            pattern = ' → '.join(list(map(str, target_umaban)))
            race_count = race_count + 1

            if pattern in data and data[pattern] > payback_border:
                win_count = win_count + 1
                sum_payback = sum_payback + data[pattern]
        self.print_result('三連単', win_count, sum_payback, race_count)

    # paybackBorderは実際、オッズを確認してから馬券購入するという流れを踏まえたもの
    def tanshou(self, ranker=0, payback_border=100):
        win_count = 0
        sum_payback = 0
        sum_race = 0

        for df in self.df_predict:
            data = self.get_dict(df, "tanshou")
            # 上位馬番の取得
            target_umaban = str(self.getmax_rev(df)["umaban"].iloc[ranker])
            # どんな結果でも最低100払い戻しは保証されているらしい
            if target_umaban in data and data[target_umaban] > payback_border:
                win_count = win_count + 1
                sum_payback = sum_payback + data[target_umaban]
            sum_race = sum_race + 1
        self.print_result('単勝', win_count, sum_payback, sum_race)

    # 3着以内に入る馬を1つ選択
    def fukushou(self, ranker=0, payback_border=100):
        win_count = 0
        sum_payback = 0

        for df in self.df_predict:
            data = self.get_dict(df, "fukushou")
            # 上位馬番の取得
            target_umaban = str(self.getmax_rev(df)["umaban"].iloc[ranker])
            if target_umaban in data and data[target_umaban] > payback_border:
                win_count = win_count + 1
                sum_payback = sum_payback + data[target_umaban]
        self.print_result('複勝', win_count, sum_payback, len(self.df_predict))

    def wakuren(self, ranker=[0, 1], payback_border=100):
        win_count = 0
        sum_payback = 0
        # 枠連を販売していないパターンがあるため専用のカウンター
        race_count = 0

        for df in self.df_predict:
            data = self.get_dict(df, "wakuren")
            if not data:
                continue
            # 上位馬番の取得
            target_umaban = [self.getmax_rev(df)["wakuban"][index] for index in ranker]
            target_umaban.sort()
            pattern = ' - '.join(list(map(str, target_umaban)))
            race_count = race_count + 1

            if pattern in data and data[pattern] > payback_border:
                win_count = win_count + 1
                sum_payback = sum_payback + data[pattern]
        self.print_result('枠連', win_count, sum_payback, race_count)

    def umaren(self, ranker=[0, 1], payback_border=100):
        win_count = 0
        sum_payback = 0

        for df in self.df_predict:
            data = self.get_dict(df, "umaren")
            # 上位馬番の取得
            target_umaban = [self.getmax_rev(df)["umaban"][index] for index in ranker]
            target_umaban.sort()
            pattern = ' - '.join(list(map(str, target_umaban)))

            if pattern in data and data[pattern] > payback_border:
                win_count = win_count + 1
                sum_payback = sum_payback + data[pattern]
        self.print_result('馬連', win_count, sum_payback, len(self.df_predict))

    # 3着以内に入る馬を２つ選択
    def wide(self, ranker=[0, 1], payback_border=100):
        win_count = 0
        sum_payback = 0

        for df in self.df_predict:
            data = self.get_dict(df, "wide")
            # 上位馬番の取得
            target_umaban = [self.getmax_rev(df)["umaban"][index] for index in ranker]
            target_umaban.sort()
            pattern = ' - '.join(list(map(str, target_umaban)))

            if pattern in data and data[pattern] > payback_border:
                win_count = win_count + 1
                sum_payback = sum_payback + data[pattern]
        self.print_result('ワイド', win_count, sum_payback, len(self.df_predict))

    def umatan(self, ranker=[0, 1], payback_border=100):
        win_count = 0
        sum_payback = 0

        for df in self.df_predict:
            data = self.get_dict(df, "umatan")
            # 上位馬番の取得
            target_umaban = [self.getmax_rev(df)["umaban"][index] for index in ranker]
            pattern = ' → '.join(list(map(str, target_umaban)))

            if pattern in data and data[pattern] > payback_border:
                win_count = win_count + 1
                sum_payback = sum_payback + data[pattern]
        self.print_result('馬単', win_count, sum_payback, len(self.df_predict))

    def sanrenpuku(self, ranker=[0, 1, 2], payback_border=100):
        win_count = 0
        sum_payback = 0
        race_count = 0

        for df in self.df_predict:
            data = self.get_dict(df, "sanrenpuku")
            # 上位馬番の取得
            try:
                target_umaban = [self.getmax_rev(df)["umaban"][index] for index in ranker]
            # 馬数不足 ex.202207010608
            except IndexError:
                continue
            target_umaban.sort()
            pattern = ' - '.join(list(map(str, target_umaban)))
            race_count = race_count + 1

            if pattern in data and data[pattern] > payback_border:
                win_count = win_count + 1
                sum_payback = sum_payback + data[pattern]
        self.print_result('三連複', win_count, sum_payback, race_count)

    def sanrentan(self, ranker=[0, 1, 2], payback_border=100):
        win_count = 0
        sum_payback = 0
        race_count = 0

        for df in self.df_predict:
            data = self.get_dict(df, "sanrentan")
            # 上位馬番の取得
            try:
                target_umaban = [self.getmax_rev(df)["umaban"][index] for index in ranker]
            except IndexError:
                continue
            pattern = ' → '.join(list(map(str, target_umaban)))
            race_count = race_count + 1

            if pattern in data and data[pattern] > payback_border:
                win_count = win_count + 1
                sum_payback = sum_payback + data[pattern]
        self.print_result('三連単', win_count, sum_payback, race_count)

    def __init__(self, df_predict, payback_data):
        self.df_predict = df_predict
        self.paybackData = payback_data
