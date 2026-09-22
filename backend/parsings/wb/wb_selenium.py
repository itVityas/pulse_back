import random
from time import sleep
import re
from typing import Optional, List, Tuple, Dict

from bs4 import BeautifulSoup
from seleniumbase import SB, Driver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from loguru import logger

from settings.loguru_conf import setup_logger
from parsings.tv_card import TVCard


setup_logger('wb')
parser_logger = logger.bind(log_name="wb")


class WBParserSelenium:
    def __init__(self, proxy_list=None, max_items=50):
        self._url = 'https://www.wildberries.ru/catalog/elektronika/tv-audio-foto-video-tehnika/televizory/televizory'
        self._proxy_list = proxy_list
        self._max_items = max_items

    def parse(self) -> List[TVCard]:
        try:
            with Driver(uc=True, incognito=True, locale="ru", locale_code="ru") as driver:
                driver.uc_open_with_reconnect(self._url)
                parser_logger.info(f'start parsing: {self._url}')

                products = []
                links = set()
                last_height = driver.execute_script("return document.body.scrollHeight")
                scroll_attemps = 0
                while True:
                    soup = BeautifulSoup(driver.get_page_source(), 'html.parser')
                    a_tags = soup.select('a[href*="/catalog/"]')
                    print('a_tags:', len(a_tags))
                    for a_tag in a_tags:
                        link = a_tag.get('href')
                        if link and link not in links and (
                                    link.find('/catalog/') != -1 and link.endswith('detail.aspx')
                                ):
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
                for link in links:
                    tv_card = self.parse_product(driver, link)
                    if tv_card:
                        products.append(tv_card)
                return products
        except Exception as e:
            parser_logger.error('parse_error:', str(e))

    def parse_prices(self, driver: SB) -> Tuple[Optional[str], Optional[str], Optional[str]]:
        """
        Возвращает (final_price, old_price, currency).
        Цены — строки только из цифр, валюта — символ ('₽', '$', '€').
        """
        final_text = ''
        old_text = ''

        try:
            final_el = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, 'ins[class*="priceBlockFinalPrice"]')
                )
            )
            final_text = final_el.text.strip()
        except Exception as e:
            parser_logger.warning(f'final_price_not_found: {e}')

        try:
            old_el = driver.find_element(
                By.CSS_SELECTOR, 'span[class*="priceBlockOldPrice"]'
            )
            old_text = old_el.text.strip()
        except Exception:
            # Старой цены может не быть (нет скидки) — это не ошибка
            old_text = ''

        final_price, currency = self._extract_price_and_currency(final_text)
        old_price, _ = self._extract_price_and_currency(old_text)
        return final_price, old_price, currency


    @staticmethod
    def _extract_price_and_currency(text: str) -> Tuple[Optional[str], Optional[str]]:
        """
        '48\u00a0690\u00a0₽'  ->  ('48690', '₽')
        '68 385 ₽'            ->  ('68385', '₽')
        '1 234,56 €'          ->  ('1234,56', '€')
        """
        if not text:
            return None, None

        # число (цифры + пробелы/nbsp + запятая или точка) и символ валюты
        match = re.search(r'([\d\s\u00A0.,]+?)\s*([^\d\s\u00A0.,]+)\s*$', text)
        if not match:
            return None, None

        price = re.sub(r'[\s\u00A0]+', '', match.group(1)).strip('.,')
        currency = match.group(2).strip()
        return price, currency

    def parse_product(self, driver: SB, url: str) -> Optional[TVCard]:
        try:
            tv_card = TVCard()
            driver.uc_open_with_reconnect(url)
            tv_card.url = url

            title_el = WebDriverWait(driver, 15).until(
                EC.visibility_of_element_located(
                    (By.CSS_SELECTOR, 'h2[class*="productTitle"]')
                )
            )
            tv_card.title = title_el.text.strip()

            price, old_price, currency = self.parse_prices(driver)
            tv_card.discount_price = price
            tv_card.full_price = old_price
            tv_card.currency = currency if currency else '₽'

            return tv_card
        except Exception as e:
            parser_logger.error(f'parse_product_error: {e}')
            return None


if __name__ == '__main__':
    parser = WBParserSelenium(proxy_list=None, max_items=5)
    res = parser.parse()
    if res:
        for i in res:
            print(i.get_dict())
        print(len(res))
    else:
        print('empty')
