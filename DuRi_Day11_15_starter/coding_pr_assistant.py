#!/usr/bin/env python3
"""
코딩 PR 보조 PoU 파일럿 시스템 (Day 33)
코드 리뷰, 보안 스캔, 성능 최적화를 통합한 시스템
"""

import hashlib
import json
import logging
import re
import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


@dataclass
class CodeFile:
    """코드 파일 정보"""

    file_path: str
    content: str
    language: str
    size: int
    lines: int
    complexity: int
    last_modified: datetime


@dataclass
class SecurityIssue:
    """보안 이슈"""

    issue_id: str
    severity: str  # critical, high, medium, low
    category: str  # injection, xss, csrf, etc.
    description: str
    file_path: str
    line_number: int
    suggestion: str
    cwe_id: str


@dataclass
class PerformanceIssue:
    """성능 이슈"""

    issue_id: str
    severity: str  # high, medium, low
    category: str  # algorithm, memory, database, etc.
    description: str
    file_path: str
    line_number: int
    suggestion: str
    impact_score: float


@dataclass
class CodeReview:
    """코드 리뷰 결과"""

    review_id: str
    file_path: str
    overall_score: float
    security_score: float
    performance_score: float
    maintainability_score: float
    test_coverage_score: float
    issues: List[Any]
    suggestions: List[str]
    approved: bool


