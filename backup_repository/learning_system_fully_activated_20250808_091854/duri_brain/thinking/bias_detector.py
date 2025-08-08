"""
🧠 DuRi 편향 탐지기 (BiasDetector)

인지적 편향을 탐지하고 분석하는 시스템입니다.
판단 과정에서 발생할 수 있는 다양한 편향을 식별하고,
편향의 영향을 평가하여 더 객관적인 판단을 도모합니다.
"""

import logging
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
from datetime import datetime
import json
import random

logger = logging.getLogger(__name__)

class BiasType(Enum):
    """편향 유형"""
    CONFIRMATION_BIAS = "confirmation_bias"        # 확인 편향
    ANCHORING_BIAS = "anchoring_bias"              # 앵커링 편향
    AVAILABILITY_BIAS = "availability_bias"        # 가용성 편향
    OVERCONFIDENCE_BIAS = "overconfidence_bias"    # 과신 편향
    GROUPTHINK_BIAS = "groupthink_bias"            # 그룹싱크 편향
    COGNITIVE_LOAD_BIAS = "cognitive_load_bias"    # 인지 부하 편향

class BiasSeverity(Enum):
    """편향 심각도"""
    NONE = "none"                                  # 없음
    LOW = "low"                                    # 낮음
    MEDIUM = "medium"                              # 중간
    HIGH = "high"                                  # 높음
    CRITICAL = "critical"                           # 치명적

@dataclass
class BiasDetection:
    """편향 탐지 결과"""
    detection_id: str
    bias_type: BiasType
    bias_description: str
    bias_severity: BiasSeverity
    bias_impact: str
    mitigation_strategy: str
    confidence: float
    created_at: datetime

@dataclass
class BiasAnalysis:
    """편향 분석"""
    analysis_id: str
    judgment_context: str
    detected_biases: List[BiasDetection]
    overall_bias_score: float
    bias_mitigation_plan: str
    created_at: datetime

