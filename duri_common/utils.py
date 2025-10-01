#!/usr/bin/env python3
"""
DuRi Common Utilities

공통으로 사용되는 유틸리티 함수들을 모아둔 모듈입니다.
"""

import json
import os
from datetime import datetime
from typing import Any, Dict, List, Optional

from .logger import get_logger

logger = get_logger("duri_common.utils")


def ensure_directory(path: str) -> bool:
    """
    디렉토리가 존재하지 않으면 생성

    Args:
        path (str): 디렉토리 경로

    Returns:
        bool: 성공 여부
    """
    try:
        os.makedirs(path, exist_ok=True)
        return True
    except Exception as e:
        logger.error(f"디렉토리 생성 실패: {path} - {e}")
        return False


def save_json(data: Dict[str, Any], filepath: str, ensure_ascii: bool = False) -> bool:
    """
    JSON 데이터를 파일에 저장

    Args:
        data (Dict): 저장할 데이터
        filepath (str): 파일 경로
        ensure_ascii (bool): ASCII 인코딩 사용 여부

    Returns:
        bool: 성공 여부
    """
    try:
        # 디렉토리 생성
        os.makedirs(os.path.dirname(filepath), exist_ok=True)

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=ensure_ascii)

        return True
    except Exception as e:
        logger.error(f"JSON 저장 실패: {filepath} - {e}")
        return False


def load_json(filepath: str) -> Optional[Dict[str, Any]]:
    """
    JSON 파일을 로드

    Args:
        filepath (str): 파일 경로

    Returns:
        Optional[Dict]: 로드된 데이터 또는 None
    """
    try:
        if not os.path.exists(filepath):
            return None

        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"JSON 로드 실패: {filepath} - {e}")
        return None


def get_timestamp() -> str:
    """
    현재 타임스탬프 반환

    Returns:
        str: ISO 형식 타임스탬프
    """
    return datetime.now().isoformat()


def format_duration(seconds: float) -> str:
    """
    초를 사람이 읽기 쉬운 형식으로 변환

    Args:
        seconds (float): 초

    Returns:
        str: 포맷된 시간 문자열
    """
    if seconds < 60:
        return f"{seconds:.2f}초"
    elif seconds < 3600:
        minutes = seconds / 60
        return f"{minutes:.1f}분"
    else:
        hours = seconds / 3600
        return f"{hours:.1f}시간"


def validate_emotion(emotion: str, valid_emotions: List[str]) -> bool:
    """
    감정 유효성 검사

    Args:
        emotion (str): 검사할 감정
        valid_emotions (List[str]): 유효한 감정 목록

    Returns:
        bool: 유효성 여부
    """
    return emotion.lower() in [e.lower() for e in valid_emotions]


def calculate_success_rate(successful: int, total: int) -> float:
    """
    성공률 계산

    Args:
        successful (int): 성공 횟수
        total (int): 전체 횟수

    Returns:
        float: 성공률 (0.0 ~ 1.0)
    """
    if total == 0:
        return 0.0
    return successful / total


def merge_dicts(dict1: Dict[str, Any], dict2: Dict[str, Any]) -> Dict[str, Any]:
    """
    두 딕셔너리를 병합 (dict2가 우선)

    Args:
        dict1 (Dict): 첫 번째 딕셔너리
        dict2 (Dict): 두 번째 딕셔너리

    Returns:
        Dict: 병합된 딕셔너리
    """
    result = dict1.copy()
    result.update(dict2)
    return result
