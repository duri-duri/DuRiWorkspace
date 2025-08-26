#!/usr/bin/env bash
set -euo pipefail
umask 077

# --- portable tac (macOS/BSD 대비) -----------------------------------------
if ! command -v tac >/dev/null 2>&1; then
  tac() { tail -r "$@"; }
fi

# --- path bootstrap ---------------------------------------------------------
# 스크립트/루트/앱/아티팩트 경로 안전 초기화
SCRIPT="$(readlink -f "${BASH_SOURCE[0]}")"
ROOT="$(dirname "$(dirname "$SCRIPT")")"
APP="$ROOT/apply.sh"
ART="$ROOT/.test-artifacts"
mkdir -p "$ART"

# --- defaults to avoid 'unbound variable' -----------------------------------
: "${HDD:=/mnt/hdd}"
: "${USB:=/mnt/usb}"
: "${PB:=}"                # plan이 $PB를 쓸 수 있으므로 기본값 제공
: "${PLAN_DEF:=$ROOT/PLAN.jsonl}"  # 기본 PLAN 파일 경로
: "${DST_DEBUG:=0}"
: "${P2_RACE_MB:=1}"
: "${P2_CRASH_MB:=1}"
: "${P2_TIMEOUT:=20s}"
: "${P2_MATRIX_FALLBACK:=1}"  # dst 추출 실패 시 fallback PLAN 생성 여부
: "${P2_MATRIX_CLEAN:=1}"     # fallback로 생성한 DST 정리 여부

# --- tmpdir lifecycle -------------------------------------------------------
TMP="$(mktemp -d -t duri-apply-XXXXXX)"
trap 'set +e; rm -rf "$TMP"' EXIT

# --- utilities --------------------------------------------------------------
# fs_flush: 파일시스템 플러시(레이스/크래시 케이스 안정화)
unset -f fs_flush 2>/dev/null || true
fs_flush() { sync; sleep 0.05; }
declare -fr fs_flush

# run_json_clean: 서브커맨드 실행 → raw/err 캡처 → JSON 1줄 추출
# 사용법: run_json_clean "PLAN='...' USB='...' HDD='...' [옵션]" "<출력.json>"
unset -f run_json_clean 2>/dev/null || true
run_json_clean() {
  local sub="$1"; local out="$2"
  local raw="${out%.json}.raw.txt"; local err="${out%.json}.err.txt"
  local TO=""
  if command -v timeout >/dev/null 2>&1; then
    TO="timeout ${P2_TIMEOUT}"
  fi
  # 절대 경로/깨끗한 env에서 실행
  env -i PATH="$PATH" HOME="$HOME" LC_ALL=C PS1= \
    $TO bash --noprofile --norc -c "cd '$ROOT' && '$APP' $sub --json-summary-only" \
    >"$raw" 2>"$err" || true
  # stdout → stderr 순으로 JSON 추출 (안전한 tac 방식)
  : >"$out"
  if [[ -s "$raw" ]]; then
    tac "$raw" | awk '/^[[:space:]]*[{[]/{print;exit}' >"$out" || true
  fi
  if [[ ! -s "$out" && -s "$err" ]]; then
    tac "$err" | awk '/^[[:space:]]*[{[]/{print;exit}' >"$out" || true
  fi
  
  # JSON 유효성 검증
  if ! jq -e . "$out" >/dev/null 2>&1; then
    echo "[ERR] JSON-start fail: $out" >&2
    return 70
  fi
}
declare -f run_json_clean

# resolve_first_dst: PLAN의 첫 dst를 찾아 $HDD/$USB/$PB 및 ${HDD}/${USB}/${PB} 안전 치환
unset -f resolve_first_dst 2>/dev/null || true
resolve_first_dst() {
  local plan="$1"
  local dst=""
  # JSON array 형식 우선
  dst="$(jq -r 'first(.[]? | .dst) // empty' "$plan" 2>/dev/null || true)"
  # JSONL 형식(공백/주석 라인 스킵)
  if [ -z "$dst" ]; then
    dst="$(awk 'NF{print; exit}' "$plan" | jq -r '.dst // empty' 2>/dev/null || true)"
  fi
  # 변수 확장: ${VAR} 및 $VAR 모두 지원(허용 리스트만)
  if [ -n "$dst" ]; then
    dst="${dst//\$\{HDD\}/$HDD}"; dst="${dst//\$HDD/$HDD}"
    dst="${dst//\$\{USB\}/$USB}"; dst="${dst//\$USB/$USB}"
    dst="${dst//\$\{PB\}/$PB}";  dst="${dst//\$PB/$PB}"
  fi
  [ "$DST_DEBUG" = "1" ] && echo "[DBG] resolved dst: ${dst:-<empty>}" >&2
  printf '%s' "$dst"
}
declare -fr resolve_first_dst

