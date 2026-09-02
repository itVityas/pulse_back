import asyncio
import re
import random

from crawlee.proxy_configuration import ProxyConfiguration
from crawlee.crawlers import PlaywrightCrawler, PlaywrightCrawlingContext
from crawlee.router import Router
from loguru import logger

from settings.loguru_conf import setup_logger


setup_logger('yandex')
parser_logger = logger.bind(log_name="yandex")

router = Router[PlaywrightCrawlingContext]()

MAXPASS = -1


async def check_captcha(context: PlaywrightCrawlingContext) -> None:
    """Проверка на капчу
    """
    content = await context.page.content()
    if "Капча" in content or "SmartCaptcha" in content or "captcha" in context.page.url.lower():
        return True
    return False


async def scroll_page(context: PlaywrightCrawlingContext) -> None:
    """Прокрутка страницы для подгрузки товаров
    """
    if await check_captcha(context):
        raise Exception("Капча обнаружена")
    operation = random.randint(0, 1)
    if operation == 0:
        await context.page.evaluate("window.scrollBy(0, window.innerHeight * 0.8)")
    elif operation == 1:
        await context.page.keyboard.press("PageDown")
    await context.page.mouse.wheel(0, random.randint(600, 1200))
    await asyncio.sleep(random.uniform(1.5, 5))
    try:
        await context.page.wait_for_load_state('networkidle', timeout=10000)
    except Exception as e:
        parser_logger.info(f"Таймаут ожидания load_state: {e}")


def extract_currency_symbol(price_text: str) -> str:
    """Извлечение символа валюты из текста цены"""
    currency_pattern = r'[₽$€£¥]|руб|RUB|USD|EUR'
    match = re.search(currency_pattern, price_text)
    if match:
        return match.group(0)

    cleaned = re.sub(r'[\d\s.,]', '', price_text)
    if cleaned:
        return cleaned.strip()

    return '₽'


async def extract_prices_direct(context: PlaywrightCrawlingContext, product_data: dict) -> None:
    """Извлечение цен напрямую со страницы без открытия блока"""
    try:
        # Ищем текущую цену (со скидкой)
        current_price_elem = context.page.locator('span[data-auto="snippet-price-current"]')
        if await current_price_elem.count() > 0:
            current_price_text = await current_price_elem.first.inner_text()
            current_price = ''.join(filter(str.isdigit, current_price_text))
            if current_price:
                product_data['current_price'] = current_price

        # Ищем старую цену (зачёркнутую)
        old_price_elem = context.page.locator('span[data-auto="snippet-price-old"]')
        if await old_price_elem.count() > 0:
            old_price_text = await old_price_elem.first.inner_text()
            old_price = ''.join(filter(str.isdigit, old_price_text))
            if old_price:
                product_data['old_price'] = old_price

        # Вторая цена - без карты
        price_block = context.page.locator('div.ds-flex._2pfPL')
        all_prices = await price_block.locator('span.ds-valueLine').all()
        no_card_price_text = await all_prices[1].inner_text()
        no_card_price = ''.join(filter(str.isdigit, no_card_price_text))
        if no_card_price:
            product_data['no_card_price'] = no_card_price

        # Извлекаем символ валюты из первой цены
        currency_symbol = extract_currency_symbol(no_card_price_text)
        if currency_symbol:
            product_data['currency'] = currency_symbol
            parser_logger.info(f"Символ валюты: {currency_symbol}")

    except Exception as e:
        parser_logger.warning(f"Ошибка при прямом парсинге цен: {e}")
        raise e


async def close_add(context: PlaywrightCrawlingContext) -> None:
    """Закрытие поп-up окна авторизации при необходимости"""
    # Проверка на явную блокировку/капчу
    captcha = await check_captcha(context)
    if captcha:
        raise Exception("Капча обнаружена")

    # Закрываем окно авторизации, если появилось
    try:
        close_button = context.page.locator('button[aria-label="Закрыть"]').or_(
            context.page.locator('div[data-zone-name="loginPopup"] button')
        ).or_(
            context.page.locator('button:has-text("Закрыть")')
        )

        if await close_button.count() > 0:
            await close_button.first.click(timeout=2000)
            await asyncio.sleep(1)
            parser_logger.info("✅ Окно авторизации закрыто")
    except Exception:
        # Игнорируем, если окна нет
        # Если за 3 секунды окно не появилось, Playwright выбросит TimeoutError.
        # Мы его игнорируем и идем дальше парсить товары.
        parser_logger.info("Окно авторизации не появилось, продолжаем работу.")


