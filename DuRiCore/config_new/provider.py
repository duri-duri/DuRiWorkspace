from __future__ import annotations
from typing import Any, Mapping, Optional, Dict, List
from pathlib import Path
import os
import logging

logger = logging.getLogger("DuRiCore.config_new.provider")

class ConfigProvider:
    """설정 제공자 인터페이스"""
    def get(self, path: str, default: Optional[Any]=None) -> Any: ...
    def section(self, path: str) -> Mapping[str, Any]: ...

class _YamlSource:
    """YAML 파일 소스"""
    def __init__(self, p: str): 
        self.path = Path(p)
    
    def load(self) -> Dict[str, Any]:
        try:
            import yaml
            if not self.path.exists():
                logger.debug(f"YAML 파일이 존재하지 않음: {self.path}")
                return {}
            return yaml.safe_load(self.path.read_text(encoding="utf-8")) or {}
        except Exception as e:
            logger.warning(f"YAML 파일 로드 실패: {e}")
            return {}

class _EnvSource:
    """환경변수 소스"""
    def __init__(self, prefix: str="DURI_"): 
        self.prefix = prefix
    
    def load(self) -> Dict[str, Any]:
        out: Dict[str, Any] = {}
        for k, v in os.environ.items():
            if k.startswith(self.prefix):
                # DURI_DAY9_ALERT_LATENCY_P95_MS -> day9.alert_latency_p95_ms
                key = k[len(self.prefix):].lower().replace('_', '.')
                out[key] = v
        return out

class _DefaultSource:
    """기본값 소스"""
    def __init__(self, d: Dict[str, Any]): 
        self.d = d
    
    def load(self) -> Dict[str, Any]: 
        return self.d

class MergedProvider(ConfigProvider):
    """여러 소스를 병합하는 설정 제공자"""
    def __init__(self, sources: List[dict]):  # list of {"root": str, "data": dict}
        self._rooted = sources
    
    def _resolve(self, path: str) -> Any:
        keys = path.split(".")
        for src in self._rooted:
            node = src["data"].get(src["root"], src["data"]) if src["root"] else src["data"]
            cur = node
            ok = True
            for k in keys:
                if isinstance(cur, dict) and k in cur:
                    cur = cur[k]
                else:
                    ok = False
                    break
            if ok:
                return cur
        return None
    
    def get(self, path: str, default: Optional[Any]=None) -> Any:
        v = self._resolve(path)
        return v if v is not None else default
    
    def section(self, path: str) -> Mapping[str, Any]:
        v = self.get(path, {}) or {}
        return v if isinstance(v, dict) else {}

def build_provider() -> ConfigProvider:
    """설정 제공자 빌드"""
    yaml_data = _YamlSource("configs/thresholds.yaml").load()
    env_data = _EnvSource("DURI_").load()
    defaults = _DefaultSource({
        "day9": {
            "alert_latency_p95_ms": 2000,  # 2초로 증가
            "alert_timeout_rate": 0.02,
            "alert_missing_rate": 0.005,
            "sweep": {
                "intensities": [0.2, 0.5, 0.8],
                "concurrencies": [1, 5, 10]
            }
        }
    }).load()
    
    return MergedProvider([
        {"root": "", "data": yaml_data},
        {"root": "", "data": {"day9": env_data}},  # env는 단순 키 덮어쓰기 용
        {"root": "", "data": defaults},
    ])
