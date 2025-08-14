"""
지능형 알고리즘 선택 엔진
문제 컨텍스트에 최적의 알고리즘을 선택하고 조합하는 시스템
"""

from typing import List, Dict, Any, Optional, Tuple
import logging
from datetime import datetime
import uuid
from dataclasses import dataclass, field

from .algorithm_knowledge_base import (
    AlgorithmKnowledge, 
    AlgorithmConnection, 
    ProblemPattern,
    AlgorithmKnowledgeBase
)

logger = logging.getLogger(__name__)

@dataclass
class ProblemContext:
    """문제 컨텍스트 정의"""
    
    context_id: str
    description: str
    domain: str
    complexity_level: str  # "simple", "medium", "complex"
    
    # 문제 특징
    key_features: List[str] = field(default_factory=list)
    constraints: List[str] = field(default_factory=list)
    goals: List[str] = field(default_factory=list)
    
    # 메타데이터
    created_at: datetime = field(default_factory=datetime.now)
    priority: float = 0.5  # 우선순위 (0-1)

@dataclass
class AlgorithmRecommendation:
    """알고리즘 추천 결과"""
    
    algorithm: AlgorithmKnowledge
    confidence_score: float  # 신뢰도 (0-1)
    reasoning: str           # 추천 이유
    expected_efficiency: float  # 예상 효율성
    risk_level: str         # 위험도 ("low", "medium", "high")
    
    # 대안 정보
    alternatives: List[AlgorithmKnowledge] = field(default_factory=list)
    combination_suggestions: List[str] = field(default_factory=list)

@dataclass
class CombinedAlgorithm:
    """조합된 알고리즘"""
    
    combination_id: str
    name: str
    description: str
    
    # 구성 요소
    primary_algorithm: AlgorithmKnowledge
    supporting_algorithms: List[AlgorithmKnowledge] = field(default_factory=list)
    
    # 조합 정보
    combination_logic: str = ""  # 조합 로직 설명
    expected_success_rate: float = 0.0  # 예상 성공률
    complexity: str = "O(n)"  # 전체 복잡도
    
    # 메타데이터
    created_at: datetime = field(default_factory=datetime.now)
    usage_count: int = 0

