import psutil
import subprocess
import json
from typing import List, Dict, Optional, Tuple
from datetime import datetime
from ..models.monitor import CpuInfo, MemoryInfo, DiskInfo, NetworkInfo, ContainerResourceInfo
from duri_common.logger import get_logger

logger = get_logger("duri_control.resource_utils")

class ResourceUtils:
    """리소스 모니터링 유틸리티 클래스"""
    
    @staticmethod
    def check_docker_available() -> bool:
        """Docker CLI 사용 가능 여부 확인"""
        try:
            result = subprocess.run(
                ["docker", "--version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            return result.returncode == 0
        except Exception:
            return False
    
    @staticmethod
    def get_cpu_info() -> CpuInfo:
        """CPU 정보 수집"""
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            cpu_count = psutil.cpu_count()
            cpu_freq = psutil.cpu_freq()
            
            return CpuInfo(
                usage_percent=cpu_percent,
                cores=cpu_count,
                frequency_mhz=cpu_freq.current if cpu_freq else None,
                temperature=None  # 온도 정보는 별도 라이브러리 필요
            )
        except Exception as e:
            logger.error(f"CPU 정보 수집 실패: {e}")
            return CpuInfo(usage_percent=0.0, cores=0)
    
    @staticmethod
    def get_memory_info() -> MemoryInfo:
        """메모리 정보 수집"""
        try:
            memory = psutil.virtual_memory()
            swap = psutil.swap_memory()
            
            return MemoryInfo(
                total_gb=memory.total / (1024**3),
                used_gb=memory.used / (1024**3),
                available_gb=memory.available / (1024**3),
                usage_percent=memory.percent,
                swap_total_gb=swap.total / (1024**3) if swap.total > 0 else None,
                swap_used_gb=swap.used / (1024**3) if swap.used > 0 else None
            )
        except Exception as e:
            logger.error(f"메모리 정보 수집 실패: {e}")
            return MemoryInfo(total_gb=0.0, used_gb=0.0, available_gb=0.0, usage_percent=0.0)
    
    @staticmethod
    def get_disk_info() -> List[DiskInfo]:
        """디스크 정보 수집"""
        try:
            disks = []
            for partition in psutil.disk_partitions():
                try:
                    usage = psutil.disk_usage(partition.mountpoint)
                    disks.append(DiskInfo(
                        total_gb=usage.total / (1024**3),
                        used_gb=usage.used / (1024**3),
                        free_gb=usage.free / (1024**3),
                        usage_percent=(usage.used / usage.total) * 100,
                        mount_point=partition.mountpoint
                    ))
                except PermissionError:
                    continue  # 권한이 없는 마운트 포인트는 건너뛰기
            return disks
        except Exception as e:
            logger.error(f"디스크 정보 수집 실패: {e}")
            return []
    
    @staticmethod
    def get_network_info() -> NetworkInfo:
        """네트워크 정보 수집"""
        try:
            # 기본 네트워크 인터페이스 찾기
            net_io = psutil.net_io_counters()
            interfaces = psutil.net_if_addrs()
            
            # 기본 인터페이스 (eth0 또는 첫 번째 인터페이스)
            default_interface = "eth0"
            if default_interface not in interfaces and interfaces:
                default_interface = list(interfaces.keys())[0]
            
            return NetworkInfo(
                bytes_sent=net_io.bytes_sent,
                bytes_recv=net_io.bytes_recv,
                packets_sent=net_io.packets_sent,
                packets_recv=net_io.packets_recv,
                interface=default_interface
            )
        except Exception as e:
            logger.error(f"네트워크 정보 수집 실패: {e}")
            return NetworkInfo(
                bytes_sent=0, bytes_recv=0, packets_sent=0, packets_recv=0, interface="unknown"
            )
    
    @staticmethod
    def get_container_stats() -> List[ContainerResourceInfo]:
        """Docker 컨테이너 리소스 정보 수집"""
        if not ResourceUtils.check_docker_available():
            logger.warning("Docker CLI를 사용할 수 없습니다. 컨테이너 정보를 수집할 수 없습니다.")
            return []
        
        try:
            # 실행 중인 컨테이너 목록 조회
            result = subprocess.run(
                ["docker", "ps", "--format", "{{.ID}}\t{{.Names}}\t{{.Status}}"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode != 0:
                logger.error(f"Docker 컨테이너 목록 조회 실패: {result.stderr}")
                return []
            
            containers = []
            container_names = []
            
            # 컨테이너 목록 파싱
            for line in result.stdout.strip().split('\n'):
                if not line.strip():
                    continue
                    
                parts = line.split('\t')
                if len(parts) >= 3:
                    container_id = parts[0]
                    container_name = parts[1]
                    status = parts[2]
                    container_names.append(container_name)
                    
                    # 기본값으로 컨테이너 정보 생성
                    containers.append(ContainerResourceInfo(
                        container_id=container_id,
                        container_name=container_name,
                        cpu_percent=0.0,
                        memory_usage_mb=0.0,
                        memory_limit_mb=None,
                        memory_percent=None,
                        network_rx_mb=None,
                        network_tx_mb=None,
                        status=status,
                        timestamp=datetime.now()
                    ))
            
            # 전체 컨테이너 통계 조회
            stats_result = subprocess.run(
                ["docker", "stats", "--no-stream", "--format", "table {{.Container}} {{.CPUPerc}} {{.MemUsage}} {{.MemPerc}} {{.NetIO}} {{.BlockIO}}"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if stats_result.returncode == 0 and stats_result.stdout.strip():
                try:
                    lines = stats_result.stdout.strip().split('\n')
                    logger.debug(f"Docker stats output lines: {len(lines)}")
                    logger.debug(f"First line: {lines[0] if lines else 'None'}")
                    
                    if len(lines) >= 2:  # 헤더 + 데이터
                        for i, stat_line in enumerate(lines[1:]):  # 헤더 제외
                            logger.debug(f"Processing line {i+1}: {stat_line}")
                            if stat_line.strip():
                                # 공백으로 분리된 데이터 파싱 (연속된 공백을 하나로 처리)
                                parts = stat_line.split()
                                logger.debug(f"Parts count: {len(parts)}, Parts: {parts}")
                                
                                if len(parts) >= 6:
                                    container_id = parts[0].strip()
                                    logger.debug(f"Looking for container ID: {container_id}")
                                    
                                    # 해당 컨테이너 찾기
                                    for container in containers:
                                        # 짧은 ID나 전체 ID로 매칭
                                        if (container.container_id == container_id or 
                                            container.container_id.startswith(container_id) or
                                            container_id.startswith(container.container_id) or
                                            container.container_name in container_id):
                                            
                                            logger.debug(f"Found matching container: {container.container_name}")
                                            
                                            # CPU 사용률 파싱
                                            if parts[1] and parts[1] != '--':
                                                cpu_str = parts[1].replace('%', '').strip()
                                                try:
                                                    container.cpu_percent = float(cpu_str)
                                                    logger.debug(f"CPU parsed: {cpu_str} -> {container.cpu_percent}")
                                                except ValueError as e:
                                                    logger.debug(f"CPU parsing failed: {cpu_str}, error: {e}")
                                                    pass
                                            
                                            # 메모리 사용량 파싱 (parts[2]와 parts[3]을 결합)
                                            if len(parts) >= 4 and parts[2] and parts[2] != '--':
                                                mem_str = f"{parts[2]} {parts[3]}"  # "26.62MiB / 15.53GiB"
                                                logger.debug(f"Memory string: {mem_str}")
                                                if '/' in mem_str:
                                                    used_str, limit_str = mem_str.split('/')
                                                    try:
                                                        # MiB 단위로 변환
                                                        if 'MiB' in used_str:
                                                            container.memory_usage_mb = float(used_str.replace('MiB', ''))
                                                        elif 'GiB' in used_str:
                                                            container.memory_usage_mb = float(used_str.replace('GiB', '')) * 1024
                                                        
                                                        if 'MiB' in limit_str:
                                                            container.memory_limit_mb = float(limit_str.replace('MiB', ''))
                                                        elif 'GiB' in limit_str:
                                                            container.memory_limit_mb = float(limit_str.replace('GiB', '')) * 1024
                                                        
                                                        logger.debug(f"Memory parsed: {used_str} -> {container.memory_usage_mb}MB")
                                                    except ValueError as e:
                                                        logger.debug(f"Memory parsing failed: {mem_str}, error: {e}")
                                                        pass
                                            
                                            # 메모리 사용률 파싱
                                            if len(parts) >= 5 and parts[4] and parts[4] != '--':
                                                mem_percent_str = parts[4].replace('%', '').strip()
                                                try:
                                                    container.memory_percent = float(mem_percent_str)
                                                    logger.debug(f"Memory percent parsed: {mem_percent_str} -> {container.memory_percent}")
                                                except ValueError as e:
                                                    logger.debug(f"Memory percent parsing failed: {mem_percent_str}, error: {e}")
                                                    pass
                                            
                                            # 네트워크 정보 파싱 (parts[5]와 parts[6]을 결합)
                                            if len(parts) >= 7 and parts[5] and parts[5] != '--':
                                                net_str = f"{parts[5]} {parts[6]}"  # "3.11kB / 1.57kB"
                                                logger.debug(f"Network string: {net_str}")
                                                if '/' in net_str:
                                                    rx_str, tx_str = net_str.split('/')
                                                    try:
                                                        if 'MB' in rx_str:
                                                            container.network_rx_mb = float(rx_str.replace('MB', ''))
                                                        if 'MB' in tx_str:
                                                            container.network_tx_mb = float(tx_str.replace('MB', ''))
                                                        logger.debug(f"Network parsed: RX={container.network_rx_mb}, TX={container.network_tx_mb}")
                                                    except ValueError as e:
                                                        logger.debug(f"Network parsing failed: {net_str}, error: {e}")
                                                        pass
                                            
                                            logger.debug(f"컨테이너 {container.container_name} 정보 업데이트 완료")
                                            break
                                    else:
                                        logger.debug(f"No matching container found for ID: {container_id}")
                            
                except Exception as e:
                    logger.warning(f"컨테이너 통계 파싱 실패: {e}")
                    import traceback
                    logger.debug(f"Traceback: {traceback.format_exc()}")
            
            logger.info(f"총 {len(containers)}개 컨테이너 정보 수집 완료")
            return containers
            
        except Exception as e:
            logger.error(f"컨테이너 통계 수집 실패: {e}")
            return [] 