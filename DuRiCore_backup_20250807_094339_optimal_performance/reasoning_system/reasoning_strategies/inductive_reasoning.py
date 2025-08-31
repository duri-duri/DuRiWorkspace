#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DuRi 추론 시스템 - 귀납적 추론 모듈

귀납적 추론을 담당하는 모듈입니다.
- 패턴 분석 및 일반화
- 통계적 추론
- 확률적 결론 도출
"""

import logging
import asyncio
from typing import Dict, List, Any, Optional, Tuple, Union, Set
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

logger = logging.getLogger(__name__)

class InductiveType(Enum):
    """귀납적 추론 유형"""
    ENUMERATIVE = "enumerative"  # 열거적 귀납
    STATISTICAL = "statistical"  # 통계적 귀납
    ANALOGICAL = "analogical"  # 유추적 귀납
    CAUSAL = "causal"  # 인과적 귀납
    PREDICTIVE = "predictive"  # 예측적 귀납

@dataclass
class InductiveObservation:
    """귀납적 관찰"""
    observation_id: str
    content: str
    frequency: int = 1
    confidence: float = 1.0
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class InductivePattern:
    """귀납적 패턴"""
    pattern_id: str
    pattern_type: str
    observations: List[InductiveObservation]
    strength: float = 1.0
    confidence: float = 1.0
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class InductiveGeneralization:
    """귀납적 일반화"""
    generalization_id: str
    content: str
    supporting_observations: List[InductiveObservation]
    confidence: float = 1.0
    exceptions: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class InductiveAnalysis:
    """귀납적 분석 결과"""
    pattern_strength: float
    generalization_confidence: float
    statistical_significance: float
    patterns: List[InductivePattern] = field(default_factory=list)
    generalizations: List[InductiveGeneralization] = field(default_factory=list)
    issues: List[str] = field(default_factory=list)
    suggestions: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

class InductiveReasoning:
    """귀납적 추론 클래스"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.reasoning_history = []
        self.performance_metrics = {
            'total_reasonings': 0,
            'successful_reasonings': 0,
            'average_pattern_strength': 0.0,
            'average_generalization_confidence': 0.0
        }
        self.logger.info("귀납적 추론기 초기화 완료")
    
    async def perform_inductive_reasoning(self, observations: List[InductiveObservation], 
                                        inductive_type: InductiveType = InductiveType.ENUMERATIVE) -> InductiveAnalysis:
        """귀납적 추론 수행"""
        try:
            start_time = datetime.now()
            self.logger.info(f"귀납적 추론 시작: {inductive_type.value}")
            
            # 패턴 분석
            patterns = self._analyze_patterns(observations, inductive_type)
            
            # 일반화 수행
            generalizations = self._create_generalizations(patterns, inductive_type)
            
            # 분석 수행
            analysis = self._analyze_inductive_reasoning(patterns, generalizations, inductive_type)
            
            # 성능 메트릭 업데이트
            processing_time = (datetime.now() - start_time).total_seconds()
            self._update_performance_metrics(analysis, processing_time)
            
            # 추론 히스토리에 추가
            self.reasoning_history.append({
                'observations': observations,
                'inductive_type': inductive_type,
                'analysis': analysis,
                'processing_time': processing_time,
                'timestamp': datetime.now()
            })
            
            self.logger.info(f"귀납적 추론 완료: {inductive_type.value}, 패턴 강도: {analysis.pattern_strength:.2f}")
            return analysis
            
        except Exception as e:
            self.logger.error(f"귀납적 추론 중 오류 발생: {e}")
            return InductiveAnalysis(
                pattern_strength=0.0,
                generalization_confidence=0.0,
                statistical_significance=0.0,
                issues=[f"오류 발생: {str(e)}"]
            )
    
    def _analyze_patterns(self, observations: List[InductiveObservation], 
                         inductive_type: InductiveType) -> List[InductivePattern]:
        """패턴 분석"""
        patterns = []
        
        try:
            if inductive_type == InductiveType.ENUMERATIVE:
                patterns = self._enumerative_pattern_analysis(observations)
            elif inductive_type == InductiveType.STATISTICAL:
                patterns = self._statistical_pattern_analysis(observations)
            elif inductive_type == InductiveType.ANALOGICAL:
                patterns = self._analogical_pattern_analysis(observations)
            elif inductive_type == InductiveType.CAUSAL:
                patterns = self._causal_pattern_analysis(observations)
            elif inductive_type == InductiveType.PREDICTIVE:
                patterns = self._predictive_pattern_analysis(observations)
            else:
                patterns = self._general_pattern_analysis(observations)
            
            return patterns
            
        except Exception as e:
            self.logger.error(f"패턴 분석 중 오류: {e}")
            return []
    
    def _enumerative_pattern_analysis(self, observations: List[InductiveObservation]) -> List[InductivePattern]:
        """열거적 패턴 분석"""
        patterns = []
        
        try:
            # 관찰 내용별 그룹화
            content_groups = {}
            for observation in observations:
                content = observation.content.lower()
                if content not in content_groups:
                    content_groups[content] = []
                content_groups[content].append(observation)
            
            # 패턴 생성
            for content, group_observations in content_groups.items():
                if len(group_observations) > 1:  # 2개 이상의 관찰이 있어야 패턴으로 간주
                    pattern = InductivePattern(
                        pattern_id=f"enumerative_pattern_{len(patterns)}",
                        pattern_type="enumerative",
                        observations=group_observations,
                        strength=len(group_observations) / len(observations),
                        confidence=min(1.0, len(group_observations) / 10.0)
                    )
                    patterns.append(pattern)
            
            return patterns
            
        except Exception as e:
            self.logger.error(f"열거적 패턴 분석 중 오류: {e}")
            return []
    
    def _statistical_pattern_analysis(self, observations: List[InductiveObservation]) -> List[InductivePattern]:
        """통계적 패턴 분석"""
        patterns = []
        
        try:
            # 통계적 특성 분석
            total_observations = len(observations)
            if total_observations == 0:
                return patterns
            
            # 빈도 분석
            frequency_distribution = {}
            for observation in observations:
                content = observation.content.lower()
                if content not in frequency_distribution:
                    frequency_distribution[content] = 0
                frequency_distribution[content] += observation.frequency
            
            # 통계적 패턴 생성
            for content, frequency in frequency_distribution.items():
                if frequency > 1:  # 2회 이상 나타난 경우만 패턴으로 간주
                    related_observations = [obs for obs in observations if obs.content.lower() == content]
                    pattern = InductivePattern(
                        pattern_id=f"statistical_pattern_{len(patterns)}",
                        pattern_type="statistical",
                        observations=related_observations,
                        strength=frequency / total_observations,
                        confidence=min(1.0, frequency / 20.0)
                    )
                    patterns.append(pattern)
            
            return patterns
            
        except Exception as e:
            self.logger.error(f"통계적 패턴 분석 중 오류: {e}")
            return []
    
    def _analogical_pattern_analysis(self, observations: List[InductiveObservation]) -> List[InductivePattern]:
        """유추적 패턴 분석"""
        patterns = []
        
        try:
            # 유사성 기반 패턴 분석
            similarity_groups = []
            
            for i, obs1 in enumerate(observations):
                for j, obs2 in enumerate(observations[i+1:], i+1):
                    similarity = self._calculate_similarity(obs1, obs2)
                    if similarity > 0.7:  # 유사도가 70% 이상인 경우
                        # 기존 그룹에 추가하거나 새 그룹 생성
                        added_to_group = False
                        for group in similarity_groups:
                            if any(self._calculate_similarity(obs1, group_obs) > 0.7 for group_obs in group):
                                group.extend([obs1, obs2])
                                added_to_group = True
                                break
                        
                        if not added_to_group:
                            similarity_groups.append([obs1, obs2])
            
            # 패턴 생성
            for group in similarity_groups:
                if len(group) > 1:
                    pattern = InductivePattern(
                        pattern_id=f"analogical_pattern_{len(patterns)}",
                        pattern_type="analogical",
                        observations=group,
                        strength=len(group) / len(observations),
                        confidence=min(1.0, len(group) / 10.0)
                    )
                    patterns.append(pattern)
            
            return patterns
            
        except Exception as e:
            self.logger.error(f"유추적 패턴 분석 중 오류: {e}")
            return []
    
    def _causal_pattern_analysis(self, observations: List[InductiveObservation]) -> List[InductivePattern]:
        """인과적 패턴 분석"""
        patterns = []
        
        try:
            # 인과 관계 패턴 분석
            causal_groups = []
            
            # 시간 순서나 논리적 순서를 기반으로 인과 관계 추정
            for i, obs1 in enumerate(observations):
                for j, obs2 in enumerate(observations[i+1:], i+1):
                    if self._is_causally_related(obs1, obs2):
                        causal_groups.append([obs1, obs2])
            
            # 패턴 생성
            for group in causal_groups:
                pattern = InductivePattern(
                    pattern_id=f"causal_pattern_{len(patterns)}",
                    pattern_type="causal",
                    observations=group,
                    strength=len(group) / len(observations),
                    confidence=0.6  # 인과 관계는 일반적으로 중간 정도의 신뢰도
                )
                patterns.append(pattern)
            
            return patterns
            
        except Exception as e:
            self.logger.error(f"인과적 패턴 분석 중 오류: {e}")
            return []
    
    def _predictive_pattern_analysis(self, observations: List[InductiveObservation]) -> List[InductivePattern]:
        """예측적 패턴 분석"""
        patterns = []
        
        try:
            # 예측 가능한 패턴 분석
            predictive_groups = []
            
            # 시계열이나 순차적 패턴 분석
            for i in range(len(observations) - 1):
                current_obs = observations[i]
                next_obs = observations[i + 1]
                
                if self._is_predictive_related(current_obs, next_obs):
                    predictive_groups.append([current_obs, next_obs])
            
            # 패턴 생성
            for group in predictive_groups:
                pattern = InductivePattern(
                    pattern_id=f"predictive_pattern_{len(patterns)}",
                    pattern_type="predictive",
                    observations=group,
                    strength=len(group) / len(observations),
                    confidence=0.5  # 예측은 일반적으로 낮은 신뢰도
                )
                patterns.append(pattern)
            
            return patterns
            
        except Exception as e:
            self.logger.error(f"예측적 패턴 분석 중 오류: {e}")
            return []
    
    def _general_pattern_analysis(self, observations: List[InductiveObservation]) -> List[InductivePattern]:
        """일반 패턴 분석"""
        patterns = []
        
        try:
            # 기본적인 패턴 분석
            if observations:
                pattern = InductivePattern(
                    pattern_id="general_pattern_0",
                    pattern_type="general",
                    observations=observations,
                    strength=1.0,
                    confidence=0.5
                )
                patterns.append(pattern)
            
            return patterns
            
        except Exception as e:
            self.logger.error(f"일반 패턴 분석 중 오류: {e}")
            return []
    
    def _calculate_similarity(self, obs1: InductiveObservation, obs2: InductiveObservation) -> float:
        """유사도 계산"""
        try:
            # 간단한 유사도 계산 (실제로는 더 복잡한 알고리즘이 필요)
            content1 = obs1.content.lower()
            content2 = obs2.content.lower()
            
            # 공통 단어 수 계산
            words1 = set(content1.split())
            words2 = set(content2.split())
            
            if not words1 or not words2:
                return 0.0
            
            intersection = words1.intersection(words2)
            union = words1.union(words2)
            
            return len(intersection) / len(union)
            
        except Exception as e:
            self.logger.error(f"유사도 계산 중 오류: {e}")
            return 0.0
    
    def _is_causally_related(self, obs1: InductiveObservation, obs2: InductiveObservation) -> bool:
        """인과 관계 확인"""
        try:
            # 간단한 인과 관계 확인 (실제로는 더 복잡한 분석이 필요)
            content1 = obs1.content.lower()
            content2 = obs2.content.lower()
            
            # 인과 관계 키워드 확인
            causal_keywords = ['cause', 'effect', 'result', 'because', 'therefore', 'leads to']
            
            for keyword in causal_keywords:
                if keyword in content1 or keyword in content2:
                    return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"인과 관계 확인 중 오류: {e}")
            return False
    
    def _is_predictive_related(self, obs1: InductiveObservation, obs2: InductiveObservation) -> bool:
        """예측 관계 확인"""
        try:
            # 간단한 예측 관계 확인
            content1 = obs1.content.lower()
            content2 = obs2.content.lower()
            
            # 예측 관련 키워드 확인
            predictive_keywords = ['predict', 'forecast', 'future', 'will', 'going to', 'likely']
            
            for keyword in predictive_keywords:
                if keyword in content1 or keyword in content2:
                    return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"예측 관계 확인 중 오류: {e}")
            return False
    
    def _create_generalizations(self, patterns: List[InductivePattern], 
                              inductive_type: InductiveType) -> List[InductiveGeneralization]:
        """일반화 생성"""
        generalizations = []
        
        try:
            for pattern in patterns:
                if pattern.observations:
                    # 패턴 기반 일반화 생성
                    generalization = self._create_generalization_from_pattern(pattern, inductive_type)
                    generalizations.append(generalization)
            
            return generalizations
            
        except Exception as e:
            self.logger.error(f"일반화 생성 중 오류: {e}")
            return []
    
    def _create_generalization_from_pattern(self, pattern: InductivePattern, 
                                          inductive_type: InductiveType) -> InductiveGeneralization:
        """패턴으로부터 일반화 생성"""
        try:
            # 관찰 내용 분석
            contents = [obs.content for obs in pattern.observations]
            
            # 일반화 내용 생성
            if inductive_type == InductiveType.ENUMERATIVE:
                generalization_content = f"관찰된 {len(pattern.observations)}개 사례에서 공통적으로 나타나는 패턴: {contents[0]}"
            elif inductive_type == InductiveType.STATISTICAL:
                generalization_content = f"통계적으로 {pattern.strength:.1%}의 확률로 나타나는 패턴: {contents[0]}"
            elif inductive_type == InductiveType.ANALOGICAL:
                generalization_content = f"유사한 특성을 가진 {len(pattern.observations)}개 사례에서 발견된 패턴: {contents[0]}"
            elif inductive_type == InductiveType.CAUSAL:
                generalization_content = f"인과 관계가 추정되는 {len(pattern.observations)}개 사례에서 발견된 패턴: {contents[0]}"
            elif inductive_type == InductiveType.PREDICTIVE:
                generalization_content = f"예측 가능한 {len(pattern.observations)}개 사례에서 발견된 패턴: {contents[0]}"
            else:
                generalization_content = f"일반적인 패턴: {contents[0]}"
            
            # 예외 사항 식별
            exceptions = self._identify_exceptions(pattern)
            
            generalization = InductiveGeneralization(
                generalization_id=f"generalization_{len(self.reasoning_history)}",
                content=generalization_content,
                supporting_observations=pattern.observations,
                confidence=pattern.confidence,
                exceptions=exceptions
            )
            
            return generalization
            
        except Exception as e:
            self.logger.error(f"패턴으로부터 일반화 생성 중 오류: {e}")
            return InductiveGeneralization(
                generalization_id="error",
                content="일반화 생성 오류",
                supporting_observations=[],
                confidence=0.0
            )
    
    def _identify_exceptions(self, pattern: InductivePattern) -> List[str]:
        """예외 사항 식별"""
        exceptions = []
        
        try:
            # 패턴과 일치하지 않는 관찰들을 예외로 식별
            pattern_content = pattern.observations[0].content.lower()
            
            for observation in pattern.observations[1:]:
                if observation.content.lower() != pattern_content:
                    exceptions.append(f"예외: {observation.content}")
            
            return exceptions
            
        except Exception as e:
            self.logger.error(f"예외 사항 식별 중 오류: {e}")
            return []
    
    def _analyze_inductive_reasoning(self, patterns: List[InductivePattern], 
                                   generalizations: List[InductiveGeneralization],
                                   inductive_type: InductiveType) -> InductiveAnalysis:
        """귀납적 추론 분석"""
        try:
            # 패턴 강도 분석
            pattern_strength = self._analyze_pattern_strength(patterns)
            
            # 일반화 신뢰도 분석
            generalization_confidence = self._analyze_generalization_confidence(generalizations)
            
            # 통계적 유의성 분석
            statistical_significance = self._analyze_statistical_significance(patterns)
            
            # 문제점 식별
            issues = self._identify_issues(patterns, generalizations)
            
            # 개선 제안
            suggestions = self._generate_suggestions(patterns, generalizations, inductive_type)
            
            return InductiveAnalysis(
                pattern_strength=pattern_strength,
                generalization_confidence=generalization_confidence,
                statistical_significance=statistical_significance,
                patterns=patterns,
                generalizations=generalizations,
                issues=issues,
                suggestions=suggestions
            )
            
        except Exception as e:
            self.logger.error(f"귀납적 추론 분석 중 오류: {e}")
            return InductiveAnalysis(
                pattern_strength=0.0,
                generalization_confidence=0.0,
                statistical_significance=0.0,
                issues=[f"분석 오류: {str(e)}"]
            )
    
    def _analyze_pattern_strength(self, patterns: List[InductivePattern]) -> float:
        """패턴 강도 분석"""
        try:
            if not patterns:
                return 0.0
            
            # 패턴들의 평균 강도 계산
            strengths = [pattern.strength for pattern in patterns]
            average_strength = sum(strengths) / len(strengths)
            
            return average_strength
            
        except Exception as e:
            self.logger.error(f"패턴 강도 분석 중 오류: {e}")
            return 0.0
    
    def _analyze_generalization_confidence(self, generalizations: List[InductiveGeneralization]) -> float:
        """일반화 신뢰도 분석"""
        try:
            if not generalizations:
                return 0.0
            
            # 일반화들의 평균 신뢰도 계산
            confidences = [gen.confidence for gen in generalizations]
            average_confidence = sum(confidences) / len(confidences)
            
            return average_confidence
            
        except Exception as e:
            self.logger.error(f"일반화 신뢰도 분석 중 오류: {e}")
            return 0.0
    
    def _analyze_statistical_significance(self, patterns: List[InductivePattern]) -> float:
        """통계적 유의성 분석"""
        try:
            if not patterns:
                return 0.0
            
            # 패턴의 크기와 신뢰도를 기반으로 통계적 유의성 계산
            significance_scores = []
            
            for pattern in patterns:
                # 패턴 크기가 클수록, 신뢰도가 높을수록 유의성이 높음
                size_factor = min(1.0, len(pattern.observations) / 10.0)
                confidence_factor = pattern.confidence
                significance = (size_factor + confidence_factor) / 2
                significance_scores.append(significance)
            
            average_significance = sum(significance_scores) / len(significance_scores)
            return average_significance
            
        except Exception as e:
            self.logger.error(f"통계적 유의성 분석 중 오류: {e}")
            return 0.0
    
    def _identify_issues(self, patterns: List[InductivePattern], 
                        generalizations: List[InductiveGeneralization]) -> List[str]:
        """문제점 식별"""
        issues = []
        
        try:
            # 패턴이 부족한 경우
            if len(patterns) < 2:
                issues.append("패턴이 부족합니다.")
            
            # 패턴 강도가 낮은 경우
            weak_patterns = [pattern for pattern in patterns if pattern.strength < 0.3]
            if weak_patterns:
                issues.append(f"강도가 낮은 패턴이 {len(weak_patterns)}개 있습니다.")
            
            # 일반화 신뢰도가 낮은 경우
            low_confidence_generations = [gen for gen in generalizations if gen.confidence < 0.5]
            if low_confidence_generations:
                issues.append(f"신뢰도가 낮은 일반화가 {len(low_confidence_generations)}개 있습니다.")
            
            return issues
            
        except Exception as e:
            self.logger.error(f"문제점 식별 중 오류: {e}")
            return [f"문제점 식별 오류: {str(e)}"]
    
    def _generate_suggestions(self, patterns: List[InductivePattern], 
                            generalizations: List[InductiveGeneralization],
                            inductive_type: InductiveType) -> List[str]:
        """개선 제안 생성"""
        suggestions = []
        
        try:
            # 패턴이 부족한 경우
            if len(patterns) < 2:
                suggestions.append("더 많은 관찰을 추가하여 패턴을 발견하세요.")
            
            # 패턴 강도가 낮은 경우
            weak_patterns = [pattern for pattern in patterns if pattern.strength < 0.3]
            if weak_patterns:
                suggestions.append("패턴의 강도를 높이기 위해 더 많은 관련 관찰을 수집하세요.")
            
            # 일반화 신뢰도가 낮은 경우
            low_confidence_generations = [gen for gen in generalizations if gen.confidence < 0.5]
            if low_confidence_generations:
                suggestions.append("일반화의 신뢰도를 높이기 위해 더 많은 지지 관찰을 수집하세요.")
            
            # 귀납 유형별 제안
            if inductive_type == InductiveType.ENUMERATIVE:
                suggestions.append("열거적 귀납을 위해 체계적인 관찰을 수행하세요.")
            elif inductive_type == InductiveType.STATISTICAL:
                suggestions.append("통계적 귀납을 위해 충분한 표본 크기를 확보하세요.")
            elif inductive_type == InductiveType.ANALOGICAL:
                suggestions.append("유추적 귀납을 위해 유사성 기준을 명확히 하세요.")
            elif inductive_type == InductiveType.CAUSAL:
                suggestions.append("인과적 귀납을 위해 인과 관계를 실험적으로 검증하세요.")
            elif inductive_type == InductiveType.PREDICTIVE:
                suggestions.append("예측적 귀납을 위해 시간적 순서를 고려하세요.")
            
            return suggestions
            
        except Exception as e:
            self.logger.error(f"개선 제안 생성 중 오류: {e}")
            return [f"제안 생성 오류: {str(e)}"]
    
    def _update_performance_metrics(self, analysis: InductiveAnalysis, processing_time: float):
        """성능 메트릭 업데이트"""
        self.performance_metrics['total_reasonings'] += 1
        if analysis.pattern_strength > 0.5 and analysis.generalization_confidence > 0.5:
            self.performance_metrics['successful_reasonings'] += 1
        
        # 평균 패턴 강도 업데이트
        total_strength = self.performance_metrics['average_pattern_strength'] * (self.performance_metrics['total_reasonings'] - 1)
        self.performance_metrics['average_pattern_strength'] = (total_strength + analysis.pattern_strength) / self.performance_metrics['total_reasonings']
        
        # 평균 일반화 신뢰도 업데이트
        total_confidence = self.performance_metrics['average_generalization_confidence'] * (self.performance_metrics['total_reasonings'] - 1)
        self.performance_metrics['average_generalization_confidence'] = (total_confidence + analysis.generalization_confidence) / self.performance_metrics['total_reasonings']
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """성능 메트릭 조회"""
        return self.performance_metrics.copy()
    
    def get_reasoning_history(self) -> List[Dict[str, Any]]:
        """추론 히스토리 조회"""
        return self.reasoning_history.copy()
