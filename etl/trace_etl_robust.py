#!/usr/bin/env python3
"""
Trace v2 ETL 견고화 버전: DLQ, 재시도, idempotency
Redis → Postgres upsert with dead letter queue and exponential backoff
"""
import json, os, time, traceback, uuid
import psycopg2
from psycopg2.extras import Json
import redis
from datetime import datetime, timezone
from typing import Dict, Any, Optional

REDIS_URL = os.getenv("REDIS_URL", "redis://duri-redis:6379/0")
QUEUE_KEY = os.getenv("TRACE_QUEUE", "trace:events")
DLQ_KEY = os.getenv("TRACE_DLQ", "trace:dead")

PG_DSN = os.getenv("PG_DSN", "postgresql://duri:duri@duri-postgres:5432/duri")

# 재시도 설정
MAX_RETRIES = int(os.getenv("MAX_RETRIES", "5"))
RETRY_DELAYS = [0.5, 1, 2, 4, 8]  # 지수 백오프

def pg():
    return psycopg2.connect(PG_DSN)

def as_uuid(s):
    """UUID 검증 함수"""
    try:
        return uuid.UUID(str(s))
    except (ValueError, TypeError):
        raise ValueError(f"Invalid UUID format: {s}")

def ensure_span(cur, span):
    """스팬 업서트 (필수 키: span_name, status, start_ts)"""
    # UUID 검증
    as_uuid(span.get('span_id'))
    if span.get('parent_span_id'):
        as_uuid(span['parent_span_id'])
    
    # deploy_req_id FK 검증 및 처리
    deploy_req_id = span.get('deploy_req_id')
    if deploy_req_id:
        # deploy_events 테이블에 존재하는지 확인
        cur.execute("SELECT 1 FROM deploy_events WHERE req_id = %s", (deploy_req_id,))
        if not cur.fetchone():
            print(f"⚠️ deploy_req_id '{deploy_req_id}' not found in deploy_events, setting to NULL")
            deploy_req_id = None
    
    # JSONB 필드를 Json 래퍼로 처리
    span_data = span.copy()
    span_data['deploy_req_id'] = deploy_req_id  # NULL로 설정된 값 사용
    if 'labels' in span_data and isinstance(span_data['labels'], dict):
        span_data['labels'] = Json(span_data['labels'])
    if 'attrs' in span_data and isinstance(span_data['attrs'], dict):
        span_data['attrs'] = Json(span_data['attrs'])
    
    cur.execute("""
        INSERT INTO trace_span (span_id, parent_span_id, deploy_req_id, artifact_id,
                                span_name, status, start_ts, end_ts, labels, attrs)
        VALUES (%(span_id)s, %(parent_span_id)s, %(deploy_req_id)s, %(artifact_id)s,
                %(span_name)s, %(status)s, %(start_ts)s, %(end_ts)s, %(labels)s, %(attrs)s)
        ON CONFLICT (span_id) DO UPDATE
        SET status = EXCLUDED.status,
            end_ts = COALESCE(EXCLUDED.end_ts, trace_span.end_ts),
            labels = COALESCE(EXCLUDED.labels, trace_span.labels),
            attrs  = COALESCE(EXCLUDED.attrs,  trace_span.attrs);
    """, span_data)

def insert_eval_snapshot(cur, snap):
    """평가 스냅샷 삽입"""
    # UUID 검증
    as_uuid(snap.get('snapshot_id'))
    if snap.get('span_id'):
        as_uuid(snap['span_id'])
    
    # JSONB 필드를 Json 래퍼로 처리
    snap_data = snap.copy()
    if 'meta' in snap_data and isinstance(snap_data['meta'], dict):
        snap_data['meta'] = Json(snap_data['meta'])
    
    cur.execute("""
        INSERT INTO eval_snapshot (snapshot_id, span_id, window_start, window_end,
                                   policy_version, sample_source, kpi_name,
                                   kpi_value, n_samples, meta)
        VALUES (%(snapshot_id)s, %(span_id)s, %(window_start)s, %(window_end)s,
                %(policy_version)s, %(sample_source)s, %(kpi_name)s,
                %(kpi_value)s, %(n_samples)s, %(meta)s)
        ON CONFLICT (snapshot_id) DO NOTHING;
    """, snap_data)

