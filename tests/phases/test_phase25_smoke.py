import importlib

def test_phase25_import_and_boot():
    mod = importlib.import_module("duri_finale.runner")
    out = getattr(mod, "boot")()
    assert isinstance(out, dict)
    for k in ["creative","ethics","future","evolution"]:
        assert k in out and out[k] is True