class CodingPRAssistant:
    """코딩 PR 보조 시스템"""

    def __init__(self):
        self.security_patterns = self._load_security_patterns()
        self.performance_patterns = self._load_performance_patterns()
        self.code_standards = self._load_code_standards()
        self.logger = self._setup_logging()

    def _load_security_patterns(self) -> Dict[str, List[str]]:
        """보안 패턴 로드"""
        return {
            "injection": [
                r"SELECT.*\+.*",  # SQL injection
                r"eval\s*\(",  # Code injection
                r"exec\s*\(",  # Command injection
                r"system\s*\(",  # Command injection
            ],
            "xss": [
                r"innerHTML\s*=",  # XSS vulnerability
                r"document\.write",  # XSS vulnerability
                r"\.html\s*\(",  # XSS vulnerability
            ],
            "csrf": [
                r"<form.*method.*post",  # CSRF vulnerability
                r"XMLHttpRequest",  # CSRF vulnerability
            ],
            "sensitive_data": [
                r"password\s*=",  # Hardcoded password
                r"api_key\s*=",  # Hardcoded API key
                r"secret\s*=",  # Hardcoded secret
                r"token\s*=",  # Hardcoded token
            ],
        }

    def _load_performance_patterns(self) -> Dict[str, List[str]]:
        """성능 패턴 로드"""
        return {
            "algorithm": [
                r"for.*for.*for",  # Nested loops
                r"while.*while",  # Nested while loops
                r"O\(n\^3\)",  # Cubic complexity
            ],
            "memory": [
                r"new\s+\w+\[\d+\]",  # Large array allocation
                r"malloc\s*\(",  # Manual memory allocation
                r"free\s*\(",  # Manual memory deallocation
            ],
            "database": [
                r"SELECT\s+\*",  # Select all columns
                r"WHERE.*LIKE.*%",  # Pattern matching
                r"ORDER\s+BY.*DESC",  # Sorting
            ],
            "io": [
                r"readFileSync",  # Synchronous file read
                r"writeFileSync",  # Synchronous file write
                r"fs\.readFile",  # File operations
            ],
        }

    def _load_code_standards(self) -> Dict[str, Any]:
        """코드 표준 로드"""
        return {
            "python": {
                "max_line_length": 120,
                "max_function_length": 50,
                "max_class_length": 200,
                "max_complexity": 10,
                "naming_conventions": {
                    "functions": r"^[a-z_][a-z0-9_]*$",
                    "classes": r"^[A-Z][a-zA-Z0-9]*$",
                    "constants": r"^[A-Z_][A-Z0-9_]*$",
                },
            },
            "javascript": {
                "max_line_length": 100,
                "max_function_length": 30,
                "max_class_length": 150,
                "max_complexity": 8,
                "naming_conventions": {
                    "functions": r"^[a-z][a-zA-Z0-9]*$",
                    "classes": r"^[A-Z][a-zA-Z0-9]*$",
                    "constants": r"^[A-Z_][A-Z0-9_]*$",
                },
            },
            "java": {
                "max_line_length": 120,
                "max_function_length": 40,
                "max_class_length": 300,
                "max_complexity": 12,
                "naming_conventions": {
                    "functions": r"^[a-z][a-zA-Z0-9]*$",
                    "classes": r"^[A-Z][a-zA-Z0-9]*$",
                    "constants": r"^[A-Z_][A-Z0-9_]*$",
                },
            },
        }

    def _setup_logging(self) -> logging.Logger:
        """로깅 설정"""
        logger = logging.getLogger("coding_pr_assistant")
        logger.setLevel(logging.INFO)

        handler = logging.FileHandler(
            f"coding_pr_assistant_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        )
        formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        handler.setFormatter(formatter)
        logger.addHandler(handler)

        return logger

    def analyze_code_file(self, file_path: str, content: str) -> CodeFile:
        """코드 파일 분석"""
        lines = content.split("\n")
        language = self._detect_language(file_path)

        # 복잡도 계산 (간단한 버전)
        complexity = self._calculate_complexity(content)

        code_file = CodeFile(
            file_path=file_path,
            content=content,
            language=language,
            size=len(content),
            lines=len(lines),
            complexity=complexity,
            last_modified=datetime.now(),
        )

        self.logger.info(f"Analyzed code file: {file_path}")
        return code_file

    def _detect_language(self, file_path: str) -> str:
        """프로그래밍 언어 감지"""
        extension = Path(file_path).suffix.lower()
        language_map = {
            ".py": "python",
            ".js": "javascript",
            ".ts": "typescript",
            ".java": "java",
            ".cpp": "cpp",
            ".c": "c",
            ".cs": "csharp",
            ".php": "php",
            ".rb": "ruby",
            ".go": "go",
            ".rs": "rust",
        }
        return language_map.get(extension, "unknown")

    def _calculate_complexity(self, content: str) -> int:
        """코드 복잡도 계산 (간단한 버전)"""
        complexity = 1  # 기본 복잡도

        # 조건문 복잡도
        complexity += len(re.findall(r"\bif\b", content))
        complexity += len(re.findall(r"\belse\b", content))
        complexity += len(re.findall(r"\bswitch\b", content))
        complexity += len(re.findall(r"\bcase\b", content))

        # 반복문 복잡도
        complexity += len(re.findall(r"\bfor\b", content))
        complexity += len(re.findall(r"\bwhile\b", content))
        complexity += len(re.findall(r"\bdo\b", content))

        # 예외 처리 복잡도
        complexity += len(re.findall(r"\btry\b", content))
        complexity += len(re.findall(r"\bcatch\b", content))

        return complexity

    def scan_security_issues(self, code_file: CodeFile) -> List[SecurityIssue]:
        """보안 이슈 스캔"""
        issues = []
        lines = code_file.content.split("\n")

        for category, patterns in self.security_patterns.items():
            for pattern in patterns:
                for i, line in enumerate(lines):
                    if re.search(pattern, line, re.IGNORECASE):
                        issue = SecurityIssue(
                            issue_id=f"SEC_{hashlib.md5(f'{code_file.file_path}:{i}:{pattern}'.encode()).hexdigest()[:8]}",
                            severity=self._get_severity(category),
                            category=category,
                            description=f"Potential {category} vulnerability detected",
                            file_path=code_file.file_path,
                            line_number=i + 1,
                            suggestion=self._get_security_suggestion(category),
                            cwe_id=self._get_cwe_id(category),
                        )
                        issues.append(issue)

        self.logger.info(f"Found {len(issues)} security issues in {code_file.file_path}")
        return issues

    def scan_performance_issues(self, code_file: CodeFile) -> List[PerformanceIssue]:
        """성능 이슈 스캔"""
        issues = []
        lines = code_file.content.split("\n")

        for category, patterns in self.performance_patterns.items():
            for pattern in patterns:
                for i, line in enumerate(lines):
                    if re.search(pattern, line, re.IGNORECASE):
                        issue = PerformanceIssue(
                            issue_id=f"PERF_{hashlib.md5(f'{code_file.file_path}:{i}:{pattern}'.encode()).hexdigest()[:8]}",
                            severity=self._get_performance_severity(category),
                            category=category,
                            description=f"Potential {category} performance issue detected",
                            file_path=code_file.file_path,
                            line_number=i + 1,
                            suggestion=self._get_performance_suggestion(category),
                            impact_score=self._get_impact_score(category),
                        )
                        issues.append(issue)

        self.logger.info(f"Found {len(issues)} performance issues in {code_file.file_path}")
        return issues

    def review_code_standards(self, code_file: CodeFile) -> List[str]:
        """코드 표준 리뷰"""
        suggestions = []
        standards = self.code_standards.get(code_file.language, {})

        if not standards:
            return suggestions

        # 라인 길이 체크
        max_line_length = standards.get("max_line_length", 120)
        lines = code_file.content.split("\n")
        for i, line in enumerate(lines):
            if len(line) > max_line_length:
                suggestions.append(f"Line {i+1}: Line too long ({len(line)} > {max_line_length})")

        # 복잡도 체크
        max_complexity = standards.get("max_complexity", 10)
        if code_file.complexity > max_complexity:
            suggestions.append(
                f"Function complexity too high ({code_file.complexity} > {max_complexity})"
            )

        # 함수 길이 체크 (간단한 버전)
        functions = re.findall(r"def\s+\w+.*:", code_file.content)
        if len(functions) > 0:
            avg_function_length = code_file.lines / len(functions)
            max_function_length = standards.get("max_function_length", 50)
            if avg_function_length > max_function_length:
                suggestions.append(
                    f"Average function length too long ({avg_function_length:.1f} > {max_function_length})"
                )

        return suggestions

    def generate_code_review(self, code_file: CodeFile) -> CodeReview:
        """코드 리뷰 생성"""
        self.logger.info(f"Generating code review for {code_file.file_path}")

        # 보안 이슈 스캔
        security_issues = self.scan_security_issues(code_file)

        # 성능 이슈 스캔
        performance_issues = self.scan_performance_issues(code_file)

        # 코드 표준 리뷰
        standard_suggestions = self.review_code_standards(code_file)

        # 점수 계산
        security_score = max(0, 100 - len(security_issues) * 20)
        performance_score = max(0, 100 - len(performance_issues) * 15)
        maintainability_score = max(0, 100 - len(standard_suggestions) * 10)
        test_coverage_score = self._estimate_test_coverage(code_file)

        overall_score = (
            security_score + performance_score + maintainability_score + test_coverage_score
        ) / 4

        # 승인 여부 결정
        approved = overall_score >= 80 and len(security_issues) == 0

        review = CodeReview(
            review_id=f"REVIEW_{hashlib.md5(f'{code_file.file_path}:{datetime.now()}'.encode()).hexdigest()[:8]}",
            file_path=code_file.file_path,
            overall_score=overall_score,
            security_score=security_score,
            performance_score=performance_score,
            maintainability_score=maintainability_score,
            test_coverage_score=test_coverage_score,
            issues=security_issues + performance_issues,
            suggestions=standard_suggestions,
            approved=approved,
        )

        return review

    def _get_severity(self, category: str) -> str:
        """보안 이슈 심각도 결정"""
        severity_map = {
            "injection": "critical",
            "xss": "high",
            "csrf": "high",
            "sensitive_data": "critical",
        }
        return severity_map.get(category, "medium")

    def _get_performance_severity(self, category: str) -> str:
        """성능 이슈 심각도 결정"""
        severity_map = {
            "algorithm": "high",
            "memory": "high",
            "database": "medium",
            "io": "medium",
        }
        return severity_map.get(category, "low")

    def _get_security_suggestion(self, category: str) -> str:
        """보안 이슈 제안"""
        suggestions = {
            "injection": "Use parameterized queries or prepared statements",
            "xss": "Sanitize user input and use proper encoding",
            "csrf": "Implement CSRF tokens and validate requests",
            "sensitive_data": "Move sensitive data to environment variables or secure storage",
        }
        return suggestions.get(category, "Review and fix the security issue")

    def _get_performance_suggestion(self, category: str) -> str:
        """성능 이슈 제안"""
        suggestions = {
            "algorithm": "Consider using more efficient algorithms or data structures",
            "memory": "Optimize memory usage and avoid memory leaks",
            "database": "Add proper indexing and optimize queries",
            "io": "Use asynchronous I/O operations where possible",
        }
        return suggestions.get(category, "Review and optimize the performance issue")

    def _get_cwe_id(self, category: str) -> str:
        """CWE ID 반환"""
        cwe_map = {
            "injection": "CWE-89",
            "xss": "CWE-79",
            "csrf": "CWE-352",
            "sensitive_data": "CWE-798",
        }
        return cwe_map.get(category, "CWE-000")

    def _get_impact_score(self, category: str) -> float:
        """영향 점수 계산"""
        impact_map = {"algorithm": 0.8, "memory": 0.7, "database": 0.6, "io": 0.5}
        return impact_map.get(category, 0.3)

    def _estimate_test_coverage(self, code_file: CodeFile) -> float:
        """테스트 커버리지 추정"""
        # 간단한 테스트 커버리지 추정
        test_keywords = ["test", "spec", "assert", "expect", "mock"]
        test_count = sum(1 for keyword in test_keywords if keyword in code_file.content.lower())

        # 파일 크기에 따른 테스트 커버리지 추정
        if test_count > 0:
            return min(100, test_count * 20)
        else:
            return 0.0

    def generate_pr_summary(self, reviews: List[CodeReview]) -> Dict[str, Any]:
        """PR 요약 생성"""
        total_files = len(reviews)
        approved_files = sum(1 for review in reviews if review.approved)
        rejected_files = total_files - approved_files

        avg_overall_score = (
            sum(review.overall_score for review in reviews) / total_files if total_files > 0 else 0
        )
        avg_security_score = (
            sum(review.security_score for review in reviews) / total_files if total_files > 0 else 0
        )
        avg_performance_score = (
            sum(review.performance_score for review in reviews) / total_files
            if total_files > 0
            else 0
        )
        avg_maintainability_score = (
            sum(review.maintainability_score for review in reviews) / total_files
            if total_files > 0
            else 0
        )
        avg_test_coverage_score = (
            sum(review.test_coverage_score for review in reviews) / total_files
            if total_files > 0
            else 0
        )

        total_issues = sum(len(review.issues) for review in reviews)
        total_suggestions = sum(len(review.suggestions) for review in reviews)

        summary = {
            "pr_summary": {
                "total_files": total_files,
                "approved_files": approved_files,
                "rejected_files": rejected_files,
                "approval_rate": ((approved_files / total_files * 100) if total_files > 0 else 0),
                "avg_overall_score": avg_overall_score,
                "avg_security_score": avg_security_score,
                "avg_performance_score": avg_performance_score,
                "avg_maintainability_score": avg_maintainability_score,
                "avg_test_coverage_score": avg_test_coverage_score,
                "total_issues": total_issues,
                "total_suggestions": total_suggestions,
            },
            "recommendations": [],
            "next_steps": [],
        }

        # 권장사항 생성
        if avg_security_score < 80:
            summary["recommendations"].append(
                "보안 점수가 낮습니다. 보안 이슈를 우선적으로 해결하세요."
            )
        if avg_performance_score < 80:
            summary["recommendations"].append("성능 점수가 낮습니다. 성능 최적화가 필요합니다.")
        if avg_maintainability_score < 80:
            summary["recommendations"].append("유지보수성 점수가 낮습니다. 코드 표준을 준수하세요.")
        if avg_test_coverage_score < 70:
            summary["recommendations"].append(
                "테스트 커버리지가 낮습니다. 테스트 코드를 추가하세요."
            )

        # 다음 단계
        if summary["pr_summary"]["approval_rate"] >= 80:
            summary["next_steps"].append("PR 승인 가능")
        else:
            summary["next_steps"].append("PR 수정 필요")

        return summary


def main():
    """메인 실행 함수"""
    print("🚀 코딩 PR 보조 PoU 파일럿 시스템 시작 (Day 33)")

    assistant = CodingPRAssistant()

    # 테스트 코드 파일들
    test_files = [
        {
            "path": "example.py",
            "content": """
def calculate_sum(numbers):
    total = 0
    for num in numbers:
        total += num
    return total

def process_user_input(user_input):
    # Potential security issue
    result = eval(user_input)
    return result

def inefficient_sort(data):
    # Potential performance issue
    for i in range(len(data)):
        for j in range(len(data)):
            if data[i] > data[j]:
                data[i], data[j] = data[j], data[i]
    return data

def hardcoded_password():
    # Potential security issue
    password = "admin123"
    return password
""",
        },
        {
            "path": "example.js",
            "content": """
function calculateSum(numbers) {
    let total = 0;
    for (let num of numbers) {
        total += num;
    }
    return total;
}

function processUserInput(userInput) {
    // Potential XSS vulnerability
    document.getElementById('output').innerHTML = userInput;
    return userInput;
}

function inefficientSearch(data, target) {
    // Potential performance issue
    for (let i = 0; i < data.length; i++) {
        for (let j = 0; j < data.length; j++) {
            if (data[i] === target) {
                return i;
            }
        }
    }
    return -1;
}
""",
        },
    ]

    reviews = []

    # 각 파일에 대해 코드 리뷰 수행
    for file_info in test_files:
        print(f"\n📁 분석 중: {file_info['path']}")

        # 코드 파일 분석
        code_file = assistant.analyze_code_file(file_info["path"], file_info["content"])

        # 코드 리뷰 생성
        review = assistant.generate_code_review(code_file)
        reviews.append(review)

        print(f"   - 전체 점수: {review.overall_score:.1f}")
        print(f"   - 보안 점수: {review.security_score:.1f}")
        print(f"   - 성능 점수: {review.performance_score:.1f}")
        print(f"   - 유지보수성: {review.maintainability_score:.1f}")
        print(f"   - 테스트 커버리지: {review.test_coverage_score:.1f}")
        print(f"   - 이슈 수: {len(review.issues)}")
        print(f"   - 제안 수: {len(review.suggestions)}")
        print(f"   - 승인 여부: {'✅ 승인' if review.approved else '❌ 거부'}")

    # PR 요약 생성
    summary = assistant.generate_pr_summary(reviews)

    print(f"\n📊 PR 요약:")
    print(f"   - 총 파일 수: {summary['pr_summary']['total_files']}")
    print(f"   - 승인된 파일: {summary['pr_summary']['approved_files']}")
    print(f"   - 거부된 파일: {summary['pr_summary']['rejected_files']}")
    print(f"   - 승인률: {summary['pr_summary']['approval_rate']:.1f}%")
    print(f"   - 평균 전체 점수: {summary['pr_summary']['avg_overall_score']:.1f}")
    print(f"   - 평균 보안 점수: {summary['pr_summary']['avg_security_score']:.1f}")
    print(f"   - 평균 성능 점수: {summary['pr_summary']['avg_performance_score']:.1f}")
    print(f"   - 평균 유지보수성: {summary['pr_summary']['avg_maintainability_score']:.1f}")
    print(f"   - 평균 테스트 커버리지: {summary['pr_summary']['avg_test_coverage_score']:.1f}")
    print(f"   - 총 이슈 수: {summary['pr_summary']['total_issues']}")
    print(f"   - 총 제안 수: {summary['pr_summary']['total_suggestions']}")

    # 권장사항 출력
    if summary["recommendations"]:
        print(f"\n💡 권장사항:")
        for recommendation in summary["recommendations"]:
            print(f"   - {recommendation}")

    # 다음 단계 출력
    if summary["next_steps"]:
        print(f"\n🚀 다음 단계:")
        for step in summary["next_steps"]:
            print(f"   - {step}")

    # 결과 저장
    result_path = f"coding_pr_assistant_result_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(result_path, "w", encoding="utf-8") as f:
        json.dump(
            {
                "reviews": [
                    {
                        "review_id": review.review_id,
                        "file_path": review.file_path,
                        "overall_score": review.overall_score,
                        "security_score": review.security_score,
                        "performance_score": review.performance_score,
                        "maintainability_score": review.maintainability_score,
                        "test_coverage_score": review.test_coverage_score,
                        "issues_count": len(review.issues),
                        "suggestions_count": len(review.suggestions),
                        "approved": review.approved,
                    }
                    for review in reviews
                ],
                "summary": summary,
            },
            f,
            indent=2,
            ensure_ascii=False,
            default=str,
        )

    print(f"\n📋 결과 저장 완료: {result_path}")


if __name__ == "__main__":
    main()
