#!/usr/bin/env python3
# tools/audit_chain_check.py
import os, psycopg2, hashlib, sys

def check_audit_chain():
    """감사체인 위조 탐지 테스트"""
    try:
        conn = psycopg2.connect(
            host=os.getenv("PGHOST","/var/run/postgresql"),
            port=os.getenv("PGPORT","5432"),
            dbname=os.getenv("PGDATABASE","postgres"),
            user=os.getenv("PGUSER","postgres"),
            password=os.getenv("PGPASSWORD", None)  # 없으면 peer로 시도
        )
        cur = conn.cursor()
        cur.execute("SELECT id,prev_hash,this_hash,details::text FROM audit_ledger ORDER BY id")
        bad, prev = [], None
        for i,ph,th,det in cur:
            h = hashlib.sha256(((prev or '')+det).encode()).hexdigest()
            if h != th: bad.append((i, th, h))
            prev = th
        print("BAD:", bad)
        conn.close()
        return len(bad) == 0
    except Exception as e:
        print(f"DB 접속 실패: {e}")
        return False

if __name__ == "__main__":
    success = check_audit_chain()
    sys.exit(0 if success else 1)
