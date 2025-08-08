#!/usr/bin/env python3
"""
DuRi Evolution API Server

Evolution 모듈의 API 엔드포인트를 제공하는 Flask 서버입니다.
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import sys
from datetime import datetime
from typing import Dict, Any, Optional

# 프로젝트 루트 경로 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from evolution.evolution_controller import EvolutionController
from evolution.action_executor import ActionExecutor, ExecutionContext
from evolution.result_recorder import ResultRecorder
from evolution.experience_manager import ExperienceManager
from duri_common.logger import get_logger

logger = get_logger("duri_evolution.server")

def create_evolution_app():
    """Evolution Flask 앱 생성"""
    app = Flask(__name__)
    CORS(app)
    
    # Evolution 컴포넌트 초기화
    evolution_controller = EvolutionController()
    action_executor = ActionExecutor()
    result_recorder = ResultRecorder()
    experience_manager = ExperienceManager()
    
    @app.route('/health', methods=['GET'])
    def health_check():
        """헬스 체크 엔드포인트"""
        return jsonify({
            'status': 'healthy',
            'service': 'duri-evolution',
            'timestamp': datetime.now().isoformat(),
            'version': '1.0.0'
        })
    
    @app.route('/api/evolution/status', methods=['GET'])
    def get_evolution_status():
        """Evolution 상태 조회"""
        try:
            current_session = evolution_controller.get_current_session()
            evolution_state = evolution_controller.get_evolution_state()
            
            status = {
                'current_session': current_session,
                'evolution_state': evolution_state.value if evolution_state else None,
                'is_active': current_session is not None
            }
            
            return jsonify({
                'success': True,
                'data': status,
                'timestamp': datetime.now().isoformat()
            })
        except Exception as e:
            logger.error(f"Evolution 상태 조회 실패: {e}")
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    @app.route('/api/evolution/session/start', methods=['POST'])
    def start_evolution_session():
        """진화 세션 시작"""
        try:
            data = request.get_json() or {}
            metadata = data.get('metadata', {})
            
            session_id = evolution_controller.start_evolution_session(metadata)
            
            return jsonify({
                'success': True,
                'data': {'session_id': session_id},
                'timestamp': datetime.now().isoformat()
            })
            
        except Exception as e:
            logger.error(f"진화 세션 시작 실패: {e}")
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    @app.route('/api/evolution/session/end', methods=['POST'])
    def end_evolution_session():
        """진화 세션 종료"""
        try:
            session = evolution_controller.end_evolution_session()
            
            return jsonify({
                'success': True,
                'data': session,
                'timestamp': datetime.now().isoformat()
            })
            
        except Exception as e:
            logger.error(f"진화 세션 종료 실패: {e}")
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    @app.route('/api/evolution/cycle', methods=['POST'])
    def execute_evolution_cycle():
        """진화 사이클 실행"""
        try:
            data = request.get_json()
            if not data:
                return jsonify({
                    'success': False,
                    'error': '요청 데이터가 없습니다.'
                }), 400
            
            emotion = data.get('emotion')
            context = data.get('context', {})
            use_experience = data.get('use_experience', True)
            
            if not emotion:
                return jsonify({
                    'success': False,
                    'error': '감정 정보가 필요합니다.'
                }), 400
            
            # 진화 사이클 실행
            execution_result, recorded_result, learning_insights = evolution_controller.execute_evolution_cycle(
                emotion, context, use_experience
            )
            
            return jsonify({
                'success': True,
                'data': {
                    'execution_result': execution_result,
                    'recorded_result': recorded_result,
                    'learning_insights': learning_insights
                },
                'timestamp': datetime.now().isoformat()
            })
            
        except Exception as e:
            logger.error(f"진화 사이클 실행 실패: {e}")
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    @app.route('/api/evolution/cycle/adaptive', methods=['POST'])
    def execute_adaptive_evolution_cycle():
        """적응형 진화 사이클 실행"""
        try:
            data = request.get_json()
            if not data:
                return jsonify({
                    'success': False,
                    'error': '요청 데이터가 없습니다.'
                }), 400
            
            emotion = data.get('emotion')
            context = data.get('context', {})
            learning_rate = data.get('learning_rate', 0.1)
            
            if not emotion:
                return jsonify({
                    'success': False,
                    'error': '감정 정보가 필요합니다.'
                }), 400
            
            # 적응형 진화 사이클 실행
            execution_result, recorded_result, learning_insights, evolution_metadata = evolution_controller.execute_adaptive_evolution_cycle(
                emotion, context, learning_rate
            )
            
            return jsonify({
                'success': True,
                'data': {
                    'execution_result': execution_result,
                    'recorded_result': recorded_result,
                    'learning_insights': learning_insights,
                    'evolution_metadata': evolution_metadata
                },
                'timestamp': datetime.now().isoformat()
            })
            
        except Exception as e:
            logger.error(f"적응형 진화 사이클 실행 실패: {e}")
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    @app.route('/api/evolution/action/execute', methods=['POST'])
    def execute_action():
        """액션 실행"""
        try:
            data = request.get_json()
            if not data:
                return jsonify({
                    'success': False,
                    'error': '요청 데이터가 없습니다.'
                }), 400
            
            action = data.get('action')
            emotion = data.get('emotion')
            intensity = data.get('intensity', 0.5)
            confidence = data.get('confidence', 0.5)
            environment = data.get('environment')
            user_context = data.get('user_context', {})
            session_id = data.get('session_id')
            
            if not action or not emotion:
                return jsonify({
                    'success': False,
                    'error': '액션과 감정 정보가 필요합니다.'
                }), 400
            
            # 실행 컨텍스트 생성
            execution_context = ExecutionContext(
                emotion=emotion,
                intensity=intensity,
                confidence=confidence,
                environment=environment,
                user_context=user_context,
                session_id=session_id
            )
            
            # 액션 실행
            execution_result = action_executor.execute_action(action, execution_context)
            
            return jsonify({
                'success': True,
                'data': execution_result,
                'timestamp': datetime.now().isoformat()
            })
            
        except Exception as e:
            logger.error(f"액션 실행 실패: {e}")
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    @app.route('/api/evolution/experience/recommend', methods=['POST'])
    def get_recommended_action():
        """경험 기반 액션 추천"""
        try:
            data = request.get_json()
            if not data:
                return jsonify({
                    'success': False,
                    'error': '요청 데이터가 없습니다.'
                }), 400
            
            emotion = data.get('emotion')
            context = data.get('context', {})
            confidence_threshold = data.get('confidence_threshold', 0.7)
            
            if not emotion:
                return jsonify({
                    'success': False,
                    'error': '감정 정보가 필요합니다.'
                }), 400
            
            # 추천 액션 조회
            recommendation = experience_manager.get_recommended_action(
                emotion, context, confidence_threshold
            )
            
            return jsonify({
                'success': True,
                'data': {
                    'recommendation': recommendation,
                    'has_recommendation': recommendation is not None
                },
                'timestamp': datetime.now().isoformat()
            })
            
        except Exception as e:
            logger.error(f"액션 추천 실패: {e}")
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    @app.route('/api/evolution/patterns', methods=['GET'])
    def get_experience_patterns():
        """경험 패턴 조회"""
        try:
            emotion = request.args.get('emotion')
            min_confidence = request.args.get('min_confidence', 0.0, type=float)
            limit = request.args.get('limit', 50, type=int)
            
            patterns = experience_manager.get_experience_patterns(
                emotion=emotion, min_confidence=min_confidence, limit=limit
            )
            
            return jsonify({
                'success': True,
                'data': patterns,
                'timestamp': datetime.now().isoformat()
            })
            
        except Exception as e:
            logger.error(f"경험 패턴 조회 실패: {e}")
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    @app.route('/api/evolution/insights', methods=['GET'])
    def get_learning_insights():
        """학습 인사이트 조회"""
        try:
            emotion = request.args.get('emotion')
            insight_type = request.args.get('insight_type')
            limit = request.args.get('limit', 50, type=int)
            
            insights = experience_manager.get_learning_insights(
                emotion=emotion, insight_type=insight_type, limit=limit
            )
            
            return jsonify({
                'success': True,
                'data': insights,
                'timestamp': datetime.now().isoformat()
            })
            
        except Exception as e:
            logger.error(f"학습 인사이트 조회 실패: {e}")
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    @app.route('/api/evolution/statistics', methods=['GET'])
    def get_evolution_statistics():
        """Evolution 통계 조회"""
        try:
            stats = evolution_controller.get_comprehensive_statistics()
            
            return jsonify({
                'success': True,
                'data': stats,
                'timestamp': datetime.now().isoformat()
            })
            
        except Exception as e:
            logger.error(f"Evolution 통계 조회 실패: {e}")
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    @app.route('/api/evolution/insights/evolution', methods=['GET'])
    def get_evolution_insights():
        """진화 인사이트 조회"""
        try:
            limit = request.args.get('limit', 10, type=int)
            
            insights = evolution_controller.get_evolution_insights(limit=limit)
            
            return jsonify({
                'success': True,
                'data': insights,
                'timestamp': datetime.now().isoformat()
            })
            
        except Exception as e:
            logger.error(f"진화 인사이트 조회 실패: {e}")
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    @app.route('/api/evolution/data/export', methods=['POST'])
    def export_evolution_data():
        """진화 데이터 내보내기"""
        try:
            data = request.get_json() or {}
            export_path = data.get('export_path', '/tmp')
            
            success = evolution_controller.export_evolution_data(export_path)
            
            return jsonify({
                'success': success,
                'data': {'export_path': export_path},
                'timestamp': datetime.now().isoformat()
            })
            
        except Exception as e:
            logger.error(f"진화 데이터 내보내기 실패: {e}")
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    @app.route('/api/evolution/data/reset', methods=['POST'])
    def reset_evolution_data():
        """진화 데이터 초기화"""
        try:
            data = request.get_json() or {}
            confirm = data.get('confirm', False)
            
            if not confirm:
                return jsonify({
                    'success': False,
                    'error': '초기화를 위해서는 confirm=true를 설정해야 합니다.'
                }), 400
            
            success = evolution_controller.reset_evolution_data(confirm=True)
            
            return jsonify({
                'success': success,
                'data': {'reset_completed': success},
                'timestamp': datetime.now().isoformat()
            })
            
        except Exception as e:
            logger.error(f"진화 데이터 초기화 실패: {e}")
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    return app

def main():
    """메인 실행 함수"""
    app = create_evolution_app()
    
    # 포트 설정 (8082)
    port = int(os.environ.get('PORT', 8082))
    
    try:
        logger.info("🔄 DuRi Evolution API 서버 시작 중...")
        logger.info(f"📍 포트: {port}")
        logger.info("=" * 50)
        
        # 서버 실행
        app.run(host="0.0.0.0", port=port, debug=False)
        
    except Exception as e:
        logger.error(f"❌ Evolution 서버 시작 실패: {e}")

if __name__ == "__main__":
    main() 