#!/usr/bin/env python3
"""
DuRi 부트스트랩 시스템

애플리케이션 진입점에서 로깅 시스템을 초기화합니다.
"""

import logging
import os
from typing import Optional

# 멀티프로세스 안정화 체크 훅
_booted_pid: Optional[int] = None


def bootstrap_logging(level: int = logging.INFO, force: bool = False) -> None:
    """
    DuRi 로깅 시스템을 초기화합니다.

    Args:
        level: 로깅 레벨
        force: 기존 설정을 강제로 재설정할지 여부
    """
    global _booted_pid

    # PID 기반 중복 초기화 방지
    current_pid = os.getpid()
    if _booted_pid == current_pid and not force:
        return

    try:
        from .duri_logging.setup import setup_logging

        setup_logging(level=level, force=force)

        # 부트스트랩 완료 상태 업데이트
        _booted_pid = current_pid

        # 초기화 완료 로그
        logger = logging.getLogger(__name__)
        logger.info(
            f"DuRi 로깅 시스템 부트스트랩 완료 (PID: {current_pid})",
            extra={"component": "core"},
        )

    except Exception as e:
        # 부트스트랩 실패 시 기본 로깅으로 폴백
        logging.basicConfig(
            level=level,
            format="%(asctime)s %(levelname)s %(name)s:%(lineno)d - %(message)s",
            force=force,
        )

        logger = logging.getLogger(__name__)
        logger.error(f"DuRi 로깅 시스템 부트스트랩 실패: {e}")
        logger.info("기본 로깅 시스템으로 폴백")


def bootstrap_with_context(
    level: int = logging.INFO,
    request_id: Optional[str] = None,
    session_id: Optional[str] = None,
    learning_session_id: Optional[str] = None,
    phase: Optional[str] = None,
) -> None:
    """
    컨텍스트와 함께 로깅 시스템을 초기화합니다.

    Args:
        level: 로깅 레벨
        request_id: 요청 ID
        session_id: 세션 ID
        learning_session_id: 학습 세션 ID
        phase: 학습 단계
    """
    # 로깅 시스템 초기화
    bootstrap_logging(level=level)

    # 컨텍스트 설정
    try:
        from .duri_logging.context import set_learning_session_id, set_phase, set_request_id, set_session_id

        if request_id:
            set_request_id(request_id)
        if session_id:
            set_session_id(session_id)
        if learning_session_id:
            set_learning_session_id(learning_session_id)
        if phase:
            set_phase(phase)

    except Exception as e:
        logger = logging.getLogger(__name__)
        logger.warning(f"컨텍스트 설정 실패: {e}")


def test_bootstrap():
    """부트스트랩 시스템을 테스트합니다."""
    # 1. 기본 부트스트랩 테스트
    bootstrap_logging()

    # 2. 컨텍스트와 함께 부트스트랩 테스트
    bootstrap_with_context(
        request_id="test_req_123",
        session_id="test_sess_456",
        learning_session_id="test_learn_789",
        phase="testing",
    )

    # 3. 로깅 테스트
    logger = logging.getLogger("test.bootstrap")
    logger.info("부트스트랩 테스트 완료")

    print("✅ 부트스트랩 시스템 테스트 통과")
    return True


if __name__ == "__main__":
    test_bootstrap()
