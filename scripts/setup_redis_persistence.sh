#!/bin/bash

# Redis 볼륨 정책 통일 및 영속화 설정 스크립트
# 이 스크립트는 Redis 데이터의 영속성을 보장하고 볼륨 정책을 통일합니다.

set -e

echo "🔧 Redis 볼륨 정책 통일 및 영속화 설정"
echo "========================================"

# 1. 현재 Redis 상태 확인
echo "1. 현재 Redis 상태 확인..."
docker compose -p duriworkspace ps duri-redis || echo "Redis 컨테이너가 실행 중이지 않습니다."

# 2. 기존 볼륨 백업 (데이터 보존)
echo "2. 기존 Redis 데이터 백업..."
if docker compose -p duriworkspace ps duri-redis | grep -q "Up"; then
    echo "Redis가 실행 중입니다. 데이터를 백업합니다..."
    docker compose -p duriworkspace exec -T duri-redis redis-cli BGSAVE
    sleep 2
    docker compose -p duriworkspace exec -T duri-redis redis-cli SAVE
    echo "✅ Redis 데이터 백업 완료"
else
    echo "⚠️ Redis가 실행 중이지 않습니다. 백업을 건너뜁니다."
fi

# 3. 기존 볼륨 정리 (선택적)
echo "3. 기존 볼륨 정리..."
read -p "기존 Redis 볼륨을 정리하시겠습니까? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "기존 볼륨을 정리합니다..."
    docker compose -p duriworkspace down
    docker volume rm duriworkspace_duri_redis_data 2>/dev/null || echo "볼륨이 이미 존재하지 않습니다."
    echo "✅ 기존 볼륨 정리 완료"
else
    echo "기존 볼륨을 유지합니다."
fi

# 4. 새로운 설정으로 Redis 재시작
echo "4. 새로운 설정으로 Redis 재시작..."
docker compose -p duriworkspace up -d duri-redis

# 5. Redis 설정 확인
echo "5. Redis 설정 확인..."
sleep 5
docker compose -p duriworkspace exec duri-redis redis-cli CONFIG GET appendonly
docker compose -p duriworkspace exec duri-redis redis-cli CONFIG GET appendfsync

# 6. 데이터 영속성 테스트
echo "6. 데이터 영속성 테스트..."
docker compose -p duriworkspace exec duri-redis redis-cli SET test:persistence "Redis 영속성 테스트 $(date)"
docker compose -p duriworkspace exec duri-redis redis-cli GET test:persistence

# 7. 컨테이너 재시작 테스트
echo "7. 컨테이너 재시작 테스트..."
docker compose -p duriworkspace restart duri-redis
sleep 5
docker compose -p duriworkspace exec duri-redis redis-cli GET test:persistence

if [ $? -eq 0 ]; then
    echo "✅ Redis 데이터 영속성 테스트 성공!"
else
    echo "❌ Redis 데이터 영속성 테스트 실패!"
    exit 1
fi

# 8. 최종 상태 확인
echo "8. 최종 상태 확인..."
docker compose -p duriworkspace ps duri-redis
docker volume ls | grep redis

echo ""
echo "🎉 Redis 볼륨 정책 통일 및 영속화 설정 완료!"
echo ""
echo "📋 설정 요약:"
echo "- AOF (Append Only File) 활성화: appendonly yes"
echo "- 동기화 주기: everysec (매초)"
echo "- 볼륨 이름: duriworkspace_duri_redis_data"
echo "- 프로젝트 이름: duriworkspace (통일)"
echo ""
echo "💡 향후 주의사항:"
echo "- 항상 'docker compose -p duriworkspace' 사용"
echo "- 'docker compose down -v' 사용 시 데이터 손실 주의"
echo "- 정기적인 Redis 데이터 백업 권장"
