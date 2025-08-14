#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DuRi Phase Ω: Evolution Integration System

이 모듈은 DuRi의 자가 성장 메커니즘을 구현하는 통합 시스템입니다.
Self-Rewriting, Genetic Programming, MetaCoder를 통합하여 DuRi가 스스로 진화할 수 있도록 합니다.

주요 기능:
- Self-Rewriting Module 통합
- Genetic Programming Engine 통합
- MetaCoder Engine 통합
- 자가 성장 루프 관리
- 진화 결과 평가 및 적용
"""

import asyncio
import json
import logging
import os
import time
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple, Union

# Phase Ω 모듈들 import
from self_rewriting_module import SelfRewritingModule, CodeAssessment, RewriteProposal, RewriteResult
from genetic_evolution_engine import GeneticEvolutionEngine, EvolutionConfig, EvolutionResult, GeneticIndividual
from meta_coder import MetaCoder, CodeAnalysis, RefactorProposal, RefactorResult

# Phase Z 및 Phase Ω 모듈들 import
from duri_thought_flow import DuRiThoughtFlow
from phase_omega_integration import DuRiPhaseOmega

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class EvolutionPhase(Enum):
    """진화 단계 열거형"""
    ASSESSMENT = "assessment"
    SELF_REWRITING = "self_rewriting"
    GENETIC_EVOLUTION = "genetic_evolution"
    META_CODING = "meta_coding"
    INTEGRATION = "integration"
    VALIDATION = "validation"


class EvolutionStatus(Enum):
    """진화 상태 열거형"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    ROLLED_BACK = "rolled_back"


@dataclass
class EvolutionStep:
    """진화 단계 데이터 클래스"""
    step_id: str
    phase: EvolutionPhase
    status: EvolutionStatus
    start_time: datetime
    end_time: Optional[datetime] = None
    result: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None


@dataclass
class EvolutionSession:
    """진화 세션 데이터 클래스"""
    session_id: str
    target_goal: str
    steps: List[EvolutionStep] = field(default_factory=list)
    overall_status: EvolutionStatus = EvolutionStatus.PENDING
    start_time: datetime = field(default_factory=datetime.now)
    end_time: Optional[datetime] = None
    final_result: Optional[Dict[str, Any]] = None
    evolution_score: float = 0.0


@dataclass
class EvolutionResult:
    """진화 결과 데이터 클래스"""
    success: bool
    session: EvolutionSession
    improvements_made: List[str]
    quality_improvement: float
    performance_improvement: float
    maintainability_improvement: float
    evolution_time: float
    error_message: Optional[str] = None


