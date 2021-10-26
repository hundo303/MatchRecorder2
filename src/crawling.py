import requests
import os
import re
from bs4 import BeautifulSoup
import time
import datetime
from typing import Union, List, Tuple


class Page:
    def __init__(self, url: str):
        self.url: str = url
        self.soup = None
        self.res: requests.models.Response = requests.models.Response()

    def send_request(self) -> None:
        time.sleep(0.5)
        self.res = requests.get(self.url)
        self.soup = BeautifulSoup(self.res.text, 'html.parser')

    def judge_not_found(self) -> bool:
        if self.res.status_code == 404:
            return True
        else:
            return False


class GamePage(Page):
    def __init__(self, url):
        super().__init__(url)
        self.game_num: str = re.search('\d{10}', self.url).group()
        self.year: str = self.game_num[0:4]


class ScorePage(GamePage):
    def make_game_dir_name(self) -> str:
        return fr'./HTML/{self.year}/index/{self.game_num}'

    def judge_farm(self) -> bool:
        tag = self.soup.find('th', class_='bb-splitsTable__head bb-splitsTable__head--bench')
        if tag is None:
            return True
        else:
            return False

    def judge_no_game(self) -> bool:
        div_tag = self.soup.find('div', id='detail_footer_leftbox')
        status_text = div_tag.p.get_text()

        if status_text == 'ノーゲーム' or status_text == '試合中止':
            return True
        else:
            return False

    def judge_in_period(self, start_m: int, start_d: int, stop_m: int, stop_d: int) -> bool:
        p = self.soup.select_one('#contentMain > div > div.bb-main > div.bb-modCommon02 > p.bb-gameDescription')
        game_month = int(re.search(r'\d{1,2}月', str(p)).group()[:-1])
        game_day = int(re.search(r'\d{1,2}日', str(p)).group()[:-1])
        game_num = game_month * 100 + game_day

        start_num = start_m * 100 + start_d
        stop_num = stop_m * 100 + stop_d

        return start_num <= game_num <= stop_num


class IndexPage(GamePage):
    def get_next_url(self) -> Union[str, None]:
        div_tag = self.soup.select_one('#liveinfo')
        status_text = div_tag.p.get_text()

        if status_text == '試合終了':
            return None

        # 本体
        p = self.soup.find('a', id='btn_next')
        url_dir = p.get('href')

        return 'https://baseball.yahoo.co.jp' + url_dir

    def storage_html(self, game_dir: str) -> None:
        index = self.url[-7:]
        with open(game_dir + rf'/{index}.html', 'w', encoding='utf-8') as f:
            f.write(self.res.text)
            print(f'Done: {game_dir}/{index}.html')


class StatsPage(GamePage):
    def storage_html(self) -> None:
        stats_dir: str = fr'./HTML/{self.year}/stats/'
        html_name: str = f'{self.game_num}.html'

        with open(stats_dir + html_name, 'w', encoding='utf-8') as f:
            f.write(self.res.text)
            print('Done(stats): ' + stats_dir + html_name)


class SchedulePage(Page):
    def __init__(self, url: str, year: int):
        super().__init__(url)
        self.schedule_path = f'./HTML/{year}/schedule/{url[-10:]}.html'

    def fetch_game_url_list(self) -> List[str]:
        game_url_list: list = []
        above_list: list = []
        under_list: list = []

        above_list_name = self.soup.select_one('#gm_card > section:nth-child(1) > header > h1').text
        under_list_name = self.soup.select_one('#gm_card > section:nth-child(2) > header > h1').text

        if above_list_name == 'セ・リーグ' or above_list_name == 'パ・リーグ' or above_list_name == 'セ・パ交流戦':
            above_list = self.soup.select('#gm_card > section:nth-child(1) > ul > li > a')
        if under_list_name == 'セ・リーグ' or under_list_name == 'パ・リーグ' or above_list_name == 'セ・パ交流戦':
            under_list = self.soup.select('#gm_card > section:nth-child(2) > ul > li > a')

        for game in above_list + under_list:
            game_url_list.append(game.get('href'))
        return list(map(lambda url: url.replace('index', ''), game_url_list))

    def storage_html(self):
        with open(self.schedule_path, 'w', encoding='utf-8') as f:
            f.write(self.res.text)

    def set_soup(self):
        if os.path.exists(self.schedule_path):
            with open(self.schedule_path, encoding='utf-8 ') as f:
                self.soup = BeautifulSoup(f, 'html.parser')
        else:
            self.send_request()
            self.storage_html()


