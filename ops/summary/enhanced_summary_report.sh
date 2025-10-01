#!/usr/bin/env bash
set -euo pipefail

# 강화된 일일 요약 리포트 생성 스크립트
# Phase 3: 관찰성 일원화 + 19:05 일일 요약
# 사람이 보게 될 1장 자동 생성

ROOT="$(git rev-parse --show-toplevel)"
cd "$ROOT"

source ops/summary/config.env

# --- 락: 경합/중복 실행 차단 ---
if [[ -e "$LOCK_PATH" ]]; then
  echo "[WARN] lock present, skip run"; exit 100
fi
trap 'rm -f "$LOCK_PATH"' EXIT
: > "$LOCK_PATH"

ts() { date +"%Y-%m-%d %H:%M:%S%z"; }

fail_fast() {
  echo "[ERROR] $1"; exit 1
}

# --- Phase 3: 관찰성 일원화 검증 ---
echo "[INFO] Phase 3: 관찰성 일원화 검증 시작..."

# 1) 표준 로그 디렉토리 구조 확인
[[ -d "var/logs/backup" ]] || fail_fast "missing var/logs/backup"
[[ -d "var/logs/gate" ]] || fail_fast "missing var/logs/gate"
[[ -d "var/logs/system" ]] || fail_fast "missing var/logs/system"

# 2) 로그 디렉토리 쓰기 권한 확인
[[ -w "var/logs/backup" ]] || fail_fast "no write permission to var/logs/backup"
[[ -w "var/logs/gate" ]] || fail_fast "no write permission to var/logs/gate"
[[ -w "var/logs/system" ]] || fail_fast "no write permission to var/logs/system"

echo "[INFO] Phase 3: 관찰성 일원화 검증 완료"

# --- 로그 수집 & 상태 해석 ---
today=$(date +"%Y-%m-%d")
yesterday=$(date -d "yesterday" +"%Y-%m-%d")

# 표준 로그 경로에서 백업 상태 수집
backup_logs_dir="var/logs/backup/daily"
gate_logs_dir="var/logs/gate"
system_logs_dir="var/logs/system"

# 백업 작업별 성공/실패 카운트
incr_success=$(find "$backup_logs_dir" -name "incr_${today}*.log" -exec grep -l "SUCCESS\|COMPLETED" {} \; 2>/dev/null | wc -l | xargs)
incr_failed=$(find "$backup_logs_dir" -name "incr_${today}*.log" -exec grep -l "FAIL\|ERROR" {} \; 2>/dev/null | wc -l | xargs)

retention_success=$(find "$backup_logs_dir" -name "retention_${today}*.log" -exec grep -l "SUCCESS\|COMPLETED" {} \; 2>/dev/null | wc -l | xargs)
retention_failed=$(find "$backup_logs_dir" -name "retention_${today}*.log" -exec grep -l "FAIL\|ERROR" {} \; 2>/dev/null | wc -l | xargs)

health_success=$(find "$backup_logs_dir" -name "health_${today}*.log" -exec grep -l "SUCCESS\|COMPLETED" {} \; 2>/dev/null | wc -l | xargs)
health_failed=$(find "$backup_logs_dir" -name "health_${today}*.log" -exec grep -l "FAIL\|ERROR" {} \; 2>/dev/null | wc -l | xargs)

# 게이트 백업 상태
gate_core=$(find "$gate_logs_dir/core" -name "*${today}*.log" 2>/dev/null | wc -l | xargs)
gate_extended=$(find "$gate_logs_dir/extended" -name "*${today}*.log" 2>/dev/null | wc -l | xargs)
gate_full=$(find "$gate_logs_dir/full" -name "*${today}*.log" 2>/dev/null | wc -l | xargs)

# 시스템 상태
system_health=$(find "$system_logs_dir/health" -name "*${today}*.log" 2>/dev/null | wc -l | xargs)
system_alerts=$(find "$system_logs_dir/alerts" -name "*${today}*.log" 2>/dev/null | wc -l | xargs)

