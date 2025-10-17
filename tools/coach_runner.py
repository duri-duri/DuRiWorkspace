#!/usr/bin/env python3
"""
Coach Runner: 두리 호출 및 자동채점
- 각 item에 대해 두리 호출(필요시 툴 호출)
- 채점기(grader.type)에 따라 스코어 산출
- 결과 JSON에 {score, latency_ms, tool_used, policy_violations} 저장
"""

import json
import time
import hashlib
import argparse
import requests
from typing import Dict, Any, List
import psycopg2
from psycopg2.extras import DictCursor

# 설정
DURI_BRAIN_URL = "http://duri_brain:8081"
PG_CONFIG = {
    "host": "duri-postgres",
    "port": 5432,
    "dbname": "duri",
    "user": "duri",
    "password": "duri"
}

class CoachRunner:
    def __init__(self, exp_id: str, max_tokens: int = 50000, max_cost: float = 5.0):
        self.exp_id = exp_id
        self.max_tokens = max_tokens
        self.max_cost = max_cost
        self.total_tokens = 0
        self.total_cost = 0.0
        
    def call_duri(self, task: str) -> Dict[str, Any]:
        """두리 호출 (툴 호출 포함)"""
        start_time = time.time()
        
        try:
            # 두리 호출
            response = requests.post(
                f"{DURI_BRAIN_URL}/emotion",
                json={"user_id": f"coach_{self.exp_id}", "text": task},
                headers={"X-DuRi-Shadow": "1"},
                timeout=30
            )
            response.raise_for_status()
            
            result = response.json()
            latency_ms = int((time.time() - start_time) * 1000)
            
            # 툴 호출 검증
            tool_used = self._check_tool_usage(task, result)
            tool_digest = self._generate_tool_digest(result)
            
            return {
                "text": result.get("response", ""),
                "tool_calls": result.get("tool_calls", []),
                "tool_digest": tool_digest,
                "latency_ms": latency_ms,
                "tool_used": tool_used,
                "success": True
            }
            
        except Exception as e:
            return {
                "text": f"Error: {str(e)}",
                "tool_calls": [],
                "tool_digest": "",
                "latency_ms": int((time.time() - start_time) * 1000),
                "tool_used": False,
                "success": False
            }
    
    def _check_tool_usage(self, task: str, result: Dict[str, Any]) -> bool:
        """툴 사용 필요성 검증"""
        # 숫자/현황/집계 키워드가 있으면 툴 호출 필요
        tool_keywords = ["수", "개", "건", "조회", "확인", "상태", "통계", "집계", "카운트"]
        requires_tool = any(keyword in task for keyword in tool_keywords)
        
        # 실제 툴 호출 여부 확인
        tool_calls = result.get("tool_calls", [])
        actual_tool_used = len(tool_calls) > 0
        
        return actual_tool_used if requires_tool else True
    
    def _generate_tool_digest(self, result: Dict[str, Any]) -> str:
        """툴 호출 로그 해시 생성"""
        tool_calls = result.get("tool_calls", [])
        if not tool_calls:
            return ""
        
        # 툴 호출 로그를 문자열로 변환하여 해시 생성
        tool_log = json.dumps(tool_calls, sort_keys=True)
        return hashlib.md5(tool_log.encode()).hexdigest()[:8]
    
    def grade_answer(self, task: str, answer: str, grader: Dict[str, Any]) -> float:
        """채점기 표준화: rule/regex/sql 3가지 타입"""
        grader_type = grader.get("type", "rule")
        spec = grader.get("spec", {})
        
        try:
            if grader_type == "rule":
                return self._grade_rule(answer, spec)
            elif grader_type == "regex":
                return self._grade_regex(answer, spec)
            elif grader_type == "sql":
                return self._grade_sql(task, answer, spec)
            else:
                return 0.0
        except Exception as e:
            print(f"⚠️ 채점 오류: {e}")
            return 0.0
    
    def _grade_rule(self, answer: str, spec: Dict[str, Any]) -> float:
        """정확 문자열/집합 매칭"""
        if "match_set" in spec:
            # 집합 매칭 (에러 코드 등)
            expected = set(spec.get("set", []))
            # 답변에서 코드 추출 (E123 형태)
            import re
            found = set(re.findall(r'E\d+', answer))
            if expected == found:
                return 1.0
            elif found.issubset(expected):
                return 0.5  # 부분 점수
            else:
                return 0.0
        
        # 문자열 포함 검사
        must_include = spec.get("must_include", [])
        if all(keyword in answer for keyword in must_include):
            return 1.0
        else:
            return 0.0
    
    def _grade_regex(self, answer: str, spec: str) -> float:
        """정규식 매칭"""
        import re
        if re.search(spec, answer, re.IGNORECASE):
            return 1.0
        else:
            return 0.0
    
    def _grade_sql(self, task: str, answer: str, spec: str) -> float:
        """SQL 쿼리 결과와 비교"""
        try:
            # 답변에서 숫자 추출
            import re
            numbers = re.findall(r'\d+', answer)
            if not numbers:
                return 0.0
            
            # SQL 쿼리 실행
            with psycopg2.connect(**PG_CONFIG) as conn:
                with conn.cursor() as cur:
                    cur.execute(spec)
                    result = cur.fetchone()
                    if result and str(result[0]) in numbers:
                        return 1.0
                    else:
                        return 0.0
        except Exception as e:
            print(f"⚠️ SQL 채점 오류: {e}")
            return 0.0
    
    def run_batch(self, items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """배치 실행"""
        results = []
        
        for item in items:
            # 비용/토큰 체크
            if self.total_tokens > self.max_tokens or self.total_cost > self.max_cost:
                print(f"⚠️ 한도 초과: tokens={self.total_tokens}, cost={self.total_cost}")
                break
            
            # 두리 호출
            answer = self.call_duri(item["task"])
            
            # 채점
            score = self.grade_answer(
                item["task"], 
                answer["text"], 
                json.loads(item["grader"])
            )
            
            # 정책 위반 검사
            policy_violations = self._check_policy_violations(answer["text"])
            
            result = {
                "exp_id": self.exp_id,
                "item_id": item["id"],
                "prompt": {"task": item["task"]},
                "answer": answer,
                "score": score,
                "latency_ms": answer["latency_ms"],
                "policy_violations": policy_violations,
                "tool_required": self._requires_tool(item["task"]),
                "tool_used": answer["tool_used"],
                "tool_ok": answer["tool_used"] or not self._requires_tool(item["task"]),
                "ts": time.time()
            }
            
            results.append(result)
            
            # 토큰/비용 추정 (간단한 추정)
            self.total_tokens += len(item["task"]) + len(answer["text"])
            self.total_cost += 0.002  # 대략적 추정
        
        return results
    
    def _check_policy_violations(self, text: str) -> int:
        """정책 위반 검사"""
        violations = 0
        
        # 금칙어 검사
        forbidden_words = ["해킹", "크래킹", "바이러스", "악성코드"]
        if any(word in text for word in forbidden_words):
            violations += 1
        
        # PII 노출 검사
        import re
        if re.search(r'\d{3}-\d{4}-\d{4}', text):  # 전화번호
            violations += 1
        if re.search(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', text):  # 이메일
            violations += 1
        
        return violations
    
    def _requires_tool(self, task: str) -> bool:
        """툴 사용 필요성 판단"""
        tool_keywords = ["수", "개", "건", "조회", "확인", "상태", "통계", "집계", "카운트"]
        return any(keyword in task for keyword in tool_keywords)

def main():
    parser = argparse.ArgumentParser(description="Coach Runner")
    parser.add_argument("--exp", required=True, help="실험 ID")
    parser.add_argument("--input", required=True, help="입력 TSV 파일")
    parser.add_argument("--out", required=True, help="출력 JSON 파일")
    parser.add_argument("--max-tokens", type=int, default=50000, help="최대 토큰 수")
    parser.add_argument("--max-cost", type=float, default=5.0, help="최대 비용")
    
    args = parser.parse_args()
    
    # 입력 파일 읽기
    items = []
    with open(args.input, 'r') as f:
        for line in f:
            parts = line.strip().split('\t')
            if len(parts) >= 4:
                items.append({
                    "id": int(parts[0]),
                    "task": parts[1],
                    "gold_answer": parts[2],
                    "grader": parts[3]
                })
    
    # Coach 실행
    runner = CoachRunner(args.exp, args.max_tokens, args.max_cost)
    results = runner.run_batch(items)
    
    # 결과 저장
    with open(args.out, 'w') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Coach 배치 완료: {len(results)}개 결과 저장")

if __name__ == "__main__":
    main()
