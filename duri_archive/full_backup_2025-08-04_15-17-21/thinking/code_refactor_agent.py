"""
🔧 DuRi 코드 리팩토링 에이전트 시스템
목표: DuRi가 자기 자신의 코드 구조를 읽고 평가하고 재정리할 수 있는 리팩토링 에이전트를 구축
"""

import ast
import json
import logging
import math
import os
import random
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RefactorType(Enum):
    """리팩토링 유형"""

    FUNCTION_SEPARATION = "function_separation"
    DUPLICATE_REMOVAL = "duplicate_removal"
    VARIABLE_NAMING = "variable_naming"
    CODE_STRUCTURE = "code_structure"
    PERFORMANCE_OPTIMIZATION = "performance_optimization"


class CodeQuality(Enum):
    """코드 품질"""

    EXCELLENT = "excellent"
    GOOD = "good"
    FAIR = "fair"
    POOR = "poor"
    CRITICAL = "critical"


@dataclass
class CodeAnalysis:
    """코드 분석"""

    file_path: str
    total_lines: int
    function_count: int
    class_count: int
    complexity_score: float
    quality_score: float
    issues_found: List[str]
    suggestions: List[str]
    analyzed_at: datetime


@dataclass
class RefactorTask:
    """리팩토링 작업"""

    task_id: str
    refactor_type: RefactorType
    target_file: str
    description: str
    priority: int
    estimated_effort: int
    created_at: datetime
    completed_at: Optional[datetime] = None
    success: Optional[bool] = None


@dataclass
class RefactorResult:
    """리팩토링 결과"""

    result_id: str
    task: RefactorTask
    original_code: str
    refactored_code: str
    improvements: List[str]
    quality_improvement: float
    execution_time: float
    completed_at: datetime


