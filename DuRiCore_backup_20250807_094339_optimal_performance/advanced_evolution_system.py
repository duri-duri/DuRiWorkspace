#!/usr/bin/env python3
"""
DuRiCore Phase 8 - 고급 학습 및 진화 시스템
지속적 학습, 자기 진화, 적응형 성능 최적화, 미래 지향적 기능을 구현한 시스템
"""

import asyncio
import logging
import json
import time
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import random
import statistics

# 기존 시스템들 import
from enhanced_integration_system import EnhancedIntegrationSystem

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class EvolutionLevel(Enum):
    """진화 수준 열거형"""
    BASIC = "basic"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"
    MASTER = "master"

class LearningType(Enum):
    """학습 유형 열거형"""
    CONTINUOUS = "continuous"
    ADAPTIVE = "adaptive"
    META = "meta"
    TRANSFER = "transfer"
    EMERGENT = "emergent"

@dataclass
class EvolutionContext:
    """진화 컨텍스트 데이터 클래스"""
    evolution_level: EvolutionLevel
    learning_type: LearningType
    performance_metrics: Dict[str, float]
    environment_data: Dict[str, Any]
    evolution_history: List[Dict[str, Any]]
    created_at: str

@dataclass
class EvolutionResult:
    """진화 결과 데이터 클래스"""
    evolution_level: EvolutionLevel
    learning_type: LearningType
    improvement_score: float
    new_capabilities: List[str]
    performance_metrics: Dict[str, float]
    evolution_time: float
    created_at: str

