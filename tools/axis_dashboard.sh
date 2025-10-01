#!/usr/bin/env bash
set -Eeuo pipefail

AX=$(ls -1d backup_repository/axes/* | tail -n1)
M="$AX/manifest.csv"
OUT="$AX/dashboard/$(date '+%Y%m%d_%H%M%S')"
mkdir -p "$OUT"

# 기본 지표 계산
tot=$(tail -n +2 "$M" | wc -l)
vis=$(tail -n +2 "$M" | awk -F, '$4!="_unclassified"{c++} END{print c+0}')
prov=$(find /mnt/h/ARCHIVE -type f -name "*.prov" | wc -l)
ok=$(tail -n +2 "$M" | awk -F, '$11==1{c++} END{print c+0}')

# 가시성 V 계산
V=$(awk -v v=$vis -v t=$tot 'BEGIN{if(t==0)print 0; else printf "%.3f", v/t}')

# 재현성 R 계산
R=$(awk -v o=$ok -v t=$tot 'BEGIN{if(t==0)print 0; else printf "%.3f", o/t}')

# 신선도 F 계산 (핵심축의 평균 mtime)
core_axes="backup_engine,learning_system,quality_improvement"
F=$(awk -F, -v cores="$core_axes" 'BEGIN{n=split(cores,c,","); for(i=1;i<=n;i++) core[c[i]]=1} NR>1 && core[$4]{print $3}' "$M" \
| awk -v now="$(date +%s)" '{sum+= (now-$1)/86400; cnt++} END{if(cnt) printf "%.2f", sum/cnt; else print "N/A"}')

# 요약 리포트
cat > "$OUT/summary.txt" <<EOF
=== BACKUP SYSTEM METRICS ===
Date: $(date '+%Y-%m-%d %H:%M:%S')
Total Files: $tot
Visible Files: $vis
Provenance Files: $prov
Success Files: $ok

=== KEY METRICS ===
V(가시성): $V (목표: ≥0.95)
R(재현성): $R (목표: ≥0.98)
F(신선도,일): $F (목표: ≤7)

=== STATUS ===
EOF

# 상태 판정
if (( $(echo "$V >= 0.95" | bc -l) )); then
  echo "✅ 가시성 목표 달성" >> "$OUT/summary.txt"
else
  echo "❌ 가시성 목표 미달 (현재: $V)" >> "$OUT/summary.txt"
fi

if (( $(echo "$R >= 0.98" | bc -l) )); then
  echo "✅ 재현성 목표 달성" >> "$OUT/summary.txt"
else
  echo "❌ 재현성 목표 미달 (현재: $R)" >> "$OUT/summary.txt"
fi

if [[ "$F" != "N/A" ]] && (( $(echo "$F <= 7" | bc -l) )); then
  echo "✅ 신선도 목표 달성" >> "$OUT/summary.txt"
else
  echo "❌ 신선도 목표 미달 (현재: $F)" >> "$OUT/summary.txt"
fi

# 축별 카운트 (정렬)
tail -n +2 "$M" | awk -F, '{print $4}' | sort | uniq -c | sort -nr > "$OUT/axis_counts_sorted.tsv"

# 교차 카운트 (주축×태그)
awk -F, 'NR>1{
  axis=$4; split($6, arr, /;/);
  for(i in arr) if(arr[i]!="") c[axis,arr[i]]++
}
END{
  for(k in c){
    split(k, ab, SUBSEP); printf "%s x %s = %d\n", ab[1], ab[2], c[k]
  }
}' "$M" | sort -nr > "$OUT/cross_counts_sorted.tsv"

echo "Dashboard generated -> $OUT"
