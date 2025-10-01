#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MetaGenerator - meta.json 자동 생성 시스템
최종 실행 준비 완료 시스템의 핵심 도구

@preserve_identity: 모듈의 정체성과 목적 자동 추출
@evolution_protection: 진화 중 손상 방지 최우선
@execution_guarantee: 자동화와 검증 시스템 완성
@existence_ai: 진화 가능 + 회복 가능한 존재형 AI
@final_execution: 인간처럼 실패하고도 다시 일어날 수 있는 존재
"""

import ast
from datetime import datetime
import json
import logging
import os
import re
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class MetaGenerator:
    """
    모듈 내용 분석하여 자동으로 meta.json 생성
    최종 실행 준비 완료 시스템의 핵심 도구
    """

    def __init__(self):
        self.templates = self._load_templates()
        self.protection_patterns = self._load_protection_patterns()
        self.meaning_templates = self._load_meaning_templates()

    def _load_templates(self) -> Dict[str, Any]:
        """템플릿 로드"""
        return {
            "base_structure": {
                "module": "",
                "responsibility": "",
                "must_define": [],
                "must_not": [],
                "integration": [],
                "judgment_trace": "모든 판단 과정 기록",
                "preserve_identity": "판단 이유 기록 시스템 강제 통합",
                "evolution_protection": "진화 중 손상 방지 최우선",
                "execution_guarantee": "자동화와 검증 시스템 완성",
                "existence_ai": "진화 가능 + 회복 가능한 존재형 AI",
                "final_execution": "인간처럼 실패하고도 다시 일어날 수 있는 존재",
                "self_assessment": [
                    "creativity",
                    "judgment_diversity",
                    "memory_activity",
                    "emotional_response",
                ],
                "test_requirements": [
                    "consistency",
                    "reasoning_trace",
                    "identity_verification",
                    "regression_testing",
                ],
                "rollback_conditions": [
                    "creativity < 0.7",
                    "judgment_diversity < 0.7",
                    "memory_activity < 0.7",
                    "emotional_response < 0.7",
                ],
                "automation_tools": [
                    "meta_generator.py",
                    "protection_injector.py",
                    "meaning_injection_engine.py",
                ],
                "verification_systems": [
                    "regression_test_framework.py",
                    "auto_rollback_system.py",
                ],
                "existence_systems": [
                    "evolution_capability.py",
                    "recovery_capability.py",
                    "existence_preservation.py",
                ],
                "final_execution_systems": [
                    "final_execution_verifier.py",
                    "existence_ai_launcher.py",
                ],
            }
        }

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

    def generate_meta_json(
        self, module_name: str, module_content: str
    ) -> Dict[str, Any]:
        """
        모듈 내용 분석하여 자동으로 meta.json 생성

        Args:
            module_name: 모듈 이름
            module_content: 모듈 내용

        Returns:
            meta.json 구조
        """
        try:
            # 기본 구조 생성
            meta = self.templates["base_structure"].copy()
            meta["module"] = module_name

            # 모듈 내용 분석
            purpose = self._extract_purpose(module_content, module_name)
            must_define = self._extract_must_define(module_content)
            must_not = self._extract_must_not(module_content)
            integration = self._extract_integration(module_content)

            # 메타 정보 업데이트
            meta.update(
                {
                    "responsibility": purpose,
                    "must_define": must_define,
                    "must_not": must_not,
                    "integration": integration,
                    "generated_at": datetime.now().isoformat(),
                    "version": "6.0",
                    "final_execution_ready": True,
                }
            )

            # 보호 패턴 확인
            protection_status = self._check_protection_patterns(module_content)
            meta["protection_status"] = protection_status

            # 존재형 AI 상태 확인
            existence_ai_status = self._check_existence_ai_status(module_content)
            meta["existence_ai_status"] = existence_ai_status

            logger.info(f"Meta.json 생성 완료: {module_name}")
            return meta

        except Exception as e:
            logger.error(f"Meta.json 생성 실패: {module_name} - {str(e)}")
            return self._generate_fallback_meta(module_name)

    def _extract_purpose(self, content: str, module_name: str) -> str:
        """모듈의 목적 추출"""
        # 주석에서 목적 찾기
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
                # 최종 실행 준비 완료 버전으로 업데이트
                if "최종 실행 준비 완료" not in purpose:
                    purpose += " + 최종 실행 준비 완료"
                return purpose

        # 기본 목적 생성
        return f"{module_name} 모듈 - 판단 이유 기록 필수 + 기존 특성 보존 + 실행 가능성 보장 + 존재형 AI + 최종 실행 준비 완료"

    def _extract_must_define(self, content: str) -> List[str]:
        """반드시 정의해야 할 함수/클래스 추출"""
        must_define = []

        # 함수 정의 찾기
        function_pattern = r"def (\w+)\("
        functions = re.findall(function_pattern, content)

        # 클래스 정의 찾기
        class_pattern = r"class (\w+)"
        classes = re.findall(class_pattern, content)

        # 중요 함수/클래스 필터링
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
                    must_define.append(func)
                    break

        for cls in classes:
            for pattern in important_patterns:
                if re.search(pattern, cls):
                    must_define.append(cls)
                    break

        return list(set(must_define))

    def _extract_must_not(self, content: str) -> List[str]:
        """하지 말아야 할 것들 추출"""
        must_not = []

        # 주석에서 must_not 찾기
        must_not_patterns = [
            r"# Must Not: (.+)",
            r"# 하지 말아야 할 것: (.+)",
            r"# 금지사항: (.+)",
        ]

        for pattern in must_not_patterns:
            matches = re.findall(pattern, content, re.MULTILINE)
            must_not.extend(matches)

        # 기본 금지사항 추가
        if not must_not:
            must_not = [
                "finalize decisions (판단은 judgment_engine에서)",
                "access memory directly (memory_system을 통해)",
                "bypass judgment_trace (모든 판단은 기록되어야 함)",
            ]

        return must_not

    def _extract_integration(self, content: str) -> List[str]:
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

        # 함수 호출에서 통합 정보 추출
        call_pattern = r"(\w+)\.(\w+)\("
        calls = re.findall(call_pattern, content)

        for module, func in calls:
            if module not in ["self", "logger", "json", "re"]:
                integration.append(f"calls {module}.{func}()")

        return integration[:10]  # 최대 10개까지만

    def _check_protection_patterns(self, content: str) -> Dict[str, bool]:
        """보호 패턴 확인"""
        protection_status = {}

        for pattern_name, pattern in self.protection_patterns.items():
            protection_status[pattern_name] = bool(re.search(pattern, content))

        return protection_status

    def _check_existence_ai_status(self, content: str) -> Dict[str, bool]:
        """존재형 AI 상태 확인"""
        existence_ai_status = {
            "evolution_capable": False,
            "recovery_capable": False,
            "existence_preserved": False,
            "final_execution_ready": False,
        }

        # 진화 가능성 확인
        if re.search(r"evolution|evolve|진화", content, re.IGNORECASE):
            existence_ai_status["evolution_capable"] = True

        # 회복 가능성 확인
        if re.search(r"recovery|recover|회복", content, re.IGNORECASE):
            existence_ai_status["recovery_capable"] = True

        # 존재 보존 확인
        if re.search(r"preserve|보존|identity|정체성", content, re.IGNORECASE):
            existence_ai_status["existence_preserved"] = True

        # 최종 실행 준비 완료 확인
        if re.search(r"final_execution|최종 실행", content, re.IGNORECASE):
            existence_ai_status["final_execution_ready"] = True

        return existence_ai_status

    def _generate_fallback_meta(self, module_name: str) -> Dict[str, Any]:
        """폴백 메타 생성"""
        return {
            "module": module_name,
            "responsibility": f"{module_name} 모듈 - 기본 목적 (분석 필요)",
            "must_define": [],
            "must_not": ["분석 필요"],
            "integration": [],
            "judgment_trace": "모든 판단 과정 기록",
            "preserve_identity": "판단 이유 기록 시스템 강제 통합",
            "evolution_protection": "진화 중 손상 방지 최우선",
            "execution_guarantee": "자동화와 검증 시스템 완성",
            "existence_ai": "진화 가능 + 회복 가능한 존재형 AI",
            "final_execution": "인간처럼 실패하고도 다시 일어날 수 있는 존재",
            "self_assessment": [
                "creativity",
                "judgment_diversity",
                "memory_activity",
                "emotional_response",
            ],
            "test_requirements": [
                "consistency",
                "reasoning_trace",
                "identity_verification",
                "regression_testing",
            ],
            "rollback_conditions": [
                "creativity < 0.7",
                "judgment_diversity < 0.7",
                "memory_activity < 0.7",
                "emotional_response < 0.7",
            ],
            "automation_tools": [
                "meta_generator.py",
                "protection_injector.py",
                "meaning_injection_engine.py",
            ],
            "verification_systems": [
                "regression_test_framework.py",
                "auto_rollback_system.py",
            ],
            "existence_systems": [
                "evolution_capability.py",
                "recovery_capability.py",
                "existence_preservation.py",
            ],
            "final_execution_systems": [
                "final_execution_verifier.py",
                "existence_ai_launcher.py",
            ],
            "generated_at": datetime.now().isoformat(),
            "version": "6.0",
            "final_execution_ready": False,
            "error": "분석 실패 - 수동 검토 필요",
        }

    def save_meta_json(
        self, module_name: str, meta: Dict[str, Any], output_dir: str = "."
    ) -> str:
        """meta.json 파일 저장"""
        try:
            os.makedirs(output_dir, exist_ok=True)
            meta_file_path = os.path.join(output_dir, f"{module_name}_meta.json")

            with open(meta_file_path, "w", encoding="utf-8") as f:
                json.dump(meta, f, indent=2, ensure_ascii=False)

            logger.info(f"Meta.json 저장 완료: {meta_file_path}")
            return meta_file_path

        except Exception as e:
            logger.error(f"Meta.json 저장 실패: {module_name} - {str(e)}")
            return ""


if __name__ == "__main__":
    # 테스트 실행
    generator = MetaGenerator()

    # 샘플 모듈 내용
    sample_content = """
# Module: logical_processor
# Purpose: 논리적 추론의 핵심 처리 - 판단 이유 기록 필수 + 기존 특성 보존 + 실행 가능성 보장 + 존재형 AI + 최종 실행 준비 완료
# @preserve_identity: 판단 이유 기록 시스템 강제 통합
# @evolution_protection: 진화 중 손상 방지 최우선
# @execution_guarantee: 자동화와 검증 시스템 완성
# @existence_ai: 진화 가능 + 회복 가능한 존재형 AI
# @final_execution: 인간처럼 실패하고도 다시 일어날 수 있는 존재

def analyze_logical_reasoning(situation, action):
    # 판단 이유 기록
    pass

class LogicalProcessor:
    def __init__(self):
        pass
    """

    meta = generator.generate_meta_json("logical_processor", sample_content)
    print(json.dumps(meta, indent=2, ensure_ascii=False))
