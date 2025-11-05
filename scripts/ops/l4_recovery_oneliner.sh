#!/usr/bin/env bash
# L4 Recovery One-Liner - 재부팅 후 한 줄 복구 명령
# Purpose: 재부팅 후 최소한의 조치로 복구
# Usage: 복사해서 붙여넣기

# 사용자 권한으로 실행
bash /home/duri/DuRiWorkspace/scripts/ops/l4_recover_and_verify.sh

# 또는 root 권한으로 실행 (필요 시)
# systemctl start l4-ensure.service && su - duri -c 'bash /home/duri/DuRiWorkspace/scripts/ops/l4_recover_and_verify.sh'

