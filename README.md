# MatchRecorder2

# About
[一球速報](https://baseball.yahoo.co.jp/npb/)からデータを取得し、Sqliteのファイルに保存します。

# Requirement

* python3
* BeautifulSoup4
* sqlite3

# Installation
```bash
apt install python3
pip3 install beautifulsoup4
```

# Usage

試合のデータのダウンロード
```bash
python3 main.py
```

選手データのダウンロード
```bash
python3 fetch_player.py
```

# DB ER図
![DB Image](https://github.com/hundo303/MatchRecorder2/blob/image/db.svg)

# WARN
試合データは保存済みのHTMLを二重で取得することはありませんが、選手データは更新されている可能性があるため何度でもリクエストを送る仕様となっています。
サイト様に負担をかけないよう、必要な回数のみ実行するようお願いします。

# Note
データの取得が途中で中断された場合、最後に取得したファイルもしくはディレクトリを削除することをおすすめします。また、DBへの書き込みが途中で中断された場合は、1度sqliteファイルを削除することをおすすめします。  
また、requestsのSSL関連のエラーが出る場合は以下の記事を参考に、自己責任で対処をお願いします。  
https://qiita.com/sidious/items/f9a6eaaf6b1786d6a92c


# Author
[Gmail](<mailto:sakaigen303@gmail.com>)
