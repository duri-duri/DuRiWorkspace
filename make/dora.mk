# DORA 메트릭 관련 Makefile

# 배포 이벤트 기록 (라벨 지원)
record-deployment:
	@echo "=== 📊 배포 이벤트 기록 ==="
	@bash scripts/push_deploy_event.sh
	@echo "✅ 배포 이벤트 기록 완료"

release-with-metrics: release record-deployment
	@echo "✅ 메트릭 포함 릴리스 완료"
