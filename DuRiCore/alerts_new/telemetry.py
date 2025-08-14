from __future__ import annotations
import random
import logging
import math
import statistics
import json
from dataclasses import dataclass
from typing import List, Optional, Dict

logger = logging.getLogger(__name__)

# Baseline profiles for consistent parameter loading (DEBUG independent)
BASELINE_PROFILES = {
    "baseline_v1": {
        "base_missing_prob": 0.0002,
        "base_mu_ms": 700.0,
        "base_sigma": 0.24,
        "max_tail_ms": 1200.0,
        "missing_given_timeout": 0.005,
        "tail_prob": 0.0005,
        "tail_scale_ms": 40.0,
        "timeout_over_ms": 60.0,
        "base_min_ms": 450.0,
        "base_max_ms": 950.0,
    }
}

def _load_sim_params(config):
    """Load simulation parameters with fallback to baseline profile"""
    # Always start with baseline_v1 as the foundation
    params = {**BASELINE_PROFILES["baseline_v1"]}
    
    if config is None or not hasattr(config, "sim"):
        # No config provided, use baseline_v1
        logger.info("[SimAlertProbe] No config provided, using baseline_v1 profile")
        return params
    
    sim = config.sim
    
    # Try profile-based loading first
    prof_key = getattr(sim, "profile", None)
    if prof_key and prof_key in BASELINE_PROFILES:
        params = {**BASELINE_PROFILES[prof_key]}
        logger.info(f"[SimAlertProbe] Using profile: {prof_key}")
    else:
        # Try explicit fields; if missing, keep baseline_v1 values
        for k in BASELINE_PROFILES["baseline_v1"].keys():
            if hasattr(sim, k):
                params[k] = getattr(sim, k)
        
        if prof_key:
            logger.info(f"[SimAlertProbe] Profile '{prof_key}' not found, using explicit + baseline_v1 fallback")
        else:
            logger.info("[SimAlertProbe] No profile specified, using explicit + baseline_v1 fallback")
    
    # Hard safety clamps
    params["max_tail_ms"] = min(params["max_tail_ms"], 2000.0)
    params["base_sigma"] = max(0.05, min(params["base_sigma"], 1.0))
    params["tail_prob"] = max(0.0001, min(params["tail_prob"], 0.1))
    
    return params

@dataclass
class AlertResult:
    """알림 결과 데이터 클래스"""
    success: bool
    latency_ms: float
    timed_out: bool
    missing: bool

class AlertProbe:
    """알림 프로브 인터페이스"""
    def send_and_measure(self, timeout_ms: int) -> AlertResult: ...

