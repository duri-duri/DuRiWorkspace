from pathlib import Path
import runpy

def test_phase11_smoke():
    # orchestrator 실행이 예외 없이 끝나는지만 확인
    runpy.run_path(str(Path("scripts/core/phase11/orchestrator.py")))
