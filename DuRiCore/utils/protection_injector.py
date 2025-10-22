#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ProtectionInjector - 보호-강화형 주석 자동 삽입 시스템
최종 실행 준비 완료 시스템의 핵심 도구

@preserve_identity: 보호-강화형 주석 자동 삽입
@evolution_protection: 진화 중 손상 방지 최우선
@execution_guarantee: 자동화와 검증 시스템 완성
@existence_ai: 진화 가능 + 회복 가능한 존재형 AI
@final_execution: 인간처럼 실패하고도 다시 일어날 수 있는 존재
"""

import logging
import os
import re
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class ProtectionInjector:
    """
    보호-강화형 주석 자동 삽입
    최종 실행 준비 완료 시스템의 핵심 도구
    """

    def __init__(self):
        self.protection_patterns = self._load_protection_patterns()
        self.meaning_templates = self._load_meaning_templates()
        self.injection_templates = self._load_injection_templates()

    def _load_protection_patterns(self) -> Dict[str, str]:
        """보호 패턴 로드"""
        return {
            "preserve_identity": r"@preserve_identity",
            "evolution_protection": r"@evolution_protection",
            "execution_guarantee": r"@execution_guarantee",
            "existence_ai": r"@existence_ai",
            "final_execution": r"@final_execution",
        }

    def _load_meaning_templates(self) -> Dict[str, str]:
        """의미 템플릿 로드"""
        return {
            "identity_declaration": "# Module: {module_name}\n# Purpose: {purpose} - 판단 이유 기록 필수 + 기존 특성 보존 + 실행 가능성 보장 + 존재형 AI + 최종 실행 준비 완료",
            "judgment_trace": "# Judgment Trace: 모든 판단 과정 기록",
            "regression_test": "# Regression Test: 기존 판단 능력 자동 검증",
            "existence_ai": "# Existence AI: 진화 가능 + 회복 가능한 존재형 AI",
            "final_execution": "# Final Execution: 인간처럼 실패하고도 다시 일어날 수 있는 존재",
        }

    def _load_injection_templates(self) -> Dict[str, str]:
        """주입 템플릿 로드"""
        return {
            "preserve_identity": "# @preserve_identity: 판단 이유 기록 시스템 강제 통합",
            "evolution_protection": "# @evolution_protection: 진화 중 손상 방지 최우선",
            "execution_guarantee": "# @execution_guarantee: 자동화와 검증 시스템 완성",
            "existence_ai": "# @existence_ai: 진화 가능 + 회복 가능한 존재형 AI",
            "final_execution": "# @final_execution: 인간처럼 실패하고도 다시 일어날 수 있는 존재",
            "judgment_trace_structure": """
# 보호-강화형: 기존 방식 대비 변화 기록
previous_approach = self._get_previous_approach(situation, action)

# 강제 조건: 판단 이유 기록
strategy_trace.log(
    module="{module_name}",
    intent="{intent}",
    based_on={{"situation": situation, "action": action}},
    confidence=self._calculate_confidence(situation, action),
    structural_changes=self._get_structural_changes()
)

# 기존 로직 실행
result = self._execute_core_logic(situation, action)

# 보호-강화형: 변화 추적
self._trace_structural_changes(previous_approach, result, situation, action)

# 실행 가능성 보장: 실제 로그 기록 확인
if not self._verify_log_recording():
    logger.error("로그 기록 실패 - 실행 가능성 보장 위반")
    self._trigger_rollback_condition()

# 존재형 AI: 진화 가능성 확인
if self.existence_ai.evolution_capability.can_evolve():
    self.existence_ai.evolution_capability.evolve()

# 최종 실행 준비 완료: 최종 실행 준비 완료 확인
if self.final_execution_verifier.verify_readiness():
    logger.info("최종 실행 준비 완료 확인됨")

