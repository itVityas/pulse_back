import random
from time import sleep
import re
from typing import Optional, List, Tuple

from bs4 import BeautifulSoup
from seleniumbase import SB
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from loguru import logger

from settings.loguru_conf import setup_logger
from parsings.tv_card import TVCard


setup_logger('ozon')
parser_logger = logger.bind(log_name="ozon")


class OzonParserSelenium:
    def __init__(self, proxy_list=None, max_items=50):
        self._url = 'https://ozon.ru/category/televizory-15528/'
        self._proxy_list = proxy_list
        self._max_items = max_items

    def parse(self) -> List[TVCard]:
        try:
            with SB(uc=True, incognito=True, locale="ru") as driver:
                driver.uc_open_with_reconnect(self._url)
                parser_logger.info(f'start parsing: {self._url}')

                products = []
                links = set()
                last_height = driver.execute_script("return document.body.scrollHeight")
                scroll_attemps = 0
                while True:
                    soup = BeautifulSoup(driver.get_page_source(), 'html.parser')
                    a_tags = soup.select('a[href*="/product/"]')
                    print('a_tags:', len(a_tags))
                    for a_tag in a_tags:
                        link = a_tag.get('href')
                        if link and link not in links and link.find('/product/') != -1:
                            links.add(link)
                            if len(links) > self._max_items:
                                break
                    parser_logger.debug(f'найдено тегов: {len(links)}')
                    if self._max_items != -1 and len(links) >= self._max_items:
                        break

                    scroll_height = random.randint(200, 500)
                    driver.execute_script(f"window.scrollBy(0, {scroll_height});")
                    sleep(random.uniform(2.0, 4.0))
                    new_height = driver.execute_script("return document.body.scrollHeight")
                    if new_height == last_height:
                        scroll_attemps += 1
                        if scroll_attemps > 5:
                            scroll_height = random.randint(200, 500)
                            driver.execute_script(f"window.scrollBy(0, {scroll_height});")
                        if scroll_attemps > 10:
                            logger.info('Достигнут конец прокрутки')
                            break
                    else:
                        last_height = new_height
                        scroll_attemps = 0

                print('links:', len(links))
                # for link in links:
                #     tv_card = self.parse_product(driver, 'https://ozon.ru' + link)
                #     if tv_card:
                #         products.append(tv_card)
                return products
        except Exception as e:
            parser_logger.warning('parse_error:', str(e))


if __name__ == '__main__':
    parser = OzonParserSelenium(proxy_list=None, max_items=20)
    res = parser.parse()
    if res:
        for i in res:
            print(i.get_dict())
        print(len(res))
    else:
        print('empty')
