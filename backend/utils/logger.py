import logging
import sys
from logging.handlers import RotatingFileHandler


def setup_logger(name: str = "drax") -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    fmt = logging.Formatter(
        "[%(asctime)s] %(levelname)s %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setFormatter(fmt)
    logger.addHandler(stream_handler)

    file_handler = RotatingFileHandler(
        "app.log", maxBytes=10 * 1024 * 1024, backupCount=5
    )
    file_handler.setFormatter(fmt)
    logger.addHandler(file_handler)

    return logger


logger = setup_logger()
