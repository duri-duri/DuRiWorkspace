import importlib

import pytest

MODULES = [
    "duri_core",
    "duri_brain",
    "duri_evolution",
]


@pytest.mark.parametrize("m", MODULES)
def test_imports(m):
    importlib.import_module(m)
