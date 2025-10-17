#!/usr/bin/env python3
"""
게이트 스모크 테스트
N/3 게이트/드리프트/비용 컷아웃 로직 시뮬
"""

import pytest
import psycopg2
from psycopg2.extras import DictCursor
import os

# PostgreSQL 설정 - 환경변수 기반으로 호스트/포트를 읽도록
PG = {
    "host": os.getenv("PGHOST", os.getenv("POSTGRES_HOST", "127.0.0.1")),
    "port": int(os.getenv("PGPORT", os.getenv("POSTGRES_PORT", "5432"))),
    "dbname": os.getenv("PGDATABASE", os.getenv("POSTGRES_DB", "duri")),
    "user": os.getenv("PGUSER", os.getenv("POSTGRES_USER", "duri")),
    "password": os.getenv("PGPASSWORD", os.getenv("POSTGRES_PASSWORD", "duri")),
}

class TestGateSmoke:
    """게이트 스모크 테스트"""
    
    def test_n3_gate_logic(self):
        """N/3 게이트 로직 시뮬"""
        with psycopg2.connect(**PG) as conn:
            with conn.cursor(cursor_factory=DictCursor) as cur:
                # 15분 내 3연속 promote 확인
                cur.execute("""
                    WITH snaps AS (
                      SELECT decision_ts, decision='promote' AS pass
                      FROM promotion_decisions
                      WHERE model_id='shadow_proxy' AND decision_ts >= NOW()-INTERVAL '15 minutes'
                      ORDER BY decision_ts DESC LIMIT 3
                    ) 
                    SELECT COUNT(*) FILTER (WHERE pass) AS passes, 
                    CASE WHEN COUNT(*) FILTER (WHERE pass)=3 THEN 'PROMOTE_STABLE' ELSE 'HOLD' END AS gate 
                    FROM snaps
                """)
                result = cur.fetchone()
                assert result is not None
                assert 'gate' in result
                print(f"N/3 게이트 결과: {result['gate']}")
    
    def test_drift_guard_logic(self):
        """드리프트 가드 로직 시뮬"""
        with psycopg2.connect(**PG) as conn:
            with conn.cursor(cursor_factory=DictCursor) as cur:
                # 1시간 vs 24시간 중앙값 대비 드리프트 확인
                cur.execute("""
                    WITH w1 AS (
                      SELECT PERCENTILE_CONT(0.95) WITHIN GROUP (ORDER BY latency_s) p95,
                             AVG(cost_usd) cost
                      FROM v_feedback_events_clean
                      WHERE ts >= NOW() - INTERVAL '1 hour' AND meta_model_id='shadow_proxy' AND track='cand'
                    ),
                    w24 AS (
                      SELECT PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY latency_s) med_p95,
                             PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY cost_usd) med_cost
                      FROM v_feedback_events_clean
                      WHERE ts >= NOW() - INTERVAL '24 hours' AND meta_model_id='shadow_proxy' AND track='cand'
                    )
                    SELECT ROUND((w1.p95/w24.med_p95)::numeric,3) AS p95_rel,
                           ROUND((w1.cost/w24.med_cost)::numeric,3) AS cost_rel,
                           CASE WHEN w1.p95/w24.med_p95 > 1.15 OR w1.cost/w24.med_cost > 1.15 
                                THEN 'ALERT' ELSE 'OK' END AS status
                    FROM w1, w24
                """)
                result = cur.fetchone()
                assert result is not None
                assert 'status' in result
                print(f"드리프트 가드 결과: {result['status']}")
    
    def test_cost_cap_logic(self):
        """비용 캡 로직 시뮬"""
        with psycopg2.connect(**PG) as conn:
            with conn.cursor(cursor_factory=DictCursor) as cur:
                # 10분 비용×6 > USD_CAP 확인
                cur.execute("""
                    WITH c AS (
                      SELECT SUM(cost_usd) cost_10m
                      FROM v_feedback_events_clean
                      WHERE ts >= NOW() - INTERVAL '10 minutes'
                    ),
                    limits AS (SELECT 5.00::numeric AS usd_per_hour_cap)
                    SELECT cost_10m, ROUND((cost_10m*6)::numeric,2) AS projected_hourly, 
                    CASE WHEN cost_10m*6 > (SELECT usd_per_hour_cap FROM limits) THEN 'CUTOUT' ELSE 'OK' END AS status
                    FROM c
                """)
                result = cur.fetchone()
                assert result is not None
                assert 'status' in result
                print(f"비용 캡 결과: {result['status']}")
    
    def test_promotion_idempotent(self):
        """promotion_decisions 아이템포턴트 삽입 테스트"""
        with psycopg2.connect(**PG) as conn:
            with conn.cursor(cursor_factory=DictCursor) as cur:
                # 동일 입력 3회 → 1행 확인
                test_model = "test_idempotent_model"
                test_decision = "test_decision"
                test_reason = "test_reason"
                
                # 기존 테스트 데이터 정리
                cur.execute("DELETE FROM promotion_decisions WHERE model_id = %s", (test_model,))
                
                # 3회 동일 삽입
                for i in range(3):
                    cur.execute("SELECT insert_promotion_once(%s, %s, %s)", (test_model, test_decision, test_reason))
                
                # 결과 확인 (1행만 있어야 함)
                cur.execute("SELECT COUNT(*) as count FROM promotion_decisions WHERE model_id = %s", (test_model,))
                result = cur.fetchone()
                assert result['count'] == 1, f"아이템포턴트 실패: {result['count']}행 발견"
                
                # 정리
                cur.execute("DELETE FROM promotion_decisions WHERE model_id = %s", (test_model,))
                print("아이템포턴트 테스트 통과")
    
    def test_view_checksum(self):
        """v_feedback_events_clean DDL 체크섬 테스트"""
        with psycopg2.connect(**PG) as conn:
            with conn.cursor(cursor_factory=DictCursor) as cur:
                # 현재 뷰 정의 가져오기
                cur.execute("SELECT definition FROM pg_views WHERE viewname='v_feedback_events_clean'")
                result = cur.fetchone()
                assert result is not None
                assert 'definition' in result
                
                # 기대하는 정의와 비교 (파일에서 읽기)
                ddl_file = "/home/duri/DuRiWorkspace/v_feedback_events_clean_ddl.sql"
                if os.path.exists(ddl_file):
                    with open(ddl_file, 'r') as f:
                        expected_ddl = f.read().strip()
                    current_ddl = result['definition'].strip()
                    assert current_ddl == expected_ddl, "DDL 체크섬 불일치"
                    print("DDL 체크섬 테스트 통과")
                else:
                    print("⚠️ DDL 파일 없음, 체크섬 테스트 스킵")

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