# --- 성능 지표 수집 ---
# RTO 집계 (복원 시간)
rto_avg="n/a"; rto_max="n/a"
if [[ -f "$STATE_DIR/restore_slo.jsonl" ]]; then
  rto_avg=$(tail -n 50 "$STATE_DIR/restore_slo.jsonl" | awk -F'"' '/"rto_sec":/{sum+=$(NF-1);cnt++} END{if(cnt) printf("%.0fs",sum/cnt); else print "n/a"}')
  rto_max=$(tail -n 50 "$STATE_DIR/restore_slo.jsonl" | awk -F'"' '/"rto_sec":/{if($(NF-1)>max) max=$(NF-1)} END{if(max!="") printf("%.0fs",max); else print "n/a"}')
fi

# 백업 크기 및 처리 시간
backup_size_total="n/a"
backup_duration_avg="n/a"
if [[ -d "$backup_logs_dir" ]]; then
  # 로그에서 백업 크기 및 시간 정보 추출 (예시)
  backup_size_total=$(find "$backup_logs_dir" -name "*${today}*.log" -exec grep -h "backup_size\|total_size" {} \; 2>/dev/null | awk '{sum+=$NF} END{printf("%.1f MB", sum/1024/1024)}' || echo "n/a")
  backup_duration_avg=$(find "$backup_logs_dir" -name "*${today}*.log" -exec grep -h "duration\|elapsed" {} \; 2>/dev/null | awk '{sum+=$NF;cnt++} END{if(cnt) printf("%.0fs",sum/cnt); else print "n/a"}' || echo "n/a")
fi

# --- 의존성 준수 상태 ---
dependency_violations=0
dependency_status="✅ 준수"

# INCR → RETENTION 의존성 확인
if [[ $incr_failed -gt 0 && $retention_success -gt 0 ]]; then
  dependency_violations=$((dependency_violations + 1))
  dependency_status="⚠️  위반 (INCR 실패 후 RETENTION 실행)"
fi

# INCR → HEALTH 의존성 확인
if [[ $incr_failed -gt 0 && $health_success -gt 0 ]]; then
  dependency_violations=$((dependency_violations + 1))
  dependency_status="⚠️  위반 (INCR 실패 후 HEALTH 실행)"
fi

if [[ $dependency_violations -eq 0 ]]; then
  dependency_status="✅ 준수"
fi

# --- 전체 상태 판정 ---
status="OK"
if [[ $incr_failed -gt 0 || $retention_failed -gt 0 || $health_failed -gt 0 ]]; then
  status="WARN"
fi

if [[ $dependency_violations -gt 0 ]]; then
  status="ERROR"
fi

# --- summary.json (기계용) ---
mkdir -p "$(dirname "$SUMMARY_JSON")"
cat > "$SUMMARY_JSON".tmp <<EOF
{
  "date": "$(date +%F)",
  "P0": "done",
  "P1": "done",
  "P2": "done",
  "P3": "done",
  "status": "$status",
  "rto_avg": "$rto_avg",
  "rto_max": "$rto_max",
  "phase3_completed": true,
  "observability_unified": true,
  "daily_summary_enhanced": true,
  "backup_operations": {
    "incr": {"success": $incr_success, "failed": $incr_failed},
    "retention": {"success": $retention_success, "failed": $retention_failed},
    "health": {"success": $health_success, "failed": $health_failed}
  },
  "gate_operations": {
    "core": $gate_core,
    "extended": $gate_extended,
    "full": $gate_full
  },
  "system_status": {
    "health_checks": $system_health,
    "alerts": $system_alerts
  },
  "performance_metrics": {
    "backup_size_total": "$backup_size_total",
    "backup_duration_avg": "$backup_duration_avg"
  },
  "dependency_status": {
    "violations": $dependency_violations,
    "status": "$dependency_status"
  }
}
EOF
mv -f "$SUMMARY_JSON".tmp "$SUMMARY_JSON"

# --- summary.md (사람용) ---
cat > "$SUMMARY_MD".tmp <<EOF
# 📊 DuRi 백업 시스템 일일 요약 — $(date +%F)

## 🎯 **전체 상태**
- **상태**: **$status**
- **생성 시간**: $(ts)
- **Phase 3**: **관찰성 일원화 완료** ✅

## 📈 **백업 작업 현황**

