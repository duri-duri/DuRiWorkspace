"""
DuRi의 자기 개선 엔진

5단계 학습: 시행착오를 통한 개선
DuRi가 전략을 자가 개선하는 루프입니다.
"""

import logging
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
import random
import copy

logger = logging.getLogger(__name__)

class ImprovementType(Enum):
    """개선 유형"""
    MUTATION = "mutation"  # 변이
    CROSSOVER = "crossover"  # 교차
    OPTIMIZATION = "optimization"  # 최적화
    INNOVATION = "innovation"  # 혁신

@dataclass
class ImprovementResult:
    """개선 결과"""
    original_strategy: Dict[str, Any]
    improved_strategy: Dict[str, Any]
    improvement_type: ImprovementType
    improvement_score: float
    changes_made: List[str]
    confidence_gain: float
    timestamp: datetime
    success: bool

@dataclass
class LearningEvaluationCriteria:
    """학습 개선 평가 기준"""
    criteria_name: str
    weight: float
    current_value: float
    target_value: float
    improvement_potential: float

class SelfImprovementEngine:
    """
    DuRi의 자기 개선 엔진
    
    5단계 학습: 시행착오를 통한 개선
    DuRi가 전략을 자가 개선하는 루프입니다.
    """
    
    def __init__(self):
        """SelfImprovementEngine 초기화"""
        self.improvement_history: List[ImprovementResult] = []
        self.evaluation_criteria: Dict[str, LearningEvaluationCriteria] = {}
        self.learning_patterns: Dict[str, float] = {}
        self.mutation_rules: Dict[str, Any] = {}
        
        # 기본 평가 기준 초기화
        self._initialize_evaluation_criteria()
        
        logger.info("SelfImprovementEngine 초기화 완료")
    
    def improve(self, old_strategy: Dict[str, Any], 
                feedback_data: Optional[Dict[str, Any]] = None,
                improvement_type: Optional[ImprovementType] = None) -> ImprovementResult:
        """
        전략을 개선합니다.
        
        Args:
            old_strategy: 개선할 전략
            feedback_data: 피드백 데이터
            improvement_type: 개선 유형
            
        Returns:
            ImprovementResult: 개선 결과
        """
        try:
            # 개선 유형 결정
            if not improvement_type:
                improvement_type = self._determine_improvement_type(old_strategy, feedback_data)
            
            # 개선 실행
            improved_strategy = self._execute_improvement(old_strategy, improvement_type, feedback_data)
            
            # 개선 점수 계산
            improvement_score = self._calculate_improvement_score(old_strategy, improved_strategy, feedback_data)
            
            # 변경사항 추적
            changes_made = self._track_changes(old_strategy, improved_strategy)
            
            # 신뢰도 향상 계산
            confidence_gain = self._calculate_confidence_gain(improvement_score, feedback_data)
            
            # 평가 기준 업데이트
            self._update_evaluation_criteria(improvement_score, feedback_data)
            
            result = ImprovementResult(
                original_strategy=old_strategy,
                improved_strategy=improved_strategy,
                improvement_type=improvement_type,
                improvement_score=improvement_score,
                changes_made=changes_made,
                confidence_gain=confidence_gain,
                timestamp=datetime.now(),
                success=improvement_score > 0.0
            )
            
            self.improvement_history.append(result)
            self._update_learning_patterns(result)
            
            logger.info(f"전략 개선 완료: {improvement_type.value}, 개선점수: {improvement_score:.2f}, 신뢰도향상: {confidence_gain:.2f}")
            return result
            
        except Exception as e:
            logger.error(f"전략 개선 실패: {e}")
            return ImprovementResult(
                original_strategy=old_strategy,
                improved_strategy=old_strategy,
                improvement_type=improvement_type or ImprovementType.MUTATION,
                improvement_score=0.0,
                changes_made=[f"개선 실패: {str(e)}"],
                confidence_gain=0.0,
                timestamp=datetime.now(),
                success=False
            )
    
    def _initialize_evaluation_criteria(self):
        """평가 기준을 초기화합니다."""
        self.evaluation_criteria = {
            "performance": LearningEvaluationCriteria("성능", 0.3, 0.0, 1.0, 0.0),
            "efficiency": LearningEvaluationCriteria("효율성", 0.25, 0.0, 1.0, 0.0),
            "reliability": LearningEvaluationCriteria("신뢰성", 0.2, 0.0, 1.0, 0.0),
            "adaptability": LearningEvaluationCriteria("적응성", 0.15, 0.0, 1.0, 0.0),
            "creativity": LearningEvaluationCriteria("창의성", 0.1, 0.0, 1.0, 0.0)
        }
    
    def _determine_improvement_type(self, strategy: Dict[str, Any], 
                                  feedback_data: Optional[Dict[str, Any]]) -> ImprovementType:
        """개선 유형을 결정합니다."""
        if not feedback_data:
            return ImprovementType.MUTATION
        
        # 피드백 기반 개선 유형 결정
        performance_issues = feedback_data.get('performance_issues', [])
        reliability_issues = feedback_data.get('reliability_issues', [])
        efficiency_issues = feedback_data.get('efficiency_issues', [])
        
        if performance_issues and reliability_issues:
            return ImprovementType.OPTIMIZATION  # 성능과 신뢰성 문제 → 최적화
        elif efficiency_issues:
            return ImprovementType.CROSSOVER  # 효율성 문제 → 교차
        elif len(performance_issues) > 3:
            return ImprovementType.INNOVATION  # 많은 성능 문제 → 혁신
        else:
            return ImprovementType.MUTATION  # 기본 → 변이
    
    def _execute_improvement(self, strategy: Dict[str, Any], 
                           improvement_type: ImprovementType,
                           feedback_data: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """개선을 실행합니다."""
        improved_strategy = copy.deepcopy(strategy)
        
        if improvement_type == ImprovementType.MUTATION:
            improved_strategy = self._mutate_strategy(improved_strategy, feedback_data)
        elif improvement_type == ImprovementType.CROSSOVER:
            improved_strategy = self._crossover_strategy(improved_strategy, feedback_data)
        elif improvement_type == ImprovementType.OPTIMIZATION:
            improved_strategy = self._optimize_strategy(improved_strategy, feedback_data)
        elif improvement_type == ImprovementType.INNOVATION:
            improved_strategy = self._innovate_strategy(improved_strategy, feedback_data)
        
        return improved_strategy
    
    def _mutate_strategy(self, strategy: Dict[str, Any], 
                        feedback_data: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """전략을 변이시킵니다."""
        mutated_strategy = copy.deepcopy(strategy)
        
        # 파라미터 변이
        if 'parameters' in mutated_strategy:
            for param, value in mutated_strategy['parameters'].items():
                if isinstance(value, (int, float)):
                    # 5-15% 범위에서 랜덤 변이
                    mutation_rate = random.uniform(0.05, 0.15)
                    mutation = value * mutation_rate * random.choice([-1, 1])
                    mutated_strategy['parameters'][param] = value + mutation
        
        # 실행 방법 변이
        if 'execution_method' in mutated_strategy:
            methods = ['standard', 'aggressive', 'conservative', 'adaptive']
            if mutated_strategy['execution_method'] in methods:
                current_index = methods.index(mutated_strategy['execution_method'])
                new_index = (current_index + random.choice([-1, 1])) % len(methods)
                mutated_strategy['execution_method'] = methods[new_index]
        
        return mutated_strategy
    
    def _crossover_strategy(self, strategy: Dict[str, Any], 
                          feedback_data: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """전략을 교차시킵니다."""
        # 다른 성공 전략과의 교차 (시뮬레이션)
        successful_strategies = [
            {'parameters': {'speed': 0.8, 'accuracy': 0.9}},
            {'parameters': {'efficiency': 0.85, 'reliability': 0.95}},
            {'parameters': {'adaptability': 0.7, 'creativity': 0.8}}
        ]
        
        if successful_strategies:
            partner_strategy = random.choice(successful_strategies)
            crossover_strategy = copy.deepcopy(strategy)
            
            # 파라미터 교차
            if 'parameters' in crossover_strategy and 'parameters' in partner_strategy:
                for param in crossover_strategy['parameters']:
                    if param in partner_strategy['parameters']:
                        if random.random() < 0.5:  # 50% 확률로 교차
                            crossover_strategy['parameters'][param] = partner_strategy['parameters'][param]
            
            return crossover_strategy
        
        return strategy
    
    def _optimize_strategy(self, strategy: Dict[str, Any], 
                         feedback_data: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """전략을 최적화합니다."""
        optimized_strategy = copy.deepcopy(strategy)
        
        # 피드백 기반 최적화
        if feedback_data:
            performance_issues = feedback_data.get('performance_issues', [])
            reliability_issues = feedback_data.get('reliability_issues', [])
            
            # 성능 문제 해결
            if performance_issues and 'parameters' in optimized_strategy:
                if 'speed' in optimized_strategy['parameters']:
                    optimized_strategy['parameters']['speed'] = min(1.0, optimized_strategy['parameters']['speed'] * 1.1)
                if 'efficiency' in optimized_strategy['parameters']:
                    optimized_strategy['parameters']['efficiency'] = min(1.0, optimized_strategy['parameters']['efficiency'] * 1.05)
            
            # 신뢰성 문제 해결
            if reliability_issues and 'parameters' in optimized_strategy:
                if 'reliability' in optimized_strategy['parameters']:
                    optimized_strategy['parameters']['reliability'] = min(1.0, optimized_strategy['parameters']['reliability'] * 1.15)
                if 'safety_margin' in optimized_strategy['parameters']:
                    optimized_strategy['parameters']['safety_margin'] = min(1.0, optimized_strategy['parameters']['safety_margin'] * 1.2)
        
        return optimized_strategy
    
    def _innovate_strategy(self, strategy: Dict[str, Any], 
                         feedback_data: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """전략을 혁신합니다."""
        innovative_strategy = copy.deepcopy(strategy)
        
        # 혁신적 변화 적용
        if 'parameters' in innovative_strategy:
            # 새로운 파라미터 추가
            new_params = {
                'innovation_factor': random.uniform(0.1, 0.3),
                'creativity_boost': random.uniform(0.2, 0.4),
                'adaptive_rate': random.uniform(0.6, 0.9)
            }
            innovative_strategy['parameters'].update(new_params)
        
        # 실행 방법 혁신
        innovative_strategy['execution_method'] = 'innovative'
        innovative_strategy['innovation_level'] = 'high'
        
        return innovative_strategy
    
    def _calculate_improvement_score(self, old_strategy: Dict[str, Any], 
                                   improved_strategy: Dict[str, Any],
                                   feedback_data: Optional[Dict[str, Any]]) -> float:
        """개선 점수를 계산합니다."""
        score = 0.0
        
        # 파라미터 개선도 계산
        if 'parameters' in old_strategy and 'parameters' in improved_strategy:
            old_params = old_strategy['parameters']
            new_params = improved_strategy['parameters']
            
            for param in new_params:
                if param in old_params:
                    old_value = old_params[param]
                    new_value = new_params[param]
                    
                    if isinstance(old_value, (int, float)) and isinstance(new_value, (int, float)):
                        if new_value > old_value:
                            score += 0.1
                        elif new_value < old_value:
                            score -= 0.05
        
        # 피드백 기반 점수 조정
        if feedback_data:
            issues_resolved = feedback_data.get('issues_resolved', 0)
            score += issues_resolved * 0.2
        
        return max(score, 0.0)
    
    def _track_changes(self, old_strategy: Dict[str, Any], 
                      improved_strategy: Dict[str, Any]) -> List[str]:
        """변경사항을 추적합니다."""
        changes = []
        
        # 파라미터 변경 추적
        if 'parameters' in old_strategy and 'parameters' in improved_strategy:
            old_params = old_strategy['parameters']
            new_params = improved_strategy['parameters']
            
            for param in new_params:
                if param in old_params:
                    old_value = old_params[param]
                    new_value = new_params[param]
                    
                    if old_value != new_value:
                        changes.append(f"{param}: {old_value} → {new_value}")
                else:
                    changes.append(f"새 파라미터 추가: {param} = {new_params[param]}")
        
        # 실행 방법 변경 추적
        if 'execution_method' in old_strategy and 'execution_method' in improved_strategy:
            if old_strategy['execution_method'] != improved_strategy['execution_method']:
                changes.append(f"실행방법: {old_strategy['execution_method']} → {improved_strategy['execution_method']}")
        
        return changes
    
    def _calculate_confidence_gain(self, improvement_score: float, 
                                 feedback_data: Optional[Dict[str, Any]]) -> float:
        """신뢰도 향상을 계산합니다."""
        base_gain = improvement_score * 0.5
        
        # 피드백 기반 조정
        if feedback_data:
            positive_feedback = feedback_data.get('positive_feedback', 0)
            negative_feedback = feedback_data.get('negative_feedback', 0)
            
            feedback_ratio = positive_feedback / (positive_feedback + negative_feedback) if (positive_feedback + negative_feedback) > 0 else 0.5
            base_gain *= feedback_ratio
        
        return min(base_gain, 1.0)
    
    def _update_evaluation_criteria(self, improvement_score: float, 
                                  feedback_data: Optional[Dict[str, Any]]):
        """평가 기준을 업데이트합니다."""
        # 개선 점수에 따른 기준 업데이트
        for criteria in self.evaluation_criteria.values():
            if improvement_score > 0.1:
                criteria.current_value = min(1.0, criteria.current_value + improvement_score * 0.1)
                criteria.improvement_potential = max(0.0, criteria.improvement_potential - improvement_score * 0.05)
    
    def _update_learning_patterns(self, result: ImprovementResult):
        """학습 패턴을 업데이트합니다."""
        pattern_key = f"{result.improvement_type.value}_{len(result.changes_made)}"
        current_success = self.learning_patterns.get(pattern_key, 0)
        
        if result.success:
            self.learning_patterns[pattern_key] = current_success + 1
    
    def get_improvement_statistics(self) -> Dict[str, Any]:
        """개선 통계를 반환합니다."""
        total_improvements = len(self.improvement_history)
        successful_improvements = len([r for r in self.improvement_history if r.success])
        
        type_counts = {}
        for result in self.improvement_history:
            type_name = result.improvement_type.value
            type_counts[type_name] = type_counts.get(type_name, 0) + 1
        
        avg_improvement_score = sum(r.improvement_score for r in self.improvement_history) / total_improvements if total_improvements > 0 else 0
        avg_confidence_gain = sum(r.confidence_gain for r in self.improvement_history) / total_improvements if total_improvements > 0 else 0
        
        return {
            "total_improvements": total_improvements,
            "successful_improvements": successful_improvements,
            "success_rate": successful_improvements / total_improvements if total_improvements > 0 else 0,
            "type_distribution": type_counts,
            "average_improvement_score": avg_improvement_score,
            "average_confidence_gain": avg_confidence_gain,
            "learning_patterns": self.learning_patterns
        }
    
    def get_evaluation_criteria_summary(self) -> Dict[str, Any]:
        """평가 기준 요약을 반환합니다."""
        summary = {}
        for name, criteria in self.evaluation_criteria.items():
            summary[name] = {
                "current_value": criteria.current_value,
                "target_value": criteria.target_value,
                "improvement_potential": criteria.improvement_potential,
                "weight": criteria.weight
            }
        return summary

# 싱글톤 인스턴스
_self_improvement_engine = None

def get_self_improvement_engine() -> SelfImprovementEngine:
    """SelfImprovementEngine 싱글톤 인스턴스 반환"""
    global _self_improvement_engine
    if _self_improvement_engine is None:
        _self_improvement_engine = SelfImprovementEngine()
    return _self_improvement_engine 