import pathlib

import pandas as pd

# レースデータhtmlの保存先ディレクトリパス
input_html_dir = 'D:/netkeiba/html_data/race/'


def get_last_slash_word(url):
    """
    filterはリスト内の空文字を除去する
    :return urlの最後の文字列
    """
    return list(filter(None, url.split('/')))[-1]


def make_urls_depend_race_id(base_url, start_year):
    """
    レースデータhtmlのファイル名からレースid依存のURLリスト作成

    :param base_url: race_idが可変部分となるベースとなるURL
    :param start_year: 対象のレースidの開始年度。

    レース開催地によって上５桁目以降レースidの大小が大きく（日付に依存していない）綺麗に区切ることができないので年度単位で取得。

    クロール時の各parse関数で対象タグ要素の有無を判定し、弾く処理を追加すること。

    [おまけ] 同レース開催地の場合、下３桁目が日ごとに変わる。１レース目は下２桁が01で以後1ずつ増える。
    """
    p_temp = pathlib.Path(input_html_dir)
    str_p_list = [x.stem for x in list(p_temp.iterdir())]
    str_p_df = pd.DataFrame({"race_id": str_p_list})
    str_p_df = str_p_df.loc[str_p_df["race_id"] >= str(start_year) + '00000000', :]
    return [base_url + race_id for race_id in str_p_df["race_id"]]


def make_output_dir(path):
    """
    出力先ディレクトリの作成
    """
    try:
        pathlib.Path(path).mkdir()
    except FileExistsError:
        pass


def write_html(output_dir_path, url, response):
    """
    HTMLだけとってくる
    htmlの記載に「charset=euc-jp」がない場合、encodingの別途指定が必要。
    :param output_dir_path:
    :param url: URLのキーのなるid部分
    :param response:
    """
    path = output_dir_path + url + '.html'

    html_file = open(path, 'w', encoding='euc-jp')
    html_file.write(response.text.replace('\ufffd', ''))  # 文字コードeuc-jpに変換できない文字削除
    html_file.close()

    print("CRAWLED:", response.url)
