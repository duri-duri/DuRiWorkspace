#!/usr/bin/env bash
set -euo pipefail
# E) 타임아웃 적응형: 최근 epoch p95가 8m 넘어가면 150, 아니면 90 (간단히 90으로 고정)
: "${BUNDLE_TIMEOUT:=90}"

# 비동기 실행 옵션 (백그라운드 실행)
ASYNC="${ASYNC:-0}"
if [ "$ASYNC" = "1" ]; then
    # 백그라운드 실행 (호출부가 기다리지 않음)
    (
        timeout "${BUNDLE_TIMEOUT}s" "$0" "$@" 2>&1 || echo "[WARN] bundle timeout"
    ) &
    exit 0
fi

ts="$(date -u +%Y%m%d-%H%M%S)"
# add 2-digit random suffix to avoid ID collisions within the same second
rnd=$(awk 'BEGIN{srand(); printf "%02d", int(rand()*100)}')
ev_dir="var/evolution/EV-${ts}-${rnd}"
mkdir -p "$ev_dir"
[ -f var/ANCHOR/SHA256SUMS ] && cp -a var/ANCHOR/SHA256SUMS "$ev_dir/ANCHOR.SHA256SUMS" || true
[ -f var/STATE.SHA256SUMS.snapshot ] && cp -a var/STATE.SHA256SUMS.snapshot "$ev_dir/STATE.SHA256SUMS.snapshot" || true
mkdir -p var/events; [ -f var/events/evolution.jsonl ] || touch var/events/evolution.jsonl
if command -v jq >/dev/null 2>&1; then
  echo '{}' | jq -c --arg ts "$(date -Iseconds -u)" --arg cyc "EV-${ts}" '{ts:$ts,cycle_id:$cyc}' >> var/events/evolution.jsonl
else
  echo "{\"ts\":\"$(date -Iseconds -u)\",\"cycle_id\":\"EV-${ts}\"}" >> var/events/evolution.jsonl
fi
tail -n 50 var/events/evolution.jsonl > "$ev_dir/evolution.EV-${ts}.jsonl"
# Γ2+Γ3: AB 평가를 EV별로 재계산 (고정값 방지, EV 국소 입력 강제)
EV_BASE="$(basename "$ev_dir")"
EV_JSONL="$ev_dir/evolution.EV-${ts}.jsonl"

# P1: 레거시 fallback 제거 (라벨 없는 p라인 차단)
rm -f "$ev_dir/.ab_cache" "$ev_dir/ab_eval.prom" 2>/dev/null || true

