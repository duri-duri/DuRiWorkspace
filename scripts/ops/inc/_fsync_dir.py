#!/usr/bin/env python3
# L4 Directory fsync
# Purpose: 디렉터리 fsync로 rename 내구성 보장
# Usage: python3 scripts/ops/inc/_fsync_dir.py <directory>

import os
import sys

if len(sys.argv) < 2:
    sys.exit(1)

d = sys.argv[1]

try:
    fd = os.open(d, os.O_DIRECTORY)
    try:
        os.fsync(fd)
    finally:
        os.close(fd)
except Exception as e:
    sys.stderr.write(f"fsync_dir failed: {e}\n")
    sys.exit(1)

