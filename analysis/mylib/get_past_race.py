import pandas as pd
from tqdm import tqdm


class PastRaceProcessing:
    def past_race_id_list(self, horse_id):
        # cudfはlocに向いていない
        race_df = self.merged_df_for_past.xs(horse_id, level='horse_id')
        race_length = len(race_df)
        if race_length <= self.pastNum:
            return None
        past_df_list = []
        for i in range(self.pastNum + 1):
            data = race_df[i: i + race_length - self.pastNum]
            if i == 0:
                # horse_processing.pyで取得される海外レースのidに英語が含まれていると自動的にstr型になる。
                # マージでインデックス型を合わせる必要があるため変換 ex 2019J0033009
                race_id = list(map(str, data.index))
            else:
                # mergeはなぜか使えない 一致する自作カラムが最低一つ必要か？
                past_df_list.append(
                    data.rename(columns=dict(zip(race_df.columns, race_df.columns + "_" + str(i)))).reset_index(
                        drop=True))
        merged_frame = pd.concat(past_df_list, axis=1)
        # ここでマルチインデックスを付け足す  参照段階で残す場合、括弧でくくるパターンloc[[horse_id],:]　は処理が重いので
        merged_frame.index = pd.MultiIndex.from_arrays([race_id, [horse_id] * (race_length - self.pastNum)],
                                                       names=["race_id", "horse_id"])
        return merged_frame

    def get_past_race(self):
        horse_id_list = [multi_index[1] for multi_index in self.merged_df_for_past.index]
        horse_id_list = list(set(horse_id_list))  # 馬idが重複して入っているのでsetを使う
        result_list = []

        # マルチプロセスにすると遅くなる。引数で渡す変数のサイズが大きいためか？
        for horse_id in tqdm(horse_id_list):
            result_list.append(self.past_race_id_list(horse_id))

        # Noneは省略されて詰められる
        return pd.concat(result_list)

    def __init__(self, merged_df):
        self.pastNum = 1

        # 過去に関係なく一貫性のあるコラム 過去データとして連結しないカラム
        common_columns = ["birth_date", "from", "maker_id", "sex", "trainer_id", "tresen", "race_cnt", "order"]
        # 過去のカウント系の除外
        for order_idx in range(3):
            common_columns.append("order_" + str(order_idx + 1) + "_cnt_normalize")

        # ソートのためにtarget_columnsにrace_dateを含めること
        target_columns = list(set(merged_df.columns) - set(common_columns))
        self.merged_df_for_past = merged_df[target_columns].sort_values("race_date", ascending=False)

        self.df = merged_df.merge(self.get_past_race(), on=["race_id", "horse_id"], how="inner")
        for i in range(self.pastNum):
            self.df["race_date_" + str(i + 1)] = (self.df["race_date"] - self.df["race_date_" + str(i + 1)]).map(
                lambda x: x.days).astype("int16")
