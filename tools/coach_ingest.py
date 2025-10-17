#!/usr/bin/env python3
"""
Coach Ingest: 결과 기록 및 요약
- Coach 결과를 Postgres에 저장
- Redis에 배치 요약 저장
- 일일 지표 업데이트
"""

import json
import argparse
import psycopg2
from psycopg2.extras import DictCursor
import redis
from datetime import datetime, timezone

# 설정
PG_CONFIG = {
    "host": "duri-postgres",
    "port": 5432,
    "dbname": "duri",
    "user": "duri",
    "password": "duri"
}

REDIS_CONFIG = {
    "host": "duri-redis",
    "port": 6379,
    "decode_responses": True
}

class CoachIngest:
    def __init__(self):
        self.pg_conn = psycopg2.connect(**PG_CONFIG)
        self.redis_conn = redis.Redis(**REDIS_CONFIG)
    
    def ingest_results(self, exp_id: str, results: list):
        """Coach 결과를 DB에 저장"""
        with self.pg_conn.cursor() as cur:
            # Coach 실행 기록
            total_tokens = sum(len(r["prompt"]["task"]) + len(r["answer"]["text"]) for r in results)
            avg_score = sum(r["score"] for r in results) / len(results) if results else 0
            total_cost = len(results) * 0.002  # 대략적 추정
            
            cur.execute("""
                INSERT INTO coach_runs (exp_id, sample_count, token_input, token_output, cost, notes)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (exp_id, len(results), total_tokens, 0, total_cost, f"avg_score={avg_score:.3f}"))
            
            # 개별 결과 저장
            for result in results:
                cur.execute("""
                    INSERT INTO coach_results (
                        exp_id, item_id, prompt, answer, score, latency_ms,
                        policy_violations, tool_required, tool_used, tool_ok
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    result["exp_id"],
                    result["item_id"],
                    json.dumps(result["prompt"]),
                    json.dumps(result["answer"]),
                    result["score"],
                    result["latency_ms"],
                    result["policy_violations"],
                    result["tool_required"],
                    result["tool_used"],
                    result["tool_ok"]
                ))
            
            self.pg_conn.commit()
    
    def update_redis_summary(self, exp_id: str, results: list):
        """Redis에 배치 요약 저장"""
        if not results:
            return
        
        # 통계 계산
        scores = [r["score"] for r in results]
        latencies = [r["latency_ms"] for r in results]
        
        avg_score = sum(scores) / len(scores)
        p95_latency = sorted(latencies)[int(len(latencies) * 0.95)] if latencies else 0
        total_cost = len(results) * 0.002
        
        # 툴 사용 통계
        tool_required_count = sum(1 for r in results if r["tool_required"])
        tool_used_count = sum(1 for r in results if r["tool_used"])
        tool_success_rate = tool_used_count / tool_required_count if tool_required_count > 0 else 1.0
        
        # 정책 위반 통계
        total_violations = sum(r["policy_violations"] for r in results)
        
        # Redis에 저장
        batch_key = f"coach:batch:{exp_id}"
        batch_data = {
            "exp_id": exp_id,
            "n": len(results),
            "avg_score": round(avg_score, 3),
            "p95_latency": p95_latency,
            "cost": round(total_cost, 5),
            "tool_success_rate": round(tool_success_rate, 3),
            "violations": total_violations,
            "ts": datetime.now(timezone.utc).isoformat()
        }
        
        self.redis_conn.setex(batch_key, 86400, json.dumps(batch_data))
        
        # 일일 지표 업데이트
        today = datetime.now().strftime("%Y-%m-%d")
        self._update_daily_metrics(today, avg_score, p95_latency, total_cost, total_violations)
    
    def _update_daily_metrics(self, day: str, accuracy: float, latency_p95: int, cost: float, violations: int):
        """일일 지표 업데이트 (Redis)"""
        # 기존 값과 평균 계산 (간단한 이동평균)
        existing_acc = self.redis_conn.get(f"gate:accuracy:{day}")
        existing_p95 = self.redis_conn.get(f"gate:latency_p95:{day}")
        existing_cost = self.redis_conn.get(f"gate:cost_per_1k:{day}")
        existing_vio = self.redis_conn.get(f"gate:violations:{day}")
        
        # 가중 평균 (새 값 30%, 기존 값 70%)
        new_acc = (accuracy * 0.3 + float(existing_acc or 0) * 0.7) if existing_acc else accuracy
        new_p95 = int(latency_p95 * 0.3 + int(existing_p95 or 0) * 0.7) if existing_p95 else latency_p95
        new_cost = (cost * 0.3 + float(existing_cost or 0) * 0.7) if existing_cost else cost
        new_vio = violations + int(existing_vio or 0)
        
        # Redis에 저장
        self.redis_conn.setex(f"gate:accuracy:{day}", 86400, new_acc)
        self.redis_conn.setex(f"gate:latency_p95:{day}", 86400, new_p95)
        self.redis_conn.setex(f"gate:cost_per_1k:{day}", 86400, new_cost)
        self.redis_conn.setex(f"gate:violations:{day}", 86400, new_vio)
    
    def close(self):
        """연결 종료"""
        self.pg_conn.close()
        self.redis_conn.close()

def main():
    parser = argparse.ArgumentParser(description="Coach Ingest")
    parser.add_argument("--exp", required=True, help="실험 ID")
    parser.add_argument("--input", required=True, help="입력 JSON 파일")
    
    args = parser.parse_args()
    
    # 결과 파일 읽기
    with open(args.input, 'r') as f:
        results = json.load(f)
    
    # Ingest 실행
    ingest = CoachIngest()
    try:
        ingest.ingest_results(args.exp, results)
        ingest.update_redis_summary(args.exp, results)
        print(f"✅ Coach 결과 기록 완료: {len(results)}개 결과")
    finally:
        ingest.close()

if __name__ == "__main__":
    main()
