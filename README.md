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
pip3 install sqlite3
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

# WARN
試合データは保存済みのHTMLを二重で取得することはありませんが、選手データは更新されている可能性があるため何度でもリクエストを送る仕様となっています。
サイト様に負担をかけないよう、必要な回数のみ実行するようお願いします。

# Note
データの取得が途中で中断された場合、最後に取得したファイルもしくはディレクトリを削除することをおすすめします。また、DBへの書き込みが途中で中断された場合は、1度sqliteファイルを削除することをおすすめします。

# Author
[Gmail](<mailto:sakaigen303@gmail.com>)
