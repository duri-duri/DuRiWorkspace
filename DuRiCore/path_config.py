#!/usr/bin/env python3
"""
DuRi 경로 설정 파일
"""

import os
import sys

# DuRi 프로젝트 루트 경로
DURI_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 시스템 경로 추가
sys.path.insert(0, DURI_ROOT)
sys.path.insert(0, os.path.join(DURI_ROOT, 'DuRiCore'))
sys.path.insert(0, os.path.join(DURI_ROOT, 'duri_modules'))
sys.path.insert(0, os.path.join(DURI_ROOT, 'duri_brain'))

# 경로 설정 완료
print(f"DuRi 경로 설정 완료: {DURI_ROOT}")
