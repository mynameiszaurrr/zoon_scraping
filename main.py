from bs4 import BeautifulSoup
import requests
import time
import json
import pandas as pd
import fake_useragent

us = fake_useragent.UserAgent(verify_ssl=False).random

URL = 'https://zoon.ru/msk/repair/'
HEADERS = {
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,'
              'application/signed-exchange;v=b3;q=0.9',
    'accept-encoding': '*/*',
    'accept-language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
    'user-agent': us
}
page_number = 1

s = requests.Session()

for page in range(page_number, 20):
    index_with_all_pages = s.post(url='https://zoon.ru/msk/repair/?action=listJson&type=service',
                                  data={
                                        'need[]': 'items',
                                        'search_query_form': '1',
                                        'page': page},
                                  headers=HEADERS).text
    if index_with_all_pages != '{"success":false}':
        with open(f'/Users/zaurmamedov/Desktop/python/zoon_freelans/pages/{page}.json', 'w') as json_file:
            json_file.write(index_with_all_pages)
            page_number += 1
        print(f'Страница {page} сохраненна в папку "pages"')
        time.sleep(2)
    else:
        break
print(f'Все страницы для работы сохраненны (всего {page_number} страниц), начинаем парсить информацию из этих страниц')

for page in range(1, page_number):
    with open(f'/Users/zaurmamedov/Desktop/python/zoon_freelans/pages/{page}.json', 'r') as file:
        src = file.read()
    data_json = json.loads(src)
    with open(f'/Users/zaurmamedov/Desktop/python/zoon_freelans/pages/html_pages/{page}.html', 'w', encoding='UTF-8') as html_file:
        html_file.write(data_json['html'])
    print(f'Страница {page} спарсина')

names = []
address = []
metro = []
district = []
work_time_list = []
service_name_list = []
service_price_list = []
service_list = []
service_info_list = []
number_list = []
page_info_list = []
link_list = []

for page in range(1, page_number):
    with open(f'/Users/zaurmamedov/Desktop/python/zoon_freelans/pages/html_pages/{page}.html', 'r') as html_file:
        src = html_file.read()
        soup = BeautifulSoup(src, 'lxml')
        link = soup.find_all('a', class_='js-item-url')
        for i in link:
            if i["href"] == 'javascript:void()':
                continue
            else:
                link_list.append(i["href"])

links_count = len(link_list)

for link in link_list:
    response = requests.get(url=link, headers=HEADERS).text
    page_soup = BeautifulSoup(response, 'lxml')
    names.append(page_soup.find('h1').find('span').text.strip().replace(u'\xa0', u' '))
    try:
        adr = page_soup.find('address', class_='iblock').text.strip().replace(u'\xa0', u' ')
        full_adr = ''.join(adr)
        address.append(full_adr)
    except Exception:
        address.append('Нет данных про адрес')

    try:
        metro_ad = []
        for metro_address in page_soup.find_all('div', class_='address-metro invisible-links'):
            metro_ad.append(metro_address.find('a').text)
        metro.append(metro_ad)
    except Exception:
        metro.append('Нет данных про станции метро')

    try:
        dis = page_soup.find('address', class_='iblock').find_next_sibling().text.strip().replace(u'\n', u'').replace(u'\t', u'').split(',')[0]
        if dis == None:
            district.append('Нет данных про метро')
        else:
            district.append(str(dis))
    except Exception:
        district.append('Нет данных про метро')

    try:
        work_time = page_soup.find('dd', class_='upper-first').find('div').text
        work_time_list.append(work_time)
    except Exception:
        work_time_list.append('Нет данных про время работы')

    try:
        service_ad = []
        for service in page_soup.find_all('dt', class_='fs-small gray')[1:]:
            service_ad.append(service.text.strip())
        service_list.append(service_ad)
    except Exception:
        service_list.append('Нет данных про услуги')

    page_id = page_soup.find('span', class_='js-phone phoneView phone-hidden')['data-json'].split('{"object_id":"')[1].split('","')[0].split('.')[0]
    service_catalog = requests.get(url=f'https://zoon.ru/js.php?area=menu&action=itemList&owner_type=organization&owner_id={page_id}&masterprice_ids=&category=all&search=&page=&sort=likes&isMenuSubPage=0&firstUpdate=0',
                                   headers=HEADERS).text
    service_soup = BeautifulSoup(service_catalog, 'lxml')

    try:
        service_name = service_soup.find_all('span', class_='js-pricelist-title')
        service_name_ad = []
        for name in service_name:
            service_name_ad.append(name.text.strip().replace(u'\xa0', u' '))
        service_name_list.append(service_name_ad)
    except Exception:
        service_name_list.append('Нет данных про название услуг')

    service_price = service_soup.find_all('div', class_='pricelist-item-price')
    service_price_ad = []
    try:
        for price in service_price:
            service_price_ad.append(price.text.strip().replace(u'\xa0', u''))
        service_price_list.append(service_price_ad)
    except Exception:
        service_price_list.append('Нет данных про прайс')

    try:
        service_info_ad = []
        for info in page_soup.find_all('dd', class_='first-p'):
            service_info_ad.append(info.text.strip())
        service_info_list.append(service_info_ad)
    except Exception:
        service_info_list.append("Нет описании услуг")

    try:
        number = page_soup.find('span', class_='js-phone phoneView phone-hidden').find('a', class_='tel-phone js-phone-number')[
            'href'][4:]
        number_list.append(number)
    except Exception:
        number_list.append("Нет контактного номера")

    try:
        page_info = page_soup.find('dd', class_='js-desc oh word-break').text.strip()
        page_info_list.append(page_info)
    except Exception:
        page_info_list.append("Нет описания фирмы")
    links_count -= 1
    print(f'Вся информация из страницы {link} вытащена! идем дальше! Осталось {links_count} ссылок...')

data1 = {
    "Имя": names,
    "Адрес": address,
    "Метро": metro,
    "Округ": district,
    "Время работы": work_time_list,
    "Название работы": service_name_list,
    "Цена работы": service_price_list,
    "Сервис лист": service_list,
    "Сервис инфо лист": service_info_list,
    "Контакты": number_list,
    "Отзывы": page_info_list,
    "Ссылка": link_list
}

df = pd.DataFrame(data=data1)
df.to_csv('cartridge_accounting.csv', sep='\t', encoding='UTF-16')
