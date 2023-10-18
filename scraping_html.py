import datetime
import difflib
import glob
import json
import os
import re
import requests
from bs4 import BeautifulSoup

# 設定ファイルの読み取り
with open('./settings.json') as f_json:
    json_data = json.load(f_json)
site_cnt = len(json_data['website'])

for site_num in range(site_cnt):
    HTML_name = json_data['website'][site_num]['title']
    HTML_URL = json_data['website'][site_num]['URL']
    LINE_Notify_token = json_data['website'][site_num]['LINE_Notify_token']
    HTML_encoding = json_data['website'][site_num]['encoding']
    print(HTML_name, HTML_URL, LINE_Notify_token, HTML_encoding)   

    # 現在のログを取得
    log_file_list = glob.glob('./title_collection_*_' + HTML_name +'.log')
    log_file_path = log_file_list[0]

    # スクレイピング
    response = requests.get(HTML_URL)
    response.encoding = HTML_encoding
    txt = BeautifulSoup(response.text, 'html.parser')

    # htmlからテキスト部を抽出
    item_text = [j for j in txt.stripped_strings]
    item_text = '\n'.join(item_text)
    item_text = re.sub(r'(\n)(\n)*', r'\n', item_text)
    #print(item_text)

    # logとitem_textの差分を取り、更新があるなら通知を送信する
    with open(log_file_path, mode='r') as f_read:
        log = '\n'.join([s.rstrip() for s in f_read.readlines()])
    diff = difflib.ndiff(log, item_text)
    added_article = ''.join([r for r in diff if r[0:1] in ['+']])
    added_article = added_article.replace('+ ', '')
    #print('\n'.join(diff))     # 全部を見る
    print(added_article)        # 差分だけ見る

    # LINE Notifyで通知を送信する
    def send_notify(message: str, token: str):
        line_notify_api = 'https://notify-api.line.me/api/notify'
        headers = {'Authorization': f'Bearer {token}'}
        data = {'message': f'\n{HTML_name}の新着記事： \n{message} \n\n{HTML_URL}'}
        requests.post(line_notify_api, headers=headers, data=data)

    # logを作成する
    log_text = item_text     # type(item_text) -> list
    current_date = datetime.datetime.now().strftime('%Y-%m-%d')
    new_log_file_path = f'./title_collection_{current_date}_{HTML_name}.log'
    os.remove(log_file_path)
    with open(new_log_file_path, mode='w') as f_log:
        f_log.write(log_text)

    # 更新がある場合はNotifyで通知
    if added_article != '':
        send_notify(added_article, LINE_Notify_token)