import scraping as sp
import glob
import sqlite3
import os
from typing import Union, Tuple, List
import datetime
import re


class DbOperator:
    def __init__(self, db_name: str):
        self.db_path = f'./output_db/{db_name}.db'
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

    def close(self):
        self.cnn.close()

    def take_last_update_date(self) -> Union[str, None]:
        c = self.cnn.cursor()
        c.execute('SELECT max(date) from game_data')

        return c.fetchone()[0]

    def take_last_id_at_bat(self) -> int:
        cur = self.cnn.cursor()
        cur.execute('SELECT MAX(id) from data_at_bat')
        last_id_at_bat = cur.fetchone()[0]

        return 0 if last_id_at_bat is None else last_id_at_bat

    def take_game_id(self) -> int:
        if not os.path.exists(self.db_path):
            return 0

        cur = self.cnn.cursor()
        cur.execute('SELECT MAX(id) from game_data')

        game_id = cur.fetchone()[0]
        return 0 if game_id is None else game_id

    def write_pitch_data(self, insert_data_list: List[
        Tuple[int, int, bool, int, bool, int, int, str, str, str, str, str, str, str, str,
              str, str, str, int, int, str, int, str, int, int, int, int, str, int]]):
        cur = self.cnn.cursor()

        cur.executemany(
            'INSERT INTO pitch_data (id_at_bat, pitcher_id, pitcher_left, batter_id, batter_left, in_box_count, '
            'match_number_times, c, first, second, third, ss, lf, cf, rf, first_runner, second_runner, '
            'third_runner, number_pitch_at_bat, number_pitch_game, ball_type, speed, ball_result, strike_count, '
            'ball_count, top_coordinate, left_coordinate, steal, steal_non_pitch) '
            'VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
            insert_data_list)

        self.cnn.commit()

    def write_data_at_bat(self, insert_data: Tuple[int, int, str, str, int, int, str, str]):
        cur = self.cnn.cursor()
        cur.execute(
            'INSERT INTO data_at_bat (game_id, inning, attack_team, defense_team, out, rbi, result_big, result_small) '
            'Values (?, ?, ?, ?, ?, ?, ?, ?)', insert_data)
        self.cnn.commit()

    def write_game_data(self, insert_data: Tuple[str, str, str, int, int, int, int, int, int, int, int, int,
                                                 int, int, int, int, int, int, int, int, int, int, int, int,
                                                 int, int, int, int, int, int, int, int, int]):
        cur = self.cnn.cursor()
        cur.execute('INSERT INTO game_data (date, day_week, studiam, first_hits, second_hits, first_miss, second_miss,'
                    'first_point_1, first_point_2, first_point_3, first_point_4, first_point_5, first_point_6,'
                    'first_point_7, first_point_8, first_point_9, first_point_10, first_point_11, first_point_12,'
                    'first_total, second_point_1, second_point_2, second_point_3, second_point_4, second_point_5,'
                    'second_point_6, second_point_7, second_point_8, second_point_9, second_point_10, second_point_11,'
                    'second_point_12, second_total) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)', insert_data)
        self.cnn.commit()

    def write_batting_stats(self, insert_data_list: List[Tuple[int, int, float, int, int, int, int, int, int, int, int, int, int, int]]):
        cur = self.cnn.cursor()
        cur.executemany(
            'INSERT INTO batting_stats (player_id, game_id, avg, times_at_bat, run, hits, rbi, k, walks, hit_by_pitch,'
            'sacrifice, steal, miss, hr) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', insert_data_list)
        self.cnn.commit()

    def write_pitch_stats(self, insert_data_list: List[Tuple[int, int, int, float, int, int, int, int, int, int, int, int, int, int]]):
        cur = self.cnn.cursor()
        cur.executemany(
            'INSERT INTO pitch_stats (player_id, game_id, era, inning, pitch_num, batter_match_num, hits, hr, k,'
            'walks, hit_by_pitch, balk, run, er) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)', insert_data_list)
        self.cnn.commit()


