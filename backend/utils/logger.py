import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path


BACKEND_DIR = Path(__file__).resolve().parent.parent
LOG_FILE = BACKEND_DIR / "app.log"


def setup_logger(name: str = "drax") -> logging.Logger:
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger

    logger.setLevel(logging.INFO)

    fmt = logging.Formatter(
        "[%(asctime)s] %(levelname)s %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setFormatter(fmt)
    logger.addHandler(stream_handler)

    try:
        file_handler = RotatingFileHandler(
            LOG_FILE,
            maxBytes=10 * 1024 * 1024,
            backupCount=5,
        )
        file_handler.setFormatter(fmt)
        logger.addHandler(file_handler)
    except OSError:
        logger.warning("File logging disabled; could not write to %s", LOG_FILE)

    return logger


logger = setup_logger()