def craw(now_y: int = None, start_m: int = None, start_d: int = None, stop_m: int = None, stop_d: int = None) -> None:
    # 入力された日付に1つでもNoneがあればこちら側で決める
    if any(arg is None for arg in [now_y, start_m, start_d, stop_m, stop_d]):
        now_y, start_m, start_d, stop_m, stop_d = decision_date()

    make_dir_if_not_exists(now_y)

    schedule_rul_list = make_schedule_url_list(now_y, start_m, start_d, stop_m, stop_d)
    for schedule_url in schedule_rul_list:
        schedulePage = SchedulePage(schedule_url, now_y)
        schedulePage.set_soup()

        game_url_list = schedulePage.fetch_game_url_list()

        for game_url in game_url_list:
            score_url: str = game_url + 'score'
            stats_url: str = game_url + 'stats'
            start_url = score_url + '?index=0110100'

            scorePage = ScorePage(score_url)
            statsPage = StatsPage(stats_url)
            game_dir = scorePage.make_game_dir_name()
            if os.path.exists(game_dir):
                print('skip: ' + game_dir)
                continue

            scorePage.send_request()

            if scorePage.judge_no_game():
                continue
            else:
                statsPage.storage_html()

                os.mkdir(game_dir)
                fetch_game_html(start_url, game_dir)


# 良い感じに範囲決めてくれるやつ
def decision_date() -> Tuple[int, int, int, int, int]:
    dt_now = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9)))
    now_y = dt_now.year
    now_m = dt_now.month
    now_d = dt_now.day
    start_m: int = int()
    start_d: int = int()
    last_month: int = -1
    last_day: int = -1

    # npbの公式サイトから開幕日を取得
    res = requests.get(f'https://npb.jp/event/{now_y}/')
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
                start_m = month_1
                start_d = day_1
            else:
                start_m = month_2
                start_d = day_2

        elif '第7戦' in str(p):
            last_date = str(p).split('br')[-1]
            last_month = int(re.search(r'\d{1,2}月', last_date).group()[:-1])
            last_day = int(re.search(r'\d{1,2}日', last_date).group()[:-1])

    if last_month == -1 or last_day == -1:
        Exception('シーズン終了日の取得に失敗しました')
    elif now_m * 100 + now_d > last_month * 100 + last_day:
        return now_y, start_m, start_d, last_month, last_day

    return now_y, start_m, start_d, now_m, now_d - 1


# 範囲内の試合のscheduleページのurlを生成
def make_schedule_url_list(year: int, start_month: int, start_day: int, stop_month: int, stop_day: int) -> List[str]:
    last_day_list: list = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]

    if (year % 4 == 0 and year % 100 != 0) or year % 400 == 0:
        last_day_list[1] = 29

    root_url: str = 'https://baseball.yahoo.co.jp/npb/schedule/?date='
    last_day_list[stop_month - 1] = stop_day

    date_url_list = []
    for month in range(start_month, stop_month + 1):
        first_day = 1 if month != start_month else start_day
        for day in range(first_day, last_day_list[month - 1] + 1):
            date_url: str = root_url + str(year) + '-' + str(month).zfill(2) + '-' + str(day).zfill(2)
            date_url_list.append(date_url)

    return date_url_list


def fetch_game_html(url: str, game_dir: str):
    index_page = IndexPage(url)

    index_page.send_request()

    #  404なら例外を投げる
    if index_page.judge_not_found():
        return Exception('Error:status_code404: ', url)

    index_page.storage_html(game_dir)

    next_url = index_page.get_next_url()

    if next_url is None:
        return

    fetch_game_html(next_url, game_dir)


def make_dir_if_not_exists(year: int):
    html_dir = './HTML'
    player_dir = './HTML/player'
    year_dir = f'./HTML/{year}'
    stats_dir = year_dir + '/stats'
    index_dir = year_dir + '/index'
    schedule_dir = year_dir + '/schedule'

    if not os.path.exists(html_dir):
        os.mkdir(html_dir)
    if not os.path.exists(player_dir):
        os.mkdir(player_dir)
    if not os.path.exists(year_dir):
        os.mkdir(year_dir)
    if not os.path.exists(stats_dir):
        os.mkdir(stats_dir)
    if not os.path.exists(index_dir):
        os.mkdir(index_dir)
    if not os.path.exists(schedule_dir):
        os.mkdir(schedule_dir)
