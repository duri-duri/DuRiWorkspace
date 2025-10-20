from __future__ import annotations
from typing import Any, Dict, Tuple
from pathlib import Path
import json
import time

# 통합 시스템 모듈을 불러와 실제로 바인딩된 최종 클래스 객체를 가져옵니다.
import integrated_evolution_system as ies

C = ies.DuRiIntegratedEvolutionSystem
logger = getattr(ies, "logger", None)

# ---- JSON 직렬화 보조 (안전 직렬화) ----
def _json_default(o):
    try:
        import dataclasses, enum, datetime
        if dataclasses.is_dataclass(o):
            return dataclasses.asdict(o)
        if isinstance(o, enum.Enum):
            return o.value
        if isinstance(o, (set, frozenset)):
            return list(o)
        if isinstance(o, (datetime.datetime, datetime.date, datetime.time)):
            return o.isoformat()
        return str(o)
    except Exception:
        return str(o)

# ---- _save_evolution_log 없거나 기본형이면 안전 버전으로 대체 ----
async def _save_evolution_log(self, summary: Dict[str, Any]) -> None:
    try:
        artifacts = Path(ies.__file__).parent / "artifacts"
        artifacts.mkdir(parents=True, exist_ok=True)
        log_path = artifacts / "evolution_log.json"
        with log_path.open("w", encoding="utf-8") as f:
            json.dump(summary, f, indent=2, ensure_ascii=False, default=_json_default)
        if logger: logger.info(f"📝 진화 로그 저장: {log_path}")
    except Exception as e:
        if logger: logger.warning(f"⚠️ 로그 저장 실패: {e}")

# ---- 컴포넌트 lazy init (존재 보장) ----
async def _ensure_components(self) -> None:
    try:
        if not hasattr(self, "self_rewriter") or self.self_rewriter is None:
            try:
                from self_rewriting_module import SelfRewritingModule
                self.self_rewriter = SelfRewritingModule()
            except Exception as e:
                if logger: logger.error(f"SelfRewritingModule 초기화 실패: {e}")
                self.self_rewriter = None
        if not hasattr(self, "genetic_engine") or self.genetic_engine is None:
            try:
                from genetic_evolution_engine import GeneticEvolutionEngine
                self.genetic_engine = GeneticEvolutionEngine()
            except Exception as e:
                if logger: logger.error(f"GeneticEvolutionEngine 초기화 실패: {e}")
                self.genetic_engine = None
        if not hasattr(self, "meta_coder") or self.meta_coder is None:
            try:
                from meta_coder import MetaCoder
                self.meta_coder = MetaCoder()
            except Exception as e:
                if logger: logger.error(f"MetaCoder 초기화 실패: {e}")
                self.meta_coder = None
    except Exception as e:
        if logger: logger.error(f"컴포넌트 lazy init 실패: {e}")

# ---- 호출부 호환 _get_optimal_node ----
async def _get_optimal_node(self, *args, node: str | None = None, **kwargs) -> str:
    try:
        import socket
        return node or socket.gethostname()
    except Exception:
        return node or "local"

# ---- 공개 API run_once ----
async def run_once(self, tracks: Tuple[str, ...] = ("self_rewrite","genetic","meta")) -> Dict[str, Any]:
    results: Dict[str, Any] = {}
    try:
        if logger: logger.info(f"🚀 통합 진화 시스템 실행 시작: tracks={tracks}")
        # 보조 메서드 보장
        if not hasattr(self, "_ensure_components"):
            setattr(C, "_ensure_components", _ensure_components)
        if not hasattr(self, "_save_evolution_log"):
            setattr(C, "_save_evolution_log", _save_evolution_log)

        await self._ensure_components()

        # 세션 생성 (현행 EvolutionSession 시그니처 가정)
        session = ies.EvolutionSession(
            session_id=f"evo_{int(time.time())}",
            stimulus_event="manual_run_once",
            start_time=time.time(),
        )

        for track in tracks:
            if track == "self_rewrite":
                if getattr(self, "self_rewriter", None) is None:
                    if logger: logger.error("Self-Rewriting 컴포넌트 없음: 스킵")
                    results["self_rewrite"] = {"skipped": True, "reason": "self_rewriter_missing"}
                else:
                    results["self_rewrite"] = await self._execute_self_rewriting(session)
            elif track == "genetic":
                if getattr(self, "genetic_engine", None) is None:
                    if logger: logger.error("Genetic Engine 없음: 스킵")
                    results["genetic"] = {"skipped": True, "reason": "genetic_engine_missing"}
                else:
                    results["genetic"] = await self._execute_genetic_evolution(session)
            elif track == "meta":
                if getattr(self, "meta_coder", None) is None:
                    if logger: logger.error("Meta Coder 없음: 스킵")
                    results["meta"] = {"skipped": True, "reason": "meta_coder_missing"}
                else:
                    results["meta"] = await self._execute_meta_coding(session)

        summary = {
            "success": True,
            "session_id": session.session_id,
            "tracks_executed": tracks,
            "results": results,
            "runtime_ms": (time.time() - session.start_time) * 1000 if hasattr(session, "start_time") else None,
            "timestamp": time.time(),
        }
        await self._save_evolution_log(summary)
        if logger: logger.info(f"✅ 통합 진화 시스템 실행 완료: {summary.get('runtime_ms')}")
        return summary
    except Exception as e:
        if logger: logger.error(f"❌ 통합 진화 시스템 실행 실패: {e}")
        return {"success": False, "error": str(e)}

# ---- 실제 클래스에 메서드 장착 (멱등) ----
if not hasattr(C, "run_once"):
    setattr(C, "run_once", run_once)
if not hasattr(C, "_get_optimal_node"):
    setattr(C, "_get_optimal_node", _get_optimal_node)
# 보조들도 보장
if not hasattr(C, "_ensure_components"):
    setattr(C, "_ensure_components", _ensure_components)
if not hasattr(C, "_save_evolution_log"):
    setattr(C, "_save_evolution_log", _save_evolution_log)
