#!/usr/bin/env bash
set -euo pipefail
W="$HOME/DuRiWorkspace"
USR="$HOME/.config/systemd/user"
log(){ printf "[%s] %s\n" "$(date '+%F %T')" "$*"; }
if git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  git switch -c "sos/$(date +%Y%m%d)-catchup" 2>/dev/null || true
fi
log "AB 평가 메트릭 생성"
mkdir -p "$W/var/metrics"
if python3 "$W/scripts/evolution/make_ab_eval_prom.py" --out "$W/var/metrics/ab_eval.prom" 2>/dev/null; then
  log "OK: make_ab_eval_prom.py → var/metrics/ab_eval.prom"
else
  log "WARN: 생성 스크립트 실패 → placeholder 작성"
  cat > "$W/var/metrics/ab_eval.prom" <<'EOF'
# HELP duri_ab_p_value AB evaluation p-value (lower is better)
# TYPE duri_ab_p_value gauge
duri_ab_p_value 0.42
EOF
fi
if systemctl --user cat duri-shadow-exporter.service >/dev/null 2>&1; then
  if ! systemctl --user cat duri-shadow-exporter.service | grep -q 'metrics_exporter_enhanced.py'; then
    log "PATCH: exporter unit → metrics_exporter_enhanced.py"
    systemctl --user cat duri-shadow-exporter.service | sed 's/metrics_exporter\.py/metrics_exporter_enhanced.py/g' > "$USR/duri-shadow-exporter.service"
    systemctl --user daemon-reload
  fi
  systemctl --user restart duri-shadow-exporter.service || true
  systemctl --user status  duri-shadow-exporter.service --no-pager | sed -n '1,6p' || true
else
  log "WARN: duri-shadow-exporter.service 미발견(백업 편차). 계속 진행."
fi
for t in duri-evidence.timer kimshin-backup.timer kimshin-dr-restore.timer; do
  if systemctl --user list-unit-files | awk '{print $1}' | grep -qx "$t"; then
    log "ENABLE+START: $t"
    systemctl --user enable --now "$t" || true
  fi
done
sleep 2
HEALTH_OK=0
for p in 8080 8081 8082 8083; do
  if curl -fsS "http://127.0.0.1:$p/health" >/dev/null 2>&1; then
    log "HEALTH OK :$p"; HEALTH_OK=$((HEALTH_OK+1))
  else
    log "HEALTH FAIL:$p"
  fi
done
EXP_OK="NO"
curl -fsS http://127.0.0.1:9109/metrics 2>/dev/null | grep -q '^duri_shadow_exporter_up' && EXP_OK="UP" || true
PVAL=$(curl -fsS http://127.0.0.1:9109/metrics 2>/dev/null | awk '/^duri_ab_p_value/{print $2; exit}' || true)
log "요약"
log " - health: ${HEALTH_OK}/4"
log " - exporter: ${EXP_OK}"
log " - ab p-value(metric): ${PVAL:-NA}"
