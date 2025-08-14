"""
알고리즘 조합 최적화 강화학습 시스템
Multi-Armed Bandit을 사용하여 최적의 알고리즘 조합을 찾는 시스템
"""

import numpy as np
import pandas as pd
from typing import List, Dict, Any, Optional, Tuple, Set
import logging
from datetime import datetime
import pickle
import json
import random
from collections import defaultdict, deque

# 강화학습 라이브러리
try:
    import gym
    from gym import spaces
    RL_AVAILABLE = True
except ImportError:
    RL_AVAILABLE = False
    logging.warning("강화학습 라이브러리가 설치되지 않았습니다. pip install gym")

from ..algorithm_knowledge.algorithm_knowledge_base import (
    AlgorithmKnowledge, 
    ProblemPattern,
    AlgorithmKnowledgeBase
)

logger = logging.getLogger(__name__)

class MultiArmedBandit:
    """Multi-Armed Bandit 알고리즘"""
    
    def __init__(self, n_arms: int, exploration_rate: float = 0.1):
        self.n_arms = n_arms
        self.exploration_rate = exploration_rate
        self.arm_counts = np.zeros(n_arms)
        self.arm_rewards = np.zeros(n_arms)
        self.arm_values = np.zeros(n_arms)
        
    def select_arm(self) -> int:
        """팔 선택 (ε-greedy 정책)"""
        if random.random() < self.exploration_rate:
            # 탐색: 무작위 선택
            return random.randint(0, self.n_arms - 1)
        else:
            # 활용: 최고 가치 팔 선택
            return np.argmax(self.arm_values)
    
    def update(self, arm: int, reward: float):
        """팔의 보상 업데이트"""
        self.arm_counts[arm] += 1
        self.arm_rewards[arm] += reward
        
        # 평균 보상 계산
        self.arm_values[arm] = self.arm_rewards[arm] / self.arm_counts[arm]
    
    def get_arm_stats(self) -> Dict[str, np.ndarray]:
        """팔 통계 정보 반환"""
        return {
            'counts': self.arm_counts.copy(),
            'rewards': self.arm_rewards.copy(),
            'values': self.arm_values.copy()
        }

