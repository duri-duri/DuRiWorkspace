#!/usr/bin/env python3
"""
API Routes for DuRi Emotion Processing System
"""

import json
import os
from flask import Blueprint, request, jsonify, current_app
from datetime import datetime
from typing import Dict, Any
from duri_core.app.logic import process_emotion, validate_emotion_data
from duri_common.logger import get_logger
from duri_core.core.database import DatabaseManager
from duri_core.core.loop_orchestrator import LoopOrchestrator
from duri_core.core.decision_processor import CoreService
from duri_common.config.config import Config

# Blueprint 생성
bp = Blueprint('api', __name__)
logger = get_logger("duri_core.api")
config = Config()

# 데이터베이스 매니저 초기화
db_manager = DatabaseManager()

# 루프 오케스트레이터 초기화
loop_orchestrator = LoopOrchestrator()
core_service = CoreService()

# 감정 로깅 설정
EMOTION_LOG_DIR = "logs"
os.makedirs(EMOTION_LOG_DIR, exist_ok=True)

def save_request_log(request_data: dict, timestamp: str) -> str:
    """
    요청 내용을 로그 파일에 저장
    
    Args:
        request_data (dict): 요청 데이터
        timestamp (str): 타임스탬프
    
    Returns:
        str: 저장된 로그 파일 경로
    """
    try:
        log_dir = config.get_log_dir()
        os.makedirs(log_dir, exist_ok=True)
        
        # 날짜별 파일명 생성 (YYYY-MM-DD 형식)
        date_str = datetime.now().strftime("%Y-%m-%d")
        request_log_file = os.path.join(log_dir, f"{date_str}_emotion_requests.json")
        
        # 로그 엔트리 생성
        log_entry = {
            "timestamp": timestamp,
            "request_id": f"req_{timestamp.replace(':', '-').replace('.', '-')}",
            "method": "POST",
            "endpoint": "/emotion",
            "request_data": request_data,
            "client_ip": request.remote_addr,
            "user_agent": request.headers.get('User-Agent', 'Unknown')
        }
        
        # 로그 파일에 추가 (JSON Lines 형식)
        with open(request_log_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(log_entry, ensure_ascii=False) + '\n')
        
        logger.info(f"요청 로그 저장: {request_log_file}")
        return request_log_file
        
    except Exception as e:
        logger.error(f"요청 로그 저장 실패: {e}")
        return ""

def save_response_log(response_data: dict, request_id: str, timestamp: str) -> str:
    """
    응답 결과를 로그 파일에 저장
    
    Args:
        response_data (dict): 응답 데이터
        request_id (str): 요청 ID
        timestamp (str): 타임스탬프
    
    Returns:
        str: 저장된 로그 파일 경로
    """
    try:
        log_dir = config.get_log_dir()
        os.makedirs(log_dir, exist_ok=True)
        
        # 날짜별 파일명 생성 (YYYY-MM-DD 형식)
        date_str = datetime.now().strftime("%Y-%m-%d")
        response_log_file = os.path.join(log_dir, f"{date_str}_emotion_responses.json")
        
        # 로그 엔트리 생성
        log_entry = {
            "timestamp": timestamp,
            "request_id": request_id,
            "response_data": response_data,
            "processing_time": datetime.now().isoformat()
        }
        
        # 로그 파일에 추가 (JSON Lines 형식)
        with open(response_log_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(log_entry, ensure_ascii=False) + '\n')
        
        logger.info(f"응답 로그 저장: {response_log_file}")
        return response_log_file
        
    except Exception as e:
        logger.error(f"응답 로그 저장 실패: {e}")
        return ""

