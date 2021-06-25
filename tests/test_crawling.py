import unittest
from bs4 import BeautifulSoup
import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
import crawling


class TestScorePage(unittest.TestCase):
    def setUp(self) -> None:
        score_url = 'https://baseball.yahoo.co.jp/npb/game/2021123456/score'

        self.scorePage = crawling.ScorePage(score_url)
        self.scorePageFarm = crawling.ScorePage(score_url)
        self.scorePageNoGame = crawling.ScorePage(score_url)

        with open('HTML/crowling/score.html', encoding='utf-8') as f:
            self.scorePage.soup = BeautifulSoup(f, 'html.parser')
        with open('HTML/crowling/score_farm.html', encoding='utf-8') as f:
            self.scorePageFarm.soup = BeautifulSoup(f, 'html.parser')
        with open('HTML/crowling/score_no_game.html', encoding='utf-8') as f:
            self.scorePageNoGame.soup = BeautifulSoup(f, 'html.parser')

    def test_score_page(self):
        self.assertEqual(self.scorePage.make_game_dir_name(), './HTML/2021/index/2021123456')

        self.assertFalse(self.scorePage.judge_farm())
        self.assertTrue(self.scorePageFarm.judge_farm())

        self.assertFalse(self.scorePage.judge_no_game())
        self.assertTrue(self.scorePageNoGame.judge_no_game())

        self.assertTrue(self.scorePage.judge_in_period(3, 25, 3, 27))
        self.assertTrue(self.scorePage.judge_in_period(3, 26, 3, 28))
        self.assertFalse(self.scorePage.judge_in_period(3, 27, 3, 29))


class TestIndexPage(unittest.TestCase):
    def setUp(self) -> None:
        index_url = 'https://baseball.yahoo.co.jp/npb/game/2021123456/score?index=1234567'

        self.indexPage = crawling.IndexPage(index_url)
        self.indexPageLast = crawling.IndexPage(index_url)

        with open('HTML/crowling/2021000095_0110100.html', encoding='utf-8') as f:
            self.indexPage.soup = BeautifulSoup(f, 'html.parser')

        with open('HTML/crowling/2021000095_score.html', encoding='utf-8') as f:
            self.indexPageLast.soup = BeautifulSoup(f, 'html.parser')

    def test_index_page(self):
        self.assertEqual(self.indexPage.get_next_url(),
                         'https://baseball.yahoo.co.jp/npb/game/2021000095/score?index=0110200')
        self.assertEqual(self.indexPageLast.get_next_url(), None)


class TestSchedulePage(unittest.TestCase):
    def setUp(self) -> None:
        schedule_url = 'https://baseball.yahoo.co.jp/npb/schedule/?date=2021-03-26'

        self.schedulePage = crawling.SchedulePage(schedule_url)
        self.scheduleNotGamePage = crawling.SchedulePage(schedule_url)

        with open('HTML/crowling/schedule_2021-03-26.html', encoding='utf-8') as f:
            self.schedulePage.soup = BeautifulSoup(f, 'html.parser')

        with open('HTML/crowling/schedule_2021-03-25.html', encoding='utf-8') as f:
            self.scheduleNotGamePage.soup = BeautifulSoup(f, 'html.parser')

    def test_schedule_page(self):
        self.assertEqual(self.schedulePage.fetch_game_url_list(),
                         ['https://baseball.yahoo.co.jp/npb/game/2021000096/',
                          'https://baseball.yahoo.co.jp/npb/game/2021000095/',
                          'https://baseball.yahoo.co.jp/npb/game/2021000097/',
                          'https://baseball.yahoo.co.jp/npb/game/2021000098/',
                          'https://baseball.yahoo.co.jp/npb/game/2021000099/',
                          'https://baseball.yahoo.co.jp/npb/game/2021000100/'])
        self.assertEqual(self.scheduleNotGamePage.fetch_game_url_list(), [])


class TestMakeScheduleUrlList(unittest.TestCase):
    def test_make_schedule_url_list(self):
        self.assertEqual(crawling.make_schedule_url_list(2021, 1, 31, 2, 1),
                         ['https://baseball.yahoo.co.jp/npb/schedule/?date=2021-01-31',
                          'https://baseball.yahoo.co.jp/npb/schedule/?date=2021-02-01'])


if __name__ == '__main__':
    unittest.main()