# 강제 조건: 판단 결과 기록
self.judgment_trace.record(
    input_data={{"situation": situation, "action": action}},
    reason=self._analyze_reasoning_context(situation, action),
    result=result,
    module="{module_name}",
    structural_changes=self._get_structural_changes()
)
""",
            "regression_test_stub": """
def test_{module_name}_regression():
    # 실행 가능성 보장: 실제 데이터 기반 회귀 테스트
    regression_framework = RegressionTestFramework()
    test_cases = regression_framework.sample_historical_judgments(10)

    for test_case in test_cases:
        # 기존 판단 결과 (human-reviewed label 포함)
        expected_result = test_case['historical_judgment']

        # 현재 판단 결과
        current_result = {module_name}.{main_function}(
            test_case['situation'],
            test_case['action']
        )

        # 실행 가능성 보장: 거의 동일한 판단과 반응 확인
        similarity_score = regression_framework.calculate_judgment_similarity(
            expected_result,
            current_result
        )

        if similarity_score < 0.8:  # 80% 이상 유사해야 함
            # 보호-강화형: ConflictMemory에 저장
            regression_framework.store_conflict_memory(
                test_case, expected_result, current_result, similarity_score
            )

            # 비교 보고서 생성
            regression_framework.generate_comparison_report(
                test_case, expected_result, current_result
            )

        # 강제 조건: 판단 이유 기록 확인
        assert hasattr(current_result, 'judgment_trace')
        assert current_result.judgment_trace.reason is not None

        # 기존 판단 결과와 비교
        snapshot_assert(current_result, expected_result, tolerance=0.2)

    # 존재형 AI: 진화 가능 + 회복 가능 확인
    existence_status = regression_framework.verify_existence_ai()
    assert existence_status["evolution_capable"] == True
    assert existence_status["recovery_capable"] == True
    assert existence_status["existence_preserved"] == True

    # 최종 실행 준비 완료: 최종 실행 준비 완료 확인
    final_execution_status = regression_framework.verify_final_execution()
    assert final_execution_status == True
