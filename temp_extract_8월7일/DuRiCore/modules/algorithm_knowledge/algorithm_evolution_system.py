"""
알고리즘 학습 및 진화 시스템
성공/실패 사례로부터 알고리즘을 개선하고 새로운 알고리즘을 생성하는 시스템
"""

from typing import List, Dict, Any, Optional, Tuple
import logging
from datetime import datetime
import uuid
import random
import json
from dataclasses import dataclass, field

from .algorithm_knowledge_base import (
    AlgorithmKnowledge, 
    AlgorithmConnection, 
    ProblemPattern,
    AlgorithmKnowledgeBase
)

logger = logging.getLogger(__name__)

@dataclass
class LearningSession:
    """학습 세션 정보"""
    
    session_id: str
    algorithm_id: str
    problem_context: str
    success: bool
    efficiency_score: float
    execution_time: float
    feedback: str
    
    # 메타데이터
    created_at: datetime = field(default_factory=datetime.now)
    improvement_suggestions: List[str] = field(default_factory=list)

@dataclass
class AlgorithmImprovement:
    """알고리즘 개선 정보"""
    
    improvement_id: str
    algorithm_id: str
    improvement_type: str  # "parameter_tuning", "logic_modification", "combination_enhancement"
    description: str
    before_state: Dict[str, Any]
    after_state: Dict[str, Any]
    improvement_score: float
    
    # 메타데이터
    created_at: datetime = field(default_factory=datetime.now)
    applied: bool = False

@dataclass
class NewAlgorithm:
    """새로 생성된 알고리즘"""
    
    algorithm_id: str
    name: str
    description: str
    category: str
    
    # 생성 정보
    source_algorithms: List[str]  # 기반이 된 알고리즘들
    generation_method: str        # 생성 방법
    confidence_level: float       # 신뢰도
    
    # 메타데이터
    created_at: datetime = field(default_factory=datetime.now)
    tested: bool = False