class GameDbWriter:
    def __init__(self, dbOperator: DbOperator, stats_file, index_dir, start_id_at_bat, game_id):
        self.dbOperator: DbOperator = dbOperator
        self.stats_file = stats_file
        self.index_dir = index_dir
        self.id_at_bat = start_id_at_bat
        self.game_id = game_id

    def get_id_at_bat(self):
        return self.id_at_bat

    def write_index_dir(self):
        files = glob.glob(f'{self.index_dir}/*.html')
        start_num = 0

        for i, file in enumerate(files):
            print(f'write: {file}')
            if file == files[-1]:
                continue

            indexPage = sp.IndexPageScraper(file)
            pdd = indexPage.get_pitch_data_dict()

            if indexPage.judge_non_butter():
                continue

            save_pitch_data_list = []
            for ball_data in pdd['ball_data_list']:
                save_pitch_data_list.append((self.id_at_bat, pdd['pitcher_id'], pdd['pitcher_left'], pdd['batter_id'],
                                             pdd['batter_left'], pdd['num_at_bat'], pdd['match_batter_number'],
                                             pdd['c'], pdd['first'], pdd['second'], pdd['third'], pdd['ss'], pdd['lf'],
                                             pdd['cf'], pdd['rf'], pdd['first_runner'], pdd['second_runner'],
                                             pdd['third_runner'], ball_data['pitch_number_in_at_bat'],
                                             ball_data['pitch_number_in_game'], ball_data['type_of_pitch'], ball_data['speed'],
                                             ball_data['pitch_result_text'], ball_data['strike_count'], ball_data['ball_count'],
                                             ball_data['top'], ball_data['left'], pdd['write_steal'], pdd['steal_non_pitch']))

            if files[i][-9:-7] != files[i + 1][-9:7]:
                inning = int(file[-12:-10])
                save_bat_data = (self.game_id, inning, pdd['attack_team'], pdd['defense_team'], pdd['out'], pdd['rbi'],
                                 pdd['result_big'], pdd['result_small'])
                self.dbOperator.write_data_at_bat(save_bat_data)
                self.dbOperator.write_pitch_data(save_pitch_data_list)
                self.id_at_bat += 1
                start_num = 0
            else:
                self.dbOperator.write_pitch_data(save_pitch_data_list[start_num:])
                start_num = len(save_pitch_data_list)

    def write_stats_file(self):
        statsPage = sp.StatsPageScraper(self.stats_file)
        game_date, day_week = statsPage.take_date()
        game_stadium = statsPage.take_stadium()
        point_board = statsPage.take_point_board()
        fb: dict = point_board[0]  # first point board
        sb: dict = point_board[1]  # second point board
        player_stats = statsPage.take_player_stats()
        batting_stats_list = player_stats[0]
        pitching_stats_list = player_stats[1]

        save_game_data = (game_date, day_week, game_stadium, fb['hits'], sb['hits'], fb['miss'], sb['miss'],
                          fb[1], fb[2], fb[3], fb[4], fb[5], fb[6], fb[7], fb[8], fb[9], fb[10], fb[11], fb[12],
                          fb['total'],
                          sb[1], sb[2], sb[3], sb[4], sb[5], sb[6], sb[7], sb[8], sb[9], sb[10], sb[11], sb[12],
                          sb['total'])

        save_batting_stats_list = []
        for bs in batting_stats_list:
            save_batting_stats_list.append((bs['player_id'], self.game_id, bs['avg'], bs['times_at_bat'], bs['run'],
                                            bs['hits'], bs['rbi'], bs['k'], bs['walks'], bs['hit_by_pitch'],
                                            bs['sacrifice'],
                                            bs['steal'], bs['miss'], bs['hr']))

        save_pitch_stats_list = []
        for ps in pitching_stats_list:
            save_pitch_stats_list.append((ps['player_id'], self.game_id, ps['era'], ps['inning'], ps['pitch_num'],
                                          ps['batter_match_num'], ps['hits'], ps['hr'], ps['k'], ps['walks'],
                                          ps['hit_by_pitch'], ps['balk'], ps['run'], ps['er']))

        self.dbOperator.write_game_data(save_game_data)
        self.dbOperator.write_pitch_stats(save_pitch_stats_list)
        self.dbOperator.write_batting_stats(save_batting_stats_list)


def write_db(db_name: str, year: int):
    if not os.path.exists('./output_db'):
        os.mkdir('./output_db')

    stats_files = sorted(glob.glob(f'./HTML/{year}/stats/*.html'))
    index_dirs = sorted(glob.glob(f'./HTML/{year}/index/*'))

    dbOperator = DbOperator(db_name)
    id_at_bat = dbOperator.take_last_id_at_bat()
    game_id = dbOperator.take_game_id()
    last_update_date_str = dbOperator.take_last_update_date()

    for stats_file, index_dir in zip(stats_files, index_dirs):
        statsPage = sp.StatsPageScraper(stats_file)
        stats_date_str = statsPage.take_date()[0]
        stats_date = datetime.datetime.strptime(stats_date_str, '%Y-%m-%d')

        if last_update_date_str is None:
            last_update_date = datetime.datetime(year, 1, 1)
        else:
            last_update_date = datetime.datetime.strptime(last_update_date_str, '%Y-%m-%d')

        if stats_date <= last_update_date:
            continue

        gameDbWriter = GameDbWriter(dbOperator, stats_file, index_dir, id_at_bat, game_id)
        gameDbWriter.write_index_dir()
        gameDbWriter.write_stats_file()

        id_at_bat = gameDbWriter.get_id_at_bat()
        game_id += 1

    dbOperator.close()
