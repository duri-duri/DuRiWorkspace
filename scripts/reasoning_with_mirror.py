import json
import sys

from DuRiCore.unified.reasoning.mirror import handle

payload = json.loads(sys.stdin.read() or "{}")
print(json.dumps(handle(payload), ensure_ascii=False))
