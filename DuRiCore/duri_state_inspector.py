#!/usr/bin/env python3
"""
DuRi State Inspector
DuRi의 현재 상태를 심도있게 진단하는 도구

기능:
1. 시스템 구조 분석
2. 모듈 연결성 테스트
3. 의존성 분석
4. 문제점 식별
5. 진단 리포트 생성
"""

import ast
import importlib
import inspect
import json
import os
import sys
import time
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple


@dataclass
class ModuleInfo:
    """모듈 정보"""

    name: str
    path: str
    size: int
    lines: int
    functions: List[str]
    classes: List[str]
    imports: List[str]
    can_import: bool
    import_error: Optional[str] = None


@dataclass
class SystemAnalysisReport:
    """시스템 분석 리포트"""

    total_files: int
    python_files: int
    markdown_files: int
    other_files: int
    total_lines: int
    total_size: int
    modules: Dict[str, ModuleInfo]
    dependency_graph: Dict[str, List[str]]
    connectivity_status: Dict[str, bool]
    problems: List[str]
    timestamp: str


class DuriStateInspector:
    """DuRi 상태 진단 도구"""

    def __init__(self, base_path: str = "."):
        self.base_path = Path(base_path)
        self.modules: Dict[str, ModuleInfo] = {}
        self.dependency_graph: Dict[str, List[str]] = {}
        self.connectivity_status: Dict[str, bool] = {}
        self.problems: List[str] = []

    def scan_all_systems(self) -> SystemAnalysisReport:
        """전체 시스템 스캔"""
        print("🔍 DuRi 시스템 구조 분석 시작...")

        # 1. 모든 파일 스캔
        self._scan_all_files()

        # 2. Python 모듈 분석
        self._analyze_python_modules()

        # 3. 의존성 분석
        self._analyze_dependencies()

        # 4. 연결성 테스트
        self._test_connectivity()

        # 5. 문제점 식별
        self._identify_problems()

        return self._generate_report()

    def _scan_all_files(self):
        """모든 파일 스캔"""
        print("📁 파일 스캔 중...")

        for file_path in self.base_path.rglob("*"):
            if file_path.is_file():
                relative_path = file_path.relative_to(self.base_path)

                # 파일 정보 수집
                size = file_path.stat().st_size
                lines = 0

                if file_path.suffix in [".py", ".md", ".txt"]:
                    try:
                        with open(file_path, "r", encoding="utf-8") as f:
                            lines = len(f.readlines())
                    except:
                        lines = 0

                # 모듈 정보 생성
                module_name = str(relative_path).replace("/", ".").replace("\\", ".")
                if module_name.endswith(".py"):
                    module_name = module_name[:-3]

                self.modules[str(relative_path)] = ModuleInfo(
                    name=module_name,
                    path=str(relative_path),
                    size=size,
                    lines=lines,
                    functions=[],
                    classes=[],
                    imports=[],
                    can_import=False,
                )

    def _analyze_python_modules(self):
        """Python 모듈 상세 분석"""
        print("🐍 Python 모듈 분석 중...")

        for file_path, module_info in self.modules.items():
            if not file_path.endswith(".py"):
                continue

            full_path = self.base_path / file_path

            try:
                # AST 분석으로 함수, 클래스, import 추출
                with open(full_path, "r", encoding="utf-8") as f:
                    content = f.read()
                    tree = ast.parse(content)

                # 함수와 클래스 추출
                functions = []
                classes = []
                imports = []

                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef):
                        functions.append(node.name)
                    elif isinstance(node, ast.ClassDef):
                        classes.append(node.name)
                    elif isinstance(node, ast.Import):
                        for alias in node.names:
                            imports.append(alias.name)
                    elif isinstance(node, ast.ImportFrom):
                        if node.module:
                            imports.append(node.module)

                # 모듈 정보 업데이트
                module_info.functions = functions
                module_info.classes = classes
                module_info.imports = imports

            except Exception as e:
                print(f"⚠️  모듈 분석 실패: {file_path} - {e}")

    def _analyze_dependencies(self):
        """의존성 분석"""
        print("🔗 의존성 분석 중...")

        for file_path, module_info in self.modules.items():
            if not file_path.endswith(".py"):
                continue

            dependencies = []
            for import_name in module_info.imports:
                # 로컬 모듈인지 확인
                if import_name.startswith(".") or import_name in self.modules:
                    dependencies.append(import_name)

            self.dependency_graph[file_path] = dependencies

    def _test_connectivity(self):
        """모듈 연결성 테스트"""
        print("🔌 연결성 테스트 중...")

        for file_path, module_info in self.modules.items():
            if not file_path.endswith(".py"):
                continue

            try:
                # import 테스트
                module_name = module_info.name
                if module_name.startswith("."):
                    module_name = module_name[1:]

                # sys.path에 현재 디렉토리 추가
                sys.path.insert(0, str(self.base_path))

                # 모듈 import 시도
                module = importlib.import_module(module_name)

                # 함수 호출 가능성 테스트
                callable_functions = []
                for func_name in module_info.functions:
                    if hasattr(module, func_name):
                        func = getattr(module, func_name)
                        if callable(func):
                            callable_functions.append(func_name)

                module_info.can_import = True
                self.connectivity_status[file_path] = True

                print(f"✅ {file_path}: import 성공, {len(callable_functions)}개 함수 호출 가능")

            except Exception as e:
                module_info.can_import = False
                module_info.import_error = str(e)
                self.connectivity_status[file_path] = False
                print(f"❌ {file_path}: import 실패 - {e}")

    def _identify_problems(self):
        """문제점 식별"""
        print("🚨 문제점 식별 중...")

        # 1. import 실패한 모듈들
        failed_imports = [path for path, status in self.connectivity_status.items() if not status]
        if failed_imports:
            self.problems.append(f"Import 실패 모듈: {len(failed_imports)}개")
            for path in failed_imports[:5]:  # 상위 5개만 표시
                self.problems.append(f"  - {path}")

        # 2. 의존성 문제
        circular_deps = self._find_circular_dependencies()
        if circular_deps:
            self.problems.append(f"순환 참조 발견: {len(circular_deps)}개")

        # 3. 실행 루프 관련 모듈 확인
        execution_modules = ["judgment", "action", "feedback", "orchestrator", "engine"]
        missing_execution = []
        for module in execution_modules:
            found = False
            for path in self.modules.keys():
                if module in path.lower():
                    found = True
                    break
            if not found:
                missing_execution.append(module)

        if missing_execution:
            self.problems.append(f"실행 루프 관련 모듈 부족: {missing_execution}")

    def _find_circular_dependencies(self) -> List[List[str]]:
        """순환 참조 찾기"""
        visited = set()
        rec_stack = set()
        cycles = []

        def dfs(node):
            visited.add(node)
            rec_stack.add(node)

            for neighbor in self.dependency_graph.get(node, []):
                if neighbor not in visited:
                    if dfs(neighbor):
                        return True
                elif neighbor in rec_stack:
                    cycles.append([node, neighbor])
                    return True

            rec_stack.remove(node)
            return False

        for node in self.dependency_graph:
            if node not in visited:
                dfs(node)

        return cycles

    def _generate_report(self) -> SystemAnalysisReport:
        """진단 리포트 생성"""
        print("📊 진단 리포트 생성 중...")

        # 통계 계산
        python_files = len([f for f in self.modules.keys() if f.endswith(".py")])
        markdown_files = len([f for f in self.modules.keys() if f.endswith(".md")])
        other_files = len(self.modules) - python_files - markdown_files

        total_lines = sum(m.lines for m in self.modules.values())
        total_size = sum(m.size for m in self.modules.values())

        return SystemAnalysisReport(
            total_files=len(self.modules),
            python_files=python_files,
            markdown_files=markdown_files,
            other_files=other_files,
            total_lines=total_lines,
            total_size=total_size,
            modules=self.modules,
            dependency_graph=self.dependency_graph,
            connectivity_status=self.connectivity_status,
            problems=self.problems,
            timestamp=datetime.now().isoformat(),
        )

    def print_summary(self, report: SystemAnalysisReport):
        """진단 결과 요약 출력"""
        print("\n" + "=" * 60)
        print("🔍 DURI DIAGNOSTIC REPORT")
        print("=" * 60)

        print(f"\n📁 시스템 구조:")
        print(f"  - 총 파일 수: {report.total_files}개")
        print(f"  - Python 파일: {report.python_files}개")
        print(f"  - Markdown 파일: {report.markdown_files}개")
        print(f"  - 기타 파일: {report.other_files}개")
        print(f"  - 총 코드 라인: {report.total_lines:,} lines")
        print(f"  - 총 파일 크기: {report.total_size:,} bytes")

        print(f"\n🔌 연결성 진단:")
        working_modules = sum(1 for status in report.connectivity_status.values() if status)
        failed_modules = len(report.connectivity_status) - working_modules
        print(f"  - 호출 가능한 모듈: {working_modules}개")
        print(f"  - 호출 불가 모듈: {failed_modules}개")
        print(f"  - 연결성 성공률: {working_modules/(working_modules+failed_modules)*100:.1f}%")

        print(f"\n🚨 발견된 문제점:")
        if report.problems:
            for i, problem in enumerate(report.problems, 1):
                print(f"  {i}. {problem}")
        else:
            print("  ✅ 특별한 문제점이 발견되지 않았습니다.")

        print(f"\n⏰ 진단 시간: {report.timestamp}")
        print("=" * 60)

    def save_detailed_report(
        self,
        report: SystemAnalysisReport,
        filename: str = "duri_diagnostic_report.json",
    ):
        """상세 진단 리포트 저장"""
        report_dict = asdict(report)

        # 모듈 정보에서 불필요한 데이터 제거
        for module_info in report_dict["modules"].values():
            if "import_error" in module_info and module_info["import_error"] is None:
                del module_info["import_error"]

        with open(filename, "w", encoding="utf-8") as f:
            json.dump(report_dict, f, indent=2, ensure_ascii=False)

        print(f"📄 상세 리포트 저장: {filename}")


def main():
    """메인 실행 함수"""
    print("🚀 DuRi 상태 진단 시작")
    print("=" * 50)

    # 진단 도구 생성
    inspector = DuriStateInspector()

    # 전체 시스템 분석
    report = inspector.scan_all_systems()

    # 결과 출력
    inspector.print_summary(report)

    # 상세 리포트 저장
    inspector.save_detailed_report(report)

    print("\n✅ 진단 완료!")


if __name__ == "__main__":
    main()
