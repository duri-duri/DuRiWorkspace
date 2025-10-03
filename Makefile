.PHONY: eval gate smoke clean k-sweep archive

# 변수 정의 - 기본값 설정
GT ?= .reports/day62/ground_truth_clean.tsv
K ?= 3
THRESH_P ?= 0.30
QUIET ?= 1

# 의존성 정의
SCRIPTS = scripts/rag_eval.sh scripts/rag_gate.sh
TESTS = tests/eval_smoke.sh

# 출력 파일 정리
clean:
	@rm -f .reports/last_eval.tsv
	@find .reports -name "eval_*.tsv" -type f | head -10 | xargs rm -f

# 평가 실행 - 결과를 파일로 저장 후 요약 표시
eval: $(GT) $(SCRIPTS)
	@mkdir -p .reports
	@TIMEOUT_SECS=8 bash scripts/rag_eval.sh "$(GT)" > .reports/last_eval.tsv || { echo "eval failed"; exit 1; }
	@tail -n 10 .reports/last_eval.tsv

# 게이트 검증 - 테스트 통과 여부 확인
gate: $(GT) $(SCRIPTS)
	@K="$(K)" THRESH_P="$(THRESH_P)" QUIET="$(QUIET)" bash scripts/rag_gate.sh "$(GT)"

# 스모크 테스트 - 전체 파이프라인 검증
smoke: $(GT) $(SCRIPTS) $(TESTS)
	@bash tests/eval_smoke.sh

# k-스윕 검증 - 여러 k값으로 성능 비교
k-sweep: $(GT) $(SCRIPTS)
	@bash scripts/rag_k_sweep.sh "$(GT)"

# 결과 아카이브 편의 (최근 결과 심볼릭 링크)
archive:
	@find .reports -name "eval_*.tsv" -type f | head -1 | xargs -I {} ln -sf {} .reports/last_eval.tsv || true
	@find .reports -name "eval_*.jsonl" -type f | head -1 | xargs -I {} ln -sf {} .reports/last_eval.jsonl || true

# 전체 검증 - 모든 타겟 순차 실행
test: clean eval gate smoke
	@echo "All tests passed successfully!"
