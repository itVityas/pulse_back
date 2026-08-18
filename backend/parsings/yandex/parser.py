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
    max_scrolls = 3  # количество прокруток
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
    await context.page.wait_for_load_state("networkidle")

    # Получаем данные о товаре
    product_data = {
        'url': context.request.url,
        'title': await context.page.title(),
        'price': await context.page.eval_on_selector('span[data-test="price"]', 'el => el.textContent'),
        'brand': await context.page.eval_on_selector('a[data-test="brand-link"]', 'el => el.textContent'),
        'rating': await context.page.eval_on_selector('span[data-test="rating"]', 'el => el.textContent'),
        'reviews_count': await context.page.eval_on_selector('a[data-test="reviews-link"]', 'el => el.textContent'),
    }

    # Сохраняем данные в результаты
    context.push_data(product_data)
    parser_logger.info(f"Данные о товаре сохранены: {product_data['title']}")


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
