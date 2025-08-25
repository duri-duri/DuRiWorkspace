#!/usr/bin/env bash
# tests/test_apply.sh
# APPLY → VERIFY → (옵션) MISMATCH 재검증
# + 사전 프로브(P1~P4) + 안전 캡처(B1/B3) 내장
set -euo pipefail

# ──────────────────────────────────────────────────────────────
# 0) 공통 셋업
# ──────────────────────────────────────────────────────────────
ROOT="$(dirname "$(dirname "$(readlink -f "$0")")")"
APP="${ROOT}/apply.sh"
ART=".test-artifacts"
mkdir -p "$ART"

log(){ printf '[test] %s\n' "$*"; }

# 의존 도구 확인
for c in jq sha256sum rsync mktemp dd awk sed grep tr head cp rm wc tac; do
  command -v "$c" >/dev/null 2>&1 || { echo "[ERR] missing command: $c" >&2; exit 127; }
done

# 가드레일 요구 경로
USB="/mnt/usb"
HDD="/mnt/hdd"

# /mnt/hdd/ARCHIVE 기본 디렉토리 확보(쓰기 불가 시 중단)
if ! mkdir -p "${HDD}/ARCHIVE/FULL" "${HDD}/ARCHIVE/INCR" 2>/dev/null; then
  echo "[ERR] cannot create ${HDD}/ARCHIVE/* (권한/마운트 확인 필요)" >&2
  exit 90
fi

# 작업용 임시 디렉토리
TMP="$(mktemp -d -t duri-applytest-XXXXXXXX)"
trap 'rm -rf "$TMP"' EXIT

# ──────────────────────────────────────────────────────────────
# A) 사전 프로브(P1~P4) — 증거 수집
# ──────────────────────────────────────────────────────────────

# P1: 인터랙티브 여부
bash -ic 'echo FLAGS:$-; [[ $- == *i* ]] && echo I=1 || echo I=0' \
  > "${ART}/probe_P1_interactive.txt" 2>&1 || true

# P2: 프롬프트 변수/환경 초기화 파일
{
  printf 'PS1=%q\n' "${PS1-}"
  printf 'BASH_ENV=%q\n' "${BASH_ENV-<unset>}"
} > "${ART}/probe_P2_prompt_env.txt"

# P3: apply.sh 순수 출력(청정 셸) 샘플
env -i PATH="$PATH" HOME="$HOME" LC_ALL=C \
  bash --noprofile --norc -c "cd '$ROOT' && ./apply.sh --verify-only --json-summary --quiet" \
  1>"${ART}/probe_P3_raw.json" 2>"${ART}/probe_P3_raw.err" || true

# P4: ANSI/색상 코드 혼입 여부
grep -aUoP '\x1B\[[0-9;]*[A-Za-z]' "${ART}/probe_P3_raw.json" \
  > "${ART}/probe_P4_ansi.txt" 2>/dev/null || echo "NO-ANSI" > "${ART}/probe_P4_ansi.txt"

# 환경 고정 (ANSI/로케일 변동 방지)
export NO_COLOR=1
export LC_ALL=C
export LANG=C

