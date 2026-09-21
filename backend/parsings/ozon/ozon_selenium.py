import random
from time import sleep
import re
from typing import Optional, List, Tuple

from bs4 import BeautifulSoup
from seleniumbase import SB, Driver
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
            # with SB(uc=True, incognito=True, locale="ru") as driver:
            with Driver(uc=True, incognito=True, locale="ru") as driver:
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
                for link in links:
                    tv_card = self.parse_product(driver, 'https://ozon.ru' + link)
                    if tv_card:
                        products.append(tv_card)
                return products
        except Exception as e:
            parser_logger.warning('parse_error:', str(e))

    def get_price(self, driver) -> Optional[Tuple[float, str]]:
        """
        Возвращает (цена_float, код_валюты) или None, если не найдено.
        Пример: ('478,71 BYN') -> (478.71, 'BYN')
        """
        PRICE_RE = re.compile(r'(\d[\d\s\u00a0]*[.,]?\d*)\s*([A-Za-zА-Яа-я]{2,4})|[₽$€¥])')
        try:
            driver.wait_for_element('[data-widget="webPrice"]', timeout=15)
            # raw = driver.get_text('[data-widget="webPrice"] .tsHeadline600Large').strip()
            raw = driver.get_text(
                '[data-widget="webPrice"] span.tsHeadline600Large'
            ).strip()
        except Exception as e:
            parser_logger.warning(f'price_not_found: {e}')
            return None

        # Иногда внутри пробел-разделитель тысяч — убираем
        raw = raw.replace('\u00a0', ' ').strip()

        match = PRICE_RE.search(raw)
        if not match:
            parser_logger.warning(f'price_regex_mismatch: {raw!r}')
            return None

        number_str, currency = match.groups()

        # "1 234,56" -> "1234.56"  |  "1,234.56" -> "1234.56"
        number_str = number_str.replace(' ', '')
        if ',' in number_str and '.' in number_str:
            # Определяем, что разделитель дробной части (последний символ)
            if number_str.rfind(',') > number_str.rfind('.'):
                number_str = number_str.replace('.', '').replace(',', '.')
            else:
                number_str = number_str.replace(',', '')
        else:
            number_str = number_str.replace(',', '.')

        try:
            price = float(number_str)
        except ValueError:
            parser_logger.warning(f'price_parse_error: {raw!r}')
            return None

        return price, currency.upper()

    def _extract_description_from_soup(self, soup: BeautifulSoup) -> Optional[str]:
        """Пытается вытащить описание из уже разобранного DOM."""
        # 1) Стандартные виджеты Ozon (самый надёжный путь)
        for sel in (
            '[data-widget="webDescription"]',
            '[data-widget="webShortDescription"]',
            '[data-widget="webRichAnnotation"]',
        ):
            block = soup.select_one(sel)
            if block:
                text = block.get_text(separator='\n', strip=True)
                if text:
                    return text

        # 2) Fallback: span с классами RA-* (текущая вёрстка из твоего фрагмента)
        for span in soup.find_all('span'):
            classes = span.get('class') or []
            if any(c.startswith('RA-') for c in classes):
                text = span.get_text(separator='\n', strip=True)
                if len(text) > 80:          # отсекаем короткие служебные спаны
                    return text

        return None

    def parse_description(self, driver) -> Optional[str]:
        """
        Возвращает описание товара.
        Если описания нет в DOM — кликает по кнопке 'Перейти к описанию'
        и ждёт его появления.
        """
        try:
            # --- Шаг 1. Может, описание уже в DOM ---
            soup = BeautifulSoup(driver.get_page_source(), 'html.parser')
            desc = self._extract_description_from_soup(soup)
            if desc:
                parser_logger.debug('description_found_on_load')
                return desc

            # --- Шаг 2. Пробуем нажать кнопку ---
            clicked = False
            try:
                btn = driver.find_element(
                    By.CSS_SELECTOR,
                    '[title="Перейти к описанию"]'
                )
                driver.execute_script(
                    "arguments[0].scrollIntoView({block:'center'});", btn
                )
                sleep(random.uniform(0.4, 1.0))

                try:
                    btn.click()
                except Exception:
                    # Иногда клик перехватывает дочерний svg — жмём через JS
                    driver.execute_script("arguments[0].click();", btn)

                clicked = True
                parser_logger.debug('desc_button_clicked')
            except Exception as e:
                parser_logger.debug(f'desc_button_not_found: {e}')

            # --- Шаг 3. Ждём появления описания (если кликали) ---
            if clicked:
                for _ in range(20):              # ~10 секунд
                    sleep(0.5)
                    soup = BeautifulSoup(driver.get_page_source(), 'html.parser')
                    desc = self._extract_description_from_soup(soup)
                    if desc:
                        return desc

            # --- Шаг 4. Последняя попытка — перечитать DOM как есть ---
            soup = BeautifulSoup(driver.get_page_source(), 'html.parser')
            return self._extract_description_from_soup(soup)

        except Exception as e:
            parser_logger.error(f'parse_description_error: {e}')
            return None

    def parse_product(self, driver, url) -> Optional[TVCard]:
        try:
            tv_card = TVCard()
            driver.uc_open_with_reconnect(url)
            tv_card.url = url

            h1_element = driver.find_element(By.CSS_SELECTOR, 'h1.pdp_i5b.tsHeadline550Medium')
            tv_card.title = h1_element.text
            print(tv_card.title)

            price, currency = self.get_price(driver)
            tv_card.full_price = price
            tv_card.currency = currency
            print(price, currency)

            tv_card.description = self.parse_description(driver)
            print(tv_card.description)

            return tv_card
        except Exception as e:
            parser_logger.error('parse_product_error:', str(e))


if __name__ == '__main__':
    parser = OzonParserSelenium(proxy_list=None, max_items=5)
    res = parser.parse()
    if res:
        for i in res:
            print(i.get_dict())
        print(len(res))
    else:
        print('empty')
