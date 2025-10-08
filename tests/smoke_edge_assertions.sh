#!/usr/bin/env bash
# 스모크 확장: 엣지 5종 자동단언
set -euo pipefail

echo "🧪 스모크 확장: 엣지 5종 자동단언"

# 1) 헤더만 있음 → exit 1
echo "1. 헤더만 있음 → exit 1"
printf "scope\tdomain\tcount\tndcg@3\tmrr\toracle_recall@3\n" > /tmp/m.tsv
bash scripts/alerts/threshold_guard.sh /tmp/m.tsv 3; rc=$?
[[ $rc -eq 1 ]] && echo "✅ PASS: 헤더만 있음 → exit 1" || { echo "❌ FAIL: 예상 exit 1, 실제 $rc"; exit 1; }

# 2) overall 누락 → exit 1
echo "2. overall 누락 → exit 1"
printf "scope\tdomain\tcount\tndcg@3\tmrr\toracle_recall@3\ndomain\thealth\t5\t0.9\t0.9\t1.0\n" > /tmp/m.tsv
bash scripts/alerts/threshold_guard.sh /tmp/m.tsv 3; rc=$?
[[ $rc -eq 1 ]] && echo "✅ PASS: overall 누락 → exit 1" || { echo "❌ FAIL: 예상 exit 1, 실제 $rc"; exit 1; }

# 3) NaN 포함 → exit 1
echo "3. NaN 포함 → exit 1"
printf "scope\tdomain\tcount\tndcg@3\tmrr\toracle_recall@3\nall\t-\t5\tNaN\t0.9\t1.0\n" > /tmp/m.tsv
bash scripts/alerts/threshold_guard.sh /tmp/m.tsv 3; rc=$?
[[ $rc -eq 1 ]] && echo "✅ PASS: NaN 포함 → exit 1" || { echo "❌ FAIL: 예상 exit 1, 실제 $rc"; exit 1; }

# 4) CRLF 입력 → 정상 0
echo "4. CRLF 입력 → 정상 0"
{ printf "scope\tdomain\tcount\tndcg@3\tmrr\toracle_recall@3\r\n"; printf "all\t-\t5\t0.90\t0.90\t0.9\r\n"; } > /tmp/m.tsv
bash scripts/alerts/threshold_guard.sh /tmp/m.tsv 3; rc=$?
[[ $rc -eq 0 ]] && echo "✅ PASS: CRLF 입력 → 정상 0" || { echo "❌ FAIL: 예상 exit 0, 실제 $rc"; exit 1; }

# 5) 도메인별 override 우선순위 → CLI 우선
echo "5. 도메인별 override 우선순위 → CLI 우선"
printf "scope\tdomain\tcount\tndcg@3\tmrr\toracle_recall@3\nall\t-\t5\t0.90\t0.90\t0.9\n" > /tmp/m.tsv
TH_NDCG=0.99 TH_MRR=0.99 TH_ORACLE=1.1 GUARD_STRICT=1 bash scripts/alerts/threshold_guard.sh /tmp/m.tsv 3; rc=$?
[[ $rc -eq 2 ]] && echo "✅ PASS: CLI override 우선 → exit 2" || { echo "❌ FAIL: 예상 exit 2, 실제 $rc"; exit 1; }

echo "🎉 모든 엣지 케이스 자동단언 통과!"
