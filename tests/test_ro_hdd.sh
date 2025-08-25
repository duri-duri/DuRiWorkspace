#!/usr/bin/env bash
# tests/test_ro_hdd.sh
# 목적: 가드레일(/mnt/hdd/ARCHIVE/(FULL|INCR)/...) 유지하면서
#       /mnt/hdd 를 파일시스템 레벨 read-only 로 만들어 APPLY 실패를 "보장"
set -euo pipefail
## micro-stability
export LC_ALL=${LC_ALL:-C.UTF-8}
export LANG=${LANG:-C.UTF-8}
umask 022

ROOT="$(dirname "$(dirname "$(readlink -f "$0")")")"
APP="${ROOT}/apply.sh"
ART=".test-artifacts"; mkdir -p "$ART"

log(){ printf '[test] %s\n' "$*"; }

# JSON only 캡처 유틸(청정 셸 + 마지막 JSON 라인 + 정합성 게이트)
run_json_clean () {
  # 사용법:
  #   run_json_clean "PLAN='...' USB='...' HDD='...' APPLY=1" .out.json ["timeout 1s"]
  local assigns="$1"; local out="$2"; local to="${3:-}"
  local _raw_out="${out%.json}.raw.txt"; local _raw_err="${out%.json}.err.txt"
  : >"$_raw_out"; : >"$_raw_err"
  local TO=""
  if command -v timeout >/dev/null 2>&1; then TO="timeout 20s"; fi
  if [[ -n "$to" ]]; then TO="$to"; fi
  env -i PATH="$PATH" HOME="$HOME" LC_ALL=C LANG=C PS1= \
    $TO bash --noprofile --norc -c \
    "cd '$ROOT' && ${assigns} '$APP' --json-summary-only" \
    >"$_raw_out" 2>"$_raw_err" || true
  tac "$_raw_out" | awk '/^[[:space:]]*[{[]/{print;exit}' >"$out"
  head -c1 "$out" | grep -q '[{\[]' || { echo '[ERR] JSON-start fail:' "$out"; return 70; }
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

# =========================
# Phase-2: ENOSPC (HDD를 8MB tmpfs로 바꿔 공간부족 유발)
# =========================
case_enospc() {
  log "P2/enospc: tmpfs(8M) -> dst 12M write -> ENOSPC 기대"
  sudo -n true >/dev/null 2>&1 || { echo "[SKIP] sudo required for ENOSPC"; return 0; }
  # tmpfs로 /mnt/hdd를 대체
  sudo umount -f /mnt/hdd >/dev/null 2>&1 || true
  sudo mkdir -p /mnt/hdd
  sudo mount -t tmpfs -o size=8m,mode=0777 tmpfs /mnt/hdd
  sudo mkdir -p /mnt/hdd/ARCHIVE/FULL /mnt/hdd/ARCHIVE/INCR
  # 12MB 파일 준비
  local tmp; tmp="$(mktemp -d -t duri-p2enospc-XXXXXX)"
  mkdir -p "$tmp/src"
  local f="$tmp/src/FULL__p2-enospc.tar.zst"
  dd if=/dev/zero of="$f" bs=1M count=12 status=none
  sync || true
  local h; h="$(sha256sum "$f" | awk '{print $1}')"
  local plan="$tmp/plan.jsonl" dst="/mnt/hdd/ARCHIVE/FULL/FULL__p2-enospc.tar.zst"
  printf '[{"src":"%s","sha256":"%s","dst":"%s"}]\n' "$f" "$h" "$dst" >"$plan"
  set +e
  run_json_clean "PLAN='$plan' USB='/mnt/usb' HDD='/mnt/hdd' APPLY=1" "--json-summary-only" ".test-artifacts/p2_enospc.json" || true
  set -e
  # JSON 스키마 검증
  jq -e 'type=="object" and (.rc? // 0 | type=="number")' .test-artifacts/p2_enospc.json >/dev/null
  # 합격: rc!=0 또는 full_ok==0 또는 full_bad>0
  jq -e '(.rc!=0) or ((.full_ok? // 0)==0) or ((.full_bad? // 0)>0)' .test-artifacts/p2_enospc.json >/dev/null
  log "P2/enospc OK"
  # 정리
  sudo umount /mnt/hdd || true
}

if [[ "${RUN_ENOSPC:-0}" == "1" ]]; then
  # 의존 도구 확인
  for c in jq sha256sum dd awk sed grep head tr cp rm mktemp timeout; do
    command -v "$c" >/dev/null 2>&1 || { echo "[ERR] missing command: $c" >&2; exit 127; }
  done
  case_enospc
fi
