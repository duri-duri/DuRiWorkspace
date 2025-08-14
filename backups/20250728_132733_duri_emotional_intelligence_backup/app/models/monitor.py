from pydantic import BaseModel
from typing import Dict, List, Optional
from datetime import datetime
from enum import Enum

class ServiceStatus(str, Enum):
    HEALTHY = "healthy"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"

class ServiceInfo(BaseModel):
    status: ServiceStatus
    port: int
    response_time: Optional[float] = None
    last_check: datetime
    error_message: Optional[str] = None

class SystemSummary(BaseModel):
    total_services: int
    healthy_services: int
    unhealthy_services: int
    unknown_services: int
    overall_status: ServiceStatus
    last_updated: datetime

class ServicesResponse(BaseModel):
    status: str = "success"
    services: Dict[str, ServiceInfo]
    timestamp: datetime

class SummaryResponse(BaseModel):
    status: str = "success"
    summary: SystemSummary
    timestamp: datetime

# 리소스 모니터링 모델
class CpuInfo(BaseModel):
    usage_percent: float
    cores: int
    frequency_mhz: Optional[float] = None
    temperature: Optional[float] = None

class MemoryInfo(BaseModel):
    total_gb: float
    used_gb: float
    available_gb: float
    usage_percent: float
    swap_total_gb: Optional[float] = None
    swap_used_gb: Optional[float] = None

class DiskInfo(BaseModel):
    total_gb: float
    used_gb: float
    free_gb: float
    usage_percent: float
    mount_point: str

class NetworkInfo(BaseModel):
    bytes_sent: int
    bytes_recv: int
    packets_sent: int
    packets_recv: int
    interface: str

class SystemResources(BaseModel):
    cpu: CpuInfo
    memory: MemoryInfo
    disks: List[DiskInfo]
    network: NetworkInfo
    timestamp: datetime

class ContainerResourceInfo(BaseModel):
    container_id: str
    container_name: str
    cpu_percent: float
    memory_usage_mb: float
    memory_limit_mb: Optional[float] = None
    memory_percent: Optional[float] = None
    network_rx_mb: Optional[float] = None
    network_tx_mb: Optional[float] = None
    status: str
    timestamp: datetime

class ResourcesResponse(BaseModel):
    status: str = "success"
    resources: SystemResources
    timestamp: datetime

class ContainersResponse(BaseModel):
    status: str = "success"
    containers: List[ContainerResourceInfo]
    timestamp: datetime 