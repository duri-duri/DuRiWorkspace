# Phase-2 Test Suite — Quick Guide

## Quick start
```bash
make help
make smoke
P2_RACE_MB=2 P2_CRASH_MB=2 P2_TIMEOUT=2s make test-all-ci
```

## Tunables

* `P2_RACE_MB`  : race 파일 크기(MB, 기본 1)
* `P2_CRASH_MB` : crash 파일 크기(MB, 기본 1)
* `P2_TIMEOUT`  : Phase-2 타임아웃 (`500ms`, `2s`, 기본 20s)
* `ENOSPC_SIZE` : ENOSPC용 tmpfs 크기 (예: `8m`)
* `FILL_MB`     : tmpfs 사전 채우기 MB (기본 7)

## RO / ENOSPC

```bash
sudo true
make test-ro-hdd
ENOSPC_SIZE=8m FILL_MB=7 make test-enospc
```

## Troubleshooting

* **JSON-start fail**:
  ```bash
  tac .test-artifacts/*.raw.txt | sed -n '1,5p'
  tac .test-artifacts/*.err.txt | sed -n '1,5p'
  ```
* **ENOSPC/RO 판정 수식**:
  ```bash
  jq -e '(.rc != 0) or ((.full_ok? // 0 | tonumber)==0) or ((.full_bad? // 0 | tonumber)>0)' .test-artifacts/*.json
  ```
* **강한 부하 예시**:
  ```bash
  P2_RACE_MB=8 P2_CRASH_MB=16 P2_TIMEOUT=2s make test-extra
  ```

## CI Badge

아래 배지를 README.md 상단에 추가하면 상태를 한눈에 볼 수 있습니다.

```md
[![Phase-2 CI](https://github.com/duri-duri/DuRiWorkspace/actions/workflows/ci-phase2.yml/badge.svg?branch=main)](https://github.com/duri-duri/DuRiWorkspace/actions/workflows/ci-phase2.yml)
```
