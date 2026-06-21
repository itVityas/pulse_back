class MyHttpException(Exception):
    def __init__(self, status_code: int, detail: str, title: str):
        self.title = title
        self.detail = detail
        self.status_code = status_code
