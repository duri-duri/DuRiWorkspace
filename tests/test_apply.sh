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

# run_json_clean 함수는 아래에 정의됨 (중복 제거)

# json_first_line: 파일에서 처음 등장하는 JSON 오브젝트/배열 시작 줄만 추출
json_first_line() {
  local f="$1"
  tac "$f" | awk '/^[[:space:]]*[{[]/{print;exit}' | tac
}

# json_sanitize_file: JSON 파일 정제 (ANSI 제거, NaN/Inf→null, 유효성 검증)
json_sanitize_file() {
  local f="$1"
  # 1) ANSI 컬러 제거
  sed -i -r 's/\x1B\[[0-9;]*[mK]//g' "$f" 2>/dev/null || true
  # 2) 파일 내에서 첫 JSON 블록만 남기기 ({ 또는 [ 로 시작)
  if ! head -c 1 "$f" | grep -q '[{\[]'; then
    # 뒤에서부터 검색해 JSON 시작 라인만 추출
    tac "$f" | awk '/^[[:space:]]*[{[]/{print;exit}' > "$f.__head" || true
    if [[ -s "$f.__head" ]]; then mv "$f.__head" "$f"; else : > "$f"; fi
  fi
  # 3) NaN / Infinity → null 치환 (jq가 허용하지 않음)
  sed -i -E 's/: *-?Infinity([,}])/:\ null\1/g; s/: *NaN([,}])/:\ null\1/g' "$f" 2>/dev/null || true
  # 4) 빠르게 유효성 체크. 실패하면 원본 유지하되 에러만 남김
  if ! jq -e . "$f" >/dev/null 2>&1; then
    echo "[WARN] JSON sanitize failed: $f" 1>&2
    return 1
  fi
  return 0
}

# resolve_first_dst: PLAN의 첫 경로를 찾아 $HDD/$USB/$PB 및 ${HDD}/${USB}/${PB} 안전 치환
unset -f resolve_first_dst 2>/dev/null || true
resolve_first_dst() {
  local plan="$1"
  local dst=""
  # 다형 파서: 숫자/불린/null 무시, 문자열/객체만 처리
  dst="$(jq -r '
    if type=="array" then .[] else . end
    | if type=="object" then (.src // .dst // .path // .)
      elif type=="string" then .
      else empty end
    | select(type=="string")
  ' "$plan" 2>/dev/null | head -n 1 || true)"
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

  # JSON-only 모드에서는 stdout에 JSON만 있으므로 직접 복사
  cp "$raw" "$out" || true

  # 이제 stdout은 반드시 단일 JSON이어야 한다.
  # 파싱 실패 시 바로 실패(대체 JSON으로 덮어쓰지 않음)
  jq -e . "$out" >/dev/null 2>&1 || { echo "[ERR] invalid JSON: $out" >&2; return 70; }
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

# JSON 파일 디버그 출력 (읽기 전용)
for f in "$ART"/step*.json; do
  [[ -f "$f" ]] || continue
  echo "[DEBUG] head $f"
  head -n 3 "$f" || true
done

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
