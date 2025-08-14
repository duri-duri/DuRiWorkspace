"""
간단한 Phase 1 + Phase 2 통합 관리자
"""

import logging
from typing import Dict, Any
from datetime import datetime

logger = logging.getLogger(__name__)

class SimpleIntegrationManager:
    """간단한 통합 관리자"""
    
    def __init__(self):
        self.phase1_solver = None
        self.phase2_system = None
        self.integration_status = 'not_initialized'
        
        logger.info("간단한 통합 관리자 초기화 완료")
    
    def set_phase1_solver(self, phase1_solver) -> bool:
        """Phase 1 솔버 설정"""
        try:
            if hasattr(phase1_solver, 'get_integration_interface'):
                self.phase1_solver = phase1_solver
                logger.info("Phase 1 솔버 설정 완료")
                return True
            else:
                logger.error("Phase 1 솔버에 통합 인터페이스가 없습니다")
                return False
        except Exception as e:
            logger.error(f"Phase 1 솔버 설정 실패: {e}")
            return False
    
    def set_phase2_system(self, phase2_system) -> bool:
        """Phase 2 시스템 설정"""
        try:
            if hasattr(phase2_system, 'integrate_with_phase1'):
                self.phase2_system = phase2_system
                logger.info("Phase 2 시스템 설정 완료")
                return True
            else:
                logger.error("Phase 2 시스템에 통합 인터페이스가 없습니다")
                return False
        except Exception as e:
            logger.error(f"Phase 2 시스템 설정 실패: {e}")
            return False
    
    def perform_integration(self) -> Dict[str, Any]:
        """통합 수행"""
        try:
            if not self.phase1_solver or not self.phase2_system:
                return {'success': False, 'reason': 'Phase 1 또는 Phase 2가 설정되지 않음'}
            
            # Phase 1과 Phase 2 통합
            integration_result = self.phase2_system.integrate_with_phase1(self.phase1_solver)
            
            if integration_result.get('success'):
                self.integration_status = 'completed'
                logger.info("통합 완료")
                
                return {
                    'success': True,
                    'integration_status': 'completed',
                    'timestamp': datetime.now().isoformat()
                }
            else:
                self.integration_status = 'failed'
                return {
                    'success': False,
                    'reason': integration_result.get('reason', '알 수 없는 오류')
                }
                
        except Exception as e:
            logger.error(f"통합 수행 실패: {e}")
            return {'success': False, 'reason': str(e)}
    
    def get_status(self) -> Dict[str, Any]:
        """상태 정보"""
        return {
            'integration_status': self.integration_status,
            'phase1_configured': bool(self.phase1_solver),
            'phase2_configured': bool(self.phase2_system),
            'ready_for_integration': bool(self.phase1_solver and self.phase2_system)
        }