@router.default_handler
async def default_handler(context: PlaywrightCrawlingContext) -> None:
    """Обработчик главной страницы поиска со всеми телевизорами"""
    parser_logger.info(f"Главная страница загружена успешно. {context.request.url}")

    await asyncio.sleep(2)

    await close_add(context)
    goods_find = 0
    if MAXPASS != -1:
        max_goods = MAXPASS
    else:
        max_goods = 2_147_483_647
    unique_urls = set()
    attemps = 0
    while goods_find < max_goods:
        try:
            # await context.page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            # Проверяем, жива ли страница
            try:
                await context.page.evaluate("1")
            except Exception as e:
                parser_logger.warning("Страница закрыта, прерываем прокрутку" + e)
                break
            try:
                # Прокрутка с таймаутом
                # await asyncio.wait_for(
                #     # context.page.evaluate("window.scrollBy(0, 1500)"),
                #     context.page.evaluate("window.scrollBy(0, window.innerHeight * 0.8)"),
                #     timeout=20.0
                # )
                # await context.page.evaluate("window.scrollBy(0, window.innerHeight * 0.8)")
                await scroll_page(context)
            except asyncio.TimeoutError:
                parser_logger.warning("Прокрутка зависла, продолжаем")
            except Exception as e:
                parser_logger.warning(f"Ошибка при прокрутке: {e}")
                break

            print('get content')
            await close_add(context)

            links_elements = await context.page.locator('a[href*="/card/"]').all()
            print('Links', len(links_elements))
            if len(links_elements) == 0:
                attemps += 1
                parser_logger.warning("Ссылки не найдены, продолжаем прокрутку")
                if attemps > 3:
                    break
            for link in links_elements:
                href = await link.get_attribute('href')
                if href:
                    attemps = 0
                    yandex_card = '/card/'
                    if yandex_card in href:
                        full_url = f"https://market.yandex.ru{href}"
                        if full_url not in unique_urls:
                            unique_urls.add(full_url)
                    goods_find = len(unique_urls)
                    if goods_find >= max_goods:
                        break
        except Exception as e:
            parser_logger.warning(f"Ошибка обработки: {e}")
            print(e)
    print(len(unique_urls))
    parser_logger.info(f"Найдено уникальных товаров: {len(unique_urls)}")
    await context.enqueue_links(
            urls=unique_urls,
            label='PRODUCT',
        )


@router.handler('PRODUCT')
async def product_handler(context: PlaywrightCrawlingContext) -> None:
    """Обработчик страницы товара"""
    parser_logger.info(f"Страница товара загружена. {context.request.url}")
    await asyncio.sleep(2)

    try:
        product_data = {
            'url': context.request.url,
            'name': await context.page.locator('h1[data-auto="productCardTitle"]').inner_text(),
        }

        # Извлекаем верхние характеристики
        spec_labels_top = await context.page.locator('label.ds-flex:has(span)').all()

        # --- Извлечение описания ---
        try:
            # Ищем описание в блоке с классом _2jcSz или через data-zone-name="description"
            description_elem = context.page.locator(
                '[data-zone-name="description"] div._2jcSz span.ds-text_lineClamp_4')

            if await description_elem.count() > 0:
                description_text = await description_elem.inner_text()
                product_data['description'] = description_text.strip()
            else:
                # Альтернативный поиск описания
                description_elem = context.page.locator(
                    'div[data-zone-name="description"] span.ds-text_lineClamp_4')
                if await description_elem.count() > 0:
                    description_text = await description_elem.inner_text()
                    product_data['description'] = description_text.strip()
                else:
                    product_data['description'] = None
                    parser_logger.warning("Описание не найдено")
        except Exception as e:
            parser_logger.warning(f"Ошибка при извлечении описания: {e}")
            product_data['description'] = None

        # Переходим на вкладку с полными характеристиками
        full_specs_button = context.page.locator(
                selector='a[data-auto="full-specs-link"]',
                has_text='Все характеристики',
            ).first
        if await full_specs_button.count() > 0:
            await full_specs_button.scroll_into_view_if_needed()
            await asyncio.sleep(0.5)
            await full_specs_button.click()
        else:
            parser_logger.warning('Все характеристики не найдены')
        await asyncio.sleep(2)

        spec_labels_all = await context.page.locator('label.ds-flex:has(span)').all()
        specs = {}
        spec_labels = spec_labels_top + spec_labels_all

        for label in spec_labels:
            try:
                # Пытаемся найти название (первый span) и значение (последний span)
                # Но нужно исключить span внутри ссылок (если значение - это ссылка)
                # Поэтому ищем все span, которые являются прямыми потомками label
                all_spans = await label.locator('> div > span').all()

                # Если не нашли через прямой путь, пробуем все span внутри label
                if not all_spans:
                    all_spans = await label.locator('span').all()

                if len(all_spans) < 2:
                    continue

                # Первый span - это обычно название, последний - значение
                key = await all_spans[0].inner_text()
                value = await all_spans[-1].inner_text()

                # Очищаем от лишних пробелов
                key = key.strip()
                value = value.strip()

                # Если значение пустое, пробуем взять текст из ссылки, если она есть
                if not value:
                    link = label.locator('a')
                    if await link.count() > 0:
                        value = await link.inner_text()
                        value = value.strip()

                if key and value:
                    specs[key] = value
                    parser_logger.debug(f"Найдена характеристика: {key} = {value}")

            except Exception as e:
                parser_logger.warning(f"Ошибка при парсинге характеристики: {e}")
                continue

        # Извлекаем нужные характеристики
        # Сопоставляем ключи из HTML с нашими эталонными (регистронезависимо)
        for html_key, html_value in specs.items():
            lower_key = html_key.lower()

            if 'диагональ' in lower_key:
                product_data['diagonal'] = html_value
            elif ('разрешение hd' in lower_key) or ('разрешение' in lower_key and 'hd' in lower_key):
                product_data['resolution'] = html_value
            elif 'операционная система' in lower_key:
                product_data['os'] = html_value
            elif 'частота обновления' in lower_key:
                product_data['refresh_rate'] = html_value
            elif 'тип матрицы' in lower_key:
                product_data['display'] = html_value
            elif 'бренд' in lower_key:
                product_data['brand'] = html_value

        product_data.setdefault('diagonal', None)
        product_data.setdefault('resolution', None)
        product_data.setdefault('os', None)
        product_data.setdefault('refresh_rate', None)
        product_data.setdefault('display', None)
        product_data.setdefault('brand', None)

        # --- Извлечение цен ---
        try:
            # Ищем блок с ценами и кликаем для открытия деталей
            price_details_icon = context.page.locator('[data-auto="price-details-icon"]')

            if await price_details_icon.count() > 0:
                await price_details_icon.first.click()
                await asyncio.sleep(1)

                # Теперь извлекаем цены из открывшегося блока
                # Ищем блок с деталями цен (по классам из второго файла)
            await extract_prices_direct(context, product_data)

        except Exception as e:
            parser_logger.warning(f"Ошибка при извлечении цен: {e}")

        await context.push_data(product_data)
        parser_logger.info(f"Данные о товаре сохранены: {product_data['name']}")
    except Exception as e:
        print(e)
        parser_logger.error(f"Ошибка при парсинге страницы товара: {e}")


