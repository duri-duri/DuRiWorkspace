.PHONY: up down restart smoke ci logs

up:        ## 필수 서비스 기동
	docker compose up -d duri_control duri_brain

down:
	docker compose down

restart:
	docker compose restart duri_control duri_brain

smoke:     ## 스모크 테스트
	bash scripts/smoke_health_metrics.sh

ci:        ## CI에서 호출
	bash scripts/ci_health_check.sh

logs:
	docker compose logs -f --tail=200 duri_control duri_brain
