#!/usr/bin/env bash
set -euo pipefail
: "${ART:=.test-artifacts}"
: "${DST_DEBUG:=0}"

mkdir -p "$ART"

# P2 튜닝 변수 (기본값)
P2_RACE_MB="${P2_RACE_MB:-1}"
P2_CRASH_MB="${P2_CRASH_MB:-1}"
P2_TIMEOUT="${P2_TIMEOUT:-20s}"

# TMP 작업 디렉터리 (일부 케이스에서 사용)
if ! command -v timeout >/dev/null 2>&1; then
  # timeout 없으면 no-timeout 모드로 동작 (CI/로컬 환경 호환성)
  _TIMEOUT_PREFIX=()
else
  _TIMEOUT_PREFIX=(timeout "$P2_TIMEOUT")
fi

TMP="${TMP:-}"
if [[ -z "${TMP}" ]]; then
  TMP="$(mktemp -d -t duri-p2-XXXXXX)"
fi
trap 'set +e; rm -rf "$TMP"' EXIT

# 유틸: 파일시스템 플러시(레이스/크래시 직후 안전한 합성 위해 약간의 간격)
fs_flush() {
  sync; (command -v syncfs >/dev/null 2>&1 && syncfs) || true
}

# resolve_first_dst: PLAN에서 첫 항목 dst를 추출하고 $HDD/$USB/$PB만 확장
# - JSON array와 JSONL 모두 지원
# - 치환 범위는 환경변수 HDD/USB/PB로 한정(보안/예측가능성)
resolve_first_dst() {
  local _p="${1:-}"
  local _raw=""
  [[ -n "$_p" && -s "$_p" ]] || { echo ""; return 0; }

  # 1) array JSON 시도
  _raw="$(jq -er '.[0].dst' "$_p" 2>/dev/null || true)"
  if [[ -z "$_raw" || "$_raw" == "null" ]]; then
    # 2) JSONL (첫 줄)
    _raw="$(head -n1 "$_p" | jq -er '.dst' 2>/dev/null || true)"
  fi

  # 환경변수만 안전 치환
  local _expanded
  _expanded="$(
    printf '%s' "$_raw" \
    | sed -e "s|\${HDD}|$HDD|g" -e "s|\$HDD|$HDD|g" \
          -e "s|\${USB}|$USB|g" -e "s|\$USB|$USB|g" \
          -e "s|\${PB}|$PB|g"   -e "s|\$PB|$PB|g"
  )"
  [[ "$DST_DEBUG" == "1" ]] && echo "[DBG] resolved dst: $_expanded" 1>&2
  printf '%s' "$_expanded"
}

# ──────────────────────────────────────────────────────────────────────────────
# 단일 run_json_clean: (sub_cmd, out_json)
#  - sub_cmd: apply.sh에 넘길 "ENV… ARG…" 문자열(예: "PLAN='…' APPLY=1 --verify-only")
#  - out_json: 결과 JSON 파일 경로
#   * stdout/stderr RAW를 .raw.txt/.err.txt 로 남기고 끝줄에서 JSON 라인만 추출
# ──────────────────────────────────────────────────────────────────────────────
run_json_clean() {
  local sub="${1:?sub_cmd required}"
  local out="${2:?out_json required}"
  local raw="${out%.json}.raw.txt"
  local err="${out%.json}.err.txt"

  # 깨끗한 환경에서 실행 + timeout
  env -i PATH="$PATH" HOME="$HOME" LC_ALL=C PS1= \
    "${_TIMEOUT_PREFIX[@]}" \
    bash --noprofile --norc -c "cd '$ROOT' && '$APP' $sub --json-summary-only" \
    >"$raw" 2>"$err" || true

  # RAW에서 첫 번째 JSON 라인 추출
  : >"$out"
  if [[ -s "$raw" ]]; then
    tac "$raw" | awk '/^[[:space:]]*[{[]/{print; exit}' >"$out" || true
  fi
  if [[ ! -s "$out" && -s "$err" ]]; then
    tac "$err" | awk '/^[[:space:]]*[{[]/{print; exit}' >"$out" || true
  fi

  # JSON 유효성
  if ! jq -e . "$out" >/dev/null 2>&1; then
    echo "[ERR] invalid JSON: $out"
    return 71
  fi
}

