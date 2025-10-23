#!/usr/bin/env python3
"""
DuRi 안전 로깅 설정

로깅 충돌을 방지하고 기본 필드를 안전하게 처리합니다.
"""

import logging
import threading

# 로깅 예약 키 목록
RESERVED = {
    "name",
    "msg",
    "args",
    "levelname",
    "levelno",
    "pathname",
    "filename",
    "module",
    "exc_info",
    "exc_text",
    "stack_info",
    "lineno",
    "funcName",
    "created",
    "msecs",
    "relativeCreated",
    "thread",
    "threadName",
    "processName",
    "process",
}

# 중복 초기화 방지
_setup_done = False
_setup_lock = threading.Lock()


def sanitize_extra(extra: dict | None) -> dict:
    """예약 키 충돌을 방지하고 안전한 extra 딕셔너리를 반환합니다."""
    if not extra:
        return {}

    out = {}
    for k, v in extra.items():
        # module -> component 변환
        safe_key = "component" if k == "module" else k

        # 예약 키 충돌 방지
        if safe_key in RESERVED:
            safe_key = f"extra_{safe_key}"

        out[safe_key] = v

    return out


class DefaultFieldsFilter(logging.Filter):
    """기본 필드가 없을 때 안전한 기본값을 제공합니다."""

    def filter(self, record: logging.LogRecord) -> bool:
        if not hasattr(record, "component"):
            record.component = "_"
        return True


class SafeLogger(logging.Logger):
    """안전한 로깅을 제공하는 Logger 클래스."""

    def _log(
        self,
        level,
        msg,
        args,
        exc_info=None,
        extra=None,
        stack_info=False,
        stacklevel=1,
    ):
        """로깅 전에 extra를 안전하게 처리합니다."""
        extra = sanitize_extra(extra)
        super()._log(level, msg, args, exc_info, extra, stack_info, stacklevel)


def setup_logging(level=logging.INFO, force=False):
    """
    안전한 로깅 시스템을 설정합니다.

    Args:
        level: 로깅 레벨
        force: 기존 설정을 강제로 재설정할지 여부
    """
    global _setup_done

    with _setup_lock:
        if _setup_done and not force:
            return

        # SafeLogger를 기본 Logger 클래스로 설정
        logging.setLoggerClass(SafeLogger)

        # 기본 로깅 설정
        logging.basicConfig(
            level=level,
            format="%(asctime)s %(levelname)s %(name)s:%(lineno)d [%(component)s] - %(message)s",
            force=force,
        )

        # 루트 로거에 기본 필터 장착
        root = logging.getLogger()
        root.addFilter(DefaultFieldsFilter())

        # 모든 핸들러에 필터 장착
        for handler in root.handlers:
            handler.addFilter(DefaultFieldsFilter())

        _setup_done = True


def test_logging_safety():
    """로깅 안전성을 테스트합니다."""
    setup_logging()
    logger = logging.getLogger("test")

    # 1. extra 없는 로깅
    logger.info("no extra ok")

    # 2. module 키 사용
    logger.info("with module", extra={"module": "memory"})

    # 3. 예약 키 사용
    logger.info("with reserved", extra={"filename": "test.py", "process": 123})

    # 4. component 직접 사용
    logger.info("with component", extra={"component": "brain"})

    print("✅ 로깅 안전성 테스트 통과")
    return True


if __name__ == "__main__":
    test_logging_safety()
