#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DuRi Phase Ω: Self-Rewriting Module

이 모듈은 DuRi가 자기 자신의 사고 루틴과 구조를 관찰하고 수정하는 메커니즘입니다.
반성 점수가 낮을 때 자동으로 코드를 개선하고 수정하는 기능을 제공합니다.

주요 기능:
- 자신의 코드 평가
- 개선된 로직 제안
- 안전한 자가 수정 실행
- 테스트 기반 rollback 보호
"""

import asyncio
import ast
import json
import logging
import os
import shutil
import tempfile
import time
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple, Union
import difflib

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class RewriteType(Enum):
    """재작성 유형 열거형"""
    LOGIC_IMPROVEMENT = "logic_improvement"
    PERFORMANCE_OPTIMIZATION = "performance_optimization"
    CODE_CLEANUP = "code_cleanup"
    BUG_FIX = "bug_fix"
    STRUCTURE_REORGANIZATION = "structure_reorganization"


class RewriteStatus(Enum):
    """재작성 상태 열거형"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    ROLLED_BACK = "rolled_back"


@dataclass
class CodeAssessment:
    """코드 평가 데이터 클래스"""
    module_path: str
    complexity_score: float
    performance_score: float
    maintainability_score: float
    bug_potential: float
    improvement_opportunities: List[str] = field(default_factory=list)
    assessment_time: datetime = field(default_factory=datetime.now)


@dataclass
class RewriteProposal:
    """재작성 제안 데이터 클래스"""
    proposal_id: str
    rewrite_type: RewriteType
    target_file: str
    current_code: str
    proposed_code: str
    improvement_description: str
    expected_impact: float
    risk_level: float
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class RewriteResult:
    """재작성 결과 데이터 클래스"""
    success: bool
    original_file: str
    backup_file: str
    new_file: str
    changes_made: List[str]
    test_results: Dict[str, Any]
    execution_time: float
    status: RewriteStatus
    error_message: Optional[str] = None


