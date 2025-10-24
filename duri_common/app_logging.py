import logging
import os


def get_logger(name="duri"):
    lvl = os.getenv("DURI_LOG_LEVEL", "INFO").upper()
    logging.basicConfig(level=lvl, format="%(asctime)s %(levelname)s %(name)s - %(message)s")
    return logging.getLogger(name)
