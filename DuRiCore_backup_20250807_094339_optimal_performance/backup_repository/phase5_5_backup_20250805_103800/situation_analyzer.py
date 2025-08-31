#!/usr/bin/env python3
"""
DuRiCore Phase 5 Day 3 - 상황 분석 엔진
입력 데이터 분석, 컨텍스트 추출, 상황 패턴 인식 시스템
"""

import json
import re
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
import logging
import math

logger = logging.getLogger(__name__)

class AnalysisMethod(Enum):
    """분석 방법 열거형"""
    PATTERN_MATCHING = "pattern_matching"
    KEYWORD_ANALYSIS = "keyword_analysis"
    CONTEXT_ANALYSIS = "context_analysis"
    SEMANTIC_ANALYSIS = "semantic_analysis"
    HYBRID_ANALYSIS = "hybrid_analysis"

@dataclass
class ContextElement:
    """컨텍스트 요소"""
    key: str
    value: Any
    importance: float
    category: str
    confidence: float

@dataclass
class SituationPattern:
    """상황 패턴"""
    pattern_type: str
    confidence: float
    keywords: List[str]
    context_indicators: List[str]
    risk_factors: List[str]
    urgency_indicators: List[str]

class SituationAnalyzer:
    """상황 분석 엔진"""
    
    def __init__(self):
        # 패턴 사전
        self.situation_patterns = {
            "learning": {
                "keywords": ["학습", "공부", "배우", "이해", "알다", "깨달", "교육", "훈련"],
                "risk_factors": ["어려움", "복잡", "실패", "오류"],
                "urgency_indicators": ["시험", "마감", "기한", "긴급"]
            },
            "decision": {
                "keywords": ["결정", "선택", "판단", "결론", "의사결정", "정책", "방향"],
                "risk_factors": ["중요", "위험", "실패", "책임"],
                "urgency_indicators": ["긴급", "즉시", "지금", "마감"]
            },
            "problem": {
                "keywords": ["문제", "오류", "실패", "위험", "장애", "고장", "충돌"],
                "risk_factors": ["심각", "위험", "손실", "피해"],
                "urgency_indicators": ["긴급", "즉시", "응급", "비상"]
            },
            "opportunity": {
                "keywords": ["기회", "가능성", "잠재력", "성장", "발전", "혁신", "진보"],
                "risk_factors": ["불확실", "위험", "실패"],
                "urgency_indicators": ["제한", "기한", "경쟁", "시장"]
            },
            "conflict": {
                "keywords": ["갈등", "충돌", "대립", "문제", "분쟁", "의견차이"],
                "risk_factors": ["심각", "위험", "관계악화", "손실"],
                "urgency_indicators": ["긴급", "즉시", "해결", "중재"]
            },
            "routine": {
                "keywords": ["일상", "반복", "정기", "보통", "평범", "일반"],
                "risk_factors": ["지루", "효율성", "개선"],
                "urgency_indicators": ["시간", "일정", "계획"]
            }
        }
        
        # 위험 키워드 사전
        self.risk_keywords = {
            "high": ["위험", "심각", "중요", "치명", "비상", "긴급", "실패", "손실"],
            "medium": ["주의", "관심", "문제", "이슈", "개선", "검토"],
            "low": ["일반", "보통", "평범", "정상", "안전"]
        }
        
        # 긴급도 키워드 사전
        self.urgency_keywords = {
            "high": ["긴급", "즉시", "지금", "바로", "비상", "응급", "마감", "기한"],
            "medium": ["빠른", "신속", "조속", "가능한", "곧"],
            "low": ["나중", "여유", "천천", "차근차근"]
        }
        
        # 복잡도 지표
        self.complexity_indicators = {
            "high": ["복잡", "다양", "많은", "여러", "다중", "통합", "종합"],
            "medium": ["일반", "보통", "평균", "적당"],
            "low": ["단순", "간단", "기본", "일차원"]
        }
        
        logger.info("상황 분석 엔진 초기화 완료")
    
    async def analyze_situation(self, input_data: Dict[str, Any], 
                              context: Dict[str, Any]) -> Dict[str, Any]:
        """상황 분석 (주 메서드)"""
        try:
            # 1. 입력 데이터 분석
            data_analysis = await self._analyze_input_data(input_data)
            
            # 2. 컨텍스트 추출
            context_elements = await self._extract_context_elements(context)
            
            # 3. 상황 패턴 인식
            situation_pattern = await self._recognize_situation_pattern(input_data, context)
            
            # 4. 위험도 평가
            risk_level = await self._assess_risk_level(input_data, context)
            
            # 5. 긴급도 평가
            urgency_level = await self._assess_urgency_level(input_data, context)
            
            # 6. 복잡도 계산
            complexity_score = await self._calculate_complexity(input_data, context)
            
            # 7. 신뢰도 계산
            confidence = await self._calculate_analysis_confidence(
                data_analysis, context_elements, situation_pattern
            )
            
            return {
                "situation_type": situation_pattern.pattern_type,
                "context_elements": [elem.key for elem in context_elements],
                "key_factors": await self._identify_key_factors(input_data, context),
                "risk_level": risk_level,
                "urgency_level": urgency_level,
                "complexity_score": complexity_score,
                "confidence": confidence,
                "analysis_method": AnalysisMethod.HYBRID_ANALYSIS.value,
                "pattern_details": {
                    "keywords": situation_pattern.keywords,
                    "context_indicators": situation_pattern.context_indicators,
                    "risk_factors": situation_pattern.risk_factors,
                    "urgency_indicators": situation_pattern.urgency_indicators
                }
            }
            
        except Exception as e:
            logger.error(f"상황 분석 오류: {e}")
            return {
                "situation_type": "error",
                "context_elements": [],
                "key_factors": [],
                "risk_level": 0.5,
                "urgency_level": 0.5,
                "complexity_score": 0.5,
                "confidence": 0.3,
                "analysis_method": "error_fallback",
                "pattern_details": {}
            }
    
    async def _analyze_input_data(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """입력 데이터 분석"""
        try:
            analysis = {
                "data_type": type(input_data).__name__,
                "data_size": len(str(input_data)),
                "key_fields": list(input_data.keys()) if isinstance(input_data, dict) else [],
                "complexity": self._calculate_data_complexity(input_data),
                "quality_score": self._assess_data_quality(input_data),
                "content_analysis": self._analyze_content(input_data)
            }
            
            return analysis
            
        except Exception as e:
            logger.error(f"입력 데이터 분석 오류: {e}")
            return {"error": str(e)}
    
    async def _extract_context_elements(self, context: Dict[str, Any]) -> List[ContextElement]:
        """컨텍스트 요소 추출"""
        try:
            elements = []
            
            for key, value in context.items():
                importance = self._calculate_context_importance(key, value)
                category = self._categorize_context_element(key, value)
                confidence = self._calculate_context_confidence(key, value)
                
                element = ContextElement(
                    key=key,
                    value=value,
                    importance=importance,
                    category=category,
                    confidence=confidence
                )
                
                elements.append(element)
            
            # 중요도 순으로 정렬
            elements.sort(key=lambda x: x.importance, reverse=True)
            
            return elements
            
        except Exception as e:
            logger.error(f"컨텍스트 요소 추출 오류: {e}")
            return []
    
    async def _recognize_situation_pattern(self, input_data: Dict[str, Any], 
                                         context: Dict[str, Any]) -> SituationPattern:
        """상황 패턴 인식"""
        try:
            content = str(input_data) + str(context)
            content_lower = content.lower()
            
            best_pattern = None
            best_score = 0.0
            matched_keywords = []
            context_indicators = []
            risk_factors = []
            urgency_indicators = []
            
            for pattern_name, pattern_info in self.situation_patterns.items():
                # 키워드 매칭
                pattern_keywords = pattern_info["keywords"]
                matched = [kw for kw in pattern_keywords if kw in content_lower]
                
                if matched:
                    score = len(matched) / len(pattern_keywords)
                    
                    if score > best_score:
                        best_score = score
                        best_pattern = pattern_name
                        matched_keywords = matched
                        
                        # 위험 요소 확인
                        risk_keywords = pattern_info["risk_factors"]
                        risk_factors = [kw for kw in risk_keywords if kw in content_lower]
                        
                        # 긴급도 지표 확인
                        urgency_keywords = pattern_info["urgency_indicators"]
                        urgency_indicators = [kw for kw in urgency_keywords if kw in content_lower]
                        
                        # 컨텍스트 지표 확인
                        context_indicators = self._extract_context_indicators(context)
            
            if not best_pattern:
                best_pattern = "general"
                best_score = 0.1
            
            return SituationPattern(
                pattern_type=best_pattern,
                confidence=best_score,
                keywords=matched_keywords,
                context_indicators=context_indicators,
                risk_factors=risk_factors,
                urgency_indicators=urgency_indicators
            )
            
        except Exception as e:
            logger.error(f"상황 패턴 인식 오류: {e}")
            return SituationPattern(
                pattern_type="unknown",
                confidence=0.0,
                keywords=[],
                context_indicators=[],
                risk_factors=[],
                urgency_indicators=[]
            )
    
    async def _assess_risk_level(self, input_data: Dict[str, Any], 
                                context: Dict[str, Any]) -> float:
        """위험도 평가"""
        try:
            risk_score = 0.0
            content = str(input_data) + str(context)
            content_lower = content.lower()
            
            # 컨텍스트 기반 위험도
            if "risk" in context:
                risk_score += float(context["risk"])
            
            if "danger" in context:
                risk_score += float(context["danger"])
            
            # 키워드 기반 위험도
            for risk_level, keywords in self.risk_keywords.items():
                for keyword in keywords:
                    if keyword in content_lower:
                        if risk_level == "high":
                            risk_score += 0.3
                        elif risk_level == "medium":
                            risk_score += 0.2
                        elif risk_level == "low":
                            risk_score += 0.1
            
            # 특정 위험 키워드
            high_risk_words = ["위험", "심각", "중요", "치명", "비상", "긴급", "실패", "손실"]
            for word in high_risk_words:
                if word in content_lower:
                    risk_score += 0.2
            
            return min(1.0, risk_score)
            
        except Exception as e:
            logger.error(f"위험도 평가 오류: {e}")
            return 0.5
    
    async def _assess_urgency_level(self, input_data: Dict[str, Any], 
                                   context: Dict[str, Any]) -> float:
        """긴급도 평가"""
        try:
            urgency_score = 0.0
            content = str(input_data) + str(context)
            content_lower = content.lower()
            
            # 컨텍스트 기반 긴급도
            if "urgency" in context:
                urgency_score += float(context["urgency"])
            
            if "priority" in context:
                priority = context["priority"]
                if priority == "high":
                    urgency_score += 0.4
                elif priority == "medium":
                    urgency_score += 0.2
            
            # 키워드 기반 긴급도
            for urgency_level, keywords in self.urgency_keywords.items():
                for keyword in keywords:
                    if keyword in content_lower:
                        if urgency_level == "high":
                            urgency_score += 0.3
                        elif urgency_level == "medium":
                            urgency_score += 0.2
                        elif urgency_level == "low":
                            urgency_score += 0.1
            
            # 특정 긴급 키워드
            high_urgency_words = ["긴급", "즉시", "지금", "바로", "비상", "응급", "마감", "기한"]
            for word in high_urgency_words:
                if word in content_lower:
                    urgency_score += 0.2
            
            return min(1.0, urgency_score)
            
        except Exception as e:
            logger.error(f"긴급도 평가 오류: {e}")
            return 0.5
    
    async def _calculate_complexity(self, input_data: Dict[str, Any], 
                                   context: Dict[str, Any]) -> float:
        """복잡도 계산"""
        try:
            complexity = 0.0
            content = str(input_data) + str(context)
            content_lower = content.lower()
            
            # 데이터 크기 기반 복잡도
            data_size = len(str(input_data)) + len(str(context))
            complexity += min(0.3, data_size / 1000)
            
            # 요소 개수 기반 복잡도
            element_count = len(input_data) + len(context)
            complexity += min(0.3, element_count / 10)
            
            # 키워드 기반 복잡도
            for complexity_level, keywords in self.complexity_indicators.items():
                for keyword in keywords:
                    if keyword in content_lower:
                        if complexity_level == "high":
                            complexity += 0.2
                        elif complexity_level == "medium":
                            complexity += 0.1
                        elif complexity_level == "low":
                            complexity += 0.05
            
            # 특정 복잡도 지표
            complexity_indicators = ["복잡", "다양", "많은", "여러", "다중", "통합", "종합"]
            for indicator in complexity_indicators:
                if indicator in content_lower:
                    complexity += 0.1
            
            return min(1.0, complexity)
            
        except Exception as e:
            logger.error(f"복잡도 계산 오류: {e}")
            return 0.5
    
    async def _identify_key_factors(self, input_data: Dict[str, Any], 
                                   context: Dict[str, Any]) -> List[str]:
        """핵심 요소 식별"""
        try:
            factors = []
            
            # 컨텍스트 기반 요소
            important_keys = ["importance", "urgency", "risk", "priority", "deadline"]
            for key in important_keys:
                if key in context:
                    factors.append(key)
            
            # 데이터 기반 요소
            if "content" in input_data:
                factors.append("content_analysis")
            
            if "emotion" in context:
                factors.append("emotional_context")
            
            if "memory" in context:
                factors.append("memory_context")
            
            # 패턴 기반 요소
            content = str(input_data) + str(context)
            if "학습" in content or "공부" in content:
                factors.append("learning_context")
            
            if "결정" in content or "선택" in content:
                factors.append("decision_context")
            
            if "문제" in content or "오류" in content:
                factors.append("problem_context")
            
            if "기회" in content or "가능성" in content:
                factors.append("opportunity_context")
            
            return list(set(factors))  # 중복 제거
            
        except Exception as e:
            logger.error(f"핵심 요소 식별 오류: {e}")
            return []
    
    async def _calculate_analysis_confidence(self, data_analysis: Dict[str, Any],
                                           context_elements: List[ContextElement],
                                           situation_pattern: SituationPattern) -> float:
        """분석 신뢰도 계산"""
        try:
            confidence = 0.5  # 기본값
            
            # 데이터 품질 기반 신뢰도
            if "quality_score" in data_analysis:
                confidence += data_analysis["quality_score"] * 0.3
            
            # 컨텍스트 요소 기반 신뢰도
            if context_elements:
                avg_confidence = sum(elem.confidence for elem in context_elements) / len(context_elements)
                confidence += avg_confidence * 0.2
            
            # 패턴 신뢰도
            confidence += situation_pattern.confidence * 0.3
            
            # 요소 개수 기반 신뢰도
            if len(context_elements) > 3:
                confidence += 0.1
            
            return min(1.0, confidence)
            
        except Exception as e:
            logger.error(f"분석 신뢰도 계산 오류: {e}")
            return 0.5
    
    def _calculate_data_complexity(self, data: Any) -> float:
        """데이터 복잡도 계산"""
        try:
            if isinstance(data, dict):
                return min(1.0, len(data) / 10)
            elif isinstance(data, list):
                return min(1.0, len(data) / 20)
            else:
                return 0.1
        except:
            return 0.5
    
    def _assess_data_quality(self, data: Any) -> float:
        """데이터 품질 평가"""
        try:
            if data is None:
                return 0.0
            elif isinstance(data, dict) and len(data) > 0:
                return 0.8
            elif isinstance(data, list) and len(data) > 0:
                return 0.7
            else:
                return 0.5
        except:
            return 0.5
    
    def _analyze_content(self, data: Any) -> Dict[str, Any]:
        """내용 분석"""
        try:
            content = str(data)
            analysis = {
                "length": len(content),
                "word_count": len(content.split()),
                "has_numbers": any(char.isdigit() for char in content),
                "has_special_chars": any(not char.isalnum() and not char.isspace() for char in content)
            }
            return analysis
        except:
            return {}
    
    def _calculate_context_importance(self, key: str, value: Any) -> float:
        """컨텍스트 중요도 계산"""
        try:
            importance = 0.5  # 기본값
            
            # 키 기반 중요도
            important_keys = ["importance", "urgency", "risk", "priority", "deadline"]
            if key.lower() in important_keys:
                importance += 0.3
            
            # 값 기반 중요도
            if isinstance(value, str):
                if value.lower() in ["high", "critical", "urgent", "important"]:
                    importance += 0.2
                elif value.lower() in ["low", "minor", "optional"]:
                    importance -= 0.1
            
            return max(0.0, min(1.0, importance))
        except:
            return 0.5
    
    def _categorize_context_element(self, key: str, value: Any) -> str:
        """컨텍스트 요소 분류"""
        try:
            if key in ["importance", "priority", "urgency"]:
                return "priority"
            elif key in ["risk", "danger", "threat"]:
                return "risk"
            elif key in ["emotion", "mood", "feeling"]:
                return "emotion"
            elif key in ["time", "deadline", "schedule"]:
                return "time"
            elif key in ["memory", "history", "past"]:
                return "memory"
            else:
                return "general"
        except:
            return "general"
    
    def _calculate_context_confidence(self, key: str, value: Any) -> float:
        """컨텍스트 신뢰도 계산"""
        try:
            confidence = 0.7  # 기본값
            
            # 값 타입 기반 신뢰도
            if isinstance(value, (int, float)):
                confidence += 0.2
            elif isinstance(value, str):
                confidence += 0.1
            elif isinstance(value, dict):
                confidence += 0.1
            
            return min(1.0, confidence)
        except:
            return 0.5
    
    def _extract_context_indicators(self, context: Dict[str, Any]) -> List[str]:
        """컨텍스트 지표 추출"""
        try:
            indicators = []
            
            for key, value in context.items():
                if isinstance(value, str):
                    if value.lower() in ["high", "critical", "urgent"]:
                        indicators.append(f"{key}:high_priority")
                    elif value.lower() in ["low", "minor", "optional"]:
                        indicators.append(f"{key}:low_priority")
            
            return indicators
        except:
            return []

# 테스트 함수
async def test_situation_analyzer():
    """상황 분석 엔진 테스트"""
    print("=== DuRiCore Phase 5 Day 3 - 상황 분석 엔진 테스트 ===")
    
    # 분석기 초기화
    analyzer = SituationAnalyzer()
    
    # 테스트 케이스들
    test_cases = [
        {
            "input": {
                "content": "중요한 프로젝트에서 위험한 상황이 발생했습니다. 긴급한 의사결정이 필요합니다.",
                "priority": "high",
                "context": "business_critical"
            },
            "context": {
                "risk_level": 0.8,
                "urgency": 0.9,
                "importance": "critical",
                "stakeholders": ["management", "team", "clients"]
            }
        },
        {
            "input": {
                "content": "새로운 머신러닝 알고리즘을 학습하고 있습니다. 매우 흥미로운 내용입니다.",
                "topic": "machine_learning",
                "difficulty": "intermediate"
            },
            "context": {
                "learning_type": "self_study",
                "progress": 0.6,
                "motivation": "high"
            }
        },
        {
            "input": {
                "content": "일상적인 업무를 처리하고 있습니다. 특별한 이슈는 없습니다.",
                "task_type": "routine",
                "complexity": "low"
            },
            "context": {
                "workload": "normal",
                "stress_level": "low",
                "deadline": "flexible"
            }
        }
    ]
    
    # 각 테스트 케이스 분석
    for i, test_case in enumerate(test_cases):
        print(f"\n테스트 케이스 {i+1}:")
        print(f"입력: {test_case['input']['content'][:50]}...")
        
        result = await analyzer.analyze_situation(test_case["input"], test_case["context"])
        
        print(f"상황 타입: {result['situation_type']}")
        print(f"위험도: {result['risk_level']:.3f}")
        print(f"긴급도: {result['urgency_level']:.3f}")
        print(f"복잡도: {result['complexity_score']:.3f}")
        print(f"신뢰도: {result['confidence']:.3f}")
        print(f"핵심 요소: {result['key_factors']}")
        print(f"컨텍스트 요소: {result['context_elements']}")
    
    print("\n=== 테스트 완료 ===")

if __name__ == "__main__":
    import asyncio
    asyncio.run(test_situation_analyzer()) 