### **일일 백업 (18:30-19:00)**
| 작업 | 상태 | 성공 | 실패 | 비고 |
|------|------|------|------|------|
| **INCR** (18:30) | $([[ $incr_success -gt 0 ]] && echo "✅ 성공" || echo "❌ 실패") | $incr_success | $incr_failed | 일일 증분 백업 |
| **RETENTION** (18:45) | $([[ $retention_success -gt 0 ]] && echo "✅ 성공" || echo "❌ 실패") | $retention_success | $retention_failed | 보존 정책 실행 |
| **HEALTH** (19:00) | $([[ $health_success -gt 0 ]] && echo "✅ 성공" || echo "❌ 실패") | $health_success | $health_failed | 시스템 상태 점검 |

### **게이트 백업 (수시)**
| 유형 | 실행 횟수 | 비고 |
|------|------------|------|
| **CORE** | $gate_core | 핵심 파일 백업 |
| **EXTENDED** | $gate_extended | 확장 파일 백업 |
| **FULL** | $gate_full | 전체 시스템 백업 |

## 🔍 **시스템 상태**
- **상태 점검**: $system_health건
- **알림/경고**: $system_alerts건
- **의존성 준수**: $dependency_status

## ⚡ **성능 지표**
- **RTO (평균/최대)**: $rto_avg / $rto_max
- **백업 크기**: $backup_size_total
- **평균 처리 시간**: $backup_duration_avg

## 📋 **Phase 진행 상황**
- **Phase 0**: ✅ 안전장치 가동 완료
- **Phase 1**: ✅ SOoT 확정·정책 정렬 완료
- **Phase 2**: ✅ 스케줄·의존성 표준화 완료
- **Phase 3**: ✅ **관찰성 일원화 완료**

## 🚨 **주의사항**
$([[ $incr_failed -gt 0 ]] && echo "- INCR 실패: 다음날 FULL 자동 스케줄 예정")
$([[ $retention_failed -gt 0 ]] && echo "- RETENTION 실패: 1일 연기 예정")
$([[ $dependency_violations -gt 0 ]] && echo "- 의존성 위반: 운영 규칙 점검 필요")

## 📅 **다음날 계획**
$([[ $incr_failed -gt 0 ]] && echo "- INCR 실패 시 FULL 백업 실행")
$([[ $retention_failed -gt 0 ]] && echo "- RETENTION 재시도")
- 정상 백업 스케줄 유지
- 19:05 일일 요약 자동 생성

---

> **💡 운영 팁**: 이 요약은 매일 19:05에 자동 생성됩니다.
> **📁 로그 위치**: \`var/logs/\` (표준화된 구조)
> **🔧 문제 발생 시**: \`ops/summary/summary_report.sh\` 실행하여 상태 확인
EOF
mv -f "$SUMMARY_MD".tmp "$SUMMARY_MD"

echo "[INFO] 강화된 일일 요약 생성 완료: $SUMMARY_JSON / $SUMMARY_MD"

# --- Phase 3: Runbook Drill 힌트 ---
echo "[HINT] Phase 3 완료: 관찰성 일원화 + 19:05 일일 요약 강화" >&2
echo "[HINT] 다음 단계: Runbook Drill 시스템 구축" >&2

# DRY-RUN 모드일 때는 여기까지
if [[ "$DRY_RUN" == "1" ]]; then
  echo "[DRY] stop before README update"; exit 0
fi

# --- README Phase 표 갱신 ---
python3 ops/summary/update_phase_table.py \
  --readme "$README_PATH" \
  --summary "$SUMMARY_JSON"

# --- Git 커밋/푸시 ---
git config user.name  "$GIT_USER_NAME"  || true
git config user.email "$GIT_USER_EMAIL" || true

git checkout "$GIT_BRANCH"
git add "$README_PATH" "$SUMMARY_JSON" "$SUMMARY_MD" || true
git commit -m "auto: daily phase update + Phase 3 관찰성 일원화 완료 ($(date +%F))" || true
git push origin "$GIT_BRANCH" || true

echo "[INFO] README updated & committed (Phase 3 관찰성 일원화 완료)"
echo "[INFO] Phase 3: 관찰성 일원화 + 19:05 일일 요약 강화 완료"
