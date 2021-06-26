import glob
import re
import scraping as sp
import sqlite3
from typing import List, Tuple
from bs4 import BeautifulSoup
import crawling


class MemberPage(crawling.Page):
    player_list: list = []

    @classmethod
    def append_player_url_list(cls, player_url: str) -> None:
        cls.player_list.append(player_url)

    @classmethod
    def get_player_url_list(cls) -> list:
        return cls.player_list

    def fetch_players(self) -> list:
        url_list: list = []
        root_url = 'https://baseball.yahoo.co.jp'
        tr_list = self.soup.select('#tm_plyr > tr')

        for tr in tr_list:
            td_list = tr.select('td')
            player_profile_url = root_url + td_list[1].a.get('href')
            url_list.append(player_profile_url)
            self.append_player_url_list(player_profile_url)

        return url_list


class PlayerPage(crawling.Page):
    def storage_html(self) -> None:
        player_id = self.url.split('/')[5]
        player_dir: str = f'./HTML/player'
        html_name: str = f'{player_id}.html'

        with open(player_dir + '/' + html_name, 'w', encoding='utf-8') as f:
            f.write(self.res.text)
            print(f'Done(player): {player_id}')


class PlayerDbWrite:
    def __init__(self, db_name: str):
        self.db_path = f'./{db_name}.db'
        self.cnn = sqlite3.connect(self.db_path)

        self.make_db_table()

    def make_db_table(self):
        c = self.cnn.cursor()

        # pitch_data
        c.execute('CREATE TABLE IF NOT EXISTS pitch_data('
                  'id INTEGER PRIMARY KEY, '
                  'id_at_bat INTEGER NOT NULL, '
                  'pitcher_id INTEGER NOT NULL, '
                  'pitcher_left INTEGER NOT NULL, '
                  'batter_id INTEGER  NOT NULL, '
                  'batter_left INTEGER NOT NULL, '
                  'in_box_count INTEGER NOT NULL, '
                  'match_number_times INTEGER NOT NULL, '
                  'c TEXT NOT NULL, '
                  'first TEXT NOT NULL, '
                  'second TEXT NOT NULL, '
                  'third TEXT NOT NULL, '
                  'ss TEXT NOT NULL, '
                  'lf TEXT NOT NULL, '
                  'cf TEXT NOT NULL, '
                  'rf TEXT NOT NULL, '
                  'first_runner TEXT, '
                  'second_runner TEXT, '
                  'third_runner TEXT, '
                  'number_pitch_at_bat INTEGER NOT NULL, '
                  'number_pitch_game INTEGER NOT NULL, '
                  'ball_type TEXT NOT NULL, '
                  'speed INTEGER, '
                  'ball_result TEXT NOT NULL, '
                  'strike_count INTEGER NOT NULL, '
                  'ball_count INTEGER NOT NULL, '
                  'top_coordinate INTEGER NOT NULL, '
                  'left_coordinate INTEGER NOT NULL, '
                  'steal TEXT, '
                  'steal_non_pitch INTEGER)')

        # data_at_bat
        c.execute('CREATE TABLE IF NOT EXISTS data_at_bat( '
                  'id INTEGER PRIMARY KEY, '
                  'game_id INTEGER NOT NULL, '
                  'inning INTEGER NOT NULL, '
                  'attack_team TEXT NOT NULL, '
                  'defense_team TEXT NOT NULL, '
                  'out INTEGER NOT NULL, '
                  'rbi INTEGER NOT NULL, '
                  'result_big TEXT NOT NULL, '
                  'result_small TEXT NOT NULL)')

        # player
        c.execute('CREATE TABLE IF NOT EXISTS player( '
                  'id INTEGER PRIMARY KEY, '
                  'name text NOT NULL, '
                  'team text NOT NULL, '
                  'uniform_number TEXT NOT NULL, '
                  'position text NOT NULL, '
                  'date_of_birth date, '
                  'height integer, '
                  'weight integer, '
                  'throw_arm text, '
                  'batting_arm text, '
                  'draft_year integer, '
                  'draft_rank text, '
                  'total_year integer)')

        # game_data
        c.execute('CREATE TABLE IF NOT EXISTS game_data('
                  'id INTEGER PRIMARY KEY, '
                  'date DATE NOT NULL, '
                  'day_week TEXT NOT NULL, '
                  'studiam TEXT NOT NULL, '
                  'first_hits INTEGER NOT NULL, '
                  'second_hits INTEGER NOT NULL, '
                  'first_miss INTEGER NOT NULL, '
                  'second_miss INTEGER NOT NULL, '
                  'first_point_1 INTEGER, '
                  'first_point_2 INTEGER , '
                  'first_point_3 INTEGER, '
                  'first_point_4 INTEGER, '
                  'first_point_5 INTEGER, '
                  'first_point_6 INTEGER, '
                  'first_point_7 INTEGER, '
                  'first_point_8 INTEGER, '
                  'first_point_9 INTEGER, '
                  'first_point_10 INTEGER, '
                  'first_point_11 INTEGER, '
                  'first_point_12 INTEGER, '
                  'first_total INTEGER NOT NULL, '
                  'second_point_1 INTEGER, '
                  'second_point_2 INTEGER, '
                  'second_point_3 INTEGER, '
                  'second_point_4 INTEGER, '
                  'second_point_5 INTEGER, '
                  'second_point_6 INTEGER, '
                  'second_point_7 INTEGER, '
                  'second_point_8 INTEGER, '
                  'second_point_9 INTEGER, '
                  'second_point_10 INTEGER, '
                  'second_point_11 INTEGER, '
                  'second_point_12 INTEGER, '
                  'second_total INTEGER NOT NULL)')

        # batting_stats
        c.execute('CREATE TABLE IF NOT EXISTS batting_stats('
                  'id INTEGER PRIMARY KEY, '
                  'player_id INTEGER NOT NULL, '
                  'game_id INTEGER NOT NULL, '
                  'avg REAL, '
                  'times_at_bat INTEGER NOT NULL, '
                  'run INTEGER NOT NULL, '
                  'hits INTEGER NOT NULL, '
                  'rbi INTEGER NOT NULL, '
                  'k INTEGER NOT NULL, '
                  'walks INTEGER NOT NULL, '
                  'hit_by_pitch INTEGER NOT NULL, '
                  'sacrifice INTEGER NOT NULL, '
                  'steal INTEGER NOT NULL, '
                  'miss INTEGER NOT NULL, '
                  'hr INTEGER NOT NULL)')

        # pitch_stats
        c.execute('CREATE TABLE IF NOT EXISTS pitch_stats( '
                  'id INTEGER PRIMARY KEY, '
                  'player_id INTEGER NOT NULL, '
                  'game_id INTEGER NOT NULL, '
                  'era INTEGER, '
                  'inning REAL NOT NULL, '
                  'pitch_num INTEGER NOT NULL, '
                  'batter_match_num INTEGER NOT NULL, '
                  'hits INTEGER NOT NULL, '
                  'hr INTEGER NOT NULL, '
                  'k INTEGER NOT NULL, '
                  'walks INTEGER NOT NULL, '
                  'hit_by_pitch INTEGER NOT NULL, '
                  'balk INTEGER NOT NULL, '
                  'run INTEGER NOT NULL, '
                  'er INTEGER NOT NULL)')

        self.cnn.commit()

    def write_player(self, insert_data_list: List[Tuple[str, str, int, str, str, int, int, str, str, int, str, int]]):
        cur = self.cnn.cursor()
        cur.executemany(
            'INSERT INTO player VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
            insert_data_list)
        self.cnn.commit()

    def take_player_id_list(self) -> List[Tuple[int]]:
        c = self.cnn.cursor()
        c.execute('select id from player')
        player_list = c.fetchall()

        return player_list


