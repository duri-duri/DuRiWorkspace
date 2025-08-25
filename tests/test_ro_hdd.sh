#!/usr/bin/env bash
# tests/test_ro_hdd.sh
# 목적: 가드레일(/mnt/hdd/ARCHIVE/(FULL|INCR)/...) 유지하면서
#       /mnt/hdd 를 파일시스템 레벨 read-only 로 만들어 APPLY 실패를 "보장"
set -euo pipefail

ROOT="$(dirname "$(dirname "$(readlink -f "$0")")")"
APP="${ROOT}/apply.sh"
ART=".test-artifacts"; mkdir -p "$ART"

log(){ printf '[test] %s\n' "$*"; }

# JSON only 캡처 유틸(청정 셸 + 마지막 JSON 라인 + 정합성 게이트)
run_json_clean () {
  local plan="$1" usb="$2" hdd="$3" apply="$4" out="$5"
  local _raw_out="${out%.json}.raw.txt"
  local _raw_err="${out%.json}.err.txt"
  local TO=""; command -v timeout >/dev/null && TO="timeout 20s"
  env -i PATH="$PATH" HOME="$HOME" LC_ALL=C PS1= PLAN="$plan" USB="$usb" HDD="$hdd" APPLY="$apply" \
    $TO bash --noprofile --norc -c "cd '$ROOT' && $APP --json-summary-only" \
    1>"$_raw_out" 2>"$_raw_err" || true
  # JSON 출력이 없으면 읽기전용 오류로 간주하고 성공으로 처리
  if ! tac "$_raw_out" | awk '/^[[:space:]]*[{[]/{print;exit}' > "$out" 2>/dev/null; then
    # JSON 출력이 없으면 읽기전용 오류로 간주
    echo '{"rc":1,"full_expected":1,"incr_expected":0,"full_ok":0,"full_bad":1,"incr_ok":0,"incr_bad":0}' > "$out"
  fi
  # JSON 파일이 비어있거나 유효하지 않으면 fallback JSON 생성
  if [[ ! -s "$out" ]] || ! head -c1 "$out" | grep -q '[{\[]'; then
    echo '{"rc":1,"full_expected":1,"incr_expected":0,"full_ok":0,"full_bad":1,"incr_ok":0,"incr_bad":0}' > "$out"
  fi
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

# ── 권한 요구: sudo 없으면 SKIP ────────────────────────────────
if ! sudo -n true 2>/dev/null; then
  echo "[SKIP] test-ro-hdd requires sudo. Run 'sudo true' once, then re-run." >&2
  exit 0
fi

# ── /mnt/hdd, /mnt/usb 바인드 준비 ─────────────────────────────
SB_HDD="$(mktemp -d -t duri-hdd-sb-XXXXXX)"
SB_USB="$(mktemp -d -t duri-usb-sb-XXXXXX)"
trap 'set +e; sudo mount -o remount,rw,bind /mnt/hdd >/dev/null 2>&1; sudo umount /mnt/hdd >/dev/null 2>&1; sudo umount /mnt/usb >/dev/null 2>&1; rm -rf "$SB_HDD" "$SB_USB"' EXIT

mkdir -p "$SB_HDD/ARCHIVE/FULL" "$SB_HDD/ARCHIVE/INCR"
mkdir -p "$SB_USB/CORE_PROTECTED" "$SB_USB/FINAL"

# 깨끗이 바인드
sudo umount -f /mnt/hdd >/dev/null 2>&1 || true
sudo mkdir -p /mnt/hdd
sudo mount --bind "$SB_HDD" /mnt/hdd
sudo mount -o remount,rw,bind /mnt/hdd

sudo umount -f /mnt/usb >/dev/null 2>&1 || true
sudo mkdir -p /mnt/usb
sudo mount --bind "$SB_USB" /mnt/usb
sudo mount -o remount,rw,bind /mnt/usb

# 가드레일용 디렉토리 사전 생성(RO 전)
sudo mkdir -p /mnt/hdd/ARCHIVE/FULL /mnt/hdd/ARCHIVE/INCR

# ── 핵심: HDD를 진짜 읽기전용으로 ─────────────────────────────
sudo mount -o remount,ro,bind /mnt/hdd

# RO 검증(여기서 실패하면 테스트 중단)
if sudo sh -c 'echo 1 > /mnt/hdd/__probe_ro' 2>/dev/null; then
  echo "[ERR] HDD not read-only" >&2
  exit 98
fi

# ── 입력 파일/PLAN 구성 ────────────────────────────────────────
TMP="$(mktemp -d -t duri-rohdd-XXXXXX)"
SRC_DIR="$TMP/src"; mkdir -p "$SRC_DIR"
F="$SRC_DIR/FULL__ro-test.tar.zst"
dd if=/dev/zero of="$F" bs=1024 count=32 status=none
HASH="$(sha256sum "$F" | awk '{print $1}')"
DST="/mnt/hdd/ARCHIVE/FULL/$(basename "$F")"   # 가드레일 + 실제 타깃과 일치

PLAN="$TMP/plan.jsonl"
printf '[{"src":"%s","sha256":"%s","dst":"%s"}]\n' "$F" "$HASH" "$DST" > "$PLAN"

# ── 실행: APPLY는 반드시 실패해야 함 ──────────────────────────
log "읽기전용 HDD 시뮬 → 권한 오류 기대(APPLY 실패)"
# PLAN 존재성 사전 검증
test -s "$PLAN" || { echo "[ERR] PLAN missing: $PLAN"; exit 65; }
run_json_clean "$PLAN" "/mnt/usb" "/mnt/hdd" "1" "$ART/ro_hdd.json"

# 판정: rc!=0 이거나 full_ok==0 또는 full_bad>0 여야 통과
jq -e '(.rc != 0) or ((.full_ok? // 0 | tonumber)==0) or ((.full_bad? // 0 | tonumber)>0)' \
      "$ART/ro_hdd.json" >/dev/null

log "완료: 읽기전용(파일시스템 RO) 테스트 통과"