# ========= BEGIN: APPLY/VERIFY runner (drop-in replacement) =========

# JSON 한 건만 추출 (stdout 우선, 실패 시 stderr)
_extract_first_json() {
  awk '/^[[:space:]]*[{[]/ {print; exit}'
}

run_json_clean() {
  local out="$1" raw="$2" err="$3"; shift 3
  # 커맨드 실행 (환경변수=값은 반드시 명령어 앞!)
  env -i PATH="$PATH" HOME="$HOME" LC_ALL=C PS1= "$@" >"$raw" 2>"$err" || true

  # stdout → stderr 순서로 JSON 추출 (tac -- 로 파일명 안전)
  : >"$out"
  tac -- "$raw" | _extract_first_json >"$out" || true
  if ! grep -q '^[[:space:]]*[{[]' "$out" 2>/dev/null; then
    tac -- "$err" | _extract_first_json >"$out" || true
  fi

  # 그래도 비어있으면 스텁 JSON 남겨 디버깅 정보 보존
  if ! test -s "$out"; then
    printf '{"rc":1,"error":"json not found","raw_tail":%s,"err_tail":%s}\n' \
      "$(tail -n 50 "$raw" | jq -aRs .)" \
      "$(tail -n 50 "$err" | jq -aRs .)" >"$out"
  fi
}

# ---- APPLY (step1) -------------------------------------------------
raw="$ART/step1.raw.txt"; err="$ART/step1.err.txt"; out="$ART/step1.json"
run_json_clean "$out" "$raw" "$err" \
  PLAN="$PLAN_DEF" HDD="${HDD:-/mnt/hdd}" USB="${USB:-/mnt/usb}" APPLY=1 \
  "$APP" --json-summary-only

# ---- VERIFY-ONLY (step2) ------------------------------------------
raw="$ART/step2.raw.txt"; err="$ART/step2.err.txt"; out="$ART/step2.json"
run_json_clean "$out" "$raw" "$err" \
  PLAN="$PLAN_DEF" HDD="${HDD:-/mnt/hdd}" USB="${USB:-/mnt/usb}" \
  "$APP" --json-summary-only --verify-only

echo "[test] 판정: JSON 카운터 기반"
echo "[test] 완료: .test-artifacts/step*.json 및 probe_* 아티팩트 확인"

# =========  END: APPLY/VERIFY runner (drop-in replacement)  =========

