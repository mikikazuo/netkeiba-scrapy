from generate_csv import mylib
from netkeiba.netkeiba.spiders import mylib as crawl_mylib


class RaceScraper(mylib.Scraper):
    def scrape_from_page(self, html_path):
        html = mylib.read_html(html_path)
        result_all = []

        for horse_row in html.xpath('//table[@class="race_table_01 nk_tb_common"]//tr[position()>1]'):
            owner = horse_row.xpath("diary_snap_cut/td/a/@title")
            # 例外処理　URLリンクがついていないパターンがある
            if len(owner):
                owner = owner[0]
                owner_id = crawl_mylib.get_last_slash_word(horse_row.xpath("diary_snap_cut/td/a/@href")[-1])
            else:
                owner = horse_row.xpath("diary_snap_cut/td//text()")[-1].strip()
                owner_id = None

            """
            【注意】ファイルから取得する場合は、一部tdがdiary_snap_cutで囲われているためtdの要素数が一致しない
                   ページ表示中はdiary_snap_cutで囲われなくなる。                    
            """
            result = {
                "race_id": html_path.stem,
                "horse_id": crawl_mylib.get_last_slash_word(horse_row.xpath("td[4]/a/@href")[0]),
                "sex": horse_row.xpath("td[5]")[0].text[0],
                "age": horse_row.xpath("td[5]")[0].text[1:],
                "tresen": horse_row.xpath("td[13]")[0].text.strip()[1],  # 前後に多数の空白があるためstrip処理 ex.200006060207
                "trainer": horse_row.xpath("td[13]/a/@title")[0],
                "trainer_id": crawl_mylib.get_last_slash_word(horse_row.xpath("td[13]/a/@href")[0]),
                "owner": owner,  # 馬主は途中で変わることがある
                "owner_id": owner_id,
            }

            race_info = html.xpath("//diary_snap_cut/span")[0].text.split("/")
            result["turn"] = None  # Noneのパターンあり
            for i in ["左", "右", "直"]:
                if i in race_info[0]:
                    result["turn"] = i
                    break
            result["outside"] = "外" in race_info[0]
            result["start_time"] = race_info[-1].split(" : ", 1)[-1]
            result_all.append(result)
        return result_all


if __name__ == '__main__':
    input_html_dir = "D:/netkeiba/html_data/race/"
    # スクレイピング結果csvの出力先パス
    output_csv_path = "D:/netkeiba/csv_data/race.csv"

    RaceScraper(input_html_dir, output_csv_path, (2017, 2030))
