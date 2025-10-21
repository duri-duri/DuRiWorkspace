from __future__ import annotations

import asyncio
import json
import time
from pathlib import Path
from typing import Any, Dict, Tuple

import integrated_evolution_system as ies  # 반드시 정상 import

C = ies.DuRiIntegratedEvolutionSystem
logger = getattr(ies, "logger", None)


# ---------- JSON 직렬화 유틸 ----------
def _json_default(o):
    try:
        import dataclasses
        import datetime
        import enum

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


def _to_jsonable(x):
    if isinstance(x, dict):
        return {str(k): _to_jsonable(v) for k, v in x.items()}
    if isinstance(x, (list, tuple, set, frozenset)):
        return [_to_jsonable(v) for v in x]
    if hasattr(x, "__dict__") and not isinstance(x, (str, bytes)):
        try:
            return _to_jsonable(vars(x))
        except Exception:
            return str(x)
    return x


# ---------- 안전한 로그 저장 ----------
async def _save_evolution_log(self, summary: Dict[str, Any]) -> None:
    try:
        artifacts = Path(ies.__file__).parent / "artifacts"
        artifacts.mkdir(parents=True, exist_ok=True)
        log_path = artifacts / "evolution_log.json"
        safe_summary = _to_jsonable(summary)
        with log_path.open("w", encoding="utf-8") as f:
            json.dump(safe_summary, f, indent=2, ensure_ascii=False, default=_json_default)
        if logger:
            logger.info(f"📝 진화 로그 저장: {log_path}")
    except Exception as e:
        if logger:
            logger.warning(f"⚠️ 로그 저장 실패: {e}")


# ---------- lazy init ----------
async def _ensure_components(self) -> None:
    try:
        if not hasattr(self, "self_rewriter") or self.self_rewriter is None:
            try:
                from self_rewriting_module import SelfRewritingModule

                self.self_rewriter = SelfRewritingModule()
            except Exception as e:
                if logger:
                    logger.error(f"SelfRewritingModule 초기화 실패: {e}")
                self.self_rewriter = None
        if not hasattr(self, "genetic_engine") or self.genetic_engine is None:
            try:
                from genetic_evolution_engine import GeneticEvolutionEngine

                self.genetic_engine = GeneticEvolutionEngine()
            except Exception as e:
                if logger:
                    logger.error(f"GeneticEvolutionEngine 초기화 실패: {e}")
                self.genetic_engine = None
        if not hasattr(self, "meta_coder") or self.meta_coder is None:
            try:
                from meta_coder import MetaCoder

                self.meta_coder = MetaCoder()
            except Exception as e:
                if logger:
                    logger.error(f"MetaCoder 초기화 실패: {e}")
                self.meta_coder = None
    except Exception as e:
        if logger:
            logger.error(f"컴포넌트 lazy init 실패: {e}")


# ---------- 노드 선택 (듀얼 인터페이스) ----------
# 기본은 '동기' 버전으로 제공 → 어느 호출부에서도 경고 없이 동작
def _get_optimal_node(self, *args, node: str | None = None, **kwargs) -> str:
    try:
        import socket

        return node or socket.gethostname()
    except Exception:
        return node or "local"


# 필요시 await 가능한 별칭
async def _get_optimal_node_async(self, *args, node: str | None = None, **kwargs) -> str:
    return _get_optimal_node(self, *args, node=node, **kwargs)


# ---------- 공개 API ----------
async def run_once(
    self, tracks: Tuple[str, ...] = ("self_rewrite", "genetic", "meta")
) -> Dict[str, Any]:
    results: Dict[str, Any] = {}
    try:
        if logger:
            logger.info(f"🚀 통합 진화 시스템 실행 시작: tracks={tracks}")
        # 보조 메서드 항상 최신으로 덮어쓰기(원본에 있더라도 안전 버전 사용)
        C._ensure_components = _ensure_components
        C._save_evolution_log = _save_evolution_log
        C._get_optimal_node = _get_optimal_node  # 동기 기본
        C._get_optimal_node_async = _get_optimal_node_async  # async 별칭

        await self._ensure_components()

        session = ies.EvolutionSession(
            session_id=f"evo_{int(time.time())}",
            stimulus_event="manual_run_once",
            start_time=time.time(),
        )

        for track in tracks:
            if track == "self_rewrite":
                if getattr(self, "self_rewriter", None) is None:
                    if logger:
                        logger.error("Self-Rewriting 컴포넌트 없음: 스킵")
                    results["self_rewrite"] = {"skipped": True, "reason": "self_rewriter_missing"}
                else:
                    results["self_rewrite"] = await self._execute_self_rewriting(session)
            elif track == "genetic":
                if getattr(self, "genetic_engine", None) is None:
                    if logger:
                        logger.error("Genetic Engine 없음: 스킵")
                    results["genetic"] = {"skipped": True, "reason": "genetic_engine_missing"}
                else:
                    results["genetic"] = await self._execute_genetic_evolution(session)
            elif track == "meta":
                if getattr(self, "meta_coder", None) is None:
                    if logger:
                        logger.error("Meta Coder 없음: 스킵")
                    results["meta"] = {"skipped": True, "reason": "meta_coder_missing"}
                else:
                    results["meta"] = await self._execute_meta_coding(session)

        summary = {
            "success": True,
            "session_id": session.session_id,
            "tracks_executed": tracks,
            "results": results,
            "runtime_ms": (time.time() - getattr(session, "start_time", time.time())) * 1000,
            "timestamp": time.time(),
        }
        await self._save_evolution_log(summary)
        if logger:
            logger.info(f"✅ 통합 진화 시스템 실행 완료: {summary.get('runtime_ms')}")
        return summary
    except Exception as e:
        if logger:
            logger.error(f"❌ 통합 진화 시스템 실행 실패: {e}")
        return {"success": False, "error": str(e)}


# ---------- 멱등 주입 ----------
C.run_once = run_once
C._get_optimal_node = _get_optimal_node
if not hasattr(C, "_get_optimal_node_async"):
    C._get_optimal_node_async = _get_optimal_node_async
C._ensure_components = _ensure_components
C._save_evolution_log = _save_evolution_log
