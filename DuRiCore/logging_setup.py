#!/usr/bin/env python3
"""
DuRi 로깅 설정 유틸
"""

import logging
import os
from logging.handlers import RotatingFileHandler

def ensure_duri_logger(path="./logs/duri-core.log"):
    """DuRi 로거 설정 및 보장"""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    logger = logging.getLogger("duri-core")
    logger.setLevel(logging.INFO)
    logger.propagate = False  # 상위로 전파 방지

    # 중복 추가 방지
    if not any(isinstance(h, RotatingFileHandler) and h.baseFilename.endswith("duri-core.log")
               for h in logger.handlers):
        handler = RotatingFileHandler(path, maxBytes=10*1024*1024, backupCount=5, encoding="utf-8")
        handler.setFormatter(logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s"))
        handler.flush = getattr(handler, "flush", lambda: None)
        logger.addHandler(handler)
    return logger

def flush_duri_logger():
    """DuRi 로거 강제 flush"""
    logger = logging.getLogger("duri-core")
    for h in logger.handlers:
        if hasattr(h, "flush"):
            h.flush()
