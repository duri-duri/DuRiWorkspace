import re
import logging
from typing import Dict, Any, List, Tuple, Optional
from enum import Enum

logger = logging.getLogger(__name__)


class LogLevel(Enum):
    """로그 레벨 정의"""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class ValidationError(Exception):
    """검증 오류"""
    pass


class ConfigValidator:
    """설정 검증기"""
    
    def __init__(self):
        self.validators = {
            'log_level': self._validate_log_level,
            'max_threads': self._validate_max_threads,
            'timeout': self._validate_timeout,
            'retry_count': self._validate_retry_count,
            'port': self._validate_port,
            'host': self._validate_host,
            'debug': self._validate_debug,
            'db_host': self._validate_db_host,
            'db_port': self._validate_db_port,
            'db_name': self._validate_db_name,
            'db_user': self._validate_db_user,
            'redis_host': self._validate_redis_host,
            'redis_port': self._validate_redis_port
        }
    
    def validate_config(self, service_name: str, config_data: Dict[str, Any]) -> Tuple[bool, List[str], List[str]]:
        """설정 전체 검증"""
        errors = []
        warnings = []
        
        try:
            # 기본 필드 검증
            for field, value in config_data.items():
                if field in self.validators:
                    field_errors, field_warnings = self.validators[field](value)
                    errors.extend(field_errors)
                    warnings.extend(field_warnings)
            
            # 서비스별 특화 검증
            service_errors, service_warnings = self._validate_service_specific(service_name, config_data)
            errors.extend(service_errors)
            warnings.extend(service_warnings)
            
            # 의존성 검증
            dependency_errors, dependency_warnings = self._validate_dependencies(service_name, config_data)
            errors.extend(dependency_errors)
            warnings.extend(dependency_warnings)
            
            # 비즈니스 로직 검증
            business_errors, business_warnings = self._validate_business_logic(service_name, config_data)
            errors.extend(business_errors)
            warnings.extend(business_warnings)
            
        except Exception as e:
            errors.append(f"검증 중 오류 발생: {str(e)}")
            logger.error(f"설정 검증 중 예외 발생: {e}")
        
        return len(errors) == 0, errors, warnings
    
    def _validate_log_level(self, value: Any) -> Tuple[List[str], List[str]]:
        """로그 레벨 검증"""
        errors = []
        warnings = []
        
        if not isinstance(value, str):
            errors.append("로그 레벨은 문자열이어야 합니다")
            return errors, warnings
        
        try:
            LogLevel(value.upper())
        except ValueError:
            valid_levels = [level.value for level in LogLevel]
            errors.append(f"유효하지 않은 로그 레벨: {value}. 유효한 값: {', '.join(valid_levels)}")
        
        return errors, warnings
    
    def _validate_max_threads(self, value: Any) -> Tuple[List[str], List[str]]:
        """최대 스레드 수 검증"""
        errors = []
        warnings = []
        
        if not isinstance(value, int):
            errors.append("max_threads는 정수여야 합니다")
            return errors, warnings
        
        if value <= 0:
            errors.append("max_threads는 0보다 커야 합니다")
        elif value > 100:
            warnings.append("max_threads가 100을 초과합니다. 성능에 영향을 줄 수 있습니다")
        elif value > 50:
            warnings.append("max_threads가 50을 초과합니다. 시스템 리소스를 많이 사용할 수 있습니다")
        
        return errors, warnings
    
    def _validate_timeout(self, value: Any) -> Tuple[List[str], List[str]]:
        """타임아웃 검증"""
        errors = []
        warnings = []
        
        if not isinstance(value, (int, float)):
            errors.append("timeout은 숫자여야 합니다")
            return errors, warnings
        
        if value <= 0:
            errors.append("timeout은 0보다 커야 합니다")
        elif value > 3600:
            warnings.append("timeout이 1시간을 초과합니다")
        elif value < 1:
            warnings.append("timeout이 1초 미만입니다. 네트워크 지연으로 인한 문제가 발생할 수 있습니다")
        
        return errors, warnings
    
    def _validate_retry_count(self, value: Any) -> Tuple[List[str], List[str]]:
        """재시도 횟수 검증"""
        errors = []
        warnings = []
        
        if not isinstance(value, int):
            errors.append("retry_count는 정수여야 합니다")
            return errors, warnings
        
        if value < 0:
            errors.append("retry_count는 0 이상이어야 합니다")
        elif value > 10:
            warnings.append("retry_count가 10을 초과합니다. 과도한 재시도로 인한 문제가 발생할 수 있습니다")
        
        return errors, warnings
    
    def _validate_port(self, value: Any) -> Tuple[List[str], List[str]]:
        """포트 번호 검증"""
        errors = []
        warnings = []
        
        if not isinstance(value, int):
            errors.append("port는 정수여야 합니다")
            return errors, warnings
        
        if value < 1 or value > 65535:
            errors.append("port는 1-65535 범위여야 합니다")
        elif value < 1024:
            warnings.append("포트 번호가 1024 미만입니다. 관리자 권한이 필요할 수 있습니다")
        
        return errors, warnings
    
    def _validate_host(self, value: Any) -> Tuple[List[str], List[str]]:
        """호스트 검증"""
        errors = []
        warnings = []
        
        if not isinstance(value, str):
            errors.append("host는 문자열이어야 합니다")
            return errors, warnings
        
        if value not in ['0.0.0.0', 'localhost', '127.0.0.1']:
            # IP 주소 형식 검증
            ip_pattern = r'^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$'
            if not re.match(ip_pattern, value):
                warnings.append(f"호스트 주소 형식이 표준이 아닙니다: {value}")
        
        return errors, warnings
    
    def _validate_debug(self, value: Any) -> Tuple[List[str], List[str]]:
        """디버그 모드 검증"""
        errors = []
        warnings = []
        
        if not isinstance(value, bool):
            errors.append("debug는 불린 값이어야 합니다")
            return errors, warnings
        
        if value:
            warnings.append("디버그 모드가 활성화되어 있습니다. 프로덕션 환경에서는 비활성화하는 것을 권장합니다")
        
        return errors, warnings
    
    def _validate_db_host(self, value: Any) -> Tuple[List[str], List[str]]:
        """데이터베이스 호스트 검증"""
        errors = []
        warnings = []
        
        if not isinstance(value, str):
            errors.append("db_host는 문자열이어야 합니다")
            return errors, warnings
        
        if not value:
            errors.append("db_host는 비어있을 수 없습니다")
        
        return errors, warnings
    
    def _validate_db_port(self, value: Any) -> Tuple[List[str], List[str]]:
        """데이터베이스 포트 검증"""
        errors = []
        warnings = []
        
        if not isinstance(value, int):
            errors.append("db_port는 정수여야 합니다")
            return errors, warnings
        
        if value < 1 or value > 65535:
            errors.append("db_port는 1-65535 범위여야 합니다")
        elif value != 5432:
            warnings.append("PostgreSQL 기본 포트(5432)가 아닙니다")
        
        return errors, warnings
    
    def _validate_db_name(self, value: Any) -> Tuple[List[str], List[str]]:
        """데이터베이스 이름 검증"""
        errors = []
        warnings = []
        
        if not isinstance(value, str):
            errors.append("db_name은 문자열이어야 합니다")
            return errors, warnings
        
        if not value:
            errors.append("db_name은 비어있을 수 없습니다")
        
        # 데이터베이스 이름 형식 검증
        if not re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', value):
            warnings.append("데이터베이스 이름에 특수문자가 포함되어 있습니다")
        
        return errors, warnings
    
    def _validate_db_user(self, value: Any) -> Tuple[List[str], List[str]]:
        """데이터베이스 사용자 검증"""
        errors = []
        warnings = []
        
        if not isinstance(value, str):
            errors.append("db_user는 문자열이어야 합니다")
            return errors, warnings
        
        if not value:
            errors.append("db_user는 비어있을 수 없습니다")
        
        return errors, warnings
    
    def _validate_redis_host(self, value: Any) -> Tuple[List[str], List[str]]:
        """Redis 호스트 검증"""
        errors = []
        warnings = []
        
        if not isinstance(value, str):
            errors.append("redis_host는 문자열이어야 합니다")
            return errors, warnings
        
        if not value:
            errors.append("redis_host는 비어있을 수 없습니다")
        
        return errors, warnings
    
    def _validate_redis_port(self, value: Any) -> Tuple[List[str], List[str]]:
        """Redis 포트 검증"""
        errors = []
        warnings = []
        
        if not isinstance(value, int):
            errors.append("redis_port는 정수여야 합니다")
            return errors, warnings
        
        if value < 1 or value > 65535:
            errors.append("redis_port는 1-65535 범위여야 합니다")
        elif value != 6379:
            warnings.append("Redis 기본 포트(6379)가 아닙니다")
        
        return errors, warnings
    
    def _validate_service_specific(self, service_name: str, config_data: Dict[str, Any]) -> Tuple[List[str], List[str]]:
        """서비스별 특화 검증"""
        errors = []
        warnings = []
        
        if service_name == "duri_core":
            # duri_core 특화 검증
            if 'custom_config' in config_data:
                custom = config_data['custom_config']
                if 'brain_url' in custom and not custom['brain_url'].startswith('http'):
                    errors.append("brain_url은 http:// 또는 https://로 시작해야 합니다")
                if 'control_url' in custom and not custom['control_url'].startswith('http'):
                    errors.append("control_url은 http:// 또는 https://로 시작해야 합니다")
        
        elif service_name == "duri_brain":
            # duri_brain 특화 검증
            if 'custom_config' in config_data:
                custom = config_data['custom_config']
                if 'cache_size' in custom and custom['cache_size'] > 10000:
                    warnings.append("캐시 크기가 10000을 초과합니다. 메모리 사용량에 주의하세요")
                if 'prediction_timeout' in custom and custom['prediction_timeout'] > 60:
                    warnings.append("예측 타임아웃이 60초를 초과합니다")
        
        return errors, warnings
    
    def _validate_dependencies(self, service_name: str, config_data: Dict[str, Any]) -> Tuple[List[str], List[str]]:
        """의존성 검증"""
        errors = []
        warnings = []
        
        # 포트 충돌 검증
        if 'port' in config_data:
            port = config_data['port']
            if port in [8080, 8081, 8082, 8083]:
                # 다른 서비스와의 포트 충돌 가능성
                if service_name == "duri_core" and port != 8080:
                    warnings.append("duri_core는 일반적으로 8080 포트를 사용합니다")
                elif service_name == "duri_brain" and port != 8081:
                    warnings.append("duri_brain은 일반적으로 8081 포트를 사용합니다")
                elif service_name == "duri_evolution" and port != 8082:
                    warnings.append("duri_evolution은 일반적으로 8082 포트를 사용합니다")
                elif service_name == "duri_control" and port != 8083:
                    warnings.append("duri_control은 일반적으로 8083 포트를 사용합니다")
        
        return errors, warnings
    
    def _validate_business_logic(self, service_name: str, config_data: Dict[str, Any]) -> Tuple[List[str], List[str]]:
        """비즈니스 로직 검증"""
        errors = []
        warnings = []
        
        # 타임아웃과 재시도 횟수의 조합 검증
        if 'timeout' in config_data and 'retry_count' in config_data:
            timeout = config_data['timeout']
            retry_count = config_data['retry_count']
            total_timeout = timeout * (retry_count + 1)
            
            if total_timeout > 300:  # 5분
                warnings.append(f"총 타임아웃 시간이 5분을 초과합니다: {total_timeout}초")
        
        # 스레드 수와 타임아웃의 조합 검증
        if 'max_threads' in config_data and 'timeout' in config_data:
            max_threads = config_data['max_threads']
            timeout = config_data['timeout']
            
            if max_threads * timeout > 1000:
                warnings.append("스레드 수와 타임아웃의 곱이 1000을 초과합니다. 리소스 사용량에 주의하세요")
        
        return errors, warnings


# 전역 검증기 인스턴스
config_validator = ConfigValidator() 