import time

from mylib import *

if __name__ == "__main__":
    pd.set_option("display.max_columns", None)
    start = time.time()

    race_data = RaceProcessing()
    horse_data = HorseProcessing()
    # condition_data = ConditionProcessing()
    # yoso_data = YosoProcessing()
    pillar_data = PillarProcessing()
    jockey_profile = JockeyProfileProcessing()
    # jockey_result_profile = JockeyResultProcessing()
    paybackData = PaybackProcessing()

    # デフォルトはレースid基準となっているため日付順にソート
    merged_df = race_data.df.merge(horse_data.df, on=["race_id", "horse_id"], how="inner").sort_values(
        by=['race_date', 'race_id'])
    # merged_df = PastRaceProcessing(merged_df).df
    # レースデータで中止や除外になった馬は、HorseProcessingで弾いているので内部結合で弾く
    for data in [pillar_data]:  # , condition_data, yoso_data]:
        merged_df = merged_df.merge(data.df, on=["race_id", "horse_id"], how="left")

    merged_df = pillar_data.update_race_date(merged_df)
    merged_df = jockey_profile.merge(merged_df)
    # merged_df = jockey_result_profile.merge(merged_df)
    # yoso_data.categorize(merged_df)

    # マージ使用後用済み
    merged_df['jockey_id'] = merged_df['jockey_id'].astype("category")
    gbm = LightGbm(merged_df)
    df_predict = predict_convert_list(gbm.test_df)
    # gbm.protData()

    money = Monetize(df_predict, paybackData.df)
    money.check_payback(['tanshou', 'fukushou'], False, [0, 1, 2])
    money.check_payback(['wakuren', 'umaren', 'wide'], False, [[0, 1], [0, 2], [1, 2]])
    money.check_payback(['umatan'], True, [[0, 1], [1, 0], [0, 2], [1, 2], [2, 0]])
    money.check_payback(['sanrenpuku'], False, [[0, 1, 2], [0, 1, 3], [0, 2, 3], [1, 2, 3]])
    money.check_payback(['sanrentan'], True, [[0, 1, 2], [0, 2, 1], [1, 0, 2], [1, 2, 0], [2, 0, 1], [2, 1, 0]])

    print(f'経過時間: {time.time() - start}')
