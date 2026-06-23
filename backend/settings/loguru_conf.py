import logging
import json

from loguru import logger


class InterceptHandler(logging.Handler):
    def emit(self, record):
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        frame, depth = logging.currentframe(), 2
        while frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        logger.opt(
            depth=depth,
            exception=record.exc_info
        ).log(level, record.getMessage())


def custom_serializer(message):
    payload = {
        "timestamp": message["time"].isoformat(),
        "level": message["level"].name,
        "message": message["message"],
        "module": message["module"]
    }

    if message["extra"]:
        payload["context"] = message["extra"]

    message["extra"]["json_output"] = json.dumps(payload, ensure_ascii=False)


def setup_logger():
    logging.basicConfig(handlers=[InterceptHandler()], level=0, force=True)
    logger.remove()
    logger.configure(patcher=custom_serializer)
    logger.add(
        "logs/app_json.log",
        serialize=False,
        format="{extra[json_output]}",
        rotation="1 day",
        retention="7 days",
        level="INFO"
    )
