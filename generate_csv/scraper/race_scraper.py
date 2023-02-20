from generate_csv import mylib
from netkeiba.netkeiba.spiders import mylib as crawl_mylib

def scrape_from_page(race_html_path):
    html = mylib.read_html(race_html_path)

    result_table_rows = html.xpath('//table[@class="race_table_01 nk_tb_common"]//tr[position()>1]')
    race_result_all = []
    for result_table_row in result_table_rows:
        owner = result_table_row.xpath("diary_snap_cut/td/a/@title")
        # 例外処理　URLリンクがついていないパターンがある
        if len(owner):
            owner = owner[0]
            owner_id = crawl_mylib.get_last_slash_word(result_table_row.xpath("diary_snap_cut/td/a/@href")[-1])
        else:
            owner = result_table_row.xpath("diary_snap_cut/td//text()")[-1].strip()
            owner_id = None

        """
        【注意】ファイルから取得する場合は、一部tdがdiary_snap_cutで囲われているためtdの要素数が一致しない
               ページ表示中はdiary_snap_cutで囲われなくなる。                    
        """
        race_result = {
            "race_id": race_html_path.stem,
            "horse_id": result_table_row.xpath("td[4]/a/@href")[0][7:-1],
            "sex": result_table_row.xpath("td[5]")[0].text[0],
            "age": result_table_row.xpath("td[5]")[0].text[1:],
            "tresen": result_table_row.xpath("td[13]")[0].text.strip()[1],  # 前後に多数の空白があるためstrip処理 ex.200006060207
            "trainer": result_table_row.xpath("td[13]/a/@title")[0],
            "trainer_id": crawl_mylib.get_last_slash_word(result_table_row.xpath("td[13]/a/@href")[0]),
            "owner": owner,  # 馬主は途中で変わることがある
            "owner_id": owner_id,
        }

        race_info = html.xpath("//diary_snap_cut/span")[0].text.split("/")
        race_result["turn"] = None  # Noneのパターンあり
        for i in ["左", "右", "直"]:
            if i in race_info[0]:
                race_result["turn"] = i
                break
        race_result["outside"] = "外" in race_info[0]
        race_result["start_time"] = race_info[-1].split(" : ", 1)[-1]
        race_result_all.append(race_result)
    return race_result_all


if __name__ == '__main__':
    input_html_dir = "D:/netkeiba/html_data/race/"
    # スクレイピング結果csvの出力先パス
    output_csv_path = "D:/netkeiba/csv_data/race.csv"

    mylib.Scraper(input_html_dir, output_csv_path, scrape_from_page)
