#!/usr/bin/env bash
# L4 주간 요약 후처리: Score 기반 자동 판정 + 인간 행동 가이드 주석 + (옵션) 관찰 루프 자동 중단
# - 원본 파이프라인/임계값/프로덕션 설정을 변경하지 않음 (기본 읽기 전용)
# - decision 및 권고사항은 var/audit/recommendations.log 로 남김
# - summary 파일을 직접 찾아 append (요약 스크립트 내부 구현에 의존하지 않음)

set -euo pipefail

# 리포지토리 루트 결정: git 최상위 → 폴백(/home/duri/DuRiWorkspace)
ROOT="$(git rev-parse --show-toplevel 2>/dev/null || true)"
if [[ -z "${ROOT}" || ! -d "${ROOT}/.git" ]]; then
  ROOT="/home/duri/DuRiWorkspace"
fi
AUDIT_DIR="${ROOT}/var/audit"
LOG_DIR="${AUDIT_DIR}/logs"
RECO_FILE="${AUDIT_DIR}/recommendations.log"
mkdir -p "${LOG_DIR}"
touch "${RECO_FILE}"

# summary 자동 탐색(최신 weekly_*.log) – 없으면 no-op 종료
summary="${summary:-}"
if [[ -z "${summary:-}" ]]; then
  summary="$(ls -1t "${LOG_DIR}"/weekly_*.log 2>/dev/null | head -1 || true)"
fi
[[ -z "${summary}" ]] && { echo "[skip] no weekly summary found" | tee -a "${RECO_FILE}"; exit 0; }

# 머신리더블 NDJSON/JSON 산출 경로
DECISIONS_NDJSON="${AUDIT_DIR}/decisions.ndjson"
DECISIONS_DIR="${AUDIT_DIR}/decisions"
mkdir -p "${DECISIONS_DIR}"

# 이미 가이드가 붙어 있으면 중복 방지
if grep -q "^=== Human Action Guide ===" "$summary" 2>/dev/null; then
  echo "[skip] guide already present in: $summary" >> "$RECO_FILE"
  # 중복이어도 머신리더블 레코드는 남긴다(운영 대시보드 일관성)
  :
fi

# Score 확보: (1) 환경변수 score, (2) summary에서 파싱, (3) 없으면 0.00
score_str="${score:-}"
if [[ -z "$score_str" ]]; then
  score_str="$(awk -F': *' '/^Score/ {print $2; exit}' "$summary" 2>/dev/null || true)"
fi
if [[ -z "$score_str" ]]; then
  score_str="0.00"
fi

# 실수 비교 유틸(awk 기반)
ge() { awk -v a="$1" -v b="$2" 'BEGIN{exit !(a>=b)}'; }
lt() { awk -v a="$1" -v b="$2" 'BEGIN{exit !(a<b)}'; }

decision="CONTINUE"
action_note=""

if ge "$score_str" "0.92"; then
  decision="APPROVED"
  action_note=$'# ✅ Score ≥ 0.92 → Global L4 운영 승인\n# 다음 단계:\n# 1) 정책 학습 PR 확인 (필요 시 다음 주기 merge 준비)\n# 2) rollback_label.tsv 최신화 여부 점검\n# 3) L5(상위 기준) 준비 항목 사전 점검'
elif ge "$score_str" "0.85"; then
  decision="CONTINUE"
  action_note=$'# ⚠️ Score 0.85~0.92 → 관찰 연장\n# 다음 단계:\n# 1) rollback_label.tsv TP/FP 누락 여부 확인\n# 2) policy:update-proposed PR 내용 검토(merge 금지)\n# 3) 다음 주 Score 변동 원인 기록(스파이크/데이터 공백 등)'
else
  decision="REVIEW"
  action_note=$'# ❌ Score < 0.85 → 임계값/정책 재검토 권고\n# 다음 단계:\n# 1) var/audit/logs/* 주요 실패 구간 점검\n# 2) rollback_label.tsv 라벨 누락 확인\n# 3) 임계값·정책 후보 도출(제안 리포트 준비)'
fi

# Summary에 주석(인간 행동 가이드)와 자동판정 기록 append
{
  echo ""
  echo "=== Human Action Guide ==="
  printf "%s\n" "$action_note"
  echo "# --- 자동 생성: L4 weekly post-decision module"
  echo ""
  echo "[AUTO] Decision: $decision"
  echo "[AUTO] Score   : $score_str"
} >> "$summary"

# 권고 로그 파일에 머신 판정 및 권고사항 기록
{
  echo "=== $(date +'%F %T %Z') L4 Weekly Decision ==="
  echo "summary=$summary"
  echo "score=$score_str"
  echo "decision=$decision"
  case "$decision" in
    "APPROVED")
      echo "recommendation=keep_cycle"
      echo "note=다음 주기로 자동 유지; 정책 PR은 필요 시만 수동 merge"
      ;;
    "CONTINUE")
      echo "recommendation=extend_observation"
      echo "note=관찰 연장; rollback 라벨과 정책 PR 검토 강화"
      ;;
    "REVIEW")
      echo "recommendation=stop_and_review"
      echo "note=관찰 중단 권고; 임계값/정책 재검토"
      ;;
  esac
  echo ""
} >> "$RECO_FILE"

# (옵션) REVIEW 시 관찰 루프 자동 중단 — 명시적 opt-in
AUTO_SUSPEND_ON_REVIEW="${AUTO_SUSPEND_ON_REVIEW:-0}"
if [[ "$decision" == "REVIEW" && "$AUTO_SUSPEND_ON_REVIEW" == "1" ]]; then
  {
    echo "[AUTO] REVIEW → l4-daily.timer 비활성화 시도 (user systemd)"
    systemctl --user disable --now l4-daily.timer || true
    echo "[AUTO] REVIEW → l4-weekly.timer 유지 (다음 실행에서 재평가 가능)"
  } >> "$summary" 2>&1
fi

exit 0

