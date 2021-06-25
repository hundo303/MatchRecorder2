from bs4 import BeautifulSoup
import re
from typing import List, Tuple, Union


class PageScraper:
    def __init__(self, html_path: str):
        self.html_path = html_path

        self.top_or_bottom = int(self.html_path[-10])

        with open(html_path, encoding='utf-8') as f:
            self.soup = BeautifulSoup(f, 'html.parser')


class IndexPageScraper(PageScraper):
    def __init__(self, html_path: str):
        super().__init__(html_path)
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
                pitch_speed: Union[int, None] = None
            else:
                pitch_speed: Union[int, None] = int(pitch_speed_str.replace('km/h', ''))

            pitch_result_text: str = re.sub(r'\s', '', td_list[4].get_text())

            style_text = style_tag.get('style')
            top_text = re.search(r'top:-?\d+', style_text).group()
            top: int = int(top_text.replace('top:', ''))
            left_text = re.search(r'left:-?\d+', style_text).group()
            left: int = int(left_text.replace('left:', ''))

            ball_data_list.append((pitch_number_in_at_bat,
                                   pitch_number_in_game,
                                   type_of_pitch,
                                   pitch_speed,
                                   pitch_result_text,
                                   strike_count,
                                   ball_count,
                                   top,
                                   left))

            strike_count, ball_count = take_count()

        self.pitch_data_dict['ball_data_list'] = ball_data_list
        return self.pitch_data_dict['ball_data_list']

    def judge_out(self) -> bool:
        tr_list = self.soup.select('#pitchesDetail > section:nth-child(2) > table:nth-child(3) > tbody > tr')

        if not tr_list:
            return False

        td_list = tr_list[-1].select('td')
        pitch_result_class = td_list[0].span.get('class')[1]
        pitch_result_number = int(pitch_result_class[-1])

        pitch_result_text = re.sub(r'\s', '', td_list[4].get_text())

        self.pitch_data_dict['out'] = pitch_result_number == 3 or '三振' in pitch_result_text
        return self.pitch_data_dict['out']

    def take_date(self) -> Tuple[int, int, str]:
        p = self.soup.select_one('#contentMain > div > div.bb-main > div.bb-modCommon02 > p.bb-gameDescription')
        game_month = int(re.search(r'\d{1,2}月', str(p)).group()[:-1])
        game_day = int(re.search(r'\d{1,2}日', str(p)).group()[:-1])
        day_week = re.search(r'（[日月火水木金土]）', str(p)).group().replace('（', '').replace('）', '')

        self.pitch_data_dict['month'] = game_month
        self.pitch_data_dict['day'] = game_day
        self.pitch_data_dict['day_week'] = day_week
        return self.pitch_data_dict['month'], self.pitch_data_dict['day'], self.pitch_data_dict['day_week']

    def take_match_player_data(self) -> Tuple[int, bool, int, bool]:
        def take_player_data(div):
            tr_nm_box = div.select_one('table > tbody > tr > '
                                       'td:nth-child(2) > table > '
                                       'tbody > tr.nm_box')

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
        return plate_appearances

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
                       '左': '不明', '中': '不明', '右': '不明', '指': '不明', '投': '不明'}

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

    def take_rbi(self):
        match = re.search(r'＋\d点', self.pitch_data_dict['result_big'])
        if match:
            rbi_str = re.sub(r'\D', '', match.group())
            rbi = int(rbi_str)
            return rbi
        else:
            return 0

    def take_match_team(self):
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

        return attack_team, defense_team

    def judge_non_butter(self):
        tag = self.soup.select_one('#batt > tbody > tr > td:nth-child(2) > table > tbody >'
                              ' tr.nm_box > td.nm')
        return tag is None


if __name__ == '__main__':
    indexPageScraper = IndexPageScraper('./HTML/2021/index/2021000095/0820500.html')
