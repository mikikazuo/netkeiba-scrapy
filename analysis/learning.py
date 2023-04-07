import time

from mylib import *

if __name__ == "__main__":
    pd.set_option("display.max_columns", None)
    start = time.time()

    race_data = RaceProcessing()
    horse_data = HorseProcessing()
    condition_data = ConditionProcessing()
    yoso_data = YosoProcessing()
    pillar_data = PillarProcessing()
    paybackData = PaybackProcessing()

    merged_df = race_data.df.merge(horse_data.df, on=["race_id", "horse_id"], how="inner")
    #merged_df = PastRaceProcessing(merged_df).df
    # レースデータで中止や除外になった馬は、HorseProcessingで弾いているので内部結合で弾く
    for data in [condition_data, yoso_data, pillar_data]:
        merged_df = merged_df.merge(data.df, on=["race_id", "horse_id"], how="left")
    merged_df = yoso_data.categorize(merged_df)
    pillar_data.update_race_date(merged_df)

    gbm = LightGbm(merged_df)
    df_predict = gbm.makePredictDataset()
    #gbm.protData()
    money = Monetize(df_predict, paybackData.df)

    money.check_pattern_payback(['tanshou', 'fukushou'], list(range(3)))
    money.check_pattern_payback(['wakuren', 'umaren', 'wide', 'umatan'], [[0, 1], [0, 2], [1, 2]])
    money.check_pattern_payback(['sanrenpuku', 'sanrentan'], [[0, 1, 2], [0, 1, 3], [0, 2, 3], [1, 2, 3]])

    process_time = time.time() - start
    print(f'経過時間: {process_time}')

