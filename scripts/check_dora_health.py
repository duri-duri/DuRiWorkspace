#!/usr/bin/env python3
"""
Dora Exporter 헬스체크 스크립트 (jq 대신 Python 사용)
"""
import urllib.request
import json
import sys

def check_health():
    try:
        with urllib.request.urlopen('http://localhost:8000/health') as response:
            data = json.loads(response.read().decode())
            print(json.dumps(data, indent=2))
            return data.get('status') == 'healthy'
    except Exception as e:
        print(f'Error: {e}', file=sys.stderr)
        return False

if __name__ == '__main__':
    success = check_health()
    sys.exit(0 if success else 1)
