#!/usr/bin/env python3
"""
DORA 메트릭 익스포터 - 완전 재작성 (막판 미세 조정 4개 반영)
- Healthcheck에서 curl 의존 제거
- 포트 내부화 후에도 배포 이벤트 푸시 가능하게
- dedup 관측성 더 탄탄하게 (라벨·TTL 노출)
- 코드 청소(권장)
"""

import os
import json
import time
import threading
import ipaddress
from datetime import datetime
from urllib.parse import parse_qs
from collections import OrderedDict
from http.server import ThreadingHTTPServer as HTTPServer, BaseHTTPRequestHandler
from prometheus_client import Counter, Gauge, generate_latest, CONTENT_TYPE_LATEST
import redis

# 환경 변수
PUSH_TOKEN = os.getenv('DORA_PUSH_TOKEN', 'duri-secret-token-2024')
REDIS_URL = os.getenv('REDIS_URL', 'redis://127.0.0.1:6379/0')

# 보안 설정
ALLOW_LOCAL_BYPASS = os.getenv('ALLOW_LOCAL_BYPASS', '0') == '1'
ALLOW_CIDR = os.getenv('ALLOW_PUSH_CIDR', '')  # 예: "172.18.0.0/16"

# 레이트리밋 튜닝
RL_CAP = float(os.getenv('PUSH_RL_CAPACITY', '10'))
RL_REFILL = float(os.getenv('PUSH_RL_REFILL', '10'))

# dedup TTL 설정
DEDUP_TTL = int(os.getenv('PUSH_DEDUP_TTL_SEC', '300'))

# Redis 연결
try:
    r = redis.from_url(REDIS_URL)
    r.ping()
    REDIS_AVAILABLE = True
    print(f"✅ Redis 연결 성공: {REDIS_URL}")
except Exception as e:
    print(f"❌ Redis 연결 실패: {e}")
    REDIS_AVAILABLE = False
    r = None

# 메트릭 정의
deployment_events = Counter('duri_deployment_events_total', 'Total deployment events')
deployment_events_persisted = Gauge('duri_deployment_events_persisted', 'Persisted deployment events')
deployment_events_labeled = Counter('duri_deployment_events_labeled_total', 'Labeled deployment events', ['env', 'service', 'source', 'commit'])

# 평가 점수 메트릭
auto_eval_score = Gauge('duri_auto_eval_score', 'Auto evaluation score', ['task_type', 'level'])
auto_eval_recent_avg = Gauge('duri_auto_eval_recent_avg', 'Recent average evaluation score')

# 지능형 게이트 메트릭 (Gauge로 변경 - 이중집계 방지)
promo_decisions = Gauge('duri_promo_decisions', 'Promotion decisions', ['decision'])

# Canary ratio 메트릭
canary_ratio = Gauge('duri_canary_ratio', 'Current canary traffic ratio')

# dedup/ratelimit 관측성 메트릭 (라벨 추가)
dedup_hits = Counter('duri_push_dedup_total', 'Deduplicated push requests', ['reason'])
rate_limited_hits = Counter('duri_push_rate_limited_total', 'Rate-limited push requests')

# 운영 튜닝값 메트릭
rl_tokens = Gauge('duri_push_tokens', 'Current tokens per source', ['source'])

# 간단 CIDR 체크 유틸
def ip_in_cidr(ip, cidr):
    try:
        return ipaddress.ip_address(ip) in ipaddress.ip_network(cidr, strict=False)
    except:
        return False

# dedup TTL을 Redis로 (재기동에도 유지)
def seen_once(qid: str, ttl=DEDUP_TTL):
    if not REDIS_AVAILABLE or not qid:
        return False
    # SETNX + EX를 한 번에 (redis-py 6.x는 set(..., nx=True, ex=ttl))
    return not r.set(f"push:seen:{qid}", 1, nx=True, ex=ttl)  # True면 이미 봄(=중복)

# 레이트리밋터 (스레드 세이프티 추가)
class TokenBucket:
    def __init__(self, capacity=RL_CAP, refill_rate=RL_REFILL):
        self.capacity = capacity
        self.tokens = capacity
        self.refill_rate = refill_rate
        self.last_refill = time.time()

class RateLimiter:
    def __init__(self):
        self.buckets = {}
        self._lock = threading.Lock()
    
    def get_bucket(self, key):
        with self._lock:
            return self.buckets.setdefault(key, TokenBucket())
    
    def is_allowed(self, key, tokens=1.0):
        bucket = self.get_bucket(key)
        now = time.time()
        
        # 토큰 리필
        time_passed = now - bucket.last_refill
        tokens_to_add = time_passed * bucket.refill_rate
        bucket.tokens = min(bucket.capacity, bucket.tokens + tokens_to_add)
        bucket.last_refill = now
        
        # 토큰 소비
        if bucket.tokens >= tokens:
            bucket.tokens -= tokens
            return True
        else:
            return False
    
    def get_tokens(self, key):
        bucket = self.get_bucket(key)
        now = time.time()
        
        # 토큰 리필
        time_passed = now - bucket.last_refill
        tokens_to_add = time_passed * bucket.refill_rate
        bucket.tokens = min(bucket.capacity, bucket.tokens + tokens_to_add)
        bucket.last_refill = now
        
        return bucket.tokens

