#!/usr/bin/env python3
"""
Logging utilities for DuRi emotion processing system
"""

import os
import json
from datetime import datetime
from duri_common.logger import get_logger

logger = get_logger("duri_core.logging")


def get_last_result_for_emotion(emotion, evolution_log_path):
    """
    특정 감정에 대한 마지막 결과를 조회
    """
    try:
        with open(evolution_log_path, "r") as f:
            logs = json.load(f)
        for entry in reversed(logs):
            if entry.get("experience", {}).get("emotion") == emotion:
                return entry.get("experience", {}).get("result")
    except Exception as e:
        logger.warning(f"evolution_log 읽기 실패: {e}")
    return None


def append_receive_json_log(entry, receive_json_log_path):
    """
    감정 수신 로그를 JSON 파일에 추가
    """
    logs = []
    if os.path.exists(receive_json_log_path):
        with open(receive_json_log_path, "r") as f:
            try:
                logs = json.load(f)
            except:
                logs = []
    logs.append(entry)
    with open(receive_json_log_path, "w") as f:
        json.dump(logs[-500:], f, indent=2, ensure_ascii=False)


def write_emotion_log(log_file, timestamp, data):
    """
    감정 데이터를 로그 파일에 기록
    형식: [2025-06-27 07:29:17] [RECEIVED] emotion=angry
    """
    try:
        # ISO 형식의 timestamp를 읽기 쉬운 형식으로 변환
        dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
        formatted_time = dt.strftime('%Y-%m-%d %H:%M:%S')
        
        # 감정 추출
        emotion = data.get("emotion", "unknown")
        
        # 일관된 로그 형식으로 기록
        log_message = f"[{formatted_time}] [RECEIVED] emotion={emotion}"
        
        with open(log_file, "a") as f:
            f.write(log_message + "\n")
            
    except Exception as e:
        logger.error(f"로그 파일 기록 실패: {e}") 