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
