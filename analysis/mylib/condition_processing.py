import ast

import pandas as pd

import mypath
from analysis.mylib.general import *


class ConditionProcessing(DataframeProcessing):
    def __init__(self):
        # 海外のレースが含まれない範囲の場合、int型になってしまうため手動でstr化 ex.2019J0033009
        self.df = pd.read_csv(mypath.condition_csv, dtype={'race_id': str})

        self.df['condition_score_past'] = self.df['condition_score_past'].map(ast.literal_eval)
        for i in range(5):
            self.df[f'condition_score_{i + 1}'] = self.df['condition_score_past']
            self.df[f'condition_score_{i + 1}'] = self.df[f'condition_score_{i + 1}'].map(
                lambda x: x[i] if len(x) > i else -1)
            self.change_type([f'condition_score_{i + 1}'], "int8")
        self.df = self.df.drop('condition_score_past', axis=1)

        self.change_type(['condition_score', 'condition_rank', 'rise_rank'], "int8")
        self.df = self.df.set_index(["race_id", "horse_id"])
