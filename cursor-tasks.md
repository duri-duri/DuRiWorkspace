# DuRi Cursor Tasks: 자동 제안 태스크 목록

## [Task] EV cadence < 2.5/h

**증상**: `scripts/doctor.sh`에서 `EV_velocity(h) < 2.5` 또는 `scripts/gate_check.sh`에서 `[FAIL] EV velocity`

**원인 추정**:
- 파일럿 주기 설정 오류 (MIN/MAX_GAP_SEC)
- Shadow 워커 비활성화
- Shadow epoch 병목 (p95 > 12min)

**수정 체크리스트**:
1. `scripts/pilot_24h.sh`에서 `MIN_GAP_SEC=480`, `MAX_GAP_SEC=720` 확인
2. `pgrep -fa "shadow_parallel_worker\|pilot_24h"`로 워커 프로세스 확인
3. `bash scripts/start_shadow_2worker.sh` 실행 (비활성화 시)
4. Shadow epoch duration 분석: `grep "SHADOW_EPOCH_DURATION" var/logs/shadow.log | tail -10`
5. systemd timer 설정 고려 (선택): `/etc/systemd/system/duri-pilot.timer`

**권장 커서 프롬프트**:
```
Inspect pilot_24h.sh cadence settings. Ensure start_shadow_2worker.sh is active. Check Shadow epoch p95 duration.
```

---

## [Task] AB p-value constant

**증상**: `scripts/doctor.sh`에서 `unique_vals ≤ 1` 또는 `test_ab_variance.py` 실패

**원인 추정**:
- EV별 입력 슬라이싱 실패
- RNG seed 고정 또는 누락
- 캐시된 ab_eval.prom 재사용

**수정 체크리스트**:
1. `scripts/evolution/evidence_bundle.sh`에서 `--input "$EV_JSONL"` 전달 확인
2. `scripts/evolution/make_ab_eval_prom_min.py`에서 `--seed` 인자 처리 확인
3. EV별 입력 파일 경로 확인: `ls -la var/evolution/EV-*/evolution.*.jsonl`
4. 캐시 파일 강제 제거: `find var/evolution -name "ab_eval.prom" -delete` (주의: 기존 EV 삭제)
5. RNG seed 로직 확인: `combined_seed = (ev_hash + seed_hash) % (2**32)`

**권장 커서 프롬프트**:
```
Verify EV-sliced JSONL input path in evidence_bundle.sh. Force RNG seed = stable_hash(ev_id) in make_ab_eval_prom_min.py. Remove cached ab_eval.* before recompute.
```

---

## [Task] Shadow epoch p95 > 12m

**증상**: `scripts/doctor.sh`에서 `p95 > 720s` 또는 `scripts/gate_check.sh`에서 `[WARN] Shadow epoch p95`

**원인 추정**:
- Shadow 단일 워커 실행 (병렬화 부재)
- Bundle 단계 동기 블로킹
- 타임아웃 미적용

**수정 체크리스트**:
1. Shadow 병렬화 확인: `pgrep -fa "shadow_parallel_worker" | wc -l` (예상: 2)
2. Bundle 비동기화 확인: `grep "BUNDLE_ASYNC" scripts/shadow_duri_integration_final.sh`
3. 타임아웃 적용 확인: `grep "BUNDLE_TIMEOUT" scripts/evolution/evidence_bundle.sh`
4. 병목 단계 분석: `grep "SHADOW_EPOCH_(START|END)" var/logs/shadow.log | tail -20`
5. 2-worker 강제 시작: `bash scripts/start_shadow_2worker.sh`

**권장 커서 프롬프트**:
```
Surface bottleneck phase from Shadow epoch logs. Propose parallel map (2-worker) or timeout enforcement in shadow_duri_integration_final.sh.
```

---

## [Task] DB consistency issue

**증상**: `scripts/doctor.sh`에서 `[WARN] DB 스키마/이름 정합성` 또는 `docker-compose.yml`과 실제 DB 불일치

**수정 체크리스트**:
1. `docker-compose.yml`에서 `POSTGRES_DB=duri_db` 확인
2. 모든 `DATABASE_URL`이 `duri_db`를 가리키는지 확인
3. `bash scripts/db_migrate_to_duri_db.sh` 실행 (마이그레이션 필요 시)
4. DB 존재 확인: `docker exec duri-postgres psql -U postgres -tc "SELECT datname FROM pg_database WHERE datistemplate=false;"`

---

## [Task] Metrics endpoint unavailable

**증상**: `scripts/doctor.sh`에서 `[WARN] metrics endpoint 확인 필요`

**수정 체크리스트**:
1. `shadow/metrics_exporter_enhanced.py` 프로세스 확인: `pgrep -fa "metrics_exporter"`
2. 포트 9109 리스닝 확인: `netstat -tlnp | grep 9109` 또는 `ss -tlnp | grep 9109`
3. systemd 서비스 확인: `systemctl --user status duri-shadow-exporter.service`
4. 재시작: `systemctl --user restart duri-shadow-exporter.service`

---

## [Task] Pilot process not running

**증상**: `scripts/doctor.sh`에서 `[WARN] 파일럿/워커 프로세스 없음`

**수정 체크리스트**:
1. `bash scripts/start_shadow_2worker.sh` 실행
2. systemd timer 설정 (선택): `/etc/systemd/system/duri-pilot.timer` 및 `.service` 파일 생성
3. 프로세스 확인: `pgrep -fa "pilot_24h\|shadow_parallel_worker"`

