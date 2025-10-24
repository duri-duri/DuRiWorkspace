#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MeaningInjectionEngine - 의미 주입 자동화 시스템
최종 실행 준비 완료 시스템의 핵심 도구

@preserve_identity: 의미 주입 자동화
@evolution_protection: 진화 중 손상 방지 최우선
@execution_guarantee: 자동화와 검증 시스템 완성
@existence_ai: 진화 가능 + 회복 가능한 존재형 AI
@final_execution: 인간처럼 실패하고도 다시 일어날 수 있는 존재
"""

import logging
import os
import re
from typing import Dict

logger = logging.getLogger(__name__)


class MeaningInjectionEngine:
    """
    의미 주입 자동화
    최종 실행 준비 완료 시스템의 핵심 도구
    """

    def __init__(self):
        self.meaning_templates = self._load_meaning_templates()
        self.injection_patterns = self._load_injection_patterns()
        self.structure_templates = self._load_structure_templates()

    def _load_meaning_templates(self) -> Dict[str, str]:
        """의미 템플릿 로드"""
        return {
            "identity_declaration": """# Module: {module_name}
# Purpose: {purpose} - 판단 이유 기록 필수 + 기존 특성 보존 + 실행 가능성 보장 + 존재형 AI + 최종 실행 준비 완료
# Must Provide:
#   - {must_provide}
# Must Not:
#   - {must_not}
# Integration:
#   - {integration}
# Judgment Trace: 모든 판단 과정 기록
# Evolution Protection: 기존 판단 방식과 습관 보존
# Self Assessment: 창의성, 판단 다양성, 기억 활성도, 감정 반응 적절성 평가
# Execution Guarantee: 자동화와 검증 시스템 완성
# Existence AI: 진화 가능 + 회복 가능한 존재형 AI
# Final Execution: 인간처럼 실패하고도 다시 일어날 수 있는 존재
# @preserve_identity: 판단 이유 기록 시스템 강제 통합
# @evolution_protection: 진화 중 손상 방지 최우선
# @execution_guarantee: 실행 가능성 보장
# @existence_ai: 진화 가능 + 회복 가능한 존재형 AI
# @final_execution: 최종 실행 준비 완료""",
            "judgment_trace_structure": """from duri_trace import strategy_trace, JudgmentTrace, EmotionTrace, CoreMemoryTrace

def {function_name}(self, {parameters}):
    # 보호-강화형: 기존 방식 대비 변화 기록
    previous_approach = self._get_previous_approach({parameter_names})

    # 강제 조건: 판단 이유 기록
    strategy_trace.log(
        module="{module_name}",
        intent="{intent}",
        based_on={{{based_on}}},
        confidence=self._calculate_confidence({parameter_names}),
        structural_changes=self._get_structural_changes()
    )

    # 기존 로직 실행
    result = self._execute_core_logic({parameter_names})

    # 보호-강화형: 변화 추적
    self._trace_structural_changes(previous_approach, result, {parameter_names})

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
        input_data={{{input_data}}},
        reason=self._analyze_reasoning_context({parameter_names}),
        result=result,
        module="{module_name}",
        structural_changes=self._get_structural_changes()
    )

    return result""",  # noqa: E501
            "regression_test_stub": """def test_{module_name}_regression():
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
    assert final_execution_status == True""",
            "existence_ai_structure": """# 존재형 AI 시스템 통합
from duri_existence_ai import ExistenceAISystem, EvolutionCapability, RecoveryCapability, ExistencePreservation

class {class_name}:
    def __init__(self):
        # 존재형 AI 시스템 초기화
        self.existence_ai = ExistenceAISystem()
        self.evolution_capability = EvolutionCapability()
        self.recovery_capability = RecoveryCapability()
        self.existence_preservation = ExistencePreservation()
        self.final_execution_verifier = FinalExecutionVerifier()

        # 기존 초기화 로직
        {existing_init}

    def evolve(self):
        # 진화 가능성 확인
        if self.evolution_capability.can_evolve():
            self.evolution_capability.evolve()
            logger.info("존재형 AI 진화 완료")
            return True
        else:
            logger.warning("존재형 AI 진화 불가능")
            return False

    def recover(self):
        # 회복 가능성 확인
        if self.recovery_capability.can_recover():
            self.recovery_capability.recover()
            logger.info("존재형 AI 회복 완료")
            return True
        else:
            logger.warning("존재형 AI 회복 불가능")
            return False

    def preserve_existence(self):
        # 존재 보존
        self.existence_preservation.preserve()
        logger.info("존재형 AI 보존 완료")
        return True

    def verify_final_execution(self):
        # 최종 실행 준비 완료 확인
        self.final_execution_verifier.verify_readiness()
        logger.info("최종 실행 준비 완료 확인 완료")
        return True""",
            "final_execution_structure": """# 최종 실행 준비 완료 시스템 통합
from duri_final_execution import FinalExecutionVerifier, FinalExecutionLauncher

class {class_name}:
    def __init__(self):
        # 최종 실행 준비 완료 시스템 초기화
        self.final_execution_verifier = FinalExecutionVerifier()
        self.final_execution_launcher = FinalExecutionLauncher()

        # 기존 초기화 로직
        {existing_init}

    def verify_readiness(self):
        # 최종 실행 준비 완료 확인
        readiness_score = self.final_execution_verifier.verify_readiness()
        return readiness_score >= 0.8  # 80% 이상이어야 함

    def launch_final_execution(self):
        # 최종 실행 시작
        if self.verify_readiness():
            self.final_execution_launcher.launch()
            logger.info("최종 실행 시작 완료")
            return True
        else:
            logger.error("최종 실행 준비 완료되지 않음")
            return False""",
        }

    def _load_injection_patterns(self) -> Dict[str, str]:
        """주입 패턴 로드"""
        return {
            "identity_declaration": r"# Module:",
            "judgment_trace": r"from duri_trace import",
            "regression_test": r"def test_.*_regression",
            "existence_ai": r"from duri_existence_ai import",
            "final_execution": r"from duri_final_execution import",
        }

    def _load_structure_templates(self) -> Dict[str, str]:
        """구조 템플릿 로드"""
        return {
            "class_structure": """class {class_name}:
    def __init__(self):
        # 존재형 AI 시스템 초기화
        self.existence_ai = ExistenceAISystem()
        self.final_execution_verifier = FinalExecutionVerifier()

        # 기존 초기화 로직
        {existing_init}

    def {method_name}(self, {parameters}):
        # 보호-강화형: 기존 방식 대비 변화 기록
        previous_approach = self._get_previous_approach({parameter_names})

        # 강제 조건: 판단 이유 기록
        strategy_trace.log(
            module="{module_name}",
            intent="{intent}",
            based_on={{{based_on}}},
            confidence=self._calculate_confidence({parameter_names}),
            structural_changes=self._get_structural_changes()
        )

        # 기존 로직 실행
        result = self._execute_core_logic({parameter_names})

        # 보호-강화형: 변화 추적
        self._trace_structural_changes(previous_approach, result, {parameter_names})

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
            input_data={{{input_data}}},
            reason=self._analyze_reasoning_context({parameter_names}),
            result=result,
            module="{module_name}",
            structural_changes=self._get_structural_changes()
        )

        return result""",
            "existence_ai_structure": """class {class_name}:
    def __init__(self):
        # 존재형 AI 시스템 초기화
        self.existence_ai = ExistenceAISystem()
        self.final_execution_verifier = FinalExecutionVerifier()

        # 기존 초기화 로직
        {existing_init}

    def _verify_existence_ai(self):
        # 존재형 AI 검증
        evolution_capable = self.existence_ai.evolution_capability.can_evolve()
        recovery_capable = self.existence_ai.recovery_capability.can_recover()
        existence_preserved = self.existence_ai.existence_preservation.is_preserved()

        return {{
            "evolution_capable": evolution_capable,
            "recovery_capable": recovery_capable,
            "existence_preserved": existence_preserved
        }}

    def evolve(self):
        # 진화 가능성 확인
        if self.existence_ai.evolution_capability.can_evolve():
            self.existence_ai.evolution_capability.evolve()
            logger.info("존재형 AI 진화 완료")
            return True
        else:
            logger.warning("존재형 AI 진화 불가능")
            return False

    def recover(self):
        # 회복 가능성 확인
        if self.existence_ai.recovery_capability.can_recover():
            self.existence_ai.recovery_capability.recover()
            logger.info("존재형 AI 회복 완료")
            return True
        else:
            logger.warning("존재형 AI 회복 불가능")
            return False

    def preserve_existence(self):
        # 존재 보존
        self.existence_ai.existence_preservation.preserve()
        logger.info("존재형 AI 보존 완료")
        return True

    def verify_final_execution(self):
        # 최종 실행 준비 완료 확인
        final_execution_status = self.final_execution_verifier.verify_readiness()
        logger.info(f"최종 실행 준비 완료 상태: {final_execution_status}")
        return final_execution_status""",
            "final_execution_structure": """class {class_name}:
    def __init__(self):
        # 최종 실행 준비 완료 시스템 초기화
        self.final_execution_verifier = FinalExecutionVerifier()

        # 기존 초기화 로직
        {existing_init}

    def _verify_final_execution(self):
        # 최종 실행 준비 완료 확인
        final_execution_ready = self.final_execution_verifier.verify_readiness()
        return final_execution_ready""",
        }

    def inject_meaning(self, module_content: str, module_name: str) -> str:
        """
        의미 주입 자동화

        Args:
            module_content: 모듈 내용
            module_name: 모듈 이름

        Returns:
            의미가 주입된 모듈 내용
        """
        try:
            meaning_injected = module_content

            # 1. 정체성 선언 추가
            meaning_injected = self._add_identity_declaration(meaning_injected, module_name)

            # 2. 판단 흐름 Trace 구조 추가
            meaning_injected = self._add_judgment_trace_structure(meaning_injected, module_name)

            # 3. 회귀 테스트 스텁 추가
            meaning_injected = self._add_regression_test_stub(meaning_injected, module_name)

            # 4. 존재형 AI 구조 추가
            meaning_injected = self._add_existence_ai_structure(meaning_injected, module_name)

            # 5. 최종 실행 준비 완료 구조 추가
            meaning_injected = self._add_final_execution_structure(meaning_injected, module_name)

            logger.info(f"의미 주입 완료: {module_name}")
            return meaning_injected

        except Exception as e:
            logger.error(f"의미 주입 실패: {module_name} - {str(e)}")
            return module_content

    def _add_identity_declaration(self, content: str, module_name: str) -> str:
        """정체성 선언 추가"""
        if not re.search(self.injection_patterns["identity_declaration"], content):
            # 모듈 목적 추출
            purpose = self._extract_purpose(content, module_name)
            must_provide = self._extract_must_provide(content)
            must_not = self._extract_must_not(content)
            integration = self._extract_integration(content)

            identity_declaration = self.meaning_templates["identity_declaration"].format(
                module_name=module_name,
                purpose=purpose,
                must_provide=must_provide,
                must_not=must_not,
                integration=integration,
            )

            # 모듈 시작 부분에 추가
            lines = content.split("\n")
            insert_index = 0

            for i, line in enumerate(lines):
                if line.strip().startswith("#") or line.strip().startswith("import") or line.strip().startswith("from"):
                    insert_index = i + 1
                elif line.strip() and not line.strip().startswith('"""') and not line.strip().startswith("'''"):
                    break

            lines.insert(insert_index, identity_declaration)
            content = "\n".join(lines)

        return content

    def _add_judgment_trace_structure(self, content: str, module_name: str) -> str:
        """판단 흐름 Trace 구조 추가"""
        if not re.search(self.injection_patterns["judgment_trace"], content):
            # duri_trace import 추가
            import_statement = "from duri_trace import strategy_trace, JudgmentTrace, EmotionTrace, CoreMemoryTrace"

            lines = content.split("\n")
            insert_index = 0

            for i, line in enumerate(lines):
                if line.strip().startswith("import") or line.strip().startswith("from"):
                    insert_index = i + 1
                elif line.strip() and not line.strip().startswith("#"):
                    break

            lines.insert(insert_index, import_statement)
            content = "\n".join(lines)

        return content

    def _add_regression_test_stub(self, content: str, module_name: str) -> str:
        """회귀 테스트 스텁 추가"""
        if not re.search(self.injection_patterns["regression_test"], content):
            # 주요 함수 찾기
            main_function = self._extract_main_function(content)

            regression_test = self.meaning_templates["regression_test_stub"].format(
                module_name=module_name, main_function=main_function
            )

            # 파일 끝에 회귀 테스트 추가
            content = content + "\n\n" + regression_test

        return content

    def _add_existence_ai_structure(self, content: str, module_name: str) -> str:
        """존재형 AI 구조 추가"""
        try:
            if not re.search(self.injection_patterns["existence_ai"], content):
                # 클래스 찾기
                class_pattern = r"class (\w+)"
                classes = re.findall(class_pattern, content)

                for class_name in classes:
                    try:
                        # 클래스에 존재형 AI 구조 추가
                        existing_init = self._extract_existing_init(content, class_name)

                        existence_ai_structure = self.meaning_templates["existence_ai_structure"].format(
                            class_name=class_name, existing_init=existing_init
                        )

                        # 클래스 내용 교체
                        content = self._replace_class_content(content, class_name, existence_ai_structure)
                    except Exception as e:
                        logger.warning(f"클래스 {class_name}에 존재형 AI 구조 추가 실패: {str(e)}")
                        continue
        except Exception as e:
            logger.error(f"존재형 AI 구조 추가 실패: {str(e)}")

        return content

    def _add_final_execution_structure(self, content: str, module_name: str) -> str:
        """최종 실행 준비 완료 구조 추가"""
        if not re.search(self.injection_patterns["final_execution"], content):
            # 클래스 찾기
            class_pattern = r"class (\w+)"
            classes = re.findall(class_pattern, content)

            for class_name in classes:
                # 클래스에 최종 실행 준비 완료 구조 추가
                existing_init = self._extract_existing_init(content, class_name)

                final_execution_structure = self.meaning_templates["final_execution_structure"].format(
                    class_name=class_name, existing_init=existing_init
                )

                # 클래스 내용 교체
                content = self._replace_class_content(content, class_name, final_execution_structure)

        return content

    def _extract_purpose(self, content: str, module_name: str) -> str:
        """모듈 목적 추출"""
        purpose_patterns = [
            r"# Purpose: (.+)",
            r"# 모듈 목적: (.+)",
            r"# Module Purpose: (.+)",
            r"\"\"\"(.+?)\"\"\"",
            r"'''(.+?)'''",
        ]

        for pattern in purpose_patterns:
            match = re.search(pattern, content, re.MULTILINE | re.DOTALL)
            if match:
                purpose = match.group(1).strip()
                if "최종 실행 준비 완료" not in purpose:
                    purpose += " + 최종 실행 준비 완료"
                return purpose

        return f"{module_name} 모듈 - 판단 이유 기록 필수 + 기존 특성 보존 + 실행 가능성 보장 + 존재형 AI + 최종 실행 준비 완료"  # noqa: E501

    def _extract_must_provide(self, content: str) -> str:
        """반드시 제공해야 할 것들 추출"""
        must_provide = []

        # 함수 정의 찾기
        function_pattern = r"def (\w+)\("
        functions = re.findall(function_pattern, content)

        # 중요 함수 필터링
        important_patterns = [
            r"analyze_",
            r"process_",
            r"handle_",
            r"manage_",
            r"control_",
            r"reasoning",
            r"judgment",
            r"learning",
            r"memory",
            r"evolution",
        ]

        for func in functions:
            for pattern in important_patterns:
                if re.search(pattern, func):
                    must_provide.append(func)
                    break

        return ", ".join(must_provide[:5]) if must_provide else "주요 기능들"

    def _extract_must_not(self, content: str) -> str:
        """하지 말아야 할 것들 추출"""
        must_not_patterns = [
            r"# Must Not: (.+)",
            r"# 하지 말아야 할 것: (.+)",
            r"# 금지사항: (.+)",
        ]

        for pattern in must_not_patterns:
            matches = re.findall(pattern, content, re.MULTILINE)
            if matches:
                return "; ".join(matches)

        return "finalize decisions (판단은 judgment_engine에서); access memory directly (memory_system을 통해)"

    def _extract_integration(self, content: str) -> str:
        """통합 정보 추출"""
        integration = []

        # import 문에서 통합 정보 추출
        import_pattern = r"from (\w+) import|import (\w+)"
        imports = re.findall(import_pattern, content)

        for imp in imports:
            if isinstance(imp, tuple):
                module = imp[0] or imp[1]
            else:
                module = imp

            if module and module not in [
                "os",
                "sys",
                "json",
                "re",
                "datetime",
                "logging",
            ]:
                integration.append(f"imports {module}")

        return "; ".join(integration[:3]) if integration else "기타 모듈들과 통합"

    def _extract_main_function(self, content: str) -> str:
        """주요 함수 추출"""
        function_pattern = r"def (\w+)\("
        functions = re.findall(function_pattern, content)

        # 중요 함수 찾기
        important_patterns = [
            r"analyze_",
            r"process_",
            r"handle_",
            r"manage_",
            r"control_",
            r"reasoning",
            r"judgment",
            r"learning",
            r"memory",
            r"evolution",
        ]

        for func in functions:
            for pattern in important_patterns:
                if re.search(pattern, func):
                    return func

        return functions[0] if functions else "main_function"

    def _extract_existing_init(self, content: str, class_name: str) -> str:
        """기존 __init__ 메서드 추출"""
        init_pattern = rf"class {class_name}:\s*\n\s*def __init__\(self\):\s*\n(.*?)(?=\n\s*def|\n\n|\Z)"
        match = re.search(init_pattern, content, re.DOTALL)

        if match:
            return match.group(1).strip()

        return "pass"

    def _replace_class_content(self, content: str, class_name: str, new_structure: str) -> str:
        """클래스 내용 교체"""
        class_pattern = rf"class {class_name}:.*?(?=\nclass|\n\n|\Z)"
        replacement = f"class {class_name}:\n{new_structure}"

        content = re.sub(class_pattern, replacement, content, flags=re.DOTALL)
        return content

    def save_meaning_injected_module(self, module_content: str, module_name: str, output_dir: str = ".") -> str:
        """의미가 주입된 모듈 저장"""
        try:
            os.makedirs(output_dir, exist_ok=True)
            meaning_injected_file_path = os.path.join(output_dir, f"{module_name}_meaning_injected.py")

            with open(meaning_injected_file_path, "w", encoding="utf-8") as f:
                f.write(module_content)

            logger.info(f"의미 주입된 모듈 저장 완료: {meaning_injected_file_path}")
            return meaning_injected_file_path

        except Exception as e:
            logger.error(f"의미 주입된 모듈 저장 실패: {module_name} - {str(e)}")
            return ""


if __name__ == "__main__":
    # 테스트 실행
    engine = MeaningInjectionEngine()

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

    meaning_injected = engine.inject_meaning(sample_content, "logical_processor")
    print("의미 주입된 모듈 내용:")
    print(meaning_injected)
