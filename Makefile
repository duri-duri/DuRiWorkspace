# DuRiWorkspace Makefile
# 로컬 개발 편의 명령어들

.PHONY: metrics test clean help

# 메트릭 리포트 생성 (로컬)
metrics:
	@echo "🧪 Running metrics tests..."
	python -m pytest tests/test_metrics.py -v
	@echo "📊 Generating metrics report..."
	python - <<'PY'
	from insight.metrics import evaluate_text
	import json
	sample = [
	  'The quick brown fox jumps over the lazy dog.',
	  'A fast brown fox leaps over a sleepy canine.',
	  'The dog is lazy and sleeps all day.',
	  'Innovative solutions require creative thinking and comprehensive analysis.',
	  'This is a very short text.',
	]
	results=[]
	for i,t in enumerate(sample):
	  r=evaluate_text(t, detailed=True); r['text']=t; r['index']=i; results.append(r)
	report={'total_samples':len(sample),'average_composite_score':sum(x['composite_score'] for x in results)/len(results),
	        'results':results,'summary':{'highest_score':max(results,key=lambda x:x['composite_score']),
	        'lowest_score':min(results,key=lambda x:x['composite_score']),
	        'score_range':max(x['composite_score'] for x in results)-min(x['composite_score'] for x in results)}}
	open('metrics_report.json','w').write(json.dumps(report,indent=2))
	print('✅ metrics_report.json written')
	PY
	@echo "✅ Metrics report generated: metrics_report.json"

# 모든 테스트 실행
test:
	@echo "🧪 Running all tests..."
	python -m pytest tests/ -v

# 캐시 및 임시 파일 정리
clean:
	@echo "🧹 Cleaning up..."
	rm -f metrics_report.json
	rm -rf __pycache__/
	rm -rf .pytest_cache/
	find . -name "*.pyc" -delete
	find . -name "*.pyo" -delete

# 도움말
help:
	@echo "DuRiWorkspace Development Commands:"
	@echo ""
	@echo "  make metrics    - Generate local metrics report"
	@echo "  make test       - Run all tests"
	@echo "  make clean      - Clean cache and temp files"
	@echo "  make help       - Show this help"
	@echo ""
	@echo "Phase 19-1: 메트릭 리포트 CI 구현 완료 ✅"