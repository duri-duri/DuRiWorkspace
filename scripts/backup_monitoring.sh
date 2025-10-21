#!/bin/bash

# DuRi 모니터링 데이터 백업 스크립트
# 사용법: ./backup_monitoring.sh [백업경로]

set -euo pipefail

# 기본 설정
BACKUP_DIR="${1:-/home/duri/backups/monitoring}"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_PATH="${BACKUP_DIR}/duri_monitoring_${DATE}"

# 로깅 함수
log_info() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] INFO: $1"
}

log_error() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] ERROR: $1" >&2
}

log_info "DuRi 모니터링 데이터 백업 시작"

# 백업 디렉터리 생성
mkdir -p "${BACKUP_PATH}"

# 1. Prometheus 데이터 백업
log_info "Prometheus 데이터 백업 중..."
if docker compose -p duriworkspace exec -T prometheus tar -czf - -C /prometheus . > "${BACKUP_PATH}/prometheus_data.tar.gz"; then
    log_info "Prometheus 데이터 백업 완료"
else
    log_error "Prometheus 데이터 백업 실패"
fi

# 2. Grafana 데이터 백업
log_info "Grafana 데이터 백업 중..."
if docker compose -p duriworkspace exec -T grafana tar -czf - -C /var/lib/grafana . > "${BACKUP_PATH}/grafana_data.tar.gz"; then
    log_info "Grafana 데이터 백업 완료"
else
    log_error "Grafana 데이터 백업 실패"
fi

# 3. 설정 파일 백업
log_info "설정 파일 백업 중..."
cp -r prometheus.yml "${BACKUP_PATH}/"
cp -r prometheus/rules "${BACKUP_PATH}/"
cp -r ops/observability "${BACKUP_PATH}/"
cp -r grafana/provisioning "${BACKUP_PATH}/"
cp docker-compose.monitoring.yml "${BACKUP_PATH}/"
log_info "설정 파일 백업 완료"

# 4. 백업 메타데이터 생성
cat > "${BACKUP_PATH}/backup_info.txt" << EOF
DuRi 모니터링 백업 정보
=======================
백업 일시: $(date)
백업 경로: ${BACKUP_PATH}
Docker Compose 프로젝트: duriworkspace

포함된 데이터:
- Prometheus 메트릭 데이터 (prometheus_data.tar.gz)
- Grafana 대시보드 및 설정 (grafana_data.tar.gz)
- Prometheus 설정 파일 (prometheus.yml, prometheus/rules/)
- Alertmanager 설정 (ops/observability/)
- Grafana 프로비저닝 설정 (grafana/provisioning/)
- Docker Compose 모니터링 설정 (docker-compose.monitoring.yml)

복원 방법:
1. 설정 파일들을 원래 위치에 복사
2. Docker 볼륨에 데이터 압축 해제:
   - Prometheus: docker compose exec prometheus tar -xzf - -C /prometheus < prometheus_data.tar.gz
   - Grafana: docker compose exec grafana tar -xzf - -C /var/lib/grafana < grafana_data.tar.gz
3. 모니터링 스택 재시작: docker compose -f docker-compose.yml -f docker-compose.monitoring.yml --profile monitoring up -d
EOF

# 5. 백업 압축
log_info "백업 압축 중..."
cd "${BACKUP_DIR}"
tar -czf "duri_monitoring_${DATE}.tar.gz" "duri_monitoring_${DATE}"
rm -rf "duri_monitoring_${DATE}"
log_info "백업 압축 완료: duri_monitoring_${DATE}.tar.gz"

# 6. 오래된 백업 정리 (30일 이상)
log_info "오래된 백업 정리 중..."
find "${BACKUP_DIR}" -name "duri_monitoring_*.tar.gz" -mtime +30 -delete
log_info "오래된 백업 정리 완료"

log_info "DuRi 모니터링 데이터 백업 완료: ${BACKUP_DIR}/duri_monitoring_${DATE}.tar.gz"

# 백업 크기 확인
BACKUP_SIZE=$(du -h "${BACKUP_DIR}/duri_monitoring_${DATE}.tar.gz" | cut -f1)
log_info "백업 크기: ${BACKUP_SIZE}"
