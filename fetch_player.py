import glob
import re
import scraping as sp
import sqlite3
from typing import List, Tuple
from bs4 import BeautifulSoup
import crawling
import write_db as wd


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


class PlayerDbWrite(wd.DbOperator):
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
    player_db_writer = PlayerDbWrite(db_name)
    player_files = glob.glob('./HTML/player/*.html')
    player_id_list = player_db_writer.take_player_id_list()

    save_data_list = []
    for file in player_files:
        player_page = sp.PlayerPageScraper(file)
        pdd = player_page.take_player_profile()  # player_data_dict
        player_id = int(re.sub('\D+', '', file))

        if (player_id,) in player_id_list:
            continue

        save_data_list.append(
            (player_id, pdd['player_name'], pdd['team_name'], pdd['uniform_number'], pdd['position'],
             pdd['date_of_birth'], pdd['height'], pdd['weight'], pdd['throw_arm'],
             pdd['batting_arm'], pdd['draft_year'], pdd['draft_rank'], pdd['total_year']))

    player_db_writer.write_player(save_data_list)


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
    write_db()
