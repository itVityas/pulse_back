import random
from time import sleep
import re
from typing import Optional, List, Tuple, Dict

from bs4 import BeautifulSoup
from seleniumbase import SB
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
            with SB(uc=True, incognito=True, locale="ru", locale_code="ru") as driver:
                driver.uc_open_with_reconnect(self._url)
                driver.sleep(10)
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
            parser_logger.error(f'parse_error: {e}')

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

    def open_characteristics(self, driver: SB) -> Dict:
        """
        Кликает по кнопке "Характеристики и описание", дожидается открытия
        бокового меню и возвращает dict с полями для TVCard.
        """
        data: Dict = {
            'description': None,
            'os': None,
            'screen_resolution': None,
            'brand': None,
            'matrix': None,
            'diagonal': None,
            'refresh_rate': None,
        }

        try:
            # 1. Кнопка "Характеристики и описание"
            button = WebDriverWait(driver, 15).until(
                EC.element_to_be_clickable(
                    (By.CSS_SELECTOR, 'button[class*="btnDetail"], a[class*="btnDetail"]')
                )
            )
            driver.execute_script(
                "arguments[0].scrollIntoView({block: 'center'});", button
            )
            sleep(random.uniform(0.4, 0.8))
            try:
                button.click()
            except Exception:
                # иногда клик перехватывается оверлеем — жмём через JS
                driver.execute_script("arguments[0].click();", button)

            # 2. Панель с характеристиками
            WebDriverWait(driver, 15).until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, 'div[class*="detailsDesktopWrapper"]')
                )
            )
            sleep(random.uniform(0.6, 1.0))  # даём таблицам отрисоваться

            soup = BeautifulSoup(driver.get_page_source(), 'html.parser')
            panel = soup.select_one('div[class*="detailsDesktopWrapper"]')
            if not panel:
                parser_logger.warning('panel_not_found')
                return data

            # 3. Собираем все пары "характеристика -> значение"
            specs: Dict[str, str] = {}
            for table in panel.select('table'):
                for row in table.select('tr'):
                    key_el = row.select_one('th')
                    val_el = row.select_one('td')
                    if not key_el or not val_el:
                        continue
                    key = key_el.get_text(' ', strip=True)
                    val = val_el.get_text(' ', strip=True)
                    if key and val:
                        specs[key] = val

            # 4. Описание
            desc_el = panel.select_one('section#section-description p')
            if desc_el:
                data['description'] = desc_el.get_text('\n', strip=True)

            # 5. Маппинг в поля TVCard
            data['os'] = specs.get('Операционная система')
            data['screen_resolution'] = specs.get('Разрешение экрана')
            data['matrix'] = specs.get('Тип матрицы')
            data['brand'] = (
                specs.get('Бренд')
                or specs.get('Производитель')
                or specs.get('Марка')
            )

            # Диагональ: '65"' -> 65
            diag_raw = specs.get('Диагональ')
            if diag_raw:
                m = re.search(r'\d+', diag_raw)
                if m:
                    data['diagonal'] = int(m.group())

            # Частота обновления: '60 Гц' -> 60
            rr_raw = (
                specs.get('Частота смены кадров (Гц)')
                or specs.get('Частота обновления')
            )
            if rr_raw:
                m = re.search(r'\d+', rr_raw)
                if m:
                    data['refresh_rate'] = int(m.group())

            return data

        except Exception as e:
            parser_logger.error(f'open_characteristics_error: {e}')
            return data

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

            chars = self.open_characteristics(driver)
            tv_card.description = chars['description']
            tv_card.os = chars['os']
            tv_card.screen_resolution = chars['screen_resolution']
            tv_card.matrix = chars['matrix']
            tv_card.diagonal = chars['diagonal']
            tv_card.refresh_rate = chars['refresh_rate']
            if chars['brand']:
                tv_card.brand = chars['brand']

            return tv_card
        except Exception as e:
            parser_logger.error(f'parse_product_error: {e}')
            return None


if __name__ == '__main__':
    parser = WBParserSelenium(proxy_list=None, max_items=50)
    res = parser.parse()
    if res:
        for i in res:
            print(i.get_dict())
        print(len(res))
    else:
        print('empty')
