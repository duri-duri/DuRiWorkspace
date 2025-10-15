import json, os, glob, time, psutil

report = {"checks":[]}

def add(name, ok, detail): 
    report["checks"].append({"name":name,"ok":bool(ok),"detail":detail})

# 1) Risk variability
try:
    from DuRiCore.risk_management.intelligent_risk_analyzer import IntelligentRiskAnalyzer
    ia = IntelligentRiskAnalyzer()
    outs = [ia.analyze_risk(c) for c in ({"cpu_usage":10,"memory_usage":20},
                                         {"cpu_usage":50,"memory_usage":60},
                                         {"cpu_usage":90,"memory_usage":95})]
    var = len(set(map(str, outs))) > 1
    add("risk_variability", var, {"outputs":outs})
except Exception as e:
    add("risk_variability", False, {"error":str(e)})

# 2) Deploy artifact
try:
    from DuRiCore.deployment_system import DeploymentSystem
    ds = DeploymentSystem(); ds.activate()
    res = ds.deploy({"environment":"production"})
    # 탐색
    paths = []
    for d in (".","/home/duri/DuRiWorkspace","./artifacts","./logs"):
        paths += glob.glob(os.path.join(d,"**","*DEPLOY*"), recursive=True)
        paths += glob.glob(os.path.join(d,"**","*deploy*"), recursive=True)
    has_artifact = bool(paths) or any(k in res.get("deployment",{}) for k in ("artifact_path","log_path","image_tag"))
    add("deploy_artifact", has_artifact, {"deploy_result":res, "found_paths":paths[:5]})
except Exception as e:
    add("deploy_artifact", False, {"error":str(e)})

# 3) State persistence
try:
    from duri_modules.autonomous.duri_autonomous_core import DuRiAutonomousCore
    core = DuRiAutonomousCore(); core.activate()
    r1 = core.run_learning_cycle(); r2 = core.run_learning_cycle()
    paths = []
    for d in (".","/home/duri/DuRiWorkspace","/tmp"):
        paths += glob.glob(os.path.join(d,"**","*CYCLE*"), recursive=True)
    ok = r1!=r2 and len(paths)>0
    add("state_persistence", ok, {"r1":r1,"r2":r2,"state_files":paths[:5]})
except Exception as e:
    add("state_persistence", False, {"error":str(e)})

# 4) psutil sensitivity
try:
    cpu1 = psutil.cpu_percent(interval=1)
    t = time.time()+2
    x=0
    while time.time()<t:
        x+=1
    cpu2 = psutil.cpu_percent(interval=1)
    add("psutil_sensitivity", cpu2>cpu1+10, {"idle":cpu1,"under_load":cpu2})
except Exception as e:
    add("psutil_sensitivity", False, {"error":str(e)})

# 5) API visibility
try:
    import requests
    response = requests.get("http://localhost:8080/health", timeout=5)
    api_ok = response.status_code == 200
    add("api_visibility", api_ok, {"status_code":response.status_code, "response":response.json()})
except Exception as e:
    add("api_visibility", False, {"error":str(e)})

# Score & verdict
score = sum(1 for c in report["checks"] if c["ok"])
report["score"]=score
report["verdict"] = ("REAL" if score>=2 else "POC" if score==1 else "STRINGY")
print(json.dumps(report, ensure_ascii=False, indent=2))