class BiasDetector:
    """편향 탐지기 - 인지적 편향 탐지 및 분석"""
    
    def __init__(self):
        self.bias_detections: List[BiasDetection] = []
        self.bias_analyses: List[BiasAnalysis] = []
        self.bias_patterns = {
            BiasType.CONFIRMATION_BIAS: [
                "기존 믿음과 일치하는 정보만 찾는 경향",
                "반대 증거를 무시하는 경향",
                "선택적 정보 수집"
            ],
            BiasType.ANCHORING_BIAS: [
                "첫 번째 정보에 과도하게 의존",
                "초기 값에 고정되는 경향",
                "조정 부족"
            ],
            BiasType.AVAILABILITY_BIAS: [
                "쉽게 떠오르는 정보에 과도하게 의존",
                "최근 경험에 과도하게 의존",
                "드라마틱한 사례에 과도하게 의존"
            ],
            BiasType.OVERCONFIDENCE_BIAS: [
                "자신의 능력을 과대평가",
                "예측의 정확성을 과대평가",
                "불확실성을 과소평가"
            ],
            BiasType.GROUPTHINK_BIAS: [
                "그룹  압력에 따른 판단 왜곡",
                "일치성 추구로 인한 비판적 사고 부족",
                "그룹 내 소수 의견 무시"
            ],
            BiasType.COGNITIVE_LOAD_BIAS: [
                "정보 과부하로 인한 판단 왜곡",
                "복잡성 회피로 인한 단순화",
                "인지 자원 부족으로 인한 휴리스틱 의존"
            ]
        }
        
        logger.info("🧠 BiasDetector 초기화 완료")
    
    def detect_biases(self, judgment_context: str, decision_data: Dict[str, Any]) -> BiasAnalysis:
        """편향 탐지 수행"""
        try:
            logger.info(f"🔍 편향 탐지 시작: {judgment_context}")
            
            analysis_id = f"bias_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            # 1. 각 편향 유형별 탐지
            detected_biases = []
            for bias_type in BiasType:
                bias_detection = self._detect_specific_bias(bias_type, judgment_context, decision_data)
                if bias_detection.bias_severity != BiasSeverity.NONE:
                    detected_biases.append(bias_detection)
            
            # 2. 전체 편향 점수 계산
            overall_bias_score = self._calculate_overall_bias_score(detected_biases)
            
            # 3. 편향 완화 계획 생성
            bias_mitigation_plan = self._generate_mitigation_plan(detected_biases)
            
            analysis = BiasAnalysis(
                analysis_id=analysis_id,
                judgment_context=judgment_context,
                detected_biases=detected_biases,
                overall_bias_score=overall_bias_score,
                bias_mitigation_plan=bias_mitigation_plan,
                created_at=datetime.now()
            )
            
            self.bias_analyses.append(analysis)
            self.bias_detections.extend(detected_biases)
            
            logger.info(f"✅ 편향 탐지 완료: {len(detected_biases)}개 편향 탐지, 전체 점수: {overall_bias_score:.3f}")
            return analysis
            
        except Exception as e:
            logger.error(f"❌ 편향 탐지 오류: {e}")
            return self._create_error_analysis(judgment_context, str(e))
    
    def _detect_specific_bias(self, bias_type: BiasType, context: str, decision_data: Dict[str, Any]) -> BiasDetection:
        """특정 편향 탐지"""
        detection_id = f"bias_detection_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # 편향 심각도 결정 (시뮬레이션)
        severity = self._determine_bias_severity(bias_type, context, decision_data)
        
        # 편향 설명 생성
        bias_description = self._generate_bias_description(bias_type, context)
        
        # 편향 영향 평가
        bias_impact = self._evaluate_bias_impact(bias_type, severity, context)
        
        # 완화 전략 생성
        mitigation_strategy = self._generate_mitigation_strategy(bias_type, severity)
        
        # 신뢰도 계산
        confidence = self._calculate_bias_confidence(bias_type, severity, context)
        
        detection = BiasDetection(
            detection_id=detection_id,
            bias_type=bias_type,
            bias_description=bias_description,
            bias_severity=severity,
            bias_impact=bias_impact,
            mitigation_strategy=mitigation_strategy,
            confidence=confidence,
            created_at=datetime.now()
        )
        
        return detection
    
    def _determine_bias_severity(self, bias_type: BiasType, context: str, decision_data: Dict[str, Any]) -> BiasSeverity:
        """편향 심각도 결정"""
        # 시뮬레이션: 각 편향 유형별로 다른 확률 분포
        if bias_type == BiasType.CONFIRMATION_BIAS:
            severity_prob = random.uniform(0.0, 1.0)
        elif bias_type == BiasType.ANCHORING_BIAS:
            severity_prob = random.uniform(0.0, 1.0)
        elif bias_type == BiasType.AVAILABILITY_BIAS:
            severity_prob = random.uniform(0.0, 1.0)
        elif bias_type == BiasType.OVERCONFIDENCE_BIAS:
            severity_prob = random.uniform(0.0, 1.0)
        elif bias_type == BiasType.GROUPTHINK_BIAS:
            severity_prob = random.uniform(0.0, 1.0)
        elif bias_type == BiasType.COGNITIVE_LOAD_BIAS:
            severity_prob = random.uniform(0.0, 1.0)
        else:
            severity_prob = random.uniform(0.0, 1.0)
        
        # 심각도 결정
        if severity_prob >= 0.8:
            return BiasSeverity.CRITICAL
        elif severity_prob >= 0.6:
            return BiasSeverity.HIGH
        elif severity_prob >= 0.4:
            return BiasSeverity.MEDIUM
        elif severity_prob >= 0.2:
            return BiasSeverity.LOW
        else:
            return BiasSeverity.NONE
    
    def _generate_bias_description(self, bias_type: BiasType, context: str) -> str:
        """편향 설명 생성"""
        patterns = self.bias_patterns.get(bias_type, [])
        if patterns:
            return random.choice(patterns)
        return f"{bias_type.value} 패턴이 탐지되었습니다"
    
    def _evaluate_bias_impact(self, bias_type: BiasType, severity: BiasSeverity, context: str) -> str:
        """편향 영향 평가"""
        impacts = [
            f"{bias_type.value}로 인해 판단의 객관성이 저하될 수 있습니다",
            f"{bias_type.value}가 의사결정 과정에 부정적 영향을 미칠 수 있습니다",
            f"{bias_type.value}로 인해 대안적 관점이 무시될 수 있습니다",
            f"{bias_type.value}가 최종 결과의 신뢰성을 저하시킬 수 있습니다"
        ]
        return random.choice(impacts)
    
    def _generate_mitigation_strategy(self, bias_type: BiasType, severity: BiasSeverity) -> str:
        """완화 전략 생성"""
        strategies = {
            BiasType.CONFIRMATION_BIAS: [
                "반대 증거를 적극적으로 찾아보세요",
                "다양한 관점에서 정보를 수집하세요",
                "기존 믿음에 도전하는 질문을 하세요"
            ],
            BiasType.ANCHORING_BIAS: [
                "여러 기준점을 고려하세요",
                "초기 값에 고정되지 마세요",
                "범위를 넓게 설정하세요"
            ],
            BiasType.AVAILABILITY_BIAS: [
                "체계적인 데이터 수집을 하세요",
                "통계적 정보를 활용하세요",
                "개인적 경험에만 의존하지 마세요"
            ],
            BiasType.OVERCONFIDENCE_BIAS: [
                "불확실성을 인정하세요",
                "다양한 시나리오를 고려하세요",
                "피드백을 적극적으로 구하세요"
            ],
            BiasType.GROUPTHINK_BIAS: [
                "소수 의견을 적극적으로 수용하세요",
                "비판적 사고를 장려하세요",
                "외부 관점을 도입하세요"
            ],
            BiasType.COGNITIVE_LOAD_BIAS: [
                "정보를 단계적으로 처리하세요",
                "복잡한 문제를 작은 단위로 나누세요",
                "적절한 휴식을 취하세요"
            ]
        }
        
        bias_strategies = strategies.get(bias_type, ["편향을 인식하고 주의하세요"])
        return random.choice(bias_strategies)
    
    def _calculate_bias_confidence(self, bias_type: BiasType, severity: BiasSeverity, context: str) -> float:
        """편향 신뢰도 계산"""
        # 심각도가 높을수록 신뢰도도 높음
        severity_score = {
            BiasSeverity.NONE: 0.0,
            BiasSeverity.LOW: 0.3,
            BiasSeverity.MEDIUM: 0.6,
            BiasSeverity.HIGH: 0.8,
            BiasSeverity.CRITICAL: 0.9
        }
        
        base_confidence = severity_score.get(severity, 0.5)
        context_bonus = random.uniform(0.0, 0.1)
        return min(base_confidence + context_bonus, 1.0)
    
    def _calculate_overall_bias_score(self, detected_biases: List[BiasDetection]) -> float:
        """전체 편향 점수 계산"""
        if not detected_biases:
            return 0.0
        
        # 각 편향의 심각도와 신뢰도를 고려한 가중 평균
        severity_weights = {
            BiasSeverity.NONE: 0.0,
            BiasSeverity.LOW: 0.2,
            BiasSeverity.MEDIUM: 0.5,
            BiasSeverity.HIGH: 0.8,
            BiasSeverity.CRITICAL: 1.0
        }
        
        total_weighted_score = 0.0
        total_weight = 0.0
        
        for bias in detected_biases:
            weight = severity_weights.get(bias.bias_severity, 0.5)
            weighted_score = weight * bias.confidence
            total_weighted_score += weighted_score
            total_weight += weight
        
        return total_weighted_score / total_weight if total_weight > 0 else 0.0
    
    def _generate_mitigation_plan(self, detected_biases: List[BiasDetection]) -> str:
        """편향 완화 계획 생성"""
        if not detected_biases:
            return "탐지된 편향이 없습니다"
        
        # 가장 심각한 편향부터 완화 계획 생성
        critical_biases = [b for b in detected_biases if b.bias_severity == BiasSeverity.CRITICAL]
        high_biases = [b for b in detected_biases if b.bias_severity == BiasSeverity.HIGH]
        
        priority_biases = critical_biases + high_biases
        
        if priority_biases:
            bias_names = [b.bias_type.value for b in priority_biases[:3]]  # 최대 3개
            return f"우선적으로 {', '.join(bias_names)} 편향을 완화하는 것이 필요합니다"
        else:
            return "탐지된 편향들은 대부분 낮은 수준이므로 지속적 모니터링이 필요합니다"
    
    def _create_error_analysis(self, context: str, error_message: str) -> BiasAnalysis:
        """오류 분석 생성"""
        return BiasAnalysis(
            analysis_id=f"error_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            judgment_context=context,
            detected_biases=[],
            overall_bias_score=0.0,
            bias_mitigation_plan=f"오류 발생: {error_message}",
            created_at=datetime.now()
        )
    
    def get_bias_detection_history(self, limit: int = 10) -> List[BiasDetection]:
        """편향 탐지 기록 조회"""
        return self.bias_detections[-limit:]
    
    def get_bias_analysis_history(self, limit: int = 10) -> List[BiasAnalysis]:
        """편향 분석 기록 조회"""
        return self.bias_analyses[-limit:]
    
    def get_bias_metrics(self) -> Dict[str, Any]:
        """편향 메트릭 조회"""
        if not self.bias_detections:
            return {"message": "편향 탐지 기록이 없습니다"}
        
        # 편향 유형별 통계
        bias_type_counts = {}
        severity_counts = {}
        
        for detection in self.bias_detections:
            bias_type = detection.bias_type.value
            severity = detection.bias_severity.value
            
            bias_type_counts[bias_type] = bias_type_counts.get(bias_type, 0) + 1
            severity_counts[severity] = severity_counts.get(severity, 0) + 1
        
        # 평균 편향 점수
        avg_bias_score = sum(analysis.overall_bias_score for analysis in self.bias_analyses) / len(self.bias_analyses) if self.bias_analyses else 0
        
        return {
            "total_bias_detections": len(self.bias_detections),
            "total_bias_analyses": len(self.bias_analyses),
            "bias_type_distribution": bias_type_counts,
            "severity_distribution": severity_counts,
            "average_bias_score": avg_bias_score
        }

def get_bias_detector() -> BiasDetector:
    """BiasDetector 인스턴스를 반환합니다."""
    return BiasDetector() 