class AlgorithmCombinationOptimizer:
    """알고리즘 조합 최적화 강화학습 시스템"""
    
    def __init__(self, knowledge_base: AlgorithmKnowledgeBase):
        self.knowledge_base = knowledge_base
        
        # 강화학습 모델들
        self.multi_armed_bandit = None
        self.epsilon_greedy = None
        self.ucb_optimizer = None
        
        # 알고리즘 조합 데이터
        self.algorithm_combinations = []
        self.combination_performance = {}
        self.optimization_history = []
        
        # 하이퍼파라미터
        self.exploration_rate = 0.1
        self.learning_rate = 0.01
        self.discount_factor = 0.95
        
        # 성능 메트릭
        self.optimization_metrics = {
            'total_rewards': 0,
            'average_reward': 0,
            'exploration_count': 0,
            'exploitation_count': 0,
            'best_combination_found': None,
            'optimization_iterations': 0
        }
        
        logger.info("알고리즘 조합 최적화 시스템 초기화 완료")
    
    def generate_algorithm_combinations(self, max_combination_size: int = 3) -> List[List[str]]:
        """알고리즘 조합 생성"""
        try:
            algorithm_ids = list(self.knowledge_base.algorithms.keys())
            combinations = []
            
            # 단일 알고리즘
            combinations.extend([[aid] for aid in algorithm_ids])
            
            # 2개 조합
            if max_combination_size >= 2:
                for i in range(len(algorithm_ids)):
                    for j in range(i + 1, len(algorithm_ids)):
                        combinations.append([algorithm_ids[i], algorithm_ids[j]])
            
            # 3개 조합
            if max_combination_size >= 3:
                for i in range(len(algorithm_ids)):
                    for j in range(i + 1, len(algorithm_ids)):
                        for k in range(j + 1, len(algorithm_ids)):
                            combinations.append([algorithm_ids[i], algorithm_ids[j], algorithm_ids[k]])
            
            self.algorithm_combinations = combinations
            logger.info(f"알고리즘 조합 {len(combinations)}개 생성 완료")
            return combinations
            
        except Exception as e:
            logger.error(f"알고리즘 조합 생성 실패: {e}")
            return []
    
    def initialize_optimization_models(self):
        """최적화 모델들 초기화"""
        try:
            if not self.algorithm_combinations:
                self.generate_algorithm_combinations()
            
            n_combinations = len(self.algorithm_combinations)
            
            # Multi-Armed Bandit 초기화
            self.multi_armed_bandit = MultiArmedBandit(
                n_arms=n_combinations,
                exploration_rate=self.exploration_rate
            )
            
            # UCB (Upper Confidence Bound) 최적화기
            self.ucb_optimizer = UCBAlgorithm(n_combinations)
            
            logger.info(f"최적화 모델 초기화 완료: {n_combinations}개 조합")
            
        except Exception as e:
            logger.error(f"최적화 모델 초기화 실패: {e}")
    
    def evaluate_combination_performance(self, combination: List[str], 
                                       problem_context: Dict[str, Any]) -> float:
        """알고리즘 조합 성능 평가"""
        try:
            if not combination:
                return 0.0
            
            total_score = 0.0
            synergy_bonus = 0.0
            
            # 개별 알고리즘 성능 합계
            for alg_id in combination:
                if alg_id in self.knowledge_base.algorithms:
                    algorithm = self.knowledge_base.algorithms[alg_id]
                    
                    # 기본 성능 점수
                    base_score = (algorithm.success_rate + algorithm.efficiency_score) / 2
                    
                    # 문제 맥락과의 적합성
                    context_score = self._calculate_context_similarity(algorithm, problem_context)
                    
                    # 최종 점수
                    algorithm_score = (base_score * 0.7) + (context_score * 0.3)
                    total_score += algorithm_score
            
            # 시너지 보너스 계산
            if len(combination) > 1:
                synergy_bonus = self._calculate_synergy_bonus(combination)
            
            # 조합 크기에 따른 페널티
            size_penalty = 0.1 * (len(combination) - 1)
            
            # 최종 성능 점수
            final_score = (total_score / len(combination)) + synergy_bonus - size_penalty
            
            return max(0.0, min(1.0, final_score))
            
        except Exception as e:
            logger.error(f"조합 성능 평가 실패: {e}")
            return 0.0
    
    def _calculate_context_similarity(self, algorithm: AlgorithmKnowledge, 
                                    problem_context: Dict[str, Any]) -> float:
        """알고리즘과 문제 맥락 간의 유사도 계산"""
        try:
            similarity_score = 0.0
            
            # 도메인 일치도
            if 'domain' in problem_context:
                domain_match = any(domain in problem_context['domain'] 
                                 for domain in algorithm.applicable_domains)
                if domain_match:
                    similarity_score += 0.3
            
            # 입력 패턴 일치도
            if 'input_pattern' in problem_context:
                pattern_match = any(pattern in problem_context['input_pattern'] 
                                  for pattern in algorithm.input_patterns)
                if pattern_match:
                    similarity_score += 0.4
            
            # 복잡도 적합성
            if 'complexity_requirement' in problem_context:
                complexity_match = self._check_complexity_compatibility(
                    algorithm.complexity, 
                    problem_context['complexity_requirement']
                )
                if complexity_match:
                    similarity_score += 0.3
            
            return similarity_score
            
        except Exception as e:
            logger.error(f"맥락 유사도 계산 실패: {e}")
            return 0.0
    
    def _check_complexity_compatibility(self, algorithm_complexity: str, 
                                      required_complexity: str) -> bool:
        """복잡도 호환성 확인"""
        complexity_order = {
            "O(1)": 1, "O(log n)": 2, "O(n)": 3, "O(n log n)": 4,
            "O(n^2)": 5, "O(n^3)": 6, "O(2^n)": 7
        }
        
        alg_comp = complexity_order.get(algorithm_complexity, 3)
        req_comp = complexity_order.get(required_complexity, 3)
        
        # 알고리즘 복잡도가 요구 복잡도 이하인 경우 적합
        return alg_comp <= req_comp
    
    def _calculate_synergy_bonus(self, combination: List[str]) -> float:
        """알고리즘 조합의 시너지 보너스 계산"""
        try:
            synergy_score = 0.0
            
            for i, alg_id1 in enumerate(combination):
                for j, alg_id2 in enumerate(combination[i+1:], i+1):
                    if alg_id1 in self.knowledge_base.algorithms and alg_id2 in self.knowledge_base.algorithms:
                        alg1 = self.knowledge_base.algorithms[alg_id1]
                        alg2 = self.knowledge_base.algorithms[alg_id2]
                        
                        # 카테고리 상보성
                        if alg1.category != alg2.category:
                            synergy_score += 0.1
                        
                        # 복잡도 균형
                        comp1 = self._extract_complexity_score(alg1.complexity)
                        comp2 = self._extract_complexity_score(alg2.complexity)
                        if abs(comp1 - comp2) <= 1:  # 복잡도가 비슷한 경우
                            synergy_score += 0.05
                        
                        # 도메인 중복성 (낮을수록 좋음)
                        common_domains = set(alg1.applicable_domains) & set(alg2.applicable_domains)
                        if len(common_domains) > 0:
                            synergy_score += 0.02
            
            return min(0.2, synergy_score)  # 최대 0.2점
            
        except Exception as e:
            logger.error(f"시너지 보너스 계산 실패: {e}")
            return 0.0
    
    def _extract_complexity_score(self, complexity: str) -> float:
        """복잡도를 수치로 변환"""
        complexity_mapping = {
            "O(1)": 1.0, "O(log n)": 2.0, "O(n)": 3.0, "O(n log n)": 4.0,
            "O(n^2)": 5.0, "O(n^3)": 6.0, "O(2^n)": 7.0
        }
        
        for pattern, score in complexity_mapping.items():
            if pattern in complexity:
                return score
        
        return 3.0
    
    def optimize_combination(self, problem_context: Dict[str, Any], 
                           iterations: int = 100) -> Dict[str, Any]:
        """알고리즘 조합 최적화 수행"""
        try:
            if not self.multi_armed_bandit:
                self.initialize_optimization_models()
            
            best_combination = None
            best_score = 0.0
            total_reward = 0.0
            
            logger.info(f"알고리즘 조합 최적화 시작: {iterations}회 반복")
            
            for iteration in range(iterations):
                # 팔 선택 (조합 선택)
                selected_arm = self.multi_armed_bandit.select_arm()
                selected_combination = self.algorithm_combinations[selected_arm]
                
                # 성능 평가
                performance_score = self.evaluate_combination_performance(
                    selected_combination, problem_context
                )
                
                # 보상 업데이트
                self.multi_armed_bandit.update(selected_arm, performance_score)
                
                # UCB 업데이트
                self.ucb_optimizer.update(selected_arm, performance_score)
                
                # 최고 성능 조합 업데이트
                if performance_score > best_score:
                    best_score = performance_score
                    best_combination = selected_combination.copy()
                
                total_reward += performance_score
                
                # 최적화 히스토리 기록
                self.optimization_history.append({
                    'iteration': iteration,
                    'selected_combination': selected_combination,
                    'performance_score': performance_score,
                    'exploration': self.multi_armed_bandit.exploration_rate > random.random()
                })
                
                # 진행 상황 로깅
                if (iteration + 1) % 20 == 0:
                    logger.info(f"최적화 진행률: {iteration + 1}/{iterations}, "
                              f"현재 최고 점수: {best_score:.3f}")
            
            # 최적화 메트릭 업데이트
            self.optimization_metrics.update({
                'total_rewards': total_reward,
                'average_reward': total_reward / iterations,
                'best_combination_found': best_combination,
                'optimization_iterations': iterations
            })
            
            # 최적화 결과
            optimization_result = {
                'best_combination': best_combination,
                'best_score': best_score,
                'total_reward': total_reward,
                'average_reward': total_reward / iterations,
                'optimization_history': self.optimization_history[-50:],  # 최근 50개만
                'arm_statistics': self.multi_armed_bandit.get_arm_stats(),
                'optimization_timestamp': datetime.now().isoformat()
            }
            
            logger.info(f"최적화 완료! 최고 점수: {best_score:.3f}")
            logger.info(f"최적 조합: {best_combination}")
            
            return optimization_result
            
        except Exception as e:
            logger.error(f"조합 최적화 실패: {e}")
            return {}
    
    def get_recommended_combinations(self, problem_context: Dict[str, Any], 
                                   top_k: int = 5) -> List[Dict[str, Any]]:
        """상위 K개 알고리즘 조합 추천"""
        try:
            if not self.algorithm_combinations:
                return []
            
            # 모든 조합의 성능 평가
            combination_scores = []
            for combination in self.algorithm_combinations:
                score = self.evaluate_combination_performance(combination, problem_context)
                combination_scores.append({
                    'combination': combination,
                    'score': score,
                    'size': len(combination)
                })
            
            # 점수 기준 정렬
            combination_scores.sort(key=lambda x: x['score'], reverse=True)
            
            # 상위 K개 반환
            top_combinations = []
            for i, item in enumerate(combination_scores[:top_k]):
                recommendation = {
                    'rank': i + 1,
                    'combination': item['combination'],
                    'score': item['score'],
                    'size': item['size'],
                    'algorithms': []
                }
                
                # 알고리즘 상세 정보
                for alg_id in item['combination']:
                    if alg_id in self.knowledge_base.algorithms:
                        alg = self.knowledge_base.algorithms[alg_id]
                        recommendation['algorithms'].append({
                            'id': alg_id,
                            'name': alg.name,
                            'category': alg.category,
                            'success_rate': alg.success_rate,
                            'efficiency_score': alg.efficiency_score
                        })
                
                top_combinations.append(recommendation)
            
            return top_combinations
            
        except Exception as e:
            logger.error(f"조합 추천 실패: {e}")
            return []
    
    def save_optimization_state(self, filepath: str) -> bool:
        """최적화 상태 저장"""
        try:
            state_data = {
                'multi_armed_bandit': self.multi_armed_bandit,
                'ucb_optimizer': self.ucb_optimizer,
                'algorithm_combinations': self.algorithm_combinations,
                'combination_performance': self.combination_performance,
                'optimization_history': self.optimization_history,
                'optimization_metrics': self.optimization_metrics
            }
            
            with open(filepath, 'wb') as f:
                pickle.dump(state_data, f)
            
            logger.info(f"최적화 상태 저장 완료: {filepath}")
            return True
            
        except Exception as e:
            logger.error(f"최적화 상태 저장 실패: {e}")
            return False
    
    def load_optimization_state(self, filepath: str) -> bool:
        """최적화 상태 로드"""
        try:
            with open(filepath, 'rb') as f:
                state_data = pickle.load(f)
            
            self.multi_armed_bandit = state_data['multi_armed_bandit']
            self.ucb_optimizer = state_data['ucb_optimizer']
            self.algorithm_combinations = state_data['algorithm_combinations']
            self.combination_performance = state_data['combination_performance']
            self.optimization_history = state_data['optimization_history']
            self.optimization_metrics = state_data['optimization_metrics']
            
            logger.info(f"최적화 상태 로드 완료: {filepath}")
            return True
            
        except Exception as e:
            logger.error(f"최적화 상태 로드 실패: {e}")
            return False
    
    def get_optimization_metrics(self) -> Dict[str, Any]:
        """최적화 메트릭 반환"""
        return self.optimization_metrics.copy()

class UCBAlgorithm:
    """UCB (Upper Confidence Bound) 알고리즘"""
    
    def __init__(self, n_arms: int):
        self.n_arms = n_arms
        self.arm_counts = np.zeros(n_arms)
        self.arm_rewards = np.zeros(n_arms)
        self.arm_values = np.zeros(n_arms)
        self.total_pulls = 0
    
    def select_arm(self) -> int:
        """UCB 기준으로 팔 선택"""
        if self.total_pulls < self.n_arms:
            # 초기에는 모든 팔을 한 번씩 시도
            return self.total_pulls
        
        # UCB 값 계산
        ucb_values = self.arm_values + np.sqrt(2 * np.log(self.total_pulls) / self.arm_counts)
        return np.argmax(ucb_values)
    
    def update(self, arm: int, reward: float):
        """팔의 보상 업데이트"""
        self.arm_counts[arm] += 1
        self.arm_rewards[arm] += reward
        self.total_pulls += 1
        
        # 평균 보상 계산
        self.arm_values[arm] = self.arm_rewards[arm] / self.arm_counts[arm]