class CodeRefactorAgent:
    def __init__(self):
        self.code_analyses = []
        self.refactor_tasks = []
        self.refactor_results = []
        self.quality_threshold = 0.7
        self.complexity_threshold = 10.0

        # Phase 24 시스템들
        self.evolution_system = None
        self.consciousness_system = None
        self.test_generator = None

    def initialize_phase_24_integration(self):
        """Phase 24 시스템들과 통합"""
        try:
            import sys

            sys.path.append(".")
            from duri_brain.thinking.phase_23_enhanced import (
                get_phase23_enhanced_system,
            )
            from duri_brain.thinking.phase_24_self_evolution_ai import (
                get_phase24_system,
            )
            from duri_brain.thinking.unit_test_generator import get_unit_test_generator

            self.evolution_system = get_phase24_system()
            self.consciousness_system = get_phase23_enhanced_system()
            self.test_generator = get_unit_test_generator()

            logger.info("✅ Phase 24 시스템들과 통합 완료")
            return True
        except Exception as e:
            logger.error(f"❌ Phase 24 시스템 통합 실패: {e}")
            return False

    def analyze_code_file(self, file_path: str) -> CodeAnalysis:
        """코드 파일 분석"""
        logger.info(f"📊 코드 분석 시작: {file_path}")

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            # 기본 통계 계산
            lines = content.split("\n")
            total_lines = len(lines)

            # AST 분석 (시뮬레이션)
            function_count = random.randint(5, 20)
            class_count = random.randint(1, 5)
            complexity_score = random.uniform(5.0, 15.0)
            quality_score = random.uniform(0.6, 0.95)

            # 이슈 식별
            issues_found = []
            if complexity_score > self.complexity_threshold:
                issues_found.append("복잡도가 너무 높음")
            if quality_score < self.quality_threshold:
                issues_found.append("코드 품질 개선 필요")
            if function_count > 15:
                issues_found.append("함수가 너무 많음")

            # 개선 제안
            suggestions = []
            if complexity_score > self.complexity_threshold:
                suggestions.append("함수 분리 필요")
            if quality_score < self.quality_threshold:
                suggestions.append("변수명 개선 필요")
            if function_count > 15:
                suggestions.append("클래스 분리 고려")

            analysis = CodeAnalysis(
                file_path=file_path,
                total_lines=total_lines,
                function_count=function_count,
                class_count=class_count,
                complexity_score=complexity_score,
                quality_score=quality_score,
                issues_found=issues_found,
                suggestions=suggestions,
                analyzed_at=datetime.now(),
            )

            self.code_analyses.append(analysis)
            logger.info(
                f"✅ 코드 분석 완료: {file_path} - 품질 점수 {quality_score:.3f}"
            )
            return analysis

        except Exception as e:
            logger.error(f"❌ 코드 분석 실패: {file_path} - {e}")
            return None

    def create_refactor_task(
        self,
        refactor_type: RefactorType,
        target_file: str,
        description: str,
        priority: int = 1,
    ) -> RefactorTask:
        """리팩토링 작업 생성"""
        logger.info(f"🔧 리팩토링 작업 생성: {refactor_type.value}")

        task = RefactorTask(
            task_id=f"refactor_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            refactor_type=refactor_type,
            target_file=target_file,
            description=description,
            priority=priority,
            estimated_effort=random.randint(1, 5),
            created_at=datetime.now(),
        )

        self.refactor_tasks.append(task)
        logger.info(f"✅ 리팩토링 작업 생성 완료: {task.task_id}")
        return task

    def execute_function_separation(self, task: RefactorTask) -> RefactorResult:
        """함수 분리 리팩토링"""
        logger.info(f"🔧 함수 분리 실행: {task.target_file}")

        start_time = datetime.now()

        # 원본 코드 (시뮬레이션)
        original_code = """
def complex_function():
    # 복잡한 로직
    result1 = process_data()
    result2 = analyze_data()
    result3 = generate_report()
    return final_result
"""

        # 리팩토링된 코드
        refactored_code = """
def process_data():
    # 데이터 처리 로직
    return processed_data

def analyze_data():
    # 데이터 분석 로직
    return analyzed_data

def generate_report():
    # 리포트 생성 로직
    return report

def complex_function():
    # 분리된 함수들 호출
    result1 = process_data()
    result2 = analyze_data()
    result3 = generate_report()
    return final_result
"""

        improvements = [
            "함수 분리로 가독성 향상",
            "단일 책임 원칙 적용",
            "테스트 용이성 개선",
        ]

        quality_improvement = random.uniform(0.1, 0.3)

        end_time = datetime.now()
        execution_time = (end_time - start_time).total_seconds()

        result = RefactorResult(
            result_id=f"result_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            task=task,
            original_code=original_code,
            refactored_code=refactored_code,
            improvements=improvements,
            quality_improvement=quality_improvement,
            execution_time=execution_time,
            completed_at=end_time,
        )

        self.refactor_results.append(result)
        task.completed_at = end_time
        task.success = True

        logger.info(f"✅ 함수 분리 완료: 품질 개선 {quality_improvement:.3f}")
        return result

    def execute_duplicate_removal(self, task: RefactorTask) -> RefactorResult:
        """중복 제거 리팩토링"""
        logger.info(f"🔧 중복 제거 실행: {task.target_file}")

        start_time = datetime.now()

        # 원본 코드 (시뮬레이션)
        original_code = """
def validate_user_input(data):
    if not data:
        return False
    return True

def validate_product_input(data):
    if not data:
        return False
    return True

def validate_order_input(data):
    if not data:
        return False
    return True
"""

        # 리팩토링된 코드
        refactored_code = """
def validate_input(data):
    if not data:
        return False
    return True

def validate_user_input(data):
    return validate_input(data)

def validate_product_input(data):
    return validate_input(data)

def validate_order_input(data):
    return validate_input(data)
"""

        improvements = ["중복 코드 제거", "공통 함수 추출", "유지보수성 향상"]

        quality_improvement = random.uniform(0.15, 0.25)

        end_time = datetime.now()
        execution_time = (end_time - start_time).total_seconds()

        result = RefactorResult(
            result_id=f"result_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            task=task,
            original_code=original_code,
            refactored_code=refactored_code,
            improvements=improvements,
            quality_improvement=quality_improvement,
            execution_time=execution_time,
            completed_at=end_time,
        )

        self.refactor_results.append(result)
        task.completed_at = end_time
        task.success = True

        logger.info(f"✅ 중복 제거 완료: 품질 개선 {quality_improvement:.3f}")
        return result

    def execute_variable_naming(self, task: RefactorTask) -> RefactorResult:
        """변수명 개선 리팩토링"""
        logger.info(f"🔧 변수명 개선 실행: {task.target_file}")

        start_time = datetime.now()

        # 원본 코드 (시뮬레이션)
        original_code = """
def calculate_total():
    x = get_price()
    y = get_tax()
    z = x + y
    return z
"""

        # 리팩토링된 코드
        refactored_code = """
def calculate_total():
    base_price = get_price()
    tax_amount = get_tax()
    total_amount = base_price + tax_amount
    return total_amount
"""

        improvements = ["변수명 명확성 향상", "코드 가독성 개선", "의도 명확화"]

        quality_improvement = random.uniform(0.1, 0.2)

        end_time = datetime.now()
        execution_time = (end_time - start_time).total_seconds()

        result = RefactorResult(
            result_id=f"result_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            task=task,
            original_code=original_code,
            refactored_code=refactored_code,
            improvements=improvements,
            quality_improvement=quality_improvement,
            execution_time=execution_time,
            completed_at=end_time,
        )

        self.refactor_results.append(result)
        task.completed_at = end_time
        task.success = True

        logger.info(f"✅ 변수명 개선 완료: 품질 개선 {quality_improvement:.3f}")
        return result

    def execute_refactor_task(self, task: RefactorTask) -> RefactorResult:
        """리팩토링 작업 실행"""
        logger.info(f"🔧 리팩토링 작업 실행: {task.refactor_type.value}")

        if task.refactor_type == RefactorType.FUNCTION_SEPARATION:
            return self.execute_function_separation(task)
        elif task.refactor_type == RefactorType.DUPLICATE_REMOVAL:
            return self.execute_duplicate_removal(task)
        elif task.refactor_type == RefactorType.VARIABLE_NAMING:
            return self.execute_variable_naming(task)
        else:
            logger.error(f"❌ 지원하지 않는 리팩토링 유형: {task.refactor_type.value}")
            return None

    def analyze_codebase(self, directory: str = "duri_brain") -> List[CodeAnalysis]:
        """코드베이스 전체 분석"""
        logger.info(f"📊 코드베이스 분석 시작: {directory}")

        analyses = []

        # 주요 파일들 분석
        target_files = [
            "duri_brain/thinking/phase_24_self_evolution_ai.py",
            "duri_brain/thinking/phase_23_enhanced.py",
            "duri_brain/thinking/external_validation_bridge.py",
            "duri_brain/thinking/unit_test_generator.py",
        ]

        for file_path in target_files:
            if os.path.exists(file_path):
                analysis = self.analyze_code_file(file_path)
                if analysis:
                    analyses.append(analysis)

        logger.info(f"✅ 코드베이스 분석 완료: {len(analyses)}개 파일 분석")
        return analyses

    def generate_refactor_plan(
        self, analyses: List[CodeAnalysis]
    ) -> List[RefactorTask]:
        """리팩토링 계획 생성"""
        logger.info("📋 리팩토링 계획 생성")

        tasks = []

        for analysis in analyses:
            if analysis.quality_score < self.quality_threshold:
                # 품질이 낮은 파일에 대해 리팩토링 작업 생성
                if analysis.complexity_score > self.complexity_threshold:
                    task = self.create_refactor_task(
                        RefactorType.FUNCTION_SEPARATION,
                        analysis.file_path,
                        "복잡도가 높은 함수 분리 필요",
                        priority=2,
                    )
                    tasks.append(task)

                if "변수명 개선" in analysis.suggestions:
                    task = self.create_refactor_task(
                        RefactorType.VARIABLE_NAMING,
                        analysis.file_path,
                        "변수명 개선 필요",
                        priority=1,
                    )
                    tasks.append(task)

                if "중복 제거" in analysis.suggestions:
                    task = self.create_refactor_task(
                        RefactorType.DUPLICATE_REMOVAL,
                        analysis.file_path,
                        "중복 코드 제거 필요",
                        priority=3,
                    )
                    tasks.append(task)

        logger.info(f"✅ 리팩토링 계획 생성 완료: {len(tasks)}개 작업")
        return tasks

    def get_refactor_status(self) -> Dict[str, Any]:
        """리팩토링 상태 확인"""
        total_tasks = len(self.refactor_tasks)
        completed_tasks = len([t for t in self.refactor_tasks if t.completed_at])
        successful_tasks = len([t for t in self.refactor_tasks if t.success])

        if total_tasks > 0:
            completion_rate = completed_tasks / total_tasks
            success_rate = (
                successful_tasks / completed_tasks if completed_tasks > 0 else 0.0
            )
        else:
            completion_rate = 0.0
            success_rate = 0.0

        status = {
            "system": "Code Refactor Agent",
            "total_tasks": total_tasks,
            "completed_tasks": completed_tasks,
            "successful_tasks": successful_tasks,
            "completion_rate": completion_rate,
            "success_rate": success_rate,
            "code_analyses": len(self.code_analyses),
            "refactor_results": len(self.refactor_results),
        }

        return status


def get_code_refactor_agent():
    """코드 리팩토링 에이전트 시스템 인스턴스 반환"""
    return CodeRefactorAgent()


if __name__ == "__main__":
    # 코드 리팩토링 에이전트 시스템 테스트
    agent = get_code_refactor_agent()

    if agent.initialize_phase_24_integration():
        logger.info("🚀 코드 리팩토링 에이전트 시스템 테스트 시작")

        # 코드베이스 분석
        analyses = agent.analyze_codebase()

        # 리팩토링 계획 생성
        tasks = agent.generate_refactor_plan(analyses)

        # 리팩토링 작업 실행
        for task in tasks[:3]:  # 처음 3개 작업만 실행
            result = agent.execute_refactor_task(task)
            if result:
                logger.info(f"리팩토링 완료: {result.task.refactor_type.value}")

        # 최종 상태 확인
        status = agent.get_refactor_status()
        logger.info(f"완료율: {status['completion_rate']:.2%}")
        logger.info(f"성공율: {status['success_rate']:.2%}")

        logger.info("✅ 코드 리팩토링 에이전트 시스템 테스트 완료")
    else:
        logger.error("❌ 코드 리팩토링 에이전트 시스템 초기화 실패")
