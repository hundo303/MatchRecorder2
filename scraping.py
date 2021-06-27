from bs4 import BeautifulSoup
import re
from typing import List, Tuple, Union


class PageScraper:
    def __init__(self, html_path: str):
        self.html_path = html_path

        with open(html_path, encoding='utf-8') as f:
            self.soup = BeautifulSoup(f, 'html.parser')


class IndexPageScraper(PageScraper):
    def __init__(self, html_path: str):
        super().__init__(html_path)
        self.top_or_bottom = int(self.html_path[-10])
        self.pitch_data_dict: dict = {}

    #  1球ごとの投球内容は[打席での球数, 試合での球数, 球種, 球速, 結果, ストライクカウント, ボールカウント]
    def take_ball_data_list(self) -> List[Tuple[int, int, str, int, str, int, int, int]]:
        def take_count():
            if pitch_result_number == 1:
                if 'ファウル' in pitch_result_text and strike_count == 2:
                    return strike_count, ball_count
                else:
                    return strike_count + 1, ball_count

            elif pitch_result_number == 2:
                return strike_count, ball_count + 1

            else:
                return strike_count, ball_count

        ball_data_list: list = []
        strike_count: int = 0
        ball_count: int = 0

        tr_list = self.soup.select('#pitchesDetail > section:nth-child(2) > table:nth-child(3) > tbody > tr')
        span_list = self.soup.select('#pitchesDetail > section:nth-child(2) > '
                                     'table:nth-child(1) > tbody > tr > td > '
                                     'div > span')

        for tr, style_tag in zip(tr_list, span_list):
            td_list = tr.select('td')
            pitch_result_class = td_list[0].span.get('class')[1]
            pitch_result_number = int(pitch_result_class[-1])

            pitch_number_in_at_bat: int = int(td_list[0].span.get_text())
            pitch_number_in_game: int = int(td_list[1].get_text())
            type_of_pitch: str = td_list[2].get_text()

            pitch_speed_str: str = td_list[3].get_text()
            if pitch_speed_str == '-':
                speed: Union[int, None] = None
            else:
                speed: Union[int, None] = int(pitch_speed_str.replace('km/h', ''))

            pitch_result_text: str = re.sub(r'\s', '', td_list[4].get_text())

            style_text = style_tag.get('style')
            top_text = re.search(r'top:-?\d+', style_text).group()
            top: int = int(top_text.replace('top:', ''))
            left_text = re.search(r'left:-?\d+', style_text).group()
            left: int = int(left_text.replace('left:', ''))

            ball_data_list.append({'pitch_number_in_at_bat': pitch_number_in_at_bat,
                                   'pitch_number_in_game': pitch_number_in_game,
                                   'type_of_pitch': type_of_pitch,
                                   'speed': speed,
                                   'pitch_result_text': pitch_result_text,
                                   'strike_count': strike_count,
                                   'ball_count': ball_count,
                                   'top': top,
                                   'left': left})

            strike_count, ball_count = take_count()

        self.pitch_data_dict['ball_data_list'] = ball_data_list
        return self.pitch_data_dict['ball_data_list']

    def judge_out(self) -> bool:
        self.pitch_data_dict['out'] = False
        tr_list = self.soup.select('#pitchesDetail > section:nth-child(2) > table:nth-child(3) > tbody > tr')

        if not tr_list:
            return False

        td_list = tr_list[-1].select('td')
        pitch_result_class = td_list[0].span.get('class')[1]
        pitch_result_number = int(pitch_result_class[-1])

        pitch_result_text = re.sub(r'\s', '', td_list[4].get_text())

        self.pitch_data_dict['out'] = pitch_result_number == 3 or '三振' in pitch_result_text
        return self.pitch_data_dict['out']

    def take_match_player_data(self) -> Tuple[int, bool, int, bool]:
        def take_player_data(div):
            tr_nm_box = div.select_one('table > tbody > tr > '
                                       'td:nth-child(2) > table > '
                                       'tbody > tr.nm_box')
            if tr_nm_box.select_one('td.nm > a') is None:
                return None, None
            id_url = tr_nm_box.select_one('td.nm > a').get('href')
            player_id = int(id_url.split('/')[3])

            if tr_nm_box.select_one('td.dominantHand') is None:
                left_hand = False
            else:
                dominant_hand = tr_nm_box.select_one('td.dominantHand').get_text()
                left_hand = (dominant_hand == '左投' or dominant_hand == '左打')

            return player_id, left_hand

        pitcher_side = 'L' if self.top_or_bottom == 1 else 'R'

        div_pitcher = self.soup.select_one(f'#pitcher{pitcher_side} > div.card')
        div_batter = self.soup.select_one('#batter')

        pitcher_data = take_player_data(div_pitcher)
        batter_data = take_player_data(div_batter)

        self.pitch_data_dict['pitcher_id'] = pitcher_data[0]
        self.pitch_data_dict['pitcher_left'] = pitcher_data[1]
        self.pitch_data_dict['batter_id'] = batter_data[0]
        self.pitch_data_dict['batter_left'] = batter_data[1]

        return_tuple = (
            self.pitch_data_dict['pitcher_id'], self.pitch_data_dict['pitcher_left'], self.pitch_data_dict['batter_id'],
            self.pitch_data_dict['batter_left'])
        return return_tuple

    def take_num_at_bat(self) -> int:
        span_list = self.soup.select('#batt > tbody > tr > td:nth-child(2) > '
                                     'table > tbody > tr:nth-child(2) > td > '
                                     'table > tbody > tr:nth-child(2) > td > span')

        plate_appearances = len(span_list) + 1
        self.pitch_data_dict['num_at_bat'] = plate_appearances
        return self.pitch_data_dict['num_at_bat']

    def take_match_batter_number(self) -> int:
        pitcher_side = 'L' if self.top_or_bottom == 1 else 'R'
        div_pitcher = self.soup.select_one(f'#pitcher{pitcher_side} > div.card')
        team_number_str = div_pitcher.get('class')[1]

        td = self.soup.select_one(f'#pitcher{pitcher_side} > div.card.{team_number_str} > '
                                  'table > tbody > tr > td:nth-child(2) > '
                                  'table > tbody > tr.score > td:nth-child(2)')

        match_batter_number: int = int(td.get_text())

        self.pitch_data_dict['match_batter_number'] = match_batter_number
        return self.pitch_data_dict['match_batter_number']

    def take_defense(self) -> Tuple[str, str, str, str, str, str, str, str]:
        defense_dic = {'捕': '不明', '一': '不明', '二': '不明', '三': '不明', '遊': '不明',
                       '左': '不明', '中': '不明', '右': '不明', '指': '不明', '投': '不明',
                       '打': '不明', '走': '不明'}

        pitcher_side = 'L' if self.top_or_bottom == 1 else 'R'
        defense_side = 'h' if self.top_or_bottom == 1 else 'a'

        div_pitcher = self.soup.select_one(f'#pitcher{pitcher_side} > div.card')
        team_number_str = div_pitcher.get('class')[1]

        tr_list = self.soup.select(f'#gm_memh > table.bb-splitsTable.bb-splitsTable--team1 > tbody > tr')

        for tr in tr_list:
            td_list = tr.select('td')
            if len(td_list) == 0:
                continue

            position = td_list[1].get_text()
            player = td_list[2].a.get_text().replace(' ', '')
            if not position == '':
                if defense_dic[position] == '不明':
                    defense_dic[position] = player
                else:
                    defense_dic[position] += f'||{player}'

        self.pitch_data_dict['c'] = defense_dic['捕']
        self.pitch_data_dict['first'] = defense_dic['一']
        self.pitch_data_dict['second'] = defense_dic['二']
        self.pitch_data_dict['third'] = defense_dic['三']
        self.pitch_data_dict['ss'] = defense_dic['遊']
        self.pitch_data_dict['lf'] = defense_dic['左']
        self.pitch_data_dict['cf'] = defense_dic['中']
        self.pitch_data_dict['rf'] = defense_dic['右']

        return_tuple = (self.pitch_data_dict['c'],
                        self.pitch_data_dict['first'],
                        self.pitch_data_dict['second'],
                        self.pitch_data_dict['third'],
                        self.pitch_data_dict['ss'],
                        self.pitch_data_dict['lf'],
                        self.pitch_data_dict['cf'],
                        self.pitch_data_dict['rf'])
        return return_tuple

    def take_result_at_bat(self) -> Tuple[Tuple[str, str], Tuple[str, str]]:
        result_at_bat = self.soup.select_one('#result')
        if result_at_bat.span is None:
            result_span = ''
        else:
            result_span = result_at_bat.span.get_text()
        if result_at_bat.em is None:
            result_em = ''
        else:
            result_em = result_at_bat.em.get_text()

        self.pitch_data_dict['result_big'] = result_span
        self.pitch_data_dict['result_small'] = result_em

        return self.pitch_data_dict['result_big'], self.pitch_data_dict['result_small']

    def take_runner(self) -> Tuple[Union[str, None], Union[str, None], Union[str, None]]:
        runner_dict: dict = {1: None, 2: None, 3: None}
        div_list = self.soup.select('#dakyu > div')
        for div in div_list:
            base_number = int(div.get('id')[-1])
            runner = div.span.get_text()
            runner_name = runner.split(' ')[1]
            runner_dict[base_number] = runner_name

        self.pitch_data_dict['first_runner'] = runner_dict[1]
        self.pitch_data_dict['second_runner'] = runner_dict[2]
        self.pitch_data_dict['third_runner'] = runner_dict[3]

        return_tuple = (self.pitch_data_dict['first_runner'],
                        self.pitch_data_dict['second_runner'],
                        self.pitch_data_dict['third_runner'])
        return return_tuple

    def take_match_team(self) -> Tuple[str, str]:
        attack_team = str
        defense_team = str

        first_team = self.soup.select_one('#ing_brd > tbody > tr:nth-child(1) > '
                                          'td.bb-gameScoreTable__data.bb-gameScoreTable__data--team > '
                                          'a').get_text()
        second_team = self.soup.select_one('#ing_brd > tbody > tr:nth-child(2) > '
                                           'td.bb-gameScoreTable__data.bb-gameScoreTable__data--team > '
                                           'a').get_text()

        if self.top_or_bottom == 1:
            attack_team, defense_team = first_team, second_team
        elif self.top_or_bottom == 2:
            attack_team, defense_team = second_team, first_team

        self.pitch_data_dict['attack_team'] = attack_team
        self.pitch_data_dict['defense_team'] = defense_team
        return self.pitch_data_dict['attack_team'], self.pitch_data_dict['defense_team']

    def take_rbi(self) -> int:
        match = re.search(r'＋\d点', self.pitch_data_dict['result_big'])
        if match:
            rbi_str = re.sub(r'\D', '', match.group())
            rbi = int(rbi_str)
            self.pitch_data_dict['rbi'] = rbi
            return rbi
        else:
            self.pitch_data_dict['rbi'] = 0
            return 0

    def judge_non_butter(self) -> bool:
        tag = self.soup.select_one('#batt > tbody > tr > td:nth-child(2) > table > tbody >'
                                   ' tr.nm_box > td.nm')

        return tag is None

    def take_intentional_walk(self) -> bool:
        intentional_walk = '申告敬遠' in self.pitch_data_dict['result_big']
        self.pitch_data_dict['intentional_walk'] = intentional_walk
        return self.pitch_data_dict['intentional_walk']

    def judge_steal(self) -> Tuple[str, bool]:
        write_steal, steal_non_pitch = None, None

        for steal in ('盗塁成功', '盗塁失敗'):
            if steal in self.pitch_data_dict['result_small'] and not '盗塁成功率' in self.pitch_data_dict['result_small']:
                write_steal = steal
                steal_non_pitch = False
                if self.pitch_data_dict['ball_data_list'] == [] or not steal in \
                                                                       self.pitch_data_dict['ball_data_list'][-1][
                                                                           'pitch_result_text']:
                    steal_non_pitch = True

        self.pitch_data_dict['write_steal'] = write_steal
        self.pitch_data_dict['steal_non_pitch'] = steal_non_pitch

        return self.pitch_data_dict['write_steal'], self.pitch_data_dict['steal_non_pitch']

    def get_pitch_data_dict(self) -> dict:
        self.take_ball_data_list()
        self.judge_out()
        self.take_match_player_data()
        self.take_num_at_bat()
        self.take_match_batter_number()
        self.take_defense()
        self.take_result_at_bat()
        self.take_runner()
        self.take_match_team()
        self.take_rbi()
        self.take_intentional_walk()
        self.judge_steal()

        return self.pitch_data_dict


