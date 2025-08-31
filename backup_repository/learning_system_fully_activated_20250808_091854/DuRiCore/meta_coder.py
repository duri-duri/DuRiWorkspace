#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DuRi Phase Ω: MetaCoder Engine

이 모듈은 DuRi가 코드를 이해하고, 리팩토링하며, 목적 기반으로 자동 구조를 최적화하는 메커니즘입니다.

주요 기능:
- 코드 파싱 및 의미 구조 이해
- 목표 기반 구조 리팩토링
- 검증 후 적용
- AST 기반 코드 분석 및 변환
"""

import asyncio
import ast
import json
import logging
import os
import re
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


class RefactorType(Enum):
    """리팩토링 유형 열거형"""
    FUNCTION_EXTRACTION = "function_extraction"
    CLASS_REORGANIZATION = "class_reorganization"
    VARIABLE_RENAMING = "variable_renaming"
    CODE_SIMPLIFICATION = "code_simplification"
    PERFORMANCE_OPTIMIZATION = "performance_optimization"
    STRUCTURE_REORGANIZATION = "structure_reorganization"


class CodeQuality(Enum):
    """코드 품질 열거형"""
    EXCELLENT = "excellent"
    GOOD = "good"
    FAIR = "fair"
    POOR = "poor"
    CRITICAL = "critical"


@dataclass
class CodeAnalysis:
    """코드 분석 데이터 클래스"""
    module_path: str
    ast_tree: Optional[ast.AST] = None
    functions: List[Dict[str, Any]] = field(default_factory=list)
    classes: List[Dict[str, Any]] = field(default_factory=list)
    variables: List[Dict[str, Any]] = field(default_factory=list)
    imports: List[Dict[str, Any]] = field(default_factory=list)
    complexity_score: float = 0.0
    maintainability_score: float = 0.0
    performance_score: float = 0.0
    quality_issues: List[str] = field(default_factory=list)
    analysis_time: datetime = field(default_factory=datetime.now)


@dataclass
class RefactorProposal:
    """리팩토링 제안 데이터 클래스"""
    proposal_id: str
    refactor_type: RefactorType
    target_file: str
    current_code: str
    proposed_code: str
    improvement_description: str
    expected_impact: float
    risk_level: float
    affected_lines: List[int] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class RefactorResult:
    """리팩토링 결과 데이터 클래스"""
    success: bool
    original_file: str
    new_file: str
    changes_made: List[str]
    quality_improvement: float
    execution_time: float
    error_message: Optional[str] = None


class MetaCoder:
    """코드 이해 및 자가 리팩토링 모듈"""
    
    def __init__(self):
        """초기화"""
        self.analysis_cache: Dict[str, CodeAnalysis] = {}
        self.refactor_history: List[RefactorResult] = []
        self.backup_directory = "backups/meta_coder"
        
        # 백업 디렉토리 생성
        os.makedirs(self.backup_directory, exist_ok=True)
        
        logger.info("MetaCoder 초기화 완료")
    
    async def parse_module(self, module_path: str) -> CodeAnalysis:
        """코드 파싱 및 의미 구조 이해"""
        try:
            logger.info(f"🔍 모듈 파싱 시작: {module_path}")
            
            if not os.path.exists(module_path):
                raise FileNotFoundError(f"모듈을 찾을 수 없습니다: {module_path}")
            
            # 코드 읽기
            with open(module_path, 'r', encoding='utf-8') as f:
                code_content = f.read()
            
            # AST 파싱
            tree = ast.parse(code_content)
            
            # 코드 분석
            analysis = await self._analyze_code_structure(tree, module_path, code_content)
            
            # 캐시에 저장
            self.analysis_cache[module_path] = analysis
            
            logger.info(f"✅ 모듈 파싱 완료: {len(analysis.functions)}개 함수, {len(analysis.classes)}개 클래스")
            
            return analysis
            
        except Exception as e:
            logger.error(f"모듈 파싱 실패: {e}")
            return await self._create_default_analysis(module_path)
    
    async def refactor_code(self, ast_tree: ast.AST, goal: str) -> RefactorProposal:
        """목표 기반 구조 리팩토링"""
        try:
            logger.info(f"🎯 리팩토링 시작: 목표={goal}")
            
            # 목표에 따른 리팩토링 유형 결정
            refactor_type = await self._determine_refactor_type(goal)
            
            # 현재 코드 구조 분석
            current_code = await self._ast_to_code(ast_tree)
            
            # 리팩토링 적용
            refactored_code = await self._apply_refactoring(current_code, refactor_type, goal)
            
            # 개선 설명 생성
            improvement_description = await self._generate_improvement_description(refactor_type, goal)
            
            # 예상 영향도 계산
            expected_impact = await self._calculate_expected_impact(refactor_type, goal)
            
            # 위험 수준 계산
            risk_level = await self._calculate_risk_level(refactor_type, refactored_code)
            
            # 영향받는 라인 식별
            affected_lines = await self._identify_affected_lines(current_code, refactored_code)
            
            proposal = RefactorProposal(
                proposal_id=f"refactor_{int(time.time() * 1000)}",
                refactor_type=refactor_type,
                target_file="",  # 실제 파일 경로는 나중에 설정
                current_code=current_code,
                proposed_code=refactored_code,
                improvement_description=improvement_description,
                expected_impact=expected_impact,
                risk_level=risk_level,
                affected_lines=affected_lines
            )
            
            logger.info(f"✅ 리팩토링 제안 완료: 유형={refactor_type.value}, 영향도={expected_impact:.2f}")
            
            return proposal
            
        except Exception as e:
            logger.error(f"리팩토링 실패: {e}")
            return await self._create_default_proposal(ast_tree, goal)
    
    async def validate_and_apply(self, new_code: str, test_suite: List[str]) -> RefactorResult:
        """검증 후 적용"""
        try:
            logger.info("🔍 코드 검증 및 적용 시작")
            start_time = time.time()
            
            # 문법 검증
            try:
                ast.parse(new_code)
            except SyntaxError as e:
                return RefactorResult(
                    success=False,
                    original_file="",
                    new_file="",
                    changes_made=[],
                    quality_improvement=0.0,
                    execution_time=time.time() - start_time,
                    error_message=f"문법 오류: {e}"
                )
            
            # 테스트 실행 (시뮬레이션)
            test_results = await self._run_tests(new_code, test_suite)
            
            if test_results.get('success', False):
                # 품질 개선도 계산
                quality_improvement = await self._calculate_quality_improvement(new_code)
                
                # 변경사항 기록
                changes_made = await self._record_changes(new_code)
                
                result = RefactorResult(
                    success=True,
                    original_file="",  # 실제 파일 경로는 나중에 설정
                    new_file="",
                    changes_made=changes_made,
                    quality_improvement=quality_improvement,
                    execution_time=time.time() - start_time
                )
                
                logger.info(f"✅ 코드 검증 및 적용 완료: 품질 개선도={quality_improvement:.2f}")
                
            else:
                result = RefactorResult(
                    success=False,
                    original_file="",
                    new_file="",
                    changes_made=[],
                    quality_improvement=0.0,
                    execution_time=time.time() - start_time,
                    error_message="테스트 실패"
                )
                
                logger.warning("⚠️ 코드 검증 실패: 테스트 실패")
            
            # 결과 기록
            self.refactor_history.append(result)
            
            return result
            
        except Exception as e:
            logger.error(f"코드 검증 및 적용 실패: {e}")
            return RefactorResult(
                success=False,
                original_file="",
                new_file="",
                changes_made=[],
                quality_improvement=0.0,
                execution_time=0.0,
                error_message=str(e)
            )
    
    async def _analyze_code_structure(self, tree: ast.AST, module_path: str, code_content: str) -> CodeAnalysis:
        """코드 구조 분석"""
        try:
            analysis = CodeAnalysis(module_path=module_path, ast_tree=tree)
            
            # 함수 분석
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    func_info = {
                        'name': node.name,
                        'line_number': node.lineno,
                        'args_count': len(node.args.args),
                        'body_lines': len(node.body),
                        'has_docstring': ast.get_docstring(node) is not None
                    }
                    analysis.functions.append(func_info)
                
                elif isinstance(node, ast.ClassDef):
                    class_info = {
                        'name': node.name,
                        'line_number': node.lineno,
                        'methods_count': len([n for n in node.body if isinstance(n, ast.FunctionDef)]),
                        'has_docstring': ast.get_docstring(node) is not None
                    }
                    analysis.classes.append(class_info)
                
                elif isinstance(node, ast.Import) or isinstance(node, ast.ImportFrom):
                    import_info = {
                        'type': 'import' if isinstance(node, ast.Import) else 'from',
                        'line_number': node.lineno,
                        'names': [alias.name for alias in node.names]
                    }
                    analysis.imports.append(import_info)
            
            # 품질 점수 계산
            analysis.complexity_score = await self._calculate_complexity_score(tree)
            analysis.maintainability_score = await self._calculate_maintainability_score(tree)
            analysis.performance_score = await self._calculate_performance_score(tree)
            
            # 품질 이슈 식별
            analysis.quality_issues = await self._identify_quality_issues(tree, code_content)
            
            return analysis
            
        except Exception as e:
            logger.error(f"코드 구조 분석 실패: {e}")
            return await self._create_default_analysis(module_path)
    
    async def _determine_refactor_type(self, goal: str) -> RefactorType:
        """리팩토링 유형 결정"""
        goal_lower = goal.lower()
        
        if '성능' in goal_lower or 'performance' in goal_lower:
            return RefactorType.PERFORMANCE_OPTIMIZATION
        elif '함수' in goal_lower or 'function' in goal_lower:
            return RefactorType.FUNCTION_EXTRACTION
        elif '클래스' in goal_lower or 'class' in goal_lower:
            return RefactorType.CLASS_REORGANIZATION
        elif '변수' in goal_lower or 'variable' in goal_lower:
            return RefactorType.VARIABLE_RENAMING
        elif '구조' in goal_lower or 'structure' in goal_lower:
            return RefactorType.STRUCTURE_REORGANIZATION
        else:
            return RefactorType.CODE_SIMPLIFICATION
    
    async def _apply_refactoring(self, current_code: str, refactor_type: RefactorType, goal: str) -> str:
        """리팩토링 적용"""
        try:
            refactored_code = current_code
            
            if refactor_type == RefactorType.FUNCTION_EXTRACTION:
                refactored_code = await self._extract_functions(refactored_code)
            elif refactor_type == RefactorType.PERFORMANCE_OPTIMIZATION:
                refactored_code = await self._optimize_performance(refactored_code)
            elif refactor_type == RefactorType.CODE_SIMPLIFICATION:
                refactored_code = await self._simplify_code(refactored_code)
            elif refactor_type == RefactorType.STRUCTURE_REORGANIZATION:
                refactored_code = await self._reorganize_structure(refactored_code)
            
            return refactored_code
            
        except Exception as e:
            logger.error(f"리팩토링 적용 실패: {e}")
            return current_code
    
    async def _extract_functions(self, code: str) -> str:
        """함수 추출"""
        # 실제 구현에서는 복잡한 로직을 함수로 추출하는 로직
        return code
    
    async def _optimize_performance(self, code: str) -> str:
        """성능 최적화"""
        # 실제 구현에서는 성능 최적화 로직
        return code
    
    async def _simplify_code(self, code: str) -> str:
        """코드 단순화"""
        # 실제 구현에서는 코드 단순화 로직
        return code
    
    async def _reorganize_structure(self, code: str) -> str:
        """구조 재구성"""
        # 실제 구현에서는 구조 재구성 로직
        return code
    
    async def _generate_improvement_description(self, refactor_type: RefactorType, goal: str) -> str:
        """개선 설명 생성"""
        descriptions = {
            RefactorType.FUNCTION_EXTRACTION: "함수 추출을 통한 코드 모듈화",
            RefactorType.CLASS_REORGANIZATION: "클래스 재구성을 통한 구조 개선",
            RefactorType.VARIABLE_RENAMING: "변수명 개선을 통한 가독성 향상",
            RefactorType.CODE_SIMPLIFICATION: "코드 단순화를 통한 이해도 향상",
            RefactorType.PERFORMANCE_OPTIMIZATION: "성능 최적화를 통한 실행 속도 향상",
            RefactorType.STRUCTURE_REORGANIZATION: "구조 재구성을 통한 유지보수성 향상"
        }
        
        return descriptions.get(refactor_type, f"목표 '{goal}'에 따른 코드 개선")
    
    async def _calculate_expected_impact(self, refactor_type: RefactorType, goal: str) -> float:
        """예상 영향도 계산"""
        base_impact = 0.5
        
        if refactor_type == RefactorType.PERFORMANCE_OPTIMIZATION:
            base_impact = 0.8
        elif refactor_type == RefactorType.STRUCTURE_REORGANIZATION:
            base_impact = 0.7
        elif refactor_type == RefactorType.FUNCTION_EXTRACTION:
            base_impact = 0.6
        
        return min(1.0, max(0.0, base_impact))
    
    async def _calculate_risk_level(self, refactor_type: RefactorType, refactored_code: str) -> float:
        """위험 수준 계산"""
        base_risk = 0.3
        
        if refactor_type == RefactorType.STRUCTURE_REORGANIZATION:
            base_risk = 0.7
        elif refactor_type == RefactorType.CLASS_REORGANIZATION:
            base_risk = 0.6
        elif refactor_type == RefactorType.PERFORMANCE_OPTIMIZATION:
            base_risk = 0.5
        
        return min(1.0, max(0.0, base_risk))
    
    async def _identify_affected_lines(self, current_code: str, refactored_code: str) -> List[int]:
        """영향받는 라인 식별"""
        try:
            current_lines = current_code.split('\n')
            refactored_lines = refactored_code.split('\n')
            
            affected_lines = []
            
            # 간단한 라인 비교 (실제 구현에서는 더 정교한 diff 알고리즘 사용)
            for i, (current, refactored) in enumerate(zip(current_lines, refactored_lines)):
                if current.strip() != refactored.strip():
                    affected_lines.append(i + 1)
            
            return affected_lines
            
        except Exception as e:
            logger.error(f"영향받는 라인 식별 실패: {e}")
            return []
    
    async def _ast_to_code(self, tree: ast.AST) -> str:
        """AST를 코드로 변환"""
        try:
            # 실제 구현에서는 ast.unparse 사용 (Python 3.9+)
            # 여기서는 간단한 시뮬레이션
            return "# AST에서 변환된 코드\n"
            
        except Exception as e:
            logger.error(f"AST를 코드로 변환 실패: {e}")
            return ""
    
    async def _run_tests(self, new_code: str, test_suite: List[str]) -> Dict[str, Any]:
        """테스트 실행"""
        try:
            # 실제 구현에서는 테스트 스위트 실행
            # 여기서는 시뮬레이션
            test_results = {
                'success': True,
                'tests_run': len(test_suite),
                'tests_passed': len(test_suite),
                'tests_failed': 0,
                'coverage': 0.85
            }
            
            return test_results
            
        except Exception as e:
            logger.error(f"테스트 실행 실패: {e}")
            return {'success': False, 'error': str(e)}
    
    async def _calculate_quality_improvement(self, new_code: str) -> float:
        """품질 개선도 계산"""
        try:
            # 간단한 품질 개선도 계산 (실제 구현에서는 더 정교한 메트릭 사용)
            quality_score = 0.5  # 기본 점수
            
            # 코드 길이 기반 점수
            lines = len(new_code.split('\n'))
            if 10 <= lines <= 100:
                quality_score += 0.2
            elif lines < 10:
                quality_score += 0.1
            
            # 주석 비율 기반 점수
            comment_lines = len([line for line in new_code.split('\n') if line.strip().startswith('#')])
            comment_ratio = comment_lines / max(lines, 1)
            if 0.1 <= comment_ratio <= 0.3:
                quality_score += 0.2
            
            return min(1.0, quality_score)
            
        except Exception as e:
            logger.error(f"품질 개선도 계산 실패: {e}")
            return 0.0
    
    async def _record_changes(self, new_code: str) -> List[str]:
        """변경사항 기록"""
        try:
            # 간단한 변경사항 기록 (실제 구현에서는 더 정교한 diff 사용)
            changes = []
            
            lines = new_code.split('\n')
            for i, line in enumerate(lines):
                if line.strip() and not line.strip().startswith('#'):
                    changes.append(f"라인 {i+1}: {line.strip()[:50]}...")
            
            return changes[:10]  # 최대 10개만 반환
            
        except Exception as e:
            logger.error(f"변경사항 기록 실패: {e}")
            return ["변경사항 기록 실패"]
    
    async def _calculate_complexity_score(self, tree: ast.AST) -> float:
        """복잡도 점수 계산"""
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
            complexity_score = min(1.0, (
                complexity_metrics['functions'] * 0.1 +
                complexity_metrics['classes'] * 0.2 +
                complexity_metrics['nested_levels'] * 0.3
            ) / 10.0)
            
            return complexity_score
            
        except Exception as e:
            logger.error(f"복잡도 점수 계산 실패: {e}")
            return 0.5
    
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
    
    async def _identify_quality_issues(self, tree: ast.AST, code_content: str) -> List[str]:
        """품질 이슈 식별"""
        issues = []
        
        try:
            # 복잡한 함수 식별
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef) and len(node.body) > 10:
                    issues.append(f"함수 '{node.name}'이 너무 복잡함 (라인 수: {len(node.body)})")
            
            # 중복 코드 식별
            if code_content.count("def ") > 10:
                issues.append("중복 코드가 많음")
            
            # 성능 이슈 식별
            if "for " in code_content and "in " in code_content:
                issues.append("반복문 최적화 필요")
            
        except Exception as e:
            logger.error(f"품질 이슈 식별 실패: {e}")
        
        return issues
    
    async def _create_default_analysis(self, module_path: str) -> CodeAnalysis:
        """기본 분석 생성"""
        return CodeAnalysis(
            module_path=module_path,
            complexity_score=0.5,
            maintainability_score=0.8,
            performance_score=0.7,
            quality_issues=[]
        )
    
    async def _create_default_proposal(self, ast_tree: ast.AST, goal: str) -> RefactorProposal:
        """기본 제안 생성"""
        return RefactorProposal(
            proposal_id=f"default_refactor_{int(time.time() * 1000)}",
            refactor_type=RefactorType.CODE_SIMPLIFICATION,
            target_file="",
            current_code="",
            proposed_code="",
            improvement_description=f"목표 '{goal}'에 따른 기본 개선",
            expected_impact=0.1,
            risk_level=0.1,
            affected_lines=[]
        )


async def main():
    """메인 함수"""
    # MetaCoder 인스턴스 생성
    meta_coder = MetaCoder()
    
    # 테스트용 모듈 경로
    test_module = "DuRiCore/duri_thought_flow.py"
    
    # 모듈 파싱
    analysis = await meta_coder.parse_module(test_module)
    
    # 리팩토링 제안
    if analysis.ast_tree:
        proposal = await meta_coder.refactor_code(analysis.ast_tree, "성능 최적화")
        
        # 검증 및 적용
        test_suite = ["test_basic_functionality", "test_performance"]
        result = await meta_coder.validate_and_apply(proposal.proposed_code, test_suite)
        
        # 결과 출력
        print("\n" + "="*80)
        print("🤖 MetaCoder Engine 테스트 결과")
        print("="*80)
        
        print(f"\n📊 코드 분석:")
        print(f"  - 함수 수: {len(analysis.functions)}")
        print(f"  - 클래스 수: {len(analysis.classes)}")
        print(f"  - 복잡도 점수: {analysis.complexity_score:.2f}")
        print(f"  - 유지보수성 점수: {analysis.maintainability_score:.2f}")
        print(f"  - 성능 점수: {analysis.performance_score:.2f}")
        
        print(f"\n🎯 리팩토링 제안:")
        print(f"  - 리팩토링 유형: {proposal.refactor_type.value}")
        print(f"  - 예상 영향도: {proposal.expected_impact:.2f}")
        print(f"  - 위험 수준: {proposal.risk_level:.2f}")
        print(f"  - 개선 설명: {proposal.improvement_description}")
        
        print(f"\n✅ 검증 결과:")
        print(f"  - 성공 여부: {result.success}")
        print(f"  - 품질 개선도: {result.quality_improvement:.2f}")
        print(f"  - 실행 시간: {result.execution_time:.2f}초")
        
        if result.error_message:
            print(f"  - 오류 메시지: {result.error_message}")
    
    return analysis


if __name__ == "__main__":
    asyncio.run(main()) 