import requests
import os
import re
from bs4 import BeautifulSoup
import time
import datetime


class Page:
    def __init__(self, url):
        self.url: str = url
        self.soup: BeautifulSoup = BeautifulSoup
        self.res: requests.models.Response = requests.models.Response()

    def send_request(self):
        self.res = requests.get(self.url)
        self.soup = BeautifulSoup(self.res.text, 'html.parser')

    def judge_not_found(self):
        if self.res.status_code == 404:
            return True
        else:
            return False


class ScorePage(Page):
    def make_game_dir_name(self) -> str:
        game_num: str = re.search('\d{10}', self.url).group()
        year: str = game_num[0:4]
        return fr'./HTML/{year}/index/{game_num}'

    def judge_farm(self) -> bool:
        tag = self.soup.find('th', class_='bb-splitsTable__head bb-splitsTable__head--bench')
        if tag is None:
            return True
        else:
            return False

    def judge_no_game(self):
        div_tag = self.soup.find('div', id='detail_footer_leftbox')
        status_text = div_tag.p.get_text()

        if status_text == 'ノーゲーム' or status_text == '試合中止':
            return True
        else:
            return False


class IndexPage(Page):
    def get_next_url(self):
        div_tag = self.soup.find('div', id='detail_footer_leftbox')
        status_text = div_tag.p.get_text()

        if status_text == '試合終了':
            return None

        # 本体
        p = self.soup.find('a', id='btn_next')
        url_dir = p.get('href')

        return 'https://baseball.yahoo.co.jp' + url_dir

    def storage_html(self, game_dir):
        index = self.url[-7:]
        with open(game_dir + rf'/{index}.html', 'w', encoding='utf-8') as f:
            f.write(self.res.text)
            print(f'Done: {game_dir}/{index}.html')


class StatsPage(Page):
    def storage_html(self):
        game_num: str = re.search('\d{10}', self.url).group()
        year: str = game_num[0:4]
        html_name: str = fr'./HTML/{year}/stats/{game_num}.html'

        with open(html_name, 'w', encoding='utf-8') as f:
            f.write(self.res.text)
            print(html_name)


def craw():
    def decision_date():
        dt_now = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9)))
        now_y_ = dt_now.year
        now_m_ = dt_now.month
        now_d_ = dt_now.day
        start_m_: int = int()
        start_d_: int = int()

        # npbの公式サイトから開幕日を取得
        res = requests.get(f'https://npb.jp/event/{now_y_}/')
        soup = BeautifulSoup(res.content, 'html.parser')

        p_list = soup.select('#layout > div.contents > div > p')

        for p in p_list:
            if 'セントラル・リーグ開幕' in str(p) and 'パシフィック・リーグ開幕' in str(p):
                split_list = str(p).split('br')
                month_1 = re.search(r'\d{1,2}月', split_list[0]).group()[:-1]
                month_2 = re.search(r'\d{1,2}月', split_list[1]).group()[:-1]

                day_1 = re.search(r'\d{1,2}日', split_list[0]).group()[:-1]
                day_2 = re.search(r'\d{1,2}日', split_list[1]).group()[:-1]

                month_1, month_2, day_1, day_2 = list(map(int, [month_1, month_2, day_1, day_2]))

                if month_1 * 100 + day_1 < month_2 * 100 + day_2:
                    start_m_ = month_1
                    start_d_ = day_1
                else:
                    start_m_ = month_2
                    start_d_ = day_2

            elif '第7戦' in str(p):
                last_date = str(p).split('br')[-1]
                last_month = int(re.search(r'\d{1,2}月', last_date).group()[:-1])
                last_day = int(re.search(r'\d{1,2}日', last_date).group()[:-1])


        if now_m_ * 100 + now_d_ > last_month*100 + last_day:
            return now_y_, last_month, last_day, start_m_, start_d_

        return now_y_, now_m_, now_d_, start_m_, start_d_

    def make_date_url_list(year: int, start_month: int, start_day: int, stop_month: int, stop_day: int) -> list:
        last_day_list: list = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]

        if (year % 4 == 0 and year % 100 != 0) or year % 400 == 0:
            last_day_list[1] = 29

        root_url: str = 'https://baseball.yahoo.co.jp/npb/game/'
        last_day_list[stop_month - 1] = stop_day

        date_url_list = []
        for month in range(start_month, stop_month + 1):
            first_day = 1 if month != start_month else start_day

            for day in range(first_day, last_day_list[month - 1] + 1):
                date_url: str = root_url + str(year) + str(month).zfill(2) + str(day).zfill(2)
                date_url_list.append(date_url)

        return date_url_list

    def fetch_game_html(url, game_dir_):
        index_page = IndexPage(url)

        time.sleep(1)
        index_page.send_request()

        #  404なら例外を投げる
        if index_page.judge_not_found():
            return Exception('Error:status_code404')

        index_page.storage_html(game_dir_)

        next_url = index_page.get_next_url()

        if next_url is None:
            return

        fetch_game_html(next_url, game_dir_)

    # 本体
    now_y, now_m, now_d, start_m, start_d = decision_date()

    for date_rul in make_date_url_list(now_y, start_m, start_d, now_m, now_d - 1):
        for game_no in range(1, 7):
            score_url: str = date_rul + str(game_no).zfill(2) + '/score'
            stats_url: str = date_rul + str(game_no).zfill(2) + '/stats'
            start_url = score_url + '?index=0110100'

            score_page = ScorePage(score_url)
            stats_page = StatsPage(stats_url)
            game_dir = score_page.make_game_dir_name()
            if os.path.exists(game_dir):
                continue

            time.sleep(1)
            score_page.send_request()

            if score_page.judge_not_found() or score_page.judge_farm():
                break
            elif score_page.judge_no_game():
                continue
            else:
                stats_page.send_request()
                stats_page.storage_html()

                os.mkdir(game_dir)
                fetch_game_html(start_url, game_dir)


if __name__ == '__main__':
    craw()
