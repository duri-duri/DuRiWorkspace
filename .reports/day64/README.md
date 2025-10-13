# Day 64: 3도메인 통합 성능 분석

## 🎯 목표
- RAG 검색 품질 상승 (현재 micro_p@3=0.3333 → 목표 0.45~0.50)
- 3도메인 통합 성능 분석 및 개선

## 📊 현재 베이스라인
- micro_p@3: 0.3333
- micro_r@3: 0.2941
- macro_p@3: 0.3333
- macro_r@3: 0.2941

## 🔬 개선 실험 계획
1. Query expand: 동의어/약어 사전 적용
2. BM25 + dense hybrid 가중치 튜닝 (α 스윕: 0.3, 0.5, 0.7)
3. Re-rank 적용: top-20 → cross-encoder 재정렬 → top-3

## 📈 목표 지표
- micro_p@3 ≥ 0.45
- 게이트 상향: THRESH_P=0.45

