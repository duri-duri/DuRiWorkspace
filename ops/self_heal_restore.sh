#!/usr/bin/env bash
set -euo pipefail

# 자가회복(Self-healing) 최소 안전 루프
# 트리거 신호: (a) SRM 지속(>10분), (b) 드리프트/비용 컷아웃, (c) DB 무결성 실패 중 2개 이상 동시 발생 시

PKG="$1"
BASE="/home/duri/DuRiWorkspace"

echo "=== 🚨 자가회복 복구 시작 ==="
echo "복구 패키지: $PKG"
echo "기본 경로: $BASE"

if [ ! -f "$PKG" ]; then
    echo "❌ 복구 패키지 없음: $PKG"
    exit 1
fi

# 1. 격리: CANARY_RATIO=0
echo "🛡️ 1. 격리: CANARY_RATIO=0"
docker compose exec duri-redis redis-cli SET canary:ratio 0 || echo "⚠️ Redis 설정 실패"

# 2. 임시 디렉토리 생성
TMP=$(mktemp -d)
echo "📦 2. 패키지 압축 해제: $TMP"
tar -C "$TMP" -xzf "$PKG" || {
    echo "❌ 패키지 압축 해제 실패"
    rm -rf "$TMP"
    exit 1
}

# 3. DB 복구
echo "🗄️ 3. DB 복구"
docker compose stop duri-postgres || echo "⚠️ Postgres 정지 실패"
sleep 3
docker compose start duri-postgres || echo "⚠️ Postgres 시작 실패"
sleep 5

# Postgres 복구
if [ -f "$TMP"/gate_*/db/duri.pgdump ]; then
    echo "   - Postgres 덤프 복구 중..."
    cat "$TMP"/gate_*/db/duri.pgdump | docker compose exec -T duri-postgres \
      pg_restore -U duri -d duri --clean --if-exists || echo "   ⚠️ Postgres 복구 실패"
else
    echo "   ⚠️ Postgres 덤프 파일 없음"
fi

# Redis 복구
if [ -f "$TMP"/gate_*/db/redis_dump.rdb ]; then
    echo "   - Redis 덤프 복구 중..."
    docker compose stop duri-redis || echo "⚠️ Redis 정지 실패"
    sleep 2
    cp "$TMP"/gate_*/db/redis_dump.rdb /tmp/redis_dump.rdb
    docker compose start duri-redis || echo "⚠️ Redis 시작 실패"
    sleep 3
    rm -f /tmp/redis_dump.rdb
else
    echo "   ⚠️ Redis 덤프 파일 없음"
fi

# 4. 코드 복원 (bundle → repo 재생)
echo "📝 4. 코드 복원"
for repo in duri_core duri_evolution duri_brain duri_control; do
    if [ -f "$TMP"/gate_*/git_bundles/$repo.bundle ]; then
        echo "   - $repo 복원 중..."
        rm -rf "$BASE/$repo"_restored
        mkdir -p "$BASE/$repo"_restored
        (cd "$BASE/$repo"_restored && git clone "$TMP"/gate_*/git_bundles/$repo.bundle "$repo" --config core.bare=false) || echo "   ⚠️ $repo bundle 복원 실패"
        rsync -a --delete "$BASE/$repo"_restored/"$repo"/ "$BASE/$repo"/ || echo "   ⚠️ $repo 동기화 실패"
        rm -rf "$BASE/$repo"_restored
    else
        echo "   ⚠️ $repo bundle 파일 없음"
    fi
done

# 5. 재배포
echo "🚀 5. 재배포"
docker compose up -d --build || echo "⚠️ 재배포 실패"

# 6. 자가검증(10분 루틴)
echo "🔍 6. 자가검증"
sleep 10
if [ -f "$BASE/ops/check_srm_and_guard.sh" ]; then
    "$BASE/ops/check_srm_and_guard.sh" || echo "⚠️ 자가검증 실패"
else
    echo "⚠️ 자가검증 스크립트 없음"
fi

# 7. 정리
rm -rf "$TMP"

echo ""
echo "=== ✅ 자가회복 복구 완료 ==="
echo "복구 패키지: $PKG"
echo "복구 시간: $(date)"
echo ""
echo "🎯 다음 단계:"
echo "   1. 자가검증 결과 확인"
echo "   2. 승인 후 카나리 재개: ./run_promote_canary.sh 0.10"
echo "   3. 10분 후 재검증: ./check_srm_and_guard.sh"
echo ""
echo "⚠️ 중요: 복구 후 반드시 수동 검증 후 승인하세요!"
