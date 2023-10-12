import datetime
import difflib
import glob
import os
import requests
from bs4 import BeautifulSoup

URL = 'https://***/rss/feed.xml'
log_file_list = glob.glob('./title_collection_*.log')
log_file_path = log_file_list[0]

# スクレイピング
response = requests.get(URL)
txt = BeautifulSoup(response.text, 'xml')

# サイトのメインタイトルを取得
title_text = txt.find('title').get_text()
print('main title: ', title_text)

# CSSセレクターを使うと、複数のtitleが取得できる
item_text = [n.get_text() for n in txt.select('title')]

# logとitem_textの差分を取り、新しいtitleがあるなら通知を送信する
with open(log_file_path, mode='r') as f_read:
    log = [s.rstrip() for s in f_read.readlines()]
diff = difflib.ndiff(log, item_text)
#print('\n'.join(diff))     # 全部を見る
print('\n'.join([r for r in diff if r[0:1] in ['-', '+']]))   # 差分だけ見る

# logを作成する
print(log_file_path)
current_date = datetime.datetime.now().strftime('%Y-%m-%d')
new_log_file_path = f'./title_collection_{current_date}.log'
os.remove(log_file_path)

log_text = '\n'.join(item_text)     # type(item_text) -> list
with open(new_log_file_path, mode='w') as f_log:
    f_log.write(log_text)
