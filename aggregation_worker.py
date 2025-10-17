#!/usr/bin/env python3
"""
DB 기반 집계 워커
30초마다 피드백 데이터를 DB에서 읽어서 aggregate_snapshots와 guard_results를 갱신
"""
import os, time, sys, traceback, yaml, json
from datetime import datetime, timezone, timedelta
import psycopg2
from psycopg2.extras import DictCursor

# PostgreSQL 연결 설정
PG = dict(
    host=os.getenv("POSTGRES_HOST", "duri-postgres"),
    port=int(os.getenv("POSTGRES_PORT", "5432")),
    dbname=os.getenv("POSTGRES_DB", "duri"),
    user=os.getenv("POSTGRES_USER", "duri"),
    password=os.getenv("POSTGRES_PASSWORD", "duri"),
)

# 설정
INTERVAL = int(os.getenv("AGG_INTERVAL_SEC", "30"))
WINDOW_H = int(os.getenv("AGG_WINDOW_HOURS", "24"))
MIN_REQUIRED = int(os.getenv("MIN_REQUIRED_SAMPLES", "50"))

# SSOT 승격 정책 import
import sys
sys.path.append('/app')
# from duri_common.policy.promotion import PromoLimits, PromoWeights, validate_promotion_config

# 승격 정책 검증 (임시 비활성화)
# validation = validate_promotion_config()
# if not validation["valid"]:
#     print(f"❌ 승격 정책 검증 실패: {validation['issues']}", flush=True)
#     sys.exit(1)

# if validation["warnings"]:
#     print(f"⚠️ 승격 정책 경고: {validation['warnings']}", flush=True)

# print(f"✅ 승격 정책 검증 완료: {validation['limits']}", flush=True)
print("✅ aggregation_worker 시작", flush=True)

# 가드 정책 로드
def load_guard_policy():
    """가드 정책을 YAML 파일에서 로드 (fallback: 환경변수)"""
    policy_file = "/app/configs/promotion_guard.yaml"
    try:
        if os.path.exists(policy_file):
            with open(policy_file, 'r', encoding='utf-8') as f:
                policy = yaml.safe_load(f)
                print(f"📋 가드 정책 로드: {policy_file}", flush=True)
                # 부팅 요약 로그
                print(f"[agg] view={os.getenv('AGG_SRC_VIEW')} "
                      f"window={policy.get('window_hours','?')}h "
                      f"min={policy.get('min_required','?')} "
                      f"effective_from={policy.get('effective_from','-')}", flush=True)
                return policy
    except Exception as e:
        print(f"⚠️ 가드 정책 로드 실패: {e}", flush=True)
    
    # Fallback: 환경변수
    return {
        "min_required": MIN_REQUIRED,
        "window_hours": WINDOW_H,
        "success_pp_min": float(os.getenv("GUARD_SUCCESS_PP_MIN", "0.0")),
        "halluc_pp_max": float(os.getenv("GUARD_HALLUC_PP_MAX", "1.0")),
        "p95_rel_max": float(os.getenv("GUARD_P95_REL_MAX", "1.10")),
        "cost_rel_max": float(os.getenv("GUARD_COST_REL_MAX", "1.10")),
        "freeze_hours": int(os.getenv("GUARD_FREEZE_HOURS", "12")),
        "alpha": float(os.getenv("GUARD_ALPHA", "0.05"))
    }

# DB 집계 쿼리 (클린 뷰 + 윈도우)
def get_agg_sql(policy):
    """정책에 따른 집계 쿼리 생성"""
    window_hours = policy.get("window_hours", 24)
    src_view = os.getenv("AGG_SRC_VIEW", "v_feedback_events_clean")
    
    return f"""
WITH w AS (
  SELECT * FROM {src_view}
  WHERE ts >= now() - interval '{window_hours} hours'
)
SELECT
  COUNT(*) FILTER (WHERE track='prod') AS prod_count,
  COUNT(*) FILTER (WHERE track='cand') AS cand_count,
  AVG(CASE WHEN ok THEN 1.0 ELSE 0.0 END) FILTER (WHERE track='prod') AS prod_success_rate,
  AVG(CASE WHEN ok THEN 1.0 ELSE 0.0 END) FILTER (WHERE track='cand') AS cand_success_rate,
  AVG(CASE WHEN hallucination THEN 1.0 ELSE 0.0 END) FILTER (WHERE track='prod') AS prod_hallu_rate,
  AVG(CASE WHEN hallucination THEN 1.0 ELSE 0.0 END) FILTER (WHERE track='cand') AS cand_hallu_rate,
  PERCENTILE_CONT(0.95) WITHIN GROUP (ORDER BY latency_s) FILTER (WHERE track='prod') AS prod_p95_latency,
  PERCENTILE_CONT(0.95) WITHIN GROUP (ORDER BY latency_s) FILTER (WHERE track='cand') AS cand_p95_latency,
  AVG(cost_usd) FILTER (WHERE track='prod') AS prod_avg_cost,
  AVG(cost_usd) FILTER (WHERE track='cand') AS cand_avg_cost
FROM w;
"""

