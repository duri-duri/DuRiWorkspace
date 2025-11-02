#!/usr/bin/env bash
# Γ4: ab_pvalue_stats.sh 입출력 고정 (argv 전달, 집계창 축소 옵션 추가)
set -euo pipefail

# 집계창 파라미터 파싱 (A) p-value 분산 '진짜' 보장
WINDOW="${1:-24 hours}"
echo "[INFO] 집계창: $WINDOW"

# C) AB 통계 "유효 샘플만" 집계: n≥1만 포함, 라벨 없는 라인 제외
# 1) 최근 창 파일 수집
mapfile -t FILES < <(find var/evolution -name "ab_eval.prom" -newermt "-$WINDOW" 2>/dev/null || true)

if [ "${#FILES[@]}" -eq 0 ]; then
    echo "샘플 수: 0 (파일 없음)"
    exit 0
fi

# P3: 최종 방어막 - 라벨 있는 p라인만 수집, n>=1만 취합 (라벨 없는 p라인 절대 배제)
mapfile -t VALS < <(
    for f in "${FILES[@]}"; do
        awk '
        /^duri_ab_p_value\{/ {
            # 라벨 형식: duri_ab_p_value{ev="...",n="...",build_unixtime="..."} <value>
            # ev=..., n=... 파싱, n>=1만 취합
            if (match($0, /n="([0-9]+)".*\}\s+([0-9.eE+-]+(?:e[+-][0-9]+)?)$/, m)) {
                n_val = m[1]
                p_val = m[2]
                # n>=1만 포함, 값이 숫자이고 '--' 아님
                if (n_val != "" && n_val + 0 >= 1 && p_val != "" && p_val != "--" && p_val ~ /^[0-9.eE+-]+$/) {
                    print p_val
                }
            }
        }
        ' "$f" 2>/dev/null || true
    done
)

if [ "${#VALS[@]}" -eq 0 ]; then
  echo "샘플 수: 0"
  exit 0
fi

# (A) 숫자형만 최종 방어막: 라벨 有 + n≥1 + 숫자형 p 강제 필터
VALS_CLEAN=()
for v in "${VALS[@]}"; do
  # 숫자형만 수집 (정수/소수/과학기수법 모두 포함, '--' 완전 배제)
  if [[ "$v" =~ ^[0-9]+(\.[0-9]+)?(e-?[0-9]+)?$ ]] && [[ "$v" != "--" ]]; then
    VALS_CLEAN+=("$v")
  fi
done

if [ "${#VALS_CLEAN[@]}" -eq 0 ]; then
    echo "샘플 수: 0 (유효한 숫자형 p-value 없음)"
    exit 0
fi

# (3) 수학적 게이트 삽입: 허수 방지
if [ "${#VALS_CLEAN[@]}" -lt 2 ]; then
  echo "ab_eval_warn_insufficient_samples 1"
  echo "[WARN] 샘플 수 부족: ${#VALS_CLEAN[@]} < 2 (수치 출력 생략 → Prom에서 알람으로만 감지)"
  mkdir -p var/metrics
  echo "ab_eval_warn_insufficient_samples 1" >> var/metrics/ab_eval.prom 2>/dev/null || true
  exit 0  # 수치 출력 생략 → Prom에서 알람으로만 감지
fi

VALID_VALS=("${VALS_CLEAN[@]}")

python3 -c '
import sys, math
vals=[]
for arg in sys.argv[1:]:
    try:
        v=float(arg)
        if math.isfinite(v) and v>=0:
            vals.append(v)
    except (ValueError, OverflowError):
        continue
n=len(vals)
if n==0:
    print("샘플 수: 0")
    sys.exit(0)
avg=sum(vals)/n
mn, mx = min(vals), max(vals)
var=sum((x-avg)**2 for x in vals)/n
sd=math.sqrt(var) if var>0 else 0.0
print(f"샘플 수: {n}")
print(f"평균 p-value: {avg:.9f}")
print(f"최소: {mn:.9f}")
print(f"최대: {mx:.9f}")
print(f"표준편차: {sd:.9f}")

# (3) 수학적 게이트: 표준편차 0 체크 (허수 방지)
if sd == 0.0:
    print("ab_eval_warn_sigma_zero 1")
    import os
    os.makedirs("var/metrics", exist_ok=True)
    with open("var/metrics/ab_eval.prom", "a") as f:
        f.write("ab_eval_warn_sigma_zero 1\n")
    print("[WARN] 표준편차 0 (분산 붕괴)")
    exit(0)

print("✅ 통계적으로 유의미 (p < 0.05)" if avg<0.05 else "⚠️ 통계적으로 유의미하지 않음 (p >= 0.05)")
' "${VALID_VALS[@]}"