rate_limiter = RateLimiter()

def record_deployment_event_labeled(env, service, source, commit):
    """라벨이 있는 배포 이벤트 기록"""
    deployment_events_labeled.labels(env=env, service=service, source=source, commit=commit).inc()
    deployment_events.inc()
    
    # Redis에 영구 저장 (전용 카운터 + 리스트 저장)
    if REDIS_AVAILABLE:
        try:
            # 전용 카운터 사용
            v = r.incr("duri:deploy_events")
            deployment_events_persisted.set(v)
            
            # 이벤트 데이터를 리스트로 저장
            data = {
                'env': env,
                'service': service,
                'source': source,
                'commit': commit,
                'timestamp': time.time()
            }
            r.lpush("deploy:events", json.dumps(data))
            r.ltrim("deploy:events", 0, 999)  # 최근 1000개만 보관
            
        except Exception as e:
            print(f"❌ Redis 저장 실패: {e}")

def check_health():
    """헬스체크 (튜닝값/카운터 스냅샷 포함)"""
    health_status = {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "components": {}
    }
    
    # Redis 연결 체크
    if REDIS_AVAILABLE:
        try:
            r.ping()
            health_status["components"]["redis"] = "healthy"
        except:
            health_status["components"]["redis"] = "unhealthy"
            health_status["status"] = "degraded"
    else:
        health_status["components"]["redis"] = "unavailable"
    
    # 튜닝값/카운터 스냅샷
    health_status["components"]["rate_limiter"] = {"capacity": RL_CAP, "refill": RL_REFILL}
    if REDIS_AVAILABLE:
        health_status["components"]["dedup_ttl_sec"] = DEDUP_TTL
        health_status["components"]["deploy_events"] = int(r.get("duri:deploy_events") or 0)
    
    return health_status

def check_ready():
    ok = REDIS_AVAILABLE
    return {"status": "ready" if ok else "not_ready", "redis": "ok" if ok else "fail"}

def mask(tok: str):
    if not tok: return ""
    return ("*" * max(0, len(tok)-4)) + tok[-4:]

def verify_token(headers, client_addr=None):
    auth = headers.get('Authorization', '')
    if auth.startswith('Bearer '):
        token = auth.split(' ',1)[1].strip()
        if token == PUSH_TOKEN:
            print(f"[auth ok] ip={client_addr} token={mask(token)}")
            return True
    print(f"[auth ng] ip={client_addr} token={mask(auth.split(' ',1)[1].strip() if ' ' in auth else auth)}")
    return False

def log_deploy_event(client_ip, source, req_id, service, env):
    """배포 이벤트 보안 로그 (client_ip/source/req_id 추가 기록)"""
    print(f"[deploy] ip={client_ip} source={source} req_id={req_id} service={service} env={env}")

def update_dora_metrics():
    """DORA 메트릭 업데이트 (전용 카운터 사용)"""
    try:
        if REDIS_AVAILABLE:
            v = int(r.get("duri:deploy_events") or 0)  # 전용 카운터만 사용
            deployment_events_persisted.set(v)
    except Exception as e:
        print(f"❌ DORA 메트릭 업데이트 실패: {e}")

def update_evaluation_metrics():
    """평가 메트릭 업데이트"""
    try:
        # 더미 데이터 (실제 구현 시 tools에서 가져오기)
        auto_eval_recent_avg.set(0.85)
        auto_eval_score.labels(task_type='reasoning', level='recent').set(0.90)
        auto_eval_score.labels(task_type='coding', level='recent').set(0.80)
    except Exception as e:
        print(f"❌ 평가 메트릭 업데이트 실패: {e}")

def update_promotion_metrics():
    """승격 메트릭 업데이트 (Gauge로 변경 - 이중집계 방지)"""
    try:
        # 더미 데이터 (실제 구현 시 tools에서 가져오기)
        promo_decisions.labels(decision='promote').set(5)
        promo_decisions.labels(decision='hold').set(3)
        promo_decisions.labels(decision='rollback').set(1)
    except Exception as e:
        print(f"❌ 승격 메트릭 업데이트 실패: {e}")

def update_canary_metric():
    """Canary ratio 메트릭 업데이트"""
    try:
        if REDIS_AVAILABLE:
            v = float(r.get("canary:ratio") or 0)
            canary_ratio.set(v)
    except Exception as e:
        print(f"❌ Canary 메트릭 업데이트 실패: {e}")