def evaluate_guard(snapshot, policy):
    """가드 정책에 따른 승격 가능성 평가"""
    prod_n = int(snapshot.get("prod_count", 0))
    cand_n = int(snapshot.get("cand_count", 0))
    
    # 1. 샘플 수 검증
    min_required = policy.get("min_required", 50)
    if prod_n < min_required or cand_n < min_required:
        return False, f"insufficient_samples: prod={prod_n}, cand={cand_n}, min={min_required}"
    
    # 2. 성능 메트릭 계산
    def nz(v): return float(v) if v is not None else 0.0
    
    prod_success = nz(snapshot.get("prod_success_rate"))
    cand_success = nz(snapshot.get("cand_success_rate"))
    prod_hallu = nz(snapshot.get("prod_hallu_rate"))
    cand_hallu = nz(snapshot.get("cand_hallu_rate"))
    prod_p95 = nz(snapshot.get("prod_p95_latency"))
    cand_p95 = nz(snapshot.get("cand_p95_latency"))
    prod_cost = nz(snapshot.get("prod_avg_cost"))
    cand_cost = nz(snapshot.get("cand_avg_cost"))
    
    # 3. 차이 계산 (퍼센트포인트)
    success_pp = (cand_success - prod_success) * 100.0
    halluc_pp = (cand_hallu - prod_hallu) * 100.0
    
    # 4. 상대적 비율 계산
    p95_rel = cand_p95 / prod_p95 if prod_p95 > 0 else 1.0
    cost_rel = cand_cost / prod_cost if prod_cost > 0 else 1.0
    
    # 5. 정책 기준 검증
    reasons = []
    
    success_pp_min = policy.get("success_pp_min", 0.0)
    if success_pp < success_pp_min:
        reasons.append(f"success_pp<{success_pp_min:.2f} (got {success_pp:.2f})")
    
    halluc_pp_max = policy.get("halluc_pp_max", 1.0)
    if halluc_pp > halluc_pp_max:
        reasons.append(f"halluc_pp>{halluc_pp_max:.2f} (got {halluc_pp:.2f})")
    
    p95_rel_max = policy.get("p95_rel_max", 1.10)
    if p95_rel > p95_rel_max:
        reasons.append(f"p95_rel>{p95_rel_max:.2f} (got {p95_rel:.3f})")
    
    cost_rel_max = policy.get("cost_rel_max", 1.10)
    if cost_rel > cost_rel_max:
        reasons.append(f"cost_rel>{cost_rel_max:.2f} (got {cost_rel:.3f})")
    
    # 6. 결과 반환
    if reasons:
        return False, "; ".join(reasons)
    else:
        return True, f"pass: success_pp={success_pp:.2f}, halluc_pp={halluc_pp:.2f}, p95_rel={p95_rel:.3f}, cost_rel={cost_rel:.3f}"

