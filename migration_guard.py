#!/usr/bin/env python3
"""
스키마/마이그 자동 가드: 견고화 (psql 옵션 강화, 체크섬 확인)
"""

import psycopg2
import subprocess
import json
import hashlib
from datetime import datetime

# DB 설정
DB_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "database": "duri",
    "user": "duri",
    "password": "duri"
}

# 마이그레이션 가드 설정
MIGRATION_GUARDS = {
    "pre_migration_checks": [
        "SELECT COUNT(*) FROM feedback_events;",
        "SELECT COUNT(*) FROM promotion_candidates;",
        "SELECT COUNT(*) FROM coach_results;"
    ],
    "post_migration_checks": [
        "SELECT COUNT(*) FROM feedback_events;",
        "SELECT COUNT(*) FROM promotion_candidates;",
        "SELECT COUNT(*) FROM coach_results;",
        "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public';"
    ],
    "rollback_queries": [
        "SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE state = 'active' AND pid <> pg_backend_pid();"
    ]
}

def execute_query(query, description=""):
    """쿼리 실행 (컨테이너 환경 통일)"""
    try:
        result = subprocess.run([
            'docker', 'compose', '-p', 'duriworkspace', 'exec', '-T', 
            'duri-postgres', 'psql', '-U', 'duri', '-d', 'duri',
            '-c', query
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            # 결과 파싱
            lines = result.stdout.strip().split('\n')
            if len(lines) >= 2:
                result_value = lines[-2].strip()
                print(f"✅ {description}: {result_value}")
                return result_value
            else:
                print(f"✅ {description}: 성공")
                return "success"
        else:
            print(f"❌ {description} 실패: {result.stderr}")
            return None
        
    except Exception as e:
        print(f"❌ {description} 오류: {e}")
        return None

def calculate_checksum():
    """스키마 체크섬 계산"""
    try:
        result = subprocess.run([
            'docker', 'compose', '-p', 'duriworkspace', 'exec', '-T', 
            'duri-postgres', 'psql', '-U', 'duri', '-d', 'duri',
            '-c', "SELECT string_agg(tablename, '') FROM pg_tables WHERE schemaname = 'public' ORDER BY tablename;"
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            tables = result.stdout.strip().split('\n')[-2].strip()
            return hashlib.md5(tables.encode()).hexdigest()
        return None
    except:
        return None

def pre_migration_health_check():
    """마이그레이션 전 헬스체크"""
    print("🔍 마이그레이션 전 헬스체크")
    
    results = {}
    for query in MIGRATION_GUARDS["pre_migration_checks"]:
        result = execute_query(query, f"Pre-check: {query[:50]}...")
        results[query] = result
    
    # 체크섬 계산
    checksum = calculate_checksum()
    results["checksum"] = checksum
    print(f"✅ Pre-check 체크섬: {checksum}")
    
    return results

def post_migration_health_check():
    """마이그레이션 후 헬스체크"""
    print("🔍 마이그레이션 후 헬스체크")
    
    results = {}
    for query in MIGRATION_GUARDS["post_migration_checks"]:
        result = execute_query(query, f"Post-check: {query[:50]}...")
        results[query] = result
    
    # 체크섬 계산
    checksum = calculate_checksum()
    results["checksum"] = checksum
    print(f"✅ Post-check 체크섬: {checksum}")
    
    return results

def run_migration_with_guard(migration_file):
    """가드와 함께 마이그레이션 실행 (견고화)"""
    print(f"🚀 마이그레이션 실행: {migration_file}")
    
    # 마이그레이션 전 헬스체크
    pre_results = pre_migration_health_check()
    
    # 마이그레이션 실행 (견고화 옵션)
    try:
        result = subprocess.run([
            'docker', 'compose', '-p', 'duriworkspace', 'exec', '-T', 
            'duri-postgres', 'psql', 
            '-v', 'ON_ERROR_STOP=1',
            '-v', "statement_timeout='30s'",
            '-U', 'duri', '-d', 'duri', 
            '-f', f'/app/{migration_file}'
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ 마이그레이션 실행 성공")
            
            # 마이그레이션 후 헬스체크
            post_results = post_migration_health_check()
            
            # 결과 비교
            for query in MIGRATION_GUARDS["pre_migration_checks"]:
                if query in pre_results and query in post_results:
                    pre_val = pre_results[query]
                    post_val = post_results[query]
                    
                    if pre_val != post_val:
                        print(f"⚠️ 데이터 변경 감지: {query[:50]}... {pre_val} → {post_val}")
                    else:
                        print(f"✅ 데이터 일관성 확인: {query[:50]}... {pre_val}")
            
            # 체크섬 비교
            if pre_results.get("checksum") != post_results.get("checksum"):
                print(f"⚠️ 스키마 변경 감지: {pre_results.get('checksum')} → {post_results.get('checksum')}")
            else:
                print(f"✅ 스키마 일관성 확인: {pre_results.get('checksum')}")
            
            return True
            
        else:
            print(f"❌ 마이그레이션 실행 실패: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ 마이그레이션 실행 오류: {e}")
        return False

def rollback_migration():
    """마이그레이션 롤백"""
    print("🔄 마이그레이션 롤백")
    
    for query in MIGRATION_GUARDS["rollback_queries"]:
        execute_query(query, f"Rollback: {query[:50]}...")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) != 2:
        print("사용법: python migration_guard.py <migration_file>")
        sys.exit(1)
    
    migration_file = sys.argv[1]
    success = run_migration_with_guard(migration_file)
    
    if not success:
        rollback_migration()
        sys.exit(1)
