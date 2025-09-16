#!/usr/bin/env bash
set -euo pipefail
umask 077

# portable tac (macOS/BSD 대비)
if ! command -v tac >/dev/null 2>&1; then
  tac() { tail -r "$@"; }
fi

# paths
SCRIPT="$(readlink -f "${BASH_SOURCE[0]}")"
ROOT="$(dirname "$(dirname "$SCRIPT")")"
APP="$ROOT/apply.sh"
ART="$ROOT/.test-artifacts"
mkdir -p "$ART"

: "${HDD:=/mnt/hdd}"
: "${USB:=/mnt/usb}"
: "${P2_TIMEOUT:=20s}"

# run_json_clean (간결 버전)
run_json_clean() {
  local sub="$1"; local out="$2"
  local raw="${out%.json}.raw.txt"; local err="${out%.json}.err.txt"
  local TO=""
  if command -v timeout >/dev/null 2>&1; then
    TO="timeout ${P2_TIMEOUT}"
  fi
  env -i PATH="$PATH" HOME="$HOME" LC_ALL=C PS1= \
    $TO bash --noprofile --norc -c "cd '$ROOT' && '$APP' $sub --json-summary-only" \
    >"$raw" 2>"$err" || true
  awk '/^[[:space:]]*[{[]/ {print; exit}' "$raw" >"$out" || true
  if ! grep -q '^[[:space:]]*[{[]' "$out" 2>/dev/null; then
    awk '/^[[:space:]]*[{[]/ {print; exit}' "$err" >"$out" || true
  fi
  if ! grep -q '^[[:space:]]*[{[]' "$out" 2>/dev/null; then
    echo "[ERR] JSON-start fail: $out" >&2
    return 70
  fi
}

echo "[test] 읽기전용 HDD 시뮬 → 권한 오류 기대(APPLY 실패)"

# sudo 필요시 스킵
if ! sudo -n true 2>/dev/null; then
  echo "[SKIP] sudo 권한 없음 — RO HDD 테스트 건너뜀"
  exit 0
fi

# 샌드박스 바인드 마운트
SB_HDD="$(mktemp -d -t duri-hdd-sb-XXXXXX)"
SB_USB="$(mktemp -d -t duri-usb-sb-XXXXXX)"
trap 'set +e; sudo mount -o remount,rw,bind "$HDD" >/dev/null 2>&1; sudo umount "$HDD" >/dev/null 2>&1; sudo umount "$USB" >/dev/null 2>&1; rm -rf "$SB_HDD" "$SB_USB"' EXIT

mkdir -p "$SB_HDD/ARCHIVE/FULL" "$SB_HDD/ARCHIVE/INCR"
mkdir -p "$SB_USB/CORE_PROTECTED" "$SB_USB/FINAL"

sudo umount -f "$HDD" >/dev/null 2>&1 || true
sudo mkdir -p "$HDD"
sudo mount --bind "$SB_HDD" "$HDD"
sudo mount -o remount,rw,bind "$HDD"

sudo umount -f "$USB" >/dev/null 2>&1 || true
sudo mkdir -p "$USB"
sudo mount --bind "$SB_USB" "$USB"
sudo mount -o remount,rw,bind "$USB"

# 대상 디렉토리 구성 후 HDD를 RO로 전환
sudo mkdir -p "$HDD/ARCHIVE/FULL" "$HDD/ARCHIVE/INCR" || true
sudo mount -o remount,ro,bind "$HDD"

# RO 검증(실패해야 정상)
if sudo sh -c "echo 1 > '$HDD/__probe_ro'" 2>/dev/null; then
  echo "[ERR] RO remount 실패로 보임 — 테스트 중단"
  exit 65
fi

# PLAN 생성
TMPD="$(mktemp -d -t duri-rohdd-XXXXXX)"
SRC_DIR="$TMPD/src"; mkdir -p "$SRC_DIR"
F="$SRC_DIR/FULL__ro-test.tar.zst"
dd if=/dev/zero of="$F" bs=1024 count=32 status=none
HASH="$(sha256sum "$F" | awk '{print $1}')"
DST="$HDD/ARCHIVE/FULL/FULL__ro-test.tar.zst"
PLAN="$TMPD/plan.jsonl"
printf '[{"src":"%s","sha256":"%s","dst":"%s"}]\n' "$F" "$HASH" "$DST" > "$PLAN"

# 실행 (APPLY는 RO로 인해 실패 성격의 요약이 와야 함)
OUT="$ART/ro_hdd.json"
run_json_clean "PLAN='$PLAN' USB='$USB' HDD='$HDD' APPLY=1" "$OUT" || true

# 판정: rc!=0 또는 full_ok==0 또는 full_bad>0 이면 "테스트 통과"
if jq -e '(.rc != 0) or ((.full_ok? // 0 | tonumber)==0) or ((.full_bad? // 0 | tonumber)>0)' "$OUT" >/dev/null; then
  echo "[test] 완료: 읽기전용(파일시스템 RO) 테스트 통과"
else
  echo "[ERR] 읽기전용 테스트가 실패 패턴을 포착하지 못함"
  exit 71
fi