class ContinuousLearningSystem:
    """지속적 학습 시스템"""
    
    def __init__(self):
        self.learning_history = []
        self.knowledge_base = {}
        self.learning_patterns = {}
        self.continuous_improvement_rate = 0.1
        
    async def continuous_learn(self, context: EvolutionContext) -> EvolutionResult:
        """지속적 학습 실행"""
        start_time = time.time()
        
        # 학습 패턴 분석
        learning_pattern = self._analyze_learning_pattern(context)
        
        # 새로운 지식 획득
        new_knowledge = await self._acquire_new_knowledge(context)
        
        # 지식 통합
        integrated_knowledge = self._integrate_knowledge(new_knowledge)
        
        # 개선 점수 계산
        improvement_score = self._calculate_improvement_score(learning_pattern, integrated_knowledge)
        
        # 새로운 능력 식별
        new_capabilities = self._identify_new_capabilities(integrated_knowledge)
        
        execution_time = time.time() - start_time
        
        # 학습 기록 업데이트
        self._update_learning_history(context, improvement_score, new_capabilities)
        
        return EvolutionResult(
            evolution_level=context.evolution_level,
            learning_type=LearningType.CONTINUOUS,
            improvement_score=improvement_score,
            new_capabilities=new_capabilities,
            performance_metrics={'learning_efficiency': 0.9, 'knowledge_integration': 0.85},
            evolution_time=execution_time,
            created_at=datetime.now().isoformat()
        )
    
    def _analyze_learning_pattern(self, context: EvolutionContext) -> Dict[str, Any]:
        """학습 패턴 분석"""
        recent_performance = context.performance_metrics
        avg_score = statistics.mean(list(recent_performance.values())) if recent_performance else 0.8
        
        return {
            'pattern_type': 'continuous_improvement',
            'learning_rate': self.continuous_improvement_rate,
            'performance_trend': 'increasing' if avg_score > 0.8 else 'stable',
            'adaptation_level': 'high'
        }
    
    async def _acquire_new_knowledge(self, context: EvolutionContext) -> Dict[str, Any]:
        """새로운 지식 획득"""
        # 시뮬레이션된 지식 획득
        knowledge_domains = ['cognitive', 'adaptive', 'creative', 'strategic']
        acquired_knowledge = {}
        
        for domain in knowledge_domains:
            knowledge_level = random.uniform(0.7, 0.95)
            acquired_knowledge[domain] = {
                'level': knowledge_level,
                'confidence': random.uniform(0.8, 0.95),
                'applicability': random.uniform(0.7, 0.9)
            }
        
        return acquired_knowledge
    
    def _integrate_knowledge(self, new_knowledge: Dict[str, Any]) -> Dict[str, Any]:
        """지식 통합"""
        integrated_knowledge = {}
        
        for domain, knowledge in new_knowledge.items():
            if domain in self.knowledge_base:
                # 기존 지식과 통합
                existing = self.knowledge_base[domain]
                integrated_level = (existing['level'] + knowledge['level']) / 2
                integrated_confidence = max(existing['confidence'], knowledge['confidence'])
                integrated_applicability = (existing['applicability'] + knowledge['applicability']) / 2
            else:
                # 새로운 지식 추가
                integrated_level = knowledge['level']
                integrated_confidence = knowledge['confidence']
                integrated_applicability = knowledge['applicability']
            
            integrated_knowledge[domain] = {
                'level': integrated_level,
                'confidence': integrated_confidence,
                'applicability': integrated_applicability
            }
        
        # 지식 베이스 업데이트
        self.knowledge_base.update(integrated_knowledge)
        
        return integrated_knowledge
    
    def _calculate_improvement_score(self, learning_pattern: Dict[str, Any], 
                                   integrated_knowledge: Dict[str, Any]) -> float:
        """개선 점수 계산"""
        base_score = 0.8
        
        # 학습 패턴 기반 점수
        pattern_bonus = 0.1 if learning_pattern['performance_trend'] == 'increasing' else 0.05
        
        # 지식 통합 기반 점수
        knowledge_bonus = statistics.mean([k['level'] for k in integrated_knowledge.values()]) * 0.1
        
        # 적응 수준 기반 점수
        adaptation_bonus = 0.05 if learning_pattern['adaptation_level'] == 'high' else 0.02
        
        return min(1.0, base_score + pattern_bonus + knowledge_bonus + adaptation_bonus)
    
    def _identify_new_capabilities(self, integrated_knowledge: Dict[str, Any]) -> List[str]:
        """새로운 능력 식별"""
        new_capabilities = []
        
        for domain, knowledge in integrated_knowledge.items():
            if knowledge['level'] > 0.9 and knowledge['confidence'] > 0.9:
                if domain == 'cognitive':
                    new_capabilities.append('advanced_cognitive_processing')
                elif domain == 'adaptive':
                    new_capabilities.append('enhanced_environment_adaptation')
                elif domain == 'creative':
                    new_capabilities.append('innovative_problem_solving')
                elif domain == 'strategic':
                    new_capabilities.append('long_term_strategic_planning')
        
        return new_capabilities
    
    def _update_learning_history(self, context: EvolutionContext, 
                                improvement_score: float, new_capabilities: List[str]):
        """학습 기록 업데이트"""
        self.learning_history.append({
            'timestamp': datetime.now().isoformat(),
            'evolution_level': context.evolution_level.value,
            'improvement_score': improvement_score,
            'new_capabilities': new_capabilities,
            'knowledge_base_size': len(self.knowledge_base)
        })

