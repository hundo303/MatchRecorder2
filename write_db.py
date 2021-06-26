import scraping as sp
import glob
import sqlite3
import os
from typing import Union, Tuple


class DbOperator:
    def __init__(self, db_name: str):
        self.db_path = f'./{db_name}.db'
        self.cnn = sqlite3.connect(self.db_path)

        self.make_db_table()

    def make_db_table(self):
        c = self.cnn.cursor()

        # pitch_data
        c.execute('CREATE TABLE IF NOT EXISTS pitch_data('
                  'id INTEGER PRIMARY KEY AUTOINCREMENT, '
                  'id_at_bat INTEGER NOT NULL '
                  'pitcher_id INTEGER NOT NULL, '
                  'pircher_left INTEGER NOT NULL, '
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
                  'id INTEGER PRIMARY KEY AUTOINCREMENT, '
                  'game_id INTEGER NOT NULL '
                  'inning INTEGER NOT NULL, '
                  'attack_team TEXT NOT NULL, '
                  'defense_team TEXT NOT NULL, '
                  'out INTEGER NOT NULL, '
                  'rbi INTEGER NOT NULL, '
                  'result_big TEXT NOT NULL, '
                  'result_small TEXT NOT NULL)')

        # player
        c.execute('CREATE TABLE IF NOT EXISTS player( '
                  'id INTEGER PRIMARY KEY AUTOINCREMENT, '
                  'name text NOT NULL, '
                  'team text NOT NULL, '
                  'uniform_number integer NOT NULL, '
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
                  'id INTEGER PRIMARY KEY AUTOINCREMENT, '
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

        # pitch_stats
        c.execute('CREATE TABLE IF EXISTS pitch_stats( '
                  'id INTEGER PRIMARY KEY AUTOINCREMENT, '
                  'player_id INTEGER NOT NULL, '
                  'game_id INTEGER NOT NULL'
                  'avg REAL NOT NULL, '
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

        # batting_stats
        c.execute('CREATE TABLE IF EXISTS batting_stats( '
                  'id INTEGER PRIMARY KEY AUTOINCREMENT, '
                  'player_id INTEGER NOT NULL, '
                  'game_id INTEGER NOT NULL, '
                  'era INTEGER, '
                  'inning REAL NOT NULL'
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

    def take_last_update_date(self) -> Union[str, None]:
        if not os.path.exists(self.db_path):
            return None

        c = self.cnn.cursor()

        c.execute('SELECT max(date) from game_data')
        return c.fetchone()[0]

    def take_last_id_at_bat(self) -> int:
        if not os.path.exists(self.db_path):
            return 0

        cur = self.cnn.cursor()
        cur.execute('SELECT MAX(id) from data_at_bat')
        return cur.fetchone()[0]

    def write_pitch_data(self, insert_data: Tuple[int, int, int, int, int, int, int, str, str, str, str, str, str, str, str,
                                                  str, str, str, int, int, str, int, str, int, int, int, int, str, int]):
        cur = self.cnn.cursor()
        # insert_data = (pitcher_id, pitcher_left, batter_id, batter_left, in_box_count, match_number_times, c, first, second,
        #               third, ss, lf, cf, rf, first_runner, second_runner, third_runner, number_pitch_at_bat,
        #               number_pitch_game, ball_type, speed, strike_result, ball_count, top_coordinate, left_coordinate, steal,
        #               steal_non_pitch)
        cur.execute('INSERT INTO pitch_data (id_at_bat, pitcher_id, pitcher_left, batter_id, batter_left, in_box_count, '
                    'match_number_times, c, first, second, third, ss, lf, cf, rf, first_runner, second_runner, '
                    'third_runner, number_pitch_at_bat, number_pitch_game, ball_type, speed, strike_result, '
                    'ball_count, top_coordinate, left_coordinate, steal, steal_non_pitch) '
                    'VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
                    insert_data)

        self.cnn.commit()

    def write_data_at_at(self, insert_data: Tuple[int, int, str, str, int, int, str, str]):
        cur = self.cnn.cursor()
        cur.execute('INSERT INTO data_at_bat (inning, game_id, attack_tem, defense_team, out, rbi, result_big, result_small) '
                    'Values (?, ?, ?, ?, ?, ?, ?, ?)', insert_data)
        self.cnn.commit()

    def write_player(self, insert_data: Tuple[str, str, int, str, str, int, int, str, str, int, str, int]):
        cur = self.cnn.cursor()
        cur.execute('INSERT INTO player (name, team, uniform_number, position, date_of_birth, heigh, weigh, throw_arm,'
                    'batting_arm, draft_year, draft_rank, total_year) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
                    insert_data)
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
                    'second_point_12, second_total)', insert_data)
        self.cnn.commit()

    def write_pitch_stats(self,
                          insert_data: Tuple[int, int, float, int, int, int, int, int, int, int, int, int, int, int]):
        cur = self.cnn.cursor()
        cur.execute(
            'INSERT INTO pitch_stats (player_id, game_id, avg, times_at_bat, run, hits, rbi, k, wals, hit_by_pitch,'
            'sacrifice, steal, miss, hr) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', insert_data)
        self.cnn.commit()

    def write_bating_stats(self,
                           insert_data: Tuple[int, int, int, float, int, int, int, int, int, int, int, int, int, int]):
        cur = self.cnn.cursor()
        cur.execute(
            'INSERT INTO batting_stats (player_id, game_id, era, inning, pitch_num, batter_match_num, hits, hr, k,'
            'walks, hit_by_pitch, balk, run, er)')


class DbWriter:
    def __init__(self, db_name: str, year: int, start_month: int, start_day: int):
        self.db_name = db_name
        self.stats_files = glob.glob(f'./HTML/{year}/stats/*.html')
        self.index_files = glob.glob(f'./HTML/{year}/index/*.html')

    def run(self):
        dbOperator = DbOperator(self.db_name)
        id_at_bat = dbOperator.take_last_id_at_bat()


