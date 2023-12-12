import datetime
import difflib
import glob
import json
import os
import requests
from bs4 import BeautifulSoup

# 設定ファイルの読み取り
with open('./settings_rss.json') as f_json:
    json_data = json.load(f_json)
site_cnt = len(json_data['rss'])

for site_num in range(site_cnt):
    RSS_name = json_data['rss'][site_num]['title']
    RSS_URL = json_data['rss'][site_num]['URL']
    LINE_Notify_token = json_data['rss'][site_num]['LINE_Notify_token']

    # 現在のログを取得
    log_file_list = glob.glob('./rss_title_collection_*_' + RSS_name + '.log')
    log_file_path = log_file_list[0]

    # スクレイピング
    response = requests.get(RSS_URL)
    txt = BeautifulSoup(response.text, 'xml')

    # サイトのメインタイトルを取得
    title_text = txt.find('title').get_text()
    url_text = txt.find('link').get_text()

    # CSSセレクターを使うと、複数のtitleが取得できる
    item_text = [n.get_text() for n in txt.select('title')]

    # logとitem_textの差分を取り、新しいtitleがあるなら通知を送信する
    with open(log_file_path, mode='r') as f_read:
        log = [s.rstrip() for s in f_read.readlines()]
    diff = difflib.ndiff(log, item_text)
    added_article = '\n'.join([r for r in diff if r[0:1] in ['+']])
    added_article = added_article.replace('+ ', '')
    #print('\n'.join(diff))     # 全部を見る
    print(added_article)        # 差分だけ見る

    # LINE Notifyで通知を送信する
    def send_notify(message: str, token: str):
        line_notify_api = 'https://notify-api.line.me/api/notify'
        headers = {'Authorization': f'Bearer {token}'}
        data = {'message': f'\n{RSS_name}の新着記事： \n{message} \n\n{url_text}'}
        requests.post(line_notify_api, headers=headers, data=data)

    # logを作成する
    log_text = '\n'.join(item_text)     # type(item_text) -> list
    current_date = datetime.datetime.now().strftime('%Y-%m-%d')
    new_log_file_path = f'./rss_title_collection_{current_date}_{RSS_name}.log'
    os.remove(log_file_path)
    with open(new_log_file_path, mode='w') as f_log:
        f_log.write(log_text)

    # 更新がある場合はNotifyで通知
    if added_article != '':
        send_notify(added_article, LINE_Notify_token)