class PlayerPageScraper(PageScraper):
    def take_player_profile(self) -> dict:
        player_name = self.soup.select_one('#contentMain > div > div.bb-main > '
                                           'div.bb-modCommon01 > div > div > div >'
                                           ' ruby > h1').get_text().replace(' ', '')

        team_name_dict = {'team1': '巨人', 'team2': 'ヤクルト', 'team3': 'DeNA',
                          'team4': '中日', 'team5': '阪神', 'team6': '広島',
                          'team7': '西武', 'team8': '日本ハム', 'team9': 'ロッテ',
                          'team11': 'オリックス', 'team12': 'ソフトバンク', 'team376': '楽天'}

        team_num: str = self.soup.select_one('#contentMain > div > div.bb-main > '
                                             'section:nth-child(3) > header').get('class')[2].split('--')[-1]
        team_name = team_name_dict[team_num]

        uniform_number = self.soup.select_one('#contentMain > div > div.bb-main > '
                                              'div.bb-modCommon01 > div > div > div > '
                                              'div > p.bb-profile__number').get_text()
        position = self.soup.select_one('#contentMain > div > div.bb-main > '
                                        'div.bb-modCommon01 > div > div > div > div > '
                                        'p.bb-profile__position').get_text()

        dominant_arm = self.soup.select_one('#contentMain > div > div.bb-main > '
                                            'div.bb-modCommon01 > div > div > '
                                            'div.bb-profile__data > dl:nth-child(8) > dd').get_text()
        throw_arm = dominant_arm[0]
        batting_arm = dominant_arm[3]

        height_str: str = self.soup.select_one('#contentMain > div > div.bb-main > '
                                               'div.bb-modCommon01 > div > div > '
                                               'div.bb-profile__data > dl:nth-child(5) > '
                                               'dd').get_text()
        weight_str: str = self.soup.select_one('#contentMain > div > div.bb-main > '
                                               'div.bb-modCommon01 > div > div > '
                                               'div.bb-profile__data > dl:nth-child(6) > '
                                               'dd').get_text()
        height = int(re.search(r'\d+', height_str).group())
        weight = int(re.search(r'\d+', weight_str).group())

        date_of_birth_tag = self.soup.select_one('#contentMain > div > div.bb-main > '
                                                 'div.bb-modCommon01 > div > div > '
                                                 'div > dl:nth-child(3) > '
                                                 'dd').get_text().split('（')[0]
        date_split_list = re.findall(r'\d+', date_of_birth_tag)
        date_of_birth = f'{date_split_list[0]}-{date_split_list[1]}-{date_split_list[2]}'

        title = self.soup.select_one('#contentMain > div > div.bb-main > div.bb-modCommon01 > '
                                     'div > div > div.bb-profile__data > dl:nth-child(9) > dt').get_text()

        draft_tag = self.soup.select_one('#contentMain > div > div.bb-main > '
                                         'div.bb-modCommon01 > div > div > '
                                         'div.bb-profile__data > dl:nth-child(9) > dd').get_text()
        total_year_tag = self.soup.select_one('#contentMain > div > div.bb-main > '
                                              'div.bb-modCommon01 > div > div > '
                                              'div.bb-profile__data > dl:nth-child(10) > dd').get_text()

        if title == 'プロ通算年':
            draft_year = None
            draft_rank = None
            total_year_tag = self.soup.select_one('#contentMain > div > div.bb-main > '
                                                  'div.bb-modCommon01 > div > div > '
                                                  'div.bb-profile__data > dl:nth-child(9) > dd').get_text()

        else:
            draft_year = int(re.search(r'\d{4}', draft_tag).group())
            draft_rank = draft_tag[5:].replace('（', '').replace('）', '')

        total_year = int(re.search(r'\d+', total_year_tag).group())

        return_dict: dict = {'player_name': player_name, 'team_name': team_name, 'uniform_number': uniform_number,
                             'position': position, 'date_of_birth': date_of_birth, 'height': height, 'weight': weight,
                             'throw_arm': throw_arm, 'batting_arm': batting_arm, 'draft_year': draft_year,
                             'draft_rank': draft_rank, 'total_year': total_year}
        return return_dict


