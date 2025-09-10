#!/usr/bin/env bash
# tools/axis_graph.sh
# 관계 그래프 모델: axis × tags 네트워크 시각화
# 사용법: bash tools/axis_graph.sh [manifest.csv]

set -Eeuo pipefail

MANIFEST="${1:-backup_repository/axes/$(ls -1d backup_repository/axes/* | tail -n1)/manifest.csv}"
OUT_DIR="$(dirname "$MANIFEST")/graph_$(date '+%Y%m%d_%H%M%S')"
mkdir -p "$OUT_DIR"

# 1. 축-태그 관계 매트릭스 생성
awk -F, 'NR>1 && $6!="" {
  axis=$4
  split($6, tags, /;/)
  for(i in tags) {
    if(tags[i]!="") {
      print axis " -> " tags[i]
    }
  }
}' "$MANIFEST" | sort | uniq -c | sort -nr > "$OUT_DIR/axis_tag_relations.tsv"

# 2. 태그별 백업 수 집계
awk -F, 'NR>1 && $6!="" {
  split($6, tags, /;/)
  for(i in tags) {
    if(tags[i]!="") {
      count[tags[i]]++
    }
  }
}
END {
  for(tag in count) {
    print tag "\t" count[tag]
  }
}' "$MANIFEST" | sort -k2 -nr > "$OUT_DIR/tag_counts.tsv"

# 3. 축별 태그 다양성 계산
awk -F, 'NR>1 && $6!="" {
  axis=$4
  split($6, tags, /;/)
  for(i in tags) {
    if(tags[i]!="") {
      unique_tags[axis][tags[i]]=1
    }
  }
}
END {
  for(axis in unique_tags) {
    count=0
    for(tag in unique_tags[axis]) count++
    print axis "\t" count
  }
}' "$MANIFEST" | sort -k2 -nr > "$OUT_DIR/axis_tag_diversity.tsv"

# 4. 네트워크 그래프 (DOT 형식)
cat > "$OUT_DIR/axis_network.dot" << 'EOF'
digraph AxisNetwork {
    rankdir=LR;
    node [shape=box, style=filled];
    
    // 축 노드 (파란색)
    subgraph cluster_axes {
        label="Axes (Core Functions)";
        style=filled;
        color=lightblue;
EOF

# 축 노드 추가
awk -F, 'NR>1 {print "        " $4 " [color=blue, fillcolor=lightblue];"}' "$MANIFEST" | sort -u >> "$OUT_DIR/axis_network.dot"

cat >> "$OUT_DIR/axis_network.dot" << 'EOF'
    }
    
    // 태그 노드 (초록색)
    subgraph cluster_tags {
        label="Tags (Relationships)";
        style=filled;
        color=lightgreen;
EOF

# 태그 노드 추가
awk -F, 'NR>1 && $6!="" {
  split($6, tags, /;/)
  for(i in tags) {
    if(tags[i]!="") {
      print "        " tags[i] " [color=green, fillcolor=lightgreen];"
    }
  }
}' "$MANIFEST" | sort -u >> "$OUT_DIR/axis_network.dot"

cat >> "$OUT_DIR/axis_network.dot" << 'EOF'
    }
    
    // 관계 엣지
EOF

# 관계 엣지 추가
awk -F, 'NR>1 && $6!="" {
  axis=$4
  split($6, tags, /;/)
  for(i in tags) {
    if(tags[i]!="") {
      print "    " axis " -> " tags[i] " [color=gray, weight=1];"
    }
  }
}' "$MANIFEST" >> "$OUT_DIR/axis_network.dot"

echo "}" >> "$OUT_DIR/axis_network.dot"

# 5. 요약 리포트
cat > "$OUT_DIR/summary.txt" << EOF
=== AXIS-TAG RELATIONSHIP GRAPH ===
Generated: $(date '+%Y-%m-%d %H:%M:%S')
Manifest: $MANIFEST

=== TOP AXIS-TAG RELATIONSHIPS ===
$(head -10 "$OUT_DIR/axis_tag_relations.tsv")

=== TOP TAGS BY FREQUENCY ===
$(head -10 "$OUT_DIR/tag_counts.tsv")

=== AXIS TAG DIVERSITY ===
$(head -10 "$OUT_DIR/axis_tag_diversity.tsv")

=== FILES GENERATED ===
- axis_tag_relations.tsv: 축-태그 관계 매트릭스
- tag_counts.tsv: 태그별 백업 수
- axis_tag_diversity.tsv: 축별 태그 다양성
- axis_network.dot: 네트워크 그래프 (DOT 형식)
- summary.txt: 이 요약 리포트

=== VISUALIZATION ===
DOT 파일을 그래프로 렌더링하려면:
dot -Tpng "$OUT_DIR/axis_network.dot" -o "$OUT_DIR/axis_network.png"
dot -Tsvg "$OUT_DIR/axis_network.dot" -o "$OUT_DIR/axis_network.svg"
EOF

echo "Graph generated -> $OUT_DIR"
echo "Summary:"
cat "$OUT_DIR/summary.txt"




