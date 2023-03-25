import csv
import os
import pathlib
import time
from abc import ABCMeta, abstractmethod
from multiprocessing import Pool

import lxml.html
from tqdm import tqdm


def confirm_exist_file_delete(path):
    """
    既にファイルが存在している場合の削除確認
    """
    if os.path.exists(path):
        print("既に出力済みcsvファイル「" + path + "」があります。Enterキーでファイルを削除します。")
        input()
        os.remove(path)


def read_html(html_path):
    """
    1つのページからlxmlを使ってスクレイピングする。
    """
    read = html_path.read_text(encoding="euc-jp")
    # print("scraping", html_path.name)
    return lxml.html.fromstring(read)


def delete_space(result):
    """
    スペース（\xa0）の削除
    """
    for key in result:
        if result[key] and not isinstance(result[key], bool):
            result[key] = result[key].strip()


class Scraper(metaclass=ABCMeta):
    @abstractmethod
    def scrape_from_page(self, html_path):
        """
        リストを戻り値とするスクレイピング関数、
        """
        pass

    def __init__(self, input_html_dir, output_csv_path, regex: None | tuple | int = None):
        """
        :param input_html_dir: データ抽出元となるhtmlのディレクトリ
        :param output_csv_path: csvの出力先パス
        :param regex: [指定なし]全ファイル______[tuple指定]指定範囲年度のファイル______[int指定]対象１ファイル
        """
        # イテレータのままだと一度参照すると再度参照できないためリスト化する。ファイル名で自動でsortされている。
        path = pathlib.Path(input_html_dir)
        # 全ファイル
        if not regex:
            self.html_path_list = list(path.iterdir())
        # 指定範囲年度のファイル
        elif isinstance(regex, tuple):
            self.html_path_list = sum([list(path.glob(year + '*')) for year in map(str, range(regex[0], regex[1]))], [])
        # 指定複数ファイル
        elif isinstance(regex, list):
            self.html_path_list = sum([list(path.glob(file_id + '.html')) for file_id in regex], [])
        # 1ファイルチェック用
        elif isinstance(regex, int):
            self.html_path_list = list(path.glob(str(regex) + '.html'))

        self.output_csv_path = output_csv_path

        self.csv_header = self.init_csv_header()
        self.exec_scraper()

    def init_csv_header(self):
        """
        csvファイルが存在しない場合にヘッダーの初期化とファイルの生成
        """
        confirm_exist_file_delete(self.output_csv_path)
        header = list(self.scrape_from_page(self.html_path_list[0])[0].keys())

        with open(self.output_csv_path, "w", encoding="utf-8") as csvfile:
            # デフォルトだと改行コードがWindowsのCRLF(\r\n)になっている。
            # データ解析のDocker側はLinux系でLF(\n)なので明示的に改行コード指定
            writer = csv.DictWriter(csvfile, fieldnames=header, lineterminator='\n')
            writer.writeheader()
        print("出力csvファイルの初期化完了")
        return header

    def exec_scraper(self):
        """
        マルチプロセスによるスクレイピングの実行と結果の書き込み
        """

        def write_result(path):
            result_list = pool.map(self.scrape_from_page, path)
            for result in result_list:
                writer.writerows(result)

        start = time.time()

        with Pool() as pool:
            with open(self.output_csv_path, "a", encoding="utf-8") as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=self.csv_header, lineterminator='\n')
                # マルチプロセスで同時に参照するhtmlのパスリスト
                pooled_path = []
                for i, html_path in enumerate(tqdm(self.html_path_list)):
                    pooled_path.append(html_path)
                    # 多すぎる場合一括だと逆に遅くなるため、一定数ごとにcsvに書き込み。
                    if i > 0 and i % os.cpu_count() == 0:
                        write_result(pooled_path)
                        pooled_path = []
                # 終盤端数分の処理
                write_result(pooled_path)
        process_time = time.time() - start
        print(process_time)