def insert_artifact(cur, art):
    """아티팩트 삽입"""
    # UUID 검증
    as_uuid(art.get('artifact_id'))
    
    # JSONB 필드를 Json 래퍼로 처리
    art_data = art.copy()
    if 'meta' in art_data and isinstance(art_data['meta'], dict):
        art_data['meta'] = Json(art_data['meta'])
    
    cur.execute("""
        INSERT INTO artifact (artifact_id, kind, name, version_tag, model_sha, pipeline_sha, meta)
        VALUES (%(artifact_id)s, %(kind)s, %(name)s, %(version_tag)s, %(model_sha)s, %(pipeline_sha)s, %(meta)s)
        ON CONFLICT (artifact_id) DO UPDATE
        SET version_tag = EXCLUDED.version_tag,
            model_sha = EXCLUDED.model_sha,
            pipeline_sha = EXCLUDED.pipeline_sha,
            meta = EXCLUDED.meta;
    """, art_data)

def process_event_with_retry(evt: Dict[str, Any], r: redis.Redis) -> bool:
    """이벤트 처리 (재시도 + DLQ)"""
    for attempt in range(MAX_RETRIES):
        try:
            with pg() as conn:
                with conn.cursor() as cur:
                    kind = evt.get("kind")
                    if kind == "span_upsert":
                        ensure_span(cur, evt["span"])
                        print(f"✅ Span upsert: {evt['span'].get('span_name', 'unknown')}")
                    elif kind == "eval_snapshot":
                        insert_eval_snapshot(cur, evt["snapshot"])
                        print(f"✅ Eval snapshot: {evt['snapshot'].get('kpi_name', 'unknown')}")
                    elif kind == "deploy_event":
                        cur.execute("""
                            INSERT INTO deploy_events(req_id, env, service, source, commit, node_id, pipeline, ts)
                            VALUES (%(req_id)s, %(env)s, %(service)s, %(source)s, %(commit)s, %(node_id)s, %(pipeline)s, %(ts)s)
                            ON CONFLICT (req_id) DO NOTHING;
                        """, evt["deploy"])
                        print(f"✅ Deploy event: {evt['deploy'].get('service', 'unknown')}")
                    elif kind == "artifact_upsert":
                        insert_artifact(cur, evt["artifact"])
                        print(f"✅ Artifact upsert: {evt['artifact'].get('name', 'unknown')}")
                    else:
                        print(f"⚠️ Unknown event kind: {kind}")
                        return True  # 알 수 없는 종류는 성공으로 처리
                    conn.commit()
                    return True
        except Exception as e:
            print(f"❌ ETL Error (attempt {attempt + 1}/{MAX_RETRIES}): {e}")
            if attempt < MAX_RETRIES - 1:
                time.sleep(RETRY_DELAYS[attempt])
            else:
                # 최종 실패 시 DLQ로 이동
                try:
                    dlq_payload = {
                        "original_event": evt,
                        "error": str(e),
                        "traceback": traceback.format_exc(),
                        "failed_at": datetime.now(timezone.utc).isoformat(),
                        "attempts": MAX_RETRIES
                    }
                    r.rpush(DLQ_KEY, json.dumps(dlq_payload))
                    print(f"💀 Event moved to DLQ: {DLQ_KEY}")
                except Exception as dlq_error:
                    print(f"❌ DLQ Error: {dlq_error}")
                return False
    return False

def main():
    """메인 ETL 루프 (견고화 버전)"""
    r = redis.from_url(REDIS_URL)
    print(f"🚀 Trace ETL 견고화 버전 시작: Redis={REDIS_URL}, Queue={QUEUE_KEY}, DLQ={DLQ_KEY}")
    
    processed_count = 0
    error_count = 0
    
    while True:
        try:
            item = r.blpop(QUEUE_KEY, timeout=5)  # left-pop blocking
            if not item:
                continue
            _, payload = item
            evt = json.loads(payload)
            
            if process_event_with_retry(evt, r):
                processed_count += 1
            else:
                error_count += 1
                
            # 주기적 상태 출력
            if (processed_count + error_count) % 100 == 0:
                print(f"📊 처리 통계: 성공={processed_count}, 실패={error_count}")
                
        except Exception as e:
            print(f"❌ Main loop error: {e}")
            time.sleep(1)  # 에러 시 잠시 대기

if __name__ == "__main__":
    main()