@bp.route("/emotion", methods=["POST"])
def receive_emotion():
    """
    감정 데이터 수신 엔드포인트
    """
    start_time = datetime.now()
    request_id = None
    
    try:
        data = request.get_json(force=True)
        timestamp = datetime.now().isoformat()
        request_id = f"req_{timestamp.replace(':', '-').replace('.', '-')}"
        
        # 요청 로그 저장 (파일)
        request_log_path = save_request_log(data, timestamp)
        
        # 요청 데이터베이스 저장
        emotion = data.get("emotion", "").lower()
        db_manager.log_emotion_request(emotion, data.get("intensity", 0.5), data)
        
        logger.info(f"감정 데이터 수신 시작: {request_id}")
        logger.debug(f"요청 데이터: {json.dumps(data, ensure_ascii=False)}")
        
        # 감정 데이터 유효성 검사
        is_valid, error_message = validate_emotion_data(data)
        if not is_valid:
            error_response = {
                "status": "error",
                "error": error_message,
                "request_id": request_id
            }
            
            # 에러 응답 로그 저장 (파일)
            save_response_log(error_response, request_id, timestamp)
            
            # 에러 응답 데이터베이스 저장
            db_manager.log_emotion_response(error_response)
            
            logger.warning(f"감정 데이터 유효성 검사 실패: {error_message}")
            return jsonify(error_response), 400
        
        logger.info(f"감정 처리 시작: {emotion}")

        # 비즈니스 로직 처리
        result = process_emotion(
            emotion=emotion,
            data=data,
            timestamp=timestamp,
            config=current_app.config
        )
        
        # 응답에 요청 ID 추가
        result["request_id"] = request_id
        result["processing_time"] = (datetime.now() - start_time).total_seconds()
        
        # 응답 로그 저장 (파일)
        response_log_path = save_response_log(result, request_id, timestamp)
        
        # 성공 응답 데이터베이스 저장
        db_manager.log_emotion_response(result)
        
        logger.info(f"감정 처리 완료: {emotion} (처리시간: {result['processing_time']:.3f}s)")
        logger.debug(f"응답 데이터: {json.dumps(result, ensure_ascii=False)}")
        
        return jsonify(result)

    except Exception as e:
        error_timestamp = datetime.now().isoformat()
        error_response = {
            "status": "error",
            "error": str(e),
            "request_id": request_id or f"req_{error_timestamp.replace(':', '-').replace('.', '-')}",
            "processing_time": (datetime.now() - start_time).total_seconds()
        }
        
        # 에러 응답 로그 저장
        if request_id:
            save_response_log(error_response, request_id, error_timestamp)
            db_manager.log_emotion_response(error_response)
        
        logger.error(f"감정 처리 중 오류 발생: {e}")
        return jsonify(error_response), 500

@bp.route("/health", methods=["GET"])
def health_check():
    """헬스 체크 엔드포인트"""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "duri-core"
    })

@bp.route("/", methods=["GET"])
def index():
    """루트 엔드포인트"""
    return jsonify({
        "service": "DuRi Core API",
        "version": "1.0.0",
        "endpoints": {
            "health": "/health",
            "emotion": "/emotion",
            "emotion_vector": "/emotion/vector",
            "automated_learning": "/automated-learning/process",
            "adaptive_learning": "/adaptive-learning/process",
            "loop_status": "/loop/status/<session_id>",
            "loop_process": "/loop/process",
            "loop_complete": "/loop/complete/<session_id>",
            "loop_sessions": "/loop/sessions",
            "patterns": "/patterns"
        },
        "timestamp": datetime.now().isoformat()
    })

