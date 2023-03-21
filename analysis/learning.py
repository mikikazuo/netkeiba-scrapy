import time

from mylib import *

if __name__ == "__main__":
    pd.set_option("display.max_columns", None)
    start = time.time()

    horseData = HorseProcessing()
    raceData = RaceProcessing()
    paybackData = PaybackProcessing()

    merged_df = raceData.df.merge(horseData.df, on=["race_id", "horse_id"], how="inner")

    past_add_data = PastRaceProcessing(merged_df)

    gbm = LightGbm(past_add_data.df)
    df_predict = gbm.makePredictDataset()
    #gbm.protData()
    money = Monetize(df_predict, paybackData.df)

    money.check_pattern_payback(['tanshou', 'fukushou'], list(range(3)))
    money.check_pattern_payback(['wakuren', 'umaren', 'wide', 'umatan'], [[0, 1], [0, 2], [1, 2]])
    money.check_pattern_payback(['sanrenpuku', 'sanrentan'], [[0, 1, 2], [0, 1, 3], [0, 2, 3], [1, 2, 3]])

    process_time = time.time() - start
    print(f'経過時間: {process_time}')
