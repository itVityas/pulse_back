import asyncio

from crawlee.proxy_configuration import ProxyConfiguration
from crawlee.crawlers import PlaywrightCrawler, PlaywrightCrawlingContext
from crawlee.router import Router
from playwright.async_api import TimeoutError as PlaywrightTimeoutError


router = Router[PlaywrightCrawlingContext]()


@router.default_handler
async def default_handler(context: PlaywrightCrawlingContext) -> None:
    """Обработчик главной страницы поиска."""
    context.log.info(f'Загружаем Яндекс.Маркет: {context.request.url}')
    page = context.page

    try:
        await page.wait_for_load_state('networkidle', timeout=10000)
        await asyncio.sleep(2)
    except Exception:
        context.log.warning("Сеть не утихла, продолжаем работу с текущим состоянием.")

    # Проверка на явную блокировку/капчу
    content_snapshot = await page.content()
    if "Капча" in content_snapshot or "SmartCaptcha" in content_snapshot or "captcha" in page.url:
        context.log.error("⚠️ Внимание: Яндекс выкатил Капчу. Требуется смена IP (прокси) или сервис разгадывания.")
        return

    # Закрываем окно авторизации, если появилось
    try:
        close_button = page.locator('button[aria-label="Закрыть"]').or_(
            page.locator('div[data-zone-name="loginPopup"] button')
        ).or_(
            page.locator('button:has-text("Закрыть")')
        )

        if await close_button.count() > 0:
            await close_button.first.click(timeout=2000)
            await asyncio.sleep(1)
            context.log.info("✅ Окно авторизации закрыто")
    except:
        # Игнорируем, если окна нет
        # Если за 3 секунды окно не появилось, Playwright выбросит TimeoutError.
        # Мы его игнорируем и идем дальше парсить товары.
        context.log.info("Окно авторизации не появилось, продолжаем работу.")

    scroll_attempts = 0
    max_scrolls = 3  # Ограничиваем, чтобы не уйти в бесконечность
    previous_item_count = 0
    scroll_pause = 2  # Пауза между прокрутками
    tv_data = list()
    while scroll_attempts < max_scrolls:
        await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        await asyncio.sleep(scroll_pause)

        # Считаем текущие карточки товаров
        cards = page.locator('article[data-auto="snippet"]').or_(
            page.locator('div[data-auto="snippet"]')
        ).or_(
            page.locator('article')
        )

        link_elem = cards.locator('a[data-auto="snippet-link"]')
        link = await link_elem.get_attribute('href') if (link_elem and await link_elem.first.get_attribute('href')) else None

        title_elem = cards.locator('h3') or cards.locator('a[data-auto="snippet-link"]:not([aria-hidden="true"])')
        title = title_elem.get_text(strip=True) if title_elem else None
        print('title:', title, title_elem)

        if not title and link:
            # Вытаскиваем фрагмент "televizor-haier-32..." и делаем его читаемым
            import urllib.parse
            part = link.split('/card/')[1].split('/')[0]
            title = urllib.parse.unquote(part).replace('-', ' ').capitalize()

        if title or link:
            tv_data.append({
                'title': title,
                'url': link
            })
        scroll_attempts += 1
    print('tv_data', tv_data)
    context.push_data(tv_data)


class YandexMarketParser:
    def __init__(self, proxy_list: list, parse_url: str):
        self.proxy_list = proxy_list
        self.parse_url = parse_url

    async def parse(self):
        proxy_configuration = None
        if self.proxy_list:
            proxy_configuration = ProxyConfiguration(
                proxies=self.proxy_list
            )

        crawler = PlaywrightCrawler(
            max_requests_per_crawl=1,
            proxy_configuration=proxy_configuration,
            headless=True,
            request_handler=router,
        )
        await crawler.run([self.parse_url])
        data = await crawler.get_data()
        print('data:', data)


if __name__ == '__main__':
    parser = YandexMarketParser(
        proxy_list=None,
        # parse_url='https://market.yandex.ru/catalog--televizory/'
        # parse_url='https://market.yandex.ru/catalog--televizory/26960210/list?hid=90639&rs=eJwz4v7EyMHBIMGg0H-EFQASXQLR'
        parse_url='https://market.yandex.ru/search?text=телевизор'
    )
    asyncio.run(parser.parse())
