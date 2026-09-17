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


setup_logger('dns')
parser_logger = logger.bind(log_name="dns")


class YandexParserSelenium:
    def __init__(self, search_text, proxy_list=None, max_items=50):
        self._url = 'https://www.dns-shop.ru/catalog/17a8ae4916404e77/televizory/'
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
                for link in links:
                    tv_card = self.parse_product(driver, 'https://www.dns-shop.ru' + link)
                    if tv_card:
                        products.append(tv_card)
                return products
        except Exception as e:
            parser_logger.warning('parse_error:', str(e))

    def parse_price(self, soup: BeautifulSoup) -> Tuple[Optional[int], Optional[str]]:
        """
        Извлекает цену и валюту из карточки товара.

        Returns:
            Tuple[Optional[int], Optional[str]]: (цена как целое число, символ валюты)
            Например: (64999, '₽') или (None, None), если цена не найдена.
        """
        try:
            price_tag = soup.select_one('div.product-buy__price')
            if not price_tag:
                parser_logger.warning('Не найден блок с ценой (div.product-buy__price)')
                return None, None

            raw_text = price_tag.get_text(strip=True)
            cleaned = re.sub(r'[\s\u00a0\u2009\u202f]+', '', raw_text)

            # Ищем число и валютный символ
            # \d+ — цифры; [₽$€¥£] — распространённые символы валют
            match = re.match(r'^(\d+)([^\d]*)$', cleaned)
            if not match:
                parser_logger.warning(f'Не удалось распарсить цену: {raw_text!r}')
                return None, None

            price = int(match.group(1))
            currency = match.group(2).strip()

            return price, currency

        except Exception as e:
            parser_logger.warning('parse_price_error:', str(e))
            return None, None

    def parse_description(self, soup: BeautifulSoup) -> Optional[str]:
        """
        Извлекает описание товара из карточки.

        Обрабатывает:
        - неразрывные пробелы (\xa0) → обычный пробел
        - теги <br> → символ переноса строки
        - лишние пустые строки и отступы
        """
        try:
            desc_tag = soup.select_one('p.product-card-description__text-description')
            if not desc_tag:
                parser_logger.warning('Не найден блок описания товара')
                return None

            for br in desc_tag.find_all('br'):
                br.replace_with('\n')

            text = desc_tag.get_text()
            text = text.replace('\xa0', ' ')
            text = re.sub(r'[ \t]+', ' ', text)
            lines = [line.strip() for line in text.split('\n')]
            lines = [line for line in lines if line]
            text = '\n'.join(lines)

            return text or None

        except Exception as e:
            parser_logger.warning('parse_description_error:', str(e))
            return None

    def expand_characteristics(self, driver) -> bool:
        """Кликает 'Все характеристики', если кнопка есть."""
        try:
            buttons = driver.find_elements(
                By.CSS_SELECTOR, 'button.product-characteristics__expand'
            )
            if not buttons:
                return True  # нечего раскрывать

            btn = buttons[0]
            driver.execute_script(
                "arguments[0].scrollIntoView({block: 'center'});", btn
            )
            sleep(random.uniform(0.5, 1.2))
            btn.click()
            sleep(random.uniform(1.5, 3.0))
            return True
        except Exception as e:
            parser_logger.warning('expand_characteristics_error:', str(e))
            return False

    def parse_characteristics(self, soup: BeautifulSoup) -> dict:
        """
        Извлекает все характеристики со страницы товара в плоский словарь.
        Returns:
            dict: {название характеристики: значение}
        """
        specs = {}
        try:
            items = soup.select('li.product-characteristics__spec')
            if not items:
                parser_logger.warning('Не найдены характеристики товара')
                return specs

            for li in items:
                title_tag = li.select_one('.product-characteristics__spec-title')
                value_tag = li.select_one('.product-characteristics__spec-value')

                if not title_tag or not value_tag:
                    continue

                key = self._clean_text(title_tag.get_text())
                value = self._clean_text(value_tag.get_text())

                if key and value:
                    specs[key] = value

        except Exception as e:
            parser_logger.warning('parse_characteristics_error:', str(e))

        return specs

    @staticmethod
    def _clean_text(text: str) -> str:
        """Нормализует текст: \xa0 → пробел, схлопывает пробелы, strip."""
        if not text:
            return ''
        text = text.replace('\xa0', ' ')
        text = re.sub(r'\s+', ' ', text)
        return text.strip()

    def parse_product(self, driver, url) -> Optional[TVCard]:
        try:
            tv_card = TVCard()
            driver.uc_open_with_reconnect(url)
            tv_card.url = url
            h1_element = driver.find_element(By.CSS_SELECTOR, 'h1.product-card-top__title')
            tv_card.title = h1_element.text

            price, currency = self.parse_price(BeautifulSoup(driver.get_page_source(), 'html.parser'))
            tv_card.full_price = price
            tv_card.currency = currency

            button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable(
                    (By.CSS_SELECTOR, 'a.product-card-top__specs-more')
                )
            )
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", button)
            sleep(random.uniform(0.5, 1.5))
            button.click()
            sleep(random.uniform(2.0, 4.0))

            soup = BeautifulSoup(driver.get_page_source(), 'html.parser')
            desc = self.parse_description(soup)
            tv_card.description = desc

            self.expand_characteristics(driver)
            soup = BeautifulSoup(driver.get_page_source(), 'html.parser')
            characteristics = self.parse_characteristics(soup)
            for key, value in characteristics.items():
                l_key = key.lower()
                if l_key.find('диагональ экрана (дюйм)') != -1:
                    tv_card.diagonal = value
                elif l_key.find('разрешение экрана') != -1:
                    tv_card.screen_resolution = value
                elif l_key.find('технология экрана') != -1:
                    tv_card.matrix = value
                elif l_key.find('операционная система') != -1:
                    tv_card.os = value
                elif l_key.find('частота обновления экрана') != -1:
                    tv_card.refresh_rate = value
                elif l_key.find('модель') != -1:
                    tv_card.name = value

            return tv_card
        except Exception as e:
            parser_logger.warning('parse_product_error:', str(e))


if __name__ == '__main__':
    parser = YandexParserSelenium(search_text='телевизор', proxy_list=None, max_items=200)
    res = parser.parse()
    if res:
        for i in res:
            print(i.get_dict())
        print(len(res))
    else:
        print('empty')