if [ -f "scripts/evolution/make_ab_eval_prom_min.py" ]; then
    # Γ2: EV별 국소 입력만 사용, 시드 = hash(ev_id|build_unixtime)
    # (P1) 샘플 생성 원인 태그 계산 (대시보드 가시화)
    SRC_SEEN=0
    SRC_A_ONLY=0
    SRC_B_ONLY=0
    SRC_PAIR_FAIL=0
    SRC_FILTER_DROP=0
    
    # jsonl 파일에서 원인 카운터 계산
    if [ -f "$EV_JSONL" ]; then
        SRC_SEEN=$(wc -l < "$EV_JSONL" 2>/dev/null || echo "0")
        # A/B 균형 확인 (간단 버전)
        if grep -qE '"variant":\s*"A"' "$EV_JSONL" 2>/dev/null; then
            SRC_A_ONLY=$(grep -cE '"variant":\s*"A"' "$EV_JSONL" 2>/dev/null || echo "0")
        fi
        if grep -qE '"variant":\s*"B"' "$EV_JSONL" 2>/dev/null; then
            SRC_B_ONLY=$(grep -cE '"variant":\s*"B"' "$EV_JSONL" 2>/dev/null || echo "0")
        fi
    fi
    
    if python3 scripts/evolution/make_ab_eval_prom_min.py \
        --ev "$EV_BASE" \
        --evdir "$ev_dir" 2>&1 | tee -a var/logs/ab_eval.log; then
        echo "[OK] EV별 AB 평가 재계산: $ev_dir/ab_eval.prom (ev_id=$EV_BASE, input=$EV_JSONL)"
        # (P1) 샘플 생성 원인 태그를 prom에 추가
        {
            echo "# HELP duri_ab_sample_source_seen raw events seen"
            echo "duri_ab_sample_source_seen{ev=\"$EV_BASE\"} $SRC_SEEN"
            echo "# HELP duri_ab_sample_source_a_only events with only A"
            echo "duri_ab_sample_source_a_only{ev=\"$EV_BASE\"} $SRC_A_ONLY"
            echo "# HELP duri_ab_sample_source_b_only events with only B"
            echo "duri_ab_sample_source_b_only{ev=\"$EV_BASE\"} $SRC_B_ONLY"
            echo "# HELP duri_ab_sample_pair_fail events failed to pair"
            echo "duri_ab_sample_pair_fail{ev=\"$EV_BASE\"} $SRC_PAIR_FAIL"
            echo "# HELP duri_ab_sample_filter_drop events dropped by filters"
            echo "duri_ab_sample_filter_drop{ev=\"$EV_BASE\"} $SRC_FILTER_DROP"
        } >> "$ev_dir/ab_eval.prom" 2>/dev/null || true
    else
        # P1: 실패 시에도 라벨 일관성 유지: p라인 미출력, n=0만 명시
        # (1) 원자성 쓰기: tmp → sync → rename
        tmp_prom="${ev_dir}/ab_eval.prom.tmp"
        {
            echo "# HELP duri_ab_samples Total sample count for AB eval"
            echo "# TYPE duri_ab_samples gauge"
            echo "duri_ab_samples{ev=\"$EV_BASE\"} 0"
        } > "$tmp_prom"
        sync "$tmp_prom" 2>/dev/null || true
        mv "$tmp_prom" "$ev_dir/ab_eval.prom"
        echo "[WARN] EV별 AB 평가 재계산 실패 → 라벨 없는 fallback 금지, n=0로 기록"
    fi
else
    # P1: make_ab_eval_prom_min.py 없음 → n=0로 기록 (라벨 일관성 유지)
    # (1) 원자성 쓰기: tmp → sync → rename
    tmp_prom="${ev_dir}/ab_eval.prom.tmp"
    {
        echo "# HELP duri_ab_samples Total sample count for AB eval"
        echo "# TYPE duri_ab_samples gauge"
        echo "duri_ab_samples{ev=\"$EV_BASE\"} 0"
    } > "$tmp_prom"
    sync "$tmp_prom" 2>/dev/null || true
    mv "$tmp_prom" "$ev_dir/ab_eval.prom"
    echo "[WARN] make_ab_eval_prom_min.py 없음 → n=0로 기록"
fi
( cd "$ev_dir" && find . -maxdepth 1 -type f -printf "%P\n" | sort | xargs -r sha256sum > SHA256SUMS )

# 전송 방식 기록 (하이브리드 시스템용)
: "${TRANSPORT:=http}"
echo "transport=${TRANSPORT}" >> "${ev_dir}/summary.txt" 2>/dev/null || true

echo "[OK] bundle: $ev_dir (transport=${TRANSPORT})"

# Update latest pointer
ln -sfn "$(realpath --relative-to=var/evolution "$ev_dir")" var/evolution/LATEST || true

# EV 생성 직후 mtime 갱신 (Exporter가 읽음)
[ -L var/evolution/LATEST ] && touch -h var/evolution/LATEST || touch "$ev_dir"

# 하드닝 #2: evidence_bundle 경쟁조건 제거 (간헐 FAIL 소거)
prom="$ev_dir/ab_eval.prom"
if [ -s "$prom" ]; then
    : # ok
else
    # 가드: 최대 100*50ms = 5s 대기
    i=0
    while [ $i -lt 100 ] && [ ! -s "$prom" ]; do
        sleep 0.05
        i=$((i+1))
    done
fi

# 최종 보증
if [ ! -s "$prom" ]; then
    echo "[FATAL] ab_eval.prom not found or empty: $prom" >&2
    exit 1
fi

sync