# ──────────────────────────────────────────────────────────────
# B) 안전 캡처 유틸 (B1/B3)
# ──────────────────────────────────────────────────────────────
# B1: 완전 비인터랙티브/청정 환경으로 실행하여 stdout의 마지막 JSON만 캡처
run_json_clean () {
  # $1: 환경변수 설정 문자열 (예: "PLAN='...' USB='...' HDD='...'")
  # $2: 서브커맨드(예: "--verify-only --json-summary --quiet")
  # $3: 출력파일 경로
  local env_vars="$1" sub="$2" out="$3"
  # stdout/stderr 임시 저장(디버깅용)
  local _raw_out="${out%.json}.raw.txt"
  local _raw_err="${out%.json}.err.txt"
  env -i PATH="$PATH" HOME="$HOME" LC_ALL=C PS1= \
    bash --noprofile --norc -c "cd '$ROOT' && $env_vars $APP $sub" \
    1> "$_raw_out" 2> "$_raw_err" || true
  # 마지막 JSON 라인만 취해 저장(B2 성격 포함)
  tac "$_raw_out" | awk '/^[[:space:]]*[{[]/{print;exit}' > "$out"
  # B3: JSON 정합성 게이트
  head -c1 "$out" | grep -q '[{\[]' || { echo "[ERR] JSON-start check failed: $out" >&2; exit 70; }
  jq -e . "$out" >/dev/null || { echo "[ERR] invalid JSON: $out" >&2; exit 71; }
  # JSON 스키마(타입) 검증 게이트
  jq -e 'type=="object" and
         (.full_expected?|type=="number") and
         (.incr_expected?|type=="number") and
         (.full_ok?|type=="number") and
         (.full_bad?|type=="number") and
         (.incr_ok?|type=="number") and
         (.incr_bad?|type=="number") and
         (.rc?|type=="number")' "$out" >/dev/null \
    || { echo "[ERR] schema mismatch: $out" >&2; exit 72; }
}

# ──────────────────────────────────────────────────────────────
# 1) 샘플 파일 생성 (이름 접두사 규칙 준수: FULL__/INCR__)
# ──────────────────────────────────────────────────────────────
F="${TMP}/test/FULL__unit-full.tar.zst"
mkdir -p "$(dirname "$F")"
dd if=/dev/zero of="$F" bs=1024 count=32 status=none
HASH="$(sha256sum "$F" | awk '{print $1}')"

# dst는 가드레일 규칙: /mnt/hdd/ARCHIVE/FULL/<동일파일명>
DST_FULL="${HDD}/ARCHIVE/FULL/$(basename "$F")"

# INCR 파일도 생성 (다중 PLAN 배열 테스트)
I="${TMP}/test/INCR__unit-incr.tar.zst"
mkdir -p "$(dirname "$I")"
dd if=/dev/zero of="$I" bs=1024 count=24 status=none
HASH_INCR="$(sha256sum "$I" | awk '{print $1}')"

# PLAN(JSON array) - FULL + INCR 2항목
PLAN="${TMP}/plan.jsonl"
cat >"$PLAN" <<EOF
[{"src":"$F","sha256":"$HASH","dst":"$DST_FULL"},{"src":"$I","sha256":"$HASH_INCR","dst":"${HDD}/ARCHIVE/INCR/$(basename "$I")"}]
EOF

# ──────────────────────────────────────────────────────────────
# 2) APPLY (초기 배치) — 안전 캡처
# ──────────────────────────────────────────────────────────────
log "APPLY 단계"
# PLAN 존재성 사전 검증
test -s "$PLAN" || { echo "[ERR] PLAN missing: $PLAN"; exit 65; }
# apply.sh가 환경변수(PLAN/USB/HDD/APPLY)를 읽으므로 -c 내부에 포함
run_json_clean "PLAN='$PLAN' USB='$USB' HDD='$HDD' APPLY=1" \
               "--json-summary --quiet" \
               "${ART}/step1.json"

# ──────────────────────────────────────────────────────────────
# 3) VERIFY (정상 검증) — 안전 캡처
# ──────────────────────────────────────────────────────────────
log "VERIFY 단계(--verify-only)"
run_json_clean "PLAN='$PLAN' USB='$USB' HDD='$HDD'" \
               "--verify-only --json-summary --quiet" \
               "${ART}/step2.json"

