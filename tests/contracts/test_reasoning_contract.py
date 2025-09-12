import pytest
from logical_reasoning_engine import ReasoningEngine

@pytest.mark.parametrize("inp,exp", [
    ({"query":"1+1","context":"math"},{"result":2,"confidence":0.95}),
    ({"query":"weather","context":"general"},{"result":"unknown","confidence":0.3}),
])
def test_reasoning_contract(inp, exp):
    eng = ReasoningEngine()
    out = eng.process(inp)
    assert out["result"] == exp["result"]
    assert abs(out["confidence"]-exp["confidence"]) < 0.1
