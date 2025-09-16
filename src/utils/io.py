# src/utils/io.py
"""
I/O 유틸리티
"""
import json
import yaml
from pathlib import Path
from typing import Any, Dict

def load_json(path: Path) -> Dict[str, Any]:
    """JSON 파일 로드"""
    return json.loads(path.read_text(encoding="utf-8"))

def save_json(path: Path, data: Any) -> None:
    """JSON 파일 저장"""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

def load_yaml(path: Path) -> Dict[str, Any]:
    """YAML 파일 로드"""
    return yaml.safe_load(path.read_text(encoding="utf-8"))

def save_yaml(path: Path, data: Any) -> None:
    """YAML 파일 저장"""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.dump(data, default_flow_style=False), encoding="utf-8")
