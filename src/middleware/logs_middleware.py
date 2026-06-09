from time import time

from loguru import logger
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request


class LogMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time()

        client_host = request.client.host if request.client else "unknown"
        method = request.method
        url = str(request.url)

        response = await call_next(request)

        process_time = round((time() - start_time) * 1000, 2)
        status_code = response.status_code

        logger.bind(
            http_request={
                "client_ip": client_host,
                "method": method,
                "url": url,
            },
            http_response={
                "status_code": status_code,
                "duration_ms": process_time
            }
        ).info(f"Запрос {method} {request.url.path} завершен со статусом {status_code}")

        return response