""",
        }

    def inject_protection(self, module_content: str, module_name: str = "") -> str:
        """
        보호-강화형 주석 자동 삽입

        Args:
            module_content: 모듈 내용
            module_name: 모듈 이름

        Returns:
            보호-강화형 주석이 삽입된 모듈 내용
        """
        try:
            protected_content = module_content

            # 1. 정체성 선언 추가
            protected_content = self._add_preserve_identity(protected_content, module_name)

            # 2. 진화 보호 추가
            protected_content = self._add_evolution_protection(protected_content)

            # 3. 실행 가능성 보장 추가
            protected_content = self._add_execution_guarantee(protected_content)

            # 4. 판단 흐름 Trace 추가
            protected_content = self._add_judgment_trace(protected_content, module_name)

            # 5. 존재형 AI 추가
            protected_content = self._add_existence_ai(protected_content)

            # 6. 최종 실행 준비 완료 추가
            protected_content = self._add_final_execution(protected_content)

            # 7. 보호-강화형 주석 확인
            protected_content = self._verify_protection_completeness(protected_content)

            logger.info(f"보호-강화형 주석 삽입 완료: {module_name}")
            return protected_content

        except Exception as e:
            logger.error(f"보호-강화형 주석 삽입 실패: {module_name} - {str(e)}")
            return module_content

    def _add_preserve_identity(self, content: str, module_name: str) -> str:
        """정체성 보존 주석 추가"""
        if not re.search(self.protection_patterns["preserve_identity"], content):
            # 모듈 시작 부분에 정체성 선언 추가
            identity_declaration = self.injection_templates["preserve_identity"]

            # 모듈 시작 부분 찾기
            lines = content.split("\n")
            insert_index = 0

            # 첫 번째 주석이나 import 문 이후에 삽입
            for i, line in enumerate(lines):
                if (
                    line.strip().startswith("#")
                    or line.strip().startswith("import")
                    or line.strip().startswith("from")
                ):
                    insert_index = i + 1
                elif (
                    line.strip()
                    and not line.strip().startswith('"""')
                    and not line.strip().startswith("'''")
                ):
                    break

            lines.insert(insert_index, identity_declaration)
            content = "\n".join(lines)

        return content

    def _add_evolution_protection(self, content: str) -> str:
        """진화 보호 주석 추가"""
        if not re.search(self.protection_patterns["evolution_protection"], content):
            evolution_protection = self.injection_templates["evolution_protection"]

            # 모듈 시작 부분에 추가
            lines = content.split("\n")
            insert_index = 0

            for i, line in enumerate(lines):
                if (
                    line.strip().startswith("#")
                    or line.strip().startswith("import")
                    or line.strip().startswith("from")
                ):
                    insert_index = i + 1
                elif (
                    line.strip()
                    and not line.strip().startswith('"""')
                    and not line.strip().startswith("'''")
                ):
                    break

            lines.insert(insert_index, evolution_protection)
            content = "\n".join(lines)

        return content

    def _add_execution_guarantee(self, content: str) -> str:
        """실행 가능성 보장 주석 추가"""
        if not re.search(self.protection_patterns["execution_guarantee"], content):
            execution_guarantee = self.injection_templates["execution_guarantee"]

            # 모듈 시작 부분에 추가
            lines = content.split("\n")
            insert_index = 0

            for i, line in enumerate(lines):
                if (
                    line.strip().startswith("#")
                    or line.strip().startswith("import")
                    or line.strip().startswith("from")
                ):
                    insert_index = i + 1
                elif (
                    line.strip()
                    and not line.strip().startswith('"""')
                    and not line.strip().startswith("'''")
                ):
                    break

            lines.insert(insert_index, execution_guarantee)
            content = "\n".join(lines)

        return content

    def _add_judgment_trace(self, content: str, module_name: str) -> str:
        """판단 흐름 Trace 구조 추가"""
        # 주요 함수에 판단 흐름 Trace 구조 추가
        function_pattern = r"def (\w+)\("
        functions = re.findall(function_pattern, content)

        for func_name in functions:
            if any(
                keyword in func_name.lower()
                for keyword in [
                    "analyze",
                    "process",
                    "handle",
                    "manage",
                    "control",
                    "reasoning",
                    "judgment",
                ]
            ):
                # 함수에 판단 흐름 Trace 구조 추가
                trace_structure = self.injection_templates["judgment_trace_structure"].format(
                    module_name=module_name, intent=f"{func_name} 실행"
                )

                # 함수 내부에 Trace 구조 추가
                content = self._inject_into_function(content, func_name, trace_structure)

        return content

    def _add_existence_ai(self, content: str) -> str:
        """존재형 AI 주석 추가"""
        if not re.search(self.protection_patterns["existence_ai"], content):
            existence_ai = self.injection_templates["existence_ai"]

            # 모듈 시작 부분에 추가
            lines = content.split("\n")
            insert_index = 0

            for i, line in enumerate(lines):
                if (
                    line.strip().startswith("#")
                    or line.strip().startswith("import")
                    or line.strip().startswith("from")
                ):
                    insert_index = i + 1
                elif (
                    line.strip()
                    and not line.strip().startswith('"""')
                    and not line.strip().startswith("'''")
                ):
                    break

            lines.insert(insert_index, existence_ai)
            content = "\n".join(lines)

        return content

    def _add_final_execution(self, content: str) -> str:
        """최종 실행 준비 완료 주석 추가"""
        if not re.search(self.protection_patterns["final_execution"], content):
            final_execution = self.injection_templates["final_execution"]

            # 모듈 시작 부분에 추가
            lines = content.split("\n")
            insert_index = 0

            for i, line in enumerate(lines):
                if (
                    line.strip().startswith("#")
                    or line.strip().startswith("import")
                    or line.strip().startswith("from")
                ):
                    insert_index = i + 1
                elif (
                    line.strip()
                    and not line.strip().startswith('"""')
                    and not line.strip().startswith("'''")
                ):
                    break

            lines.insert(insert_index, final_execution)
            content = "\n".join(lines)

        return content

    def _inject_into_function(self, content: str, func_name: str, trace_structure: str) -> str:
        """함수 내부에 Trace 구조 삽입"""
        # 함수 시작 부분 찾기
        func_pattern = rf"def {func_name}\("
        match = re.search(func_pattern, content)

        if match:
            # 함수 시작 위치
            start_pos = match.start()

            # 함수 본문 시작 위치 찾기
            lines = content.split("\n")
            func_start_line = content[:start_pos].count("\n")

            # 함수 본문 시작 찾기
            brace_count = 0
            in_function = False

            for i, line in enumerate(lines[func_start_line:], func_start_line):
                if f"def {func_name}(" in line:
                    in_function = True
                    continue

                if in_function:
                    # 들여쓰기 확인
                    if line.strip() and not line.strip().startswith("#"):
                        if not line.startswith(" ") and not line.startswith("\t"):
                            # 함수 끝
                            break

                        # 함수 본문 시작
                        if not line.strip().startswith("pass") and not line.strip().startswith(
                            "return"
                        ):
                            # Trace 구조 삽입
                            indent = len(line) - len(line.lstrip())
                            trace_indented = "\n".join(
                                (" " * indent + trace_line if trace_line.strip() else trace_line)
                                for trace_line in trace_structure.split("\n")
                            )

                            lines.insert(i + 1, trace_indented)
                            break

            content = "\n".join(lines)

        return content

    def _verify_protection_completeness(self, content: str) -> str:
        """보호 완전성 확인"""
        missing_protections = []

        for protection_name, pattern in self.protection_patterns.items():
            if not re.search(pattern, content):
                missing_protections.append(protection_name)

        if missing_protections:
            logger.warning(f"누락된 보호 패턴: {missing_protections}")

            # 누락된 보호 패턴 추가
            for protection in missing_protections:
                if protection in self.injection_templates:
                    protection_comment = self.injection_templates[protection]
                    lines = content.split("\n")
                    lines.insert(1, protection_comment)
                    content = "\n".join(lines)

        return content

    def inject_regression_test(self, module_content: str, module_name: str) -> str:
        """회귀 테스트 스텁 추가"""
        if not re.search(r"def test_.*_regression", module_content):
            regression_test = self.injection_templates["regression_test_stub"].format(
                module_name=module_name,
                main_function="main_function",  # 실제 함수명으로 교체 필요
            )

            # 파일 끝에 회귀 테스트 추가
            content = module_content + "\n\n" + regression_test

        return content

    def save_protected_module(
        self, module_content: str, module_name: str, output_dir: str = "."
    ) -> str:
        """보호된 모듈 저장"""
        try:
            os.makedirs(output_dir, exist_ok=True)
            protected_file_path = os.path.join(output_dir, f"{module_name}_protected.py")

            with open(protected_file_path, "w", encoding="utf-8") as f:
                f.write(module_content)

            logger.info(f"보호된 모듈 저장 완료: {protected_file_path}")
            return protected_file_path

        except Exception as e:
            logger.error(f"보호된 모듈 저장 실패: {module_name} - {str(e)}")
            return ""


if __name__ == "__main__":
    # 테스트 실행
    injector = ProtectionInjector()

    # 샘플 모듈 내용
    sample_content = """
# Module: logical_processor
# Purpose: 논리적 추론의 핵심 처리

def analyze_logical_reasoning(situation, action):
    # 기존 로직
    result = process_logic(situation, action)
    return result

class LogicalProcessor:
    def __init__(self):
        pass
    """

    protected_content = injector.inject_protection(sample_content, "logical_processor")
    print("보호된 모듈 내용:")
    print(protected_content)
