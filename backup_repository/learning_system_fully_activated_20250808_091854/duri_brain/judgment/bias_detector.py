#!/usr/bin/env python3
"""
DuRi 편향 탐지기 - 간소화된 버전
함수 depth 2단계 제한, 조건-매핑 방식 적용
"""

import logging
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from enum import Enum
from datetime import datetime

logger = logging.getLogger(__name__)

class BiasType(Enum):
    """편향 유형"""
    CONFIRMATION_BIAS = "confirmation_bias"
    ANCHORING_BIAS = "anchoring_bias"
    AVAILABILITY_BIAS = "availability_bias"
    OVERCONFIDENCE_BIAS = "overconfidence_bias"
    GROUPTHINK_BIAS = "groupthink_bias"
    COGNITIVE_LOAD_BIAS = "cognitive_load_bias"

class BiasSeverity(Enum):
    """편향 심각도"""
    NONE = "none"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

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
    """편향 탐지기 - 간소화된 버전"""
    
    def __init__(self):
        self.bias_detections = []
        self.bias_analyses = []
        
        # 편향 패턴 (조건-매핑 방식)
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
                "그룹 압력에 따른 판단 왜곡",
                "일치성 추구로 인한 비판적 사고 부족",
                "그룹 내 소수 의견 무시"
            ],
            BiasType.COGNITIVE_LOAD_BIAS: [
                "정보 과부하로 인한 판단 왜곡",
                "복잡성 회피로 인한 단순화",
                "인지 자원 부족으로 인한 휴리스틱 의존"
            ]
        }
        
        logger.info("편향 탐지기 초기화 완료")
    
    def detect_biases(self, judgment_context: str, decision_data: Dict[str, Any]) -> BiasAnalysis:
        """편향 탐지 수행"""
        try:
            detected_biases = []
            
            # 각 편향 유형에 대해 탐지 수행
            for bias_type in BiasType:
                bias_detection = self._detect_specific_bias(bias_type, judgment_context, decision_data)
                if bias_detection.bias_severity != BiasSeverity.NONE:
                    detected_biases.append(bias_detection)
            
            # 전체 편향 점수 계산
            overall_bias_score = self._calculate_overall_bias_score(detected_biases)
            
            # 편향 완화 계획 생성
            bias_mitigation_plan = self._generate_mitigation_plan(detected_biases)
            
            analysis = BiasAnalysis(
                analysis_id=f"analysis_{datetime.now().timestamp()}",
                judgment_context=judgment_context,
                detected_biases=detected_biases,
                overall_bias_score=overall_bias_score,
                bias_mitigation_plan=bias_mitigation_plan,
                created_at=datetime.now()
            )
            
            self.bias_analyses.append(analysis)
            
            logger.info(f"편향 탐지 완료: {len(detected_biases)}개 편향 발견")
            
            return analysis
            
        except Exception as e:
            logger.error(f"편향 탐지 오류: {e}")
            return self._create_error_analysis(judgment_context, str(e))
    
    def _detect_specific_bias(self, bias_type: BiasType, context: str, decision_data: Dict[str, Any]) -> BiasDetection:
        """특정 편향 탐지"""
        # 간소화된 편향 탐지 로직
        bias_indicators = self.bias_patterns.get(bias_type, [])
        
        # 컨텍스트에서 편향 지표 확인
        bias_count = sum(1 for indicator in bias_indicators if indicator in context)
        
        # 편향 심각도 결정
        severity = self._determine_bias_severity(bias_type, context, decision_data)
        
        if severity == BiasSeverity.NONE:
            return BiasDetection(
                detection_id=f"detection_{datetime.now().timestamp()}",
                bias_type=bias_type,
                bias_description="편향 없음",
                bias_severity=BiasSeverity.NONE,
                bias_impact="영향 없음",
                mitigation_strategy="불필요",
                confidence=0.0,
                created_at=datetime.now()
            )
        
        # 편향 설명 생성
        bias_description = self._generate_bias_description(bias_type, context)
        
        # 편향 영향 평가
        bias_impact = self._evaluate_bias_impact(bias_type, severity, context)
        
        # 완화 전략 생성
        mitigation_strategy = self._generate_mitigation_strategy(bias_type, severity)
        
        # 신뢰도 계산
        confidence = self._calculate_bias_confidence(bias_type, severity, context)
        
        detection = BiasDetection(
            detection_id=f"detection_{datetime.now().timestamp()}",
            bias_type=bias_type,
            bias_description=bias_description,
            bias_severity=severity,
            bias_impact=bias_impact,
            mitigation_strategy=mitigation_strategy,
            confidence=confidence,
            created_at=datetime.now()
        )
        
        self.bias_detections.append(detection)
        
        return detection
    
    def _determine_bias_severity(self, bias_type: BiasType, context: str, decision_data: Dict[str, Any]) -> BiasSeverity:
        """편향 심각도 결정"""
        # 간소화된 심각도 결정 로직
        bias_indicators = self.bias_patterns.get(bias_type, [])
        bias_count = sum(1 for indicator in bias_indicators if indicator in context)
        
        # 조건-매핑 방식으로 심각도 결정
        severity_mapping = {
            0: BiasSeverity.NONE,
            1: BiasSeverity.LOW,
            2: BiasSeverity.MEDIUM,
            3: BiasSeverity.HIGH,
            4: BiasSeverity.CRITICAL
        }
        
        return severity_mapping.get(bias_count, BiasSeverity.NONE)
    
    def _generate_bias_description(self, bias_type: BiasType, context: str) -> str:
        """편향 설명 생성"""
        descriptions = {
            BiasType.CONFIRMATION_BIAS: "확인 편향이 감지되었습니다.",
            BiasType.ANCHORING_BIAS: "앵커링 편향이 감지되었습니다.",
            BiasType.AVAILABILITY_BIAS: "가용성 편향이 감지되었습니다.",
            BiasType.OVERCONFIDENCE_BIAS: "과신 편향이 감지되었습니다.",
            BiasType.GROUPTHINK_BIAS: "그룹싱크 편향이 감지되었습니다.",
            BiasType.COGNITIVE_LOAD_BIAS: "인지 부하 편향이 감지되었습니다."
        }
        
        return descriptions.get(bias_type, "알 수 없는 편향이 감지되었습니다.")
    
    def _evaluate_bias_impact(self, bias_type: BiasType, severity: BiasSeverity, context: str) -> str:
        """편향 영향 평가"""
        if severity == BiasSeverity.NONE:
            return "영향 없음"
        
        impact_levels = {
            BiasSeverity.LOW: "낮은 영향",
            BiasSeverity.MEDIUM: "중간 영향",
            BiasSeverity.HIGH: "높은 영향",
            BiasSeverity.CRITICAL: "치명적 영향"
        }
        
        return impact_levels.get(severity, "알 수 없는 영향")
    
    def _generate_mitigation_strategy(self, bias_type: BiasType, severity: BiasSeverity) -> str:
        """완화 전략 생성"""
        strategies = {
            BiasType.CONFIRMATION_BIAS: "반대 관점을 고려하세요.",
            BiasType.ANCHORING_BIAS: "다양한 기준점을 고려하세요.",
            BiasType.AVAILABILITY_BIAS: "체계적인 정보 수집을 하세요.",
            BiasType.OVERCONFIDENCE_BIAS: "불확실성을 인정하세요.",
            BiasType.GROUPTHINK_BIAS: "독립적인 판단을 하세요.",
            BiasType.COGNITIVE_LOAD_BIAS: "정보를 단계적으로 처리하세요."
        }
        
        return strategies.get(bias_type, "편향을 인식하고 객관적으로 판단하세요.")
    
    def _calculate_bias_confidence(self, bias_type: BiasType, severity: BiasSeverity, context: str) -> float:
        """편향 신뢰도 계산"""
        # 간소화된 신뢰도 계산
        severity_scores = {
            BiasSeverity.NONE: 0.0,
            BiasSeverity.LOW: 0.3,
            BiasSeverity.MEDIUM: 0.6,
            BiasSeverity.HIGH: 0.8,
            BiasSeverity.CRITICAL: 0.9
        }
        
        return severity_scores.get(severity, 0.0)
    
    def _calculate_overall_bias_score(self, detected_biases: List[BiasDetection]) -> float:
        """전체 편향 점수 계산"""
        if not detected_biases:
            return 0.0
        
        # 편향 심각도에 따른 가중 평균
        severity_weights = {
            BiasSeverity.LOW: 0.2,
            BiasSeverity.MEDIUM: 0.5,
            BiasSeverity.HIGH: 0.8,
            BiasSeverity.CRITICAL: 1.0
        }
        
        total_score = 0.0
        total_weight = 0.0
        
        for bias in detected_biases:
            weight = severity_weights.get(bias.bias_severity, 0.0)
            total_score += bias.confidence * weight
            total_weight += weight
        
        return total_score / max(total_weight, 1.0)
    
    def _generate_mitigation_plan(self, detected_biases: List[BiasDetection]) -> str:
        """완화 계획 생성"""
        if not detected_biases:
            return "편향이 감지되지 않았습니다."
        
        strategies = [bias.mitigation_strategy for bias in detected_biases]
        return " | ".join(strategies)
    
    def _create_error_analysis(self, context: str, error_message: str) -> BiasAnalysis:
        """오류 분석 생성"""
        return BiasAnalysis(
            analysis_id=f"error_analysis_{datetime.now().timestamp()}",
            judgment_context=context,
            detected_biases=[],
            overall_bias_score=0.0,
            bias_mitigation_plan=f"오류 발생: {error_message}",
            created_at=datetime.now()
        )
    
    def get_bias_detection_history(self, limit: int = 10) -> List[BiasDetection]:
        """편향 탐지 히스토리 반환"""
        return self.bias_detections[-limit:]
    
    def get_bias_analysis_history(self, limit: int = 10) -> List[BiasAnalysis]:
        """편향 분석 히스토리 반환"""
        return self.bias_analyses[-limit:]
    
    def get_bias_metrics(self) -> Dict[str, Any]:
        """편향 지표 반환"""
        total_detections = len(self.bias_detections)
        total_analyses = len(self.bias_analyses)
        
        if total_analyses == 0:
            return {
                "total_detections": 0,
                "total_analyses": 0,
                "average_bias_score": 0.0,
                "most_common_bias": "none"
            }
        
        # 평균 편향 점수
        average_bias_score = sum(analysis.overall_bias_score for analysis in self.bias_analyses) / total_analyses
        
        # 가장 흔한 편향
        bias_counts = {}
        for detection in self.bias_detections:
            bias_type = detection.bias_type.value
            bias_counts[bias_type] = bias_counts.get(bias_type, 0) + 1
        
        most_common_bias = max(bias_counts.items(), key=lambda x: x[1])[0] if bias_counts else "none"
        
        return {
            "total_detections": total_detections,
            "total_analyses": total_analyses,
            "average_bias_score": average_bias_score,
            "most_common_bias": most_common_bias
        } 
 
 