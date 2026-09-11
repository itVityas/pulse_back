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
from loguru import logger

from settings.loguru_conf import setup_logger
from parsings.tv_card import TVCard


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

    async def _close_register(self, driver):
        close_buttons = driver.find_elements(By.XPATH, "//button[@class='close-modal-btn']")

        # 2. Если список не пустой, значит окно появилось
        if len(close_buttons) > 0:
            close_buttons[0].click()
            await asyncio.sleep(2)
            logger.info('close register modal')

    async def parse(self) -> List[TVCard]:
        try:
            self._driver.implicitly_wait(1)
            self._driver.get(self._url)
            print('load_page')

            products = []
            links = set()
            last_height = self._driver.execute_script("return document.body.scrollHeight")
            scroll_attemps = 0
            while True:
                await self._close_register(self._driver)
                # element = self._driver.find_element(By.ID, 'SerpStatic')
                # soup = BeautifulSoup(element.get_attribute('outerHTML'), 'html.parser')
                soup = BeautifulSoup(self._driver.page_source, 'html.parser')
                a_tags = soup.select('a')
                print('find tags', len(a_tags))
                for a_tag in a_tags:
                    link = a_tag.get('href')
                    if link and link not in links and link.find('/card/') != -1:
                        links.add(link)
                print('find links: ', len(links))
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
                        print('прокрутка:', new_height, last_height)
                        logger.info('Достигнут конец прокрутки')
                        break
                else:
                    last_height = new_height
                    scroll_attemps = 0

            for link in links:
                tv_card = await self.parse_product_page('https://market.yandex.ru' + link)
                if tv_card:
                    products.append(tv_card)

            self._driver.quit()
            return products
        except Exception as e:
            parser_logger.error('parse_error: ' + str(e))

    async def extract_description(self, driver, wait) -> str | None:
        """
        Ищет на странице блок описания. Если есть кнопка «Всё описание» —
        нажимает её и возвращает полный текст описания.
        """
        try:
            # 1. Ждём появления самого блока с описанием
            wait.until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, '[data-zone-name="description"]')
                )
            )
        except TimeoutException:
            parser_logger.warning("Блок описания не найден на странице")
            return None

        # 2. Проверяем и нажимаем кнопку «Всё описание», если она есть
        try:
            read_more_btn = driver.find_element(
                By.CSS_SELECTOR, 'button[data-auto="read-more-description"]'
            )
            # Прокручиваем к кнопке и кликаем
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", read_more_btn)
            wait.until(EC.element_to_be_clickable(
                (By.CSS_SELECTOR, 'button[data-auto="read-more-description"]')
            ))
            read_more_btn.click()
            parser_logger.info("✅ Нажата кнопка «Всё описание»")

            # Небольшая пауза на раскрытие (или ждём исчезновения класса lineClamp)
            WebDriverWait(driver, 5).until(
                lambda d: 'lineClamp' not in (
                    d.find_element(
                        By.CSS_SELECTOR,
                        '[data-zone-name="description"] span.ds-text'
                    ).get_attribute('class') or ''
                )
            )
        except (NoSuchElementException, TimeoutException):
            parser_logger.info("Кнопка «Всё описание» отсутствует — описание уже полное")

        # 3. Достаём текст описания
        try:
            # После раскрытия текст лежит внутри div внутри span, либо прямо в span
            desc_container = driver.find_element(
                By.CSS_SELECTOR,
                '[data-zone-name="description"] span.ds-text'
            )

            # Пробуем получить текст из вложенного div (как в вашем HTML)
            try:
                inner_div = desc_container.find_element(By.TAG_NAME, 'div')
                description = inner_div.text.strip()
            except NoSuchElementException:
                description = desc_container.text.strip()

            if not description:
                parser_logger.warning("Описание пустое")
                return None

            parser_logger.info(f"📄 Описание получено, длина: {len(description)} символов")
            return description

        except NoSuchElementException as e:
            parser_logger.warning(f"Не удалось извлечь текст описания: {e}")
            return None

    async def extract_price_details(self, driver, wait) -> dict:
        """
        Кликает на иконку «Детали цены», дожидается появления модального окна
        и извлекает 3 цены + скидку.

        Returns:
            dict: {
                'price_with_card': int,   # цена с картой (Пэй)
                'price_without_card': int,  # цена без карты
                'regular_price': int,      # обычная цена (зачёркнутая)
                'discount_percent': int,   # процент скидки
                'discount_amount': int,    # сумма скидки в рублях
                'currency': str,
            }
        """
        result: dict = {}

        # --- 1. Клик по иконке деталей цены ---
        try:
            icon = wait.until(EC.element_to_be_clickable(
                (By.CSS_SELECTOR, '[data-auto="price-details-icon"]')
            ))
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", icon)
            await asyncio.sleep(0.5)
            icon.click()
            parser_logger.info("✅ Клик по иконке «Детали цены»")
        except (TimeoutException, NoSuchElementException) as e:
            parser_logger.warning(f"Иконка деталей цены не найдена: {e}")
            return result

        # --- 2. Ждём появления модального окна ---
        try:
            modal = wait.until(EC.presence_of_element_located(
                (By.CSS_SELECTOR, '[data-zone-name="priceDetailsPopup"]')
            ))
            # Ждём, пока модалка станет видимой
            wait.until(EC.visibility_of_element_located(
                (By.CSS_SELECTOR, '[data-zone-name="priceDetailsPopup"] .ds-modal')
            ))
            await asyncio.sleep(0.5)
            parser_logger.info("✅ Модальное окно «Детали цены» открыто")
        except TimeoutException:
            parser_logger.warning("Модальное окно деталей цены не появилось")
            return result

        # --- 3. Парсим содержимое модалки ---
        try:
            soup = BeautifulSoup(modal.get_attribute('outerHTML'), 'html.parser')

            # Все цены в модалке — элементы с классом ds-valueLine
            # Структура блока: div.ds-flex._2pfPL содержит 2 блока (с картой и без)
            price_row = soup.select_one('div.ds-flex._2pfPL')
            if not price_row:
                parser_logger.warning("Блок с ценами в модалке не найден")
                return result

            price_blocks = price_row.find_all('button', recursive=False) or \
                price_row.find_all('div', recursive=False)

            # Извлекаем цифры из текста
            def _digits(text: str) -> int | None:
                if not text:
                    return None
                digits = re.sub(r'[^\d]', '', text)
                return int(digits) if digits else None

            # Первая цена — с картой (Пэй)
            if len(price_blocks) >= 1:
                first_price_span = price_blocks[0].find('span', class_=lambda c: c and 'headline-4' in c)
                if first_price_span:
                    result['price_with_card'] = _digits(first_price_span.get_text())

            # Вторая цена — без карты
            if len(price_blocks) >= 2:
                second_price_span = price_blocks[1].find('span', class_=lambda c: c and 'headline-4' in c)
                if second_price_span:
                    result['price_without_card'] = _digits(second_price_span.get_text())

            # Третья цена — обычная (зачёркнутая) + скидка
            # Ищем блок с «Обычная цена» и «Скидка»
            detail_rows = soup.select('div.ds-flex.ds-flex_jc_sb')
            for row in detail_rows:
                label_elem = row.find('span', class_=lambda c: c and 'ds-text' in c)
                if not label_elem:
                    continue
                label = label_elem.get_text(strip=True).lower()

                # Все valueLine в строке
                values = row.find_all('span', class_=lambda c: c and 'ds-valueLine' in c)

                if 'обычная цена' in label:
                    # Внутри первого valueLine — зачёркнутая цена
                    if values:
                        price_span = values[0].find('span', class_=lambda c: c and 'ds-text' in c)
                        if price_span:
                            result['regular_price'] = _digits(price_span.get_text())

                elif 'скидка' in label:
                    # Первое значение — процент, второе — сумма
                    if len(values) >= 1:
                        pct_span = values[0].find('span', class_=lambda c: c and 'ds-text' in c)
                        if pct_span:
                            result['discount_percent'] = _digits(pct_span.get_text())
                    if len(values) >= 2:
                        amt_span = values[1].find('span', class_=lambda c: c and 'ds-text' in c)
                        if amt_span:
                            # Может быть «–46 032» — берём модуль
                            result['discount_amount'] = _digits(amt_span.get_text())

            # Валюта — ищем символ ₽ в модалке
            currency_match = re.search(r'[₽$€£¥]', modal.text)
            if currency_match:
                result['currency'] = currency_match.group(0)

            parser_logger.info(f"💰 Цены извлечены: {result}")

        except Exception as e:
            parser_logger.error(f"Ошибка при парсинге модалки цен: {e}")

        # --- 4. Закрываем модалку ---
        try:
            close_btn = driver.find_element(
                By.CSS_SELECTOR,
                '[data-zone-name="priceDetailsPopup"] .ds-modal__close'
            )
            close_btn.click()
            await asyncio.sleep(0.5)
        except (NoSuchElementException, Exception):
            # Если не нашли кнопку — жмём Escape
            try:
                from selenium.webdriver.common.keys import Keys
                driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.ESCAPE)
            except Exception:
                pass

        return result

    async def extract_full_specs(self, driver, wait) -> dict:
        """
        Находит кнопку «Все характеристики», нажимает её,
        и извлекает полный список характеристик товара.

        Returns:
            dict: {название характеристики: значение}
        """
        specs: dict = {}

        # --- 1. Клик по кнопке «Все характеристики» ---
        try:
            button = wait.until(EC.element_to_be_clickable((
                By.XPATH,
                '//button[.//span[normalize-space(text())="Все характеристики"]]'
            )))
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", button)
            await asyncio.sleep(1)
            button.click()
            parser_logger.info("✅ Нажата кнопка «Все характеристики»")

            # Ждём, пока откроется drawer/modal с полным списком.
            # Признак — появление новых label вне блока aboutFullSpecsLine__0
            # или исчезновение класса с ограничением высоты.
            await asyncio.sleep(2)
        except (TimeoutException, NoSuchElementException):
            parser_logger.info("Кнопка «Все характеристики» не найдена — используем данные со страницы")

        # --- 2. Основной парсинг DOM ---
        soup = BeautifulSoup(driver.page_source, 'html.parser')

        # Каждый <label> — одна характеристика.
        # Имя лежит в span[data-auto="product-spec"] (у копируемых) или в первом span.ds-text.
        # Значение — в последнем span.ds-text внутри label.
        for label in soup.find_all('label'):
            # Имя характеристики
            name_span = label.find('span', attrs={'data-auto': 'product-spec'})
            if name_span:
                name = name_span.get_text(strip=True)
            else:
                spans = label.find_all(
                    'span',
                    class_=lambda c: c and 'ds-text' in c
                )
                if len(spans) < 2:
                    continue
                name = spans[0].get_text(strip=True)

            # Значение — берём последний span с ds-text
            all_spans = label.find_all(
                'span',
                class_=lambda c: c and 'ds-text' in c
            )
            if not all_spans:
                continue

            # Если у label есть ссылка (например, бренд) — берём текст из неё
            link = label.find('a')
            if link:
                value = link.get_text(strip=True)
            else:
                value = all_spans[-1].get_text(strip=True)

            name = name.strip()
            value = value.strip()

            if name and value and name != value:
                specs[name] = value

        parser_logger.info(f"📋 Собрано характеристик из DOM: {len(specs)}")

        # --- 3. Fallback: если через DOM мало что собралось,
        #          тянем полный список из JSON в <noframes data-apiary="patch"> ---
        if len(specs) < 5:
            json_specs = self._extract_specs_from_json(driver.page_source)
            if json_specs:
                specs.update(json_specs)
                parser_logger.info(f"📋 Дополнено из JSON: всего {len(specs)} характеристик")

        return specs

    async def parse_product_page(self, link: str) -> Optional[TVCard]:
        try:
            service = Service(executable_path=ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=self._chrome_options)
            driver.get(link)
            parser_logger.info(f"Страница товара загружена. {link}")
            await self._close_register(driver)

            tv_card = TVCard()
            wait = WebDriverWait(driver, 10)
            title_element = wait.until(
                EC.presence_of_element_located((By.XPATH, '//h1[@data-additional-zone="title"]'))
            )
            if title_element:
                tv_card.title = title_element.text

            soup = BeautifulSoup(driver.page_source, 'html.parser')
            labels = soup.find_all('label')
            specs_dict = {}
            for label in labels:
                name_elem = label.find('span', class_=lambda c: c and 'ds-text' in c)
                value_elem = label.find_all('span', class_=lambda c: c and 'ds-text' in c)
                if name_elem and len(value_elem) >= 2:
                    name = name_elem.get_text(strip=True)
                    value = value_elem[-1].get_text(strip=True)
                    specs_dict[name] = value
            for key in specs_dict.keys():
                l_key = key.lower()
                if l_key.find('диагональ') != -1:
                    tv_card.diagonal = specs_dict.get(key, None)
                elif l_key.find('разрешение') != -1 or l_key.find('hd') != -1:
                    tv_card.screen_resolution = specs_dict.get(key, None)
                elif l_key.find('операционная система') != -1 or l_key.find('os') != -1 or l_key.find('ос') != -1:
                    tv_card.os = specs_dict.get(key, None)
                elif l_key.find('частота') != -1:
                    tv_card.refresh_rate = specs_dict.get(key, None)

            tv_card.description = await self.extract_description(driver, wait)

            specs_dict = await self.extract_full_specs(driver, wait)
            tv_card.description = await self.extract_description(driver, wait)

            # --- Сопоставление полей характеристики---
            for key, value in specs_dict.items():
                l_key = key.lower()
                if l_key == 'бренд':
                    tv_card.brand = value
                elif l_key.find('разрешение') != -1 or l_key.find('hd') != -1:
                    tv_card.screen_resolution = specs_dict.get(key, None)
                elif l_key.find('матриц') != -1:
                    tv_card.matrix = specs_dict.get(key, None)
                elif l_key.find('операционная система') != -1 or l_key.find('os') != -1 or l_key.find('ос') != -1:
                    tv_card.os = specs_dict.get(key, None)
                elif l_key.find('частота') != -1:
                    tv_card.refresh_rate = specs_dict.get(key, None)
                if l_key.find('диагональ') != -1:
                    tv_card.diagonal = specs_dict.get(key, None)

            prices = await self.extract_price_details(driver, wait)
            tv_card.card_price = prices.get('price_with_card')
            tv_card.discount_price = prices.get('price_without_card')
            tv_card.full_price = prices.get('regular_price')
            tv_card.currency = prices.get('currency')

            return tv_card
        except Exception as e:
            parser_logger.error('parse_product_page error: ' + str(e))
            return None
        finally:
            driver.quit()


if __name__ == '__main__':
    with YandexParserSelenium(search_text='телевизор', proxy_list=None, max_items=5) as parser:
        res = asyncio.run(parser.parse())
        for i in res:
            print(i.get_dict())
        print(len(res))
