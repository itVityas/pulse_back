import asyncio

from crawlee.proxy_configuration import ProxyConfiguration
from crawlee.crawlers import PlaywrightCrawler, PlaywrightCrawlingContext
from crawlee.router import Router
from loguru import logger

from settings.loguru_conf import setup_logger


setup_logger('yandex')
parser_logger = logger.bind(log_name="yandex")

router = Router[PlaywrightCrawlingContext]()


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

        # Ищем скидку в процентах
        # Ищем текст с символом % рядом с ценой
        discount_elem = context.page.locator('span:has-text("%")').first
        if await discount_elem.count() > 0:
            discount_text = await discount_elem.inner_text()
            discount = ''.join(filter(str.isdigit, discount_text))
            if discount:
                product_data['discount'] = discount

        # Цену по карте ищем в тексте "Пэй" или "по карте"
        # Это может быть сложнее, но попробуем найти
        card_price_elem = context.page.locator('span:has-text("Пэй")').first
        if await card_price_elem.count() > 0:
            # Ищем родительский элемент с ценой
            parent = card_price_elem.locator('xpath=ancestor::div[1]')
            price_in_parent = parent.locator('span.ds-valueLine')
            if await price_in_parent.count() > 0:
                card_price_text = await price_in_parent.first.inner_text()
                card_price = ''.join(filter(str.isdigit, card_price_text))
                if card_price:
                    product_data['card_price'] = card_price

    except Exception as e:
        parser_logger.warning(f"Ошибка при прямом парсинге цен: {e}")


@router.default_handler
async def default_handler(context: PlaywrightCrawlingContext) -> None:
    """Обработчик главной страницы поиска со всеми телевизорами"""
    parser_logger.info(f"Главная страница загружена успешно. {context.request.url}")

    await asyncio.sleep(2)
    try:
        await context.page.wait_for_selector('._1fWhD', timeout=10000)
    except Exception as e:
        context.log.warning(f"Селектор '._1fWhD' не найден: {e}")
        parser_logger.warning("Селектор '._1fWhD' не найден, продолжаем без него")

    # Проверка на явную блокировку/капчу
    content_snapshot = await context.page.content()
    if "Капча" in content_snapshot or "SmartCaptcha" in content_snapshot or "captcha" in context.page.url:
        context.log.error("⚠️ Внимание: Яндекс выкатил Капчу. Требуется смена IP (прокси) или сервис разгадывания.")
        parser_logger.error("⚠️ Внимание: Яндекс выкатил Капчу. Требуется смена IP (прокси) или сервис разгадывания.")
        return

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
            context.log.info("✅ Окно авторизации закрыто")
            parser_logger.info("✅ Окно авторизации закрыто")
    except Exception:
        # Игнорируем, если окна нет
        # Если за 3 секунды окно не появилось, Playwright выбросит TimeoutError.
        # Мы его игнорируем и идем дальше парсить товары.
        context.log.info("Окно авторизации не появилось, продолжаем работу.")
        parser_logger.info("Окно авторизации не появилось, продолжаем работу.")

    scroll_attempts = 0
    max_scrolls = 1  # количество прокруток
    scroll_pause = 2  # Пауза между прокрутками
    while scroll_attempts < max_scrolls:
        await context.page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        await asyncio.sleep(scroll_pause)

        await context.enqueue_links(
            selector='a[data-auto="snippet-link"]',
            label='PRODUCT',
        )
        scroll_attempts += 1


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
                await asyncio.sleep(1)  # Ждём открытия блока с ценами

                # Теперь извлекаем цены из открывшегося блока
                # Ищем блок с деталями цен (по классам из второго файла)
                price_block = context.page.locator('div.ds-flex.ds-flex_col._3yRhS')

                if await price_block.count() > 0:
                    # Извлекаем цены
                    # 1. Цена со скидкой (текущая цена) - первая цена в блоке
                    current_price_elem = price_block.locator('span.ds-valueLine[data-auto="snippet-price-current"]')
                    if await current_price_elem.count() > 0:
                        current_price_text = await current_price_elem.inner_text()
                        # Очищаем от пробелов и символов
                        current_price = ''.join(filter(str.isdigit, current_price_text))
                        product_data['current_price'] = current_price

                    # 2. Цена по карте (вторая цена в блоке)
                    # Ищем цену с пометкой "Пэй" или "по карте"
                    card_price_elem = price_block.locator('span.ds-valueLine').nth(1)  # Вторая цена
                    if await card_price_elem.count() > 0:
                        card_price_text = await card_price_elem.inner_text()
                        card_price = ''.join(filter(str.isdigit, card_price_text))
                        if card_price and card_price != product_data.get('current_price', ''):
                            product_data['card_price'] = card_price

                    # 3. Обычная цена (без скидки) - ищем зачёркнутую цену
                    old_price_elem = price_block.locator('span.ds-text_decoration_line-through')
                    if await old_price_elem.count() > 0:
                        old_price_text = await old_price_elem.inner_text()
                        old_price = ''.join(filter(str.isdigit, old_price_text))
                        if old_price:
                            product_data['old_price'] = old_price

                    # 4. Процент скидки
                    discount_elem = price_block.locator('span.ds-text_group_core:has-text("%")')
                    if await discount_elem.count() > 0:
                        discount_text = await discount_elem.inner_text()
                        discount = ''.join(filter(str.isdigit, discount_text))
                        if discount:
                            product_data['discount'] = discount

                    # Закрываем блок с ценами (опционально)
                    # await price_details_icon.first.click()
                else:
                    parser_logger.warning("Блок с деталями цен не найден")
                    # Пробуем альтернативный способ - ищем цены на странице напрямую
                    await extract_prices_direct(context, product_data)
            else:
                parser_logger.warning("Значок деталей цены не найден, пробуем прямой парсинг")
                await extract_prices_direct(context, product_data)

        except Exception as e:
            parser_logger.warning(f"Ошибка при извлечении цен: {e}")
            await extract_prices_direct(context, product_data)

        print(product_data)
        await context.push_data(product_data)
        parser_logger.info(f"Данные о товаре сохранены: {product_data['name']}")
    except Exception as e:
        print(e)
        parser_logger.error(f"Ошибка при парсинге страницы товара: {e}")


class YandexMarketParser:
    def __init__(self, proxy_list: list, parse_url: str):
        self.proxy_list = proxy_list
        self.parse_url = parse_url

    async def parse(self):
        proxy_configuration = None
        parser_logger.info("Запуск парсера")
        if self.proxy_list:
            proxy_configuration = ProxyConfiguration(
                proxies=self.proxy_list
            )

        crawler = PlaywrightCrawler(
            max_requests_per_crawl=2,
            max_request_retries=0,
            proxy_configuration=proxy_configuration,
            headless=True,
            request_handler=router,
        )
        await crawler.run([self.parse_url])


if __name__ == '__main__':
    # python3 -m  parsings.yandex.parser
    parser = YandexMarketParser(
        proxy_list=None,
        # parse_url='https://market.yandex.ru/catalog--televizory/'
        # parse_url='https://market.yandex.ru/catalog--televizory/26960210/list?hid=90639&rs=eJwz4v7EyMHBIMGg0H-EFQASXQLR'
        parse_url='https://market.yandex.ru/search?text=телевизор'
    )
    asyncio.run(parser.parse())
