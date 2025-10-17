#!/usr/bin/env python3
"""
DORA 메트릭 자동 계측
- 리드타임: 커밋 → 배포까지 시간
- 배포빈도: 일/주/월 배포 횟수
- 변경실패율: 배포 후 롤백 비율
- 복구시간: 장애 → 복구까지 시간
"""

import json
import subprocess
from datetime import datetime, timedelta
import psycopg2

def get_deployment_frequency():
    """배포빈도: 일/주/월 배포 횟수"""
    # Git 태그 기반으로 배포 횟수 계산
    result = subprocess.run(['git', 'tag', '--sort=-version:refname'], 
                          capture_output=True, text=True)
    tags = result.stdout.strip().split('\n')[:30]  # 최근 30개
    
    now = datetime.now()
    daily = sum(1 for tag in tags if is_within_period(tag, now, timedelta(days=1)))
    weekly = sum(1 for tag in tags if is_within_period(tag, now, timedelta(weeks=1)))
    monthly = sum(1 for tag in tags if is_within_period(tag, now, timedelta(days=30)))
    
    return {"daily": daily, "weekly": weekly, "monthly": monthly}

def get_lead_time():
    """리드타임: 커밋 → 배포까지 시간"""
    # 최근 배포의 커밋 시간과 배포 시간 차이
    result = subprocess.run(['git', 'log', '-1', '--format=%ct'], 
                          capture_output=True, text=True)
    commit_time = int(result.stdout.strip())
    
    # 배포 시간은 현재 시간으로 근사
    deploy_time = datetime.now().timestamp()
    
    return deploy_time - commit_time

def get_change_failure_rate():
    """변경실패율: 배포 후 롤백 비율"""
    # 실제 구현에서는 배포 히스토리와 롤백 기록을 분석
    return 0.05  # 임시 5%

def get_recovery_time():
    """복구시간: 장애 → 복구까지 시간"""
    # 실제 구현에서는 알람 발생 시간과 해결 시간을 분석
    return 300  # 임시 5분

def is_within_period(tag, now, period):
    """태그가 특정 기간 내에 생성되었는지 확인"""
    try:
        result = subprocess.run(['git', 'log', '-1', '--format=%ct', tag], 
                              capture_output=True, text=True)
        tag_time = datetime.fromtimestamp(int(result.stdout.strip()))
        return (now - tag_time) <= period
    except:
        return False

if __name__ == "__main__":
    metrics = {
        "deployment_frequency": get_deployment_frequency(),
        "lead_time_seconds": get_lead_time(),
        "change_failure_rate": get_change_failure_rate(),
        "recovery_time_seconds": get_recovery_time()
    }
    
    print(json.dumps(metrics, indent=2))
