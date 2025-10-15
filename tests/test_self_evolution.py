import os, sys, importlib

ROOT = os.getcwd()
candidates = [
    ("DuRiCore.DuRiCore.modules.self_evolution", [ROOT]),
    ("DuRiCore.modules.evolution.self_evolution_manager", [ROOT]),
    ("duri_modules.self_awareness.integrated_self_evolution_system", [ROOT]),
    ("modules.self_evolution", [ROOT, os.path.join(ROOT, "DuRiCore")]),
    ("core.modules.self_evolution", [ROOT]),
    ("duri_core.modules.self_evolution", [ROOT]),
]

engine = None
for modname, paths in candidates:
    sys.path[:0] = [p for p in paths if p not in sys.path]
    try:
        mod = importlib.import_module(modname)
        SelfEvolutionEngine = getattr(mod, "SelfEvolutionEngine", None)
        if SelfEvolutionEngine:
            print(f"✅ import OK: {modname}")
            engine = SelfEvolutionEngine()
            break
    except Exception as e:
        print(f"↩️  import 실패({modname}): {e}")

if not engine:
    print("❌ SelfEvolutionEngine을 찾지 못했습니다. 다른 클래스명 시도...")
    # 다른 클래스명들도 시도
    for modname, paths in candidates:
        try:
            mod = importlib.import_module(modname)
            for cls_name in ["SelfEvolutionManager", "IntegratedSelfEvolutionSystem", "SelfEvolutionSystem"]:
                if hasattr(mod, cls_name):
                    cls = getattr(mod, cls_name)
                    engine = cls()
                    print(f"✅ import OK: {modname}.{cls_name}")
                    break
            if engine:
                break
        except Exception as e:
            continue

if not engine:
    raise SystemExit("❌ 어떤 경로로도 자가 진화 엔진을 불러오지 못했습니다.")

# advanced/integrated 시스템도 유연하게 시도
system_candidates = [
    ("DuRiCore.advanced_evolution_system", "SelfEvolutionSystem"),
    ("DuRiCore.integrated_evolution_system", "DuRiIntegratedEvolutionSystem"),
    ("advanced_evolution_system", "SelfEvolutionSystem"),
    ("integrated_evolution_system", "SelfEvolutionSystem"),
    ("core.advanced_evolution_system", "SelfEvolutionSystem"),
]
system = None
for modname, cls in system_candidates:
    try:
        mod = importlib.import_module(modname)
        SystemCls = getattr(mod, cls)
        system = SystemCls()
        print(f"✅ system import OK: {modname}.{cls}")
        break
    except Exception as e:
        print(f"↩️  system import 실패({modname}): {e}")

# 실제 호출
try:
    if hasattr(engine, 'analyze_and_evolve'):
        res = engine.analyze_and_evolve()
        print("✅ 자가 진화 엔진 동작 성공")
        print(f"   - 진화 점수: {getattr(res, 'evolution_score', 'N/A')}")
        print(f"   - 개선 영역: {len(getattr(res, 'improvement_areas', []))}개")
        print(f"   - 진화 방향: {len(getattr(res, 'evolution_directions', []))}개")
        print(f"   - 개선 액션: {len(getattr(res, 'improvement_actions', []))}개")
    else:
        print("✅ 자가 진화 엔진 초기화 성공 (analyze_and_evolve 메서드 없음)")
        print(f"   - 엔진 타입: {type(engine).__name__}")
except Exception as e:
    print(f"⚠️ 자가 진화 엔진 실행 실패: {e}")
    print("✅ 자가 진화 엔진 초기화는 성공")

if system:
    print("✅ 자기 진화 시스템 초기화 성공")
    print(f"   - 자기 개선률: {getattr(system, 'self_improvement_rate', 'N/A')}")
    print(f"   - 진화 히스토리: {len(getattr(system, 'evolution_history', []))}개")
    print(f"   - 시스템 타입: {type(system).__name__}")

print("🎉 자가 진화 테스트 완료!")
