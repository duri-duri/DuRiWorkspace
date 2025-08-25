SHELL := /bin/bash
.SHELLFLAGS := -eu -o pipefail -c
.ONESHELL:
MAKEFLAGS += --no-builtin-rules

.PHONY: test test-apply test-extended test-ro-hdd test-all test-all-ci test-extra test-enospc check-env report smoke clean

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

# === Phase-2 ===
# 1) 추가 케이스 6종(동시성/크래시/매트릭스/가드/유니코드/벌크)
test-extra:
	@RUN_EXTRA_CASES=1 bash tests/test_apply.sh

# 2) ENOSPC(tmpfs 8MB, sudo 필요) — 필요 시에만 실행
test-enospc:
	@sudo -n true >/dev/null 2>&1 || { echo "[SKIP] sudo required for ENOSPC"; exit 0; }
	@RUN_ENOSPC=1 bash tests/test_ro_hdd.sh

# === Micro utilities ===
# 의존성 점검(부족시 127로 fail)
check-env:
	@bash -c 'set -e; for c in jq sha256sum rsync mktemp dd awk sed grep tr head cp rm timeout; do \
	  command -v $$c >/dev/null || { echo "[ERR] missing: $$c"; exit 127; }; done; echo "env OK";'

# JSON 요약 리포트(존재하는 *.json만)
report:
	@bash -c 'shopt -s nullglob; \
	for f in .test-artifacts/*.json; do \
	  [ -s $$f ] || continue; \
	  jq -r "\"rc=\(.rc // 0) full_ok=\(.full_ok? // 0) full_bad=\(.full_bad? // 0) incr_ok=\(.incr_ok? // 0) incr_bad=\(.incr_bad? // 0) :: $${f}\"" $$f; \
	done || true'

# 빠른 스모크(회귀+검증)
smoke: clean test verify-logs


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
