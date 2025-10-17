#!/usr/bin/env bash
set -euo pipefail
cd /home/duri/DuRiWorkspace

echo "=== 🛡️ **실수 방지용 얕은 하드닝 8가지 적용** ==="

# 1. 크론에서 docker compose 절대경로 적용
echo "1️⃣ **docker compose 절대경로 적용**"
sed -i 's|docker compose|/usr/bin/docker compose -p duriworkspace --remove-orphans|g' ops/shadow_on.sh ops/shadow_off.sh ops/create_gate_snapshot.sh ops/rotate_gates.sh
echo "✅ docker compose 절대경로 적용 완료"

# 2. 크론 파일 사용자 crontab 버전 생성 (sudo 불필요)
echo ""
echo "2️⃣ **사용자 crontab 버전 생성**"
cat > etc_cron_d_duri_user_crontab << 'CRON'
# DuRi Shadow 훈련장 크론 스케줄 (사용자 crontab 버전)
SHELL=/bin/bash
PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
TZ=Asia/Seoul

# 게이트 스냅샷 (매일 02:00)
0 2 * * *  cd /home/duri/DuRiWorkspace && flock -n /tmp/gate_snapshot.lock  ./ops/create_gate_snapshot.sh  >> /var/log/duri/cron.log 2>&1

# 게이트 로테이션 (매일 03:00)
0 3 * * *  cd /home/duri/DuRiWorkspace && flock -n /tmp/rotate_gates.lock   ./ops/rotate_gates.sh        >> /var/log/duri/cron.log 2>&1

# Shadow 훈련장 시작 (토요일=6 제외, 일~금 09:00)
0 9  * * 0-5 cd /home/duri/DuRiWorkspace && flock -n /tmp/shadow.lock ./ops/shadow_on.sh         >> /var/log/duri/cron.log 2>&1

# Coach 미니배치 (15분 간격, 9:10~15:55, 토요일 제외)
10-55/15 9-15 * * 0-5 cd /home/duri/DuRiWorkspace && flock -n /tmp/coach.lock ./ops/coach_batch_run.sh 30 >> /var/log/duri/cron.log 2>&1

# 일일 게이트 리포트 (15:55, 토요일 제외)
55 15 * * 0-5 cd /home/duri/DuRiWorkspace && ./ops/gate_daily_report.sh >> /var/log/duri/cron.log 2>&1

# Shadow 훈련장 중지 (토요일=6 제외, 일~금 16:00)
0 16 * * 0-5 cd /home/duri/DuRiWorkspace && flock -n /tmp/shadow.lock ./ops/shadow_off.sh        >> /var/log/duri/cron.log 2>&1
CRON
echo "✅ 사용자 crontab 버전 생성 완료"

# 3. logrotate 설정 생성
echo ""
echo "3️⃣ **logrotate 설정 생성**"
sudo tee /etc/logrotate.d/duri > /dev/null << 'LOGROTATE'
/var/log/duri/cron.log {
  rotate 14
  daily
  compress
  missingok
  notifempty
  copytruncate
  create 644 duri duri
}
LOGROTATE
echo "✅ logrotate 설정 완료"

# 4. Redis 지속성 설정 (AOF 활성화)
echo ""
echo "4️⃣ **Redis 지속성 설정**"
docker compose exec -T duri-redis redis-cli CONFIG SET appendonly yes
docker compose exec -T duri-redis redis-cli CONFIG SET save "900 1 300 10 60 10000"
echo "✅ Redis AOF 활성화 완료"

# 5. 세이프티 플래그 설정
echo ""
echo "5️⃣ **세이프티 플래그 설정**"
docker compose exec -T duri-redis redis-cli SET canary:enabled 1
docker compose exec -T duri-redis redis-cli SET shadow:enabled 1
echo "✅ 세이프티 플래그 설정 완료"

# 6. 스크립트에 세이프티 플래그 체크 추가
echo ""
echo "6️⃣ **스크립트 세이프티 플래그 체크 추가**"
for script in ops/shadow_on.sh ops/shadow_off.sh ops/coach_batch_run.sh; do
  if [ -f "$script" ]; then
    # 파일 시작 부분에 세이프티 체크 추가
    sed -i '2i# 세이프티 플래그 체크\nif [ "$(docker compose exec -T duri-redis redis-cli GET shadow:enabled)" != "1" ]; then\n  echo "⚠️ Shadow 훈련장 비활성화됨. 종료."\n  exit 0\nfi\n' "$script"
  fi
done
echo "✅ 스크립트 세이프티 플래그 체크 추가 완료"

echo ""
echo "=== ✅ **하드닝 적용 완료** ==="
echo ""
echo "🚀 **적용된 하드닝:**"
echo "   1. docker compose 절대경로 ✅"
echo "   2. 사용자 crontab 버전 생성 ✅"
echo "   3. logrotate 설정 ✅"
echo "   4. Redis AOF 활성화 ✅"
echo "   5. 세이프티 플래그 설정 ✅"
echo "   6. 스크립트 세이프티 체크 추가 ✅"
echo ""
echo "📋 **다음 단계:**"
echo "   - 사용자 crontab 적용: crontab etc_cron_d_duri_user_crontab"
echo "   - 세이프티 플래그로 전체 제어 가능"
echo "   - Redis 지속성으로 재기동 후에도 설정 유지"
