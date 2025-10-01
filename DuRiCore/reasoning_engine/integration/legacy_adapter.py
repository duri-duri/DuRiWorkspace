# 과거 호출 호환용(shim). 점진 폐기 예정.
from DuRiCore.reasoning_engine.core.reasoning_engine import ReasoningEngine as _RE


def legacy_process(query: str, context: str = "general") -> dict:
    return _RE().process({"query": query, "context": context})
