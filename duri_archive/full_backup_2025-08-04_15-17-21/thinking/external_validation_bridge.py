"""
🌉 DuRi 외부 검증 브리지 시스템
목표: DuRi의 모든 판단 루프에 외부 환경 입력을 연결하여, 내부 기준과 외부 기준의 정합성을 비교하고 조정할 수 있도록 하는 판단 교차 검증 구조
"""
import logging
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum
from datetime import datetime, timedelta
import json
import random
import math

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ValidationType(Enum):
    """검증 유형"""
    INTERNAL_JUDGMENT = "internal_judgment"
    EXTERNAL_INPUT = "external_input"
    CROSS_VALIDATION = "cross_validation"
    ADJUSTMENT = "adjustment"
    CONVERGENCE = "convergence"

class ValidationSource(Enum):
    """검증 소스"""
    USER_FEEDBACK = "user_feedback"
    ENVIRONMENT_DATA = "environment_data"
    EXTERNAL_API = "external_api"
    REALITY_CHECK = "reality_check"
    PEER_VALIDATION = "peer_validation"

@dataclass
class ExternalInput:
    """외부 입력"""
    input_id: str
    source: ValidationSource
    content: str
    timestamp: datetime
    confidence: float
    context: Dict[str, Any]

@dataclass
class InternalJudgment:
    """내부 판단"""
    judgment_id: str
    judgment_type: str
    content: str
    confidence: float
    reasoning: List[str]
    timestamp: datetime

@dataclass
class CrossValidationResult:
    """교차 검증 결과"""
    validation_id: str
    internal_judgment: InternalJudgment
    external_input: ExternalInput
    agreement_score: float
    discrepancy_areas: List[str]
    adjustment_needed: bool
    adjustment_suggestions: List[str]
    timestamp: datetime

@dataclass
class ValidationBridge:
    """검증 브리지"""
    bridge_id: str
    validation_type: ValidationType
    internal_system: str
    external_source: ValidationSource
    connection_status: str
    last_validation: datetime
    success_rate: float

