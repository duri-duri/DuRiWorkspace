#!/usr/bin/env bash
set -euo pipefail

BASE="/mnt/h/ARCHIVE/.UNWRAP/extracted/CORE__2025-08-14__1310__host-duri-head-/__UNWRAP"
KEEP="bf50763c9a"
DUPS=(df4e05a209 c831a83d0c 64b34118c6 21c73ab567)

TS="$(date +%Y%m%d_%H%M%S)"
TRASH="/mnt/h/ARCHIVE/.TRASH/dedup_$TS"
META="$TRASH/MANIFEST.txt"
LOG="$TRASH/LOG.txt"
mkdir -p "$TRASH"

log(){ echo "[$(date +%F_%T)] $*" | tee -a "$LOG"; }

# ── (1) 트리 해시 함수: 내용 완전 동일성 검증
treehash() {
  local dir="$1"
  (cd "$dir" \
    && find . -type f -print0 \
    | sort -z \
    | xargs -0 sha256sum \
    | sha256sum | awk '{print $1}')
}

# ── (2) KEEP 존재 확인
[[ -d "$BASE/$KEEP" ]] || { echo "KEEP not found: $BASE/$KEEP" >&2; exit 2; }

log "=== STAGE-1: 동일성(트리해시) 검증 시작 ==="
H_KEEP="$(treehash "$BASE/$KEEP")"
echo "[KEEP] $KEEP  treehash=$H_KEEP" | tee -a "$META"

# ── (3) 후보별 검증 + TRASH 격리(삭제 아님)
log "=== STAGE-2: TRASH 격리 + 롤백 스크립트 생성 ==="
for d in "${DUPS[@]}"; do
  if [[ -d "$BASE/$d" ]]; then
    H_DUP="$(treehash "$BASE/$d")"
    echo "[DUP ] $d  treehash=$H_DUP" | tee -a "$META"
    if [[ "$H_DUP" == "$H_KEEP" ]]; then
      mv "$BASE/$d" "$TRASH/$d"
      log "[MOVE] $d -> $TRASH/$d"
    else
      log "[SKIP] $d : treehash 불일치 (수동 확인)"
    fi
  else
    log "[MISS] $d : 원위치에 없음 (이미 이동/정리된 듯)"
  fi
done

# ── (4) ROLLBACK 생성(멱등)
cat > "$TRASH/ROLLBACK.sh" <<'EOS'
#!/usr/bin/env bash
set -euo pipefail
BASE="/mnt/h/ARCHIVE/.UNWRAP/extracted/CORE__2025-08-14__1310__host-duri-head-/__UNWRAP"
TRASH_DIR="$(cd "$(dirname "$0")" && pwd)"
for d in $(ls -1 "$TRASH_DIR" | grep -E '^[0-9a-f]{10}$' || true); do
  if [[ -e "$TRASH_DIR/$d" && ! -e "$BASE/$d" ]]; then
    mv "$TRASH_DIR/$d" "$BASE/$d"
    echo "[RESTORE] $d"
  else
    echo "[HOLD] $d : 대상 경로 존재/없음 불명 → 수동 처리"
  fi
done
EOS
chmod +x "$TRASH/ROLLBACK.sh"
log "[OK] ROLLBACK 생성: $TRASH/ROLLBACK.sh"

# ── (5) 링크 치환(선택): 비워진 자리에 KEEP 심볼릭 링크(경로 호환성 유지)
log "=== STAGE-3: 경로 유지용 심볼릭 링크 생성(선택) ==="
for d in "${DUPS[@]}"; do
  if [[ ! -e "$BASE/$d" && -d "$TRASH/$d" ]]; then
    ln -s "$BASE/$KEEP" "$BASE/$d"
    log "[LINK] $BASE/$d -> $BASE/$KEEP"
  fi
done

# ── (6) 유예기간 보호: 쓰기 금지(+ 로그/메타 보존)
chmod -R a-w "$TRASH" || true
log "[SAFE] TRASH 쓰기 금지 적용"

# ── (7) 요약 리포트
REPORT="$TRASH/REPORT.txt"
{
  echo "== DEDUP REPORT @ $(date)"
  echo "BASE: $BASE"
  echo "KEEP: $KEEP    treehash=$H_KEEP"
  echo "TRASH: $TRASH"
  echo
  echo "[TRASHED]"
  ls -1 "$TRASH" | grep -E '^[0-9a-f]{10}$' || true
  echo
  echo "[SIZES]"
  du -sh "$BASE/$KEEP" 2>/dev/null || true
  for d in "${DUPS[@]}"; do
    [[ -d "$TRASH/$d" ]] && du -sh "$TRASH/$d"
  done
} | tee "$REPORT"

echo
echo "[DONE] Stage1(해시검증) + Stage2(TRASH 격리) + Stage3(링크치환) 완료"
echo "TRASH: $TRASH"
echo "ROLLBACK: $TRASH/ROLLBACK.sh"
echo "REPORT: $REPORT"