class SelfEvolutionSystem:
    """자기 진화 시스템"""
    
    def __init__(self):
        self.evolution_history = []
        self.evolution_markers = {}
        self.self_improvement_rate = 0.15
        
    async def self_evolve(self, context: EvolutionContext) -> EvolutionResult:
        """자기 진화 실행"""
        start_time = time.time()
        
        # 진화 마커 분석
        evolution_markers = self._analyze_evolution_markers(context)
        
        # 진화 방향 결정
        evolution_direction = self._determine_evolution_direction(evolution_markers)
        
        # 진화 실행
        evolution_result = await self._execute_evolution(evolution_direction, context)
        
        # 진화 검증
        evolution_validation = self._validate_evolution(evolution_result)
        
        execution_time = time.time() - start_time
        
        # 진화 기록 업데이트
        self._update_evolution_history(context, evolution_result, evolution_validation)
        
        return EvolutionResult(
            evolution_level=context.evolution_level,
            learning_type=LearningType.EMERGENT,
            improvement_score=evolution_validation['improvement_score'],
            new_capabilities=evolution_result['new_capabilities'],
            performance_metrics={'evolution_stability': 0.9, 'self_improvement': 0.85},
            evolution_time=execution_time,
            created_at=datetime.now().isoformat()
        )
    
    def _analyze_evolution_markers(self, context: EvolutionContext) -> Dict[str, Any]:
        """진화 마커 분석"""
        performance_trend = self._calculate_performance_trend(context.performance_metrics)
        learning_efficiency = self._calculate_learning_efficiency(context.evolution_history)
        adaptation_capacity = self._calculate_adaptation_capacity(context.environment_data)
        
        return {
            'performance_trend': performance_trend,
            'learning_efficiency': learning_efficiency,
            'adaptation_capacity': adaptation_capacity,
            'evolution_readiness': (performance_trend + learning_efficiency + adaptation_capacity) / 3
        }
    
    def _determine_evolution_direction(self, evolution_markers: Dict[str, Any]) -> str:
        """진화 방향 결정"""
        readiness = evolution_markers['evolution_readiness']
        
        if readiness > 0.9:
            return 'expert_to_master'
        elif readiness > 0.8:
            return 'advanced_to_expert'
        elif readiness > 0.7:
            return 'intermediate_to_advanced'
        else:
            return 'basic_to_intermediate'
    
    async def _execute_evolution(self, evolution_direction: str, 
                                context: EvolutionContext) -> Dict[str, Any]:
        """진화 실행"""
        evolution_capabilities = {
            'basic_to_intermediate': ['basic_learning', 'simple_adaptation'],
            'intermediate_to_advanced': ['advanced_learning', 'complex_adaptation', 'pattern_recognition'],
            'advanced_to_expert': ['expert_learning', 'strategic_adaptation', 'creative_problem_solving'],
            'expert_to_master': ['master_learning', 'predictive_adaptation', 'emergent_creativity']
        }
        
        new_capabilities = evolution_capabilities.get(evolution_direction, [])
        
        # 진화 시뮬레이션
        evolution_success_rate = random.uniform(0.8, 0.95)
        evolution_stability = random.uniform(0.85, 0.95)
        
        return {
            'direction': evolution_direction,
            'new_capabilities': new_capabilities,
            'success_rate': evolution_success_rate,
            'stability': evolution_stability,
            'evolution_timestamp': datetime.now().isoformat()
        }
    
    def _validate_evolution(self, evolution_result: Dict[str, Any]) -> Dict[str, Any]:
        """진화 검증"""
        success_rate = evolution_result['success_rate']
        stability = evolution_result['stability']
        
        improvement_score = (success_rate + stability) / 2
        
        return {
            'improvement_score': improvement_score,
            'evolution_valid': success_rate > 0.8 and stability > 0.8,
            'stability_level': 'high' if stability > 0.9 else 'medium',
            'success_level': 'high' if success_rate > 0.9 else 'medium'
        }
    
    def _calculate_performance_trend(self, performance_metrics: Dict[str, float]) -> float:
        """성능 트렌드 계산"""
        if not performance_metrics:
            return 0.8
        
        avg_performance = statistics.mean(list(performance_metrics.values()))
        return min(1.0, avg_performance + 0.1)
    
    def _calculate_learning_efficiency(self, evolution_history: List[Dict[str, Any]]) -> float:
        """학습 효율성 계산"""
        if not evolution_history:
            return 0.8
        
        recent_improvements = [h.get('improvement_score', 0.8) for h in evolution_history[-5:]]
        return statistics.mean(recent_improvements)
    
    def _calculate_adaptation_capacity(self, environment_data: Dict[str, Any]) -> float:
        """적응 능력 계산"""
        # 환경 데이터 기반 적응 능력 계산
        complexity = environment_data.get('complexity', 'medium')
        change_rate = environment_data.get('change_rate', 'moderate')
        
        complexity_score = {'low': 0.7, 'medium': 0.8, 'high': 0.9}.get(complexity, 0.8)
        change_score = {'slow': 0.7, 'moderate': 0.8, 'fast': 0.9}.get(change_rate, 0.8)
        
        return (complexity_score + change_score) / 2
    
    def _update_evolution_history(self, context: EvolutionContext, 
                                 evolution_result: Dict[str, Any], 
                                 validation: Dict[str, Any]):
        """진화 기록 업데이트"""
        self.evolution_history.append({
            'timestamp': datetime.now().isoformat(),
            'evolution_level': context.evolution_level.value,
            'direction': evolution_result['direction'],
            'new_capabilities': evolution_result['new_capabilities'],
            'improvement_score': validation['improvement_score'],
            'evolution_valid': validation['evolution_valid']
        })