class AlgorithmEvolutionSystem:
    """알고리즘 학습 및 진화 시스템"""
    
    def __init__(self, knowledge_base: AlgorithmKnowledgeBase):
        self.knowledge_base = knowledge_base
        self.learning_sessions: List[LearningSession] = []
        self.improvements: List[AlgorithmImprovement] = []
        self.new_algorithms: List[NewAlgorithm] = []
        
        # 진화 파라미터
        self.evolution_threshold = 0.1  # 진화 임계값
        self.improvement_threshold = 0.05  # 개선 임계값
        self.combination_probability = 0.3  # 조합 생성 확률
        
        logger.info("알고리즘 진화 시스템 초기화 완료")
    
    def learn_from_execution(self, algorithm_id: str, problem_context: str, 
                           success: bool, efficiency_score: float, 
                           execution_time: float, feedback: str = "") -> bool:
        """
        알고리즘 실행 결과로부터 학습
        """
        try:
            # 학습 세션 생성
            session = LearningSession(
                session_id=str(uuid.uuid4()),
                algorithm_id=algorithm_id,
                problem_context=problem_context,
                success=success,
                efficiency_score=efficiency_score,
                execution_time=execution_time,
                feedback=feedback
            )
            
            self.learning_sessions.append(session)
            
            # 알고리즘 성능 업데이트
            self.knowledge_base.update_algorithm_performance(
                algorithm_id, success, efficiency_score
            )
            
            # 개선점 분석
            if not success or efficiency_score < 0.7:
                improvements = self._analyze_improvement_opportunities(session)
                for improvement in improvements:
                    self.improvements.append(improvement)
            
            # 진화 조건 확인
            if self._should_evolve(algorithm_id):
                self._trigger_evolution(algorithm_id)
            
            logger.info(f"학습 세션 완료: {algorithm_id} (성공: {success})")
            return True
            
        except Exception as e:
            logger.error(f"학습 세션 실패: {e}")
            return False
    
    def _analyze_improvement_opportunities(self, session: LearningSession) -> List[AlgorithmImprovement]:
        """개선 기회 분석"""
        improvements = []
        algorithm = self.knowledge_base.get_algorithm(session.algorithm_id)
        
        if not algorithm:
            return improvements
        
        # 1. 성공률 기반 개선
        if session.success and algorithm.success_rate < 0.8:
            improvement = AlgorithmImprovement(
                improvement_id=str(uuid.uuid4()),
                algorithm_id=session.algorithm_id,
                improvement_type="success_rate_optimization",
                description="성공률 향상을 위한 파라미터 최적화",
                before_state={"success_rate": algorithm.success_rate},
                after_state={"success_rate": algorithm.success_rate + 0.1},
                improvement_score=0.1
            )
            improvements.append(improvement)
        
        # 2. 효율성 기반 개선
        if session.efficiency_score < 0.7:
            improvement = AlgorithmImprovement(
                improvement_id=str(uuid.uuid4()),
                algorithm_id=session.algorithm_id,
                improvement_type="efficiency_optimization",
                description="효율성 향상을 위한 로직 개선",
                before_state={"efficiency_score": algorithm.efficiency_score},
                after_state={"efficiency_score": algorithm.efficiency_score + 0.15},
                improvement_score=0.15
            )
            improvements.append(improvement)
        
        # 3. 실행 시간 기반 개선
        if session.execution_time > 5.0:  # 5초 이상 걸린 경우
            improvement = AlgorithmImprovement(
                improvement_id=str(uuid.uuid4()),
                algorithm_id=session.algorithm_id,
                improvement_type="performance_optimization",
                description="실행 시간 단축을 위한 성능 최적화",
                before_state={"complexity": algorithm.complexity},
                after_state={"complexity": self._optimize_complexity(algorithm.complexity)},
                improvement_score=0.2
            )
            improvements.append(improvement)
        
        return improvements
    
    def _optimize_complexity(self, current_complexity: str) -> str:
        """복잡도 최적화"""
        if "O(n^3)" in current_complexity:
            return "O(n^2)"
        elif "O(n^2)" in current_complexity:
            return "O(n log n)"
        elif "O(n log n)" in current_complexity:
            return "O(n)"
        else:
            return current_complexity
    
    def _should_evolve(self, algorithm_id: str) -> bool:
        """진화 조건 확인"""
        algorithm = self.knowledge_base.get_algorithm(algorithm_id)
        if not algorithm:
            return False
        
        # 성공률이 낮고 개선 시도가 여러 번 있었을 때
        if (algorithm.success_rate < 0.5 and 
            algorithm.usage_count > 10 and
            len([imp for imp in self.improvements if imp.algorithm_id == algorithm_id]) > 3):
            return True
        
        # 효율성이 낮고 사용 빈도가 높을 때
        if (algorithm.efficiency_score < 0.4 and 
            algorithm.usage_count > 20):
            return True
        
        return False
    
    def _trigger_evolution(self, algorithm_id: str):
        """진화 트리거"""
        try:
            # 1. 알고리즘 조합 시도
            if random.random() < self.combination_probability:
                new_algorithm = self._create_combined_algorithm(algorithm_id)
                if new_algorithm:
                    self.new_algorithms.append(new_algorithm)
                    logger.info(f"새로운 조합 알고리즘 생성: {new_algorithm.name}")
            
            # 2. 기존 알고리즘 개선
            improvements = [imp for imp in self.improvements if imp.algorithm_id == algorithm_id]
            for improvement in improvements:
                if not improvement.applied:
                    self._apply_improvement(improvement)
            
            logger.info(f"알고리즘 진화 완료: {algorithm_id}")
            
        except Exception as e:
            logger.error(f"알고리즘 진화 실패: {e}")
    
    def _create_combined_algorithm(self, base_algorithm_id: str) -> Optional[NewAlgorithm]:
        """알고리즘 조합으로 새로운 알고리즘 생성"""
        try:
            base_algorithm = self.knowledge_base.get_algorithm(base_algorithm_id)
            if not base_algorithm:
                return None
            
            # 관련 알고리즘 찾기
            related = self.knowledge_base.get_related_algorithms(base_algorithm_id)
            if not related:
                return None
            
            # 가장 성공률이 높은 관련 알고리즘 선택
            best_related = max(related, key=lambda x: x.success_rate)
            
            # 조합 알고리즘 생성
            combined_name = f"{base_algorithm.name} + {best_related.name} Hybrid"
            combined_description = f"{base_algorithm.description}와 {best_related.description}을 조합한 하이브리드 알고리즘"
            
            # 카테고리 결정
            if base_algorithm.category == best_related.category:
                combined_category = base_algorithm.category
            else:
                combined_category = "hybrid"
            
            new_algorithm = NewAlgorithm(
                algorithm_id=str(uuid.uuid4()),
                name=combined_name,
                description=combined_description,
                category=combined_category,
                source_algorithms=[base_algorithm_id, best_related.algorithm_id],
                generation_method="combination",
                confidence_level=(base_algorithm.confidence_level + best_related.confidence_level) / 2
            )
            
            return new_algorithm
            
        except Exception as e:
            logger.error(f"조합 알고리즘 생성 실패: {e}")
            return None
    
    def _apply_improvement(self, improvement: AlgorithmImprovement) -> bool:
        """개선사항 적용"""
        try:
            algorithm = self.knowledge_base.get_algorithm(improvement.algorithm_id)
            if not algorithm:
                return False
            
            # 개선사항 적용
            if improvement.improvement_type == "success_rate_optimization":
                algorithm.success_rate = improvement.after_state["success_rate"]
            elif improvement.improvement_type == "efficiency_optimization":
                algorithm.efficiency_score = improvement.after_state["efficiency_score"]
            elif improvement.improvement_type == "performance_optimization":
                algorithm.complexity = improvement.after_state["complexity"]
            
            # 개선 이력 추가
            improvement_record = {
                'timestamp': datetime.now().isoformat(),
                'type': improvement.improvement_type,
                'description': improvement.description,
                'improvement_score': improvement.improvement_score
            }
            algorithm.improvement_history.append(improvement_record)
            
            # 업데이트 시간 갱신
            algorithm.updated_at = datetime.now()
            
            # 개선사항 적용 완료 표시
            improvement.applied = True
            
            logger.info(f"알고리즘 개선 적용 완료: {improvement.algorithm_id}")
            return True
            
        except Exception as e:
            logger.error(f"알고리즘 개선 적용 실패: {e}")
            return False
    
    def generate_new_algorithm(self, problem_pattern: str) -> Optional[NewAlgorithm]:
        """
        새로운 문제 패턴에 대한 알고리즘 자동 생성
        """
        try:
            # 1. 유사한 문제 패턴 찾기
            similar_patterns = self._find_similar_patterns(problem_pattern)
            
            if not similar_patterns:
                return None
            
            # 2. 관련 알고리즘들 수집
            related_algorithms = []
            for pattern in similar_patterns:
                for algorithm_id in pattern.applicable_algorithms:
                    algorithm = self.knowledge_base.get_algorithm(algorithm_id)
                    if algorithm:
                        related_algorithms.append(algorithm)
            
            if not related_algorithms:
                return None
            
            # 3. 최적의 알고리즘 조합 찾기
            best_combination = self._find_best_combination(related_algorithms)
            
            if not best_combination:
                return None
            
            # 4. 새로운 알고리즘 생성
            new_algorithm = self._create_adaptive_algorithm(
                problem_pattern, best_combination
            )
            
            if new_algorithm:
                self.new_algorithms.append(new_algorithm)
                logger.info(f"새로운 적응형 알고리즘 생성: {new_algorithm.name}")
            
            return new_algorithm
            
        except Exception as e:
            logger.error(f"새로운 알고리즘 생성 실패: {e}")
            return None
    
    def _find_similar_patterns(self, problem_pattern: str) -> List[ProblemPattern]:
        """유사한 문제 패턴 찾기"""
        similar_patterns = []
        keywords = self._extract_keywords(problem_pattern)
        
        for pattern in self.knowledge_base.problem_patterns.values():
            similarity = self._calculate_pattern_similarity(keywords, pattern.key_features)
            if similarity > 0.4:  # 40% 이상 유사
                similar_patterns.append(pattern)
        
        # 유사도 기준으로 정렬
        similar_patterns.sort(
            key=lambda x: self._calculate_pattern_similarity(keywords, x.key_features),
            reverse=True
        )
        
        return similar_patterns[:3]  # 상위 3개
    
    def _extract_keywords(self, text: str) -> List[str]:
        """텍스트에서 키워드 추출"""
        words = text.lower().split()
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'}
        keywords = [word for word in words if word not in stop_words and len(word) > 2]
        return keywords
    
    def _calculate_pattern_similarity(self, keywords: List[str], pattern_features: List[str]) -> float:
        """패턴 유사도 계산"""
        if not keywords or not pattern_features:
            return 0.0
        
        matches = sum(1 for keyword in keywords if any(keyword in feature.lower() for feature in pattern_features))
        return matches / len(keywords)
    
    def _find_best_combination(self, algorithms: List[AlgorithmKnowledge]) -> List[AlgorithmKnowledge]:
        """최적의 알고리즘 조합 찾기"""
        if len(algorithms) <= 2:
            return algorithms
        
        # 성공률과 효율성 기준으로 정렬
        sorted_algorithms = sorted(
            algorithms,
            key=lambda x: (x.success_rate + x.efficiency_score) / 2,
            reverse=True
        )
        
        # 상위 2개 선택
        return sorted_algorithms[:2]
    
    def _create_adaptive_algorithm(self, problem_pattern: str, 
                                 base_algorithms: List[AlgorithmKnowledge]) -> Optional[NewAlgorithm]:
        """적응형 알고리즘 생성"""
        try:
            if not base_algorithms:
                return None
            
            # 알고리즘 이름과 설명 생성
            names = [alg.name for alg in base_algorithms]
            descriptions = [alg.description for alg in base_algorithms]
            
            combined_name = f"Adaptive {' + '.join(names)}"
            combined_description = f"문제 패턴 '{problem_pattern}'에 특화된 적응형 알고리즘. {' '.join(descriptions)}"
            
            # 신뢰도 계산
            avg_confidence = sum(alg.confidence_level for alg in base_algorithms) / len(base_algorithms)
            
            new_algorithm = NewAlgorithm(
                algorithm_id=str(uuid.uuid4()),
                name=combined_name,
                description=combined_description,
                category="adaptive",
                source_algorithms=[alg.algorithm_id for alg in base_algorithms],
                generation_method="pattern_adaptation",
                confidence_level=avg_confidence * 0.8  # 새로운 알고리즘이므로 신뢰도 조정
            )
            
            return new_algorithm
            
        except Exception as e:
            logger.error(f"적응형 알고리즘 생성 실패: {e}")
            return None
    
    def get_evolution_statistics(self) -> Dict[str, Any]:
        """진화 통계 조회"""
        return {
            'total_learning_sessions': len(self.learning_sessions),
            'total_improvements': len(self.improvements),
            'applied_improvements': len([imp for imp in self.improvements if imp.applied]),
            'total_new_algorithms': len(self.new_algorithms),
            'tested_new_algorithms': len([alg for alg in self.new_algorithms if alg.tested]),
            'evolution_rate': len([imp for imp in self.improvements if imp.applied]) / max(1, len(self.improvements)),
            'recent_improvements': [
                {
                    'algorithm_id': imp.algorithm_id,
                    'type': imp.improvement_type,
                    'score': imp.improvement_score,
                    'applied': imp.applied
                }
                for imp in self.improvements[-10:]  # 최근 10개
            ],
            'recent_new_algorithms': [
                {
                    'name': alg.name,
                    'category': alg.category,
                    'confidence': alg.confidence_level,
                    'tested': alg.tested
                }
                for alg in self.new_algorithms[-5:]  # 최근 5개
            ]
        }
    
    def save_evolution_data(self, filepath: str) -> bool:
        """진화 데이터 저장"""
        try:
            data = {
                'learning_sessions': [
                    {
                        'session_id': session.session_id,
                        'algorithm_id': session.algorithm_id,
                        'problem_context': session.problem_context,
                        'success': session.success,
                        'efficiency_score': session.efficiency_score,
                        'execution_time': session.execution_time,
                        'feedback': session.feedback,
                        'created_at': session.created_at.isoformat(),
                        'improvement_suggestions': session.improvement_suggestions
                    }
                    for session in self.learning_sessions
                ],
                'improvements': [
                    {
                        'improvement_id': imp.improvement_id,
                        'algorithm_id': imp.algorithm_id,
                        'improvement_type': imp.improvement_type,
                        'description': imp.description,
                        'before_state': imp.before_state,
                        'after_state': imp.after_state,
                        'improvement_score': imp.improvement_score,
                        'created_at': imp.created_at.isoformat(),
                        'applied': imp.applied
                    }
                    for imp in self.improvements
                ],
                'new_algorithms': [
                    {
                        'algorithm_id': alg.algorithm_id,
                        'name': alg.name,
                        'description': alg.description,
                        'category': alg.category,
                        'source_algorithms': alg.source_algorithms,
                        'generation_method': alg.generation_method,
                        'confidence_level': alg.confidence_level,
                        'created_at': alg.created_at.isoformat(),
                        'tested': alg.tested
                    }
                    for alg in self.new_algorithms
                ]
            }
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            logger.info(f"진화 데이터 저장 완료: {filepath}")
            return True
            
        except Exception as e:
            logger.error(f"진화 데이터 저장 실패: {e}")
            return False
