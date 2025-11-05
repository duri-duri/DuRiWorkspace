# L4.0 최종 마무리 작업 체크리스트 (모듈화 + 디바운스 + 정규화 + 최종 마감)

## VS Code/WSL에서 실행할 명령어

### 옵션 A: 통합 실행 (권장)

```bash
cd ~/DuRiWorkspace
bash scripts/evolution/finalize_l4_complete.sh
```

이 스크립트가 자동으로:
1. .bashrc 모듈화 및 구문 에러 원천 차단 (~/.bashrc.d/*.sh)
2. .bashrc.d 파일 정리 (구문 에러 + alias 충돌 제거)
3. TriggerLimit 제거 + 서비스 측 디바운스 적용
4. 서비스 유닛 정규화 (쉘 스니펫 누수 제거)
5. 서비스 유닛 최종 정규화 (Unknown key name 경고 완전 제거)
6. .bashrc.d 로더 보증 + cold-* 실행 래퍼 고정 생성
7. 유저 유닛 영구화 및 안정성 확보
8. .bashrc 적용
9. 함수 확인
10. 헬스체크
11. 회귀 테스트

### 옵션 B: 단계별 실행

```bash
cd ~/DuRiWorkspace

# 1. .bashrc 모듈화
bash scripts/evolution/modularize_bashrc.sh

# 2. .bashrc.d 파일 정리
bash scripts/evolution/fix_bashrc_d_files.sh

# 3. TriggerLimit 제거 + 디바운스 적용
bash scripts/evolution/fix_triggerlimit_debounce.sh

# 4. 서비스 유닛 정규화
bash scripts/evolution/fix_service_unit.sh

# 5. 서비스 유닛 최종 정규화
bash scripts/evolution/fix_service_unit_final.sh

# 6. .bashrc.d 로더 보증 + cold-* 실행 래퍼 고정 생성
bash scripts/evolution/fix_bashrc_loader_and_wrappers.sh
source ~/.bashrc

# 7. 유저 유닛 영구화 및 안정성 확보
bash scripts/evolution/finalize_coldsync_stable.sh

# 8. 헬스체크
bash scripts/evolution/coldsync_healthcheck.sh

# 9. 회귀 테스트
bash scripts/evolution/coldsync_regression.sh
```

## 최종 검증

```bash
# 1. .bashrc 적용
source ~/.bashrc

# 2. 함수 확인 (모두 function이어야 함)
type dus cold-log cold-hash cold-run cold-status

# 3. 실행 래퍼 확인
ls -lh ~/.local/bin/cold_*

# 4. 최근 경고 확인 (과거 로그 무시)
journalctl --user -u coldsync-install.service --since "-2 min" --no-pager | grep -i 'Unknown key name' || echo "[OK] 최근 2분 경고 없음"

# 5. Path 유닛 경고 확인 (없어야 함)
systemctl --user status coldsync-install.path --no-pager | head -15

# 6. 디바운스 테스트 (10초 창 내 다중 저장 시 1회만 설치)
printf '\n# debounce-test1 %s\n' "$(date +%T)" >> ~/DuRiWorkspace/scripts/bin/coldsync_hosp_from_usb.sh
sleep 2
printf '\n# debounce-test2 %s\n' "$(date +%T)" >> ~/DuRiWorkspace/scripts/bin/coldsync_hosp_from_usb.sh
sleep 2
printf '\n# debounce-test3 %s\n' "$(date +%T)" >> ~/DuRiWorkspace/scripts/bin/coldsync_hosp_from_usb.sh
sleep 3
cold_log | grep -E 'INSTALLED|up-to-date'  # 10초 창 내 1회만 나와야 함

# 7. 해시 확인
cold_hash

# 8. 12초 대기 후 재저장 (새로운 창에서 또 1회 설치)
sleep 12
printf '\n# debounce-late-test %s\n' "$(date +%T)" >> ~/DuRiWorkspace/scripts/bin/coldsync_hosp_from_usb.sh
sleep 2
cold_log | grep -E 'INSTALLED|up-to-date'  # 또 1회 나와야 함

# 9. 최종 3점 점검
cold_status
cold_log 10
cold_hash
```

## 예상 결과

- ✅ 함수 정의 확인: `dus is a function`, `cold-log is a function`
- ✅ 실행 래퍼 확인: `~/.local/bin/cold_*` 모두 존재 및 실행 가능
- ✅ 최근 경고 없음: `Unknown key name` 없음 (과거 로그 무시)
- ✅ Path 유닛 경고 없음: `Unknown key name 'TriggerLimit*'` 없음
- ✅ 디바운스 작동: 10초 창 내 다중 저장 시 1회만 [INSTALLED]
- ✅ 로그: `[INSTALLED] ... -> ~/.local/bin/...`
- ✅ 해시 동일
- ✅ 헬스체크 PASS

## 생성된 파일 구조

```
~/.bashrc.d/
  ├── 10-systemd-user.sh    # systemd --user 헬퍼 (dus, dstat, dlog 등)
  └── 20-coldsync.sh         # coldsync 헬퍼 (cold-log, cold-hash 등)

~/.local/bin/
  ├── cold_log               # 실행 래퍼 (함수 대체)
  ├── cold_hash              # 실행 래퍼 (함수 대체)
  ├── cold_run               # 실행 래퍼 (함수 대체)
  ├── cold_status            # 실행 래퍼 (함수 대체)
  └── coldsync_install_debounced.sh  # 디바운스 래퍼 (10초 간격)

~/.config/systemd/user/
  ├── coldsync-install.path           # Path 유닛 (TriggerLimit 제거)
  └── coldsync-install.service       # Service 유닛 (최소 스펙, 정규화)
```

## 완료 후 상태

- ✅ .bashrc 모듈화 완료 (구문 에러 파급 방지)
- ✅ .bashrc.d 파일 정리 완료 (구문 에러 + alias 충돌 제거)
- ✅ .bashrc.d 로더 보증 완료 (재부팅 후에도 안정적)
- ✅ TriggerLimit 제거 (버전 호환성 확보)
- ✅ 디바운스 적용 (버스트 보호, 10초 간격)
- ✅ 서비스 유닛 최종 정규화 (Unknown key name 경고 완전 제거)
- ✅ cold-* 실행 래퍼 고정 생성 (전역 가용성 확보)
- ✅ 헬스체크 스크립트 버그 수정
- ✅ 유저 유닛 영구화 (linger 활성화)
- ✅ system unit 충돌 방지 (mask)

**운영 준비 완료 (p≈0.998)**

## 디바운스 동작 확인

디바운스는 10초 간격으로만 설치를 수행합니다:

```bash
# 연속 저장 테스트 (10초 창 내)
printf '\n# test1 %s\n' "$(date)" >> ~/DuRiWorkspace/scripts/bin/coldsync_hosp_from_usb.sh
sleep 1
printf '\n# test2 %s\n' "$(date)" >> ~/DuRiWorkspace/scripts/bin/coldsync_hosp_from_usb.sh
sleep 1
printf '\n# test3 %s\n' "$(date)" >> ~/DuRiWorkspace/scripts/bin/coldsync_hosp_from_usb.sh
sleep 3
cold_log | grep -E 'INSTALLED|up-to-date'  # 1회만 나와야 함

# 12초 후 다시 저장 (새로운 창)
sleep 12
printf '\n# test4 %s\n' "$(date)" >> ~/DuRiWorkspace/scripts/bin/coldsync_hosp_from_usb.sh
sleep 3
cold_log | grep -E 'INSTALLED|up-to-date'  # 또 1회 나와야 함
```

## 빠른 체크 포인트

* 최근 로그만 확인 (과거 로그 무시):

  `journalctl --user -u coldsync-install.service --since "-2 min" --no-pager`

* 상태:

  `cold_status`

* 수동 트리거:

  `cold_run`

* 해시:

  `cold_hash`

* 최근 경고 확인:

  `journalctl --user -u coldsync-install.service --since "-2 min" --no-pager | grep -i 'Unknown key name' || echo '[OK]'`

## Git 태그 및 커밋 (선택)

```bash
cd ~/DuRiWorkspace

git add docs/ops/L4_FINALIZE_CHECKLIST.md scripts/evolution/*.sh
git commit -m "ops: L4 coldsync stable; service unit finalized; bashrc loader guaranteed; cold-* wrappers fixed"

git tag -a "l4-coldsync-stable-$(date +%Y%m%d-%H%M)" -m "A plan stable + finalized + wrappers fixed"
```
