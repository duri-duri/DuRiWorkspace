#!/usr/bin/env bash
# L4 Evolution - 게이트 실행기
# 목적: PROMOTE/ROLLBACK/RETRY 결정
# Usage: bash scripts/evolution/gate_executor.sh <session_id>

set -euo pipefail

SESSION_ID="${1:-}"
ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
cd "$ROOT"

if [ -z "$SESSION_ID" ]; then
    echo "Usage: bash scripts/evolution/gate_executor.sh <session_id>"
    exit 1
fi

EV_DIR="${ROOT}/var/evolution/EV-${SESSION_ID}"
GATE_RESULT="${EV_DIR}/gate.json"

echo "=== Gate Executor ==="
echo "Session ID: $SESSION_ID"
echo ""

# 1. 메트릭 로드
METRICS_FILE="${EV_DIR}/metrics.json"
if [ ! -f "$METRICS_FILE" ]; then
    echo "❌ 메트릭 파일 없음: $METRICS_FILE"
    exit 1
fi

METRICS=$(cat "$METRICS_FILE")

# 2. Gate 실행
echo "Gate 실행 중..."
GATE_OUTPUT=$(python3 scripts/evolution/promotion_gate_v2.py \
    --gate L4.1 \
    --window 24h \
    --output "$GATE_RESULT" 2>&1)

echo "$GATE_OUTPUT"
echo ""

# 3. 결정 읽기
if [ -f "$GATE_RESULT" ]; then
    DECISION=$(jq -r '.decision' "$GATE_RESULT" 2>/dev/null || echo "UNKNOWN")
    PASSED=$(jq -r '.passed' "$GATE_RESULT" 2>/dev/null || echo "false")
    SCORE=$(jq -r '.score' "$GATE_RESULT" 2>/dev/null || echo "0.0")
    
    echo "결정: $DECISION"
    echo "통과: $PASSED"
    echo "스코어: $SCORE"
    echo ""
    
    # 4. 행동 실행
    case "$DECISION" in
        PROMOTE)
            echo "=== PROMOTE ==="
            TAG="evo-pass-$(date +%Y%m%d-%H%M)"
            
            # 태그 생성
            git tag -a "$TAG" -m "L4.1 Gate 통과: $SESSION_ID (score=$SCORE)" || true
            
            # 문서 스냅샷
            mkdir -p "${EV_DIR}/snapshot"
            git diff --stat > "${EV_DIR}/snapshot/diff_stat.txt" || true
            git log --oneline -10 > "${EV_DIR}/snapshot/recent_commits.txt" || true
            
            echo "✅ 태그 생성: $TAG"
            echo "✅ 스냅샷 저장: ${EV_DIR}/snapshot"
            ;;
        ROLLBACK)
            echo "=== ROLLBACK ==="
            
            # 직전 태그 찾기
            LAST_TAG=$(git tag -l "evo-pass-*" | sort -V | tail -1)
            
            if [ -n "$LAST_TAG" ]; then
                echo "직전 태그로 복구: $LAST_TAG"
                git checkout "$LAST_TAG" || true
            fi
            
            # 실패 리포트 저장
            FAILURE_REPORT="${EV_DIR}/failure_report.md"
            cat > "$FAILURE_REPORT" <<EOF
# 실패 리포트

Session ID: $SESSION_ID
Timestamp: $(date)
Score: $SCORE
Decision: $DECISION

## 실패 원인
$(jq -r '.failures[]' "$GATE_RESULT" 2>/dev/null || echo "Gate 미통과")

## 메트릭
$(jq '.' "$METRICS_FILE" 2>/dev/null || echo "{}")
EOF
            
            echo "✅ 실패 리포트 저장: $FAILURE_REPORT"
            
            # recover_coldsync.sh 호출 (선택)
            if [ -f "scripts/bin/recover_coldsync.sh" ]; then
                echo "coldsync 시스템 일시 차단 중..."
                bash scripts/bin/recover_coldsync.sh || true
            fi
            ;;
        RETRY*)
            RETRY_COUNT=$(echo "$DECISION" | grep -oE '[0-9]+' || echo "1")
            echo "=== RETRY ($RETRY_COUNT) ==="
            echo "재시도 대기 중..."
            ;;
        *)
            echo "=== UNKNOWN: $DECISION ==="
            ;;
    esac
else
    echo "❌ Gate 결과 파일 생성 실패"
    exit 1
fi

echo ""
echo "=== Gate Executor 완료 ==="