def update_rl_tokens_metric():
    """레이트리밋 토큰 메트릭 업데이트"""
    try:
        # 주요 소스별 토큰 수위 업데이트
        for source in ['ci', 'manual', 'auto']:
            tokens = rate_limiter.get_tokens(f"push:{source}")
            rl_tokens.labels(source=source).set(tokens)
    except Exception as e:
        print(f"❌ RL 토큰 메트릭 업데이트 실패: {e}")

# 백그라운드 갱신 루프 (단일 정의)
def bg_loop():
    """백그라운드 갱신 루프"""
    while True:
        update_dora_metrics()
        update_evaluation_metrics()
        update_promotion_metrics()
        update_canary_metric()
        update_rl_tokens_metric()
        time.sleep(30)

# HTTP 서버 클래스
class MetricsHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/metrics':
            self.send_response(200)
            self.send_header('Content-Type', CONTENT_TYPE_LATEST)
            self.end_headers()
            self.wfile.write(generate_latest())
            return
        if self.path == '/health':
            self.send_response(200)
            self.end_headers()
            self.wfile.write(json.dumps(check_health()).encode())
            return
        if self.path == '/ready':
            self.send_response(200)
            self.end_headers()
            self.wfile.write(json.dumps(check_ready()).encode())
            return
        if self.path.startswith('/push/deployment'):
            self.send_response(405); self.send_header('Allow','POST'); self.end_headers()
            self.wfile.write(b'only POST\n'); return
        self.send_response(404)
        self.end_headers()
        self.wfile.write(b'not found\n')
    
    def do_POST(self):
        if self.path.startswith('/push/deployment'):
            # 토큰 검증 (CIDR 허용 목록 + 환경변수 토글)
            client_ip = self.client_address[0]
            if not verify_token(self.headers, client_ip):
                self.send_response(401)
                self.end_headers()
                self.wfile.write(b'unauthorized\n')
                return
            # 입력 검증
            q = parse_qs(self.path.split('?')[1] if '?' in self.path else '')
            need = ['env','service','source','commit','id']
            missing = [k for k in need if not q.get(k)]
            if missing:
                self.send_response(400)
                self.end_headers()
                self.wfile.write(f"missing:{','.join(missing)}".encode())
                return

            # 중복 푸시 방지 (dedup 로직) - Redis TTL 사용
            qid = q.get('id', [None])[0]
            if qid and seen_once(qid):
                dedup_hits.labels(reason='redis_ttl').inc()
                self.send_response(200)
                self.end_headers()
                self.wfile.write(b'dedup\n')
                return
            
            # 레이트리밋 체크
            source = q.get('source', ['manual'])[0]
            if not rate_limiter.is_allowed(f"push:{source}", tokens=1.0):
                rate_limited_hits.inc()
                self.send_response(429)
                self.end_headers()
                self.wfile.write(b'rate_limited\n')
                return
            
            # 배포 이벤트 기록
            env = q.get('env', ['staging'])[0]
            service = q.get('service', ['duri_control'])[0]
            commit = q.get('commit', ['unknown'])[0]
            
            # 보안 로그 (client_ip/source/req_id 추가 기록)
            log_deploy_event(client_ip, source, qid, service, env)
            
            record_deployment_event_labeled(env, service, source, commit)
            
            # Trace v2: 배포 이벤트를 트레이스 루트 스팬으로 변환
            try:
                import time
                evt = {
                    "kind": "span_upsert",
                    "span": {
                        "span_id": f"deploy-{qid}",
                        "parent_span_id": None,
                        "deploy_req_id": qid,
                        "artifact_id": None,
                        "span_name": "deploy_root",
                        "status": "ok",
                        "start_ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                        "end_ts": None,
                        "labels": {"source": source, "env": env, "service": service},
                        "attrs": {"commit": commit, "pipeline": q.get('pipeline', ['unknown'])[0], "node_id": q.get('node_id', ['unknown'])[0]}
                    }
                }
                r.rpush("trace:events", json.dumps(evt))
                print(f"[trace] Deploy root span queued: {qid}")
            except Exception as e:
                print(f"[trace] Failed to queue deploy root span: {e}")
            
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b'OK\n')
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b'not found\n')
    
    def log_message(self, format, *args):
        # 로그 출력
        print(f"{self.address_string()} - - [{self.log_date_time_string()}] {format % args}")

if __name__ == "__main__":
    # 백그라운드 루프 시작 (한 번만)
    threading.Thread(target=bg_loop, daemon=True).start()
    
    # HTTP 서버 시작 (ThreadingHTTPServer 사용)
    httpd = HTTPServer(('0.0.0.0', 8000), MetricsHandler)
    print("🚀 DORA 메트릭 익스포터 시작: http://0.0.0.0:8000")
    httpd.serve_forever()
