#!/usr/bin/env python3
"""
DuRi Rate Limiter - IP 기준 Rate limit & burst 보호
"""

import time
from collections import defaultdict, deque
from threading import RLock
from typing import Dict, Any, Optional
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from DuRiCore.global_logging_manager import get_duri_logger
from DuRiCore.health.config import get_rate_limit_config

logger = get_duri_logger("rate_limiter")

class TokenBucket:
    """토큰 버킷 알고리즘 구현"""
    
    def __init__(self, capacity: int, refill_rate: float):
        """
        Args:
            capacity: 버킷 용량 (버스트 크기)
            refill_rate: 초당 리필 속도 (RPS)
        """
        self.capacity = capacity
        self.refill_rate = refill_rate
        self.tokens = capacity
        self.last_refill = time.time()
        self.lock = RLock()
    
    def consume(self, tokens: int = 1) -> bool:
        """
        토큰 소비 시도
        
        Args:
            tokens: 소비할 토큰 수
            
        Returns:
            성공하면 True, 실패하면 False
        """
        with self.lock:
            now = time.time()
            
            # 토큰 리필
            time_passed = now - self.last_refill
            tokens_to_add = time_passed * self.refill_rate
            self.tokens = min(self.capacity, self.tokens + tokens_to_add)
            self.last_refill = now
            
            # 토큰 소비 시도
            if self.tokens >= tokens:
                self.tokens -= tokens
                return True
            
            return False
    
    def get_stats(self) -> Dict[str, Any]:
        """버킷 상태 반환"""
        with self.lock:
            return {
                "tokens": self.tokens,
                "capacity": self.capacity,
                "refill_rate": self.refill_rate,
                "last_refill": self.last_refill
            }

class RateLimiter:
    """IP 기준 Rate Limiter"""
    
    def __init__(self):
        self.buckets: Dict[str, TokenBucket] = {}
        self.lock = RLock()
        self.config = get_rate_limit_config()
        
        # 기본 설정
        self.default_rps = self.config.get("rps", 1)
        self.default_burst = self.config.get("burst", 3)
        
        logger.info(f"RateLimiter 초기화: rps={self.default_rps}, burst={self.default_burst}")
    
    def _get_client_ip(self, request: Request) -> str:
        """클라이언트 IP 추출"""
        # X-Forwarded-For 헤더 확인 (프록시 환경)
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        # X-Real-IP 헤더 확인
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip
        
        # 직접 연결
        return request.client.host if request.client else "unknown"
    
    def _get_bucket(self, client_ip: str) -> TokenBucket:
        """클라이언트 IP에 대한 토큰 버킷 가져오기"""
        with self.lock:
            if client_ip not in self.buckets:
                self.buckets[client_ip] = TokenBucket(
                    capacity=self.default_burst,
                    refill_rate=self.default_rps
                )
                logger.debug(f"새로운 클라이언트 IP 버킷 생성: {client_ip}")
            
            return self.buckets[client_ip]
    
    def is_allowed(self, request: Request) -> tuple[bool, Dict[str, Any]]:
        """
        요청 허용 여부 확인
        
        Args:
            request: FastAPI Request 객체
            
        Returns:
            (허용 여부, 상세 정보)
        """
        client_ip = self._get_client_ip(request)
        bucket = self._get_bucket(client_ip)
        
        # 토큰 소비 시도
        allowed = bucket.consume(1)
        
        stats = bucket.get_stats()
        stats["client_ip"] = client_ip
        stats["allowed"] = allowed
        
        if not allowed:
            logger.warning(f"Rate limit 초과: IP={client_ip}, stats={stats}")
        
        return allowed, stats
    
    def get_stats(self) -> Dict[str, Any]:
        """전체 통계 반환"""
        with self.lock:
            return {
                "total_clients": len(self.buckets),
                "default_rps": self.default_rps,
                "default_burst": self.default_burst,
                "clients": {
                    ip: bucket.get_stats() 
                    for ip, bucket in self.buckets.items()
                }
            }
    
    def cleanup_expired(self, max_age_sec: int = 3600):
        """오래된 버킷 정리"""
        with self.lock:
            now = time.time()
            expired_ips = []
            
            for ip, bucket in self.buckets.items():
                if now - bucket.last_refill > max_age_sec:
                    expired_ips.append(ip)
            
            for ip in expired_ips:
                del self.buckets[ip]
            
            if expired_ips:
                logger.info(f"RateLimiter 만료된 클라이언트 정리: {len(expired_ips)}개")

# 전역 인스턴스
rate_limiter = RateLimiter()

def rate_limit_middleware(request: Request, call_next):
    """Rate limit 미들웨어"""
    
    # Rate limit 확인
    allowed, stats = rate_limiter.is_allowed(request)
    
    if not allowed:
        # 429 Too Many Requests 응답
        retry_after = int(1 / rate_limiter.default_rps)  # 초 단위
        
        return JSONResponse(
            status_code=429,
            content={
                "error": "Rate limit exceeded",
                "message": "Too many requests",
                "retry_after": retry_after,
                "client_ip": stats["client_ip"]
            },
            headers={
                "Retry-After": str(retry_after),
                "X-RateLimit-Limit": str(rate_limiter.default_rps),
                "X-RateLimit-Remaining": "0",
                "X-RateLimit-Reset": str(int(time.time()) + retry_after)
            }
        )
    
    # 요청 처리
    response = call_next(request)
    
    # Rate limit 헤더 추가
    remaining = int(stats["tokens"])
    response.headers["X-RateLimit-Limit"] = str(rate_limiter.default_rps)
    response.headers["X-RateLimit-Remaining"] = str(remaining)
    response.headers["X-RateLimit-Reset"] = str(int(time.time()) + 1)
    
    return response

def get_rate_limit_stats() -> Dict[str, Any]:
    """Rate limit 통계 반환"""
    return rate_limiter.get_stats()

def cleanup_rate_limits():
    """Rate limit 정리 작업"""
    rate_limiter.cleanup_expired()
