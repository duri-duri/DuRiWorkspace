#!/usr/bin/env python3
"""
Business Logic for DuRi Emotion Processing System
"""

import requests
from duri_core.core.logging import append_receive_json_log, write_emotion_log
from duri_core.core.decision import create_decision, create_evolution_payload
from duri_core.core.stats import update_action_stats
from duri_common.logger import get_logger
from duri_common.config.config import Config
from duri_common.config.emotion_labels import ALL_EMOTIONS, is_valid_emotion

logger = get_logger("duri_core.logic")
logic_config = Config()

def process_emotion(emotion, data, timestamp, config):
    """
    감정 데이터 처리 메인 로직
    
    Args:
        emotion (str): 감정 이름
        data (dict): 원본 데이터
        timestamp (str): 타임스탬프
        config (dict): 앱 설정
    
    Returns:
        dict: 처리 결과
    """
    
    # 1️⃣ 수신 로그 저장
    write_emotion_log(config['LOG_FILE'], timestamp, data)
    append_receive_json_log({"timestamp": timestamp, "data": data}, config['RECEIVE_JSON_LOG'])

    # 2️⃣ 조건 기반 decision 생성 (액션 통계 경로 포함)
    stats_path = config.get('ACTION_STATS_PATH')
    decision = create_decision(emotion, config['EVOLUTION_LOG_PATH'], stats_path)

    # 3️⃣ (선택) brain 전달 – 지금은 생략 가능
    # try:
    #     brain_response = requests.post(config['BRAIN_URL'], json=data, timeout=3)
    #     _ = brain_response.json()
    # except:
    #     pass

    # 4️⃣ evolution 기록
    evolution_payload = create_evolution_payload(emotion, decision)
    try:
        timeout = logic_config.get_request_timeout()
        requests.post(config['EVOLUTION_URL'], json=evolution_payload, timeout=timeout)
    except:
        pass

    # 5️⃣ 액션 통계 업데이트 (선택적)
    if stats_path:
        try:
            # 기본적으로 성공으로 가정 (실제로는 결과를 받아와야 함)
            result = "success"
            update_action_stats(emotion, decision["action"], result, stats_path)
        except Exception as e:
            logger.error(f"액션 통계 업데이트 실패: {e}")

    # 6️⃣ 응답 반환
    return {
        "status": "completed",
        "timestamp": timestamp,
        "decision": decision
    }

def validate_emotion_data(data):
    """
    감정 데이터 유효성 검사
    
    Args:
        data (dict): 검사할 데이터
    
    Returns:
        tuple: (is_valid, error_message)
    """
    if not isinstance(data, dict):
        return False, "데이터는 딕셔너리 형태여야 합니다"
    
    if "emotion" not in data:
        return False, "emotion 필드가 필요합니다"
    
    emotion = data.get("emotion", "").strip()
    if not emotion:
        return False, "emotion 값이 비어있습니다"
    
    # 감정 유효성 검사 - ALL_EMOTIONS에 포함되어 있는지 확인
    if emotion.lower() not in [e.lower() for e in ALL_EMOTIONS]:
        return False, f"Invalid emotion: {emotion}"
    
    return True, None

def format_response(status, data=None, error=None):
    """
    응답 형식화
    
    Args:
        status (str): 상태
        data (dict, optional): 데이터
        error (str, optional): 오류 메시지
    
    Returns:
        dict: 형식화된 응답
    """
    response = {"status": status}
    
    if data:
        response.update(data)
    
    if error:
        response["error"] = error
    
    return response 