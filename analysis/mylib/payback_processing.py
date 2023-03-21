import ast
import math

import pandas as pd

import mypath


def str_to_dict(str_data):
    if isinstance(str_data, float) and math.isnan(str_data):  # 馬連で弾く用
        return None

    dict_data = ast.literal_eval(str_data)
    dict_data["payback"] = list(map(lambda x: int(x.replace(',', '')), dict_data["payback"]))
    dict_data = dict(zip(dict_data["umaban"], dict_data["payback"]))
    return dict_data


class PaybackProcessing:
    # def preProcessing(self):
    #     for col in self.df.columns:
    #         data = json.loads(self.df.iloc[0][col])
    #         if len(data['payback']):
    #             for key in ['payback','ninki']:
    #                 data[key] = [int(d.replace(',', '')) for d in data[key]] #paybackが4桁ある時にカンマが入るため ex.201709040602
    #             # 馬番専用
    #             data['umaban'] = [tuple(map(int, d.split(' - '))) for d in data['umaban']] if '-' in data['umaban'][
    #                 0] else list(map(int, data['umaban']))
    #             self.df.iloc[0][col] = data
    #         else:
    #             self.df.iloc[0][col] = None

    def __init__(self):
        self.df = pd.read_csv(mypath.payback_csv, dtype={'race_id': str}, index_col="race_id")
        for column in self.df.columns:
            self.df[column] = self.df[column].map(lambda x: str_to_dict(x))
