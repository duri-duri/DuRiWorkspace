#!/usr/bin/env python3
"""
데이터 보존/프라이버시 정책
- PII 마스킹 후 저장
- 원본 30일, 가공 데이터 180일 보존
- 자동 정리 스크립트
"""

import psycopg2
from psycopg2.extras import DictCursor
from datetime import datetime, timedelta
import re

# 설정
PG_CONFIG = {
    "host": "duri-postgres",
    "port": 5432,
    "dbname": "duri",
    "user": "duri",
    "password": "duri"
}

class DataRetentionPolicy:
    def __init__(self):
        self.conn = psycopg2.connect(**PG_CONFIG)
    
    def mask_pii(self, text: str) -> str:
        """PII 마스킹 (전화번호, 이메일, 주민번호)"""
        if not text:
            return text
        
        # 전화번호 마스킹 (010-1234-5678 → 010-****-5678)
        text = re.sub(r'(\d{3})-(\d{4})-(\d{4})', r'\1-****-\3', text)
        
        # 이메일 마스킹 (user@domain.com → u***@domain.com)
        text = re.sub(r'([a-zA-Z])[a-zA-Z0-9._%+-]*@([a-zA-Z0-9.-]+\.[a-zA-Z]{2,})', r'\1***@\2', text)
        
        # 주민번호 마스킹 (123456-1234567 → 123456-*******)
        text = re.sub(r'(\d{6})-(\d{7})', r'\1-*******', text)
        
        # 신용카드 번호 마스킹 (1234-5678-9012-3456 → 1234-****-****-3456)
        text = re.sub(r'(\d{4})-(\d{4})-(\d{4})-(\d{4})', r'\1-****-****-\4', text)
        
        return text
    
    def apply_pii_masking(self):
        """기존 데이터에 PII 마스킹 적용"""
        with self.conn.cursor() as cur:
            # feedback_events 테이블 PII 마스킹
            cur.execute("""
                UPDATE feedback_events 
                SET meta = jsonb_set(
                    meta, 
                    '{user_id}', 
                    to_jsonb(mask_pii(COALESCE(meta->>'user_id', '')))
                )
                WHERE meta->>'user_id' IS NOT NULL
                AND meta->>'user_id' ~ '^[0-9-@.]+$'
            """)
            
            # coach_results 테이블 PII 마스킹
            cur.execute("""
                UPDATE coach_results 
                SET prompt = jsonb_set(
                    prompt, 
                    '{task}', 
                    to_jsonb(mask_pii(COALESCE(prompt->>'task', '')))
                )
                WHERE prompt->>'task' IS NOT NULL
            """)
            
            # prefs 테이블 PII 마스킹
            cur.execute("""
                UPDATE prefs 
                SET prompt = mask_pii(prompt),
                    chosen = mask_pii(chosen),
                    rejected = mask_pii(rejected)
                WHERE prompt IS NOT NULL
            """)
            
            self.conn.commit()
            print("✅ PII 마스킹 적용 완료")
    
    def cleanup_old_data(self):
        """오래된 데이터 정리"""
        with self.conn.cursor() as cur:
            # 30일 이상 된 원본 데이터 정리
            cutoff_30d = datetime.now() - timedelta(days=30)
            cutoff_180d = datetime.now() - timedelta(days=180)
            
            # feedback_events (30일)
            cur.execute("""
                DELETE FROM feedback_events 
                WHERE ts < %s 
                AND COALESCE(meta->>'retention_180d', 'false') = 'false'
            """, (cutoff_30d,))
            
            deleted_feedback = cur.rowcount
            
            # coach_results (180일)
            cur.execute("""
                DELETE FROM coach_results 
                WHERE ts < %s
            """, (cutoff_180d,))
            
            deleted_coach = cur.rowcount
            
            # prefs (180일)
            cur.execute("""
                DELETE FROM prefs 
                WHERE ts < %s
            """, (cutoff_180d,))
            
            deleted_prefs = cur.rowcount
            
            self.conn.commit()
            
            print(f"✅ 데이터 정리 완료:")
            print(f"   - feedback_events: {deleted_feedback}개 삭제")
            print(f"   - coach_results: {deleted_coach}개 삭제")
            print(f"   - prefs: {deleted_prefs}개 삭제")
    
    def mark_for_long_retention(self, table: str, condition: str):
        """장기 보존 태그 추가"""
        with self.conn.cursor() as cur:
            if table == "feedback_events":
                cur.execute(f"""
                    UPDATE feedback_events 
                    SET meta = jsonb_set(meta, '{{retention_180d}}', 'true')
                    WHERE {condition}
                """)
            elif table == "coach_results":
                cur.execute(f"""
                    UPDATE coach_results 
                    SET answer = jsonb_set(answer, '{{retention_180d}}', 'true')
                    WHERE {condition}
                """)
            
            self.conn.commit()
            print(f"✅ {table} 장기 보존 태그 추가 완료")
    
    def close(self):
        """연결 종료"""
        self.conn.close()

def main():
    """메인 실행"""
    policy = DataRetentionPolicy()
    
    try:
        print("🔄 데이터 보존/프라이버시 정책 적용 중...")
        
        # 1. PII 마스킹 적용
        policy.apply_pii_masking()
        
        # 2. 오래된 데이터 정리
        policy.cleanup_old_data()
        
        # 3. 고품질 데이터 장기 보존 태그
        policy.mark_for_long_retention(
            "feedback_events", 
            "score > 0.8 AND guard_violations = 0"
        )
        
        print("✅ 데이터 보존/프라이버시 정책 적용 완료")
        
    finally:
        policy.close()

if __name__ == "__main__":
    main()