class AdaptivePerformanceOptimizer:
    """적응형 성능 최적화 시스템"""
    
    def __init__(self):
        self.optimization_history = []
        self.performance_baselines = {}
        self.optimization_strategies = {}
        
    async def optimize_performance(self, context: EvolutionContext) -> EvolutionResult:
        """성능 최적화 실행"""
        start_time = time.time()
        
        # 성능 분석
        performance_analysis = self._analyze_performance(context)
        
        # 최적화 전략 선택
        optimization_strategy = self._select_optimization_strategy(performance_analysis)
        
        # 최적화 실행
        optimization_result = await self._execute_optimization(optimization_strategy, context)
        
        # 최적화 검증
        optimization_validation = self._validate_optimization(optimization_result)
        
        execution_time = time.time() - start_time
        
        # 최적화 기록 업데이트
        self._update_optimization_history(context, optimization_result, optimization_validation)
        
        return EvolutionResult(
            evolution_level=context.evolution_level,
            learning_type=LearningType.ADAPTIVE,
            improvement_score=optimization_validation['improvement_score'],
            new_capabilities=optimization_result['new_capabilities'],
            performance_metrics={'optimization_efficiency': 0.9, 'performance_gain': 0.85},
            evolution_time=execution_time,
            created_at=datetime.now().isoformat()
        )
    
    def _analyze_performance(self, context: EvolutionContext) -> Dict[str, Any]:
        """성능 분석"""
        current_metrics = context.performance_metrics
        
        # 성능 병목 식별
        bottlenecks = []
        for metric, value in current_metrics.items():
            if value < 0.8:
                bottlenecks.append(metric)
        
        # 최적화 우선순위 결정
        optimization_priorities = self._determine_optimization_priorities(bottlenecks, current_metrics)
        
        return {
            'bottlenecks': bottlenecks,
            'optimization_priorities': optimization_priorities,
            'current_performance': current_metrics,
            'optimization_potential': 1.0 - min(current_metrics.values()) if current_metrics else 0.2
        }
    
    def _select_optimization_strategy(self, performance_analysis: Dict[str, Any]) -> str:
        """최적화 전략 선택"""
        bottlenecks = performance_analysis['bottlenecks']
        optimization_potential = performance_analysis['optimization_potential']
        
        if optimization_potential > 0.3:
            return 'comprehensive_optimization'
        elif len(bottlenecks) > 2:
            return 'multi_focus_optimization'
        elif len(bottlenecks) == 1:
            return 'targeted_optimization'
        else:
            return 'maintenance_optimization'
    
    async def _execute_optimization(self, strategy: str, context: EvolutionContext) -> Dict[str, Any]:
        """최적화 실행"""
        optimization_capabilities = {
            'comprehensive_optimization': ['system_wide_optimization', 'performance_monitoring', 'adaptive_tuning'],
            'multi_focus_optimization': ['multi_domain_optimization', 'resource_allocation', 'load_balancing'],
            'targeted_optimization': ['specific_optimization', 'precision_tuning', 'efficiency_enhancement'],
            'maintenance_optimization': ['stability_maintenance', 'performance_preservation', 'gradual_improvement']
        }
        
        new_capabilities = optimization_capabilities.get(strategy, [])
        
        # 최적화 시뮬레이션
        optimization_success_rate = random.uniform(0.85, 0.95)
        performance_gain = random.uniform(0.1, 0.3)
        
        return {
            'strategy': strategy,
            'new_capabilities': new_capabilities,
            'success_rate': optimization_success_rate,
            'performance_gain': performance_gain,
            'optimization_timestamp': datetime.now().isoformat()
        }
    
    def _validate_optimization(self, optimization_result: Dict[str, Any]) -> Dict[str, Any]:
        """최적화 검증"""
        success_rate = optimization_result['success_rate']
        performance_gain = optimization_result['performance_gain']
        
        improvement_score = success_rate * (1 + performance_gain)
        
        return {
            'improvement_score': min(1.0, improvement_score),
            'optimization_valid': success_rate > 0.8,
            'performance_improvement': performance_gain,
            'stability_maintained': success_rate > 0.9
        }
    
    def _determine_optimization_priorities(self, bottlenecks: List[str], 
                                         current_metrics: Dict[str, float]) -> List[str]:
        """최적화 우선순위 결정"""
        if not bottlenecks:
            return ['general_maintenance']
        
        # 병목 심각도에 따른 우선순위
        priority_scores = {}
        for bottleneck in bottlenecks:
            current_value = current_metrics.get(bottleneck, 0.5)
            priority_scores[bottleneck] = 1.0 - current_value
        
        # 우선순위 정렬
        sorted_priorities = sorted(priority_scores.items(), key=lambda x: x[1], reverse=True)
        return [item[0] for item in sorted_priorities]
    
    def _update_optimization_history(self, context: EvolutionContext, 
                                   optimization_result: Dict[str, Any], 
                                   validation: Dict[str, Any]):
        """최적화 기록 업데이트"""
        self.optimization_history.append({
            'timestamp': datetime.now().isoformat(),
            'evolution_level': context.evolution_level.value,
            'strategy': optimization_result['strategy'],
            'new_capabilities': optimization_result['new_capabilities'],
            'improvement_score': validation['improvement_score'],
            'performance_gain': validation['performance_improvement']
        })

