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
url_text = txt.find('link').get_text()
print('main title: ', title_text)
print('link: ', url_text)

# CSSセレクターを使うと、複数のtitleが取得できる
item_text = [n.get_text() for n in txt.select('title')]

# logとitem_textの差分を取り、新しいtitleがあるなら通知を送信する
with open(log_file_path, mode='r') as f_read:
    log = [s.rstrip() for s in f_read.readlines()]
diff = difflib.ndiff(log, item_text)
added_article = '\n'.join([r for r in diff if r[0:1] in ['+']])
added_article = added_article.replace('+', '')
#print('\n'.join(diff))     # 全部を見る
print(added_article)        # 差分だけ見る

# LINE Notifyで通知を送信する
def send_notify(message: str):
    line_notify_token = '***'
    line_notify_api = 'https://notify-api.line.me/api/notify'
    headers = {'Authorization': f'Bearer {line_notify_token}'}
    data = {'message': f'\n{title_text}で記事が追加されました： \n{message} \n{url_text}'}
    requests.post(line_notify_api, headers=headers, data=data)

# logを作成する
current_date = datetime.datetime.now().strftime('%Y-%m-%d')
new_log_file_path = f'./title_collection_{current_date}.log'
os.remove(log_file_path)

log_text = '\n'.join(item_text)     # type(item_text) -> list
with open(new_log_file_path, mode='w') as f_log:
    f_log.write(log_text)

if added_article != '':
    send_notify(added_article)