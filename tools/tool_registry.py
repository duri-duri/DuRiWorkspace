#!/usr/bin/env python3
"""
도구 레지스트리 + 샌드박스(권한·쿼터·감사로그)
- 외부 액션을 통제해야 나머지 모듈을 안전하게 얹을 수 있음
- read-only→safe-write 단계적 권한, 카나리/플래그로 점진 노출
"""

import json
import time
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from enum import Enum
from dataclasses import dataclass, asdict

class ToolPermission(Enum):
    READ_ONLY = "read_only"
    SAFE_WRITE = "safe_write"
    FULL_ACCESS = "full_access"

class ToolCategory(Enum):
    DATABASE = "database"
    HTTP = "http"
    FILE_SYSTEM = "file_system"
    DOCKER = "docker"
    REDIS = "redis"
    BACKUP = "backup"
    VECTOR_DB = "vector_db"

@dataclass
class ToolDefinition:
    name: str
    category: ToolCategory
    permission: ToolPermission
    description: str
    endpoint: str
    parameters: Dict[str, Any]
    quota_per_hour: int = 100
    quota_per_day: int = 1000
    requires_auth: bool = True
    sandbox_enabled: bool = True

@dataclass
class ToolUsage:
    tool_name: str
    user_id: str
    timestamp: datetime
    parameters: Dict[str, Any]
    result: Dict[str, Any]
    execution_time: float
    success: bool
    error_message: Optional[str] = None