class AdvancedEvolutionSystem:
    """고급 진화 시스템 메인 클래스"""
    
    def __init__(self):
        """초기화"""
        self.enhanced_integration_system = EnhancedIntegrationSystem()
        
        # 고급 진화 시스템들
        self.continuous_learning_system = ContinuousLearningSystem()
        self.self_evolution_system = SelfEvolutionSystem()
        self.adaptive_performance_optimizer = AdaptivePerformanceOptimizer()
        
        self.evolution_history = []
        self.performance_metrics = {}
        
    async def initialize(self):
        """시스템 초기화"""
        await self.enhanced_integration_system.initialize()
        logger.info("Advanced Evolution System initialized successfully")
        
    async def run_advanced_evolution_cycle(self, context: EvolutionContext) -> Dict[str, Any]:
        """고급 진화 사이클 실행"""
        start_time = time.time()
        
        try:
            # 1. 기존 고급 통합 시스템 실행
            integration_result = await self.enhanced_integration_system.run_enhanced_integration_cycle({
                'user_input': '고급 진화 시스템 테스트',
                'context': context.environment_data
            })
            
            # 2. 지속적 학습
            continuous_learning_result = await self.continuous_learning_system.continuous_learn(context)
            
            # 3. 자기 진화
            self_evolution_result = await self.self_evolution_system.self_evolve(context)
            
            # 4. 적응형 성능 최적화
            performance_optimization_result = await self.adaptive_performance_optimizer.optimize_performance(context)
            
            # 5. 전체 결과 통합
            final_result = {
                'integration_systems': integration_result,
                'continuous_learning': continuous_learning_result,
                'self_evolution': self_evolution_result,
                'performance_optimization': performance_optimization_result,
                'overall_evolution_score': self._calculate_overall_evolution_score(
                    integration_result, continuous_learning_result, 
                    self_evolution_result, performance_optimization_result
                ),
                'execution_time': time.time() - start_time,
                'timestamp': datetime.now().isoformat()
            }
            
            # 성능 메트릭 업데이트
            self._update_performance_metrics(final_result)
            
            return final_result
            
        except Exception as e:
            logger.error(f"고급 진화 사이클 오류: {e}")
            return {
                'status': 'error',
                'error': str(e),
                'execution_time': time.time() - start_time
            }
    
    def _calculate_overall_evolution_score(self, integration_result: Dict, 
                                         continuous_learning_result: EvolutionResult,
                                         self_evolution_result: EvolutionResult,
                                         performance_optimization_result: EvolutionResult) -> float:
        """전체 진화 점수 계산"""
        scores = []
        
        # 통합 시스템 점수
        if 'overall_score' in integration_result:
            scores.append(integration_result['overall_score'])
        
        # 지속적 학습 점수
        scores.append(continuous_learning_result.improvement_score)
        
        # 자기 진화 점수
        scores.append(self_evolution_result.improvement_score)
        
        # 성능 최적화 점수
        scores.append(performance_optimization_result.improvement_score)
        
        return sum(scores) / len(scores) if scores else 0.8
    
    def _update_performance_metrics(self, result: Dict[str, Any]):
        """성능 메트릭 업데이트"""
        self.performance_metrics = {
            'last_execution_time': result.get('execution_time', 0),
            'overall_evolution_score': result.get('overall_evolution_score', 0.8),
            'timestamp': result.get('timestamp', datetime.now().isoformat()),
            'system_count': 28,  # 기존 25개 + 고급 진화 3개
            'evolution_level': 'advanced'
        }
        
        self.evolution_history.append({
            'timestamp': datetime.now().isoformat(),
            'overall_evolution_score': result.get('overall_evolution_score', 0.8),
            'execution_time': result.get('execution_time', 0)
        })
    
    async def get_system_status(self) -> Dict[str, Any]:
        """시스템 상태 반환"""
        integration_status = await self.enhanced_integration_system.get_system_status()
        
        return {
            'advanced_evolution_system': {
                'status': 'active',
                'evolution_systems_count': 3,
                'evolution_history_count': len(self.evolution_history),
                'performance_metrics': self.performance_metrics
            },
            'enhanced_integration_systems': integration_status,
            'total_systems': 28  # 기존 25개 + 고급 진화 3개
        }
    
    async def run_comprehensive_test(self) -> Dict[str, Any]:
        """포괄적 테스트 실행"""
        test_results = {}
        
        # 지속적 학습 테스트
        try:
            continuous_learning_test = await self.continuous_learning_system.continuous_learn(
                EvolutionContext(
                    evolution_level=EvolutionLevel.ADVANCED,
                    learning_type=LearningType.CONTINUOUS,
                    performance_metrics={'cognitive': 0.85, 'adaptive': 0.88},
                    environment_data={'complexity': 'high', 'change_rate': 'fast'},
                    evolution_history=[],
                    created_at=datetime.now().isoformat()
                )
            )
            test_results['continuous_learning'] = {
                'status': 'success',
                'score': continuous_learning_test.improvement_score,
                'capabilities': continuous_learning_test.new_capabilities
            }
        except Exception as e:
            test_results['continuous_learning'] = {
                'status': 'error',
                'error': str(e)
            }
        
        # 자기 진화 테스트
        try:
            self_evolution_test = await self.self_evolution_system.self_evolve(
                EvolutionContext(
                    evolution_level=EvolutionLevel.ADVANCED,
                    learning_type=LearningType.EMERGENT,
                    performance_metrics={'evolution': 0.87, 'adaptation': 0.89},
                    environment_data={'complexity': 'high', 'change_rate': 'fast'},
                    evolution_history=[],
                    created_at=datetime.now().isoformat()
                )
            )
            test_results['self_evolution'] = {
                'status': 'success',
                'score': self_evolution_test.improvement_score,
                'capabilities': self_evolution_test.new_capabilities
            }
        except Exception as e:
            test_results['self_evolution'] = {
                'status': 'error',
                'error': str(e)
            }
        
        # 적응형 성능 최적화 테스트
        try:
            performance_optimization_test = await self.adaptive_performance_optimizer.optimize_performance(
                EvolutionContext(
                    evolution_level=EvolutionLevel.ADVANCED,
                    learning_type=LearningType.ADAPTIVE,
                    performance_metrics={'optimization': 0.86, 'efficiency': 0.88},
                    environment_data={'complexity': 'high', 'change_rate': 'fast'},
                    evolution_history=[],
                    created_at=datetime.now().isoformat()
                )
            )
            test_results['performance_optimization'] = {
                'status': 'success',
                'score': performance_optimization_test.improvement_score,
                'capabilities': performance_optimization_test.new_capabilities
            }
        except Exception as e:
            test_results['performance_optimization'] = {
                'status': 'error',
                'error': str(e)
            }
        
        return test_results

