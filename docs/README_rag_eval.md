# RAG Evaluation System Documentation

## 🎯 Overview

DuRi AI의 RAG 시스템 평가 및 검증 도구입니다. 검색 품질을 precision@k와 recall@k 메트릭으로 측정합니다.

## 📊 Current Performance (확정)

- **요통**: hits=2, p@3=0.6667, r@3=0.4000
- **전체**: micro_p@3=0.4667, micro_r@3=0.4118
- **게이트**: PASS (threshold=0.30)

## 🚀 Quick Start

### 원클릭 명령어
```bash
# 전체 평가 실행
make eval

# 게이트 검증
make gate

# 스모크 테스트
make smoke

# k값 스윕 (1,3,5)
make k-sweep

# 결과 아카이브 유지
make archive

# 전체 검증 파이프라인
make test
```

### 직접 실행 예제
```bash
# 평가: 상세 리포트 생성
TIMEOUT_SECS=8 bash scripts/rag_eval.sh .reports/day62/ground_truth_clean.tsv

# 게이트: 품질 검증 + JUnit XML
JUNIT_OUT=.reports/junit.xml K=3 THRESH_P=0.30 QUIET=1 bash scripts/rag_gate.sh .reports/day62/ground_truth_clean.tsv

# 스모크: 간단한 검증
bash tests/eval_smoke.sh

# k-스윕: 다중 성능 비교
bash scripts/rag_k_sweep.sh .reports/day62/ground_truth_clean.tsv
```

## 📁 Output Files

- **TSV**: 평가 결과 상세 출력 (micro precision/recall 포함)
- **JSONL**: 머신 리더블 메타데이터 (CI 대시보드 연동용)
- **재현 정보**: git commit, locale, GT 파일 MD5 해시 포함

## 🔧 Exit Codes

- **0**: 성공
- **1**: 일반적인 오류
- **2**: 입력 파일 문제
- **3**: 데이터 처리 실패

## 🛡️ Robustness Features

- 로케일 자동 감지 및 안전 처리
- 임시파일 자동 정리 (trap)
- 파이프라인 안전 실패 처리
- 입력 매개변수 검증

## ⚙️ Configuration Precedence

`rag_gate.sh`의 설정 우선순위:

1. **환경변수** (최우선)
   ```bash
   THRESH_P=0.60 K=5 bash scripts/rag_gate.sh ground_truth.tsv
   ```

2. **`.gate` 파일** (환경변수가 없을 때만)
   ```bash
   # ground_truth.tsv.gate
   THRESH_P=0.30
   K=3
   ```

3. **기본값** (둘 다 없을 때)
   ```bash
   THRESH_P=0.30, K=3
   ```

### 예시
```bash
# .gate 파일만 있을 때: THRESH_P=0.30 사용
bash scripts/rag_gate.sh ground_truth.tsv

# 환경변수로 덮어쓰기: THRESH_P=0.60 사용
THRESH_P=0.60 bash scripts/rag_gate.sh ground_truth.tsv
```

## 📈 CI Integration

```bash
# 조용한 CI 모드
QUIET=1 make gate

# 원클릭 전체 검증
make test
```

## 🔄 Maintenance Tips

- GT 파일 변경 시 MD5 해시 자동 추적
- k값은 1,3,5 권장 (k=3이 메인 기준)
- 병렬 처리 필요시 GNU parallel 고려 가능

---

**Status**: Production Ready ✅
**Last Update**: $(date)
**Commit**: $(git rev-parse --short HEAD 2>/dev/null || echo 'n/a')
