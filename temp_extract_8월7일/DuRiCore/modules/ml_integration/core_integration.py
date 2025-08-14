"""
핵심 통합 관리자 (Core Integration Manager)
Phase 1과 Phase 2의 기본적인 통합만 담당하는 가벼운 모듈
"""

import logging
from typing import Dict, Any
from datetime import datetime

logger = logging.getLogger(__name__)

class CoreIntegrationManager:
    """핵심 통합 관리자 - 기본 통합 기능만 담당"""
    
    def __init__(self):
        self.phase1_solver = None
        self.phase2_system = None
        self.integration_status = 'not_initialized'
        self.integration_timestamp = None
        
        # 기본 통합 설정
        self.integration_config = {
            'auto_integration': False,  # 기본값은 수동 통합
            'performance_threshold': 0.5,
            'max_integration_attempts': 3
        }
        
        logger.info("핵심 통합 관리자 초기화 완료")
    
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
        """기본 통합 수행"""
        try:
            if not self.phase1_solver or not self.phase2_system:
                return {'success': False, 'reason': 'Phase 1 또는 Phase 2가 설정되지 않음'}
            
            # Phase 1과 Phase 2 통합
            integration_result = self.phase2_system.integrate_with_phase1(self.phase1_solver)
            
            if integration_result.get('success'):
                self.integration_status = 'completed'
                self.integration_timestamp = datetime.now().isoformat()
                logger.info("기본 통합 완료")
                
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
                    'reason': integration_result.get('reason', '알 수 없는 오류')
                }
                
        except Exception as e:
            logger.error(f"기본 통합 수행 실패: {e}")
            self.integration_status = 'error'
            return {'success': False, 'reason': str(e)}
    
    def get_integration_summary(self) -> Dict[str, Any]:
        """기본 통합 요약 정보"""
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