def run_once():
    """한 번의 집계 실행"""
    try:
        # 정책 로드
        policy = load_guard_policy()
        
        with psycopg2.connect(**PG) as conn:
            with conn.cursor(cursor_factory=DictCursor) as cur:
                # 정책 기반 집계 쿼리 실행
                agg_sql = get_agg_sql(policy)
                cur.execute(agg_sql)
                row = cur.fetchone()
                
                # None 방어
                def nz(v): 
                    return float(v) if v is not None else 0.0
                
                prod_n = int(row["prod_count"] or 0)
                cand_n = int(row["cand_count"] or 0)

                # 스냅샷 저장
                cur.execute("""
                  INSERT INTO aggregate_snapshots
                  (prod_count, cand_count, prod_success_rate, cand_success_rate,
                   prod_hallu_rate, cand_hallu_rate, prod_p95_latency, cand_p95_latency,
                   prod_avg_cost, cand_avg_cost)
                  VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                  RETURNING id
                """, (
                    prod_n, cand_n,
                    nz(row["prod_success_rate"]), nz(row["cand_success_rate"]),
                    nz(row["prod_hallu_rate"]),   nz(row["cand_hallu_rate"]),
                    nz(row["prod_p95_latency"]),  nz(row["cand_p95_latency"]),
                    nz(row["prod_avg_cost"]),     nz(row["cand_avg_cost"]),
                ))
                snapshot_id = cur.fetchone()[0]

                # 가드 판정 (정책 기반)
                passed, reason = evaluate_guard(row, policy)

                # 가드 결과 저장
                cur.execute("""
                  INSERT INTO guard_results
                  (prod_samples, cand_samples, passed, reason, snapshot_id)
                  VALUES (%s, %s, %s, %s, %s)
                """, (prod_n, cand_n, passed, reason, snapshot_id))

                print(f"✅ snapshot#{snapshot_id} prod={prod_n} cand={cand_n} guard={passed}:{reason}", flush=True)
                # 스냅샷 요약 로그 (운영자 친화)
                success_pp = (nz(row["cand_success_rate"]) - nz(row["prod_success_rate"])) * 100
                halluc_pp = (nz(row["cand_hallu_rate"]) - nz(row["prod_hallu_rate"])) * 100
                p95_rel = nz(row["cand_p95_latency"]) / nz(row["prod_p95_latency"]) if nz(row["prod_p95_latency"]) > 0 else 1.0
                cost_rel = nz(row["cand_avg_cost"]) / nz(row["prod_avg_cost"]) if nz(row["prod_avg_cost"]) > 0 else 1.0
                print(f"[agg:snap] prod={prod_n} cand={cand_n} "
                      f"succ_pp={success_pp:.2f} hallu_pp={halluc_pp:.2f} "
                      f"p95_rel={p95_rel:.3f} cost_rel={cost_rel:.3f} -> guard={passed}", flush=True)
                
                # === 후보군 메트릭 집계 (cand 모델별) ===
                # 현재 프로덕션 모델 ID (환경변수 또는 기본값)
                PROMO_BASELINE_MODEL_ID = os.getenv("PROMO_BASELINE_MODEL_ID", "prod_default")
                
                sql = f"""
WITH w AS (
  SELECT * FROM v_feedback_events_clean
  WHERE ts >= NOW() - INTERVAL '1 hour' AND track IN ('prod','cand')
),
prod AS (
  SELECT
    COUNT(*) n,
    AVG(CASE WHEN NOT hallucination THEN 1.0 ELSE 0.0 END) AS success_rate,
    AVG(CASE WHEN hallucination THEN 1.0 ELSE 0.0 END)     AS hallu_rate,
    PERCENTILE_CONT(0.95) WITHIN GROUP (ORDER BY latency_s) AS p95,
    AVG(cost_usd) AS cost
  FROM w WHERE track='prod' AND meta_model_id = '{PROMO_BASELINE_MODEL_ID}'
),
cand AS (
  SELECT
    meta_model_id AS model_id,
    COUNT(*) n,
    AVG(CASE WHEN NOT hallucination THEN 1.0 ELSE 0.0 END) AS success_rate,
    AVG(CASE WHEN hallucination THEN 1.0 ELSE 0.0 END)     AS hallu_rate,
    PERCENTILE_CONT(0.95) WITHIN GROUP (ORDER BY latency_s) AS p95,
    AVG(cost_usd) AS cost
  FROM w
  WHERE track='cand' AND meta_model_id IS NOT NULL
  GROUP BY meta_model_id
)
SELECT
  c.model_id,
  COALESCE(ROUND((c.success_rate - p.success_rate)::numeric * 100, 2), 0.0) AS success_pp,
  COALESCE(ROUND((c.hallu_rate   - p.hallu_rate)::numeric   * 100, 2), 0.0) AS halluc_pp,
  COALESCE(ROUND((c.p95 / NULLIF(p.p95,0))::numeric, 3), 1.000)               AS p95_rel,
  COALESCE(ROUND((c.cost/ NULLIF(p.cost,0))::numeric, 3), 1.000)              AS cost_rel,
  c.n AS cand_samples, p.n AS prod_samples
FROM cand c CROSS JOIN prod p;
"""
                
                cur.execute(sql)
                rows = [dict(zip([d[0] for d in cur.description], r)) for r in cur.fetchall()]
                
                # 점수 가중치 (operational.env)
                W_SUCCESS = float(os.getenv("PROMO_W_SUCCESS", "0.40"))
                W_HALLU   = float(os.getenv("PROMO_W_HALLU",  "0.30"))
                W_P95     = float(os.getenv("PROMO_W_P95",    "0.20"))
                W_COST    = float(os.getenv("PROMO_W_COST",   "0.10"))
                
                def _safe_float(v, default=0.0):
                    try:
                        return float(v) if v is not None else default
                    except (TypeError, ValueError):
                        return default
                
                def _score(r):
                    succ  = _safe_float(r.get("success_pp"), 0.0)
                    hallu = -_safe_float(r.get("halluc_pp"), 0.0)          # 낮을수록 가점
                    p95b  = 1.0 - _safe_float(r.get("p95_rel"), 1.0)       # 1보다 작으면 가점
                    costb = 1.0 - _safe_float(r.get("cost_rel"), 1.0)
                    return W_SUCCESS*succ + W_HALLU*hallu + W_P95*p95b + W_COST*costb
                
                for r in rows:
                    r["promotion_score"] = round(_score(r), 6)
                
                # 안정 정렬 + 타이브레이커
                rows.sort(key=lambda x: (
                    x["promotion_score"],
                    -float(x.get("halluc_pp", 0) or 0),
                    -(1.0 - float(x.get("p95_rel", 1) or 1)),
                    -(1.0 - float(x.get("cost_rel",1) or 1)),
                    float(x.get("cand_samples", 0) or 0)
                ), reverse=True)
                
                top5 = rows[:5]
                
                # 기록용 윈도우(워커가 쓰는 기준값 재사용)
                window_to = datetime.now(timezone.utc)
                window_from = window_to - timedelta(hours=1)
                
                policy_json = json.dumps({
                    "weights": {"success": W_SUCCESS, "hallu": W_HALLU, "p95": W_P95, "cost": W_COST},
                    "effective_from": policy.get("effective_from", ""),
                    "window_hours": 1
                })
                
                # promotion_candidates에 벌크 인서트 (멱등성 보장)
                for r in top5:
                    cur.execute("""
                        INSERT INTO promotion_candidates
                        (model_id, window_from, window_to, prod_samples, cand_samples,
                         success_pp, halluc_pp, p95_rel, cost_rel, promotion_score, selection_policy)
                        VALUES (%(model_id)s, %(window_from)s, %(window_to)s, %(prod_samples)s, %(cand_samples)s,
                                %(success_pp)s, %(halluc_pp)s, %(p95_rel)s, %(cost_rel)s, %(promotion_score)s, %(policy_json)s)
                        ON CONFLICT (model_id, window_from, window_to) DO UPDATE SET
                          prod_samples = EXCLUDED.prod_samples,
                          cand_samples = EXCLUDED.cand_samples,
                          success_pp   = EXCLUDED.success_pp,
                          halluc_pp    = EXCLUDED.halluc_pp,
                          p95_rel      = EXCLUDED.p95_rel,
                          cost_rel     = EXCLUDED.cost_rel,
                          promotion_score = EXCLUDED.promotion_score,
                          selection_policy = EXCLUDED.selection_policy
                    """, {**r, "window_from": window_from, "window_to": window_to, "policy_json": policy_json})
                
                print(f"[agg:top5] " + 
                      " ".join([f"{i+1}:{r['model_id']}@{r['promotion_score']:.3f}" for i, r in enumerate(top5)]), 
                      flush=True)
                # 점수 분해표시 (가독성 향상)
                print("[agg:top5:detail] " +
                      " ".join([f"{r['model_id']}(succ={r['success_pp']},hallu={r['halluc_pp']},p95={r['p95_rel']},cost={r['cost_rel']})"
                                for r in top5]), 
                      flush=True)
                
                # === 자동 승급 판단 (Top-1) ===
                if top5:
                    best = top5[0]
                    # 승급 임계치 (환경변수 기반, Prod/Cand 개별)
                    MIN_PROD = int(os.getenv("PROMO_MIN_PROD", "50"))
                    MIN_CAND = int(os.getenv("PROMO_MIN_CAND", "50"))
                    LIMITS = {
                        "halluc_pp_max": float(os.getenv("PROMO_HALLU_MAX", "1.0")),
                        "p95_rel_max":   float(os.getenv("PROMO_P95_MAX",   "1.10")),
                        "cost_rel_max":  float(os.getenv("PROMO_COST_MAX",  "1.10")),
                    }
                    policy_limits = {**LIMITS, "min_prod": MIN_PROD, "min_cand": MIN_CAND}
                    ok = (
                        float(best["cand_samples"]) >= policy_limits["min_cand"] and
                        float(best["prod_samples"]) >= policy_limits["min_prod"] and
                        float(best["halluc_pp"]) <= policy_limits["halluc_pp_max"] and
                        float(best["p95_rel"])    <= policy_limits["p95_rel_max"] and
                        float(best["cost_rel"])   <= policy_limits["cost_rel_max"]
                    )
                    decision = "promote" if ok else "hold"
                    # 결정 사유 메시지 가독성(±표기) - 정확한 분기
                    def _dir_hallu(v):   
                        return "better" if float(v) < 0 else ("neutral" if float(v)==0 else "worse")
                    def _dir_rel(v):     
                        v=float(v); return "better" if v < 1.0 else ("neutral" if v==1.0 else "worse")
                    
                    h_dir   = _dir_hallu(best['halluc_pp'])
                    p95_dir = _dir_rel(best['p95_rel'])
                    cost_dir= _dir_rel(best['cost_rel'])
                    reason = (f"samples(model)={best['cand_samples']}/{best['prod_samples']} (min {MIN_CAND}/{MIN_PROD}); "
                              f"limits(hallu≤{LIMITS['halluc_pp_max']}pp, p95≤{LIMITS['p95_rel_max']}, cost≤{LIMITS['cost_rel_max']}); "
                              f"hallu={h_dir}({best['halluc_pp']:+.2f}pp); "
                              f"p95={_dir_rel(best['p95_rel'])}({float(best['p95_rel']):.3f}); "
                              f"cost={_dir_rel(best['cost_rel'])}({float(best['cost_rel']):.3f})")
                    # 태스크 1: 승격 기록 무소음화(idempotent) - insert_promotion_once() 사용
                    cur.execute("SELECT insert_promotion_once(%s, %s, %s)", (best["model_id"], decision, reason))
                    print(f"[agg:decision] {best['model_id']} -> {decision} ({reason})", flush=True)
                    
                    # 태스크 2: N/3 연속 통과 게이트 - 3연속 promote 시에만 final 발행
                    if decision == 'promote':
                        cur.execute("""
                            WITH snaps AS (
                              SELECT decision_ts, decision='promote' AS pass
                              FROM promotion_decisions
                              WHERE model_id=%s AND decision_ts >= NOW()-INTERVAL '15 minutes'
                              ORDER BY decision_ts DESC LIMIT 3
                            ) SELECT COUNT(*) FILTER (WHERE pass)=3 AS ok FROM snaps
                        """, (best["model_id"],))
                        result = cur.fetchone()
                        if result and result[0]:  # 3연속 통과
                            cur.execute("SELECT insert_promotion_once(%s, %s, %s)", (best["model_id"], "promote_final", f"3연속 통과: {reason}"))
                            print(f"[agg:decision-final] {best['model_id']} -> promote_final (3연속 통과)", flush=True)
                    
    except Exception as e:
        print(f"❌ 집계 실행 실패: {e}", flush=True)
        import traceback
        traceback.print_exc()

def main_loop():
    """메인 루프"""
    print("🚀 DuRi Aggregation Worker 시작", flush=True)
    
    while True:
        try:
            run_once()
            time.sleep(60)  # 1분 대기
        except KeyboardInterrupt:
            print("🛑 사용자 중단", flush=True)
            break
        except Exception as e:
            print(f"❌ 메인 루프 오류: {e}", flush=True)
            time.sleep(30)  # 오류 시 30초 대기

if __name__ == "__main__":
    main_loop()
