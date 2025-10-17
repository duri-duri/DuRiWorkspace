#!/usr/bin/env bash
set -euo pipefail

# 리포/노드 전수(전체 코딩) 스냅샷 표준화
# 3-2-1 + 게이트 스냅샷 + 자가회복을 지금 구조에 붙임

STAMP=$(date +%Y%m%d_%H%M)
BASE="/home/duri/DuRiWorkspace"
OUT="$BASE/gate_${STAMP}"
SSD="/mnt/DURISSD/gates"             # DURISSD 스테이징

echo "=== 🚀 게이트 스냅샷 생성 시작 ==="
echo "타임스탬프: ${STAMP}"
echo "출력 경로: ${OUT}"
echo "SSD 경로: ${SSD}"

# 디렉토리 생성
mkdir -p "$OUT"/{git_bundles,docker,db,runtime-proof,build_info,checksums}
mkdir -p "$SSD"

# Docker 설정 복사
cp $BASE/docker-compose.yml $OUT/docker/ 2>/dev/null || echo "⚠️ docker-compose.yml 없음"
cp $BASE/docker-compose.ssd.yml $OUT/docker/ 2>/dev/null || echo "⚠️ docker-compose.ssd.yml 없음"
cp $BASE/.env $OUT/docker/ 2>/dev/null || echo "⚠️ .env 없음"

echo "📦 1) Git 전체 이력 bundle (네트워크 없이 복구 가능)"
for repo in duri_core duri_evolution duri_brain duri_control; do
  if [ -d "$BASE/$repo" ]; then
    echo "   - $repo bundle 생성 중..."
    (cd "$BASE/$repo" && git bundle create "$OUT/git_bundles/$repo.bundle" --all 2>/dev/null) || echo "   ⚠️ $repo bundle 실패"
  else
    echo "   ⚠️ $repo 디렉토리 없음"
  fi
done

echo "🗄️ 2) DB 덤프"
# Postgres 덤프
if docker compose exec -T duri-postgres pg_isready -U duri -d duri >/dev/null 2>&1; then
  echo "   - Postgres 덤프 중..."
  docker compose exec -T duri-postgres pg_dump -U duri -d duri -Fc > "$OUT/db/duri.pgdump" 2>/dev/null || echo "   ⚠️ Postgres 덤프 실패"
else
  echo "   ⚠️ Postgres 연결 실패"
fi

# Redis 덤프
if docker compose exec -T duri-redis redis-cli ping >/dev/null 2>&1; then
  echo "   - Redis 덤프 중..."
  docker compose exec -T duri-redis sh -lc 'redis-cli SAVE && cat /data/dump.rdb' > "$OUT/db/redis_dump.rdb" 2>/dev/null || echo "   ⚠️ Redis 덤프 실패"
else
  echo "   ⚠️ Redis 연결 실패"
fi

echo "📊 3) 런타임 증빙(이미 쓰시던 쿼리들)"
# 최신 승격 결정
docker compose exec -T duri-postgres psql -U duri -d duri \
  -c "SELECT * FROM v_promotion_latest;" > "$OUT/runtime-proof/promotion_latest.txt" 2>/dev/null || echo "   ⚠️ promotion_latest 쿼리 실패"

# 10분 분포
docker compose exec -T duri-postgres psql -U duri -d duri \
  -c "WITH recent AS (SELECT * FROM v_feedback_events_clean WHERE ts>=NOW()-INTERVAL '10 minutes' AND track IN('prod','cand')) SELECT track, COUNT(*) FROM recent GROUP BY 1;" \
  > "$OUT/runtime-proof/distribution_10m.txt" 2>/dev/null || echo "   ⚠️ distribution_10m 쿼리 실패"

# SRM 체크
RATIO=$(docker compose exec duri-redis redis-cli GET canary:ratio 2>/dev/null || echo "0.10")
docker compose exec -T duri-postgres psql -U duri -d duri \
  -c "WITH recent AS (SELECT * FROM v_feedback_events_clean WHERE ts >= NOW() - INTERVAL '10 minutes' AND track IN ('prod','cand')), prod AS (SELECT COUNT(*) n FROM recent WHERE track='prod'), total AS (SELECT COUNT(*) n FROM recent), vars AS (SELECT ${RATIO}::numeric AS expect) SELECT (SELECT n FROM prod) AS prod_n, (SELECT n FROM total) AS total_n, ROUND(((SELECT n FROM prod)::numeric / NULLIF((SELECT n FROM total),0))::numeric,4) AS prod_ratio, CASE WHEN abs(((SELECT n FROM prod)::numeric / NULLIF((SELECT n FROM total),0)) - (SELECT expect FROM vars)) > 0.05 THEN 'SRM_SUSPECTED' ELSE 'OK' END AS srm_status;" \
  > "$OUT/runtime-proof/srm_check.txt" 2>/dev/null || echo "   ⚠️ SRM 체크 실패"

echo "🔧 4) 환경/빌드 정보"
uname -a > "$OUT/build_info/uname.txt"
python3 -m pip freeze > "$OUT/build_info/pip_freeze.txt" 2>/dev/null || echo "   ⚠️ pip freeze 실패"
docker --version > "$OUT/build_info/docker_version.txt" 2>/dev/null || echo "   ⚠️ docker version 실패"

echo "🔐 5) 체크섬"
( cd "$OUT" && find . -type f -maxdepth 4 -print0 | xargs -0 sha256sum ) > "$OUT/checksums/sha256sum.txt"

echo "📦 6) 스테이징(DURISSD)으로 고속 복사 + 압축 아카이브 생성"
tar -C "$BASE" -czf "$SSD/gate_${STAMP}.tar.gz" "gate_${STAMP}" 2>/dev/null || {
  echo "   ⚠️ DURISSD 저장 실패, 로컬 저장"
  tar -C "$BASE" -czf "$BASE/gate_${STAMP}.tar.gz" "gate_${STAMP}"
}

echo "📋 7) README.txt 생성"
cat > "$OUT/README.txt" << EOF
게이트 스냅샷 복구 순서 (10줄)

1. tar -xzf gate_${STAMP}.tar.gz
2. cd gate_${STAMP}
3. docker compose -f docker/docker-compose.yml down
4. cat db/duri.pgdump | docker compose exec -T duri-postgres pg_restore -U duri -d duri --clean --if-exists
5. for repo in duri_core duri_evolution duri_brain duri_control; do
     rm -rf ../\${repo}_restored && mkdir -p ../\${repo}_restored
     cd ../\${repo}_restored && git clone ../gate_${STAMP}/git_bundles/\${repo}.bundle \${repo} --config core.bare=false
     rsync -a --delete \${repo}/ ../\${repo}/
   done
6. docker compose -f docker/docker-compose.yml up -d --build
7. ./check_srm_and_guard.sh
8. ./run_promote_canary.sh 0.10

생성 시간: $(date)
타임스탬프: ${STAMP}
EOF

echo ""
echo "=== ✅ 게이트 스냅샷 생성 완료 ==="
echo "로컬: $BASE/gate_${STAMP}"
echo "SSD: $SSD/gate_${STAMP}.tar.gz"
echo "크기: $(du -sh "$OUT" | cut -f1)"
echo ""
echo "🎯 다음 단계:"
echo "   - 매일 크론 등록: 0 2 * * * $BASE/ops/create_gate_snapshot.sh"
echo "   - 주 1회 클라우드 업로드"
echo "   - rotate_gates.sh로 DURISSD 용량 관리"
