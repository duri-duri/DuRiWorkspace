#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DuRi Phase Ω: Genetic Programming Engine

이 모듈은 DuRi가 유전자 알고리즘을 기반으로 다양한 목표 달성 루트를 생성하고,
우수한 개체를 선택하여 구조를 진화시키는 메커니즘입니다.

주요 기능:
- 다양한 코드 구조 생성
- 각 구조의 적합도 평가
- 우수한 구조들로 다음 세대 생성
- 진화 알고리즘 기반 구조 탐색
"""

import asyncio
import ast
import json
import logging
import os
import random
import time
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple, Union
import copy

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class EvolutionType(Enum):
    """진화 유형 열거형"""
    STRUCTURE_EVOLUTION = "structure_evolution"
    ALGORITHM_EVOLUTION = "algorithm_evolution"
    LOGIC_EVOLUTION = "logic_evolution"
    PERFORMANCE_EVOLUTION = "performance_evolution"
    ADAPTATION_EVOLUTION = "adaptation_evolution"


class FitnessMetric(Enum):
    """적합도 지표 열거형"""
    PERFORMANCE = "performance"
    COMPLEXITY = "complexity"
    MAINTAINABILITY = "maintainability"
    RELIABILITY = "reliability"
    ADAPTABILITY = "adaptability"


@dataclass
class GeneticIndividual:
    """유전자 개체 데이터 클래스"""
    individual_id: str
    code_structure: str
    fitness_score: float = 0.0
    generation: int = 0
    parents: List[str] = field(default_factory=list)
    mutation_count: int = 0
    crossover_count: int = 0
    created_at: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class EvolutionConfig:
    """진화 설정 데이터 클래스"""
    population_size: int = 50
    elite_size: int = 5
    mutation_rate: float = 0.1
    crossover_rate: float = 0.8
    max_generations: int = 100
    fitness_threshold: float = 0.9
    selection_pressure: float = 0.7


@dataclass
class EvolutionResult:
    """진화 결과 데이터 클래스"""
    best_individual: GeneticIndividual
    final_population: List[GeneticIndividual]
    generation_history: List[Dict[str, Any]]
    total_generations: int
    convergence_generation: int
    final_fitness: float
    evolution_time: float
    success: bool = True
    error_message: Optional[str] = None


class GeneticEvolutionEngine:
    """유전자 알고리즘 기반 진화 엔진"""
    
    def __init__(self, config: Optional[EvolutionConfig] = None):
        """초기화"""
        self.config = config or EvolutionConfig()
        self.population: List[GeneticIndividual] = []
        self.generation_history: List[Dict[str, Any]] = []
        self.current_generation = 0
        self.best_individual: Optional[GeneticIndividual] = None
        
        logger.info("Genetic Evolution Engine 초기화 완료")
    
    async def generate_population(self, seed: str, size: int) -> List[GeneticIndividual]:
        """다양한 코드 구조 생성"""
        try:
            logger.info(f"🧬 인구 생성 시작: 크기={size}")
            
            population = []
            
            # 시드 개체 생성
            seed_individual = GeneticIndividual(
                individual_id=f"seed_{int(time.time() * 1000)}",
                code_structure=seed,
                generation=0,
                fitness_score=0.0
            )
            population.append(seed_individual)
            
            # 변이를 통한 다양한 개체 생성
            for i in range(size - 1):
                mutated_structure = await self._mutate_structure(seed)
                
                individual = GeneticIndividual(
                    individual_id=f"individual_{int(time.time() * 1000)}_{i}",
                    code_structure=mutated_structure,
                    generation=0,
                    fitness_score=0.0,
                    parents=[seed_individual.individual_id]
                )
                population.append(individual)
            
            self.population = population
            logger.info(f"✅ 인구 생성 완료: {len(population)}개 개체")
            
            return population
            
        except Exception as e:
            logger.error(f"인구 생성 실패: {e}")
            return []
    
    async def evaluate_fitness(self, candidate: GeneticIndividual) -> float:
        """각 구조의 적합도 평가"""
        try:
            logger.info(f"🎯 적합도 평가 시작: {candidate.individual_id}")
            
            # 코드 구조 파싱
            try:
                tree = ast.parse(candidate.code_structure)
            except SyntaxError:
                return 0.0  # 문법 오류는 0점
            
            # 다양한 지표로 적합도 계산
            fitness_scores = {}
            
            # 성능 지표
            fitness_scores[FitnessMetric.PERFORMANCE] = await self._evaluate_performance_fitness(tree)
            
            # 복잡도 지표
            fitness_scores[FitnessMetric.COMPLEXITY] = await self._evaluate_complexity_fitness(tree)
            
            # 유지보수성 지표
            fitness_scores[FitnessMetric.MAINTAINABILITY] = await self._evaluate_maintainability_fitness(tree)
            
            # 신뢰성 지표
            fitness_scores[FitnessMetric.RELIABILITY] = await self._evaluate_reliability_fitness(tree)
            
            # 적응성 지표
            fitness_scores[FitnessMetric.ADAPTABILITY] = await self._evaluate_adaptability_fitness(tree)
            
            # 가중 평균으로 최종 적합도 계산
            weights = {
                FitnessMetric.PERFORMANCE: 0.3,
                FitnessMetric.COMPLEXITY: 0.2,
                FitnessMetric.MAINTAINABILITY: 0.2,
                FitnessMetric.RELIABILITY: 0.15,
                FitnessMetric.ADAPTABILITY: 0.15
            }
            
            final_fitness = sum(
                fitness_scores[metric] * weights[metric]
                for metric in FitnessMetric
            )
            
            candidate.fitness_score = final_fitness
            candidate.metadata['fitness_breakdown'] = fitness_scores
            
            logger.info(f"✅ 적합도 평가 완료: {candidate.individual_id} = {final_fitness:.3f}")
            
            return final_fitness
            
        except Exception as e:
            logger.error(f"적합도 평가 실패: {e}")
            return 0.0
    
    async def crossover_and_mutate(self, top_candidates: List[GeneticIndividual]) -> List[GeneticIndividual]:
        """우수한 구조들로 다음 세대 생성"""
        try:
            logger.info(f"🔄 교차 및 변이 시작: {len(top_candidates)}개 후보")
            
            new_population = []
            
            # 엘리트 개체 보존
            elite_size = min(self.config.elite_size, len(top_candidates))
            elite_candidates = sorted(top_candidates, key=lambda x: x.fitness_score, reverse=True)[:elite_size]
            
            for elite in elite_candidates:
                elite_copy = copy.deepcopy(elite)
                elite_copy.generation = self.current_generation + 1
                new_population.append(elite_copy)
            
            # 교차 및 변이로 새 개체 생성
            while len(new_population) < self.config.population_size:
                if random.random() < self.config.crossover_rate and len(top_candidates) >= 2:
                    # 교차
                    parent1, parent2 = random.sample(top_candidates, 2)
                    child_structure = await self._crossover_structures(
                        parent1.code_structure, 
                        parent2.code_structure
                    )
                    
                    child = GeneticIndividual(
                        individual_id=f"child_{int(time.time() * 1000)}_{len(new_population)}",
                        code_structure=child_structure,
                        generation=self.current_generation + 1,
                        parents=[parent1.individual_id, parent2.individual_id],
                        crossover_count=1
                    )
                    
                else:
                    # 변이
                    parent = random.choice(top_candidates)
                    mutated_structure = await self._mutate_structure(parent.code_structure)
                    
                    child = GeneticIndividual(
                        individual_id=f"mutant_{int(time.time() * 1000)}_{len(new_population)}",
                        code_structure=mutated_structure,
                        generation=self.current_generation + 1,
                        parents=[parent.individual_id],
                        mutation_count=1
                    )
                
                new_population.append(child)
            
            logger.info(f"✅ 교차 및 변이 완료: {len(new_population)}개 새 개체")
            
            return new_population
            
        except Exception as e:
            logger.error(f"교차 및 변이 실패: {e}")
            return top_candidates
    
    async def evolve_capabilities(self, seed_code: str, target_goal: str) -> EvolutionResult:
        """능력 진화 실행"""
        try:
            logger.info(f"🚀 능력 진화 시작: 목표={target_goal}")
            start_time = time.time()
            
            # 초기 인구 생성
            initial_population = await self.generate_population(seed_code, self.config.population_size)
            
            # 초기 적합도 평가
            for individual in initial_population:
                await self.evaluate_fitness(individual)
            
            self.population = initial_population
            self.current_generation = 0
            
            # 진화 루프
            convergence_count = 0
            last_best_fitness = 0.0
            
            for generation in range(self.config.max_generations):
                self.current_generation = generation
                
                logger.info(f"🔄 세대 {generation + 1}/{self.config.max_generations} 시작")
                
                # 현재 세대의 최고 개체 찾기
                best_individual = max(self.population, key=lambda x: x.fitness_score)
                
                # 수렴 검사
                if abs(best_individual.fitness_score - last_best_fitness) < 0.001:
                    convergence_count += 1
                else:
                    convergence_count = 0
                
                last_best_fitness = best_individual.fitness_score
                
                # 세대 기록
                generation_info = {
                    'generation': generation + 1,
                    'best_fitness': best_individual.fitness_score,
                    'avg_fitness': sum(x.fitness_score for x in self.population) / len(self.population),
                    'population_size': len(self.population),
                    'best_individual_id': best_individual.individual_id
                }
                self.generation_history.append(generation_info)
                
                # 목표 달성 검사
                if best_individual.fitness_score >= self.config.fitness_threshold:
                    logger.info(f"🎯 목표 달성! 적합도: {best_individual.fitness_score:.3f}")
                    break
                
                # 수렴 검사
                if convergence_count >= 10:
                    logger.info(f"🔄 수렴됨. 진화 중단.")
                    break
                
                # 다음 세대 생성
                top_candidates = await self._select_top_candidates()
                new_population = await self.crossover_and_mutate(top_candidates)
                
                # 새 세대의 적합도 평가
                for individual in new_population:
                    await self.evaluate_fitness(individual)
                
                self.population = new_population
            
            # 최종 결과 생성
            final_best = max(self.population, key=lambda x: x.fitness_score)
            self.best_individual = final_best
            
            result = EvolutionResult(
                best_individual=final_best,
                final_population=self.population,
                generation_history=self.generation_history,
                total_generations=self.current_generation + 1,
                convergence_generation=convergence_count,
                final_fitness=final_best.fitness_score,
                evolution_time=time.time() - start_time
            )
            
            logger.info(f"✅ 능력 진화 완료: 최종 적합도={final_best.fitness_score:.3f}, 세대={self.current_generation + 1}")
            
            return result
            
        except Exception as e:
            logger.error(f"능력 진화 실패: {e}")
            return EvolutionResult(
                best_individual=GeneticIndividual("error", ""),
                final_population=[],
                generation_history=[],
                total_generations=0,
                convergence_generation=0,
                final_fitness=0.0,
                evolution_time=0.0,
                success=False,
                error_message=str(e)
            )
    
    async def _mutate_structure(self, structure: str) -> str:
        """구조 변이"""
        try:
            # 간단한 변이 예시 (실제 구현에서는 더 정교한 변이 로직 필요)
            mutations = [
                # 주석 추가/제거
                lambda s: s + "\n# 변이된 코드\n" if random.random() < 0.3 else s,
                # 공백 조정
                lambda s: s.replace("    ", "  ") if random.random() < 0.2 else s,
                # 줄바꿈 추가
                lambda s: s.replace(";", ";\n") if random.random() < 0.1 else s,
            ]
            
            mutated = structure
            for mutation in mutations:
                if random.random() < self.config.mutation_rate:
                    mutated = mutation(mutated)
            
            return mutated
            
        except Exception as e:
            logger.error(f"구조 변이 실패: {e}")
            return structure
    
    async def _crossover_structures(self, structure1: str, structure2: str) -> str:
        """구조 교차"""
        try:
            # 간단한 교차 예시 (실제 구현에서는 더 정교한 교차 로직 필요)
            lines1 = structure1.split('\n')
            lines2 = structure2.split('\n')
            
            # 교차점 선택
            crossover_point = len(lines1) // 2
            
            # 교차 실행
            child_lines = lines1[:crossover_point] + lines2[crossover_point:]
            
            return '\n'.join(child_lines)
            
        except Exception as e:
            logger.error(f"구조 교차 실패: {e}")
            return structure1
    
    async def _select_top_candidates(self) -> List[GeneticIndividual]:
        """상위 후보 선택"""
        try:
            # 토너먼트 선택
            tournament_size = 3
            selected = []
            
            while len(selected) < self.config.population_size // 2:
                tournament = random.sample(self.population, tournament_size)
                winner = max(tournament, key=lambda x: x.fitness_score)
                selected.append(winner)
            
            return selected
            
        except Exception as e:
            logger.error(f"상위 후보 선택 실패: {e}")
            return self.population[:self.config.population_size // 2]
    
    async def _evaluate_performance_fitness(self, tree: ast.AST) -> float:
        """성능 적합도 평가"""
        try:
            performance_issues = 0
            
            for node in ast.walk(tree):
                # 성능 이슈 패턴 검사
                if isinstance(node, ast.ListComp) and len(node.generators) > 1:
                    performance_issues += 1
                elif isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
                    if node.func.id in ['eval', 'exec']:
                        performance_issues += 2
            
            # 성능 점수 계산 (0-1, 높을수록 좋음)
            performance_score = max(0.0, 1.0 - (performance_issues * 0.1))
            
            return performance_score
            
        except Exception as e:
            logger.error(f"성능 적합도 평가 실패: {e}")
            return 0.5
    
    async def _evaluate_complexity_fitness(self, tree: ast.AST) -> float:
        """복잡도 적합도 평가"""
        try:
            complexity_metrics = {
                'functions': 0,
                'classes': 0,
                'nested_levels': 0
            }
            
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    complexity_metrics['functions'] += 1
                elif isinstance(node, ast.ClassDef):
                    complexity_metrics['classes'] += 1
                elif isinstance(node, ast.If) or isinstance(node, ast.For) or isinstance(node, ast.While):
                    complexity_metrics['nested_levels'] += 1
            
            # 복잡도 점수 계산 (0-1, 낮을수록 좋음)
            complexity_score = max(0.0, 1.0 - (
                complexity_metrics['functions'] * 0.05 +
                complexity_metrics['classes'] * 0.1 +
                complexity_metrics['nested_levels'] * 0.15
            ))
            
            return complexity_score
            
        except Exception as e:
            logger.error(f"복잡도 적합도 평가 실패: {e}")
            return 0.5
    
    async def _evaluate_maintainability_fitness(self, tree: ast.AST) -> float:
        """유지보수성 적합도 평가"""
        try:
            maintainability_issues = 0
            
            for node in ast.walk(tree):
                # 유지보수성 이슈 패턴 검사
                if isinstance(node, ast.FunctionDef) and len(node.args.args) > 5:
                    maintainability_issues += 1
                elif isinstance(node, ast.ClassDef) and len(node.body) > 20:
                    maintainability_issues += 1
            
            # 유지보수성 점수 계산 (0-1, 높을수록 좋음)
            maintainability_score = max(0.0, 1.0 - (maintainability_issues * 0.1))
            
            return maintainability_score
            
        except Exception as e:
            logger.error(f"유지보수성 적합도 평가 실패: {e}")
            return 0.5
    
    async def _evaluate_reliability_fitness(self, tree: ast.AST) -> float:
        """신뢰성 적합도 평가"""
        try:
            reliability_issues = 0
            
            for node in ast.walk(tree):
                # 신뢰성 이슈 패턴 검사
                if isinstance(node, ast.Compare) and len(node.ops) > 1:
                    reliability_issues += 1
                elif isinstance(node, ast.ExceptHandler) and node.type is None:
                    reliability_issues += 1
            
            # 신뢰성 점수 계산 (0-1, 높을수록 좋음)
            reliability_score = max(0.0, 1.0 - (reliability_issues * 0.2))
            
            return reliability_score
            
        except Exception as e:
            logger.error(f"신뢰성 적합도 평가 실패: {e}")
            return 0.5
    
    async def _evaluate_adaptability_fitness(self, tree: ast.AST) -> float:
        """적응성 적합도 평가"""
        try:
            adaptability_score = 0.5  # 기본 점수
            
            # 적응성 지표 검사
            for node in ast.walk(tree):
                # 모듈화된 구조 검사
                if isinstance(node, ast.ClassDef):
                    adaptability_score += 0.1
                elif isinstance(node, ast.FunctionDef):
                    adaptability_score += 0.05
            
            return min(1.0, adaptability_score)
            
        except Exception as e:
            logger.error(f"적응성 적합도 평가 실패: {e}")
            return 0.5


async def main():
    """메인 함수"""
    # Genetic Evolution Engine 인스턴스 생성
    config = EvolutionConfig(
        population_size=20,
        elite_size=3,
        mutation_rate=0.1,
        crossover_rate=0.8,
        max_generations=10,
        fitness_threshold=0.8
    )
    
    genetic_engine = GeneticEvolutionEngine(config)
    
    # 테스트용 시드 코드
    seed_code = """
def example_function():
    result = 0
    for i in range(10):
        result += i
    return result
"""
    
    # 능력 진화 실행
    result = await genetic_engine.evolve_capabilities(seed_code, "성능 최적화")
    
    # 결과 출력
    print("\n" + "="*80)
    print("🧬 Genetic Evolution Engine 테스트 결과")
    print("="*80)
    
    print(f"\n🎯 진화 결과:")
    print(f"  - 최종 적합도: {result.final_fitness:.3f}")
    print(f"  - 총 세대 수: {result.total_generations}")
    print(f"  - 진화 시간: {result.evolution_time:.2f}초")
    print(f"  - 성공 여부: {result.success}")
    
    if result.best_individual:
        print(f"\n🏆 최고 개체:")
        print(f"  - ID: {result.best_individual.individual_id}")
        print(f"  - 적합도: {result.best_individual.fitness_score:.3f}")
        print(f"  - 세대: {result.best_individual.generation}")
        print(f"  - 변이 횟수: {result.best_individual.mutation_count}")
        print(f"  - 교차 횟수: {result.best_individual.crossover_count}")
    
    return result


if __name__ == "__main__":
    asyncio.run(main()) 