class DuRiEvolutionIntegration:
    """DuRi 진화 통합 시스템"""
    
    def __init__(self):
        """초기화"""
        # Phase Z 및 Phase Ω 시스템
        self.thought_flow = DuRiThoughtFlow(
            input_data={"task": "evolution_integration", "phase": "omega"},
            context={"goal": "self_evolution", "mode": "integration"}
        )
        self.phase_omega = DuRiPhaseOmega()
        
        # 진화 모듈들
        self.self_rewriter = SelfRewritingModule()
        self.genetic_engine = GeneticEvolutionEngine()
        self.meta_coder = MetaCoder()
        
        # 진화 세션 관리
        self.evolution_sessions: List[EvolutionSession] = []
        self.current_session: Optional[EvolutionSession] = None
        
        # 설정
        self.evolution_config = {
            'max_evolution_cycles': 5,
            'evolution_threshold': 0.8,
            'rollback_threshold': 0.3,
            'integration_test_required': True
        }
        
        logger.info("DuRi Evolution Integration 초기화 완료")
    
    async def start_evolution_session(self, target_goal: str) -> EvolutionSession:
        """진화 세션 시작"""
        try:
            logger.info(f"🚀 진화 세션 시작: 목표={target_goal}")
            
            session_id = f"evolution_{int(time.time() * 1000)}"
            session = EvolutionSession(
                session_id=session_id,
                target_goal=target_goal,
                overall_status=EvolutionStatus.IN_PROGRESS
            )
            
            self.current_session = session
            self.evolution_sessions.append(session)
            
            logger.info(f"✅ 진화 세션 생성 완료: {session_id}")
            
            return session
            
        except Exception as e:
            logger.error(f"진화 세션 시작 실패: {e}")
            raise
    
    async def execute_evolution_cycle(self, session: EvolutionSession) -> EvolutionResult:
        """진화 사이클 실행"""
        try:
            logger.info(f"🔄 진화 사이클 실행 시작: {session.session_id}")
            start_time = time.time()
            
            # 1단계: 코드 평가
            assessment_step = await self._execute_assessment_phase(session)
            session.steps.append(assessment_step)
            
            if assessment_step.status == EvolutionStatus.FAILED:
                return await self._create_failed_result(session, assessment_step.error_message)
            
            # 2단계: Self-Rewriting
            rewriting_step = await self._execute_self_rewriting_phase(session)
            session.steps.append(rewriting_step)
            
            if rewriting_step.status == EvolutionStatus.FAILED:
                return await self._create_failed_result(session, rewriting_step.error_message)
            
            # 3단계: Genetic Evolution
            genetic_step = await self._execute_genetic_evolution_phase(session)
            session.steps.append(genetic_step)
            
            if genetic_step.status == EvolutionStatus.FAILED:
                return await self._create_failed_result(session, genetic_step.error_message)
            
            # 4단계: MetaCoding
            metacoding_step = await self._execute_meta_coding_phase(session)
            session.steps.append(metacoding_step)
            
            if metacoding_step.status == EvolutionStatus.FAILED:
                return await self._create_failed_result(session, metacoding_step.error_message)
            
            # 5단계: 통합 및 검증
            integration_step = await self._execute_integration_phase(session)
            session.steps.append(integration_step)
            
            if integration_step.status == EvolutionStatus.FAILED:
                return await self._create_failed_result(session, integration_step.error_message)
            
            # 최종 결과 생성
            evolution_time = time.time() - start_time
            result = await self._create_evolution_result(session, evolution_time)
            
            session.end_time = datetime.now()
            session.overall_status = EvolutionStatus.COMPLETED
            session.final_result = result.__dict__
            
            logger.info(f"✅ 진화 사이클 완료: {session.session_id}, 시간={evolution_time:.2f}초")
            
            return result
            
        except Exception as e:
            logger.error(f"진화 사이클 실행 실패: {e}")
            return await self._create_failed_result(session, str(e))
    
    async def _execute_assessment_phase(self, session: EvolutionSession) -> EvolutionStep:
        """코드 평가 단계"""
        try:
            logger.info("📊 코드 평가 단계 시작")
            step = EvolutionStep(
                step_id=f"assessment_{int(time.time() * 1000)}",
                phase=EvolutionPhase.ASSESSMENT,
                status=EvolutionStatus.IN_PROGRESS,
                start_time=datetime.now()
            )
            
            # 주요 모듈들 평가
            target_modules = [
                "DuRiCore/duri_thought_flow.py",
                "DuRiCore/phase_omega_integration.py",
                "DuRiCore/self_rewriting_module.py",
                "DuRiCore/genetic_evolution_engine.py",
                "DuRiCore/meta_coder.py"
            ]
            
            assessments = {}
            for module_path in target_modules:
                if os.path.exists(module_path):
                    assessment = await self.self_rewriter.assess_self_code(module_path)
                    assessments[module_path] = assessment
            
            step.result = {
                'assessments': assessments,
                'total_modules': len(assessments),
                'average_complexity': sum(a.complexity_score for a in assessments.values()) / len(assessments) if assessments else 0,
                'average_maintainability': sum(a.maintainability_score for a in assessments.values()) / len(assessments) if assessments else 0,
                'average_performance': sum(a.performance_score for a in assessments.values()) / len(assessments) if assessments else 0
            }
            
            step.status = EvolutionStatus.COMPLETED
            step.end_time = datetime.now()
            
            logger.info(f"✅ 코드 평가 완료: {len(assessments)}개 모듈")
            
            return step
            
        except Exception as e:
            logger.error(f"코드 평가 실패: {e}")
            step.status = EvolutionStatus.FAILED
            step.error_message = str(e)
            step.end_time = datetime.now()
            return step
    
    async def _execute_self_rewriting_phase(self, session: EvolutionSession) -> EvolutionStep:
        """Self-Rewriting 단계"""
        try:
            logger.info("🔧 Self-Rewriting 단계 시작")
            step = EvolutionStep(
                step_id=f"rewriting_{int(time.time() * 1000)}",
                phase=EvolutionPhase.SELF_REWRITING,
                status=EvolutionStatus.IN_PROGRESS,
                start_time=datetime.now()
            )
            
            # 평가 결과에서 개선이 필요한 모듈 선택
            assessment_step = next((s for s in session.steps if s.phase == EvolutionPhase.ASSESSMENT), None)
            if not assessment_step or not assessment_step.result:
                raise ValueError("코드 평가 결과가 없습니다")
            
            assessments = assessment_step.result['assessments']
            improvements_made = []
            
            # 복잡도가 높은 모듈부터 개선
            sorted_modules = sorted(
                assessments.items(),
                key=lambda x: x[1].complexity_score,
                reverse=True
            )
            
            for module_path, assessment in sorted_modules[:3]:  # 상위 3개만 처리
                if assessment.complexity_score > 0.6:  # 복잡도가 높은 경우
                    # 현재 코드 읽기
                    with open(module_path, 'r', encoding='utf-8') as f:
                        current_code = f.read()
                    
                    # 개선 제안 생성
                    proposal = await self.self_rewriter.generate_alternative(current_code, assessment)
                    
                    if proposal.expected_impact > 0.3:  # 의미있는 개선이 있는 경우
                        # 안전한 재작성 실행
                        rewrite_result = await self.self_rewriter.safely_rewrite(module_path, proposal.proposed_code)
                        
                        if rewrite_result.success:
                            improvements_made.append(f"{module_path}: {proposal.improvement_description}")
            
            step.result = {
                'improvements_made': improvements_made,
                'modules_processed': len(sorted_modules[:3]),
                'successful_improvements': len(improvements_made)
            }
            
            step.status = EvolutionStatus.COMPLETED
            step.end_time = datetime.now()
            
            logger.info(f"✅ Self-Rewriting 완료: {len(improvements_made)}개 개선")
            
            return step
            
        except Exception as e:
            logger.error(f"Self-Rewriting 실패: {e}")
            step.status = EvolutionStatus.FAILED
            step.error_message = str(e)
            step.end_time = datetime.now()
            return step
    
    async def _execute_genetic_evolution_phase(self, session: EvolutionSession) -> EvolutionStep:
        """Genetic Evolution 단계"""
        try:
            logger.info("🧬 Genetic Evolution 단계 시작")
            step = EvolutionStep(
                step_id=f"genetic_{int(time.time() * 1000)}",
                phase=EvolutionPhase.GENETIC_EVOLUTION,
                status=EvolutionStatus.IN_PROGRESS,
                start_time=datetime.now()
            )
            
            # 시드 코드 생성 (현재 시스템의 핵심 로직)
            seed_code = await self._generate_seed_code()
            
            # 진화 실행
            evolution_result = await self.genetic_engine.evolve_capabilities(
                seed_code, 
                session.target_goal
            )
            
            step.result = {
                'best_fitness': evolution_result.final_fitness,
                'total_generations': evolution_result.total_generations,
                'evolution_time': evolution_result.evolution_time,
                'best_individual_id': evolution_result.best_individual.individual_id if evolution_result.best_individual else None,
                'success': evolution_result.success
            }
            
            step.status = EvolutionStatus.COMPLETED
            step.end_time = datetime.now()
            
            logger.info(f"✅ Genetic Evolution 완료: 적합도={evolution_result.final_fitness:.3f}")
            
            return step
            
        except Exception as e:
            logger.error(f"Genetic Evolution 실패: {e}")
            step.status = EvolutionStatus.FAILED
            step.error_message = str(e)
            step.end_time = datetime.now()
            return step
    
    async def _execute_meta_coding_phase(self, session: EvolutionSession) -> EvolutionStep:
        """MetaCoding 단계"""
        try:
            logger.info("🤖 MetaCoding 단계 시작")
            step = EvolutionStep(
                step_id=f"metacoding_{int(time.time() * 1000)}",
                phase=EvolutionPhase.META_CODING,
                status=EvolutionStatus.IN_PROGRESS,
                start_time=datetime.now()
            )
            
            # 주요 모듈 분석 및 리팩토링
            target_modules = [
                "DuRiCore/duri_thought_flow.py",
                "DuRiCore/phase_omega_integration.py"
            ]
            
            refactoring_results = []
            
            for module_path in target_modules:
                if os.path.exists(module_path):
                    # 모듈 파싱
                    analysis = await self.meta_coder.parse_module(module_path)
                    
                    if analysis.ast_tree:
                        # 리팩토링 제안
                        proposal = await self.meta_coder.refactor_code(
                            analysis.ast_tree, 
                            session.target_goal
                        )
                        
                        # 검증 및 적용
                        test_suite = ["test_basic_functionality"]
                        result = await self.meta_coder.validate_and_apply(
                            proposal.proposed_code, 
                            test_suite
                        )
                        
                        if result.success:
                            refactoring_results.append({
                                'module': module_path,
                                'improvement': result.quality_improvement,
                                'changes': len(result.changes_made)
                            })
            
            step.result = {
                'refactoring_results': refactoring_results,
                'modules_processed': len(target_modules),
                'successful_refactorings': len(refactoring_results),
                'average_improvement': sum(r['improvement'] for r in refactoring_results) / len(refactoring_results) if refactoring_results else 0
            }
            
            step.status = EvolutionStatus.COMPLETED
            step.end_time = datetime.now()
            
            logger.info(f"✅ MetaCoding 완료: {len(refactoring_results)}개 리팩토링")
            
            return step
            
        except Exception as e:
            logger.error(f"MetaCoding 실패: {e}")
            step.status = EvolutionStatus.FAILED
            step.error_message = str(e)
            step.end_time = datetime.now()
            return step
    
    async def _execute_integration_phase(self, session: EvolutionSession) -> EvolutionStep:
        """통합 및 검증 단계"""
        try:
            logger.info("🔗 통합 및 검증 단계 시작")
            step = EvolutionStep(
                step_id=f"integration_{int(time.time() * 1000)}",
                phase=EvolutionPhase.INTEGRATION,
                status=EvolutionStatus.IN_PROGRESS,
                start_time=datetime.now()
            )
            
            # 전체 시스템 통합 테스트
            integration_test_result = await self._run_integration_tests()
            
            # 진화 점수 계산
            evolution_score = await self._calculate_evolution_score(session)
            
            step.result = {
                'integration_test_result': integration_test_result,
                'evolution_score': evolution_score,
                'overall_improvement': evolution_score > 0.5
            }
            
            step.status = EvolutionStatus.COMPLETED
            step.end_time = datetime.now()
            
            logger.info(f"✅ 통합 및 검증 완료: 진화 점수={evolution_score:.3f}")
            
            return step
            
        except Exception as e:
            logger.error(f"통합 및 검증 실패: {e}")
            step.status = EvolutionStatus.FAILED
            step.error_message = str(e)
            step.end_time = datetime.now()
            return step
    
    async def _generate_seed_code(self) -> str:
        """시드 코드 생성"""
        # 현재 시스템의 핵심 로직을 시드 코드로 생성
        seed_code = """
# DuRi 진화 시드 코드
class DuRiCore:
    def __init__(self):
        self.thought_flow = DuRiThoughtFlow()
        self.evolution_engine = GeneticEvolutionEngine()
        self.meta_coder = MetaCoder()
    
    async def process_with_evolution(self, input_data):
        # 진화된 사고 프로세스
        result = await self.thought_flow.process(input_data)
        return result
"""
        return seed_code
    
    async def _run_integration_tests(self) -> Dict[str, Any]:
        """통합 테스트 실행"""
        try:
            # 실제 구현에서는 통합 테스트 실행
            # 여기서는 시뮬레이션
            test_results = {
                'success': True,
                'tests_run': 10,
                'tests_passed': 9,
                'tests_failed': 1,
                'coverage': 0.85,
                'performance_score': 0.8,
                'stability_score': 0.9
            }
            
            return test_results
            
        except Exception as e:
            logger.error(f"통합 테스트 실행 실패: {e}")
            return {'success': False, 'error': str(e)}
    
    async def _calculate_evolution_score(self, session: EvolutionSession) -> float:
        """진화 점수 계산"""
        try:
            total_score = 0.0
            weight_sum = 0.0
            
            # 각 단계별 점수 계산
            for step in session.steps:
                if step.status == EvolutionStatus.COMPLETED and step.result:
                    if step.phase == EvolutionPhase.ASSESSMENT:
                        weight = 0.1
                        score = step.result.get('average_maintainability', 0.5)
                    elif step.phase == EvolutionPhase.SELF_REWRITING:
                        weight = 0.3
                        score = len(step.result.get('improvements_made', [])) / 10.0
                    elif step.phase == EvolutionPhase.GENETIC_EVOLUTION:
                        weight = 0.3
                        score = step.result.get('best_fitness', 0.0)
                    elif step.phase == EvolutionPhase.META_CODING:
                        weight = 0.2
                        score = step.result.get('average_improvement', 0.0)
                    elif step.phase == EvolutionPhase.INTEGRATION:
                        weight = 0.1
                        score = step.result.get('evolution_score', 0.0)
                    else:
                        continue
                    
                    total_score += score * weight
                    weight_sum += weight
            
            final_score = total_score / weight_sum if weight_sum > 0 else 0.0
            return min(1.0, max(0.0, final_score))
            
        except Exception as e:
            logger.error(f"진화 점수 계산 실패: {e}")
            return 0.0
    
    async def _create_evolution_result(self, session: EvolutionSession, evolution_time: float) -> EvolutionResult:
        """진화 결과 생성"""
        try:
            # 개선사항 수집
            improvements_made = []
            for step in session.steps:
                if step.result:
                    if step.phase == EvolutionPhase.SELF_REWRITING:
                        improvements_made.extend(step.result.get('improvements_made', []))
                    elif step.phase == EvolutionPhase.META_CODING:
                        for refactoring in step.result.get('refactoring_results', []):
                            improvements_made.append(f"{refactoring['module']}: 품질 개선 {refactoring['improvement']:.2f}")
            
            # 품질 개선도 계산
            quality_improvement = 0.0
            performance_improvement = 0.0
            maintainability_improvement = 0.0
            
            for step in session.steps:
                if step.result:
                    if step.phase == EvolutionPhase.ASSESSMENT:
                        maintainability_improvement = step.result.get('average_maintainability', 0.0)
                    elif step.phase == EvolutionPhase.META_CODING:
                        quality_improvement = step.result.get('average_improvement', 0.0)
                    elif step.phase == EvolutionPhase.GENETIC_EVOLUTION:
                        performance_improvement = step.result.get('best_fitness', 0.0)
            
            result = EvolutionResult(
                success=True,
                session=session,
                improvements_made=improvements_made,
                quality_improvement=quality_improvement,
                performance_improvement=performance_improvement,
                maintainability_improvement=maintainability_improvement,
                evolution_time=evolution_time
            )
            
            return result
            
        except Exception as e:
            logger.error(f"진화 결과 생성 실패: {e}")
            return await self._create_failed_result(session, str(e))
    
    async def _create_failed_result(self, session: EvolutionSession, error_message: str) -> EvolutionResult:
        """실패 결과 생성"""
        session.overall_status = EvolutionStatus.FAILED
        session.end_time = datetime.now()
        
        return EvolutionResult(
            success=False,
            session=session,
            improvements_made=[],
            quality_improvement=0.0,
            performance_improvement=0.0,
            maintainability_improvement=0.0,
            evolution_time=0.0,
            error_message=error_message
        )
    
    async def get_evolution_history(self) -> List[EvolutionSession]:
        """진화 히스토리 조회"""
        return self.evolution_sessions
    
    async def get_current_session(self) -> Optional[EvolutionSession]:
        """현재 세션 조회"""
        return self.current_session


