# 🚀 DuRi Observability Green Path

## Quick Start (3 Steps)

### 1. Local Development / Pre-commit
```bash
make secret-perms-relaxed      # 로컬 편집/커밋 전
make monitoring-check          # 컨테이너 가독성 + AM 헬스
make status-monitoring         # 전체 상태
```

### 2. Production Deployment
```bash
make alertmanager-apply-secure # 운영 반영(권한 enforce + 리로드)
```

### 3. CI / New Environment
```bash
make SKIP_WEBHOOK_GUARD=1 monitoring-check  # CI/새 환경
```

## Available Targets

- `monitoring-check`: Check container readability & AM health (format check skipped in secure/CI)
- `status-monitoring`: Print Prometheus/Alertmanager/Grafana health and targets
- `alertmanager-reload-monitoring`: Reload Alertmanager safely
- `secret-perms-relaxed`: Set webhook perms for local edits (644)
- `alertmanager-apply-secure`: Enforce secure perms (600) and reload AM
- `ci-smoke`: CI smoke (green path)
- `alertmanager-validate`: Validate Alertmanager config syntax

## Variables

- `ALERTMANAGER_CONTAINER`: Auto-detected or set to `alertmanager`
- `SKIP_WEBHOOK_GUARD`: Set to `1` for CI environments

## Security Features

- ✅ Placeholder webhook detection
- ✅ Container readability validation
- ✅ Secret file permission management
- ✅ Pre-commit hook blocking webhook commits
- ✅ macOS/Linux compatibility
- ✅ Config syntax validation before reload

## 🎯 운영 핸드북 (2줄)

### 로컬/커밋 전
🟢 set ops/observability/slack_webhook_url -> owner duri:duri, mode 644
ℹ️ host perm: 644
⚠️ format not verified (non-fatal)
✅ readable in container
✅ Alertmanager healthy

### 운영 적용
🔒 set ops/observability/slack_webhook_url -> owner 65534:65534, mode 600
Checking '/etc/alertmanager/alertmanager.yml'  SUCCESS
Found:
 - global config
 - route
 - 0 inhibit rules
 - 3 receivers
 - 0 templates

ℹ️ host perm: 600
ℹ️ host can't read (secure mode) — skipping placeholder check
✅ readable in container
✅ Alertmanager healthy
Alertmanager reloaded ✅
✅ secure apply done
=== DuRi Workspace Status ===
Prometheus: Prometheus Server is Ready.

Alertmanager: OK
Grafana: ok - 12.2.0
Targets: 12
Webhook file: 600 ops/observability/slack_webhook_url

## 🔧 고급 설정

### 이미지 다이제스트 고정 (재현성 극대화)
모든 모니터링 이미지가 다이제스트로 고정되어 있어 새 환경에서도 동일한 버전이 실행됩니다.

### WEBHOOK_FILE 변수화 (유지보수성 향상)
❌ /custom/path/webhook not found

### CI 환경 변수
🟢 set ops/observability/slack_webhook_url -> owner duri:duri, mode 644
ℹ️ host perm: 644
⚠️ format not verified (non-fatal)
✅ readable in container
✅ Alertmanager healthy

## 🚀 캔어리 테스트
Sending canary alert…
❌ Failed to send canary alert

## 🔍 캔어리 테스트 이해

**캔어리 성공 = AM ↔ Slack 전달 시도 OK, 은 웹훅 문제**

- Sending canary alert via amtool…
❌  container not running 성공 시: Alertmanager가 정상적으로 알림을 처리하고 있음
- 로그에  표시: Slack 웹훅이 비활성화되었거나 다른 워크스페이스에 속함
- 해결: 실제 워크스페이스의 살아있는 Incoming Webhook URL로 교체
