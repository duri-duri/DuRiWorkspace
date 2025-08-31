#!/usr/bin/env python3
"""
DuRi Brain API Server

Brain 모듈의 API 엔드포인트를 제공하는 Flask 서버입니다.
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import sys
from datetime import datetime
from typing import Dict, Any, Optional

# 프로젝트 루트 경로 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from brain.brain_controller import BrainController
from brain.loop_manager import LoopManager
from brain.feedback_collector import FeedbackCollector
from brain.emotion_recorder import EmotionRecorder
from duri_common.logger import get_logger

logger = get_logger("duri_brain.server")

def create_brain_app():
    """Brain Flask 앱 생성"""
    app = Flask(__name__)
    CORS(app)
    
    # Brain 컴포넌트 초기화
    brain_controller = BrainController()
    loop_manager = LoopManager()
    feedback_collector = FeedbackCollector()
    emotion_recorder = EmotionRecorder()
    
    @app.route('/health', methods=['GET'])
    def health_check():
        """헬스 체크 엔드포인트"""
        return jsonify({
            'status': 'healthy',
            'service': 'duri-brain',
            'timestamp': datetime.now().isoformat(),
            'version': '1.0.0'
        })
    
    @app.route('/api/brain/status', methods=['GET'])
    def get_brain_status():
        """Brain 상태 조회"""
        try:
            status = brain_controller.get_brain_status()
            return jsonify({
                'success': True,
                'data': status,
                'timestamp': datetime.now().isoformat()
            })
        except Exception as e:
            logger.error(f"Brain 상태 조회 실패: {e}")
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    @app.route('/api/brain/process', methods=['POST'])
    def process_emotion():
        """감정 처리"""
        try:
            data = request.get_json()
            if not data:
                return jsonify({
                    'success': False,
                    'error': '요청 데이터가 없습니다.'
                }), 400
            
            emotion = data.get('emotion')
            intensity = data.get('intensity', 0.5)
            context = data.get('context', {})
            
            if not emotion:
                return jsonify({
                    'success': False,
                    'error': '감정 정보가 필요합니다.'
                }), 400
            
            # Brain 처리
            result = brain_controller.process_emotion(emotion, intensity, context)
            
            return jsonify({
                'success': True,
                'data': result,
                'timestamp': datetime.now().isoformat()
            })
            
        except Exception as e:
            logger.error(f"감정 처리 실패: {e}")
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    @app.route('/api/brain/loop/start', methods=['POST'])
    def start_emotion_loop():
        """감정 루프 시작"""
        try:
            data = request.get_json() or {}
            loop_config = data.get('config', {})
            
            result = loop_manager.start_emotion_loop(loop_config)
            
            return jsonify({
                'success': True,
                'data': result,
                'timestamp': datetime.now().isoformat()
            })
            
        except Exception as e:
            logger.error(f"감정 루프 시작 실패: {e}")
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    @app.route('/api/brain/loop/stop', methods=['POST'])
    def stop_emotion_loop():
        """감정 루프 중지"""
        try:
            result = loop_manager.stop_emotion_loop()
            
            return jsonify({
                'success': True,
                'data': result,
                'timestamp': datetime.now().isoformat()
            })
            
        except Exception as e:
            logger.error(f"감정 루프 중지 실패: {e}")
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    @app.route('/api/brain/loop/status', methods=['GET'])
    def get_loop_status():
        """루프 상태 조회"""
        try:
            status = loop_manager.get_loop_status()
            
            return jsonify({
                'success': True,
                'data': status,
                'timestamp': datetime.now().isoformat()
            })
            
        except Exception as e:
            logger.error(f"루프 상태 조회 실패: {e}")
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    @app.route('/api/brain/feedback', methods=['POST'])
    def collect_feedback():
        """피드백 수집"""
        try:
            data = request.get_json()
            if not data:
                return jsonify({
                    'success': False,
                    'error': '피드백 데이터가 없습니다.'
                }), 400
            
            feedback_type = data.get('type')
            content = data.get('content')
            metadata = data.get('metadata', {})
            
            if not feedback_type or not content:
                return jsonify({
                    'success': False,
                    'error': '피드백 타입과 내용이 필요합니다.'
                }), 400
            
            result = feedback_collector.collect_feedback(feedback_type, content, metadata)
            
            return jsonify({
                'success': True,
                'data': result,
                'timestamp': datetime.now().isoformat()
            })
            
        except Exception as e:
            logger.error(f"피드백 수집 실패: {e}")
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    @app.route('/api/brain/emotions', methods=['GET'])
    def get_emotion_history():
        """감정 히스토리 조회"""
        try:
            limit = request.args.get('limit', 100, type=int)
            emotion = request.args.get('emotion')
            
            history = emotion_recorder.get_emotion_history(emotion=emotion, limit=limit)
            
            return jsonify({
                'success': True,
                'data': history,
                'timestamp': datetime.now().isoformat()
            })
            
        except Exception as e:
            logger.error(f"감정 히스토리 조회 실패: {e}")
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    @app.route('/api/brain/emotions/current', methods=['GET'])
    def get_current_emotion():
        """현재 감정 조회"""
        try:
            current_emotion = emotion_recorder.get_current_emotion()
            
            return jsonify({
                'success': True,
                'data': current_emotion,
                'timestamp': datetime.now().isoformat()
            })
            
        except Exception as e:
            logger.error(f"현재 감정 조회 실패: {e}")
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    @app.route('/api/brain/statistics', methods=['GET'])
    def get_brain_statistics():
        """Brain 통계 조회"""
        try:
            stats = brain_controller.get_brain_statistics()
            
            return jsonify({
                'success': True,
                'data': stats,
                'timestamp': datetime.now().isoformat()
            })
            
        except Exception as e:
            logger.error(f"Brain 통계 조회 실패: {e}")
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    return app

def main():
    """메인 실행 함수"""
    app = create_brain_app()
    
    # 포트 설정 (8081)
    port = int(os.environ.get('PORT', 8081))
    
    try:
        logger.info("🧠 DuRi Brain API 서버 시작 중...")
        logger.info(f"📍 포트: {port}")
        logger.info("=" * 50)
        
        # 서버 실행
        app.run(host="0.0.0.0", port=port, debug=False)
        
    except Exception as e:
        logger.error(f"❌ Brain 서버 시작 실패: {e}")

if __name__ == "__main__":
    main() 