from DuRiCore.trace import emit_trace
from dataclasses import dataclass
from typing import Dict, Any, List, Optional
import yaml
import logging
from pathlib import Path
logger = logging.getLogger(__name__)

@dataclass(frozen=True)
class RetryConfig:
    transient_max_attempts: int = 2
    backoff_ms: List[int] = None
    jitter_ms: int = 0

@dataclass(frozen=True)
class TimeoutsConfig:
    per_attempt_ms: int = 10

@dataclass(frozen=True)
class SLOConfig:
    availability_excludes_validation: bool = True

@dataclass(frozen=True)
class StressP95Config:
    light: int = 15
    medium: int = 20
    heavy: int = 30
    extreme: int = 35

@dataclass(frozen=True)
class StressThresholds:
    success_rate_min: float = 0.9
    availability_min: float = 0.95
    p95_ms: StressP95Config = StressP95Config()
    slo: SLOConfig = SLOConfig()

@dataclass(frozen=True)
class RetryPolicy:
    transient_max_attempts: int = 2
    backoff_ms: List[int] = None
    jitter_ms: int = 0

@dataclass(frozen=True)
class AlertingPolicy:
    on_system_error: bool = True

@dataclass(frozen=True)
class Phase4BConfig:
    profile: str = 'dev'
    stress: StressThresholds = StressThresholds()
    retry: RetryPolicy = RetryPolicy(backoff_ms=[2, 8])
    timeouts: TimeoutsConfig = TimeoutsConfig()
    alerting: AlertingPolicy = AlertingPolicy()

def _dict_get(d: dict, path: List[str], default):
    """안전한 중첩 딕셔너리 접근"""
    cur = d
    for k in path:
        if not isinstance(cur, dict) or k not in cur:
            return default
        cur = cur[k]
    return cur

def _coerce_list(v) -> List[int]:
    """값을 정수 리스트로 변환"""
    if isinstance(v, (list, tuple)):
        return [int(x) for x in v]
    return [int(v)]

def load_thresholds(profile: str='dev', path: str | Path='config/thresholds.yaml') -> Phase4BConfig:
    p = Path(path)
    if not p.exists():
        logger.warning('thresholds.yaml not found. Using defaults.')
        return Phase4BConfig()
    try:
        raw = yaml.safe_load(p.read_text(encoding='utf-8')) or {}
        prof = raw.get('profile', profile)
        stress = raw.get('stress', {})
        p95 = stress.get('p95_ms', {})
        slo = stress.get('slo', {})
        stress_cfg = StressThresholds(success_rate_min=float(stress.get('success_rate_min', 0.9)), availability_min=float(stress.get('availability_min', 0.95)), p95_ms=StressP95Config(light=int(p95.get('light', 15)), medium=int(p95.get('medium', 20)), heavy=int(p95.get('heavy', 30)), extreme=int(p95.get('extreme', 35))), slo=SLOConfig(availability_excludes_validation=bool(slo.get('availability_excludes_validation', True))))
        retry = raw.get('retry', {})
        retry_cfg = RetryPolicy(transient_max_attempts=int(retry.get('transient_max_attempts', 2)), backoff_ms=_coerce_list(retry.get('backoff_ms', [2, 8])), jitter_ms=int(retry.get('jitter_ms', 3)))
        timeouts = raw.get('timeouts', {})
        timeouts_cfg = TimeoutsConfig(per_attempt_ms=int(timeouts.get('per_attempt_ms', 10)))
        alerting = raw.get('alerting', {})
        alert_cfg = AlertingPolicy(on_system_error=bool(alerting.get('on_system_error', True)))
        if not retry_cfg.backoff_ms:
            logger.warning('retry.backoff_ms is empty; using [2,8] fallback.')
            retry_cfg = RetryPolicy(transient_max_attempts=retry_cfg.transient_max_attempts, backoff_ms=[2, 8], jitter_ms=retry_cfg.jitter_ms)
        return Phase4BConfig(profile=prof, stress=stress_cfg, retry=retry_cfg, timeouts=timeouts_cfg, alerting=alert_cfg)
    except Exception as e:
        logger.warning(f'Invalid thresholds.yaml ({e}). Using defaults.')
        return Phase4BConfig()