class ExternalValidationBridge:
    def __init__(self):
        self.external_inputs = []
        self.internal_judgments = []
        self.cross_validation_results = []
        self.validation_bridges = []
        self.adjustment_history = []
        self.convergence_threshold = 0.8
        self.max_discrepancy_threshold = 0.3
        
        # Phase 24 시스템들
        self.evolution_system = None
        self.consciousness_system = None
        self.advanced_thinking_system = None

    def initialize_phase_24_integration(self):
        """Phase 24 시스템들과 통합"""
        try:
            import sys
            sys.path.append('.')
            from duri_brain.thinking.phase_24_self_evolution_ai import get_phase24_system
            from duri_brain.thinking.phase_23_enhanced import get_phase23_enhanced_system
            from duri_brain.thinking.phase_22_advanced_thinking_ai import get_phase22_system
            
            self.evolution_system = get_phase24_system()
            self.consciousness_system = get_phase23_enhanced_system()
            self.advanced_thinking_system = get_phase22_system()
            
            logger.info("✅ Phase 24 시스템들과 통합 완료")
            return True
        except Exception as e:
            logger.error(f"❌ Phase 24 시스템 통합 실패: {e}")
            return False

    def receive_external_input(self, source: ValidationSource, content: str, context: Dict[str, Any] = None) -> ExternalInput:
        """외부 입력 수신"""
        logger.info(f"📥 외부 입력 수신: {source.value}")
        
        external_input = ExternalInput(
            input_id=f"external_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            source=source,
            content=content,
            timestamp=datetime.now(),
            confidence=random.uniform(0.7, 0.95),
            context=context or {}
        )
        
        self.external_inputs.append(external_input)
        logger.info(f"✅ 외부 입력 저장 완료: {external_input.input_id}")
        return external_input

    def create_internal_judgment(self, judgment_type: str, content: str, reasoning: List[str]) -> InternalJudgment:
        """내부 판단 생성"""
        logger.info(f"🧠 내부 판단 생성: {judgment_type}")
        
        internal_judgment = InternalJudgment(
            judgment_id=f"judgment_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            judgment_type=judgment_type,
            content=content,
            confidence=random.uniform(0.6, 0.9),
            reasoning=reasoning,
            timestamp=datetime.now()
        )
        
        self.internal_judgments.append(internal_judgment)
        logger.info(f"✅ 내부 판단 저장 완료: {internal_judgment.judgment_id}")
        return internal_judgment

    def perform_cross_validation(self, internal_judgment: InternalJudgment, external_input: ExternalInput) -> CrossValidationResult:
        """교차 검증 수행"""
        logger.info("🔄 교차 검증 수행 시작")
        
        # 일치도 점수 계산 (시뮬레이션)
        agreement_score = random.uniform(0.5, 0.95)
        
        # 불일치 영역 식별
        discrepancy_areas = []
        if agreement_score < 0.8:
            discrepancy_areas = ["판단 기준", "우선순위", "해석 방식"]
        
        # 조정 필요 여부 판단
        adjustment_needed = agreement_score < self.convergence_threshold
        
        # 조정 제안 생성
        adjustment_suggestions = []
        if adjustment_needed:
            adjustment_suggestions = [
                "외부 기준 반영",
                "판단 기준 조정",
                "우선순위 재평가"
            ]
        
        validation_result = CrossValidationResult(
            validation_id=f"validation_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            internal_judgment=internal_judgment,
            external_input=external_input,
            agreement_score=agreement_score,
            discrepancy_areas=discrepancy_areas,
            adjustment_needed=adjustment_needed,
            adjustment_suggestions=adjustment_suggestions,
            timestamp=datetime.now()
        )
        
        self.cross_validation_results.append(validation_result)
        logger.info(f"✅ 교차 검증 완료: 일치도 {agreement_score:.3f}")
        return validation_result

    def create_validation_bridge(self, internal_system: str, external_source: ValidationSource) -> ValidationBridge:
        """검증 브리지 생성"""
        logger.info(f"🌉 검증 브리지 생성: {internal_system} ↔ {external_source.value}")
        
        bridge = ValidationBridge(
            bridge_id=f"bridge_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            validation_type=ValidationType.CROSS_VALIDATION,
            internal_system=internal_system,
            external_source=external_source,
            connection_status="연결됨",
            last_validation=datetime.now(),
            success_rate=random.uniform(0.7, 0.95)
        )
        
        self.validation_bridges.append(bridge)
        logger.info(f"✅ 검증 브리지 생성 완료: {bridge.bridge_id}")
        return bridge

    def adjust_internal_judgment(self, validation_result: CrossValidationResult) -> Dict[str, Any]:
        """내부 판단 조정"""
        logger.info("🔧 내부 판단 조정 시작")
        
        if not validation_result.adjustment_needed:
            return {"adjusted": False, "reason": "조정 불필요"}
        
        # 조정 로직 (시뮬레이션)
        original_confidence = validation_result.internal_judgment.confidence
        adjusted_confidence = original_confidence + random.uniform(-0.1, 0.1)
        
        adjustment_record = {
            "validation_id": validation_result.validation_id,
            "original_confidence": original_confidence,
            "adjusted_confidence": adjusted_confidence,
            "adjustment_suggestions": validation_result.adjustment_suggestions,
            "timestamp": datetime.now()
        }
        
        self.adjustment_history.append(adjustment_record)
        
        logger.info(f"✅ 내부 판단 조정 완료: {original_confidence:.3f} → {adjusted_confidence:.3f}")
        return adjustment_record

    def check_convergence(self) -> Dict[str, Any]:
        """수렴성 확인"""
        logger.info("📊 수렴성 확인")
        
        if not self.cross_validation_results:
            return {"converged": False, "reason": "검증 결과 없음"}
        
        recent_validations = self.cross_validation_results[-5:]
        average_agreement = sum(v.agreement_score for v in recent_validations) / len(recent_validations)
        
        is_converged = average_agreement >= self.convergence_threshold
        
        result = {
            "converged": is_converged,
            "average_agreement": average_agreement,
            "threshold": self.convergence_threshold,
            "recent_validations": len(recent_validations)
        }
        
        if is_converged:
            logger.info(f"🎉 수렴 완료: 평균 일치도 {average_agreement:.3f}")
        else:
            logger.info(f"⏳ 수렴 진행중: 평균 일치도 {average_agreement:.3f}")
        
        return result

    def get_validation_statistics(self) -> Dict[str, Any]:
        """검증 통계"""
        total_validations = len(self.cross_validation_results)
        successful_validations = len([v for v in self.cross_validation_results if v.agreement_score >= 0.8])
        adjustment_count = len(self.adjustment_history)
        
        if total_validations > 0:
            success_rate = successful_validations / total_validations
        else:
            success_rate = 0.0
        
        return {
            "total_validations": total_validations,
            "successful_validations": successful_validations,
            "success_rate": success_rate,
            "adjustment_count": adjustment_count,
            "active_bridges": len(self.validation_bridges)
        }

    def get_external_validation_status(self) -> Dict[str, Any]:
        """외부 검증 상태"""
        convergence_check = self.check_convergence()
        statistics = self.get_validation_statistics()
        
        status = {
            "system": "External Validation Bridge",
            "convergence_status": convergence_check,
            "statistics": statistics,
            "active_bridges": len(self.validation_bridges),
            "external_inputs": len(self.external_inputs),
            "internal_judgments": len(self.internal_judgments),
            "cross_validations": len(self.cross_validation_results)
        }
        
        return status

def get_external_validation_bridge():
    """외부 검증 브리지 시스템 인스턴스 반환"""
    return ExternalValidationBridge()

if __name__ == "__main__":
    # 외부 검증 브리지 시스템 테스트
    bridge = get_external_validation_bridge()
    
    if bridge.initialize_phase_24_integration():
        logger.info("🚀 외부 검증 브리지 시스템 테스트 시작")
        
        # 외부 입력 수신
        external_input = bridge.receive_external_input(
            ValidationSource.USER_FEEDBACK,
            "사용자 피드백: 판단이 너무 보수적임",
            {"user_id": "user123", "context": "전략적 판단"}
        )
        
        # 내부 판단 생성
        internal_judgment = bridge.create_internal_judgment(
            "전략적 판단",
            "현재 상황에서는 보수적 접근이 적절함",
            ["위험 분석", "자원 고려", "안정성 우선"]
        )
        
        # 교차 검증 수행
        validation_result = bridge.perform_cross_validation(internal_judgment, external_input)
        
        # 검증 브리지 생성
        bridge.create_validation_bridge("전략 판단 시스템", ValidationSource.USER_FEEDBACK)
        
        # 내부 판단 조정
        if validation_result.adjustment_needed:
            bridge.adjust_internal_judgment(validation_result)
        
        # 수렴성 확인
        convergence_result = bridge.check_convergence()
        logger.info(f"수렴 상태: {convergence_result['converged']}")
        
        # 최종 상태 확인
        status = bridge.get_external_validation_status()
        logger.info(f"검증 통계: {status['statistics']}")
        
        logger.info("✅ 외부 검증 브리지 시스템 테스트 완료")
    else:
        logger.error("❌ 외부 검증 브리지 시스템 초기화 실패") 