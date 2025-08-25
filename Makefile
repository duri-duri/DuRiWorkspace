SHELL := /bin/bash
.SHELLFLAGS := -eu -o pipefail -c
.ONESHELL:
MAKEFLAGS += --no-builtin-rules

.PHONY: test test-apply test-extended test-ro-hdd test-all test-all-ci clean

test:
	@bash tests/test_apply.sh

# 트레이스 포함 테스트
test-trace:
	@TRACE=1 bash tests/test_apply.sh

# 손상→재검증까지 실행
test-extended:
	@APPLY_EXT=1 bash tests/test_apply.sh

# 읽기전용 HDD 시뮬 테스트 (샌드박스에서만 수행)
test-ro-hdd:
	@bash tests/test_ro_hdd.sh

# 전체 테스트 (기본 + 확장 + 읽기전용)
test-all:
	@$(MAKE) -s test
	@$(MAKE) -s test-extended
	@$(MAKE) -s test-ro-hdd

# CI 모드 테스트 (RO 자동 스킵)
test-all-ci:
	@$(MAKE) -s clean
	@$(MAKE) -s test && $(MAKE) -s verify-logs
	@$(MAKE) -s clean
	@APPLY_EXT=1 $(MAKE) -s test-extended && $(MAKE) -s verify-logs
	@# RO는 sudo 없으면 자동 SKIP
	@$(MAKE) -s clean
	@$(MAKE) -s test-ro-hdd || true
	@echo "CI OK"



clean:
	@rm -rf .test-artifacts /tmp/duri-applytest-* || true

.PHONY: verify-logs

verify-logs:
	@echo "[CHECK] step1.json"
	@jq -e '(.rc|tonumber)==0' .test-artifacts/step1.json >/dev/null
	@echo "[CHECK] step2.json"
	@jq -e '(.rc|tonumber)==0 and ((.full_bad? // 0 | tonumber)==0)' .test-artifacts/step2.json >/dev/null
	@echo "[CHECK] mismatch (if exists)"
	@([ -f .test-artifacts/step3_mismatch.json ] && \
	  jq -e '((.full_bad? // 0 | tonumber) > 0)' \
	     .test-artifacts/step3_mismatch.json >/dev/null) || true
	@echo "OK"
