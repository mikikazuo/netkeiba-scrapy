import ast
import math

import pandas as pd

import mypath


def str_to_dict(str_data):
    if isinstance(str_data, float) and math.isnan(str_data):  # 馬連は9頭以上の場合ににしか発売されないため、ない場合ここで弾く。事前にNoneを設定している。
        return None

    dict_data = ast.literal_eval(str_data)
    dict_data["payback"] = list(map(lambda x: int(x.replace(',', '')), dict_data["payback"]))
    return dict(zip(dict_data["umaban"], dict_data["payback"]))


class PaybackProcessing:
    def __init__(self):
        print('payback start')
        # 海外のレースが含まれない範囲の場合、int型になってしまうため手動でstr化 ex.2019J0033009
        self.df = pd.read_csv(mypath.payback_csv, dtype={'race_id': str}, index_col="race_id")
        for column in self.df.columns:
            self.df[column] = self.df[column].map(lambda x: str_to_dict(x))
