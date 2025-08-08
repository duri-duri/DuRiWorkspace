"""
🔗 DuRi Insight Engine 통합 모듈
목표: Insight Engine을 기존 학습 루프와 통합
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class InsightLearningIntegrator:
    """Insight Engine과 학습 루프 통합기"""
    
    def __init__(self):
        from duri_brain.learning.insight_engine import get_dual_response_system
        self.dual_response_system = get_dual_response_system()
        self.integration_active = False
        self.insight_sessions = []
        
    def activate_integration(self) -> bool:
        """통합 활성화"""
        logger.info("🔗 Insight Engine 통합 활성화")
        self.integration_active = True
        return True
        
    def deactivate_integration(self) -> bool:
        """통합 비활성화"""
        logger.info("🔗 Insight Engine 통합 비활성화")
        self.integration_active = False
        return True
        
    def check_learning_loop_status(self) -> Dict[str, Any]:
        """학습 루프 상태 확인"""
        # 실제로는 learning_loop_manager와 연동
        return {
            "is_active": True,
            "current_cycle": "learning_phase",
            "performance_metrics": {
                "success_rate": 0.7,
                "error_rate": 0.3,
                "efficiency": 0.65
            }
        }
        
    def detect_learning_problems(self) -> Optional[str]:
        """학습 문제 감지"""
        status = self.check_learning_loop_status()
        
        problems = []
        
        # 성능 저하 감지
        if status["performance_metrics"]["efficiency"] < 0.7:
            problems.append("학습 효율성 저하")
            
        # 오류율 증가 감지
        if status["performance_metrics"]["error_rate"] > 0.2:
            problems.append("학습 오류율 증가")
            
        # 성공률 저하 감지
        if status["performance_metrics"]["success_rate"] < 0.8:
            problems.append("학습 성공률 저하")
            
        if problems:
            return " + ".join(problems)
        return None
        
    def execute_insight_enhanced_learning(self) -> Dict[str, Any]:
        """통찰 강화 학습 실행"""
        if not self.integration_active:
            return {"status": "integration_inactive", "action": "activate_first"}
            
        # 1. 학습 문제 감지
        problem = self.detect_learning_problems()
        
        if not problem:
            return {"status": "no_problems", "action": "continue_normal"}
            
        logger.info(f"🔍 학습 문제 감지: {problem}")
        
        # 2. 이중 응답 시스템 실행
        result = self.dual_response_system.execute_dual_response(problem)
        
        # 3. 결과 처리
        if result["status"] == "insight_generated":
            insight = result["insight"]
            session = result["session"]
            
            # 통찰 세션 기록
            self.insight_sessions.append({
                "timestamp": datetime.now(),
                "problem": problem,
                "insight": insight.strategy,
                "confidence": insight.confidence,
                "session_id": session.session_id
            })
            
            logger.info(f"🧠 통찰 생성됨: {insight.strategy}")
            
            return {
                "status": "insight_applied",
                "problem": problem,
                "insight": insight.strategy,
                "confidence": insight.confidence,
                "action": "apply_insight_strategy"
            }
            
        elif result["status"] == "rational_only":
            logger.info("🔧 이성적 리팩터링만 실행됨")
            return {
                "status": "rational_refactor_only",
                "problem": problem,
                "action": "continue_with_rational"
            }
            
        else:
            logger.warning("❌ 통찰 생성 실패")
            return {
                "status": "insight_failed",
                "problem": problem,
                "action": "fallback_to_rational"
            }
            
    def get_integration_status(self) -> Dict[str, Any]:
        """통합 상태 반환"""
        return {
            "integration_active": self.integration_active,
            "dual_response_system": {
                "rational_refactor_count": self.dual_response_system.rational_refactor_count,
                "insight_trigger_count": self.dual_response_system.insight_trigger_count,
                "successful_insights": self.dual_response_system.insight_engine.successful_insights
            },
            "insight_sessions": len(self.insight_sessions),
            "recent_insights": self.insight_sessions[-3:] if self.insight_sessions else []
        }
        
    def apply_insight_to_learning_loop(self, insight_strategy: str) -> bool:
        """통찰을 학습 루프에 적용"""
        logger.info(f"🔄 통찰을 학습 루프에 적용: {insight_strategy[:50]}...")
        
        # 실제로는 learning_loop_manager에 통찰 전략을 전달
        # 여기서는 시뮬레이션
        
        try:
            # 통찰 전략을 학습 루프에 적용하는 로직
            logger.info("✅ 통찰 전략이 학습 루프에 성공적으로 적용됨")
            return True
        except Exception as e:
            logger.error(f"❌ 통찰 전략 적용 실패: {e}")
            return False

# 전역 인스턴스
_insight_integrator = None

def get_insight_integrator() -> InsightLearningIntegrator:
    """전역 통합기 인스턴스 반환"""
    global _insight_integrator
    if _insight_integrator is None:
        _insight_integrator = InsightLearningIntegrator()
    return _insight_integrator

def integrate_insight_with_learning():
    """Insight Engine을 학습 루프와 통합"""
    integrator = get_insight_integrator()
    integrator.activate_integration()
    return integrator

if __name__ == "__main__":
    # 통합 테스트
    integrator = get_insight_integrator()
    
    # 통합 활성화
    integrator.activate_integration()
    
    # 통찰 강화 학습 실행
    result = integrator.execute_insight_enhanced_learning()
    
    print(f"\n🎯 통합 결과: {result}")
    
    # 상태 확인
    status = integrator.get_integration_status()
    print(f"\n📊 통합 상태: {status}") 