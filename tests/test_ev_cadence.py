#!/usr/bin/env python3
"""EV 생성 속도 테스트: 최소 cadence 확인"""
import subprocess
import pathlib

def test_ev_velocity_minimum():
    """EV 생성 속도가 최소 임계값 이상인지 확인"""
    script = pathlib.Path("scripts/ev_velocity.sh")
    assert script.exists(), f"ev_velocity.sh not found: {script}"
    
    try:
        out = subprocess.check_output(
            ["bash", str(script)],
            cwd=script.parent.parent,
            stderr=subprocess.DEVNULL,
            timeout=10
        ).decode().strip()
        
        # 출력 형식: "duri_ev_velocity 1.042"
        parts = out.split()
        assert len(parts) >= 2, f"Unexpected output format: {out}"
        evh = float(parts[-1])
        
        assert evh >= 2.5, f"EV/h too low: {evh} < 2.5 (warning threshold)"
        
        # 목표값 체크 (선택적)
        if evh < 4.0:
            print(f"[WARN] EV/h below target: {evh} < 4.0 (pass threshold)")
        else:
            print(f"[OK] EV/h meets target: {evh} ≥ 4.0")
        
        return evh
    except subprocess.TimeoutExpired:
        raise AssertionError("ev_velocity.sh timed out")
    except subprocess.CalledProcessError as e:
        raise AssertionError(f"ev_velocity.sh failed: {e}")
    except (ValueError, IndexError) as e:
        raise AssertionError(f"Failed to parse ev_velocity.sh output: {out if 'out' in locals() else 'N/A'}, error: {e}")

if __name__ == "__main__":
    evh = test_ev_velocity_minimum()
    print(f"✅ EV cadence test passed: {evh} EV/h")

