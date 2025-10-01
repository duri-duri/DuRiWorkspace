#!/usr/bin/env python3
"""
DuRi 안전 로깅 설정

로깅 충돌을 방지하고 기본 필드를 안전하게 처리합니다.
"""

import logging
import os
import threading
from typing import Optional

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

# PII 마스킹 대상 키 (의료 도메인 주의)
SENSITIVE = {"patient_name", "phone", "email", "ssn", "id_number", "address"}

# 중복 초기화 방지
_setup_done = False
_setup_lock = threading.Lock()


def sanitize_extra(extra: Optional[dict]) -> dict:
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
    """기본 필드가 없을 때 안전한 기본값을 제공하고 PII를 마스킹합니다."""

    def filter(self, record: logging.LogRecord) -> bool:
        # 기본 필드 설정
        if not hasattr(record, "component"):
            setattr(record, "component", "_")
        if not hasattr(record, "request_id"):
            setattr(record, "request_id", "-")
        if not hasattr(record, "session_id"):
            setattr(record, "session_id", "-")
        if not hasattr(record, "learning_session_id"):
            setattr(record, "learning_session_id", "-")
        if not hasattr(record, "phase"):
            setattr(record, "phase", "-")

        # 컨텍스트 변수를 record에 주입
        try:
            from .context import get_context

            ctx = get_context()
            for k, v in ctx.items():
                if not hasattr(record, k):
                    setattr(record, k, v)
        except Exception:
            pass

        # PII 마스킹 (extra 필드)
        if hasattr(record, "extra_kwargs"):
            for k in list(record.extra_kwargs):
                if k in SENSITIVE:
                    record.extra_kwargs[k] = "[REDACTED]"

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


def setup_logging(level: int = logging.INFO, force: bool = False) -> None:
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

        # 기본 로깅 설정 (DuRi 특화 포맷)
        logging.basicConfig(
            level=level,
            format="%(asctime)s %(levelname)s %(name)s:%(lineno)d [%(component)s] "
            "(req=%(request_id)s sess=%(session_id)s learn=%(learning_session_id)s phase=%(phase)s) - %(message)s",
            force=force,
        )

        # 루트 로거에 기본 필터 장착
        root = logging.getLogger()
        filt = DefaultFieldsFilter()
        root.addFilter(filt)

        # 모든 핸들러에 필터 장착
        for handler in root.handlers:
            handler.addFilter(filt)

        _setup_done = True

        # 부트스트랩 완료 로그
        logger = logging.getLogger(__name__)
        logger.info("DuRi 로깅 시스템 초기화 완료", extra={"component": "core"})


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

    # 5. PII 마스킹 테스트
    logger.info(
        "with sensitive data",
        extra={"patient_name": "John Doe", "phone": "123-456-7890"},
    )

    print("✅ 로깅 안전성 테스트 통과")
    return True


if __name__ == "__main__":
    test_logging_safety()
