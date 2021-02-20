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
        'User-Agent': 'Mozilla/5.0 ' +
                        '(Windows NT 10.0; Win64; x64; rv:85.0)' +
                            ' Gecko/20100101 Firefox/85.0',
    }

    def __init__(self, start_url: str, products_path: Path):
        self.start_url = start_url
        self.products_path = products_path

    def _get_response(self, url):
        while True:
            response = requests.get(url, headers=self.headers)
            if response.status_code == 200:
                return response
            time.sleep(0.5)

    def run(self):
        for product in self._parse(self.start_url):
            product_path = self.products_path.joinpath(f'{product["id"]}.json')
            self._save(product, product_path)

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
    save_path = Path(__file__).parent.joinpath('products')
    if not save_path.exists():
        save_path.mkdir()

    parser = Parse5Ka(url, save_path)
    parser.run()