class AlgorithmSelectionEngine:
    """지능형 알고리즘 선택 엔진"""
    
    def __init__(self, knowledge_base: AlgorithmKnowledgeBase):
        self.knowledge_base = knowledge_base
        self.selection_history: List[Dict] = []
        
        logger.info("알고리즘 선택 엔진 초기화 완료")
    
    def select_optimal_algorithm(self, problem_context: ProblemContext) -> AlgorithmRecommendation:
        """
        문제 컨텍스트에 최적의 알고리즘 선택
        """
        try:
            # 1. 문제 패턴 분석
            problem_pattern = self._analyze_problem_pattern(problem_context)
            
            # 2. 적용 가능한 알고리즘 후보 선정
            candidates = self._find_applicable_algorithms(problem_context, problem_pattern)
            
            # 3. 알고리즘 평가 및 순위 결정
            ranked_candidates = self._rank_algorithms(candidates, problem_context)
            
            # 4. 최적 알고리즘 선택
            optimal_algorithm = ranked_candidates[0] if ranked_candidates else None
            
            if not optimal_algorithm:
                return self._create_fallback_recommendation(problem_context)
            
            # 5. 추천 결과 생성
            recommendation = self._create_recommendation(
                optimal_algorithm, 
                ranked_candidates[1:5],  # 상위 5개
                problem_context
            )
            
            # 6. 선택 이력 기록
            self._record_selection(problem_context, recommendation)
            
            return recommendation
            
        except Exception as e:
            logger.error(f"알고리즘 선택 실패: {e}")
            return self._create_fallback_recommendation(problem_context)
    
    def _analyze_problem_pattern(self, problem_context: ProblemContext) -> Optional[ProblemPattern]:
        """문제 패턴 분석"""
        # 문제 설명에서 키워드 추출
        keywords = self._extract_keywords(problem_context.description)
        
        # 가장 유사한 문제 패턴 찾기
        best_match = None
        best_score = 0.0
        
        for pattern in self.knowledge_base.problem_patterns.values():
            score = self._calculate_pattern_similarity(keywords, pattern.key_features)
            if score > best_score:
                best_score = score
                best_match = pattern
        
        return best_match if best_score > 0.3 else None
    
    def _extract_keywords(self, text: str) -> List[str]:
        """텍스트에서 키워드 추출 (간단한 구현)"""
        # 실제로는 NLP 라이브러리를 사용하여 더 정교하게 구현
        words = text.lower().split()
        # 일반적인 단어 제거
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'}
        keywords = [word for word in words if word not in stop_words and len(word) > 2]
        return keywords
    
    def _calculate_pattern_similarity(self, keywords: List[str], pattern_features: List[str]) -> float:
        """패턴 유사도 계산"""
        if not keywords or not pattern_features:
            return 0.0
        
        matches = sum(1 for keyword in keywords if any(keyword in feature.lower() for feature in pattern_features))
        return matches / len(keywords)
    
    def _find_applicable_algorithms(self, problem_context: ProblemContext, 
                                  problem_pattern: Optional[ProblemPattern]) -> List[AlgorithmKnowledge]:
        """적용 가능한 알고리즘 찾기"""
        candidates = []
        
        # 1. 문제 패턴 기반 검색
        if problem_pattern:
            for algorithm_id in problem_pattern.applicable_algorithms:
                algorithm = self.knowledge_base.get_algorithm(algorithm_id)
                if algorithm:
                    candidates.append(algorithm)
        
        # 2. 키워드 기반 검색
        keywords = self._extract_keywords(problem_context.description)
        keyword_candidates = self.knowledge_base.search_algorithms(" ".join(keywords))
        candidates.extend(keyword_candidates)
        
        # 3. 도메인 기반 검색
        domain_candidates = self._search_by_domain(problem_context.domain)
        candidates.extend(domain_candidates)
        
        # 중복 제거 및 정렬
        unique_candidates = list({c.algorithm_id: c for c in candidates}.values())
        return unique_candidates
    
    def _search_by_domain(self, domain: str) -> List[AlgorithmKnowledge]:
        """도메인 기반 알고리즘 검색"""
        domain_algorithms = []
        
        for algorithm in self.knowledge_base.algorithms.values():
            if domain.lower() in [d.lower() for d in algorithm.applicable_domains]:
                domain_algorithms.append(algorithm)
        
        return domain_algorithms
    
    def _rank_algorithms(self, candidates: List[AlgorithmKnowledge], 
                        problem_context: ProblemContext) -> List[AlgorithmKnowledge]:
        """알고리즘 순위 결정"""
        if not candidates:
            return []
        
        # 각 알고리즘에 점수 부여
        scored_candidates = []
        
        for algorithm in candidates:
            score = self._calculate_algorithm_score(algorithm, problem_context)
            scored_candidates.append((algorithm, score))
        
        # 점수 기준으로 정렬
        scored_candidates.sort(key=lambda x: x[1], reverse=True)
        
        # 알고리즘만 반환
        return [candidate for candidate, score in scored_candidates]
    
    def _calculate_algorithm_score(self, algorithm: AlgorithmKnowledge, 
                                 problem_context: ProblemContext) -> float:
        """알고리즘 점수 계산"""
        score = 0.0
        
        # 1. 성공률 (40%)
        score += algorithm.success_rate * 0.4
        
        # 2. 효율성 (25%)
        score += algorithm.efficiency_score * 0.25
        
        # 3. 복잡도 적합성 (20%)
        complexity_score = self._calculate_complexity_score(algorithm.complexity, problem_context.complexity_level)
        score += complexity_score * 0.2
        
        # 4. 최근 사용성 (10%)
        recency_score = self._calculate_recency_score(algorithm.last_used)
        score += recency_score * 0.1
        
        # 5. 도메인 적합성 (5%)
        domain_score = self._calculate_domain_score(algorithm, problem_context.domain)
        score += domain_score * 0.05
        
        return score
    
    def _calculate_complexity_score(self, algorithm_complexity: str, problem_complexity: str) -> float:
        """복잡도 적합성 점수 계산"""
        complexity_mapping = {
            "simple": 0.0,
            "medium": 0.5,
            "complex": 1.0
        }
        
        problem_score = complexity_mapping.get(problem_complexity, 0.5)
        
        # 알고리즘 복잡도가 문제 복잡도와 비슷할 때 높은 점수
        if "O(1)" in algorithm_complexity:
            alg_score = 0.0
        elif "O(log" in algorithm_complexity:
            alg_score = 0.3
        elif "O(n)" in algorithm_complexity:
            alg_score = 0.6
        elif "O(n^2)" in algorithm_complexity or "O(n^3)" in algorithm_complexity:
            alg_score = 1.0
        else:
            alg_score = 0.5
        
        # 유사도 계산 (1 - |alg_score - problem_score|)
        return max(0.0, 1.0 - abs(alg_score - problem_score))
    
    def _calculate_recency_score(self, last_used: Optional[datetime]) -> float:
        """최근 사용성 점수 계산"""
        if not last_used:
            return 0.5  # 중간 점수
        
        days_since_use = (datetime.now() - last_used).days
        
        if days_since_use <= 1:
            return 1.0
        elif days_since_use <= 7:
            return 0.8
        elif days_since_use <= 30:
            return 0.6
        elif days_since_use <= 90:
            return 0.4
        else:
            return 0.2
    
    def _calculate_domain_score(self, algorithm: AlgorithmKnowledge, problem_domain: str) -> float:
        """도메인 적합성 점수 계산"""
        if not algorithm.applicable_domains:
            return 0.5
        
        if problem_domain.lower() in [d.lower() for d in algorithm.applicable_domains]:
            return 1.0
        
        return 0.0
    
    def _create_recommendation(self, optimal_algorithm: AlgorithmKnowledge, 
                              alternatives: List[AlgorithmKnowledge], 
                              problem_context: ProblemContext) -> AlgorithmRecommendation:
        """추천 결과 생성"""
        # 신뢰도 계산
        confidence_score = self._calculate_confidence_score(optimal_algorithm, problem_context)
        
        # 추천 이유 생성
        reasoning = self._generate_recommendation_reasoning(optimal_algorithm, problem_context)
        
        # 예상 효율성
        expected_efficiency = optimal_algorithm.efficiency_score
        
        # 위험도 평가
        risk_level = self._assess_risk_level(optimal_algorithm, problem_context)
        
        # 조합 제안 생성
        combination_suggestions = self._generate_combination_suggestions(optimal_algorithm, alternatives)
        
        return AlgorithmRecommendation(
            algorithm=optimal_algorithm,
            confidence_score=confidence_score,
            reasoning=reasoning,
            expected_efficiency=expected_efficiency,
            risk_level=risk_level,
            alternatives=alternatives,
            combination_suggestions=combination_suggestions
        )
    
    def _calculate_confidence_score(self, algorithm: AlgorithmKnowledge, 
                                  problem_context: ProblemContext) -> float:
        """신뢰도 점수 계산"""
        base_confidence = algorithm.confidence_level
        
        # 성공률 기반 조정
        success_adjustment = algorithm.success_rate * 0.3
        
        # 사용 횟수 기반 조정
        usage_adjustment = min(0.2, algorithm.usage_count * 0.01)
        
        # 복잡도 적합성 기반 조정
        complexity_adjustment = self._calculate_complexity_score(
            algorithm.complexity, 
            problem_context.complexity_level
        ) * 0.2
        
        final_confidence = base_confidence + success_adjustment + usage_adjustment + complexity_adjustment
        
        return min(1.0, max(0.0, final_confidence))
    
    def _generate_recommendation_reasoning(self, algorithm: AlgorithmKnowledge, 
                                         problem_context: ProblemContext) -> str:
        """추천 이유 생성"""
        reasons = []
        
        if algorithm.success_rate > 0.8:
            reasons.append(f"높은 성공률 ({algorithm.success_rate:.1%})")
        
        if algorithm.efficiency_score > 0.7:
            reasons.append(f"높은 효율성 ({algorithm.efficiency_score:.1%})")
        
        if algorithm.usage_count > 10:
            reasons.append(f"풍부한 사용 경험 ({algorithm.usage_count}회)")
        
        if algorithm.applicable_domains and problem_context.domain.lower() in [d.lower() for d in algorithm.applicable_domains]:
            reasons.append(f"도메인 특화 ({problem_context.domain})")
        
        if not reasons:
            reasons.append("가장 적합한 알고리즘으로 판단")
        
        return ", ".join(reasons)
    
    def _assess_risk_level(self, algorithm: AlgorithmKnowledge, 
                          problem_context: ProblemContext) -> str:
        """위험도 평가"""
        risk_score = 0.0
        
        # 낮은 성공률
        if algorithm.success_rate < 0.5:
            risk_score += 0.4
        
        # 낮은 효율성
        if algorithm.efficiency_score < 0.5:
            risk_score += 0.3
        
        # 적은 사용 경험
        if algorithm.usage_count < 3:
            risk_score += 0.2
        
        # 복잡도 불일치
        complexity_score = self._calculate_complexity_score(algorithm.complexity, problem_context.complexity_level)
        if complexity_score < 0.5:
            risk_score += 0.1
        
        if risk_score < 0.3:
            return "low"
        elif risk_score < 0.6:
            return "medium"
        else:
            return "high"
    
    def _generate_combination_suggestions(self, primary_algorithm: AlgorithmKnowledge, 
                                        alternatives: List[AlgorithmKnowledge]) -> List[str]:
        """조합 제안 생성"""
        suggestions = []
        
        # 관련 알고리즘 찾기
        related = self.knowledge_base.get_related_algorithms(primary_algorithm.algorithm_id)
        
        for related_alg in related[:3]:  # 상위 3개
            if related_alg.algorithm_id != primary_algorithm.algorithm_id:
                suggestions.append(f"{primary_algorithm.name} + {related_alg.name} 조합 고려")
        
        return suggestions
    
    def _create_fallback_recommendation(self, problem_context: ProblemContext) -> AlgorithmRecommendation:
        """폴백 추천 생성 (적합한 알고리즘이 없을 때)"""
        # 가장 일반적인 알고리즘 선택
        fallback_algorithm = None
        
        for algorithm in self.knowledge_base.algorithms.values():
            if algorithm.category == "problem_solving" and algorithm.success_rate > 0.5:
                fallback_algorithm = algorithm
                break
        
        if not fallback_algorithm:
            # 아무 알고리즘이나 선택
            fallback_algorithm = list(self.knowledge_base.algorithms.values())[0] if self.knowledge_base.algorithms else None
        
        if fallback_algorithm:
            return AlgorithmRecommendation(
                algorithm=fallback_algorithm,
                confidence_score=0.3,
                reasoning="적합한 알고리즘을 찾지 못하여 기본 알고리즘 추천",
                expected_efficiency=0.5,
                risk_level="high",
                alternatives=[],
                combination_suggestions=[]
            )
        else:
            # 아무 알고리즘도 없는 경우
            return None
    
    def _record_selection(self, problem_context: ProblemContext, 
                         recommendation: AlgorithmRecommendation):
        """선택 이력 기록"""
        if not recommendation:
            return
        
        record = {
            'timestamp': datetime.now().isoformat(),
            'problem_context': {
                'description': problem_context.description,
                'domain': problem_context.domain,
                'complexity_level': problem_context.complexity_level
            },
            'selected_algorithm': {
                'id': recommendation.algorithm.algorithm_id,
                'name': recommendation.algorithm.name,
                'category': recommendation.algorithm.category
            },
            'confidence_score': recommendation.confidence_score,
            'risk_level': recommendation.risk_level
        }
        
        self.selection_history.append(record)
        
        # 이력이 너무 많아지면 오래된 것 제거
        if len(self.selection_history) > 1000:
            self.selection_history = self.selection_history[-500:]
    
    def get_selection_statistics(self) -> Dict[str, Any]:
        """선택 통계 조회"""
        if not self.selection_history:
            return {}
        
        total_selections = len(self.selection_history)
        
        # 카테고리별 선택 통계
        category_stats = {}
        for record in self.selection_history:
            category = record['selected_algorithm']['category']
            if category not in category_stats:
                category_stats[category] = 0
            category_stats[category] += 1
        
        # 평균 신뢰도
        avg_confidence = sum(r['confidence_score'] for r in self.selection_history) / total_selections
        
        # 위험도 분포
        risk_distribution = {}
        for record in self.selection_history:
            risk = record['risk_level']
            if risk not in risk_distribution:
                risk_distribution[risk] = 0
            risk_distribution[risk] += 1
        
        return {
            'total_selections': total_selections,
            'category_distribution': category_stats,
            'average_confidence': avg_confidence,
            'risk_distribution': risk_distribution,
            'recent_selections': self.selection_history[-10:]  # 최근 10개
        }
