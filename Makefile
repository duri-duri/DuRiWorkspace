.PHONY: smoke rebuild-control health metrics release rollback runbook backup restore

# 빌드 인자 정의
GIT_SHA := $(shell git rev-parse --short HEAD)
BUILD_DATE := $(shell date -u +%Y-%m-%dT%H:%M:%SZ)
VERSION ?= 1.0.0

smoke:
	COMPOSE_PROJECT_NAME=duriworkspace ./bin/coach_smoke.sh

rebuild-control:
	docker compose -p duriworkspace build --no-cache duri_control && \
	docker compose -p duriworkspace up -d --force-recreate duri_control

health:
	curl -s http://localhost:8083/health | jq .

metrics:
	curl -s http://localhost:8083/metrics | jq .

status:
	docker compose -p duriworkspace ps

logs:
	docker compose -p duriworkspace logs -f duri_control

deploy:
	docker compose -p duriworkspace build duri_control && \
	docker compose -p duriworkspace up -d --force-recreate duri_control

release:
	@echo "=== 🚀 릴리스 규율 ==="
	@echo "현재 Git SHA: $(GIT_SHA)"
	@echo "현재 태그: $(shell git describe --tags --always 2>/dev/null || echo untagged)"
	docker compose -p duriworkspace build \
		--build-arg GIT_SHA=$(GIT_SHA) \
		--build-arg BUILD_DATE=$(BUILD_DATE) \
		--build-arg VERSION=$(VERSION) \
		duri_control
	docker compose -p duriworkspace up -d --force-recreate duri_control
	@echo "✅ 릴리스 완료: $(GIT_SHA)"

rollback:
	@echo "=== 🔄 롤백 ==="
	@read -p "롤백할 이미지 태그(예: duri_control:<tag>): " TAG; \
	docker compose -p duriworkspace pull $$TAG || true; \
	docker compose -p duriworkspace up -d --no-deps --force-recreate --no-build $$TAG; \
	echo "✅ 롤백 완료: $$TAG"

runbook:
	@echo "=== 📚 런북 ==="
	@echo "1. DB 끊김: make status && docker compose -p duriworkspace restart duri-postgres"
	@echo "2. 큐 적체: make logs | grep -i error"
	@echo "3. 레이트리밋: curl -s http://localhost:8083/metrics | grep rate"
	@echo "4. 롤백: make rollback"
	@echo "5. 상태 확인: make status"

backup:
	@echo "=== 💾 백업 ==="
	docker compose -p duriworkspace exec -T duri-postgres pg_dump -U duri duri > backup_$(shell date +%Y%m%d_%H%M%S).sql
	@echo "✅ 백업 완료: backup_$(shell date +%Y%m%d_%H%M%S).sql"

restore:
	@read -p "복원할 백업 파일: " BACKUP; \
	docker compose -p duriworkspace exec -T duri-postgres psql -U duri -d duri < $$BACKUP; \
	echo "✅ 복원 완료: $$BACKUP"

# 이미지 태깅/프로모션
tag-staging:
	@echo "=== 🏷️ 스테이징 태깅 ==="
	docker tag duriworkspace-duri_control:latest duriworkspace-duri_control:staging
	docker tag duriworkspace-duri_control:latest duriworkspace-duri_control:$(GIT_SHA)
	@echo "✅ 스테이징 태깅 완료: staging, $(GIT_SHA)"

promote-prod:
	@echo "=== 🚀 프로덕션 승격 ==="
	docker tag duriworkspace-duri_control:staging duriworkspace-duri_control:prod
	@echo "✅ 프로덕션 승격 완료: prod"

rollback-staging:
	@echo "=== 🔄 스테이징 롤백 ==="
	@IMAGE_TAG=staging docker compose -p duriworkspace pull duri_control || true
	@IMAGE_TAG=staging docker compose -p duriworkspace up -d --no-deps --force-recreate duri_control
	@echo "✅ 스테이징 롤백 완료 → tag=staging"

rollback-prod:
	@echo "=== 🔄 프로덕션 롤백 ==="
	docker compose -p duriworkspace up -d --force-recreate --no-build duri_control:prod
	@echo "✅ 프로덕션 롤백 완료"

# DB 마이그 자동화
migrate-up:
	@echo "=== 🗄️ DB 마이그레이션 ==="
	@if [ -f "migrations/up.sql" ]; then \
		docker compose -p duriworkspace exec -T duri-postgres psql -U duri -d duri -f /app/migrations/up.sql; \
		echo "✅ 마이그레이션 완료"; \
	else \
		echo "⚠️ migrations/up.sql 없음, 건너뜀"; \
	fi

migrate-down:
	@echo "=== 🔄 DB 마이그레이션 롤백 ==="
	@if [ -f "migrations/down.sql" ]; then \
		docker compose -p duriworkspace exec -T duri-postgres psql -U duri -d duri -f /app/migrations/down.sql; \
		echo "✅ 마이그레이션 롤백 완료"; \
	else \
		echo "⚠️ migrations/down.sql 없음, 건너뜀"; \
	fi

release-safe: migrate-up release
	@echo "✅ 안전한 릴리스 완료"

# 배포 이벤트 기록 (라벨 지원)
record-deployment:
	@echo "=== 📊 배포 이벤트 기록 ==="
	@bash scripts/push_deploy_event.sh
	@echo "✅ 배포 이벤트 기록 완료"

release-with-metrics: release record-deployment
	@echo "✅ 메트릭 포함 릴리스 완료"