@bp.route("/automated-learning/process", methods=["POST"])
def process_automated_learning():
    """
    자동화 학습 데이터 수신 및 실제 분석 처리
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        logger.info(f"📥 자동화 학습 입력: {data}")
        
        # 실제 학습 분석 수행
        conversation = data.get("conversation", "")
        user = data.get("user", "unknown")
        timestamp = data.get("timestamp", datetime.now().isoformat())
        
        # 간단한 학습 분석 (실제로는 더 정교한 분석 필요)
        word_count = len(conversation.split())
        learning_value = min(word_count / 50, 1.0)  # 단어 수 기반 학습 가치
        
        # Brain 노드 호출 (실제 구현)
        try:
            import httpx
            brain_response = httpx.post(
                "http://localhost:8081/brain/judge",
                json={"conversation": conversation, "user": user},
                timeout=5.0
            )
            brain_result = brain_response.json() if brain_response.status_code == 200 else {}
        except Exception as e:
            logger.warning(f"Brain 노드 호출 실패: {e}")
            brain_result = {}
        
        # 학습 결과 생성
        learning_result = {
            "status": "success",
            "message": "자동화 학습 분석 완료",
            "data": {
                "package_id": f"auto_learn_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "summary": f"대화 분석 완료 - {word_count}개 단어, 학습 가치: {learning_value:.3f}",
                "learning_value": learning_value,
                "brain_analysis": brain_result,
                "conversation_length": len(conversation),
                "word_count": word_count,
                "user": user
            },
            "timestamp": datetime.now().isoformat()
        }
        
        logger.info(f"📊 학습 분석 결과: {learning_result['data']['summary']}")
        return jsonify(learning_result)
        
    except Exception as e:
        logger.error(f"❌ 자동화 학습 처리 오류: {e}")
        return jsonify({"error": str(e)}), 500

@bp.route("/adaptive-learning/process", methods=["POST"])
def process_adaptive_learning():
    """
    적응적 학습 데이터 수신 및 처리 (Cursor Extension용)
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        logger.info(f"📥 적응적 학습 입력: {data}")
        
        # TODO: Brain 노드와 Evolution 노드 호출 로직 구현
        # 현재는 기본 응답만 반환
        
        return jsonify({
            "status": "success",
            "message": "적응적 학습 처리 완료",
            "data": {
                "selected_format": "detailed",
                "learning_result": "성공적으로 학습됨",
                "efficiency_metrics": {
                    "response_accuracy": 0.9,
                    "application_power": 0.8,
                    "reproducibility": 0.7,
                    "learning_speed": 0.85,
                    "overall_score": 0.81
                },
                "exploration_rate": 0.2,
                "optimal_format": "detailed",
                "reason": "상세한 설명이 학습에 효과적"
            },
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"❌ 적응적 학습 처리 오류: {e}")
        return jsonify({"error": str(e)}), 500

@bp.route('/loop/status/<session_id>', methods=['GET'])
def get_loop_status(session_id: str):
    """
    루프 상태 조회
    
    Args:
        session_id (str): 세션 ID
    """
    try:
        status = loop_orchestrator.get_loop_status(session_id)
        
        if status:
            return jsonify(status)
        else:
            return jsonify({"error": "Session not found"}), 404
            
    except Exception as e:
        logger.error(f"루프 상태 조회 실패: {e}")
        return jsonify({"error": str(e)}), 500

@bp.route('/loop/process', methods=['POST'])
def process_loop():
    """
    루프 처리 (Core, Brain, Evolution 단계별 처리)
    
    Request Body:
    {
        "session_id": "uuid",
        "stage": "core|brain|evolution"
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        session_id = data.get('session_id', '')
        stage = data.get('stage', '')
        
        if not session_id or not stage:
            return jsonify({"error": "session_id and stage are required"}), 400
        
        if stage == 'core':
            processed = core_service.process_decisions()
            return jsonify({
                "stage": "core",
                "processed": processed,
                "timestamp": datetime.now().isoformat()
            })
        
        elif stage == 'brain':
            from brain.action_processor import brain_service
            processed = brain_service.process_actions()
            return jsonify({
                "stage": "brain",
                "processed": processed,
                "timestamp": datetime.now().isoformat()
            })
        
        elif stage == 'evolution':
            from evolution.learning_processor import evolution_service
            processed = evolution_service.process_learning()
            return jsonify({
                "stage": "evolution",
                "processed": processed,
                "timestamp": datetime.now().isoformat()
            })
        
        else:
            return jsonify({"error": "Invalid stage"}), 400
            
    except Exception as e:
        logger.error(f"루프 처리 실패: {e}")
        return jsonify({"error": str(e)}), 500

@bp.route('/loop/complete/<session_id>', methods=['POST'])
def complete_loop(session_id: str):
    """
    루프 완료 처리
    
    Args:
        session_id (str): 세션 ID
    """
    try:
        success = loop_orchestrator.complete_loop(session_id)
        
        if success:
            return jsonify({
                "session_id": session_id,
                "status": "completed",
                "timestamp": datetime.now().isoformat()
            })
        else:
            return jsonify({"error": "Failed to complete loop"}), 500
            
    except Exception as e:
        logger.error(f"루프 완료 처리 실패: {e}")
        return jsonify({"error": str(e)}), 500

@bp.route('/loop/sessions', methods=['GET'])
def get_recent_sessions():
    """
    최근 세션 목록 조회
    
    Query Parameters:
        limit (int): 조회할 최대 개수 (기본값: 10)
    """
    try:
        limit = request.args.get('limit', 10, type=int)
        sessions = loop_orchestrator.get_recent_sessions(limit)
        
        return jsonify({
            "sessions": sessions,
            "count": len(sessions),
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"세션 목록 조회 실패: {e}")
        return jsonify({"error": str(e)}), 500

@bp.route('/patterns', methods=['GET'])
def get_patterns():
    """
    학습된 패턴 조회
    
    Query Parameters:
        emotion (str): 특정 감정 필터링
        action (str): 특정 행동 필터링
    """
    try:
        emotion = request.args.get('emotion', '')
        action = request.args.get('action', '')
        
        from evolution.learning_processor import evolution_service
        
        if emotion and action:
            pattern = evolution_service.get_pattern(emotion, action)
            patterns = [pattern] if pattern else []
        else:
            patterns = evolution_service.get_all_patterns()
        
        return jsonify({
            "patterns": patterns,
            "count": len(patterns),
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"패턴 조회 실패: {e}")
        return jsonify({"error": str(e)}), 500

@bp.route('/emotion/vector', methods=['POST'])
def receive_emotion_vector():
    """
    감정 벡터 수신 (기존 API와 호환성 유지)
    
    Request Body:
    {
        "emotion_vector": [0.1, 0.2, 0.3, ...],
        "timestamp": "2024-01-01T00:00:00"
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        emotion_vector = data.get('emotion_vector', [])
        timestamp = data.get('timestamp', datetime.now().isoformat())
        
        if not emotion_vector:
            return jsonify({"error": "Emotion vector is required"}), 400
        
        # 감정 벡터를 단일 감정으로 변환 (간단한 구현)
        emotion = convert_vector_to_emotion(emotion_vector)
        intensity = calculate_intensity(emotion_vector)
        
        # 감정 로깅
        log_emotion_request(emotion, intensity, {"vector": emotion_vector})
        
        # 루프 시작
        session_id = loop_orchestrator.start_emotion_loop(emotion, intensity, {"vector": emotion_vector})
        
        response_data = {
            "session_id": session_id,
            "emotion": emotion,
            "intensity": intensity,
            "status": "processing",
            "timestamp": timestamp
        }
        
        # 응답 로깅
        log_emotion_response(response_data)
        
        return jsonify(response_data)
        
    except Exception as e:
        logger.error(f"감정 벡터 처리 실패: {e}")
        return jsonify({"error": str(e)}), 500

def convert_vector_to_emotion(vector):
    """감정 벡터를 단일 감정으로 변환"""
    emotions = ["happy", "sad", "angry", "fear", "surprise", "disgust", "trust", "anticipation"]
    
    if len(vector) >= len(emotions):
        max_index = vector.index(max(vector))
        return emotions[max_index] if max_index < len(emotions) else "neutral"
    else:
        return "neutral"

def calculate_intensity(vector):
    """감정 벡터의 강도 계산"""
    if not vector:
        return 0.5
    
    max_value = max(vector)
    return min(max_value, 1.0)

def log_emotion_request(emotion: str, intensity: float, context: Dict[str, Any]):
    """감정 요청 로깅"""
    try:
        # 파일 로깅
        today = datetime.now().strftime("%Y-%m-%d")
        log_file = os.path.join(EMOTION_LOG_DIR, f"{today}_emotion_requests.json")
        
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "emotion": emotion,
            "intensity": intensity,
            "context": context
        }
        
        # 기존 로그 읽기
        logs = []
        if os.path.exists(log_file):
            with open(log_file, 'r', encoding='utf-8') as f:
                logs = json.load(f)
        
        # 새 로그 추가
        logs.append(log_entry)
        
        # 로그 저장
        with open(log_file, 'w', encoding='utf-8') as f:
            json.dump(logs, f, indent=2, ensure_ascii=False)
        
        # 데이터베이스 로깅
        db_manager.log_emotion_request(emotion, intensity, context)
        
        logger.info(f"감정 요청 로깅: {emotion} (강도: {intensity})")
        
    except Exception as e:
        logger.error(f"감정 요청 로깅 실패: {e}")

def log_emotion_response(response_data: Dict[str, Any]):
    """감정 응답 로깅"""
    try:
        # 파일 로깅
        today = datetime.now().strftime("%Y-%m-%d")
        log_file = os.path.join(EMOTION_LOG_DIR, f"{today}_emotion_responses.json")
        
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "response": response_data
        }
        
        # 기존 로그 읽기
        logs = []
        if os.path.exists(log_file):
            with open(log_file, 'r', encoding='utf-8') as f:
                logs = json.load(f)
        
        # 새 로그 추가
        logs.append(log_entry)
        
        # 로그 저장
        with open(log_file, 'w', encoding='utf-8') as f:
            json.dump(logs, f, indent=2, ensure_ascii=False)
        
        # 데이터베이스 로깅
        db_manager.log_emotion_response(response_data)
        
        logger.info(f"감정 응답 로깅: {response_data.get('session_id', 'unknown')}")
        
    except Exception as e:
        logger.error(f"감정 응답 로깅 실패: {e}") 