class StatsPageScraper(PageScraper):
    def take_date(self) -> Tuple[str, str]:
        p = self.soup.select_one('#contentMain > div > div.bb-main > div.bb-modCommon02 > p.bb-gameDescription')
        game_month = re.search(r'\d{1,2}月', str(p)).group()[:-1]
        game_day = re.search(r'\d{1,2}日', str(p)).group()[:-1]
        day_week = re.search(r'（[日月火水木金土]）', str(p)).group().replace('（', '').replace('）', '')

        year = int(re.search(r'\d{4}', self.html_path).group())
        # self.pitch_data_dict['date'] = f'{year}-{game_month}-{game_day}'
        # self.pitch_data_dict['day_week'] = day_week
        # return self.pitch_data_dict['date'], self.pitch_data_dict['day_week']
        return f'{year}-{game_month.zfill(2)}-{game_day.zfill(2)}', day_week

    def take_stadium(self) -> str:
        p = self.soup.select_one('#contentMain > div > div.bb-main > div.bb-modCommon02 > p.bb-gameDescription')
        return p.get_text().split()[2]

    def take_point_board(self) -> Tuple[dict, dict]:
        first_point_dict: dict = {1: None, 2: None, 3: None, 4: None, 5: None, 6: None, 7: None,
                                  8: None, 9: None, 10: None, 11: None, 12: None, 'hits': 0, 'miss': 0}
        second_point_dict: dict = {1: None, 2: None, 3: None, 4: None, 5: None, 6: None, 7: None,
                                   8: None, 9: None, 10: None, 11: None, 12: None, 'hits': 0, 'miss': 0}

        first_point_bord = self.soup.select('#ing_brd > tbody > tr:nth-child(1)  .bb-gameScoreTable__data')
        second_point_bord = self.soup.select('#ing_brd > tbody > tr:nth-child(2) .bb-gameScoreTable__data')

        for i, (first_point, second_point) in enumerate(zip(first_point_bord, second_point_bord)):
            if i == 0:
                continue

            # 途中で中止になった場合
            if first_point.select_one('a') is None:
                break

            first_point_dict[i] = int(first_point.select_one('a').get_text().replace('X', ''))
            if not second_point.select_one('a') is None:
                second_point_dict[i] = int(second_point.select_one('a').get_text().replace('X', ''))

        first_total_bord = self.soup.select('#ing_brd > tbody > tr:nth-child(1)  .bb-gameScoreTable__total')
        second_total_bord = self.soup.select('#ing_brd > tbody > tr:nth-child(2) .bb-gameScoreTable__total')

        first_point_dict['total'] = int(first_total_bord[0].get_text())
        first_point_dict['hits'] = int(first_total_bord[1].get_text())
        first_point_dict['miss'] = int(first_total_bord[2].get_text())
        second_point_dict['total'] = int(second_total_bord[0].get_text())
        second_point_dict['hits'] = int(second_total_bord[1].get_text())
        second_point_dict['miss'] = int(second_total_bord[2].get_text())

        return first_point_dict, second_point_dict

    def take_player_stats(self) -> Tuple[List[dict], List[dict]]:
        batting_stats_list: list = []
        pitching_stats_list: list = []
        batter_tr_list_first = self.soup.select('.bb-blowResultsTable > table > tbody > .bb-statsTable__row')
        batter_tr_list_second = self.soup.select(
            'bb-blowResultsTable:nth-child(2) > table > tbody > .bb-statsTable__row')

        for batter_tr in batter_tr_list_first + batter_tr_list_second:
            batter_stats_dict: dict = {}
            batter_td_list = batter_tr.select('td')

            if batter_td_list[1].select_one('a') is None:
                continue
            batter_stats_dict['player_id'] = batter_td_list[1].select_one('a').get('href').split('/')[3]
            batter_stats_dict['avg'] = float(batter_td_list[2].get_text()) if batter_td_list[
                                                                                  2].get_text() != '-' else None
            batter_stats_dict['times_at_bat'] = int(batter_td_list[3].get_text())
            batter_stats_dict['run'] = int(batter_td_list[4].get_text())
            batter_stats_dict['hits'] = int(batter_td_list[5].get_text())
            batter_stats_dict['rbi'] = int(batter_td_list[6].get_text())
            batter_stats_dict['k'] = int(batter_td_list[7].get_text())
            batter_stats_dict['walks'] = int(batter_td_list[8].get_text())
            batter_stats_dict['hit_by_pitch'] = int(batter_td_list[9].get_text())
            batter_stats_dict['sacrifice'] = int(batter_td_list[10].get_text())
            batter_stats_dict['steal'] = int(batter_td_list[11].get_text())
            batter_stats_dict['miss'] = int(batter_td_list[12].get_text())
            batter_stats_dict['hr'] = int(batter_td_list[13].get_text())

            batting_stats_list.append(batter_stats_dict)

        pitcher_tr_list_first = self.soup.select(
            '#gm_stats > section:nth-child(2) > section:nth-child(2) > table > tbody > tr')
        pitcher_tr_list_second = self.soup.select(
            '#gm_stats > section:nth-child(2) > section:nth-child(3) > table > tbody > tr')

        for pitcher_tr in pitcher_tr_list_first + pitcher_tr_list_second:
            pitcher_stats_dict: dict = {}
            pitcher_td_list = pitcher_tr.select('td')

            if not pitcher_td_list[0].select_one('a') is None:
                pitcher_td_list.insert(0, None)

            td_str = pitcher_td_list[2].select_one('p')
            pitcher_stats_dict['player_id'] = pitcher_td_list[1].select_one('a').get('href').split('/')[3]
            pitcher_stats_dict['era'] = float(td_str.get_text()) if td_str.get_text() != '-' else None
            pitcher_stats_dict['inning'] = float(pitcher_td_list[3].get_text())
            pitcher_stats_dict['pitch_num'] = int(pitcher_td_list[4].get_text())
            pitcher_stats_dict['batter_match_num'] = int(pitcher_td_list[5].get_text())
            pitcher_stats_dict['hits'] = int(pitcher_td_list[6].get_text())
            pitcher_stats_dict['hr'] = int(pitcher_td_list[7].get_text())
            pitcher_stats_dict['k'] = int(pitcher_td_list[8].get_text())
            pitcher_stats_dict['walks'] = int(pitcher_td_list[9].get_text())
            pitcher_stats_dict['hit_by_pitch'] = int(pitcher_td_list[10].get_text())
            pitcher_stats_dict['balk'] = int(pitcher_td_list[11].get_text())
            pitcher_stats_dict['run'] = int(pitcher_td_list[12].get_text())
            pitcher_stats_dict['er'] = int(pitcher_td_list[13].get_text())

            pitching_stats_list.append(pitcher_stats_dict)

        return batting_stats_list, pitching_stats_list

    def take_team_name(self) -> Tuple[str, str]:
        first_team = self.soup.select_one('#ing_brd > tbody > tr:nth-child(1) >'
                                          ' td.bb-gameScoreTable__data.bb-gameScoreTable__data--team >'
                                          ' a').get_text()
        second_team = self.soup.select_one('#ing_brd > tbody > tr:nth-child(2) >'
                                           ' td.bb-gameScoreTable__data.bb-gameScoreTable__data--team >'
                                           ' a').get_text()
        return first_team, second_team
