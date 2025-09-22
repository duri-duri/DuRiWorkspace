# tools/hashchain_auto_verify.py
#!/usr/bin/env python3
# 해시체인 자동검증 훅: 5분마다 연속성 검증

import psycopg2
from psycopg2.extras import RealDictCursor
import time
import json
from datetime import datetime

def verify_hashchain_integrity():
    """해시체인 연속성 검증"""
    try:
        conn = psycopg2.connect("postgresql://postgres:postgres@localhost:5433/postgres")
        
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            # 해시체인 연속성 검증
            cur.execute("""
                WITH ordered AS (
                    SELECT id, prev_hash, this_hash,
                           lag(this_hash) OVER (ORDER BY id) AS prev_chain
                    FROM audit_ledger
                    ORDER BY id
                )
                SELECT * FROM ordered 
                WHERE prev_hash IS DISTINCT FROM prev_chain
                AND prev_hash IS NOT NULL
            """)
            
            violations = cur.fetchall()
            
            if violations:
                print(f"❌ 해시체인 위반 발견: {len(violations)}건")
                for v in violations:
                    print(f"  ID {v['id']}: prev_hash={v['prev_hash'][:8]}... != prev_chain={v['prev_chain'][:8]}...")
                
                # bundle_verify_fail_total 증가
                cur.execute("""
                    INSERT INTO audit_ledger (kind, details, prev_hash, this_hash)
                    VALUES ('hashchain_violation', %s, 
                           (SELECT this_hash FROM audit_ledger ORDER BY id DESC LIMIT 1),
                           %s)
                """, (
                    json.dumps({"violations": len(violations), "timestamp": datetime.now().isoformat()}),
                    "hashchain_violation_" + datetime.now().strftime("%Y%m%d_%H%M%S")
                ))
                
                return False
            else:
                print(f"✅ 해시체인 무결성 확인: {datetime.now().strftime('%H:%M:%S')}")
                return True
                
    except Exception as e:
        print(f"❌ 해시체인 검증 실패: {e}")
        return False
    finally:
        if 'conn' in locals():
            conn.close()

def run_continuous_verification():
    """5분마다 연속 검증"""
    print("=== 해시체인 자동검증 시작 ===")
    print("• 5분마다 연속성 검증")
    print("• 위반 시 audit_ledger에 기록")
    print("• Ctrl+C로 종료")
    
    try:
        while True:
            verify_hashchain_integrity()
            time.sleep(300)  # 5분 대기
    except KeyboardInterrupt:
        print("\n=== 해시체인 자동검증 종료 ===")

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "--once":
        verify_hashchain_integrity()
    else:
        run_continuous_verification()
