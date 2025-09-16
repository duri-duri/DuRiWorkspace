# src/utils/seed.py
"""
시드 관리 유틸리티
"""
import random
import hashlib
from typing import Union

def set_seed(seed: Union[int, str]) -> None:
    """시드 설정"""
    if isinstance(seed, str):
        # 문자열을 해시해서 정수로 변환
        seed = int(hashlib.md5(seed.encode()).hexdigest()[:8], 16)
    
    random.seed(seed)

def get_seed_from_string(s: str) -> int:
    """문자열에서 시드 생성"""
    return int(hashlib.md5(s.encode()).hexdigest()[:8], 16)

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