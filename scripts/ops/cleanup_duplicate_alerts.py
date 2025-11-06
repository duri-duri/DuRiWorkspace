#!/usr/bin/env python3
# 정리 스크립트: 중복 L4WeeklyDecisionStale 제거
import re

with open('prometheus/rules/l4_alerts.yml', 'r') as f:
    lines = f.readlines()

output = []
i = 0
last_stale_start = -1
last_stale_end = -1

while i < len(lines):
    if 'L4WeeklyDecisionStale' in lines[i] and 'alert:' in lines[i]:
        # 이 alert 블록의 시작과 끝 찾기
        start = i
        i += 1
        while i < len(lines) and (lines[i].strip().startswith('-') or lines[i].strip().startswith('#') or lines[i].strip() == '' or not lines[i].strip().startswith('      - alert:')):
            if lines[i].strip().startswith('          summary:') and 'weekly_decision stale' in lines[i]:
                # 마지막 완전한 블록 찾음
                while i < len(lines) and (lines[i].strip().startswith('          ') or lines[i].strip().startswith('      - alert:')):
                    if lines[i].strip().startswith('      - alert:'):
                        break
                    i += 1
                last_stale_end = i
                break
            i += 1
        if last_stale_end > 0:
            last_stale_start = start
    else:
        i += 1

# 마지막 것만 남기고 나머지 제거
if last_stale_start > 0 and last_stale_end > 0:
    # 첫 번째부터 마지막 전까지 제거
    new_lines = []
    i = 0
    in_stale_block = False
    skip_until = -1
    
    while i < len(lines):
        if 'L4WeeklyDecisionStale' in lines[i] and 'alert:' in lines[i]:
            if i < last_stale_start or i >= last_stale_end:
                # 이전 중복 블록 건너뛰기
                while i < len(lines) and not (lines[i].strip().startswith('      - alert:') and i < last_stale_end):
                    i += 1
                continue
            else:
                # 마지막 블록은 유지
                new_lines.append(lines[i])
                i += 1
        else:
            new_lines.append(lines[i])
            i += 1
    
    with open('prometheus/rules/l4_alerts.yml', 'w') as f:
        f.writelines(new_lines)
    print("✅ 중복 제거 완료")
else:
    print("⚠️ 중복 패턴을 찾지 못함")

