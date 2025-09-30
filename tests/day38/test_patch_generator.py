import json
import subprocess
import tempfile
import os
from pathlib import Path

def run_patch_generator(action, file_path, *args):
    """Run patch generator with given arguments"""
    cmd = ["python3", "tools/patch_generator.py", action, file_path] + list(args)
    result = subprocess.run(cmd, capture_output=True, text=True)
    return json.loads(result.stdout) if result.returncode == 0 else None

def test_add_import_action():
    """Test add_import action"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write("print('hello world')\n")
        temp_file = f.name
    
    try:
        result = run_patch_generator("add_import", temp_file, "duri_common.settings")
        assert result is not None
        assert result["action"] == "add_import"
        assert result["file"] == temp_file
        assert result["module"] == "duri_common.settings"
    finally:
        os.unlink(temp_file)

def test_increase_timeout_action():
    """Test increase_timeout action"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write("timeout = 30 * timeout\n")
        temp_file = f.name
    
    try:
        result = run_patch_generator("increase_timeout", temp_file, "1.5")
        assert result is not None
        assert result["action"] == "increase_timeout"
        assert result["file"] == temp_file
        assert result["factor"] == 1.5
    finally:
        os.unlink(temp_file)

def test_unknown_action():
    """Test unknown action handling"""
    result = run_patch_generator("unknown_action", "test.py")
    assert result is not None
    assert result["status"] == "unknown_action"
