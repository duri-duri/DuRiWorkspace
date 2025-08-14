"""
Day 6: 대시보드 스키마
실시간 대시보드 API에 필요한 Pydantic 모델들
"""

from pydantic import BaseModel, Field
from typing import Dict, List, Any, Optional
from datetime import datetime

class ServiceStatus(BaseModel):
    """서비스 상태 정보"""
    name: str = Field(..., description="서비스 이름")
    status: str = Field(..., description="서비스 상태 (healthy, warning, error)")
    port: int = Field(..., description="서비스 포트")
    uptime: Optional[str] = Field(None, description="서비스 가동 시간")
    memory_usage: Optional[float] = Field(None, description="메모리 사용량 (%)")
    cpu_usage: Optional[float] = Field(None, description="CPU 사용량 (%)")
    last_check: datetime = Field(default_factory=datetime.now, description="마지막 체크 시간")

class SystemMetrics(BaseModel):
    """시스템 메트릭"""
    cpu_usage: float = Field(..., description="CPU 사용률 (%)")
    memory_usage: float = Field(..., description="메모리 사용률 (%)")
    disk_usage: float = Field(..., description="디스크 사용률 (%)")
    network_in: float = Field(..., description="네트워크 입력 (MB/s)")
    network_out: float = Field(..., description="네트워크 출력 (MB/s)")
    load_average: List[float] = Field(..., description="로드 평균")

class ApiMetrics(BaseModel):
    """API 메트릭"""
    avg_response_time: float = Field(..., description="평균 응답 시간 (ms)")
    requests_per_second: float = Field(..., description="초당 요청 수")
    error_rate: float = Field(..., description="오류율 (%)")
    active_connections: int = Field(..., description="활성 연결 수")
    total_requests: int = Field(..., description="총 요청 수")

class DatabaseMetrics(BaseModel):
    """데이터베이스 메트릭"""
    connection_count: int = Field(..., description="연결 수")
    active_queries: int = Field(..., description="활성 쿼리 수")
    avg_query_time: float = Field(..., description="평균 쿼리 시간 (ms)")
    cache_hit_ratio: float = Field(..., description="캐시 히트율 (%)")
    table_size: Dict[str, int] = Field(..., description="테이블별 크기")

class MemoryUsageMetrics(BaseModel):
    """메모리 사용량 메트릭"""
    total_memories: int = Field(..., description="총 메모리 수")
    recent_24h: int = Field(..., description="최근 24시간 메모리")
    by_type: Dict[str, int] = Field(..., description="타입별 메모리 분포")
    by_source: Dict[str, int] = Field(..., description="소스별 메모리 분포")
    by_importance: Dict[str, int] = Field(..., description="중요도별 메모리 분포")

class PerformanceMetrics(BaseModel):
    """성능 지표"""
    timestamp: datetime = Field(default_factory=datetime.now, description="타임스탬프")
    system: SystemMetrics = Field(..., description="시스템 메트릭")
    api: ApiMetrics = Field(..., description="API 메트릭")
    database: DatabaseMetrics = Field(..., description="데이터베이스 메트릭")
    memory: MemoryUsageMetrics = Field(..., description="메모리 사용량 메트릭")

class RealtimeData(BaseModel):
    """실시간 데이터"""
    timestamp: datetime = Field(default_factory=datetime.now, description="타임스탬프")
    system_status: str = Field(..., description="시스템 상태")
    active_services: int = Field(..., description="활성 서비스 수")
    memory_count: int = Field(..., description="현재 메모리 수")
    recent_activity: List[Dict[str, Any]] = Field(..., description="최근 활동")

class MemoryDashboard(BaseModel):
    """메모리 대시보드"""
    timestamp: datetime = Field(default_factory=datetime.now, description="타임스탬프")
    stats: Dict[str, Any] = Field(..., description="메모리 통계")
    recent_memories: List[Dict[str, Any]] = Field(..., description="최근 메모리들")
    by_type: Dict[str, int] = Field(..., description="타입별 분포")
    by_source: Dict[str, int] = Field(..., description="소스별 분포")
    by_importance: Dict[str, int] = Field(..., description="중요도별 분포")

class DashboardOverview(BaseModel):
    """대시보드 개요"""
    timestamp: datetime = Field(default_factory=datetime.now, description="타임스탬프")
    memory_stats: Dict[str, Any] = Field(..., description="메모리 통계")
    service_status: List[ServiceStatus] = Field(..., description="서비스 상태")
    performance_metrics: PerformanceMetrics = Field(..., description="성능 지표")
    realtime_data: RealtimeData = Field(..., description="실시간 데이터")

class DashboardConfig(BaseModel):
    """대시보드 설정"""
    auto_refresh_interval: int = Field(30, description="자동 새로고침 간격 (초)")
    chart_update_interval: int = Field(5, description="차트 업데이트 간격 (초)")
    max_data_points: int = Field(100, description="최대 데이터 포인트 수")
    enable_websocket: bool = Field(True, description="WebSocket 활성화")
    enable_notifications: bool = Field(True, description="알림 활성화")

class DashboardAlert(BaseModel):
    """대시보드 알림"""
    id: str = Field(..., description="알림 ID")
    type: str = Field(..., description="알림 타입 (warning, error, info)")
    message: str = Field(..., description="알림 메시지")
    timestamp: datetime = Field(default_factory=datetime.now, description="생성 시간")
    severity: str = Field(..., description="심각도 (low, medium, high, critical)")
    service: Optional[str] = Field(None, description="관련 서비스")
    resolved: bool = Field(False, description="해결 여부") 