#!/usr/bin/env python3
"""
Shadow 리포트 큐 시스템
약점 리포트를 큐에 적재
"""

import hashlib
import pathlib
import sys
import time

q = pathlib.Path.home() / "DuRiWorkspace/var/queue"
q.mkdir(parents=True, exist_ok=True)
data = sys.stdin.read() if not sys.stdin.isatty() else (sys.argv[1] if len(sys.argv) > 1 else "{}")
h = hashlib.sha1((data + str(time.time())).encode()).hexdigest()[:12]
p = q / f"shadow_report_{h}.json"
with open(p, "w") as f:
    f.write(data)
print(p)
