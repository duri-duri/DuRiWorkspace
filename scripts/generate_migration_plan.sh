#!/bin/bash
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
META_DIR="/mnt/usb/CORE_PROTECTED/META"

echo "🚀 이관용 PLAN 자동 생성 시작..."
echo "작업 디렉토리: $META_DIR"

# 1. INDEX 정규화
echo "📋 1단계: INDEX 정규화..."
"$SCRIPT_DIR/normalize_index.sh"

# 2. Dedup 및 GOLD 선택
echo "🔍 2단계: Dedup 및 GOLD 선택..."
"$SCRIPT_DIR/dedup_gold_selector.sh"

# 3. 이관용 PLAN 생성
echo " 이관용 PLAN 생성..."
jq -s '
  {
    dedup_info: (.[0] | length),
    gold_files: (.[1] | length),
    migration_plan: {
      keep_files: (.[1] | map(.gold)),
      remove_candidates: (.[0] | map(.dups) | add)
    }
  }
' "$META_DIR/REPORT.dedup.json" "$META_DIR/REPORT.gold.json" > "$META_DIR/REPORT.migration.plan.json"

# 4. 최종 검증
echo "✅ 3단계: 최종 검증..."
echo "📊 생성된 파일들:"
ls -la "$META_DIR"/REPORT.*.json

echo "🎯 이관용 PLAN 생성 완료!"
echo "📁 다음 파일들을 확인하세요:"
echo "  - INDEX.full.normalized.jsonl (정규화된 INDEX)"
echo "  - REPORT.dedup.json (중복 정보)"
echo "  - REPORT.gold.json (GOLD 백업)"
echo "  - REPORT.migration.plan.json (이관 계획)"
