import shutil, pytest, os, stat, subprocess as sp

SCRIPTS = [
    "scripts/rollout_ops.sh",
    "scripts/generate_rollout_summary.sh",
    "scripts/watch_rollout_health.sh",
]

@pytest.mark.parametrize("p", SCRIPTS)
def test_scripts_are_executable(p):
    assert os.path.exists(p), f"missing: {p}"
    st = os.stat(p).st_mode
    assert st & stat.S_IXUSR, f"not executable: {p}"

@pytest.mark.timeout(20)
def test_rollout_status_runs():
    r = sp.run(["bash","-lc","scripts/rollout_ops.sh status"], capture_output=True, text=True)
    assert r.returncode == 0, r.stdout + r.stderr
    assert "ROLLOUT:" in r.stdout
