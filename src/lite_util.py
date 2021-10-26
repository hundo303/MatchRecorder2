import crawling


def hoge(now_y: int = None, start_m: int = None, start_d: int = None, stop_m: int = None, stop_d: int = None) -> None:
    # 入力された日付に1つでもNoneがあればこちら側で決める
    if any(arg is None for arg in [now_y, start_m, start_d, stop_m, stop_d]):
        now_y, start_m, start_d, stop_m, stop_d = crawling.decision_date()

    schedule_rul_list = crawling.make_schedule_url_list(now_y, start_m, start_d, stop_m, stop_d)
    for schedule_url in schedule_rul_list:
        schedule_page = crawling.SchedulePage(schedule_url, now_y)
        schedule_page.set_soup()

        game_url_list = schedule_page.fetch_game_url_list()
        for game_url in game_url_list:
            score_url: str = game_url + 'score'
            stats_url: str = game_url + 'stats'
            start_url: str = score_url + '?index=0110100'

            score_page = crawling.ScorePage(score_url)
            stats_page = crawling.StatsPage(stats_url)

            # TODO ここで取得済みかの条件分岐

            score_page.send_request()
            if score_page.judge_no_game():
                continue
            # ここでstats_pageの書き込み処理(関数化)
            # ここでindex_pageの書き込み処理(関数化)
