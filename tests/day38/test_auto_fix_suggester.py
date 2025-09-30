import json, subprocess, textwrap, os

def run(log):
    p = subprocess.run(
        ["python3", "tools/auto_fix_suggester.py"],
        input=log.encode(),
        stdout=subprocess.PIPE,
        check=True,
    )
    return json.loads(p.stdout.decode())

def test_import_missing_rule_triggers():
    out = run("E   ModuleNotFoundError: No module named 'foo_bar'")
    assert "import-missing" in out["matched_rules"]

def test_timeout_rule_triggers():
    out = run("E   TimeoutError: operation timed out")
    assert "flaky-timeout" in out["matched_rules"]