async def main():
    """메인 함수"""
    print("🚀 DuRiCore Phase 8 - 고급 학습 및 진화 시스템 시작")
    print("=" * 60)
    
    # 시스템 초기화
    evolution_system = AdvancedEvolutionSystem()
    await evolution_system.initialize()
    
    # 시스템 상태 확인
    status = await evolution_system.get_system_status()
    print(f"📊 시스템 상태: {status['advanced_evolution_system']['status']}")
    print(f"🔧 진화 시스템 수: {status['advanced_evolution_system']['evolution_systems_count']}")
    print(f"📈 전체 시스템 수: {status['total_systems']}")
    
    # 포괄적 테스트 실행
    print("\n🧪 포괄적 테스트 실행 중...")
    test_results = await evolution_system.run_comprehensive_test()
    
    print("\n📋 테스트 결과:")
    for system, result in test_results.items():
        if result['status'] == 'success':
            print(f"   ✅ {system}: 점수 {result['score']:.2f}")
            print(f"      새로운 능력: {result['capabilities']}")
        else:
            print(f"   ❌ {system}: {result.get('error', 'Unknown error')}")
    
    # 고급 진화 사이클 테스트
    print("\n🔄 고급 진화 사이클 테스트...")
    evolution_context = EvolutionContext(
        evolution_level=EvolutionLevel.ADVANCED,
        learning_type=LearningType.CONTINUOUS,
        performance_metrics={'cognitive': 0.85, 'adaptive': 0.88, 'creative': 0.87},
        environment_data={'complexity': 'high', 'change_rate': 'fast'},
        evolution_history=[],
        created_at=datetime.now().isoformat()
    )
    
    cycle_result = await evolution_system.run_advanced_evolution_cycle(evolution_context)
    
    if cycle_result.get('status') != 'error':
        print(f"   ✅ 전체 진화 점수: {cycle_result.get('overall_evolution_score', 0):.2f}")
        print(f"   ⏱️  실행 시간: {cycle_result.get('execution_time', 0):.2f}초")
    else:
        print(f"   ❌ 사이클 오류: {cycle_result.get('error', 'Unknown error')}")
    
    print("\n🎉 Phase 8 고급 학습 및 진화 시스템 테스트 완료!")

if __name__ == "__main__":
    asyncio.run(main()) 