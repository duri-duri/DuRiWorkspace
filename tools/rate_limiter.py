#!/usr/bin/env python3
"""
레이트리밋(푸시 보호)
- /push/deployment에 토큰 버킷(예: 10 req/s) 추가
- 실수/루프가 파이프라인을 범람시키지 않게
"""

import time
from typing import Dict
from dataclasses import dataclass

@dataclass
class TokenBucket:
    capacity: float
    tokens: float
    refill_rate: float
    last_refill: float

class RateLimiter:
    """토큰 버킷 기반 레이트리밋터"""
    
    def __init__(self):
        self.buckets: Dict[str, TokenBucket] = {}
        
        # 기본 버킷 설정
        self.default_capacity = 10.0  # 10개 토큰
        self.default_refill_rate = 10.0  # 초당 10개 리필
    
    def get_bucket(self, key: str) -> TokenBucket:
        """버킷 가져오기 또는 생성"""
        if key not in self.buckets:
            self.buckets[key] = TokenBucket(
                capacity=self.default_capacity,
                tokens=self.default_capacity,
                refill_rate=self.default_refill_rate,
                last_refill=time.time()
            )
        return self.buckets[key]
    
    def is_allowed(self, key: str, tokens: float = 1.0) -> bool:
        """요청 허용 여부 확인"""
        bucket = self.get_bucket(key)
        now = time.time()
        
        # 토큰 리필
        time_passed = now - bucket.last_refill
        tokens_to_add = time_passed * bucket.refill_rate
        bucket.tokens = min(bucket.capacity, bucket.tokens + tokens_to_add)
        bucket.last_refill = now
        
        # 토큰 소비
        if bucket.tokens >= tokens:
            bucket.tokens -= tokens
            return True
        else:
            return False
    
    def get_remaining_tokens(self, key: str) -> float:
        """남은 토큰 수 확인"""
        bucket = self.get_bucket(key)
        now = time.time()
        
        # 토큰 리필
        time_passed = now - bucket.last_refill
        tokens_to_add = time_passed * bucket.refill_rate
        bucket.tokens = min(bucket.capacity, bucket.tokens + tokens_to_add)
        bucket.last_refill = now
        
        return bucket.tokens

# 전역 인스턴스
rate_limiter = RateLimiter()
