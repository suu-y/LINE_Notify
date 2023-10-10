import requests
from bs4 import BeautifulSoup

URL = 'https://***/rss/feed.xml'

response = requests.get(URL)
#print(response.text)

txt = BeautifulSoup(response.text, 'xml')

title_text = txt.find('title').get_text()
print(title_text)

# CSSセレクターを使うと、複数のtitleが取得できる
item_text = [n.get_text() for n in txt.select('title')]
print(item_text)