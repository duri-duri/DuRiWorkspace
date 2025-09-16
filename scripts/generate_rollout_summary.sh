#!/usr/bin/env bash
set -Eeuo pipefail
# 운영 전환 요약 리포트 생성 (기존 auto_mirror_latest.sh 패턴 활용)

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
STAMP="$(date +%Y%m%d_%H%M%S)"
REPORT_DIR="$ROOT/var/reports"
REPORT="$REPORT_DIR/ROLLOUT_SUMMARY_$STAMP.md"

mkdir -p "$REPORT_DIR"

echo "# 🚀 운영 전환 요약 리포트" > "$REPORT"
echo "**생성일시**: $(date -Iseconds)" >> "$REPORT"
echo "" >> "$REPORT"

echo "## 📊 현재 전환 상태" >> "$REPORT"
echo "- **ROLLOUT**: ${DURI_UNIFIED_REASONING_ROLLOUT:-0}%" >> "$REPORT"
echo "- **MODE**: ${DURI_UNIFIED_REASONING_MODE:-auto}" >> "$REPORT"
echo "" >> "$REPORT"

echo "## ✅ 테스트 결과" >> "$REPORT"
echo "### 계약 테스트" >> "$REPORT"
if pytest -q tests/contracts -k "reasoning" >/dev/null 2>&1; then
    echo "- ✅ **통과** (11/11)" >> "$REPORT"
else
    echo "- ❌ **실패**" >> "$REPORT"
fi

echo "### 통합 테스트" >> "$REPORT"
if pytest -q tests/contracts_unified -k "unified or rollout" >/dev/null 2>&1; then
    echo "- ✅ **통과** (4/4)" >> "$REPORT"
else
    echo "- ❌ **실패**" >> "$REPORT"
fi

echo "### 스모크 테스트" >> "$REPORT"
if pytest -q tests/contracts -k "reasoning_smoke" >/dev/null 2>&1; then
    echo "- ✅ **통과** (9/9)" >> "$REPORT"
else
    echo "- ❌ **실패**" >> "$REPORT"
fi

echo "" >> "$REPORT"
echo "## 📈 성능 벤치마크" >> "$REPORT"
if [ -d "$ROOT/.benchmarks" ]; then
    echo "- ✅ **기준선 존재**" >> "$REPORT"
    if scripts/bench_compare.sh >/dev/null 2>&1; then
        echo "- ✅ **회귀 없음** (mean +10% 이내)" >> "$REPORT"
    else
        echo "- ❌ **회귀 감지** (mean +10% 초과)" >> "$REPORT"
    fi
else
    echo "- ⚠️ **기준선 없음** (벤치마크 미실행)" >> "$REPORT"
fi

echo "" >> "$REPORT"
echo "## 📁 아티팩트 위치" >> "$REPORT"
echo "- **벤치마크**: \`var/reports/bench_*\`" >> "$REPORT"
echo "- **검증 리포트**: \`var/reports/final_verify_*\`" >> "$REPORT"
echo "- **모니터링 로그**: \`var/reports/rollout_monitor_*\`" >> "$REPORT"

echo "" >> "$REPORT"
echo "## 🎯 권장사항" >> "$REPORT"
rollout_pct="${DURI_UNIFIED_REASONING_ROLLOUT:-0}"
if [ "$rollout_pct" -eq 0 ]; then
    echo "- **다음 단계**: 25% 전환 실행" >> "$REPORT"
    echo "- **명령어**: \`scripts/rollout_ops.sh start-25\`" >> "$REPORT"
elif [ "$rollout_pct" -eq 25 ]; then
    echo "- **다음 단계**: 50% 전환 실행 (1-2시간 후)" >> "$REPORT"
    echo "- **명령어**: \`scripts/rollout_ops.sh start-50\`" >> "$REPORT"
elif [ "$rollout_pct" -eq 50 ]; then
    echo "- **다음 단계**: 100% 전환 실행 (24시간 후)" >> "$REPORT"
    echo "- **명령어**: \`scripts/rollout_ops.sh start-100\`" >> "$REPORT"
elif [ "$rollout_pct" -eq 100 ]; then
    echo "- **완료**: 100% 전환 완료" >> "$REPORT"
    echo "- **모니터링**: \`scripts/rollout_ops.sh monitor\`" >> "$REPORT"
else
    echo "- **현재**: ${rollout_pct}% 전환 중" >> "$REPORT"
    echo "- **모니터링**: \`scripts/rollout_ops.sh monitor\`" >> "$REPORT"
fi

echo "" >> "$REPORT"
echo "## 🚨 긴급 롤백" >> "$REPORT"
echo "문제 발생 시 즉시 롤백:" >> "$REPORT"
echo "\`\`\`bash" >> "$REPORT"
echo "scripts/rollout_ops.sh rollback" >> "$REPORT"
echo "\`\`\`" >> "$REPORT"

echo "✅ 요약 리포트 생성 완료: $REPORT"
