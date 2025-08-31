import re
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
from collections import defaultdict, Counter

from ..models.log_entry import LogEntry, LogQueryParams
from ..services.log_service import log_service
from duri_common.logger import get_logger

logger = get_logger("duri_control.log_query_service")


class LogQueryService:
    """고급 로그 검색 및 필터링 서비스"""
    
    def __init__(self):
        self.log_service = log_service
    
    def search_logs(
        self,
        query: Optional[str] = None,
        level: Optional[str] = None,
        service: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        limit: int = 100,
        offset: int = 0
    ) -> Tuple[List[LogEntry], int]:
        """
        고급 로그 검색 및 필터링
        
        Args:
            query: 키워드 검색 (메시지 내용에서 검색)
            level: 로그 레벨 필터 (DEBUG, INFO, WARNING, ERROR)
            service: 서비스명 필터
            start_time: 시작 시간
            end_time: 종료 시간
            limit: 결과 제한
            offset: 오프셋
            
        Returns:
            (필터링된 로그 목록, 총 개수)
        """
        try:
            # 모든 로그 가져오기
            all_logs = self.log_service.get_recent_logs(
                LogQueryParams(limit=10000)  # 충분히 큰 수로 모든 로그 가져오기
            )
            
            filtered_logs = []
            
            for log in all_logs:
                # 레벨 필터
                if level and log.level.upper() != level.upper():
                    continue
                
                # 서비스 필터
                if service and log.service_name != service:
                    continue
                
                # 시간 범위 필터
                if start_time and log.timestamp < start_time:
                    continue
                if end_time and log.timestamp > end_time:
                    continue
                
                # 키워드 검색
                if query:
                    if not self._matches_query(log, query):
                        continue
                
                filtered_logs.append(log)
            
            # 시간순 정렬 (최신순)
            filtered_logs.sort(key=lambda x: x.timestamp, reverse=True)
            
            # 페이지네이션
            total_count = len(filtered_logs)
            paginated_logs = filtered_logs[offset:offset + limit]
            
            logger.info(f"로그 검색 완료: {len(paginated_logs)}개 결과 (총 {total_count}개)")
            return paginated_logs, total_count
            
        except Exception as e:
            logger.error(f"로그 검색 중 오류 발생: {e}")
            return [], 0
    
    def _matches_query(self, log: LogEntry, query: str) -> bool:
        """키워드 검색 매칭"""
        try:
            # 대소문자 구분 없이 검색
            query_lower = query.lower()
            
            # 메시지에서 검색
            if query_lower in log.message.lower():
                return True
            
            # 서비스명에서 검색
            if query_lower in log.service_name.lower():
                return True
            
            # 컨테이너 ID에서 검색
            if log.container_id and query_lower in log.container_id.lower():
                return True
            
            # 정규식 검색 (고급 사용자를 위해)
            if query.startswith('/') and query.endswith('/'):
                try:
                    pattern = query[1:-1]  # 슬래시 제거
                    if re.search(pattern, log.message, re.IGNORECASE):
                        return True
                except re.error:
                    # 잘못된 정규식은 무시
                    pass
            
            return False
            
        except Exception as e:
            logger.debug(f"쿼리 매칭 중 오류: {e}")
            return False
    
    def get_advanced_statistics(self) -> Dict:
        """고급 로그 통계"""
        try:
            all_logs = self.log_service.get_recent_logs(
                LogQueryParams(limit=10000)
            )
            
            stats = {
                "total_logs": len(all_logs),
                "services": {},
                "levels": {},
                "hourly_distribution": defaultdict(int),
                "daily_distribution": defaultdict(int),
                "error_analysis": {
                    "total_errors": 0,
                    "error_services": defaultdict(int),
                    "error_patterns": Counter(),
                    "recent_errors": []
                },
                "performance_metrics": {
                    "avg_logs_per_minute": 0,
                    "peak_hour": None,
                    "quiet_hour": None
                }
            }
            
            if not all_logs:
                return stats
            
            # 기본 통계
            for log in all_logs:
                # 서비스별 통계
                if log.service_name not in stats["services"]:
                    stats["services"][log.service_name] = {
                        "total": 0,
                        "levels": defaultdict(int),
                        "recent_logs": []
                    }
                stats["services"][log.service_name]["total"] += 1
                stats["services"][log.service_name]["levels"][log.level] += 1
                
                # 레벨별 통계
                if log.level not in stats["levels"]:
                    stats["levels"][log.level] = 0
                stats["levels"][log.level] += 1
                
                # 시간별 분포
                hour_key = log.timestamp.strftime("%Y-%m-%d %H:00")
                stats["hourly_distribution"][hour_key] += 1
                
                # 일별 분포
                day_key = log.timestamp.strftime("%Y-%m-%d")
                stats["daily_distribution"][day_key] += 1
                
                # 에러 분석
                if log.level.upper() == "ERROR":
                    stats["error_analysis"]["total_errors"] += 1
                    stats["error_analysis"]["error_services"][log.service_name] += 1
                    
                    # 에러 패턴 분석 (첫 50자)
                    error_pattern = log.message[:50].strip()
                    stats["error_analysis"]["error_patterns"][error_pattern] += 1
                    
                    # 최근 에러 (최대 10개)
                    if len(stats["error_analysis"]["recent_errors"]) < 10:
                        stats["error_analysis"]["recent_errors"].append({
                            "timestamp": log.timestamp.isoformat(),
                            "service": log.service_name,
                            "message": log.message[:100] + "..." if len(log.message) > 100 else log.message
                        })
            
            # 성능 메트릭 계산
            if all_logs:
                # 시간 범위 계산
                timestamps = [log.timestamp for log in all_logs]
                min_time = min(timestamps)
                max_time = max(timestamps)
                time_span = max_time - min_time
                
                if time_span.total_seconds() > 0:
                    stats["performance_metrics"]["avg_logs_per_minute"] = len(all_logs) / (time_span.total_seconds() / 60)
                
                # 피크 시간 찾기
                if stats["hourly_distribution"]:
                    peak_hour = max(stats["hourly_distribution"].items(), key=lambda x: x[1])
                    quiet_hour = min(stats["hourly_distribution"].items(), key=lambda x: x[1])
                    
                    stats["performance_metrics"]["peak_hour"] = {
                        "hour": peak_hour[0],
                        "count": peak_hour[1]
                    }
                    stats["performance_metrics"]["quiet_hour"] = {
                        "hour": quiet_hour[0],
                        "count": quiet_hour[1]
                    }
            
            # 서비스별 최근 로그 추가
            for service_name in stats["services"]:
                service_logs = [log for log in all_logs if log.service_name == service_name]
                service_logs.sort(key=lambda x: x.timestamp, reverse=True)
                stats["services"][service_name]["recent_logs"] = [
                    {
                        "timestamp": log.timestamp.isoformat(),
                        "level": log.level,
                        "message": log.message[:100] + "..." if len(log.message) > 100 else log.message
                    }
                    for log in service_logs[:5]  # 최근 5개
                ]
            
            return stats
            
        except Exception as e:
            logger.error(f"고급 통계 생성 중 오류: {e}")
            return {}
    
    def get_error_summary(self, hours: int = 24) -> Dict:
        """에러 요약 정보"""
        try:
            cutoff_time = datetime.now() - timedelta(hours=hours)
            
            all_logs = self.log_service.get_recent_logs(
                LogQueryParams(limit=10000)
            )
            
            recent_errors = [
                log for log in all_logs 
                if log.level.upper() == "ERROR" and log.timestamp >= cutoff_time
            ]
            
            error_summary = {
                "period_hours": hours,
                "total_errors": len(recent_errors),
                "error_rate_per_hour": len(recent_errors) / hours if hours > 0 else 0,
                "services_with_errors": list(set(log.service_name for log in recent_errors)),
                "error_timeline": defaultdict(int),
                "critical_errors": []
            }
            
            # 에러 타임라인
            for error in recent_errors:
                hour_key = error.timestamp.strftime("%Y-%m-%d %H:00")
                error_summary["error_timeline"][hour_key] += 1
            
            # 중요 에러 식별 (패턴 기반)
            error_patterns = Counter()
            for error in recent_errors:
                # 에러 메시지에서 키워드 추출
                message_lower = error.message.lower()
                if any(keyword in message_lower for keyword in ["timeout", "connection", "failed", "exception"]):
                    error_patterns["connection/timeout"] += 1
                elif any(keyword in message_lower for keyword in ["memory", "out of memory"]):
                    error_patterns["memory"] += 1
                elif any(keyword in message_lower for keyword in ["permission", "access denied"]):
                    error_patterns["permission"] += 1
                else:
                    error_patterns["other"] += 1
            
            error_summary["error_patterns"] = dict(error_patterns)
            
            return error_summary
            
        except Exception as e:
            logger.error(f"에러 요약 생성 중 오류: {e}")
            return {}
    
    def get_service_health_report(self) -> Dict:
        """서비스별 건강도 리포트"""
        try:
            all_logs = self.log_service.get_recent_logs(
                LogQueryParams(limit=10000)
            )
            
            # 최근 1시간 로그
            one_hour_ago = datetime.now() - timedelta(hours=1)
            recent_logs = [log for log in all_logs if log.timestamp >= one_hour_ago]
            
            health_report = {}
            
            for service_name in set(log.service_name for log in all_logs):
                service_logs = [log for log in recent_logs if log.service_name == service_name]
                service_all_logs = [log for log in all_logs if log.service_name == service_name]
                
                if not service_logs:
                    health_report[service_name] = {
                        "status": "unknown",
                        "recent_activity": False,
                        "error_count": 0,
                        "warning_count": 0,
                        "last_log": None,
                        "health_score": 0
                    }
                    continue
                
                # 에러 및 경고 수
                error_count = len([log for log in service_logs if log.level.upper() == "ERROR"])
                warning_count = len([log for log in service_logs if log.level.upper() == "WARNING"])
                
                # 마지막 로그 시간
                last_log = max(service_logs, key=lambda x: x.timestamp)
                
                # 건강도 점수 계산 (0-100)
                total_recent = len(service_logs)
                if total_recent == 0:
                    health_score = 0
                else:
                    error_rate = error_count / total_recent
                    warning_rate = warning_count / total_recent
                    
                    # 기본 점수 100에서 에러/경고 비율에 따라 감점
                    health_score = max(0, 100 - (error_rate * 50) - (warning_rate * 20))
                
                # 상태 결정
                if health_score >= 80:
                    status = "healthy"
                elif health_score >= 60:
                    status = "warning"
                elif health_score >= 40:
                    status = "critical"
                else:
                    status = "down"
                
                health_report[service_name] = {
                    "status": status,
                    "recent_activity": True,
                    "error_count": error_count,
                    "warning_count": warning_count,
                    "last_log": last_log.timestamp.isoformat(),
                    "health_score": round(health_score, 1),
                    "total_logs_1h": len(service_logs),
                    "total_logs_all": len(service_all_logs)
                }
            
            return health_report
            
        except Exception as e:
            logger.error(f"서비스 건강도 리포트 생성 중 오류: {e}")
            return {}


# 전역 인스턴스
log_query_service = LogQueryService() 