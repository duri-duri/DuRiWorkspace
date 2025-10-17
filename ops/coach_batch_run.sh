#!/usr/bin/env bash
set -euo pipefail
cd /home/duri/DuRiWorkspace

# Coach 배치 안전장치: 동시 실행 방지, 토큰/비용 상한, 백오프 재시도
flock -n /tmp/coach.lock -c "
  EXP_ID=\$(date +%Y%m%d.%H%M)-coach1
  N=\${1:-30}
  MAX_TOKENS=\${2:-50000}
  MAX_COST=\${3:-5.0}
  MAX_TIME=\${4:-300}
  
  echo \"🚀 Coach 배치 시작: EXP_ID=\$EXP_ID, N=\$N, MAX_TOKENS=\$MAX_TOKENS, MAX_COST=\$MAX_COST, MAX_TIME=\$MAX_TIME\"
  
  # 1) 샘플 뽑기 (고품질만)
  echo \"📊 평가 아이템 샘플링 중...\"
  docker compose exec -T duri-postgres psql -U duri -d duri -Atc \"
    SELECT id, task, gold_answer, grader
    FROM eval_items
    WHERE created_at >= NOW() - INTERVAL '30 days'
    ORDER BY random() LIMIT \$N;
  \" > /tmp/coach_items.tsv
  
  # 2) 두리 호출 → 자동채점 (python 러너)
  echo \"🧠 두리 호출 및 자동채점 중...\"
  timeout \$MAX_TIME python tools/coach_runner.py \\
    --exp \$EXP_ID \\
    --input /tmp/coach_items.tsv \\
    --out /tmp/coach_out.json \\
    --max-tokens \$MAX_TOKENS \\
    --max-cost \$MAX_COST
  
  # 3) Redis/PG 기록 + 요약
  echo \"💾 결과 기록 및 요약 중...\"
  python tools/coach_ingest.py \\
    --exp \$EXP_ID \\
    --in /tmp/coach_out.json
  
  # 4) 정리
  rm -f /tmp/coach_items.tsv /tmp/coach_out.json
  echo \"✅ Coach 배치 완료: EXP_ID=\$EXP_ID\"
"
