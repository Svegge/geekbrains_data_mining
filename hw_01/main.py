'''
Parser for special_offers 5ka.ru
'''

import time
import json
from pathlib import Path
import requests


class Parse5Ka:
    '''
    Api parser
    '''

    headers = {
        'Accept': 'application/json',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:85.0)' +
                      ' Gecko/20100101 Firefox/85.0',
    }

    def __init__(self, start_url: str, products_path: Path,
                 params: dict, category_name: str):
        self.start_url = start_url
        self.products_path = products_path
        self.params = params
        self.category_name = category_name

    def _get_response(self, url):
        while True:
            response = requests.get(url, headers=self.headers,
                                    params=self.params)
            if response.status_code == 200:
                return response
            time.sleep(0.5)

    def run(self):
        data_dict = {}
        products_list = []
        data_dict['name'] = self.category_name
        data_dict['code'] = self.params['categories']

        for product in self._parse(self.start_url):
            products_list.append(product)

        data_dict['products'] = products_list
        product_path = self.products_path.joinpath(self.params['categories'])
        self._save(data_dict, product_path)

    def _parse(self, url):
        while url:
            response = self._get_response(url)
            data = response.json()  # data = json.loads(response.text)
            url = data['next']
            for product in data['results']:
                yield product

    @staticmethod
    def _save(data: dict, file_path):
        file_path.write_text(
            json.dumps(
                data,
                ensure_ascii=False),
            encoding='UTF-8')


if __name__ == '__main__':

    url = 'https://5ka.ru/api/v2/special_offers/'
    url_categories = 'https://5ka.ru/api/v2/categories/'

    save_path = Path(__file__).parent.joinpath('categories')
    if not save_path.exists():
        save_path.mkdir()

    headers = {
        'Accept': 'application/json',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:85.0)' +
        ' Gecko/20100101 Firefox/85.0',
    }

    response = requests.get(url_categories, headers=headers)

    categories_dic = {}

    data = response.json()

    # создаем словарь категорий
    for item in data:
        categories_dic[item['parent_group_code']] = item['parent_group_name']

    # проходим циклом по словарю категорий,
    # передаем в парсер параметризованный запрос к api
    # с указанием необходимой категории товаров для выгрузки
    for cat_id in categories_dic:
        params = {
            'categories': cat_id
        }
        category_name = categories_dic[cat_id]
        parser = Parse5Ka(url, save_path, params, category_name)
        parser.run()
