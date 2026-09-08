import asyncio
import random

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.action_chains import ActionChains
from loguru import logger

from settings.loguru_conf import setup_logger


setup_logger('yandex')
parser_logger = logger.bind(log_name="yandex")


class YandexParserSelenium:
    def __init__(self, search_text, proxy_list=None, max_items=50):
        self._url = f'https://market.yandex.ru/search?text={search_text}'
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
        # без докера
        service = Service(executable_path=ChromeDriverManager().install())
        self._driver = webdriver.Chrome(service=service, options=self._chrome_options)
        # с докером
        # self._driver = webdriver.Remote(command_executor='http://selenium:4444/wd/hub', options=self._chrome_options)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        try:
            self._driver.quit()
        except Exception as e:
            parser_logger.warning('exit:', e)

    async def _close_register(self):
        close_buttons = self._driver.find_elements(By.XPATH, "//button[@class='close-modal-btn']")

        # 2. Если список не пустой, значит окно появилось
        if len(close_buttons) > 0:
            close_buttons[0].click()
            await asyncio.sleep(2)
            logger.info('close register modal')

    async def parse(self):
        try:
            self._driver.implicitly_wait(1)
            self._driver.get(self._url)
            print('load_page')

            products = []
            links = set()
            last_height = self._driver.execute_script("return document.body.scrollHeight")
            scroll_attemps = 0
            while True:
                await self._close_register()
                # element = self._driver.find_element(By.ID, 'SerpStatic')
                # soup = BeautifulSoup(element.get_attribute('outerHTML'), 'html.parser')
                soup = BeautifulSoup(self._driver.page_source, 'html.parser')
                a_tags = soup.select('a')
                print('find tags', len(a_tags))
                for a_tag in a_tags:
                    link = a_tag.get('href')
                    if link and link not in links and link.find('/card/') != -1:
                        links.add(link)
                        products.append({'link': link})
                print('find links: ', len(links))
                if self._max_items != -1 and len(products) >= self._max_items:
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
                        print('прокрутка:', new_height, last_height)
                        logger.info('Достигнут конец прокрутки')
                        break
                else:
                    last_height = new_height
                    scroll_attemps = 0

            self._driver.quit()
            return products
        except Exception as e:
            parser_logger.error('parse_error: ' + str(e))


if __name__ == '__main__':
    with YandexParserSelenium(search_text='телевизор', proxy_list=None, max_items=50) as parser:
        res = asyncio.run(parser.parse())
        # for i in res:
        #     print(i)
        print(len(res))
