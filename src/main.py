import crawling
import write_db
import datetime
from argparse import ArgumentParser


if __name__ == '__main__':
    arg_parser = ArgumentParser()

    arg_parser.add_argument('-l', '--lite', action='store_true')
    arg = arg_parser.parse_args()

    if arg.lite:
        pass
    else:
        now_year = datetime.date.today().year
        crawling.craw()
        write_db.write_db(f'{now_year}', now_year)
