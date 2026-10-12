import requests


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