def write_db():
    db_name = 'test'
    playerDbWriter = PlayerDbWrite(db_name)
    player_files = glob.glob('./HTML/player/*.html')
    player_id_list = playerDbWriter.take_player_id_list()

    save_data_list = []
    for file in player_files:
        playerPage = sp.PlayerPageScraper(file)
        pdd = playerPage.take_player_profile()  # player_data_dict
        player_id = int(re.sub('\D+', '', file))

        if (player_id,) in player_id_list:
            continue

        save_data_list.append(
            (player_id, pdd['player_name'], pdd['team_name'], pdd['uniform_number'], pdd['position'],
             pdd['date_of_birth'], pdd['height'], pdd['weight'], pdd['throw_arm'],
             pdd['batting_arm'], pdd['draft_year'], pdd['draft_rank'], pdd['total_year']))

    playerDbWriter.write_player(save_data_list)


def fetch_player_html():
    team_number_list = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '11', '12', '376']
    root_url = 'https://baseball.yahoo.co.jp/npb/teams'

    for team_num in team_number_list:
        exec(f'team_url_p = root_url + "/{team_num}/memberlist?kind=p"')
        exec(f'team_url_b = root_url + "/{team_num}/memberlist?kind=b"')
        exec(f'memberPage{team_num}p = MemberPage(team_url_p)')
        exec(f'memberPage{team_num}b = MemberPage(team_url_b)')
        exec(f'memberPage{team_num}p.send_request()')
        exec(f'memberPage{team_num}b.send_request()')
        exec(f'memberPage{team_num}p.fetch_players()')
        exec(f'memberPage{team_num}b.fetch_players()')

    memberPage = MemberPage('')
    player_url_list = memberPage.get_player_url_list()

    for player_url in player_url_list:
        playerPage = PlayerPage(player_url)

        playerPage.send_request()
        playerPage.storage_html()


if __name__ == '__main__':
    fetch_player_html()