# ──────────────────────────────────────────────────────────────
# 4) (옵션) 손상 유도 → 재검증 — 안전 캡처
#    환경변수 APPLY_EXT=1 로 활성화
# ──────────────────────────────────────────────────────────────
if [[ "${APPLY_EXT:-}" = "1" ]]; then
  log "손상 유도(DST byte flip) → 재검증(MISMATCH 기대)"
  
  # 손상 유도(DST byte flip) → 재검증
  DST_FULL="$(jq -r '.[0].dst' "$PLAN")"
  [[ -f "$DST_FULL" ]] || { echo "[ERR] DST not found: $DST_FULL" >&2; exit 1; }

  old="$(sha256sum "$DST_FULL" | awk '{print $1}')"
  sz=$(stat -c%s "$DST_FULL")
  {
    echo "DST=$DST_FULL"
    echo "SIZE=$sz"
    echo "OLD=$old"
  } > "${ART}/step3_corrupt_debug.txt"

  # A) 끝 바이트 0x01
  printf '\x01' | dd of="$DST_FULL" bs=1 seek=$((sz-1)) conv=notrunc status=none
  sync || true
  new="$(sha256sum "$DST_FULL" | awk '{print $1}')"

  # B) 여전히 동일하면 중간 바이트 0xFF
  if [[ "$old" == "$new" ]]; then
    off=$(( sz / 2 ))
    printf '\xFF' | dd of="$DST_FULL" bs=1 seek="$off" conv=notrunc status=none
    sync || true
    new="$(sha256sum "$DST_FULL" | awk '{print $1}')"
  fi

  # C) 그래도 동일하면 길이 -1
  if [[ "$old" == "$new" ]]; then
    truncate -s $((sz-1)) "$DST_FULL"
    sync || true
    new="$(sha256sum "$DST_FULL" | awk '{print $1}')"
  fi

  {
    echo "NEW=$new"
    echo "DIFF=$([[ "$old" != "$new" ]] && echo 1 || echo 0)"
  } >> "${ART}/step3_corrupt_debug.txt"

  [[ "$old" != "$new" ]] || { echo "[test] 손상 실패"; exit 1; }

  # INCR 파일도 손상 (다중 파일 손상 테스트)
  DST_INCR="$(jq -r '.[1].dst' "$PLAN")"
  [[ -f "$DST_INCR" ]] || { echo "[ERR] INCR DST not found: $DST_INCR" >&2; exit 1; }
  
  old_incr="$(sha256sum "$DST_INCR" | awk '{print $1}')"
  sz_incr=$(stat -c%s "$DST_INCR")
  
  # INCR 파일 중간 바이트를 0xEE로 덮어쓰기
  off_incr=$(( sz_incr / 3 ))
  printf '\xEE' | dd of="$DST_INCR" bs=1 seek="$off_incr" conv=notrunc status=none
  sync || true
  new_incr="$(sha256sum "$DST_INCR" | awk '{print $1}')"
  
  # INCR 손상 확인
  if [[ "$old_incr" == "$new_incr" ]]; then
    echo "[test] INCR 손상 실패"
    exit 1
  fi
  
  # 손상 성공 후 재검증 (FULL + INCR 모두 손상된 상태)
  run_json_clean "PLAN='$PLAN' USB='$USB' HDD='$HDD'" \
                 "--verify-only --json-summary --quiet" \
                 "${ART}/step3_mismatch.json"
fi

# ──────────────────────────────────────────────────────────────
# 5) 자동 판정(요약 JSON 기반: rc에만 의존하지 않음)
# ──────────────────────────────────────────────────────────────
log "판정: JSON 카운터 기반"
jq -e '(.rc==0)'              "${ART}/step1.json" >/dev/null
jq -e '(.rc==0) and ((.full_bad|tonumber)==0)' "${ART}/step2.json" >/dev/null

if [[ -f "${ART}/step3_mismatch.json" ]]; then
  # 불일치가 반드시 탐지되었는지 확인 (키가 다를 수 있어 OR)
  jq -e '((.full_bad? // 0 | tonumber) > 0) or ((.incr_bad? // 0 | tonumber) > 0)' \
     "${ART}/step3_mismatch.json" >/dev/null
fi



log "완료: ${ART}/step*.json 및 probe_* 아티팩트 확인"
