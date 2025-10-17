#!/usr/bin/env bash
set -euo pipefail

# 데이터 무결성 체크섬 (CI)
# 태스크 7: v_feedback_events_clean 정의가 변하면 CI 실패

echo "=== 🔍 데이터 무결성 체크섬 검증 ==="

# DB 연결 정보
DB_URL="${POSTGRES_DSN:-postgresql://duri:duri@duri-postgres:5432/duri}"

# 현재 뷰 정의 가져오기
echo "📊 현재 v_feedback_events_clean 정의 확인 중..."
docker compose exec duri-postgres psql -U duri -d duri -c \
"SELECT definition FROM pg_views WHERE viewname='v_feedback_events_clean';" -At > /tmp/current_view.sql

# 기대하는 정의와 비교
echo "🔍 기대 정의와 비교 중..."
if [ -f "v_feedback_events_clean_ddl.sql" ]; then
    if diff -q /tmp/current_view.sql v_feedback_events_clean_ddl.sql > /dev/null; then
        echo "✅ v_feedback_events_clean 정의 일치"
        exit 0
    else
        echo "❌ v_feedback_events_clean 정의 불일치!"
        echo "현재 정의:"
        cat /tmp/current_view.sql
        echo ""
        echo "기대 정의:"
        cat v_feedback_events_clean_ddl.sql
        echo ""
        echo "차이점:"
        diff /tmp/current_view.sql v_feedback_events_clean_ddl.sql || true
        exit 1
    fi
else
    echo "⚠️ v_feedback_events_clean_ddl.sql 파일이 없습니다"
    echo "현재 정의를 저장합니다:"
    cat /tmp/current_view.sql
    cp /tmp/current_view.sql v_feedback_events_clean_ddl.sql
    echo "✅ v_feedback_events_clean_ddl.sql 생성 완료"
    exit 0
fi
