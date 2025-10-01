#!/usr/bin/env python3
"""
DuRi 판단 추적 시스템 - 판단과 판단 이유를 기록하여 학습 및 자기반성에 활용
"""

import json
import logging
import os
from datetime import datetime
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


def record_judgment_trace(
    context: Dict[str, Any], judgment: Dict[str, Any], reason: Optional[str] = None
) -> None:
    """
    DuRi의 판단 흐름과 그 이유를 기록하여 학습 및 자기반성에 활용

    Args:
        context: 판단 대상 상황
        judgment: 판단 결과
        reason: 판단 이유 (None일 경우 judgment에서 추출 시도)
    """
    try:
        # 파일 경로 설정
        log_path = "DuRiCore/memory/judgment_traces.jsonl"
        os.makedirs(os.path.dirname(log_path), exist_ok=True)

        # reason이 None인 경우 judgment에서 추출 시도
        if reason is None:
            if isinstance(judgment, dict):
                reason = judgment.get("reasoning", judgment.get("reason", ""))
            else:
                reason = str(judgment)

        # 기록 데이터 구성
        record = {
            "timestamp": datetime.now().isoformat(),
            "context": context,
            "judgment": judgment,
            "reason": reason or "",
            "applied_strategy": None,  # 향후 판단 전략 적용 시 사용
            "strategy_source": None,  # 향후 판단 전략 출처 시 사용
        }

        # JSONL 형식으로 저장
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")

        logger.info(f"판단 추적 기록 완료: {log_path}")

    except Exception as e:
        logger.error(f"판단 추적 기록 실패: {e}")


def get_reasoning_trace(context: Dict[str, Any]) -> str:
    """
    판단 이유 추출 함수 (기본 구현)

    Args:
        context: 판단 대상 상황

    Returns:
        str: 판단 이유 (기본값: 빈 문자열)
    """
    try:
        # 기존 reasoning 추출 로직이 있다면 사용
        if hasattr(context, "reasoning"):
            return context.reasoning
        elif isinstance(context, dict) and "reasoning" in context:
            return context["reasoning"]
        elif isinstance(context, dict) and "reason" in context:
            return context["reason"]
        else:
            return ""  # 기본값
    except Exception as e:
        logger.warning(f"판단 이유 추출 실패: {e}")
        return ""  # 예외 시 기본값
