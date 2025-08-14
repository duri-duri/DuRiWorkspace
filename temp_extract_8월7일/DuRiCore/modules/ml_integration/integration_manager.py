"""
Phase 1과 Phase 2 통합 관리자
기존 파일들을 최소한으로 수정하고, 새로운 통합 기능을 별도로 관리
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class IntegrationManager:
    """Phase 1과 Phase 2 통합 관리자"""
    
    def __init__(self):
        self.phase1_solver = None
        self.phase2_system = None
        self.integration_status = 'not_initialized'
        self.integration_timestamp = None
        
        # 통합 설정
        self.integration_config = {
            'auto_integration': True,
            'integration_validation': True,
            'performance_threshold': 0.5,
            'max_integration_attempts': 3
        }
        
        logger.info("통합 관리자 초기화 완료")
    
    def set_phase1_solver(self, phase1_solver) -> bool:
        """Phase 1 솔버 설정"""
        try:
            if not hasattr(phase1_solver, 'get_integration_interface'):
                logger.error("Phase 1 솔버에 통합 인터페이스가 없습니다")
                return False
            
            self.phase1_solver = phase1_solver
            logger.info("Phase 1 솔버 설정 완료")
            return True
            
        except Exception as e:
            logger.error(f"Phase 1 솔버 설정 실패: {e}")
            return False
    
    def set_phase2_system(self, phase2_system) -> bool:
        """Phase 2 시스템 설정"""
        try:
            if not hasattr(phase2_system, 'integrate_with_phase1'):
                logger.error("Phase 2 시스템에 통합 인터페이스가 없습니다")
                return False
            
            self.phase2_system = phase2_system
            logger.info("Phase 2 시스템 설정 완료")
            return True
            
        except Exception as e:
            logger.error(f"Phase 2 시스템 설정 실패: {e}")
            return False
    
    def check_integration_readiness(self) -> Dict[str, Any]:
        """통합 준비 상태 확인"""
        try:
            readiness_check = {
                'phase1_ready': False,
                'phase2_ready': False,
                'integration_possible': False,
                'issues': []
            }
            
            # Phase 1 준비 상태 확인
            if self.phase1_solver:
                if hasattr(self.phase1_solver, 'is_ready_for_integration'):
                    readiness_check['phase1_ready'] = self.phase1_solver.is_ready_for_integration()
                else:
                    readiness_check['issues'].append('Phase 1 통합 인터페이스 없음')
            else:
                readiness_check['issues'].append('Phase 1 솔버가 설정되지 않음')
            
            # Phase 2 준비 상태 확인
            if self.phase2_system:
                if hasattr(self.phase2_system, 'deep_learning_model'):
                    readiness_check['phase2_ready'] = bool(self.phase2_system.deep_learning_model)
                else:
                    readiness_check['issues'].append('Phase 2 딥러닝 모델이 학습되지 않음')
            else:
                readiness_check['issues'].append('Phase 2 시스템이 설정되지 않음')
            
            # 통합 가능성 확인
            readiness_check['integration_possible'] = (
                readiness_check['phase1_ready'] and 
                readiness_check['phase2_ready']
            )
            
            return readiness_check
            
        except Exception as e:
            logger.error(f"통합 준비 상태 확인 실패: {e}")
            return {'error': str(e)}
    
    def perform_integration(self) -> Dict[str, Any]:
        """Phase 1과 Phase 2 통합 수행"""
        try:
            # 준비 상태 확인
            readiness = self.check_integration_readiness()
            if not readiness.get('integration_possible', False):
                return {
                    'success': False,
                    'reason': '통합 준비되지 않음',
                    'readiness_check': readiness
                }
            
            # Phase 1과 Phase 2 통합
            integration_result = self.phase2_system.integrate_with_phase1(self.phase1_solver)
            
            if integration_result.get('success'):
                self.integration_status = 'completed'
                self.integration_timestamp = datetime.now().isoformat()
                
                logger.info("Phase 1과 Phase 2 통합 완료")
                
                return {
                    'success': True,
                    'integration_status': 'completed',
                    'integration_timestamp': self.integration_timestamp,
                    'phase1_models_count': integration_result.get('phase1_models_count', 0),
                    'hybrid_system_ready': integration_result.get('hybrid_system_ready', False)
                }
            else:
                self.integration_status = 'failed'
                return {
                    'success': False,
                    'reason': integration_result.get('reason', '알 수 없는 오류'),
                    'integration_status': 'failed'
                }
                
        except Exception as e:
            logger.error(f"통합 수행 실패: {e}")
            self.integration_status = 'error'
            return {'success': False, 'reason': str(e)}
    
    def create_enhanced_hybrid_system(self) -> Dict[str, Any]:
        """향상된 하이브리드 시스템 생성"""
        try:
            if self.integration_status != 'completed':
                return {'success': False, 'reason': '먼저 통합을 수행해야 합니다'}
            
            # 향상된 하이브리드 시스템 생성
            enhanced_result = self.phase2_system.create_enhanced_hybrid_system()
            
            if enhanced_result.get('success'):
                logger.info("향상된 하이브리드 시스템 생성 완료")
            
            return enhanced_result
            
        except Exception as e:
            logger.error(f"향상된 하이브리드 시스템 생성 실패: {e}")
            return {'success': False, 'reason': str(e)}
    
    def get_integration_summary(self) -> Dict[str, Any]:
        """통합 요약 정보"""
        summary = {
            'integration_status': self.integration_status,
            'integration_timestamp': self.integration_timestamp,
            'phase1_configured': bool(self.phase1_solver),
            'phase2_configured': bool(self.phase2_system),
            'integration_config': self.integration_config.copy()
        }
        
        # Phase 1 상태 추가
        if self.phase1_solver:
            if hasattr(self.phase1_solver, 'get_integration_summary'):
                summary['phase1_status'] = self.phase1_solver.get_integration_summary()
            else:
                summary['phase1_status'] = 'interface_not_available'
        
        # Phase 2 상태 추가
        if self.phase2_system:
            if hasattr(self.phase2_system, 'get_phase1_integration_status'):
                summary['phase2_status'] = self.phase2_system.get_phase1_integration_status()
            else:
                summary['phase2_status'] = 'interface_not_available'
        
        return summary
    
    def validate_integration(self) -> Dict[str, Any]:
        """통합 결과 검증"""
        try:
            if self.integration_status != 'completed':
                return {'valid': False, 'reason': '통합이 완료되지 않음'}
            
            # 성능 검증
            if self.phase2_system and hasattr(self.phase2_system, 'performance_metrics'):
                dl_performance = self.phase2_system.performance_metrics.get('deep_learning', {})
                r2_score = dl_performance.get('r2_score', 0)
                
                if r2_score < self.integration_config['performance_threshold']:
                    return {
                        'valid': False, 
                        'reason': f'딥러닝 성능 부족: R²={r2_score:.3f}',
                        'performance': dl_performance
                    }
            
            # 통합 상태 검증
            readiness = self.check_integration_readiness()
            if not readiness.get('integration_possible', False):
                return {'valid': False, 'reason': '통합 상태 불량'}
            
            return {
                'valid': True,
                'integration_status': 'validated',
                'performance_metrics': dl_performance if 'dl_performance' in locals() else {}
            }
            
        except Exception as e:
            logger.error(f"통합 검증 실패: {e}")
            return {'valid': False, 'reason': str(e)}
    
    def reset_integration(self) -> bool:
        """통합 상태 초기화"""
        try:
            self.integration_status = 'not_initialized'
            self.integration_timestamp = None
            
            if self.phase2_system:
                self.phase2_system.phase1_models = {}
            
            logger.info("통합 상태 초기화 완료")
            return True
            
        except Exception as e:
            logger.error(f"통합 상태 초기화 실패: {e}")
            return False
