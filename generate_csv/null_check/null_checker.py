"""
スクレイピングで出力したcsvでNoneが出力された項目をチェックするためのもの
lxmlではtext()でテキストが空の場合はNoneに変換されるっぽい
scraperでNoneを指定するとcsvファイル上では''空文字で出力され、これをpythonで読み込んで初めてNoneとなる

馬データでpaceがnoneとなっているのは地方競馬のパターンが多い
"""
import pandas as pd

import mypath


def print_example(target_filter, title, col=None):
    """
    :param target_filter: 対象にするdataframeの条件フィルタ
    :param title: タイトル
    :param col: カラムの具体値が欲しい場合、引数を設定する
    """
    filtered_df = df[target_filter]
    word = ''
    if len(filtered_df):
        word = ' | [' + title + '] race_id: ' + str(filtered_df['race_id'].iloc[0])
        if 'horse_id' in filtered_df.columns:
            word += ' / horse_id: ' + str(filtered_df['horse_id'].iloc[0])
        if col:
            word += ' / 対象カラム値: ' + str(filtered_df[col].iloc[0])
    return word


if __name__ == '__main__':
    pd.set_option('display.max_columns', None)

    # チェック対象のcsvのパス
    check_csv_path = mypath.pillar_csv

    # チェック結果シートのファイル名
    output_null_checker_path = 'pillar_check.txt'

    # int値が小数にならないようobject型で読み込む
    df = pd.read_csv(check_csv_path, dtype=object)
    row_size = str(len(df))

    with open(output_null_checker_path, 'w', encoding='utf-8') as f:
        print('対象csv', check_csv_path, file=f)
        print('対象csvの元となったhtmlのパスは各〇〇_scraper.pyファイル参照', file=f)
        print('\n---------------Noneの占める割合---------------', file=f)
        for column in df.columns:
            target_filter = df[column].isnull()
            ex_word = print_example(df[column].notnull(), 'あり', column).ljust(80)
            ex_word += print_example(target_filter, 'なし')
            print(column.rjust(18), str(len(df[target_filter])).rjust(7) + ' / ' + row_size, ex_word, file=f)

        print('\n---------------スペース（\\xa0）の占める割合(普通の半角・全角のスペースとは別扱い)---------------', file=f)
        for column in df.columns:
            target_filter = df[column].str.contains(" ", na=False)
            ex_word = print_example(target_filter, 'スペース', column)

            print(column.rjust(18), str(len(df[target_filter])).rjust(7) + ' / ' + row_size,
                  ex_word, file=f)
    print(output_null_checker_path + ' を出力しました')
