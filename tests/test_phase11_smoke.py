import subprocess as sp
import sys
from pathlib import Path


def test_phase11_smoke():
    """기존 contracts/test_ops_health_grep.py 패턴 활용"""
    # subprocess로 실행하여 출력 캡처 (기존 패턴)
    result = sp.run(
        [sys.executable, str(Path("scripts/core/phase11/orchestrator.py"))],
        capture_output=True,
        text=True,
        cwd=Path.cwd(),
    )

    # 실행 성공 확인
    assert result.returncode == 0, f"오케스트레이터 실행 실패: {result.stderr}"

    # 출력 검증 (기존 test_pipeline.py 패턴 활용)
    output = result.stdout
    assert "[core]" in output, "assistant 응답에 [core] 태그가 있어야 합니다"
    assert "(성찰)" in output, "내부 사고 결과에 (성찰) 태그가 있어야 합니다"
    assert "[phase11::telemetry]" in output, "텔레메트리 로그가 출력되어야 합니다"
