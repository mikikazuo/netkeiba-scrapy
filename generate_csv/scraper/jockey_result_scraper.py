from generate_csv import mylib


class JockeyResultScraper(mylib.Scraper):
    def scrape_from_page(self, html_path):
        html = mylib.read_html(html_path)
        result_all = []

        for result_row in html.xpath('//table/tr[position()>3]'):
            columns = ["order", "order_1_cnt", "order_2_cnt", "order_3_cnt", "order_out_cnt",
                       "grand_cnt", "grand_order_1_cnt", "special_cnt", "special_order_1_cnt",
                       "flat_cnt", "flat_order_1_cnt", "grass_cnt", "grass_order_1_cnt",
                       "dirt_cnt", "dirt_order_1_cnt", "order_1_normalize", "order_1_2_normalize",
                       "order_1_2_3_normalize", "prize"]
            columns = [f"jockey_result_{column}" for column in columns]
            result = {
                "jockey_id": html_path.stem,
                "jockey_result_year": result_row.xpath('td[@class="txt_c"]')[0].text
            }
            for i, val in enumerate(result_row.xpath('td[@class="txt_r"]//text()')):
                result[columns[i]] = val
            result_all.append(result)
        return result_all


if __name__ == '__main__':
    input_html_dir = "D:/netkeiba/html_data/jockey_result/"
    # スクレイピング結果csvの出力先パス
    output_csv_path = "D:/netkeiba/csv_data/jockey_result.csv"

    JockeyResultScraper(input_html_dir, output_csv_path)
