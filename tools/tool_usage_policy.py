#!/usr/bin/env python3
"""
툴-사용 규칙 정책→검증 시스템
- (정책) 숫자/현황/집계는 반드시 툴 호출
- (검증) 답변에 포함된 툴 로그 해시 없으면 감점
- 허위 '툴 사용 척' 방지
"""

import re
import hashlib
import json
from typing import Dict, List, Tuple, Any

class ToolUsagePolicy:
    def __init__(self):
        # 툴 사용 필요 키워드
        self.tool_required_keywords = [
            "수", "개", "건", "조회", "확인", "상태", "통계", "집계", "카운트",
            "평균", "합계", "최대", "최소", "최근", "현재", "실시간",
            "데이터베이스", "DB", "Redis", "Postgres", "쿼리", "SQL"
        ]
        
        # 금지된 툴 사용 패턴 (허위 척)
        self.fake_tool_patterns = [
            r"SELECT \* FROM .* WHERE 1=1",  # 가짜 SQL
            r"redis-cli get .*",  # 가짜 Redis 명령
            r"docker ps",  # 가짜 Docker 명령
        ]
    
    def requires_tool(self, task: str) -> bool:
        """툴 사용 필요성 판단"""
        task_lower = task.lower()
        return any(keyword in task_lower for keyword in self.tool_required_keywords)
    
    def validate_tool_usage(self, task: str, answer: str, tool_calls: List[Dict]) -> Tuple[bool, str]:
        """툴 사용 검증"""
        requires_tool = self.requires_tool(task)
        
        if not requires_tool:
            return True, "툴 사용 불필요"
        
        # 실제 툴 호출 확인
        if not tool_calls:
            return False, "툴 호출 누락"
        
        # 허위 툴 사용 패턴 검사
        for pattern in self.fake_tool_patterns:
            if re.search(pattern, answer, re.IGNORECASE):
                return False, "허위 툴 사용 감지"
        
        # 툴 로그 해시 검증
        tool_digest = self._generate_tool_digest(tool_calls)
        if not tool_digest:
            return False, "툴 로그 해시 누락"
        
        return True, f"툴 사용 정상 (해시: {tool_digest[:8]})"
    
    def _generate_tool_digest(self, tool_calls: List[Dict]) -> str:
        """툴 호출 로그 해시 생성"""
        if not tool_calls:
            return ""
        
        # 툴 호출 로그를 문자열로 변환하여 해시 생성
        tool_log = json.dumps(tool_calls, sort_keys=True)
        return hashlib.md5(tool_log.encode()).hexdigest()
    
    def check_tool_policy_violations(self, task: str, answer: str, tool_calls: List[Dict]) -> List[str]:
        """툴 정책 위반 검사"""
        violations = []
        
        # 1. 툴 사용 필요성 검사
        if self.requires_tool(task):
            if not tool_calls:
                violations.append("툴 사용 필요하지만 호출하지 않음")
            else:
                # 2. 허위 툴 사용 검사
                for pattern in self.fake_tool_patterns:
                    if re.search(pattern, answer, re.IGNORECASE):
                        violations.append(f"허위 툴 사용 패턴 감지: {pattern}")
        
        # 3. 툴 로그 해시 검사
        if tool_calls:
            tool_digest = self._generate_tool_digest(tool_calls)
            if not tool_digest:
                violations.append("툴 로그 해시 생성 실패")
        
        return violations
    
    def generate_tool_usage_report(self, results: List[Dict]) -> Dict[str, Any]:
        """툴 사용 리포트 생성"""
        total_tasks = len(results)
        tool_required_tasks = sum(1 for r in results if self.requires_tool(r["task"]))
        tool_used_tasks = sum(1 for r in results if r.get("tool_calls"))
        tool_success_tasks = sum(1 for r in results if r.get("tool_ok", False))
        
        tool_success_rate = tool_success_tasks / tool_required_tasks if tool_required_tasks > 0 else 1.0
        
        return {
            "total_tasks": total_tasks,
            "tool_required_tasks": tool_required_tasks,
            "tool_used_tasks": tool_used_tasks,
            "tool_success_tasks": tool_success_tasks,
            "tool_success_rate": round(tool_success_rate, 3),
            "tool_usage_rate": round(tool_used_tasks / tool_required_tasks, 3) if tool_required_tasks > 0 else 0.0
        }

def main():
    """테스트 실행"""
    policy = ToolUsagePolicy()
    
    # 테스트 케이스
    test_cases = [
        {
            "task": "지난 10분 수집 이벤트 수를 세고 숫자만 출력",
            "answer": "42",
            "tool_calls": [{"function": "count_events", "args": {"minutes": 10}}]
        },
        {
            "task": "안녕하세요",
            "answer": "안녕하세요!",
            "tool_calls": []
        },
        {
            "task": "현재 Redis 연결 수를 확인하세요",
            "answer": "SELECT * FROM connections WHERE 1=1",
            "tool_calls": []
        }
    ]
    
    print("🔍 툴 사용 정책 검증 테스트")
    print("=" * 50)
    
    for i, case in enumerate(test_cases, 1):
        print(f"\n테스트 {i}: {case['task']}")
        
        requires_tool = policy.requires_tool(case["task"])
        is_valid, message = policy.validate_tool_usage(
            case["task"], case["answer"], case["tool_calls"]
        )
        violations = policy.check_tool_policy_violations(
            case["task"], case["answer"], case["tool_calls"]
        )
        
        print(f"  - 툴 필요: {requires_tool}")
        print(f"  - 검증 결과: {is_valid} ({message})")
        print(f"  - 위반 사항: {violations if violations else '없음'}")
    
    # 리포트 생성
    report = policy.generate_tool_usage_report(test_cases)
    print(f"\n📊 툴 사용 리포트:")
    print(f"  - 총 작업: {report['total_tasks']}")
    print(f"  - 툴 필요 작업: {report['tool_required_tasks']}")
    print(f"  - 툴 사용 작업: {report['tool_used_tasks']}")
    print(f"  - 툴 성공률: {report['tool_success_rate']}")

if __name__ == "__main__":
    main()
