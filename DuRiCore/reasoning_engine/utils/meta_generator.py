#!/usr/bin/env python3
"""
DuRi 존재적 리팩토링 - meta.json 자동 생성 도구
Phase 3 리팩토링: 자동화 도구 구현
"""

import json
import logging
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


@dataclass
class ModuleAnalysis:
    """모듈 분석 결과"""

    module_name: str
    purpose: str
    must_define: List[str]
    must_not: List[str]
    integration: List[str]
    judgment_trace: str
    preserve_identity: str
    evolution_protection: str
    execution_guarantee: str
    existence_ai: str
    final_execution: str


class MetaGenerator:
    """meta.json 자동 생성 클래스"""

    def __init__(self):
        """MetaGenerator 초기화"""
        self.templates = self._load_templates()
        logger.info("MetaGenerator 초기화 완료")

    def _load_templates(self) -> Dict[str, Any]:
        """템플릿 로드"""
        return {
            "default_purpose": "모듈의 기본 목적",
            "default_judgment_trace": "모든 판단 과정 기록",
            "default_preserve_identity": "판단 이유 기록 시스템 강제 통합",
            "default_evolution_protection": "진화 중 손상 방지 최우선",
            "default_execution_guarantee": "자동화와 검증 시스템 완성",
            "default_existence_ai": "진화 가능 + 회복 가능한 존재형 AI",
            "default_final_execution": "인간처럼 실패하고도 다시 일어날 수 있는 존재",
        }

    def generate_meta_json(self, module_name: str, module_content: str) -> dict:
        """meta.json 자동 생성"""
        logger.info(f"meta.json 생성 시작: {module_name}")

        # 모듈 내용 분석
        analysis = self._analyze_module_content(module_name, module_content)

        # meta.json 생성
        meta_json = {
            "module": analysis.module_name,
            "responsibility": analysis.purpose,
            "must_define": analysis.must_define,
            "must_not": analysis.must_not,
            "integration": analysis.integration,
            "judgment_trace": analysis.judgment_trace,
            "preserve_identity": analysis.preserve_identity,
            "evolution_protection": analysis.evolution_protection,
            "execution_guarantee": analysis.execution_guarantee,
            "existence_ai": analysis.existence_ai,
            "final_execution": analysis.final_execution,
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

        logger.info(f"meta.json 생성 완료: {module_name}")
        return meta_json

    def _analyze_module_content(self, module_name: str, module_content: str) -> ModuleAnalysis:
        """모듈 내용 분석"""
        # 목적 추출
        purpose = self._extract_purpose(module_content, module_name)

        # 필수 정의 함수 추출
        must_define = self._extract_must_define(module_content)

        # 금지 함수 추출
        must_not = self._extract_must_not(module_content)

        # 통합 방식 추출
        integration = self._extract_integration(module_content)

        # 기본값 설정
        judgment_trace = self.templates["default_judgment_trace"]
        preserve_identity = self.templates["default_preserve_identity"]
        evolution_protection = self.templates["default_evolution_protection"]
        execution_guarantee = self.templates["default_execution_guarantee"]
        existence_ai = self.templates["default_existence_ai"]
        final_execution = self.templates["default_final_execution"]

        return ModuleAnalysis(
            module_name=module_name,
            purpose=purpose,
            must_define=must_define,
            must_not=must_not,
            integration=integration,
            judgment_trace=judgment_trace,
            preserve_identity=preserve_identity,
            evolution_protection=evolution_protection,
            execution_guarantee=execution_guarantee,
            existence_ai=existence_ai,
            final_execution=final_execution,
        )

    def _extract_purpose(self, module_content: str, module_name: str) -> str:
        """목적 추출"""
        # 주석에서 목적 찾기
        purpose_patterns = [
            r"# Purpose:\s*(.+)",
            r"# 목적:\s*(.+)",
            r'"""(.+?)"""',
            r"'''(.+?)'''",
        ]

        for pattern in purpose_patterns:
            matches = re.findall(pattern, module_content, re.MULTILINE | re.DOTALL)
            if matches:
                return matches[0].strip()

        # 기본 목적 생성
        if "logical" in module_name.lower():
            return "논리적 추론의 핵심 처리 - 판단 이유 기록 필수 + 기존 특성 보존 + 실행 가능성 보장 + 존재형 AI + 최종 실행 준비 완료"
        elif "reasoning" in module_name.lower():
            return "추론 엔진의 핵심 처리 - 판단 이유 기록 필수 + 기존 특성 보존 + 실행 가능성 보장 + 존재형 AI + 최종 실행 준비 완료"
        elif "deductive" in module_name.lower():
            return "연역적 추론 전략 - 판단 이유 기록 필수 + 기존 특성 보존 + 실행 가능성 보장 + 존재형 AI + 최종 실행 준비 완료"
        elif "inductive" in module_name.lower():
            return "귀납적 추론 전략 - 판단 이유 기록 필수 + 기존 특성 보존 + 실행 가능성 보장 + 존재형 AI + 최종 실행 준비 완료"
        elif "abductive" in module_name.lower():
            return "가설적 추론 전략 - 판단 이유 기록 필수 + 기존 특성 보존 + 실행 가능성 보장 + 존재형 AI + 최종 실행 준비 완료"
        else:
            return f"{module_name} 모듈의 핵심 처리 - 판단 이유 기록 필수 + 기존 특성 보존 + 실행 가능성 보장 + 존재형 AI + 최종 실행 준비 완료"

    def _extract_must_define(self, module_content: str) -> List[str]:
        """필수 정의 함수 추출"""
        # 함수 정의 찾기
        function_pattern = r"def\s+(\w+)\s*\("
        functions = re.findall(function_pattern, module_content)

        # 클래스 메서드 찾기
        method_pattern = r"def\s+(\w+)\s*\(self"
        methods = re.findall(method_pattern, module_content)

        # 필수 함수 목록
        all_functions = functions + methods

        # 중복 제거 및 정렬
        unique_functions = list(set(all_functions))
        unique_functions.sort()

        return unique_functions[:10]  # 최대 10개 반환

    def _extract_must_not(self, module_content: str) -> List[str]:
        """금지 함수 추출"""
        # 일반적인 금지 함수들
        default_must_not = [
            "finalize_decisions",
            "access_memory_directly",
            "store_memory",
            "select_strategy",
        ]

        # 모듈 내용에서 금지 패턴 찾기
        forbidden_patterns = [
            r"# Must Not:\s*(.+)",
            r"# 금지:\s*(.+)",
            r"@must_not\s*(.+)",
        ]

        for pattern in forbidden_patterns:
            matches = re.findall(pattern, module_content, re.MULTILINE | re.DOTALL)
            if matches:
                forbidden_items = [item.strip() for item in matches[0].split(",")]
                default_must_not.extend(forbidden_items)

        return list(set(default_must_not))

    def _extract_integration(self, module_content: str) -> List[str]:
        """통합 방식 추출"""
        # 기본 통합 방식
        default_integration = ["judgment_trace.record()", "reasoning_engine.receive()"]

        # 모듈 내용에서 통합 패턴 찾기
        integration_patterns = [
            r"# Integration:\s*(.+)",
            r"# 통합:\s*(.+)",
            r"@integration\s*(.+)",
        ]

        for pattern in integration_patterns:
            matches = re.findall(pattern, module_content, re.MULTILINE | re.DOTALL)
            if matches:
                integration_items = [item.strip() for item in matches[0].split(",")]
                default_integration.extend(integration_items)

        return list(set(default_integration))

    def save_meta_json(self, module_name: str, meta_json: dict, output_dir: str = ".") -> str:
        """meta.json 파일 저장"""
        output_path = Path(output_dir) / f"{module_name}.meta.json"

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(meta_json, f, indent=2, ensure_ascii=False)

        logger.info(f"meta.json 저장 완료: {output_path}")
        return str(output_path)


def main():
    """메인 함수"""
    import sys

    if len(sys.argv) < 2:
        print("사용법: python3 meta_generator.py <module_name> [module_content_file]")
        sys.exit(1)

    module_name = sys.argv[1]
    module_content_file = sys.argv[2] if len(sys.argv) > 2 else None

    generator = MetaGenerator()

    if module_content_file:
        with open(module_content_file, "r", encoding="utf-8") as f:
            module_content = f.read()
    else:
        # 기본 모듈 내용 생성
        module_content = f"""
# Module: {module_name}
# Purpose: {module_name} 모듈의 핵심 처리 - 판단 이유 기록 필수 + 기존 특성 보존 + 실행 가능성 보장 + 존재형 AI + 최종 실행 준비 완료
# Must Provide:
#   - analyze_{module_name.lower()}(data)
#   - process_{module_name.lower()}(input)
# Must Not:
#   - finalize decisions (판단은 judgment_engine에서)
#   - access memory directly (memory_system을 통해)
# Integration:
#   - Calls judgment_trace.record() for all decisions
#   - Returns to reasoning_engine for final judgment
"""

    meta_json = generator.generate_meta_json(module_name, module_content)
    output_path = generator.save_meta_json(module_name, meta_json)

    print(f"✅ meta.json 생성 완료: {output_path}")


if __name__ == "__main__":
    main()
