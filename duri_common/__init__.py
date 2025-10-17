from .config import load_env
# 안전 가드: app_logging 모듈이 없을 경우 대체
try:
    from .app_logging import get_logger
except Exception:  # ModuleNotFoundError 등
    import logging
    def get_logger(name: str = "duri"):
        logger = logging.getLogger(name)
        if not logger.handlers:
            h = logging.StreamHandler()
            fmt = logging.Formatter("[%(levelname)s] %(asctime)s %(name)s: %(message)s")
            h.setFormatter(fmt)
            logger.addHandler(h)
        logger.setLevel(logging.INFO)
        return logger
from .metrics import prom_counter, prom_gauge
from .settings import DuRiSettings, settings, get_settings

__all__ = [
    "get_logger",
    "load_env",
    "prom_counter",
    "prom_gauge",
    "settings",
    "DuRiSettings",
    "get_settings",
]
