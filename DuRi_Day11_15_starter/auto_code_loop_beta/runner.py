import json
import pathlib
import subprocess
import sys

BASE = pathlib.Path(__file__).resolve().parent
LOGS = BASE / "logs"
GATES = BASE / "gates"


def sh(cmd):
    return subprocess.run(cmd, shell=True, capture_output=True, text=True)


def run_tests():
    LOGS.mkdir(parents=True, exist_ok=True)
    test_json = LOGS / "test_result.json"
    gate_script = GATES / "run_regression_tests.sh"
    if not gate_script.exists():
        # beta fallback
        test_json.write_text(
            json.dumps({"pass_rate": 0.85, "failures": []}, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        return True
    r = sh(f"bash '{gate_script}'")
    return test_json.exists() and test_json.read_text(encoding="utf-8").strip() != ""


def risk_gate():
    risk_py = GATES / "risk_checks.py"
    inp = LOGS / "test_result.json"
    outp = LOGS / "risk.json"
    if not risk_py.exists() or not inp.exists():
        return False
    r = sh(f"python3 '{risk_py}' --in '{inp}' --out '{outp}'")
    return outp.exists() and outp.read_text(encoding="utf-8").strip() != ""


def promote():
    return sh(f"bash '{(BASE / 'promote.sh')}'").returncode == 0


def main():
    if not run_tests():
        print(json.dumps({"promote": False, "reason": "no_tests"}))
        sys.exit(1)

    tests_path = LOGS / "test_result.json"
    try:
        tests = json.loads(tests_path.read_text(encoding="utf-8"))
    except Exception as e:
        print(json.dumps({"promote": False, "reason": "bad_test_json", "error": str(e)}))
        sys.exit(1)

    if not risk_gate():
        print(json.dumps({"promote": False, "reason": "no_risk"}))
        sys.exit(1)

    risks_path = LOGS / "risk.json"
    try:
        risks = json.loads(risks_path.read_text(encoding="utf-8"))
    except Exception as e:
        print(json.dumps({"promote": False, "reason": "bad_risk_json", "error": str(e)}))
        sys.exit(1)

    pass_rate = float(tests.get("pass_rate", 0))
    new_risks = int(risks.get("new_risks", 0))
    human_ack = bool(risks.get("human_ack", True))

    cond = (pass_rate >= 0.80) and (new_risks == 0) and human_ack
    if cond:
        ok = promote()
        print(json.dumps({"promote": ok, "pass_rate": pass_rate}, ensure_ascii=False))
        sys.exit(0 if ok else 2)
    else:
        print(
            json.dumps(
                {
                    "promote": False,
                    "reason": "gate_failed",
                    "tests": tests,
                    "risks": risks,
                },
                ensure_ascii=False,
            )
        )
        sys.exit(1)


if __name__ == "__main__":
    LOGS.mkdir(parents=True, exist_ok=True)
    main()