class ToolRegistry:
    """도구 레지스트리 + 샌드박스"""
    
    def __init__(self):
        self.tools: Dict[str, ToolDefinition] = {}
        self.usage_log: List[ToolUsage] = []
        self.user_quotas: Dict[str, Dict[str, int]] = {}
        self.audit_log: List[Dict[str, Any]] = []
        
        # 기본 도구 등록
        self._register_default_tools()
        
    def _register_default_tools(self):
        """기본 도구들 등록"""
        default_tools = [
            ToolDefinition(
                name="postgres_query",
                category=ToolCategory.DATABASE,
                permission=ToolPermission.READ_ONLY,
                description="PostgreSQL 쿼리 실행 (읽기 전용)",
                endpoint="postgresql://duri:duri@localhost:5432/duri",
                parameters={"query": "string", "timeout": "int"},
                quota_per_hour=50,
                quota_per_day=500
            ),
            ToolDefinition(
                name="redis_get",
                category=ToolCategory.REDIS,
                permission=ToolPermission.READ_ONLY,
                description="Redis 키 조회",
                endpoint="redis://localhost:6379/0",
                parameters={"key": "string"},
                quota_per_hour=100,
                quota_per_day=1000
            ),
            ToolDefinition(
                name="http_request",
                category=ToolCategory.HTTP,
                permission=ToolPermission.SAFE_WRITE,
                description="HTTP 요청 (안전한 쓰기)",
                endpoint="http://localhost:8083",
                parameters={"method": "string", "url": "string", "data": "dict"},
                quota_per_hour=30,
                quota_per_day=300
            ),
            ToolDefinition(
                name="docker_status",
                category=ToolCategory.DOCKER,
                permission=ToolPermission.READ_ONLY,
                description="Docker 컨테이너 상태 조회",
                endpoint="docker://localhost",
                parameters={"container": "string"},
                quota_per_hour=20,
                quota_per_day=200
            )
        ]
        
        for tool in default_tools:
            self.register_tool(tool)
    
    def register_tool(self, tool: ToolDefinition):
        """도구 등록"""
        self.tools[tool.name] = tool
        self._audit_log("tool_registered", {
            "tool_name": tool.name,
            "category": tool.category.value,
            "permission": tool.permission.value
        })
    
    def check_permission(self, tool_name: str, user_id: str, action: str) -> bool:
        """권한 확인"""
        if tool_name not in self.tools:
            return False
        
        tool = self.tools[tool_name]
        
        # 권한 레벨 확인
        if action == "read" and tool.permission in [ToolPermission.READ_ONLY, ToolPermission.SAFE_WRITE, ToolPermission.FULL_ACCESS]:
            return True
        elif action == "write" and tool.permission in [ToolPermission.SAFE_WRITE, ToolPermission.FULL_ACCESS]:
            return True
        elif action == "admin" and tool.permission == ToolPermission.FULL_ACCESS:
            return True
        
        return False
    
    def check_quota(self, tool_name: str, user_id: str) -> bool:
        """쿼터 확인"""
        if tool_name not in self.tools:
            return False
        
        tool = self.tools[tool_name]
        now = datetime.now()
        
        # 사용자 쿼터 초기화
        if user_id not in self.user_quotas:
            self.user_quotas[user_id] = {}
        
        if tool_name not in self.user_quotas[user_id]:
            self.user_quotas[user_id][tool_name] = {
                "hourly_count": 0,
                "daily_count": 0,
                "last_hour": now.hour,
                "last_day": now.day
            }
        
        quota = self.user_quotas[user_id][tool_name]
        
        # 시간별 쿼터 리셋
        if now.hour != quota["last_hour"]:
            quota["hourly_count"] = 0
            quota["last_hour"] = now.hour
        
        # 일별 쿼터 리셋
        if now.day != quota["last_day"]:
            quota["daily_count"] = 0
            quota["last_day"] = now.day
        
        # 쿼터 확인
        if quota["hourly_count"] >= tool.quota_per_hour:
            return False
        
        if quota["daily_count"] >= tool.quota_per_day:
            return False
        
        return True
    
    def execute_tool(self, tool_name: str, user_id: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """도구 실행 (샌드박스)"""
        start_time = time.time()
        
        try:
            # 권한 확인
            if not self.check_permission(tool_name, user_id, "read"):
                raise PermissionError(f"권한 없음: {tool_name}")
            
            # 쿼터 확인
            if not self.check_quota(tool_name, user_id):
                raise QuotaExceededError(f"쿼터 초과: {tool_name}")
            
            # 샌드박스 실행
            result = self._execute_in_sandbox(tool_name, parameters)
            
            # 사용량 업데이트
            self._update_quota(tool_name, user_id)
            
            # 사용 로그 기록
            usage = ToolUsage(
                tool_name=tool_name,
                user_id=user_id,
                timestamp=datetime.now(),
                parameters=parameters,
                result=result,
                execution_time=time.time() - start_time,
                success=True
            )
            self.usage_log.append(usage)
            
            # 감사 로그
            self._audit_log("tool_executed", {
                "tool_name": tool_name,
                "user_id": user_id,
                "success": True,
                "execution_time": usage.execution_time
            })
            
            return result
            
        except Exception as e:
            # 실패 로그
            usage = ToolUsage(
                tool_name=tool_name,
                user_id=user_id,
                timestamp=datetime.now(),
                parameters=parameters,
                result={},
                execution_time=time.time() - start_time,
                success=False,
                error_message=str(e)
            )
            self.usage_log.append(usage)
            
            # 감사 로그
            self._audit_log("tool_failed", {
                "tool_name": tool_name,
                "user_id": user_id,
                "error": str(e),
                "execution_time": usage.execution_time
            })
            
            raise
    
    def _execute_in_sandbox(self, tool_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """샌드박스에서 도구 실행"""
        # 실제 구현에서는 각 도구별로 안전한 실행 환경 구성
        # 여기서는 시뮬레이션
        return {
            "status": "success",
            "data": f"Sandbox execution of {tool_name}",
            "timestamp": datetime.now().isoformat()
        }
    
    def _update_quota(self, tool_name: str, user_id: str):
        """쿼터 업데이트"""
        if user_id not in self.user_quotas:
            self.user_quotas[user_id] = {}
        
        if tool_name not in self.user_quotas[user_id]:
            self.user_quotas[user_id][tool_name] = {
                "hourly_count": 0,
                "daily_count": 0,
                "last_hour": datetime.now().hour,
                "last_day": datetime.now().day
            }
        
        self.user_quotas[user_id][tool_name]["hourly_count"] += 1
        self.user_quotas[user_id][tool_name]["daily_count"] += 1
    
    def _audit_log(self, action: str, data: Dict[str, Any]):
        """감사 로그 기록"""
        self.audit_log.append({
            "timestamp": datetime.now().isoformat(),
            "action": action,
            "data": data
        })
    
    def get_usage_stats(self, user_id: Optional[str] = None) -> Dict[str, Any]:
        """사용량 통계"""
        if user_id:
            user_logs = [log for log in self.usage_log if log.user_id == user_id]
        else:
            user_logs = self.usage_log
        
        return {
            "total_usage": len(user_logs),
            "success_rate": sum(1 for log in user_logs if log.success) / len(user_logs) if user_logs else 0,
            "avg_execution_time": sum(log.execution_time for log in user_logs) / len(user_logs) if user_logs else 0,
            "tool_breakdown": self._get_tool_breakdown(user_logs)
        }
    
    def _get_tool_breakdown(self, logs: List[ToolUsage]) -> Dict[str, int]:
        """도구별 사용량 분석"""
        breakdown = {}
        for log in logs:
            breakdown[log.tool_name] = breakdown.get(log.tool_name, 0) + 1
        return breakdown

class QuotaExceededError(Exception):
    """쿼터 초과 예외"""
    pass

# 전역 인스턴스
tool_registry = ToolRegistry()
