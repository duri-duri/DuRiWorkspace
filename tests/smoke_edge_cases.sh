#!/usr/bin/env bash
# Day 66 엣지 케이스 스모크 테스트
set -euo pipefail

echo "🧪 Day 66 엣지 케이스 스모크 테스트"

# 1) metrics 파일 없음 → exit 1
echo "1. metrics 파일 없음 → exit 1"
bash scripts/alerts/threshold_guard.sh /no/such.tsv 3; echo "exit:$?"

# 2) 헤더만 있고 all 없음 → exit 1
echo "2. 헤더만 있고 all 없음 → exit 1"
printf "scope\tdomain\tcount\tndcg@3\tmrr\toracle_recall@3\n" > /tmp/m.tsv
bash scripts/alerts/threshold_guard.sh /tmp/m.tsv 3; echo "exit:$?"

# 3) 수치 NaN/빈칸 → exit 1
echo "3. 수치 NaN/빈칸 → exit 1"
printf "scope\tdomain\tcount\tndcg@3\tmrr\toracle_recall@3\nall\t-\t5\tNaN\t0.9\t1.0\n" > /tmp/m.tsv
bash scripts/alerts/threshold_guard.sh /tmp/m.tsv 3; echo "exit:$?"

# 4) CRLF 포함 → 정상 0
echo "4. CRLF 포함 → 정상 0"
unix2dos </dev/null >/dev/null 2>&1 || true
{ printf "scope\tdomain\tcount\tndcg@3\tmrr\toracle_recall@3\r\n"; printf "all\t-\t5\t0.90\t0.90\t0.9\r\n"; } > /tmp/m.tsv
bash scripts/alerts/threshold_guard.sh /tmp/m.tsv 3; echo "exit:$?"

# 5) 회귀 + 비엄격 → 0
echo "5. 회귀 + 비엄격 → 0"
TH_NDCG=0.99 TH_MRR=0.99 TH_ORACLE=1.1 GUARD_STRICT=0 bash scripts/alerts/threshold_guard.sh .reports/metrics/day66_metrics.tsv 3; echo "exit:$?"

# 6) 회귀 + 엄격 → 2
echo "6. 회귀 + 엄격 → 2"
TH_NDCG=0.99 TH_MRR=0.99 TH_ORACLE=1.1 GUARD_STRICT=1 bash scripts/alerts/threshold_guard.sh .reports/metrics/day66_metrics.tsv 3; echo "exit:$?"

echo "🎉 엣지 케이스 테스트 완료!"


