from DuRiCore.reasoning_engine.core.reasoning_engine import ReasoningEngine
def handle_request(payload: dict) -> dict:
    return ReasoningEngine().process(payload)
