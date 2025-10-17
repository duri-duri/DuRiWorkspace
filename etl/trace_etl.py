#!/usr/bin/env python3
"""
Trace v2 ETL: Redis → Postgres upsert
경량 ETL 스켈레톤 (동기판, 외부 라이브러리 최소)
"""
import json, os, time
import psycopg2
import redis
from datetime import datetime, timezone

REDIS_URL = os.getenv("REDIS_URL", "redis://duri-redis:6379/0")
QUEUE_KEY = os.getenv("TRACE_QUEUE", "trace:events")

PG_DSN = os.getenv("PG_DSN", "postgresql://duri:duri@duri-postgres:5432/duri")

def pg():
    return psycopg2.connect(PG_DSN)

def ensure_span(cur, span):
    """스팬 업서트 (필수 키: span_name, status, start_ts)"""
    # JSONB 필드를 JSON 문자열로 변환
    span_data = span.copy()
    if 'labels' in span_data and isinstance(span_data['labels'], dict):
        span_data['labels'] = json.dumps(span_data['labels'])
    if 'attrs' in span_data and isinstance(span_data['attrs'], dict):
        span_data['attrs'] = json.dumps(span_data['attrs'])
    
    cur.execute("""
        INSERT INTO trace_span (span_id, parent_span_id, deploy_req_id, artifact_id,
                                span_name, status, start_ts, end_ts, labels, attrs)
        VALUES (%(span_id)s, %(parent_span_id)s, %(deploy_req_id)s, %(artifact_id)s,
                %(span_name)s, %(status)s, %(start_ts)s, %(end_ts)s, %(labels)s::jsonb, %(attrs)s::jsonb)
        ON CONFLICT (span_id) DO UPDATE
        SET status = EXCLUDED.status,
            end_ts = COALESCE(EXCLUDED.end_ts, trace_span.end_ts),
            labels = COALESCE(EXCLUDED.labels, trace_span.labels),
            attrs  = COALESCE(EXCLUDED.attrs,  trace_span.attrs);
    """, span_data)

def insert_eval_snapshot(cur, snap):
    """평가 스냅샷 삽입"""
    # JSONB 필드를 JSON 문자열로 변환
    snap_data = snap.copy()
    if 'meta' in snap_data and isinstance(snap_data['meta'], dict):
        snap_data['meta'] = json.dumps(snap_data['meta'])
    
    cur.execute("""
        INSERT INTO eval_snapshot (snapshot_id, span_id, window_start, window_end,
                                   policy_version, sample_source, kpi_name,
                                   kpi_value, n_samples, meta)
        VALUES (%(snapshot_id)s, %(span_id)s, %(window_start)s, %(window_end)s,
                %(policy_version)s, %(sample_source)s, %(kpi_name)s,
                %(kpi_value)s, %(n_samples)s, %(meta)s::jsonb)
        ON CONFLICT (snapshot_id) DO NOTHING;
    """, snap_data)

def insert_artifact(cur, art):
    """아티팩트 삽입"""
    # JSONB 필드를 JSON 문자열로 변환
    art_data = art.copy()
    if 'meta' in art_data and isinstance(art_data['meta'], dict):
        art_data['meta'] = json.dumps(art_data['meta'])
    
    cur.execute("""
        INSERT INTO artifact (artifact_id, kind, name, version_tag, model_sha, pipeline_sha, meta)
        VALUES (%(artifact_id)s, %(kind)s, %(name)s, %(version_tag)s, %(model_sha)s, %(pipeline_sha)s, %(meta)s::jsonb)
        ON CONFLICT (artifact_id) DO UPDATE
        SET version_tag = EXCLUDED.version_tag,
            model_sha = EXCLUDED.model_sha,
            pipeline_sha = EXCLUDED.pipeline_sha,
            meta = EXCLUDED.meta;
    """, art_data)

def main():
    """메인 ETL 루프"""
    r = redis.from_url(REDIS_URL)
    print(f"🚀 Trace ETL 시작: Redis={REDIS_URL}, Queue={QUEUE_KEY}")
    
    while True:
        try:
            item = r.blpop(QUEUE_KEY, timeout=5)  # left-pop blocking
            if not item:
                continue
            _, payload = item
            evt = json.loads(payload)

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
                    conn.commit()
        except Exception as e:
            print(f"❌ ETL Error: {e}")
            time.sleep(1)  # 에러 시 잠시 대기

if __name__ == "__main__":
    main()
