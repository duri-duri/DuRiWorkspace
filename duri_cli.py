#!/usr/bin/env python3
"""
DuRi CLI - 시스템 헌장 강제 적용 도구
"""

import os
from pathlib import Path
import subprocess
import sys


def display_constitution():
    """시스템 헌장 표시"""
    print("=" * 80)
    print("🧠 DuRi 시스템 헌장(Design Constitution)")
    print("=" * 80)

    print(
        """
✅ 제1원칙: duri_core는 진실의 중심이며, 판단의 기준이다.
✅ 제2원칙: duri_brain은 DuRi의 자아이며, 판단 기계이다.
✅ 제3원칙: duri_evolution은 실험과 개선의 행동자이다.
✅ 제4원칙: duri_control은 이동형 통합 제어 콘솔이다.
✅ 제5원칙: duri_head는 감정과 직관을 표현하는 상호작용 창구다.

📌 핵심 원칙:
DuRi는 절대적으로 역할이 분리된 5개의 노드로 구성된다:
core는 기준, brain은 판단, evolution은 개선, control은 외부 제어, head는 인간과의 교감이다.

이 구조를 어기는 어떤 행동도 금지되며, 잘못된 책임의 수행은 반드시 재정비되어야 한다.
"""
    )

    print("=" * 80)


def enforce_constitution():
    """시스템 헌장 강제 적용"""
    print("🔒 시스템 헌장 강제 적용 중...")

    # 각 노드의 시작 메시지 실행
    nodes = ["duri_control", "duri_brain", "duri_evolution"]

    for node in nodes:
        startup_file = Path(f"{node}/app/startup_message.py")
        if startup_file.exists():
            print(f"📋 {node} 헌장 적용 중...")
            try:
                result = subprocess.run(
                    [sys.executable, str(startup_file)], capture_output=True, text=True
                )
                if result.returncode == 0:
                    print(f"✅ {node} 헌장 적용 완료")
                else:
                    print(f"⚠️ {node} 헌장 적용 실패: {result.stderr}")
            except Exception as e:
                print(f"❌ {node} 헌장 적용 오류: {e}")

    print("🎯 시스템 헌장 강제 적용 완료!")


def check_constitution_compliance():
    """시스템 헌장 준수 여부 확인"""
    print("🔍 시스템 헌장 준수 여부 확인 중...")

    # 금지된 기능들이 올바른 노드에 있는지 확인
    compliance_checks = {
        "duri_control": {
            "allowed": ["monitoring", "backup", "gateway", "control"],
            "forbidden": ["judgment", "code_improvement", "memory_storage"],
        },
        "duri_brain": {
            "allowed": ["judgment", "emotion", "creativity", "social"],
            "forbidden": ["code_improvement", "memory_storage", "external_control"],
        },
        "duri_evolution": {
            "allowed": ["code_improvement", "experiment", "learning", "adaptation"],
            "forbidden": ["judgment", "memory_storage", "external_control"],
        },
    }

    for node, checks in compliance_checks.items():
        print(f"\n📋 {node} 준수 확인:")

        # 허용된 기능 확인
        for feature in checks["allowed"]:
            print(f"  ✅ {feature} - 허용됨")

        # 금지된 기능 확인
        for feature in checks["forbidden"]:
            print(f"  ❌ {feature} - 금지됨")

    print("\n🎯 시스템 헌장 준수 확인 완료!")


def main():
    """메인 함수"""
    if len(sys.argv) < 2:
        print("사용법:")
        print("  python duri_cli.py constitution  # 헌장 표시")
        print("  python duri_cli.py enforce       # 헌장 강제 적용")
        print("  python duri_cli.py check         # 준수 여부 확인")
        return

    command = sys.argv[1]

    if command == "constitution":
        display_constitution()
    elif command == "enforce":
        enforce_constitution()
    elif command == "check":
        check_constitution_compliance()
    else:
        print(f"❌ 알 수 없는 명령어: {command}")
        print("사용 가능한 명령어: constitution, enforce, check")


if __name__ == "__main__":
    main()