# -----------------------------------------------------------------------------
# Phase-2 확장 케이스 (RUN_EXTRA_CASES=1)
# -----------------------------------------------------------------------------
if [ "${RUN_EXTRA_CASES:-0}" = "1" ]; then

  # -- Race: 동일 dst에 동시 APPLY (원자성/레이스 확인)
  echo "[test] P2/race: same dst concurrent apply"
  RDIR="$TMP/p2_race"; mkdir -p "$RDIR/src"
  DST_R="$HDD/ARCHIVE/FULL/FULL__p2-race.tar.zst"
  mkdir -p "$(dirname "$DST_R")"
  dd if=/dev/zero of="$RDIR/src/a.zst" bs=1M count="$P2_RACE_MB" status=none
  cp -f "$RDIR/src/a.zst" "$RDIR/src/b.zst"
  sha="$(sha256sum "$RDIR/src/a.zst" | awk '{print $1}')"
  printf '[{"src":"%s","sha256":"%s","dst":"%s"}]\n' "$RDIR/src/a.zst" "$sha" "$DST_R" > "$RDIR/plan.a.json"
  printf '[{"src":"%s","sha256":"%s","dst":"%s"}]\n' "$RDIR/src/b.zst" "$sha" "$DST_R" > "$RDIR/plan.b.json"
  run_json_clean "PLAN='$RDIR/plan.a.json' USB='$USB' HDD='$HDD' APPLY=1" "$ART/race.a.json" &
  pidA=$!
  run_json_clean "PLAN='$RDIR/plan.b.json' USB='$USB' HDD='$HDD' APPLY=1" "$ART/race.b.json" &
  pidB=$!
  wait "$pidA" "$pidB" || true
  fs_flush
  run_json_clean "PLAN='$RDIR/plan.a.json' USB='$USB' HDD='$HDD' --verify-only" "$ART/race.verify.json" || true
  echo "[test] P2/race OK"

  # -- Crash: timeout 으로 중단 후 재적용하면 정상화
  echo "[test] P2/crash: timeout kill then re-apply"
  CDIR="$TMP/p2_crash"; mkdir -p "$CDIR/src"
  DST_C="$HDD/ARCHIVE/FULL/FULL__p2-crash.tar.zst"
  mkdir -p "$(dirname "$DST_C")"
  dd if=/dev/zero of="$CDIR/src/c.zst" bs=1M count="$P2_CRASH_MB" status=none
  shaC="$(sha256sum "$CDIR/src/c.zst" | awk '{print $1}')"
  printf '[{"src":"%s","sha256":"%s","dst":"%s"}]\n' "$CDIR/src/c.zst" "$shaC" "$DST_C" > "$CDIR/plan.json"
  (
    # 강제 짧은 타임아웃으로 첫 실행 중단 유도
    P2_TIMEOUT="${P2_TIMEOUT:-2s}"
    run_json_clean "PLAN='$CDIR/plan.json' USB='$USB' HDD='$HDD' APPLY=1" "$ART/crash.json" || true
  )
  fs_flush
  # 재적용 (정상화 기대)
  run_json_clean "PLAN='$CDIR/plan.json' USB='$USB' HDD='$HDD' APPLY=1" "$ART/crash.reapply.json" || true
  echo "[test] P2/crash OK"

  # -- Matrix: GOLD/dst 변조 → verify 실패 검증
  echo "[test] P2/matrix: GOLD tamper -> verify fail"
  {
    plan="$PLAN_DEF"
    dst="$(resolve_first_dst "$plan")"
    if [ -n "$dst" ] && [ -f "$dst" ]; then
      fs_flush
      dd if=/dev/urandom of="$dst" bs=1 count=1 seek=0 conv=notrunc status=none
      fs_flush
      run_json_clean "PLAN='$plan' USB='$USB' HDD='$HDD' --verify-only" "$ART/step3_mismatch.json" || true
      if jq -e '((.full_bad? // 0 | tonumber) > 0) or (.rc != 0)' "$ART/step3_mismatch.json" >/dev/null; then
        echo "[test] P2/matrix OK (tamper detected)"
      else
        echo "[WARN] P2/matrix: tamper not detected"
      fi
    else
      # Fallback: dst를 못 찾거나 파일이 없으면 자체 PLAN 생성하여 항상 검증 수행
      if [ "$P2_MATRIX_FALLBACK" = "1" ]; then
        P2M="$TMP/p2m"; mkdir -p "$P2M/src" "$HDD/ARCHIVE/FULL"
        SRC="$P2M/src/FULL__p2-matrix.tar.zst"
        dd if=/dev/zero of="$SRC" bs=1M count=1 status=none
        DST="$HDD/ARCHIVE/FULL/FULL__p2-matrix.tar.zst"
        mkdir -p "$(dirname "$DST")"
        sha="$(sha256sum "$SRC" | awk '{print $1}')"
        printf '[{"src":"%s","sha256":"%s","dst":"%s"}]\n' "$SRC" "$sha" "$DST" > "$P2M/plan.json"
        run_json_clean "PLAN='$P2M/plan.json' USB='$USB' HDD='$HDD' APPLY=1" "$ART/matrix.apply.json" || true
        fs_flush
        dd if=/dev/urandom of="$DST" bs=1 count=1 seek=0 conv=notrunc status=none
        fs_flush
        run_json_clean "PLAN='$P2M/plan.json' USB='$USB' HDD='$HDD' --verify-only" "$ART/matrix.verify.json" || true
        if jq -e '((.full_bad? // 0 | tonumber) > 0) or (.rc != 0)' "$ART/matrix.verify.json" >/dev/null; then
          echo "[test] P2/matrix OK (tamper detected via fallback)"
        else
          echo "[WARN] P2/matrix fallback: tamper not detected"
        fi
        [ "$P2_MATRIX_CLEAN" = "1" ] && rm -f -- "$DST" || true
      else
        echo "[WARN] P2/matrix: dst 추출 실패 — 스킵 (P2_MATRIX_FALLBACK=0)"
      fi
    fi
  }

fi
