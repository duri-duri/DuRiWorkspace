import subprocess as sp, re

def test_ops_logs_have_no_errors():
    cmd = r"tail -n 200 var/reports/final_verify_*/run.log 2>/dev/null | grep -Ei 'error|fail' || true"
    r = sp.run(cmd, shell=True, capture_output=True, text=True)
    # 에러 아니면서 빈 출력이면 건강
    assert r.returncode == 0
    assert not r.stdout.strip(), f"logs show errors:\n{r.stdout}"
