import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse

# удаляет лишние пробелы
def spaces(text):
    return ' '.join(text.split())

# разделяет строку на текст и ссылку
def split_link(str):
    parts = str.split()
    text_parts = []
    link = None
    for part in parts:
        if urlparse(part).scheme != '':
            link = part
        else:
            text_parts.append(part)
    text = ' '.join(text_parts)
    if link is None:
        return text
    else:
        return text, link

# получает url адрес объявления
def get_url():
    for count in range(1, 8):
        url = f'https://sch18vo.ru/announcement/?PAGEN_1={count}'
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'lxml')
        data = soup.find_all('div', class_='row m-0 index-news h-100 align-content-start')
        
        for i in data:
            card_url = 'https://sch18vo.ru' + i.find('a').get('href')
            yield card_url

# получает данные объявления       
for card_url in get_url():
    response = requests.get(card_url)
    soup = BeautifulSoup(response.text, 'lxml')
    data = soup.find('div', class_='col-12 page-content')
    title = data.find('div', class_='col-12').text
    day = data.find('div', class_='bx-newsdetail-date')
    ann = data.find('div', class_='bx-newsdetail-content bvi-tts')
    if day is None:
        continue
    else:
        day = day.text
    if ann is None:
        continue
    else:
        ann = ann.text
        ann = spaces(ann)
        split_link(ann)
