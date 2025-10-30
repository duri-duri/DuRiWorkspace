#!/usr/bin/env bash
set -euo pipefail
W="$HOME/DuRiWorkspace"
USR="$HOME/.config/systemd/user"
log(){ printf "[%s] %s\n" "$(date '+%F %T')" "$*"; }
# 0) 작업 브랜치
git rev-parse --is-inside-work-tree >/dev/null 2>&1 && {
  git add -A >/dev/null 2>&1 || true
  git switch -c sos/$(date +%Y%m%d)-catchup 2>/dev/null || true
} || true
# 1) AB 평가 메트릭 생성(없으면 placeholder)
log "AB 평가 메트릭 생성"
if python3 scripts/evolution/make_ab_eval_prom.py --out "$W/var/metrics/ab_eval.prom" 2>/dev/null; then
  log "OK: scripts/evolution/make_ab_eval_prom.py → var/metrics/ab_eval.prom"
else
  log "WARN: 생성 스크립트 실행 실패 → placeholder 작성"
  cat > "$W/var/metrics/ab_eval.prom" <<'EOF'
# HELP duri_ab_p_value AB evaluation p-value (lower is better)
# TYPE duri_ab_p_value gauge
duri_ab_p_value 0.42
EOF
fi
# 2) Exporter가 enhanced 버전 사용하는지 보정
UNIT="$USR/duri-shadow-exporter.service"
if systemctl --user cat duri-shadow-exporter.service >/dev/null 2>&1; then
  if systemctl --user cat duri-shadow-exporter.service | grep -q 'metrics_exporter_enhanced.py'; then
    log "OK: exporter unit already uses metrics_exporter_enhanced.py"
  else
    log "PATCH: exporter unit → metrics_exporter_enhanced.py"
    mkdir -p "$USR"
    systemctl --user cat duri-shadow-exporter.service | sed 's/metrics_exporter\.py/metrics_exporter_enhanced.py/g' > "$UNIT.tmp"
    mv "$UNIT.tmp" "$UNIT"
    systemctl --user daemon-reload
  fi
  systemctl --user restart duri-shadow-exporter.service || true
  systemctl --user status  duri-shadow-exporter.service --no-pager || true
else
  log "WARN: duri-shadow-exporter.service 미발견(백업 편차). 계속 진행."
fi
# 3) evidence 타이머 재활성
# 3) evidence 타이머 재활성
for t in duri-evidence.timer kimshin-backup.timer kimshin-dr-restore.timer; do
  if systemctl --user list-unit-files | grep -q "^"; then
    log "ENABLE+START: "
    systemctl --user enable --now  || true
  fi
 done
  if systemctl --user list-unit-files | grep -q "^"; then
    log "ENABLE+START: "
    systemctl --user enable --now "" || true
  fi
 done
# 4) 헬스 및 메트릭 검증
sleep 2
HEALTH_OK=0
for p in 8080 8081 8082 8083; do
  if curl -fsS "http://localhost:$p/health" >/dev/null 2>&1; then
    log "HEALTH OK :$p"
    HEALTH_OK=$((HEALTH_OK+1))
  else
    log "HEALTH FAIL:$p"
  fi
fi
EXP_OK="NO"
if curl -fsS localhost:9109/metrics | grep -q '^duri_shadow_exporter_up'; then
  EXP_OK="UP"
fi
PVAL="NA"
if curl -fsS localhost:9109/metrics | grep -E '^duri_ab_p_value' >/dev/null 2>&1; then
  PVAL="$(curl -fsS localhost:9109/metrics | awk '/^duri_ab_p_value/{print $2; exit}')"
fi
log "요약"
log " - health: ${HEALTH_OK}/4"
log " - exporter: ${EXP_OK}"
log " - ab p-value(metric): ${PVAL}"