class YandexMarketParser:
    def __init__(self, proxy_list: list, parse_url: str, max_pass: int = -1, headless: bool = True):
        self.proxy_list = proxy_list
        self.parse_url = parse_url
        self.headless = headless
        global MAXPASS
        MAXPASS = max_pass

    async def parse(self):
        proxy_configuration = None
        parser_logger.info("Запуск парсера")
        if self.proxy_list:
            proxy_configuration = ProxyConfiguration(
                proxies=self.proxy_list
            )

        crawler = PlaywrightCrawler(
            max_requests_per_crawl=None,
            max_request_retries=0,
            max_crawl_depth=3,
            retry_on_blocked=True,
            proxy_configuration=proxy_configuration,
            headless=self.headless,
            request_handler=router,
            browser_type='chrome',
            # browser_type='chromium',
            browser_new_context_options={
                'viewport': {'width': 1920, 'height': 1080},
                'user_agent': '...',
                'locale': 'ru-RU',
                'timezone_id': 'Europe/Moscow',
                'java_script_enabled': True,
                'extra_http_headers': {
                    'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                },
                'screen': {'width': 1280, 'height': 800},
            },
            browser_launch_options={
                'args': [
                    '--disable-blink-features=AutomationControlled',
                    '--disable-dev-shm-usage',
                    '--no-sandbox',
                    '--disable-setuid-sandbox',
                    '--disable-web-security',
                    '--disable-features=IsolateOrigins,site-per-process',
                    '--disable-infobars',
                    '--disable-notifications',
                ]
            },
        )
        await crawler.run([self.parse_url])
        dataset = await crawler.get_data()
        self.data = dataset


if __name__ == '__main__':
    # python3 -m  parsings.yandex.parser
    parser = YandexMarketParser(
        proxy_list=None,
        # parse_url='https://market.yandex.ru/catalog--televizory/'
        # parse_url='https://market.yandex.ru/catalog--televizory/26960210/list?hid=90639&rs=eJwz4v7EyMHBIMGg0H-EFQASXQLR'
        parse_url='https://market.yandex.ru/search?text=телевизор',
        max_pass=40,
        headless=False
    )
    asyncio.run(parser.parse())
    print(parser.data.items)
    print(len(parser.data.items))
