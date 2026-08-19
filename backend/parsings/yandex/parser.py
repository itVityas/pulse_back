import asyncio

from crawlee.proxy_configuration import ProxyConfiguration
from crawlee.crawlers import PlaywrightCrawler, PlaywrightCrawlingContext
from crawlee.router import Router
from loguru import logger

from settings.loguru_conf import setup_logger


setup_logger('yandex')
parser_logger = logger.bind(log_name="yandex")

router = Router[PlaywrightCrawlingContext]()


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

        spec_labels = await context.page.locator('label.ds-flex:has(span)').all()
        specs = {}

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
