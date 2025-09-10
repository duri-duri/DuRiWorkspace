import json, os, subprocess, pathlib, sys, time

BUDGET = 0.005  # 0.5%

def atomic_write(path: pathlib.Path, text: str):
    """원자적 쓰기 유틸리티"""
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(text, encoding="utf-8")
    tmp.replace(path)

def toast(msg):
    try:
        ps = ('[Windows.UI.Notifications.ToastNotificationManager, Windows.UI.Notifications, ContentType = WindowsRuntime] > $null;'
              '$t=New-Object Windows.Data.Xml.Dom.XmlDocument;'
              '$t.LoadXml("<toast><visual><binding template=\\"ToastGeneric\\\"><text>'+msg+'</text></binding></visual></toast>");'
              '[Windows.UI.Notifications.ToastNotificationManager]::CreateToastNotifier("DuRi").Show([Windows.UI.Notifications.ToastNotification]::new($t));')
        subprocess.run(["powershell","-Command", ps], check=False)
    except Exception as e:
        print("[toast-failed]", e)

def main():
    # 경로 안정화: __file__ 기준 절대경로 사용
    BASE = pathlib.Path(__file__).resolve().parent
    ROOT = BASE
    flag = ROOT / "FREEZE.FLAG"
    legacy = ROOT / "scripts" / "legacy_freeze_executor.sh"
    rollback = ROOT / "rollback.sh"
    
    with open("slo_sla_dashboard_v1/metrics.json","r",encoding="utf-8") as f:
        m = json.load(f)
    rate = m.get("failures",0)/max(1,m.get("requests",1))
    
    if rate > BUDGET:
        msg = f"[ALERT] Failure budget exceeded: {rate:.3%} > {BUDGET:.2%}. Freeze & rollback."
        
        # idempotent 보장: FREEZE.FLAG 있을 때 중복 실행 회피
        if flag.exists():
            print("[INFO] Freeze already active; skipping legacy execution.")
            return
            
        # 원자적 쓰기로 FREEZE.FLAG 생성
        atomic_write(flag, msg)
        
        # 레거시 프리저 연동 (에러 처리 강화)
        if legacy.exists() and legacy.is_file():
            try:
                result = subprocess.run(["bash", str(legacy)], 
                                      capture_output=True, text=True, timeout=300)
                if result.returncode != 0:
                    print(f"[WARN] Legacy freeze failed: {result.stderr}", file=sys.stderr)
                    # 롤백 훅: 레거시 스크립트 실패 시 기본 롤백 스크립트로 폴백
                    if rollback.exists():
                        try:
                            subprocess.run(["bash", str(rollback), "--safe"], 
                                         capture_output=True, text=True, timeout=300)
                            print("[INFO] Rollback script executed")
                        except Exception as rollback_e:
                            print(f"[WARN] Rollback failed: {rollback_e}", file=sys.stderr)
            except subprocess.TimeoutExpired:
                print("[WARN] Legacy freeze timeout", file=sys.stderr)
            except Exception as e:
                print(f"[WARN] Legacy freeze error: {e}", file=sys.stderr)
        else:
            print("[INFO] Legacy freeze script not found, skipping")
            
        toast(msg)
        print(msg)
    else:
        print(f"[OK] Failure rate {rate:.3%} within budget {BUDGET:.2%}.")

if __name__ == "__main__":
    main()
