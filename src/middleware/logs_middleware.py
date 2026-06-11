from time import time
import json

from loguru import logger
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request


class LogMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time()

        client_host = request.client.host if request.client else "unknown"
        method = request.method
        url = str(request.url)
        body_bytes = await request.body()
        try:
            body_str = body_bytes.decode("utf-8") if body_bytes else ""
            body_str = json.loads(body_str)
        except Exception:
            pass

        async def receive():
            return {"type": "http.request", "body": body_bytes, "more_body": False}
        request._receive = receive

        response = await call_next(request)

        process_time = round((time() - start_time) * 1000, 2)
        status_code = response.status_code

        logger.bind(
            http_request={
                "client_ip": client_host,
                "method": method,
                "url": url,
                "body": body_str,
            },
            http_response={
                "status_code": status_code,
                "duration_ms": process_time
            }
        ).info(f"Запрос {method} {request.url.path} завершен со статусом {status_code}")

        return response
