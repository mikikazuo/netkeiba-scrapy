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
    return f"{headline}: {str(top)}/{bottom}  {top / bottom * 100}%"


class Monetize:
    """
    [payback_dataの扱い]
    キーがstr型なので各々で加工して使う
    """

    def get_payback_dict(self, df, col):
        """
        ペイバック読み込み
        """
        return self.df_payback.loc[df.index.get_level_values("race_id")[0]][col]

    def getmax_rev(self, df, target_col="predict", getmin=False, top_limit=4):
        """
        上位のindexを取得
        :param df
        :param target_col 大小チェック対象カラム
        :param getmin: 少ないほうをとるのかどうか
        :param top_limit: 取得数
        """
        return df.nsmallest(top_limit, target_col) if getmin else df.nlargest(top_limit, target_col)

    def print_result(self, title, win_count, sum_payback, sum_race, match_popularity_count):
        print(f'---------{title}({sum_race}/{len(self.df_predict)})---------')
        try:
            print(print_result('勝率', win_count, sum_race))
            print(print_result('回収率', sum_payback, sum_race * 100))
            print(print_result('上位人気順一致率', match_popularity_count, win_count))
        except ZeroDivisionError:
            print("データ不足")
        print('')

    def check_payback_popularity_base(self, column, order_fix, ranker_list):
        """
        人気ベースのペイバック
        """
        # 枠連では販売していないパターンがあるため専用のカウンター
        sum_race = 0
        win_count = 0
        sum_payback = 0
        for idx, df in enumerate(self.df_predict):
            higher_rank_df = self.getmax_rev(df, "popularity", True)
            if isinstance(ranker_list[0], int):
                target_umaban = str(higher_rank_df.iloc[0]["umaban"])
            elif isinstance(ranker_list[0], list):
                target_umaban = [umaban for umaban in higher_rank_df.iloc[0:len(ranker_list[0])][
                    "wakuban" if column == 'wakuren' else 'umaban']]
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
        self.print_result(column, win_count, sum_payback, sum_race, win_count)

    def check_payback(self, column_list, order_fix, ranker_list):
        """
        :param column_list:
        :param order_fix: 順不同ではないかどうか
        :param ranker_list: 順位リスト 0が１位　int型（単勝用など）とlist型（三連単用など）の２パターン存在
        :param payback_border: オッズが指定値以上の場合に買う（オッズを確認してから馬券購入するという流れを踏まえたもの）
        """
        for column in column_list:
            print('=============================================')
            self.check_payback_popularity_base(column, order_fix, ranker_list)
            for ranker in ranker_list:
                # 枠連では販売していないパターンがあるため専用のカウンター
                sum_race = 0
                win_count = 0
                sum_payback = 0
                match_popularity_count = 0
                for idx, df in enumerate(self.df_predict):
                    higher_rank_df = self.getmax_rev(df)
                    if isinstance(ranker, int):
                        target_row = higher_rank_df.iloc[ranker]
                        # 上位馬番の取得
                        target_umaban = str(target_row["umaban"])
                        if column == 'fukushou':
                            is_match_popularity = target_row["popularity"] in [1, 2, 3]
                        else:
                            is_match_popularity = target_row["popularity"] == 1
                    elif isinstance(ranker, list):
                        try:
                            target_umaban = [higher_rank_df.iloc[index]["wakuban" if column == 'wakuren' else 'umaban']
                                             for index in ranker]
                        except IndexError:  # 馬数不足 ex.202207010608
                            continue
                        if order_fix:
                            target_umaban = ' → '.join(list(map(str, target_umaban)))
                        else:
                            target_umaban.sort()
                            target_umaban = ' - '.join(list(map(str, target_umaban)))
                        is_match_popularity = True
                        for i, index in enumerate(ranker):
                            if higher_rank_df.iloc[index]["popularity"] != i + 1:
                                is_match_popularity = False
                                break
                    data = self.get_payback_dict(df, column)
                    if not data:  # 枠連では販売していないパターンがあるため
                        continue
                    sum_race += 1
                    # どんな結果でも最低100払い戻しは保証されているらしい
                    if target_umaban in data:
                        win_count += 1
                        sum_payback += data[target_umaban]
                        if is_match_popularity:
                            match_popularity_count += 1
                self.print_result(column, win_count, sum_payback, sum_race, match_popularity_count)

    def __init__(self, df_predict, df_payback):
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
