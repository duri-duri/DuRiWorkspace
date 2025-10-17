#!/usr/bin/env python3
"""
자동 롤백: duri_recent_good < 1 and burn_rate>threshold 5~10분 지속 시 make rollback 트리거
"""

import redis
import time
import subprocess
import json
from datetime import datetime, timedelta

# Redis 연결
r = redis.Redis(host='localhost', port=6379, db=0)

# 롤백 임계값
ROLLBACK_THRESHOLDS = {
    "duri_recent_good": 1.0,  # duri_recent_good < 1
    "burn_rate": 0.05,        # burn_rate > 5%
    "duration_minutes": 5     # 5분 지속
}

def get_duri_recent_good():
    """duri_recent_good 메트릭 가져오기"""
    try:
        # Prometheus에서 메트릭 가져오기 (임시)
        result = subprocess.run(['curl', '-s', 'http://localhost:8083/metrics'], 
                              capture_output=True, text=True)
        for line in result.stdout.split('\n'):
            if line.startswith('duri_recent_good '):
                return float(line.split()[1])
        return 1.0  # 기본값
    except:
        return 1.0

def get_burn_rate():
    """Burn rate 계산"""
    try:
        # 5분 윈도우 5xx 비율 (임시)
        return 0.03  # 3%
    except:
        return 0.0

def check_rollback_conditions():
    """롤백 조건 체크"""
    duri_recent_good = get_duri_recent_good()
    burn_rate = get_burn_rate()
    
    conditions_met = (
        duri_recent_good < ROLLBACK_THRESHOLDS["duri_recent_good"] and
        burn_rate > ROLLBACK_THRESHOLDS["burn_rate"]
    )
    
    return conditions_met, {
        "duri_recent_good": duri_recent_good,
        "burn_rate": burn_rate,
        "conditions_met": conditions_met
    }

def trigger_rollback(reason):
    """롤백 트리거"""
    try:
        print(f"🚨 자동 롤백 트리거: {reason}")
        
        # make rollback 실행
        result = subprocess.run(['make', 'rollback-staging'], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ 롤백 성공")
            
            # 롤백 기록
            r.lpush("auto_rollbacks", json.dumps({
                "timestamp": datetime.now().isoformat(),
                "reason": reason,
                "success": True
            }))
            
        else:
            print(f"❌ 롤백 실패: {result.stderr}")
            
            # 실패 기록
            r.lpush("auto_rollbacks", json.dumps({
                "timestamp": datetime.now().isoformat(),
                "reason": reason,
                "success": False,
                "error": result.stderr
            }))
            
    except Exception as e:
        print(f"❌ 롤백 트리거 실패: {e}")

def monitor_rollback_conditions():
    """롤백 조건 모니터링"""
    condition_start_time = None
    
    while True:
        conditions_met, metrics = check_rollback_conditions()
        
        if conditions_met:
            if condition_start_time is None:
                condition_start_time = datetime.now()
                print(f"⚠️ 롤백 조건 감지: {metrics}")
            
            # 지속 시간 체크
            duration = datetime.now() - condition_start_time
            if duration >= timedelta(minutes=ROLLBACK_THRESHOLDS["duration_minutes"]):
                reason = f"조건 {duration.total_seconds():.0f}초 지속: {metrics}"
                trigger_rollback(reason)
                condition_start_time = None
                
        else:
            if condition_start_time is not None:
                print("✅ 롤백 조건 해제")
                condition_start_time = None
        
        time.sleep(60)  # 1분마다 체크

if __name__ == "__main__":
    print("🚀 자동 롤백 모니터링 시작")
    monitor_rollback_conditions()