# ──────────────────────────────────────────────────────────────────────────────
# 기본/확장 테스트 본문
# ──────────────────────────────────────────────────────────────────────────────

# 가드레일 요구 경로
HDD="${HDD:-/mnt/hdd}"
USB="${USB:-/mnt/usb}"
PLAN="${PLAN:-$ROOT/PLAN.jsonl}"

# PLAN 존재성 선확인
if [[ ! -s "$PLAN" ]]; then
  echo "[ERR] PLAN not found or empty: $PLAN" >&2
  exit 66
fi

echo "[test] APPLY 단계"
run_json_clean "PLAN='$PLAN' USB='$USB' HDD='$HDD' APPLY=1" "$ART/step1.json"

echo "[test] VERIFY 단계(--verify-only)"
run_json_clean "PLAN='$PLAN' USB='$USB' HDD='$HDD' --verify-only" "$ART/step2.json"

echo "[test] 판정: JSON 카운터 기반"
jq -e '(.rc|tonumber)==0' "$ART/step1.json" >/dev/null
jq -e '(.rc|tonumber)==0 and ((.full_bad? // 0 | tonumber)==0)' "$ART/step2.json" >/dev/null

echo "[test] 완료: .test-artifacts/step*.json 및 probe_* 아티팩트 확인"

# ──────────────────────────────────────────────────────────────────────────────
# Phase-2 추가 케이스 (RUN_EXTRA_CASES=1 시)
# ──────────────────────────────────────────────────────────────────────────────
if [[ "${RUN_EXTRA_CASES:-0}" == "1" ]]; then
  echo "[test] P2/race: same dst concurrent apply"
  # 동일 PLAN으로 2개 동시 실행 → 원자성/레이스 간접 확인
  (
    run_json_clean "PLAN='$PLAN' USB='$USB' HDD='$HDD' APPLY=1" "$ART/race.a.json" &
    run_json_clean "PLAN='$PLAN' USB='$USB' HDD='$HDD' APPLY=1" "$ART/race.b.json" &
    wait
    fs_flush
    jq -e '(.rc|tonumber)==0' "$ART/race.a.json" >/dev/null
    jq -e '(.rc|tonumber)==0' "$ART/race.b.json" >/dev/null
    echo "[test] P2/race OK"
  )

  echo "[test] P2/crash: timeout kill then re-apply"
  (
    # (1) 짧은 타임아웃으로 강제 중단
    local_to="${P2_TIMEOUT_LOCAL:-1s}"
    env -i PATH="$PATH" HOME="$HOME" LC_ALL=C PS1= \
      timeout "$local_to" \
      bash --noprofile --norc -c "cd '$ROOT' && '$APP' PLAN='$PLAN' USB='$USB' HDD='$HDD' APPLY=1 --json-summary-only" \
      >"$ART/crash.raw.txt" 2>"$ART/crash.err.txt" || true
    fs_flush
    # (2) 재적용은 정상완료되어야 함
    run_json_clean "PLAN='$PLAN' USB='$USB' HDD='$HDD' APPLY=1" "$ART/crash.reapply.json"
    jq -e '(.rc|tonumber)==0' "$ART/crash.reapply.json" >/dev/null
    echo "[test] P2/crash OK"
  )

  echo "[test] P2/matrix: GOLD tamper -> verify fail"
  (
    # 1) 대상 파일 생성은 상단 APPLY에서 이미 수행됨
    # 2) PLAN의 첫 dst를 해석(변수 확장)
    _first_dst="$(resolve_first_dst "$PLAN")"
    if [[ -n "${_first_dst:-}" && -f "$_first_dst" ]]; then
      # 3) 한 바이트 변조
      dd if=/dev/zero of="$_first_dst" bs=1 count=1 seek=0 conv=notrunc status=none || true
      fs_flush
      # 4) verify-only는 실패 신호(full_bad>0 또는 rc!=0)여야 함
      run_json_clean "PLAN='$PLAN' USB='$USB' HDD='$HDD' --verify-only" "$ART/matrix.verify.json"
      jq -e '(.rc != 0) or ((.full_bad? // 0 | tonumber) > 0)' "$ART/matrix.verify.json" >/dev/null
      echo "[test] P2/matrix OK (tamper detected)"
    else
      echo "[WARN] P2/matrix: dst 추출 실패 또는 파일 미존재 — 스킵"
    fi
  )
fi

exit 0
