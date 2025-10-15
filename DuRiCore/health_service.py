#!/usr/bin/env python3
"""
DuRi 헬스 서비스
"""

import time
import os
import json
from datetime import datetime
from typing import Dict, Any
from .state_schema_manager import StateSchemaManager

class HealthService:
    def __init__(self):
        self.start_time = time.time()
        self.version = "1.0.0"
        self.git_sha = "abc12345"  # 실제로는 git 명령어로 가져옴
        self.state_manager = StateSchemaManager()
        
    def get_health_status(self) -> Dict[str, Any]:
        """헬스체크 상태 반환"""
        uptime_sec = time.time() - self.start_time
        
        # 마지막 사이클 ID 가져오기
        last_cycle_id = self.state_manager.get_last_cycle_id()
        
        # 큐 깊이 (가상)
        queue_depth = 0
        
        # 시스템 메트릭
        try:
            import psutil
            cpu_usage = psutil.cpu_percent(interval=0.1)
            memory_usage = psutil.virtual_memory().percent
        except ImportError:
            cpu_usage = 0.0
            memory_usage = 0.0
            
        return {
            "service": "duri-core",
            "status": "healthy",
            "version": self.version,
            "git_sha": self.git_sha,
            "uptime_sec": round(uptime_sec, 2),
            "last_cycle_id": last_cycle_id,
            "queue_depth": queue_depth,
            "cpu_usage": cpu_usage,
            "memory_usage": memory_usage,
            "timestamp": datetime.now().isoformat()
        }
        
    def get_ready_status(self) -> Dict[str, Any]:
        """준비 상태 확인"""
        dependencies_ok = True
        storage_ok = self.state_manager.migrate_if_needed()
        
        # 추가 의존성 확인
        try:
            import psutil
            psutil_ok = True
        except ImportError:
            psutil_ok = False
            
        return {
            "service": "duri-core",
            "status": "ready" if dependencies_ok and storage_ok and psutil_ok else "not_ready",
            "dependencies_ok": dependencies_ok,
            "storage_ok": storage_ok,
            "psutil_ok": psutil_ok,
            "timestamp": datetime.now().isoformat()
        }
        
    def get_live_status(self) -> Dict[str, Any]:
        """생존 상태 확인"""
        return {
            "service": "duri-core",
            "status": "alive",
            "pid": os.getpid(),
            "timestamp": datetime.now().isoformat()
        }
        
    def get_metrics(self) -> Dict[str, Any]:
        """메트릭 데이터 반환"""
        try:
            # 사이클 데이터 로드 (StateSchemaManager 통해)
            cycles = self.state_manager.get_cycles()
                
            # 메트릭 계산
            total_cycles = len(cycles)
            successful_cycles = len([c for c in cycles if c.get('success', False)])
            failed_cycles = total_cycles - successful_cycles
            
            # 최근 10개 사이클의 평균 처리 시간
            recent_cycles = cycles[-10:] if cycles else []
            avg_processing_time = sum(c.get('total_time', 0) for c in recent_cycles) / len(recent_cycles) if recent_cycles else 0
            
            return {
                "total_cycles": total_cycles,
                "successful_cycles": successful_cycles,
                "failed_cycles": failed_cycles,
                "success_rate": successful_cycles / total_cycles if total_cycles > 0 else 0,
                "avg_processing_time": round(avg_processing_time, 3),
                "last_cycle_id": cycles[-1].get('cycle_id', 'none') if cycles else 'none',
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
        
