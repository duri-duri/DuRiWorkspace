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
