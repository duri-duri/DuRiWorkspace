"""
DuRi 로그 분석 시스템

시스템 로그를 분석하고 통계를 수집합니다.
"""

import json
import logging
import re
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from collections import defaultdict, Counter

logger = logging.getLogger(__name__)

@dataclass
class LogEntry:
    """로그 엔트리"""
    timestamp: datetime
    level: str
    module: str
    message: str
    raw_line: str

@dataclass
class LogStatistics:
    """로그 통계"""
    total_entries: int
    error_count: int
    warning_count: int
    info_count: int
    debug_count: int
    module_distribution: Dict[str, int]
    error_patterns: Dict[str, int]
    time_distribution: Dict[str, int]

class LogAnalyzer:
    """DuRi 로그 분석 시스템"""
    
    def __init__(self, log_dir: str = "logs"):
        """LogAnalyzer 초기화"""
        self.log_dir = Path(log_dir)
        self.log_entries: List[LogEntry] = []
        self.analysis_cache: Dict[str, Any] = {}
        
        logger.info("LogAnalyzer 초기화 완료")
    
    def load_logs(self, hours: int = 24) -> int:
        """
        로그를 로드합니다.
        
        Args:
            hours: 로드할 시간 범위 (시간)
            
        Returns:
            int: 로드된 로그 엔트리 수
        """
        try:
            cutoff_time = datetime.now() - timedelta(hours=hours)
            loaded_count = 0
            
            # 로그 디렉토리 탐색
            for log_file in self.log_dir.rglob("*.log"):
                loaded_count += self._load_log_file(log_file, cutoff_time)
            
            # JSONL 파일 탐색
            for jsonl_file in self.log_dir.rglob("*.jsonl"):
                loaded_count += self._load_jsonl_file(jsonl_file, cutoff_time)
            
            logger.info(f"로그 로드 완료: {loaded_count}개 엔트리")
            return loaded_count
            
        except Exception as e:
            logger.error(f"로그 로드 실패: {e}")
            return 0
    
    def _load_log_file(self, log_file: Path, cutoff_time: datetime) -> int:
        """로그 파일을 로드합니다."""
        loaded_count = 0
        
        try:
            with open(log_file, 'r', encoding='utf-8') as f:
                for line in f:
                    entry = self._parse_log_line(line.strip())
                    if entry and entry.timestamp >= cutoff_time:
                        self.log_entries.append(entry)
                        loaded_count += 1
        except Exception as e:
            logger.error(f"로그 파일 로드 실패 {log_file}: {e}")
        
        return loaded_count
    
    def _load_jsonl_file(self, jsonl_file: Path, cutoff_time: datetime) -> int:
        """JSONL 파일을 로드합니다."""
        loaded_count = 0
        
        try:
            with open(jsonl_file, 'r', encoding='utf-8') as f:
                for line in f:
                    try:
                        data = json.loads(line.strip())
                        entry = self._parse_jsonl_entry(data)
                        if entry and entry.timestamp >= cutoff_time:
                            self.log_entries.append(entry)
                            loaded_count += 1
                    except json.JSONDecodeError:
                        continue
        except Exception as e:
            logger.error(f"JSONL 파일 로드 실패 {jsonl_file}: {e}")
        
        return loaded_count
    
    def _parse_log_line(self, line: str) -> Optional[LogEntry]:
        """로그 라인을 파싱합니다."""
        try:
            # 일반적인 로그 패턴 매칭
            pattern = r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3}) - (\w+) - ([^:]+): (.+)'
            match = re.match(pattern, line)
            
            if match:
                timestamp_str, level, module, message = match.groups()
                timestamp = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S,%f')
                
                return LogEntry(
                    timestamp=timestamp,
                    level=level.lower(),
                    module=module.strip(),
                    message=message.strip(),
                    raw_line=line
                )
            
            return None
            
        except Exception as e:
            logger.debug(f"로그 라인 파싱 실패: {line[:100]}... - {e}")
            return None
    
    def _parse_jsonl_entry(self, data: Dict[str, Any]) -> Optional[LogEntry]:
        """JSONL 엔트리를 파싱합니다."""
        try:
            timestamp_str = data.get('timestamp', '')
            if timestamp_str:
                timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
            else:
                timestamp = datetime.now()
            
            return LogEntry(
                timestamp=timestamp,
                level=data.get('level', 'info').lower(),
                module=data.get('module', 'unknown'),
                message=data.get('message', ''),
                raw_line=json.dumps(data)
            )
            
        except Exception as e:
            logger.debug(f"JSONL 엔트리 파싱 실패: {e}")
            return None
    
    def analyze_logs(self) -> LogStatistics:
        """로그를 분석합니다."""
        if not self.log_entries:
            return LogStatistics(
                total_entries=0,
                error_count=0,
                warning_count=0,
                info_count=0,
                debug_count=0,
                module_distribution={},
                error_patterns={},
                time_distribution={}
            )
        
        # 기본 통계
        total_entries = len(self.log_entries)
        error_count = len([e for e in self.log_entries if e.level == 'error'])
        warning_count = len([e for e in self.log_entries if e.level == 'warning'])
        info_count = len([e for e in self.log_entries if e.level == 'info'])
        debug_count = len([e for e in self.log_entries if e.level == 'debug'])
        
        # 모듈별 분포
        module_counter = Counter([e.module for e in self.log_entries])
        module_distribution = dict(module_counter)
        
        # 오류 패턴 분석
        error_patterns = self._analyze_error_patterns()
        
        # 시간별 분포
        time_distribution = self._analyze_time_distribution()
        
        return LogStatistics(
            total_entries=total_entries,
            error_count=error_count,
            warning_count=warning_count,
            info_count=info_count,
            debug_count=debug_count,
            module_distribution=module_distribution,
            error_patterns=error_patterns,
            time_distribution=time_distribution
        )
    
    def _analyze_error_patterns(self) -> Dict[str, int]:
        """오류 패턴을 분석합니다."""
        error_entries = [e for e in self.log_entries if e.level == 'error']
        patterns = Counter()
        
        for entry in error_entries:
            # 일반적인 오류 패턴 추출
            message = entry.message.lower()
            
            if 'timeout' in message:
                patterns['timeout'] += 1
            elif 'connection' in message:
                patterns['connection_error'] += 1
            elif 'memory' in message:
                patterns['memory_error'] += 1
            elif 'permission' in message:
                patterns['permission_error'] += 1
            elif 'not found' in message:
                patterns['not_found'] += 1
            elif 'invalid' in message:
                patterns['invalid_data'] += 1
            else:
                patterns['other_error'] += 1
        
        return dict(patterns)
    
    def _analyze_time_distribution(self) -> Dict[str, int]:
        """시간별 분포를 분석합니다."""
        hour_distribution = Counter()
        
        for entry in self.log_entries:
            hour = entry.timestamp.strftime('%H')
            hour_distribution[hour] += 1
        
        return dict(hour_distribution)
    
    def get_recent_errors(self, limit: int = 10) -> List[LogEntry]:
        """최근 오류를 반환합니다."""
        error_entries = [e for e in self.log_entries if e.level == 'error']
        return sorted(error_entries, key=lambda x: x.timestamp, reverse=True)[:limit]
    
    def get_module_statistics(self, module_name: str) -> Dict[str, Any]:
        """특정 모듈의 통계를 반환합니다."""
        module_entries = [e for e in self.log_entries if e.module == module_name]
        
        if not module_entries:
            return {"error": f"모듈 {module_name}의 로그가 없습니다."}
        
        # 레벨별 분포
        level_distribution = Counter([e.level for e in module_entries])
        
        # 시간별 분포
        time_distribution = Counter([e.timestamp.strftime('%H') for e in module_entries])
        
        return {
            "module_name": module_name,
            "total_entries": len(module_entries),
            "level_distribution": dict(level_distribution),
            "time_distribution": dict(time_distribution),
            "recent_entries": [
                {
                    "timestamp": e.timestamp.isoformat(),
                    "level": e.level,
                    "message": e.message
                }
                for e in sorted(module_entries, key=lambda x: x.timestamp, reverse=True)[:5]
            ]
        }
    
    def clear_cache(self):
        """캐시를 정리합니다."""
        self.log_entries.clear()
        self.analysis_cache.clear()
        logger.info("로그 분석 캐시 정리 완료")

# 싱글톤 인스턴스
_log_analyzer = None

def get_log_analyzer() -> LogAnalyzer:
    """LogAnalyzer 싱글톤 인스턴스 반환"""
    global _log_analyzer
    if _log_analyzer is None:
        _log_analyzer = LogAnalyzer()
    return _log_analyzer 