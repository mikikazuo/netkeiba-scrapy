import pathlib

import pandas as pd

# レースデータhtmlの保存先ディレクトリパス
input_race_html_dir = 'D:/netkeiba/html_data/race/'
# 馬データhtmlの保存先ディレクトリパス
input_horse_html_dir = 'D:/netkeiba/html_data/horse/'


def make_output_dir(path):
    """
    出力先ディレクトリの作成
    """
    try:
        pathlib.Path(path).mkdir()
    except FileExistsError:
        pass


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
    p_temp = pathlib.Path(input_race_html_dir).iterdir()
    race_id_list = [x.stem for x in p_temp if x.stem >= str(start_year) + '00000000']
    return [base_url + race_id for race_id in race_id_list]


def make_urls_depend_horse_id(base_url, output_html_dir):
    """
    馬データhtmlのファイル名から馬id依存のURLリスト作成

    :param base_url: horse_idが可変部分となるベースとなるURL
    :param output_html_dir: htmlの出力先ディレクトリパス。ダウンロード済みかどうかのチェックに使う。
    """
    p_temp = pathlib.Path(input_horse_html_dir).iterdir()
    horse_id_list = [x.stem for x in p_temp]

    # ダウンロード済みhtmlは除外する
    path_iter = pathlib.Path(output_html_dir).iterdir()
    downloaded_id_list = [path.stem for path in path_iter]

    return [base_url + horse_id for horse_id in list(set(horse_id_list) - set(downloaded_id_list))]


def make_urls_depend_list_csv(base_url, input_csv_path, header, output_html_dir):
    """
    pre_crawlerフォルダ下の.pyファイルで作成したid一覧csvに依存するURLリスト作成

    :param base_url: idが可変部分となるベースとなるURL
    :param input_csv_path: 事前に作成したid一覧csvのパス
    :param header: csvヘッダ名
    :param output_html_dir: htmlの出力先ディレクトリパス。ダウンロード済みかどうかのチェックに使う。
    """
    id_df = pd.read_csv(input_csv_path, dtype={header: str})
    id_list = sorted(id_df[header])

    # ダウンロード済みhtmlは除外する
    path_iter = pathlib.Path(output_html_dir).iterdir()
    downloaded_id_list = [path.stem for path in path_iter]

    return [base_url + x for x in list(set(id_list) - set(downloaded_id_list))]


def write_html(output_dir_path, file_name, response):
    """
    HTMLだけとってくる
    htmlの記載に「charset=euc-jp」がない場合、encodingの別途指定が必要。
    :param output_dir_path:
    :param file_name: URLのキーのなるid部分
    :param response:
    """
    path = output_dir_path + file_name + '.html'
    html_file = open(path, 'w', encoding='euc-jp')
    html_file.write(response.text.replace('\ufffd', ''))  # 文字コードeuc-jpに変換できない文字削除
    html_file.close()

    print("CRAWLED:", response.url)
