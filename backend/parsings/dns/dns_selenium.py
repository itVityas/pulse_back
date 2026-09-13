import asyncio
import random
import re
from typing import Optional, List

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from seleniumbase import Driver
from loguru import logger

from settings.loguru_conf import setup_logger
from parsings.tv_card import TVCard


setup_logger('dns')
parser_logger = logger.bind(log_name="dns")


class YandexParserSelenium:
    def __init__(self, search_text, proxy_list=None, max_items=50):
        self._url = 'https://www.dns-shop.ru/catalog/17a8ae4916404e77/televizory/'
        self._proxy_list = proxy_list
        self._max_items = max_items
        self._driver: WebDriver
        self._chrome_options = webdriver.ChromeOptions()
        self._chrome_options.page_load_strategy = 'eager'
        # self._chrome_options.add_argument('--headless=new')
        self._chrome_options.add_argument('--incognito')
        self._chrome_options.add_argument('--no-sandbox')
        self._chrome_options.add_argument('--disable-gpu')
        self._chrome_options.add_argument('--disable-dev-shm-usage')
        self._chrome_options.add_argument("--disable-extensions")
        self._chrome_options.add_argument("--disable-plugins")
        self._chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        self._chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.85 Safari/537.36")

    def __enter__(self):
        service = Service(executable_path=ChromeDriverManager().install())
        self._driver = webdriver.Chrome(service=service, options=self._chrome_options)
        stealth(
            self._driver,
            languages=["ru-RU", "ru"],
            vendor="Google Inc.",
            platform="Win32",
            webgl_vendor="Intel Inc.",
            renderer="Intel Iris OpenGL Engine",
            fix_hairline=True,
        )
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        try:
            self._driver.quit()
        except Exception as e:
            parser_logger.warning('exit:', e)

    async def parse(self) -> List[TVCard]:
        try:
            self._driver.get(self._url)
            await asyncio.sleep(3)
            parser_logger.info(f'start parsing: {self._url}')

            products = []
            links = set()
            last_height = self._driver.execute_script("return document.body.scrollHeight")
            scroll_attemps = 0
            while True:
                soup = BeautifulSoup(self._driver.page_source, 'html.parser')
                a_tags = soup.select('a')
                print('a_tags:', len(a_tags))
                for a_tag in a_tags:
                    link = a_tag.get('href')
                    if link and link not in links and link.find('/product/') != -1:
                        links.add(link)
                parser_logger.debug(f'найдено тегов: {len(links)}')
                if self._max_items != -1 and len(links) >= self._max_items:
                    break

                scroll_height = random.randint(200, 500)
                # self._driver.execute_script(f"window.scrollBy(0, {scroll_height});")
                actions = ActionChains(self._driver)
                actions.scroll_by_amount(0, scroll_height).perform()
                await asyncio.sleep(5)
                new_height = self._driver.execute_script("return document.body.scrollHeight")
                if new_height == last_height:
                    scroll_attemps += 1
                    if scroll_attemps > 5:
                        scroll_height = random.randint(200, 500)
                        self._driver.execute_script(f"window.scrollBy(0, {scroll_height});")
                    if scroll_attemps > 10:
                        logger.info('Достигнут конец прокрутки')
                        break
                else:
                    last_height = new_height
                    scroll_attemps = 0

            print('links:', len(links))
            return products
        except Exception as e:
            parser_logger.warning('parse_error:', e)


if __name__ == '__main__':
    with YandexParserSelenium(search_text='телевизор', proxy_list=None, max_items=5) as parser:
        res = asyncio.run(parser.parse())
        for i in res:
            print(i.get_dict())
        print(len(res))
