#!/usr/bin/env python3
"""
DuRiCore - 자기 성찰 시스템
스스로 판단을 평가하고 개선하는 시스템
"""

import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime
from enum import Enum

logger = logging.getLogger(__name__)

class CritiqueLevel(Enum):
    """성찰 수준"""
    NONE = "none"
    BASIC = "basic"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"

class BiasType(Enum):
    """편향 유형"""
    NONE = "none"
    EMOTIONAL = "emotional"
    CONFIRMATION = "confirmation"
    ANCHORING = "anchoring"
    AVAILABILITY = "availability"
    COGNITIVE = "cognitive"

@dataclass
class SelfCritique:
    """자기 성찰 결과"""
    critique_level: CritiqueLevel
    judgment_quality: float  # 0.0 ~ 1.0
    bias_detected: bool
    bias_type: BiasType
    bias_strength: float  # 0.0 ~ 1.0
    improvement_areas: List[str]
    self_feedback: str
    confidence: float  # 0.0 ~ 1.0
    reasoning_process: str
    alternative_perspectives: List[str]
    learning_points: List[str]

class SelfCritiqueSystem:
    """자기 성찰 시스템"""
    
    def __init__(self):
        self.critique_history = []
        self.bias_patterns = {}
        self.improvement_tracking = {}
        
        # 편향 감지 패턴
        self.bias_indicators = {
            BiasType.EMOTIONAL: [
                "감정적", "화나다", "기쁘다", "슬프다", "분노", "기쁨", "슬픔",
                "매우", "정말", "완전", "절대", "전혀", "아무것도"
            ],
            BiasType.CONFIRMATION: [
                "그렇다", "맞다", "옳다", "당연하다", "분명하다", "확실하다",
                "이미", "원래", "처음부터", "당연히"
            ],
            BiasType.ANCHORING: [
                "첫번째", "처음", "시작", "기준", "기준점", "기준이",
                "비교", "상대적", "절대적"
            ],
            BiasType.AVAILABILITY: [
                "최근", "방금", "지금", "현재", "이번", "이번에",
                "기억", "생각", "느낌"
            ],
            BiasType.COGNITIVE: [
                "복잡", "어렵다", "이해", "알다", "모르다", "생각",
                "논리", "이성", "분석"
            ]
        }
        
        # 개선 영역 키워드
        self.improvement_keywords = {
            "감정적 편향": ["감정", "기분", "느낌", "화", "기쁨", "슬픔"],
            "정보 부족": ["모르다", "불확실", "애매", "모호", "불분명"],
            "논리적 오류": ["논리", "이유", "근거", "증거", "분석"],
            "경험 부족": ["처음", "새롭다", "익숙하지", "경험", "시도"],
            "편향적 사고": ["편향", "고정관념", "선입견", "편견", "고정"]
        }
        
        logger.info("자기 성찰 시스템 초기화 완료")
    
    def critique_judgment(self, judgment_data: Dict[str, Any], emotion_data: Dict[str, Any], 
                         context_data: Dict[str, Any]) -> SelfCritique:
        """판단에 대한 자기 성찰 수행"""
        try:
            # 1. 성찰 수준 결정
            critique_level = self._determine_critique_level(judgment_data, emotion_data)
            
            # 2. 판단 품질 평가
            judgment_quality = self._evaluate_judgment_quality(judgment_data, emotion_data)
            
            # 3. 편향 감지
            bias_analysis = self._detect_bias(judgment_data, emotion_data, context_data)
            
            # 4. 개선점 식별
            improvement_areas = self._identify_improvement_areas(judgment_data, judgment_quality, bias_analysis)
            
            # 5. 자기 피드백 생성
            self_feedback = self._generate_self_feedback(judgment_quality, bias_analysis, improvement_areas)
            
            # 6. 신뢰도 계산
            confidence = self._calculate_critique_confidence(judgment_quality, bias_analysis)
            
            # 7. 추론 과정 분석
            reasoning_process = self._analyze_reasoning_process(judgment_data)
            
            # 8. 대안적 관점 생성
            alternative_perspectives = self._generate_alternative_perspectives(judgment_data, bias_analysis)
            
            # 9. 학습 포인트 추출
            learning_points = self._extract_learning_points(judgment_data, bias_analysis, improvement_areas)
            
            # 성찰 결과 생성
            critique_result = SelfCritique(
                critique_level=critique_level,
                judgment_quality=judgment_quality,
                bias_detected=bias_analysis["bias_detected"],
                bias_type=bias_analysis["bias_type"],
                bias_strength=bias_analysis["bias_strength"],
                improvement_areas=improvement_areas,
                self_feedback=self_feedback,
                confidence=confidence,
                reasoning_process=reasoning_process,
                alternative_perspectives=alternative_perspectives,
                learning_points=learning_points
            )
            
            # 성찰 히스토리 저장
            self._store_critique_history(critique_result, judgment_data)
            
            return critique_result
            
        except Exception as e:
            logger.error(f"자기 성찰 오류: {e}")
            return self._create_default_critique()
    
    def _determine_critique_level(self, judgment_data: Dict[str, Any], emotion_data: Dict[str, Any]) -> CritiqueLevel:
        """성찰 수준 결정"""
        # 판단 복잡도 평가
        complexity_score = self._assess_complexity(judgment_data)
        
        # 감정 강도 평가
        emotion_intensity = emotion_data.get("intensity", 0.0) if emotion_data else 0.0
        
        # 신뢰도 평가
        confidence = judgment_data.get("judgment_confidence", 0.0)
        
        # 종합 점수 계산
        total_score = (complexity_score + emotion_intensity + confidence) / 3.0
        
        if total_score > 0.8:
            return CritiqueLevel.EXPERT
        elif total_score > 0.6:
            return CritiqueLevel.ADVANCED
        elif total_score > 0.4:
            return CritiqueLevel.INTERMEDIATE
        elif total_score > 0.2:
            return CritiqueLevel.BASIC
        else:
            return CritiqueLevel.NONE
    
    def _evaluate_judgment_quality(self, judgment_data: Dict[str, Any], emotion_data: Dict[str, Any]) -> float:
        """판단 품질 평가"""
        quality_score = 0.5  # 기본 점수
        
        # 신뢰도 기반 평가
        confidence = judgment_data.get("judgment_confidence", 0.0)
        quality_score += confidence * 0.3
        
        # 추론 과정 평가
        reasoning = judgment_data.get("reasoning_process", "")
        if reasoning and len(reasoning) > 10:
            quality_score += 0.2
        
        # 감정 영향 평가
        if emotion_data:
            emotion_intensity = emotion_data.get("intensity", 0.0)
            # 감정이 너무 강하면 품질 저하
            if emotion_intensity > 0.8:
                quality_score -= 0.2
            elif emotion_intensity < 0.3:
                quality_score += 0.1
        
        # 판단 일관성 평가
        consistency = self._evaluate_consistency(judgment_data)
        quality_score += consistency * 0.2
        
        return max(0.0, min(1.0, quality_score))
    
    def _detect_bias(self, judgment_data: Dict[str, Any], emotion_data: Dict[str, Any], 
                     context_data: Dict[str, Any]) -> Dict[str, Any]:
        """편향 감지"""
        bias_detected = False
        bias_type = BiasType.NONE
        bias_strength = 0.0
        
        judgment_text = str(judgment_data)
        
        # 각 편향 유형별 검사
        for bias_type_enum, indicators in self.bias_indicators.items():
            bias_count = 0
            for indicator in indicators:
                if indicator in judgment_text:
                    bias_count += 1
            
            if bias_count > 0:
                bias_strength_candidate = min(1.0, bias_count / len(indicators))
                if bias_strength_candidate > bias_strength:
                    bias_detected = True
                    bias_type = bias_type_enum
                    bias_strength = bias_strength_candidate
        
        # 감정적 편향 추가 검사
        if emotion_data and emotion_data.get("intensity", 0.0) > 0.7:
            emotional_bias_strength = emotion_data.get("intensity", 0.0)
            if emotional_bias_strength > bias_strength:
                bias_detected = True
                bias_type = BiasType.EMOTIONAL
                bias_strength = emotional_bias_strength
        
        return {
            "bias_detected": bias_detected,
            "bias_type": bias_type,
            "bias_strength": bias_strength
        }
    
    def _identify_improvement_areas(self, judgment_data: Dict[str, Any], quality: float, 
                                   bias_analysis: Dict[str, Any]) -> List[str]:
        """개선점 식별"""
        improvement_areas = []
        
        # 품질 기반 개선점
        if quality < 0.5:
            improvement_areas.append("판단 품질 향상 필요")
        
        if quality < 0.3:
            improvement_areas.append("기본적인 판단 능력 개선 필요")
        
        # 편향 기반 개선점
        if bias_analysis["bias_detected"]:
            bias_type = bias_analysis["bias_type"]
            if bias_type == BiasType.EMOTIONAL:
                improvement_areas.append("감정적 편향 제거 필요")
            elif bias_type == BiasType.CONFIRMATION:
                improvement_areas.append("확인 편향 극복 필요")
            elif bias_type == BiasType.ANCHORING:
                improvement_areas.append("기준점 편향 주의 필요")
            elif bias_type == BiasType.AVAILABILITY:
                improvement_areas.append("가용성 편향 극복 필요")
            elif bias_type == BiasType.COGNITIVE:
                improvement_areas.append("인지적 편향 개선 필요")
        
        # 판단 데이터 분석
        judgment_text = str(judgment_data)
        for area, keywords in self.improvement_keywords.items():
            keyword_count = sum(1 for keyword in keywords if keyword in judgment_text)
            if keyword_count > 2:
                improvement_areas.append(f"{area} 개선 필요")
        
        return list(set(improvement_areas))  # 중복 제거
    
    def _generate_self_feedback(self, quality: float, bias_analysis: Dict[str, Any], 
                               improvement_areas: List[str]) -> str:
        """자기 피드백 생성"""
        feedback_parts = []
        
        # 품질 기반 피드백
        if quality > 0.8:
            feedback_parts.append("판단이 매우 우수합니다.")
        elif quality > 0.6:
            feedback_parts.append("판단이 양호합니다.")
        elif quality > 0.4:
            feedback_parts.append("판단이 보통 수준입니다.")
        else:
            feedback_parts.append("판단 품질을 개선해야 합니다.")
        
        # 편향 기반 피드백
        if bias_analysis["bias_detected"]:
            bias_type = bias_analysis["bias_type"]
            bias_strength = bias_analysis["bias_strength"]
            
            if bias_strength > 0.7:
                feedback_parts.append(f"강한 {bias_type.value} 편향이 감지되었습니다.")
            elif bias_strength > 0.4:
                feedback_parts.append(f"중간 정도의 {bias_type.value} 편향이 있습니다.")
            else:
                feedback_parts.append(f"약간의 {bias_type.value} 편향이 있습니다.")
        
        # 개선점 기반 피드백
        if improvement_areas:
            feedback_parts.append(f"개선이 필요한 영역: {', '.join(improvement_areas)}")
        
        # 종합 피드백
        if not feedback_parts:
            feedback_parts.append("판단이 적절합니다.")
        
        return " ".join(feedback_parts)
    
    def _calculate_critique_confidence(self, quality: float, bias_analysis: Dict[str, Any]) -> float:
        """성찰 신뢰도 계산"""
        confidence = 0.5  # 기본 신뢰도
        
        # 품질 기반 신뢰도
        confidence += quality * 0.3
        
        # 편향 감지 기반 신뢰도
        if bias_analysis["bias_detected"]:
            bias_strength = bias_analysis["bias_strength"]
            # 편향을 잘 감지했다면 신뢰도 증가
            confidence += bias_strength * 0.2
        
        return max(0.0, min(1.0, confidence))
    
    def _analyze_reasoning_process(self, judgment_data: Dict[str, Any]) -> str:
        """추론 과정 분석"""
        reasoning = judgment_data.get("reasoning_process", "")
        
        if not reasoning:
            return "추론 과정이 명확하지 않습니다."
        
        analysis_parts = []
        
        # 추론 과정 길이 분석
        if len(reasoning) < 20:
            analysis_parts.append("추론 과정이 간단합니다.")
        elif len(reasoning) < 50:
            analysis_parts.append("추론 과정이 적절합니다.")
        else:
            analysis_parts.append("추론 과정이 상세합니다.")
        
        # 추론 과정 내용 분석
        if "분석" in reasoning or "고려" in reasoning:
            analysis_parts.append("체계적인 분석이 포함되어 있습니다.")
        
        if "감정" in reasoning or "느낌" in reasoning:
            analysis_parts.append("감정적 요소가 고려되었습니다.")
        
        if "경험" in reasoning or "기억" in reasoning:
            analysis_parts.append("과거 경험이 반영되었습니다.")
        
        return " ".join(analysis_parts) if analysis_parts else "추론 과정이 적절합니다."
    
    def _generate_alternative_perspectives(self, judgment_data: Dict[str, Any], 
                                         bias_analysis: Dict[str, Any]) -> List[str]:
        """대안적 관점 생성"""
        perspectives = []
        
        # 편향에 따른 대안 관점
        if bias_analysis["bias_detected"]:
            bias_type = bias_analysis["bias_type"]
            
            if bias_type == BiasType.EMOTIONAL:
                perspectives.extend([
                    "더 객관적인 관점에서 생각해보기",
                    "감정을 배제하고 논리적으로 분석하기",
                    "다른 사람의 입장에서 바라보기"
                ])
            elif bias_type == BiasType.CONFIRMATION:
                perspectives.extend([
                    "반대 관점도 고려해보기",
                    "다른 가능성도 검토하기",
                    "기존 믿음에 의문을 제기해보기"
                ])
            elif bias_type == BiasType.ANCHORING:
                perspectives.extend([
                    "다른 기준점을 설정해보기",
                    "상대적 관점에서 재평가하기",
                    "절대적 기준 대신 상대적 기준 사용하기"
                ])
        
        # 일반적인 대안 관점
        perspectives.extend([
            "다른 시간대에 다시 생각해보기",
            "더 많은 정보를 수집해보기",
            "전문가의 의견을 참고해보기"
        ])
        
        return perspectives[:5]  # 최대 5개까지만
    
    def _extract_learning_points(self, judgment_data: Dict[str, Any], bias_analysis: Dict[str, Any], 
                                improvement_areas: List[str]) -> List[str]:
        """학습 포인트 추출"""
        learning_points = []
        
        # 편향에서 학습
        if bias_analysis["bias_detected"]:
            bias_type = bias_analysis["bias_type"]
            learning_points.append(f"{bias_type.value} 편향을 인식하고 극복하는 방법 학습")
        
        # 개선점에서 학습
        for area in improvement_areas:
            learning_points.append(f"{area}을 위한 구체적인 방법 학습")
        
        # 판단 품질에서 학습
        quality = judgment_data.get("judgment_confidence", 0.0)
        if quality < 0.5:
            learning_points.append("더 정확한 판단을 위한 정보 수집 방법 학습")
        
        # 일반적인 학습 포인트
        learning_points.extend([
            "다양한 관점에서 사고하는 방법 연습",
            "감정과 논리의 균형 유지 방법 학습",
            "체계적인 분석 방법 습득"
        ])
        
        return learning_points[:5]  # 최대 5개까지만
    
    def _assess_complexity(self, judgment_data: Dict[str, Any]) -> float:
        """복잡도 평가"""
        complexity_score = 0.5  # 기본 복잡도
        
        # 판단 구성 요소 수
        judgment_keys = list(judgment_data.keys())
        if len(judgment_keys) > 5:
            complexity_score += 0.2
        
        # 추론 과정 길이
        reasoning = judgment_data.get("reasoning_process", "")
        if len(reasoning) > 50:
            complexity_score += 0.2
        
        # 신뢰도
        confidence = judgment_data.get("judgment_confidence", 0.0)
        complexity_score += confidence * 0.1
        
        return min(1.0, complexity_score)
    
    def _evaluate_consistency(self, judgment_data: Dict[str, Any]) -> float:
        """일관성 평가"""
        consistency_score = 0.5  # 기본 일관성
        
        # 판단 신뢰도와 일관성의 관계
        confidence = judgment_data.get("judgment_confidence", 0.0)
        if confidence > 0.7:
            consistency_score += 0.3
        
        # 추론 과정의 논리성
        reasoning = judgment_data.get("reasoning_process", "")
        if "분석" in reasoning and "결론" in reasoning:
            consistency_score += 0.2
        
        return min(1.0, consistency_score)
    
    def _store_critique_history(self, critique_result: SelfCritique, judgment_data: Dict[str, Any]):
        """성찰 히스토리 저장"""
        history_entry = {
            "timestamp": datetime.now().isoformat(),
            "critique_level": critique_result.critique_level.value,
            "judgment_quality": critique_result.judgment_quality,
            "bias_detected": critique_result.bias_detected,
            "bias_type": critique_result.bias_type.value,
            "improvement_areas": critique_result.improvement_areas,
            "confidence": critique_result.confidence
        }
        
        self.critique_history.append(history_entry)
        
        # 편향 패턴 추적
        if critique_result.bias_detected:
            bias_type = critique_result.bias_type.value
            if bias_type not in self.bias_patterns:
                self.bias_patterns[bias_type] = 0
            self.bias_patterns[bias_type] += 1
    
    def _create_default_critique(self) -> SelfCritique:
        """기본 성찰 결과 생성"""
        return SelfCritique(
            critique_level=CritiqueLevel.NONE,
            judgment_quality=0.0,
            bias_detected=False,
            bias_type=BiasType.NONE,
            bias_strength=0.0,
            improvement_areas=["기본적인 판단 능력 필요"],
            self_feedback="판단을 평가할 수 없습니다.",
            confidence=0.0,
            reasoning_process="추론 과정을 분석할 수 없습니다.",
            alternative_perspectives=[],
            learning_points=["기본적인 판단 방법 학습 필요"]
        )
    
    def get_critique_statistics(self) -> Dict[str, Any]:
        """성찰 통계"""
        if not self.critique_history:
            return {"total_critiques": 0}
        
        total_critiques = len(self.critique_history)
        avg_quality = sum(h["judgment_quality"] for h in self.critique_history) / total_critiques
        bias_detection_rate = sum(1 for h in self.critique_history if h["bias_detected"]) / total_critiques
        
        return {
            "total_critiques": total_critiques,
            "average_judgment_quality": avg_quality,
            "bias_detection_rate": bias_detection_rate,
            "bias_patterns": self.bias_patterns,
            "most_common_improvement_areas": self._get_most_common_improvements()
        }
    
    def _get_most_common_improvements(self) -> List[str]:
        """가장 흔한 개선점들"""
        improvement_counts = {}
        for entry in self.critique_history:
            for area in entry.get("improvement_areas", []):
                improvement_counts[area] = improvement_counts.get(area, 0) + 1
        
        # 빈도순 정렬
        sorted_improvements = sorted(improvement_counts.items(), key=lambda x: x[1], reverse=True)
        return [area for area, count in sorted_improvements[:5]] 