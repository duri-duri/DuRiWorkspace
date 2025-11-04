# L4 Evolution 시스템 - 실행 플랜 및 문서

## 개요

**현 위치**: L3.5 (자가 배포/검증 자동화 + 수동 지시 하에 안정 동작)  
**목표**: L4.1 "자율 실행 → 자기평가 → 프로모션 게이트 통과"  
**예상 도달 확률**: 7일 내 p≈0.62, 14일 내 p≈0.82

## 승격 함수

### L4 프로모션 스코어

```
prom_score = 0.35·NDCG@3 + 0.25·p@3 - 0.20·halluc_rate - 0.10·regression_rate
            - 0.05·p95_latency_z + 0.05·cost_eff + 0.10·oracle_recall
```

**최대 기울기 (∂score/∂metric)**:
- `∂/∂NDCG@3 = +0.35` (1순위 레버)
- `∂/∂halluc_rate = -0.20` (2순위 레버)
- `∂/∂p@3 = +0.25` (3순위 레버)

### L4.1 프로모션 스코어 (단순화)

```
L4_score = 0.35·p@3 + 0.20·MRR + 0.15·NDCG@3 - 0.20·halluc_rate
          - 0.05·cost_norm + 0.05·stability
```

**합격선**: L4_score ≥ 0.70, 동시에 `halluc_rate ≤ 0.08`, `stability ≥ 0.90`

## L4 Gate 조건

### 품질 요구사항
- NDCG@3 ≥ 0.78
- p@3 ≥ 0.72
- halluc_rate ≤ 2.5%
- regression_rate ≤ 1.0%

### 신뢰성 요구사항
- 7일 error_budget_burn OK
- p95 latency ≤ 기준선+10%
- self-check 통과율 ≥ 0.98

### 자율행동 요구사항
- "실험 설계 → 후보 생성 → 그라운드트루스 평가 → PR 생성" 최소 1일 3회

### 안전장치
- 자동 PR은 **draft + label: `needs-human-eyes`**
- 병합은 Gate 통과 시에만 `promotion` 라벨로 승격

## 5단계 실행 플랜 (Day21-25)

### Day21 - 파이프라인 골격
- [x] `EvolutionSession` 스키마 확정 (JSONL + SQLite)
- [x] **Promotion Gate v2**: 승격함수 계산 + 메트릭 export
- [ ] **Shadow Runner**: `shadow_proxy` 비율 10%→30% 가변

### Day22 - 데이터/지표의 기울기 키우기
- [ ] **Retriever 튜닝**: 쿼리확장, BM25+embedding 하이브리드, rerank N=50→100
- [ ] **Verifier 2단 가드**: 근거문서 인용 강제 체크, 스키마 검증
- 기대: ΔNDCG@3 +0.05~+0.09, Δhalluc -1.0~-1.8pp (p≈0.7)

### Day23 - 자동 PR/릴리즈 배관
- [ ] `auto_pr.py`: 변경점 요약 + 리포트 첨부로 draft PR 생성
- [ ] **Canary Rule**: `prom_score ≥ τ`일 때만 `promotion` 라벨 자동 부여
- [ ] **Rollback Hook**: 실패 시 `recover_coldsync.sh` 호출

### Day24 - 회귀 방지 & 비용/지연 최적화
- [ ] **Regression Sentinel**: 골든셋 회귀 테스트 상시 수행
- [ ] Latency/Cost 옵스: 캐시 키 설계, rerank depth 적응형
- 기대: regression_rate -1pp, p95 z-score -0.3~-0.5

### Day25 - 전일 릴리즈 검증 + 승격 리허설
- [ ] 24h 드라이런 결과로 승격 시뮬레이션 리포트 생성
- [ ] AC 미달 항목 자동 하이라이트 및 개입 권고

## 태스크 3종 (L4.1 자율 실행)

### 1. obs-rule-tune
- Prometheus 룰 임계치 ±x% 탐색
- `promtool check rules` → Canary 재시작 → 알람 성능 p@3 개선 측정
- 기대: `p@3 +0.05~0.08`, `stability +0.05`

### 2. doc→PR
- `docs/ops/*` 요약/정리 → 변경분 패치 → `git add/commit` → PR 초안 생성
- 기대: `halluc_rate -0.01~0.02`, `MRR +0.02`

### 3. config-patch
- Service unit의 경미 튜닝 제안 및 draft 적용 → 검증
- 기대: 안정성 향상

## 시스템 구조

### 타이머/큐 시스템
- `duri-evolve.timer` (15분) → `duri-evolve@.service` (작업 ID 파라미터화)
- 작업 큐: `var/evolution/queue/*.jsonl`

### 게이트 실행기
- 입력: 실행 후 메트릭 (`metrics/*.jsonl`), 해시, 로그 키워드
- 출력: `PROMOTE` | `ROLLBACK` | `RETRY(x)` + 사유
- 행동:
  - PROMOTE: 태그 `evo-pass-YYYYmmdd-HHMM`, 문서 스냅샷, (선택)main에 머지
  - ROLLBACK: 직전 태그로 복구 + 실패 리포트 저장

### 증거 저장
- `var/evolution/EV-<ts>/`에 `plan.md`, `run.log`, `metrics.json`, `gate.json`, `patch.diff`, `TAG`

## 실행 체크리스트

```bash
# 1. 브랜치 생성 및 시작
bash scripts/evolution/start_l4_evolution.sh

# 2. 타이머 설정 (다음 단계)
bash scripts/evolution/setup_l4_timer.sh

# 3. 첫 태스크 실행 (다음 단계)
bash scripts/evolution/run_task.sh obs-rule-tune

# 4. Gate 검증
python3 scripts/evolution/promotion_gate_v2.py --dryrun --window 24h --gate L4.1

# 5. coldsync 검증
bash scripts/bin/verify_coldsync_final.sh
```

## 분신화 로드맵 (L4.5 준비)

### Shards (분신)
- `obs-tuner`: NDCG/Recall 상승 전담
- `doc-writer`: 문서 생성/검증
- `config-guard`: 설정 최적화

### 파라미터 다양화
- 각 분신에 탐색률(ε), 보수성(β), 비용 한도(C) 다르게 설정

### 융합기
- 결과들의 게이트 스코어 상위 1개만 PROMOTE, 나머지는 학습 데이터로 축적

## 리스크 & 완화

- **R1: 잘못된 탐색** → Canary 10%, `error-budget-burn` 룰 상한
- **R2: 환상률 스파이크** → 게이트에서 `halluc_rate > 0.08` 즉시 불합격+롤백
- **R3: 파일 동시성** → 큐 소비를 단일 워커로, 락파일 사용
- **R4: 로그 유실** → 실행 시작 전 `tee`로 raw 로그 미러

## 예상 성공 확률

- **L4 도달 10일 내**: p≈0.72
- **L4.1 도달 7일 내**: p≈0.62
- **L4.1 도달 14일 내**: p≈0.82
- **L5 도달 30일 내**: p≈0.38 (L4 달성 전제)

---

**시작일**: 2025-11-04  
**목표**: L4.1 "자율 실행 → 자기평가 → 프로모션 게이트 통과"  
**상태**: 🚀 진행 중