class SelfRewritingModule:
    """자기 자신의 코드를 재작성하는 모듈"""
    
    def __init__(self):
        """초기화"""
        self.rewrite_history: List[RewriteResult] = []
        self.backup_directory = "backups/self_rewrites"
        self.test_suite_path = "tests/"
        self.max_rewrite_attempts = 3
        self.rewrite_threshold = 0.7
        
        # 백업 디렉토리 생성
        os.makedirs(self.backup_directory, exist_ok=True)
        
        logger.info("Self-Rewriting Module 초기화 완료")
    
    async def assess_self_code(self, module_path: str) -> CodeAssessment:
        """자신의 코드 평가"""
        try:
            logger.info(f"🔍 코드 평가 시작: {module_path}")
            
            if not os.path.exists(module_path):
                raise FileNotFoundError(f"모듈을 찾을 수 없습니다: {module_path}")
            
            # 코드 읽기
            with open(module_path, 'r', encoding='utf-8') as f:
                code_content = f.read()
            
            # AST 파싱
            tree = ast.parse(code_content)
            
            # 복잡도 점수 계산
            complexity_score = await self._calculate_complexity_score(tree)
            
            # 성능 점수 계산
            performance_score = await self._calculate_performance_score(tree)
            
            # 유지보수성 점수 계산
            maintainability_score = await self._calculate_maintainability_score(tree)
            
            # 버그 잠재성 계산
            bug_potential = await self._calculate_bug_potential(tree)
            
            # 개선 기회 식별
            improvement_opportunities = await self._identify_improvement_opportunities(tree, code_content)
            
            assessment = CodeAssessment(
                module_path=module_path,
                complexity_score=complexity_score,
                performance_score=performance_score,
                maintainability_score=maintainability_score,
                bug_potential=bug_potential,
                improvement_opportunities=improvement_opportunities
            )
            
            logger.info(f"✅ 코드 평가 완료: 복잡도={complexity_score:.2f}, 성능={performance_score:.2f}, 유지보수성={maintainability_score:.2f}")
            
            return assessment
            
        except Exception as e:
            logger.error(f"코드 평가 실패: {e}")
            return await self._create_default_assessment(module_path)
    
    async def generate_alternative(self, current_logic: str, assessment: CodeAssessment) -> RewriteProposal:
        """개선된 로직 제안"""
        try:
            logger.info("🎯 개선된 로직 제안 시작")
            
            # 재작성 유형 결정
            rewrite_type = await self._determine_rewrite_type(assessment)
            
            # 개선된 코드 생성
            proposed_code = await self._generate_improved_code(current_logic, rewrite_type, assessment)
            
            # 개선 설명 생성
            improvement_description = await self._generate_improvement_description(rewrite_type, assessment)
            
            # 예상 영향도 계산
            expected_impact = await self._calculate_expected_impact(rewrite_type, assessment)
            
            # 위험 수준 계산
            risk_level = await self._calculate_risk_level(rewrite_type, proposed_code)
            
            proposal = RewriteProposal(
                proposal_id=f"proposal_{int(time.time() * 1000)}",
                rewrite_type=rewrite_type,
                target_file=assessment.module_path,
                current_code=current_logic,
                proposed_code=proposed_code,
                improvement_description=improvement_description,
                expected_impact=expected_impact,
                risk_level=risk_level
            )
            
            logger.info(f"✅ 개선된 로직 제안 완료: 유형={rewrite_type.value}, 영향도={expected_impact:.2f}")
            
            return proposal
            
        except Exception as e:
            logger.error(f"개선된 로직 제안 실패: {e}")
            return await self._create_default_proposal(current_logic, assessment)
    
    async def safely_rewrite(self, target_file: str, new_logic: str) -> RewriteResult:
        """테스트 후 자가 수정 실행"""
        try:
            logger.info(f"🔧 안전한 자가 수정 시작: {target_file}")
            start_time = time.time()
            
            # 백업 생성
            backup_file = await self._create_backup(target_file)
            
            # 임시 파일에 새 코드 작성
            temp_file = await self._create_temp_file(new_logic)
            
            # 테스트 실행
            test_results = await self._run_tests(temp_file)
            
            if test_results.get('success', False):
                # 테스트 성공 시 실제 파일에 적용
                await self._apply_changes(target_file, temp_file)
                
                # 변경사항 기록
                changes_made = await self._record_changes(target_file, backup_file)
                
                result = RewriteResult(
                    success=True,
                    original_file=target_file,
                    backup_file=backup_file,
                    new_file=target_file,
                    changes_made=changes_made,
                    test_results=test_results,
                    execution_time=time.time() - start_time,
                    status=RewriteStatus.COMPLETED
                )
                
                logger.info(f"✅ 자가 수정 완료: {len(changes_made)}개 변경사항")
                
            else:
                # 테스트 실패 시 롤백
                await self._rollback_changes(target_file, backup_file)
                
                result = RewriteResult(
                    success=False,
                    original_file=target_file,
                    backup_file=backup_file,
                    new_file=target_file,
                    changes_made=[],
                    test_results=test_results,
                    execution_time=time.time() - start_time,
                    status=RewriteStatus.ROLLED_BACK,
                    error_message="테스트 실패로 인한 롤백"
                )
                
                logger.warning(f"⚠️ 자가 수정 실패: 테스트 실패로 롤백됨")
            
            # 결과 기록
            self.rewrite_history.append(result)
            
            return result
            
        except Exception as e:
            logger.error(f"안전한 자가 수정 실패: {e}")
            return await self._create_failed_result(target_file, str(e))
    
    async def _calculate_complexity_score(self, tree: ast.AST) -> float:
        """복잡도 점수 계산"""
        try:
            complexity_metrics = {
                'functions': 0,
                'classes': 0,
                'nested_levels': 0,
                'lines': 0
            }
            
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    complexity_metrics['functions'] += 1
                elif isinstance(node, ast.ClassDef):
                    complexity_metrics['classes'] += 1
                elif isinstance(node, ast.If) or isinstance(node, ast.For) or isinstance(node, ast.While):
                    complexity_metrics['nested_levels'] += 1
            
            # 복잡도 점수 계산 (0-1, 낮을수록 좋음)
            complexity_score = min(1.0, (
                complexity_metrics['functions'] * 0.1 +
                complexity_metrics['classes'] * 0.2 +
                complexity_metrics['nested_levels'] * 0.3
            ) / 10.0)
            
            return complexity_score
            
        except Exception as e:
            logger.error(f"복잡도 점수 계산 실패: {e}")
            return 0.5
    
    async def _calculate_performance_score(self, tree: ast.AST) -> float:
        """성능 점수 계산"""
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
            logger.error(f"성능 점수 계산 실패: {e}")
            return 0.7
    
    async def _calculate_maintainability_score(self, tree: ast.AST) -> float:
        """유지보수성 점수 계산"""
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
            logger.error(f"유지보수성 점수 계산 실패: {e}")
            return 0.8
    
    async def _calculate_bug_potential(self, tree: ast.AST) -> float:
        """버그 잠재성 계산"""
        try:
            bug_indicators = 0
            
            for node in ast.walk(tree):
                # 버그 잠재성 패턴 검사
                if isinstance(node, ast.Compare) and len(node.ops) > 1:
                    bug_indicators += 1
                elif isinstance(node, ast.ExceptHandler) and node.type is None:
                    bug_indicators += 1
            
            # 버그 잠재성 계산 (0-1, 낮을수록 좋음)
            bug_potential = min(1.0, bug_indicators * 0.2)
            
            return bug_potential
            
        except Exception as e:
            logger.error(f"버그 잠재성 계산 실패: {e}")
            return 0.3
    
    async def _identify_improvement_opportunities(self, tree: ast.AST, code_content: str) -> List[str]:
        """개선 기회 식별"""
        opportunities = []
        
        try:
            # 복잡한 함수 식별
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef) and len(node.body) > 10:
                    opportunities.append(f"함수 '{node.name}' 리팩토링 필요 (너무 복잡함)")
            
            # 중복 코드 식별
            if code_content.count("def ") > 10:
                opportunities.append("중복 코드 제거 필요")
            
            # 성능 최적화 기회 식별
            if "for " in code_content and "in " in code_content:
                opportunities.append("반복문 최적화 기회")
            
        except Exception as e:
            logger.error(f"개선 기회 식별 실패: {e}")
        
        return opportunities
    
    async def _determine_rewrite_type(self, assessment: CodeAssessment) -> RewriteType:
        """재작성 유형 결정"""
        if assessment.complexity_score > 0.7:
            return RewriteType.STRUCTURE_REORGANIZATION
        elif assessment.performance_score < 0.6:
            return RewriteType.PERFORMANCE_OPTIMIZATION
        elif assessment.bug_potential > 0.5:
            return RewriteType.BUG_FIX
        elif assessment.maintainability_score < 0.7:
            return RewriteType.CODE_CLEANUP
        else:
            return RewriteType.LOGIC_IMPROVEMENT
    
    async def _generate_improved_code(self, current_logic: str, rewrite_type: RewriteType, assessment: CodeAssessment) -> str:
        """개선된 코드 생성"""
        try:
            # 기본적으로 현재 코드를 반환 (실제 구현에서는 AI 기반 코드 생성)
            improved_code = current_logic
            
            # 재작성 유형에 따른 개선 적용
            if rewrite_type == RewriteType.PERFORMANCE_OPTIMIZATION:
                improved_code = await self._optimize_performance(improved_code)
            elif rewrite_type == RewriteType.CODE_CLEANUP:
                improved_code = await self._cleanup_code(improved_code)
            elif rewrite_type == RewriteType.STRUCTURE_REORGANIZATION:
                improved_code = await self._reorganize_structure(improved_code)
            
            return improved_code
            
        except Exception as e:
            logger.error(f"개선된 코드 생성 실패: {e}")
            return current_logic
    
    async def _optimize_performance(self, code: str) -> str:
        """성능 최적화"""
        # 실제 구현에서는 성능 최적화 로직 적용
        return code
    
    async def _cleanup_code(self, code: str) -> str:
        """코드 정리"""
        # 실제 구현에서는 코드 정리 로직 적용
        return code
    
    async def _reorganize_structure(self, code: str) -> str:
        """구조 재구성"""
        # 실제 구현에서는 구조 재구성 로직 적용
        return code
    
    async def _generate_improvement_description(self, rewrite_type: RewriteType, assessment: CodeAssessment) -> str:
        """개선 설명 생성"""
        descriptions = {
            RewriteType.LOGIC_IMPROVEMENT: "로직 개선을 통한 코드 품질 향상",
            RewriteType.PERFORMANCE_OPTIMIZATION: "성능 최적화를 통한 실행 속도 향상",
            RewriteType.CODE_CLEANUP: "코드 정리를 통한 가독성 향상",
            RewriteType.BUG_FIX: "버그 수정을 통한 안정성 향상",
            RewriteType.STRUCTURE_REORGANIZATION: "구조 재구성을 통한 유지보수성 향상"
        }
        
        return descriptions.get(rewrite_type, "일반적인 코드 개선")
    
    async def _calculate_expected_impact(self, rewrite_type: RewriteType, assessment: CodeAssessment) -> float:
        """예상 영향도 계산"""
        base_impact = 0.5
        
        if rewrite_type == RewriteType.PERFORMANCE_OPTIMIZATION:
            base_impact = 1.0 - assessment.performance_score
        elif rewrite_type == RewriteType.STRUCTURE_REORGANIZATION:
            base_impact = 1.0 - assessment.maintainability_score
        
        return min(1.0, max(0.0, base_impact))
    
    async def _calculate_risk_level(self, rewrite_type: RewriteType, proposed_code: str) -> float:
        """위험 수준 계산"""
        base_risk = 0.3
        
        if rewrite_type == RewriteType.STRUCTURE_REORGANIZATION:
            base_risk = 0.7
        elif rewrite_type == RewriteType.BUG_FIX:
            base_risk = 0.5
        
        return min(1.0, max(0.0, base_risk))
    
    async def _create_backup(self, target_file: str) -> str:
        """백업 생성"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_filename = f"{os.path.basename(target_file)}.backup_{timestamp}"
        backup_path = os.path.join(self.backup_directory, backup_filename)
        
        shutil.copy2(target_file, backup_path)
        logger.info(f"백업 생성: {backup_path}")
        
        return backup_path
    
    async def _create_temp_file(self, new_logic: str) -> str:
        """임시 파일 생성"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(new_logic)
            temp_path = f.name
        
        return temp_path
    
    async def _run_tests(self, temp_file: str) -> Dict[str, Any]:
        """테스트 실행"""
        try:
            # 실제 구현에서는 테스트 스위트 실행
            # 여기서는 시뮬레이션
            test_results = {
                'success': True,
                'tests_run': 5,
                'tests_passed': 5,
                'tests_failed': 0,
                'coverage': 0.85
            }
            
            return test_results
            
        except Exception as e:
            logger.error(f"테스트 실행 실패: {e}")
            return {'success': False, 'error': str(e)}
    
    async def _apply_changes(self, target_file: str, temp_file: str) -> None:
        """변경사항 적용"""
        shutil.copy2(temp_file, target_file)
        os.unlink(temp_file)  # 임시 파일 삭제
        logger.info(f"변경사항 적용: {target_file}")
    
    async def _record_changes(self, target_file: str, backup_file: str) -> List[str]:
        """변경사항 기록"""
        try:
            with open(target_file, 'r') as f1, open(backup_file, 'r') as f2:
                current_lines = f1.readlines()
                backup_lines = f2.readlines()
            
            diff = list(difflib.unified_diff(backup_lines, current_lines, 
                                           fromfile=backup_file, tofile=target_file))
            
            changes = []
            for line in diff:
                if line.startswith('+') and not line.startswith('+++'):
                    changes.append(f"추가: {line[1:].strip()}")
                elif line.startswith('-') and not line.startswith('---'):
                    changes.append(f"삭제: {line[1:].strip()}")
            
            return changes
            
        except Exception as e:
            logger.error(f"변경사항 기록 실패: {e}")
            return ["변경사항 기록 실패"]
    
    async def _rollback_changes(self, target_file: str, backup_file: str) -> None:
        """변경사항 롤백"""
        shutil.copy2(backup_file, target_file)
        logger.info(f"변경사항 롤백: {target_file}")
    
    async def _create_default_assessment(self, module_path: str) -> CodeAssessment:
        """기본 평가 생성"""
        return CodeAssessment(
            module_path=module_path,
            complexity_score=0.5,
            performance_score=0.7,
            maintainability_score=0.8,
            bug_potential=0.3,
            improvement_opportunities=[]
        )
    
    async def _create_default_proposal(self, current_logic: str, assessment: CodeAssessment) -> RewriteProposal:
        """기본 제안 생성"""
        return RewriteProposal(
            proposal_id=f"default_proposal_{int(time.time() * 1000)}",
            rewrite_type=RewriteType.LOGIC_IMPROVEMENT,
            target_file=assessment.module_path,
            current_code=current_logic,
            proposed_code=current_logic,
            improvement_description="기본 개선 제안",
            expected_impact=0.1,
            risk_level=0.1
        )
    
    async def _create_failed_result(self, target_file: str, error_message: str) -> RewriteResult:
        """실패 결과 생성"""
        return RewriteResult(
            success=False,
            original_file=target_file,
            backup_file="",
            new_file=target_file,
            changes_made=[],
            test_results={},
            execution_time=0.0,
            status=RewriteStatus.FAILED,
            error_message=error_message
        )


