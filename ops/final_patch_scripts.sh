#!/usr/bin/env bash
set -euo pipefail

# 1) 스크립트에서 docker 경로 고정 + 프로젝트명/고아정리
echo "1️⃣ docker 경로 고정 + 프로젝트명/고아정리 적용"

COMMON_HEADER='# docker compose 고정 경로 + 프로젝트명 + orphan 정리
PATH="/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"
DC="/usr/bin/docker compose -p duriworkspace"
DO_UP="$DC up -d --remove-orphans"
DO_PS="$DC ps"
DO_EXEC="$DC exec -T"
DO_LOGS="$DC logs --tail=50"'

# shadow_on.sh 패치
if [ -f "ops/shadow_on.sh" ]; then
  # 기존 헤더 제거하고 새 헤더 추가
  sed -i '1,10d' ops/shadow_on.sh
  sed -i "1i$COMMON_HEADER" ops/shadow_on.sh
  
  # docker compose 호출을 변수로 치환
  sed -i 's/docker compose up -d/$DO_UP/g' ops/shadow_on.sh
  sed -i 's/docker compose ps/$DO_PS/g' ops/shadow_on.sh
  sed -i 's/docker compose exec -T/$DO_EXEC/g' ops/shadow_on.sh
  sed -i 's/docker compose logs/$DO_LOGS/g' ops/shadow_on.sh
  
  echo "✅ ops/shadow_on.sh 패치 완료"
fi

# shadow_off.sh 패치
if [ -f "ops/shadow_off.sh" ]; then
  # 기존 헤더 제거하고 새 헤더 추가
  sed -i '1,10d' ops/shadow_off.sh
  sed -i "1i$COMMON_HEADER" ops/shadow_off.sh
  
  # docker compose 호출을 변수로 치환
  sed -i 's/docker compose down/$DC down --remove-orphans/g' ops/shadow_off.sh
  sed -i 's/docker compose ps/$DO_PS/g' ops/shadow_off.sh
  sed -i 's/docker compose exec -T/$DO_EXEC/g' ops/shadow_off.sh
  
  echo "✅ ops/shadow_off.sh 패치 완료"
fi

# 2) 사용자 crontab 사용 (권한 이슈 회피)
echo ""
echo "2️⃣ 사용자 crontab 사용"
crontab -l > /tmp/mycron 2>/dev/null || true
cat >> /tmp/mycron <<'CRON'
SHELL=/bin/bash
PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
CRON_TZ=Asia/Seoul

# 게이트 스냅샷/로테이션
0 2 * * *  cd /home/duri/DuRiWorkspace && flock -n /tmp/gate_snapshot.lock  ./ops/create_gate_snapshot.sh  >> /var/log/duri/cron.log 2>&1
0 3 * * *  cd /home/duri/DuRiWorkspace && flock -n /tmp/rotate_gates.lock   ./ops/rotate_gates.sh         >> /var/log/duri/cron.log 2>&1

# Shadow on/off (토요일 제외, 9–16)
0 9  * * 0-5 cd /home/duri/DuRiWorkspace && flock -n /tmp/shadow.lock ./ops/shadow_on.sh  >> /var/log/duri/cron.log 2>&1
0 16 * * 0-5 cd /home/duri/DuRiWorkspace && flock -n /tmp/shadow.lock ./ops/shadow_off.sh >> /var/log/duri/cron.log 2>&1
CRON
crontab /tmp/mycron && rm /tmp/mycron
echo "✅ 사용자 crontab 적용 완료"

# 3) Redis 지속성(AOF) 즉시 켜기
echo ""
echo "3️⃣ Redis 지속성(AOF) 즉시 켜기"
/usr/bin/docker compose -p duriworkspace exec -T duri-redis sh -lc '
redis-cli CONFIG SET appendonly yes &&
redis-cli CONFIG SET appendfsync everysec &&
redis-cli CONFIG REWRITE &&
redis-cli BGREWRITEAOF'
echo "✅ Redis AOF 활성화 완료"

# 4) cron.log 간단 로테이션
echo ""
echo "4️⃣ cron.log 간단 로테이션"
cat > /home/duri/DuRiWorkspace/ops/rotate_cron_log.sh <<'SH'
#!/usr/bin/env bash
set -euo pipefail
LOG=/var/log/duri/cron.log
MAX=$((50*1024*1024))   # 50MB
[ -f "$LOG" ] || exit 0
SZ=$(stat -c%s "$LOG" 2>/dev/null || echo 0)
if [ "$SZ" -ge "$MAX" ]; then
  ts=$(date +%F_%H%M%S)
  mv "$LOG" "/var/log/duri/cron.$ts.log"
  gzip -f "/var/log/duri/cron.$ts.log" || true
fi
find /var/log/duri -name "cron.*.log.gz" -mtime +14 -delete 2>/dev/null || true
SH
chmod +x /home/duri/DuRiWorkspace/ops/rotate_cron_log.sh
(crontab -l; echo "*/30 * * * * /home/duri/DuRiWorkspace/ops/rotate_cron_log.sh") | crontab -
echo "✅ cron.log 로테이션 설정 완료"

# 5) 세이프티 플래그: 스크립트 초반에 강제 체크
echo ""
echo "5️⃣ 세이프티 플래그 강제 체크 추가"

# shadow_on.sh에 세이프티 체크 추가
if [ -f "ops/shadow_on.sh" ]; then
  sed -i '/^DO_LOGS=.*/a\
\
# 세이프티 플래그 체크\
SAFE_ON=$($DO_EXEC duri-redis redis-cli GET shadow:enabled 2>/dev/null || echo 1)\
if [ "${SAFE_ON:-1}" != "1" ]; then\
  echo "🛑 shadow:enabled=0 → 사용자 차단 상태. 중단합니다."\
  exit 0\
fi' ops/shadow_on.sh
  echo "✅ shadow_on.sh 세이프티 체크 추가"
fi

# shadow_off.sh에 세이프티 체크 추가
if [ -f "ops/shadow_off.sh" ]; then
  sed -i '/^DO_LOGS=.*/a\
\
# 세이프티 플래그 체크\
SAFE_ON=$($DO_EXEC duri-redis redis-cli GET shadow:enabled 2>/dev/null || echo 1)\
if [ "${SAFE_ON:-1}" != "1" ]; then\
  echo "🛑 shadow:enabled=0 → 사용자 차단 상태. 중단합니다."\
  exit 0\
fi' ops/shadow_off.sh
  echo "✅ shadow_off.sh 세이프티 체크 추가"
fi

# 6) orphan 경고 근절 (이미 1에서 처리됨)
echo ""
echo "6️⃣ orphan 경고 근절 (이미 처리됨)"

# 7) 세이프티 플래그 기본값 설정
echo ""
echo "7️⃣ 세이프티 플래그 기본값 설정"
/usr/bin/docker compose -p duriworkspace exec -T duri-redis redis-cli MSET canary:enabled 1 shadow:enabled 1
echo "✅ 세이프티 플래그 기본값 설정 완료"

echo ""
echo "=== ✅ **마무리 7단계 적용 완료!** ==="