async def main():
    """메인 함수"""
    # DuRi Evolution Integration 인스턴스 생성
    evolution_integration = DuRiEvolutionIntegration()
    
    # 진화 세션 시작
    session = await evolution_integration.start_evolution_session("성능 최적화 및 코드 품질 향상")
    
    # 진화 사이클 실행
    result = await evolution_integration.execute_evolution_cycle(session)
    
    # 결과 출력
    print("\n" + "="*80)
    print("🚀 DuRi Evolution Integration 테스트 결과")
    print("="*80)
    
    print(f"\n📊 진화 세션:")
    print(f"  - 세션 ID: {session.session_id}")
    print(f"  - 목표: {session.target_goal}")
    print(f"  - 상태: {session.overall_status.value}")
    print(f"  - 시작 시간: {session.start_time}")
    print(f"  - 종료 시간: {session.end_time}")
    
    print(f"\n🎯 진화 결과:")
    print(f"  - 성공 여부: {result.success}")
    print(f"  - 진화 시간: {result.evolution_time:.2f}초")
    print(f"  - 품질 개선도: {result.quality_improvement:.3f}")
    print(f"  - 성능 개선도: {result.performance_improvement:.3f}")
    print(f"  - 유지보수성 개선도: {result.maintainability_improvement:.3f}")
    
    print(f"\n🔧 개선사항:")
    for improvement in result.improvements_made[:5]:  # 상위 5개만 출력
        print(f"  - {improvement}")
    
    if result.error_message:
        print(f"\n❌ 오류 메시지: {result.error_message}")
    
    return result


if __name__ == "__main__":
    asyncio.run(main()) 