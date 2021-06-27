import crawling
import write_db
import datetime

if __name__ == '__main__':
    now_year = datetime.date.today().year
    crawling.craw()
    write_db.write_db(f'{now_year}', now_year)