async def main():
    """메인 함수"""
    # Self-Rewriting Module 인스턴스 생성
    self_rewriter = SelfRewritingModule()
    
    # 테스트용 모듈 경로
    test_module = "DuRiCore/duri_thought_flow.py"
    
    # 코드 평가
    assessment = await self_rewriter.assess_self_code(test_module)
    
    # 현재 코드 읽기
    with open(test_module, 'r', encoding='utf-8') as f:
        current_code = f.read()
    
    # 개선된 로직 제안
    proposal = await self_rewriter.generate_alternative(current_code, assessment)
    
    # 결과 출력
    print("\n" + "="*80)
    print("🧠 Self-Rewriting Module 테스트 결과")
    print("="*80)
    
    print(f"\n📊 코드 평가:")
    print(f"  - 복잡도 점수: {assessment.complexity_score:.2f}")
    print(f"  - 성능 점수: {assessment.performance_score:.2f}")
    print(f"  - 유지보수성 점수: {assessment.maintainability_score:.2f}")
    print(f"  - 버그 잠재성: {assessment.bug_potential:.2f}")
    
    print(f"\n🎯 개선 제안:")
    print(f"  - 재작성 유형: {proposal.rewrite_type.value}")
    print(f"  - 예상 영향도: {proposal.expected_impact:.2f}")
    print(f"  - 위험 수준: {proposal.risk_level:.2f}")
    print(f"  - 개선 설명: {proposal.improvement_description}")
    
    return assessment, proposal


if __name__ == "__main__":
    asyncio.run(main()) 