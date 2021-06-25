import unittest
from bs4 import BeautifulSoup
import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
import scraping


class TestIndexPageScraper(unittest.TestCase):
    def setUp(self) -> None:
        index_path = 'HTML/scraping/2021000095_0110100.html'
        foul_path = 'HTML/scraping/2021000095_0120500.html'
        out_path = 'HTML/scraping/2021000095_0110100.html'
        not_out_path = 'HTML/scraping/2021000095_0120100.html'
        in_second_at_bat_path = 'HTML/scraping/2021000095_0210700.html'
        in_fourth_at_bat_path = 'HTML/scraping/2021000095_0810200.html'
        non_batter_path = 'HTML/scraping/2021000095_0410000.html'

        self.indexPage = scraping.IndexPageScraper(index_path)
        self.foulPage = scraping.IndexPageScraper(foul_path)
        self.outPage = scraping.IndexPageScraper(out_path)
        self.notOutPage = scraping.IndexPageScraper(not_out_path)
        self.secondPage = scraping.IndexPageScraper(in_second_at_bat_path)
        self.fourthPage = scraping.IndexPageScraper(in_fourth_at_bat_path)
        self.nonButterPage = scraping.IndexPageScraper(non_batter_path)

        self.indexPage.take_result_at_bat()
        self.secondPage.take_result_at_bat()

    def test_index_page_scraper(self):
        self.assertEqual(self.foulPage.take_ball_data_list(),
                         [(1, 18, 'ストレート', 141, 'ボール', 0, 0, 22, 129),
                          (2, 19, 'フォーク', 134, 'ボール[ワンバウンド]', 0, 1, 172, 94),
                          (3, 20, 'ストレート', 142, 'ファウル', 0, 2, 104, 104),
                          (4, 21, 'ストレート', 142, '見逃し', 1, 2, 67, 90),
                          (5, 22, 'ストレート', 145, 'ファウル', 2, 2, 120, 33),
                          (6, 23, 'フォーク', 135, 'ボール', 2, 2, 171, 119),
                          (7, 24, 'チェンジアップ', 125, '四球[ワンバウンド]', 2, 3, 172, 20)])

        self.assertTrue(self.outPage.judge_out())
        self.assertFalse(self.notOutPage.judge_out())

        self.assertEqual(self.indexPage.take_date(), (3, 26, '金'))

        self.assertEqual(self.indexPage.take_match_player_data(), (1200041, False, 1100061, False))
        self.assertEqual(self.notOutPage.take_match_player_data(), (1600081, True, 700027, True))

        self.assertEqual(self.indexPage.take_num_at_bat(), 1)
        self.assertEqual(self.secondPage.take_num_at_bat(), 2)

        self.assertEqual(self.indexPage.take_match_batter_number(), 0)
        self.assertEqual(self.secondPage.take_match_batter_number(), 9)
        self.assertEqual(self.fourthPage.take_match_batter_number(), 1)

        self.assertEqual(self.indexPage.take_defense(),
                         ('大城卓三', 'ウィーラー', '若林晃弘', '岡本和真', '坂本勇人', '松原聖弥', '丸佳浩', '梶谷隆幸'))

        self.assertEqual(self.indexPage.take_result_at_bat(), ('見逃し三振', '135km/h スライダー'))
        self.assertEqual(self.foulPage.take_result_at_bat(), ('四球', '125km/h チェンジアップ、ワンバウンド、ランナー満塁'))

        self.assertEqual(self.foulPage.take_runner(), (None, '岡本和', '坂本'))

        self.assertEqual(self.indexPage.take_rbi(), 0)
        self.assertEqual(self.secondPage.take_rbi(), 1)

        self.assertEqual(self.indexPage.take_match_team(), ('DeNA', "巨人"))

        self.assertTrue(self.nonButterPage.judge_non_butter())
        self.assertFalse(self.indexPage.judge_non_butter())


class TestPlayerPageScraper(unittest.TestCase):
    def setUp(self) -> None:
        matsuzaka_path = './HTML/scraping/player_11715.html'
        self.matsuzakaPage = scraping.PlayerPageScraper(matsuzaka_path)

    def test_player_page_scraper(self):
        self.assertEqual(self.matsuzakaPage.take_player_profile(),
                         {'player_name': '松坂大輔', 'team_name': '西武', 'uniform_number': 16,
                          'position': '投手', 'date_of_birth': '1980-9-13', 'height': 182,
                          'weight': 92, 'throw_arm': '右', 'batting_arm': '右', 'draft_year': 1998,
                          'draft_rank': '1位', 'total_year': 15})


if __name__ == '__main__':
    unittest.main()
