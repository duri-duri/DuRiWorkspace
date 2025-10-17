# tools/incident_runbook.md
# PZTA-CRA 3대 사고 런북

## 🚨 1. Conflict 발생 (Core↔RAG 충돌)

### 증상
- 알람: `CoreRagConflictSpike` 발생
- 로그: `core_conflict_blocked` 이벤트 증가

### 즉시 조치 (0-5분)
```bash
# 1) 자동 Core-only 강등
curl -X POST "$DURI_ENDPOINT/api/runtime/config" \
  -H "Authorization: Bearer $DURI_TOKEN" \
  -d '{"conflict_mode": "CORE_ONLY"}'

# 2) 이슈 생성
gh issue create --title "Core-RAG Conflict Detected" \
  --body "Conflict spike detected at $(date). Auto-switched to CORE_ONLY mode."
```

### 근본 원인 조사 (5-30분)
```sql
-- 충돌 패턴 분석
SELECT kind, details->>'payload' as conflict_data, created_at
FROM audit_ledger
WHERE kind = 'core_conflict_blocked'
ORDER BY created_at DESC LIMIT 10;
```

### 복구 절차 (30분-2시간)
1. **해당 캡슐 묶음 리뷰**: 충돌 발생 캡슐들 식별
2. **원인 문서 갱신**: RAG 문서 또는 Core 값 수정
3. **카나리 재개**: SPRT로 점진적 복구

---

## ⚠️ 2. Evidence < τ (근거 부족)

### 증상
- 알람: `EvidenceAttachLow` 발생
- 응답: `ABSTAIN` 상태 증가

### 즉시 조치 (0-5분)
```bash
# 1) 재탐색 큐 우선순위 ↑
curl -X POST "$DURI_ENDPOINT/api/rag/priority" \
  -H "Authorization: Bearer $DURI_TOKEN" \
  -d '{"boost_factor": 2.0}'

# 2) 근거 확충 모드 활성화
curl -X POST "$DURI_ENDPOINT/api/runtime/config" \
  -H "Authorization: Bearer $DURI_TOKEN" \
  -d '{"tau_evidence": 0.85}'
```

### 근본 원인 조사 (5-30분)
```sql
-- 근거 부족 패턴 분석
SELECT
  capsule->'fusion'->>'w' as fusion_weight,
  capsule->'rag' as rag_docs,
  created_at
FROM answer_ledger
WHERE capsule->'fusion'->>'w'::float < 0.92
ORDER BY created_at DESC LIMIT 10;
```

### 복구 절차 (30분-2시간)
1. **근거 확충**: RAG 문서 품질 개선
2. **SPRT 재평가**: 점진적 임계값 복구
3. **모니터링 강화**: 근거 품질 지표 추적

---

## 🔥 3. Bundle 검증 실패

### 증상
- 알람: `BundleVerifyFail` 발생
- 로그: 번들 해시 불일치

### 즉시 조치 (0-5분)
```bash
# 1) 즉시 직전 milestone 핀으로 롤백
LATEST_TAG=$(git describe --tags --match "milestone/*" --abbrev=0)
git checkout $LATEST_TAG

# 2) 실패 아티팩트 해시 추적
echo "Bundle verify failed at $(date)" | \
curl -X POST "$DURI_ENDPOINT/api/audit" \
  -H "Authorization: Bearer $DURI_TOKEN" \
  -d '{"kind": "bundle_verify_fail", "details": {"timestamp": "'$(date -Iseconds)'"}}'
```

### 근본 원인 조사 (5-30분)
```bash
# 1) 번들 무결성 재검증
sha256sum -c HASH.txt

# 2) 머클 루트 확인
python3 tools/build_bundle.py --verify-only
```

### 복구 절차 (30분-2시간)
1. **새 번들 빌드**: 수정된 Core로 재빌드
2. **검증 통과 확인**: 모든 체크 통과 후 배포
3. **롤백 경로 확보**: 이전 안정 버전 백업

---

## 📊 모니터링 체크리스트

### 매시간 확인
- [ ] `bundle_verify_fail_total` = 0
- [ ] `core_rag_conflict_total` = 0
- [ ] `rag_evidence_attach_rate` ≥ 0.95
- [ ] `reproducible_capsule_rate` ≥ 0.999

### 매일 확인
- [ ] `staleness_days_core_max` ≤ 180
- [ ] 캡슐 재현성 스팟체크 ≥ 99.9%
- [ ] 감사 해시체인 무결성

### 매주 확인
- [ ] DR 드릴: 최신 태그 부팅 → 골든 20문항 ≥95%
- [ ] 키 로테이션 준비 (90일 주기)
- [ ] 골든셋 교체 (2주마다 20%)

