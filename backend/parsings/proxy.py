import requests
import time

from seleniumbase import Driver
from bs4 import BeautifulSoup


def get_2ip_proxies_sb():
    url = "https://2ip.io/ru/proxy/"
    driver = Driver(uc=True, headless=True)

    try:
        driver.uc_open_with_reconnect(url, reconnect_time=5)
        time.sleep(5)

        page_source = driver.page_source
        soup = BeautifulSoup(page_source, 'html.parser')

        table = soup.find('table', {'id': 'proxy_list'}) or soup.find('table')

        if not table:
            print("Не удалось найти таблицу с прокси. Возможно, сработала защита Cloudflare.")
            return []

        proxies = []

        rows = table.find_all('tr')[1:]
        for row in rows:
            cols = row.find_all('td')
            if len(cols) >= 2:
                ip = cols[0].text.strip()

                proxies.append(ip)

        return proxies

    except Exception as e:
        print(f"Произошла ошибка при работе SeleniumBase: {e}")
        return []

    finally:
        driver.quit()


def check_proxy(proxy_url, timeout=5):
    """
    Проверяет работоспособность прокси-сервера.

    :param proxy_url: Строка вида 'http://user:pass@ip:port' или 'http://ip:port'
    :param timeout: Время ожидания ответа в секундах
    :return: True, если прокси работает, иначе False
    """
    try:
        response = requests.get(
            'https://httpbin.org/ip',
            proxies={'http': proxy_url, 'https': proxy_url},
            timeout=timeout
        )
        return response.status_code == 200
    except Exception as e:
        print(f"Proxy {proxy_url} is not working: {e}")
        return False


if __name__ == "__main__":
    t1 = time.time()
    print("Запуск SeleniumBase для обхода защиты...")
    proxy_list = get_2ip_proxies_sb()
    t2 = time.time()
    print('Время выполнения:', t2-t1)

    print(f"\nУспешно собрано прокси: {len(proxy_list)}\n")
    for item in proxy_list:
        print(f"Прокси: {item}")