class SimAlertProbe:
    """
    시뮬레이션 알림 프로브
    
    Attributes:
        seed: 랜덤 시드
        base_min_ms: 기본 지연시간 최소값(ms)
        base_max_ms: 기본 지연시간 최대값(ms)
        tail_prob: 지수 꼬리 진입 확률
        tail_scale_ms: 지수 꼬리 규모(ms)
        timeout_over_ms: 타임아웃 발생 시 초과 지연 상한(ms)
    """
    def __init__(
        self,
        seed: int = 42,
        config=None,
        base_min_ms: float = 450.0,
        base_max_ms: float = 950.0,
        tail_prob: float = 0.004,            # 더 보수적인 꼬리(기본 0.4%)
        tail_scale_ms: float = 160.0,
        timeout_over_ms: float = 80.0,
        missing_given_timeout: float = 0.02,  # timeout 조건부 누락 2%로 하향
        debug: bool = False
    ):
        self.r = random.Random(seed)
        
        # Load parameters with fallback (DEBUG independent)
        self.params = _load_sim_params(config)
        
        # Apply loaded parameters
        self.base_min_ms = self.params["base_min_ms"]
        self.base_max_ms = self.params["base_max_ms"]
        self.tail_prob = self.params["tail_prob"]
        self.tail_scale_ms = self.params["tail_scale_ms"]
        self.timeout_over_ms = self.params["timeout_over_ms"]
        self.missing_given_timeout = self.params["missing_given_timeout"]
        self.base_missing_prob = self.params["base_missing_prob"]
        self.base_sigma = self.params["base_sigma"]
        self.base_mu_ms = self.params["base_mu_ms"]
        self.max_tail_ms = self.params["max_tail_ms"]
        
        # Generate pure parameter fingerprint (only sorted params, no metadata)
        self._param_fingerprint = hash(tuple(sorted(self.params.items())))
        
        # Always log parameters at INFO level (DEBUG independent)
        logger.info("[SimAlertProbe] Using params: %s", json.dumps(self.params, sort_keys=True))
        logger.info("[SimAlertProbe] Param fingerprint: %s", self._param_fingerprint)
        
        logger.debug(f"SimAlertProbe 초기화: seed={seed}, tail_prob={self.tail_prob}, tail_scale={self.tail_scale_ms}ms")

    def param_fingerprint(self) -> int:
        return self._param_fingerprint

    def send_and_measure(self, timeout_ms: int) -> AlertResult:
        """알림 전송 및 측정 시뮬레이션"""
        # 기본 지연시간 (lognormal 분포 사용)
        if hasattr(self, 'base_sigma') and hasattr(self, 'base_mu_ms'):
            # lognormal 분포로 베이스 지연 생성
            u = self.r.random()
            v = self.r.random()
            z = math.sqrt(-2 * math.log(u)) * math.cos(2 * math.pi * v)  # Box-Muller
            base = math.exp(self.base_mu_ms + self.base_sigma * z)
            # 범위 제한
            base = max(self.base_min_ms, min(self.base_max_ms, base))
        else:
            base = self.r.uniform(self.base_min_ms, self.base_max_ms)
        
        # 지수 꼬리: 평균 = tail_scale_ms
        tail = self.r.expovariate(1.0 / self.tail_scale_ms)
        
        # max_tail_ms 제한 적용
        if hasattr(self, 'max_tail_ms'):
            tail = min(tail, self.max_tail_ms)
        
        # 총 지연시간
        lat = base + tail
        
        # 베이스 누락 확률 체크
        base_missing = False
        if hasattr(self, 'base_missing_prob'):
            base_missing = self.r.random() < self.base_missing_prob
        
        # 타임아웃 시뮬레이션
        if self.r.random() < self.tail_prob:
            over = self.r.uniform(0, self.timeout_over_ms)
            missing = self.r.random() < self.missing_given_timeout
            return AlertResult(False, timeout_ms + over, True, missing)
        
        # 베이스 누락이 있으면 missing으로 처리
        if base_missing:
            return AlertResult(False, lat, False, True)
        
        return AlertResult(True, lat, False, False)

class AlertEvaluator:
    """알림 평가자"""
    def __init__(self):
        logger.debug("AlertEvaluator 초기화")
    
    def evaluate(self, probe: AlertProbe, trials: int, timeout_ms: int, return_samples: bool = False) -> Dict[str, float]:
        """알림 성능 평가"""
        L = []  # 지연시간 리스트
        to = 0   # 타임아웃 수
        miss = 0 # 누락 수
        delivered = 0  # 전달 성공 수
        
        logger.info(f"알림 평가 시작: trials={trials}, timeout={timeout_ms}ms")
        
        for i in range(trials):
            r = probe.send_and_measure(timeout_ms)
            to += 1 if r.timed_out else 0
            miss += 1 if r.missing else 0
            delivered += 1 if r.success else 0
            
            if r.success:
                L.append(r.latency_ms)
            
            # 진행 상황 로깅 (10%마다)
            if (i + 1) % max(1, trials // 10) == 0:
                logger.debug(f"진행률: {(i + 1) / trials * 100:.1f}%")
        
        # P95 계산
        if L:
            p95 = statistics.quantiles(L, n=100)[94]
        else:
            p95 = float("inf")
        
        # 결과 계산
        result = {
            "p95_ms": round(p95, 2),
            "timeout_rate": round(to / trials, 4),
            "missing_rate": round(miss / trials, 4),
            "delivered": delivered,
            "total": trials,
            "timeouts": to,
            "missings": miss,
        }
        
        # 샘플 저장 (필요시)
        if return_samples:
            result["latencies_ms"] = L  # 전달된 샘플만 저장
        
        # 분포 분석 로깅 추가
        if L:
            near_1800 = sum(1800 <= x < 2000 for x in L)
            over_2000 = sum(x >= 2000 for x in L)
            logger.info(f"[sim-dist] count(>=1800,<2000)={near_1800}, count(>={timeout_ms})={over_2000}")
        
        logger.info(f"알림 평가 완료: p95={result['p95_ms']}ms, "
                   f"timeout_rate={result['timeout_rate']}, "
                   f"missing_rate={result['missing_rate']}")
        
        return result
