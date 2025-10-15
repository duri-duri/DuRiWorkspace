#!/usr/bin/env python3
"""
DuRi 전역 로깅 관리자 - JSON 이중 출력 + 로그 위생 개선
"""

import logging
import os
import json
import re
from logging.handlers import RotatingFileHandler
from typing import Optional, Dict, Any
from datetime import datetime, timezone

class GlobalLoggingManager:
    """전역 로깅 관리자 (싱글톤)"""
    
    _instance = None
    _initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not self._initialized:
            self.log_file = "./logs/duri-core.log"
            self.max_bytes = 10 * 1024 * 1024  # 10MB
            self.backup_count = 5
            self._setup_logging()
            GlobalLoggingManager._initialized = True
    
    def _setup_logging(self):
        """로깅 설정"""
        # 디렉토리 생성
        os.makedirs(os.path.dirname(self.log_file), exist_ok=True)
        
        # 루트 로거 설정
        root_logger = logging.getLogger()
        root_logger.setLevel(logging.INFO)
        
        # 기존 핸들러 제거 (중복 방지)
        for handler in root_logger.handlers[:]:
            root_logger.removeHandler(handler)
        
        # DuRi 전용 로거 설정
        duri_logger = logging.getLogger("duri-core")
        duri_logger.setLevel(logging.INFO)
        duri_logger.propagate = False  # 상위로 전파 방지
        
        # 파일 핸들러 (기존 형식 유지)
        if not any(isinstance(h, RotatingFileHandler) and h.baseFilename.endswith("duri-core.log")
                   for h in duri_logger.handlers):
            file_handler = RotatingFileHandler(
                self.log_file, 
                maxBytes=self.max_bytes, 
                backupCount=self.backup_count, 
                encoding="utf-8"
            )
            file_handler.setFormatter(
                logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
            )
            duri_logger.addHandler(file_handler)
        
        # 콘솔 JSON 핸들러 (구조화 로그)
        if not any(isinstance(h, logging.StreamHandler) for h in duri_logger.handlers):
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(JsonFormatter())
            duri_logger.addHandler(console_handler)
    
    def get_logger(self, name: str = "duri-core") -> logging.Logger:
        """로거 반환"""
        return logging.getLogger(name)
    
    def get_context_logger(self, *, deploy_id: Optional[str] = None, 
                          cycle_id: Optional[str] = None, 
                          trace_id: Optional[str] = None, 
                          name: str = "duri-core"):
        """컨텍스트 로거 반환 - 필드 자동주입"""
        base = logging.getLogger(name)
        
        class _ContextAdapter(logging.LoggerAdapter):
            def process(self, msg, kwargs):
                extra = kwargs.get("extra", {})
                if deploy_id:
                    extra.setdefault("deploy_id", deploy_id)
                if cycle_id:
                    extra.setdefault("cycle_id", cycle_id)
                if trace_id:
                    extra.setdefault("trace_id", trace_id)
                kwargs["extra"] = extra
                return msg, kwargs
        
        return _ContextAdapter(base, {})
    
    def flush_all(self):
        """모든 핸들러 강제 flush"""
        for logger_name in ["duri-core", "DuRiCore", "duri_modules"]:
            logger = logging.getLogger(logger_name)
            for handler in logger.handlers:
                if hasattr(handler, "flush"):
                    handler.flush()
    
    def log_system_event(self, event_type: str, message: str, level: str = "INFO", 
                        deploy_id: Optional[str] = None, cycle_id: Optional[str] = None,
                        trace_id: Optional[str] = None):
        """시스템 이벤트 로깅 - 컨텍스트 포함"""
        logger = self.get_logger("duri-core")
        log_level = getattr(logging, level.upper(), logging.INFO)
        
        # 컨텍스트 정보를 별도 필드로 추가
        extra_fields = {}
        if deploy_id:
            extra_fields["deploy_id"] = deploy_id
        if cycle_id:
            extra_fields["cycle_id"] = cycle_id
        if trace_id:
            extra_fields["trace_id"] = trace_id
        if event_type:
            extra_fields["event_type"] = event_type
        
        logger.log(log_level, f"[{event_type}] {message}", extra=extra_fields)
        self.flush_all()
    
    @staticmethod
    def utc_now() -> str:
        """UTC 시간 ISO8601 형식"""
        return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")

class JsonFormatter(logging.Formatter):
    """JSON 로그 포맷터 - 로그 위생 개선"""
    
    # 비밀/토큰 패턴 (로그에서 마스킹) - 오탐/누락 최소화
    SENSITIVE_PATTERNS = [
        (re.compile(r'(?i)\bpassword\s*[:=]\s*([^\s",}]+)'), r'password="***"'),
        (re.compile(r'(?i)\bapi[_-]?key\s*[:=]\s*([^\s",}]+)'), r'api_key="***"'),
        (re.compile(r'(?i)\btoken\s*[:=]\s*([^\s",}]+)'), r'token="***"'),
        (re.compile(r'(?i)\bsecret\s*[:=]\s*([^\s",}]+)'), r'secret="***"'),
        (re.compile(r'(?i)\bbearer\s+([A-Za-z0-9\-._~+/]+=*)'), r'Bearer ***'),
        (re.compile(r'(?i)\bauthorization\s*[:=]\s*([^\s",}]+)'), r'authorization="***"'),
    ]
    
    def _sanitize_message(self, message: str) -> str:
        """메시지에서 비밀 정보 마스킹 - 오탐/누락 최소화"""
        sanitized = message
        for pattern, replacement in self.SENSITIVE_PATTERNS:
            sanitized = pattern.sub(replacement, sanitized)
        return sanitized
    
    def format(self, record: logging.LogRecord) -> str:
        """로그 레코드를 JSON 형식으로 포맷 - 로그 위생 적용"""
        # 메시지 위생 처리
        sanitized_message = self._sanitize_message(record.getMessage())
        
        log_entry = {
            "timestamp": GlobalLoggingManager.utc_now(),
            "level": record.levelname,
            "logger": record.name,
            "message": sanitized_message,
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
            "process_id": record.process,
            "thread_name": record.threadName
        }
        
        # 컨텍스트 정보 추가 (extra 필드에서)
        for key, value in record.__dict__.items():
            if key not in ['name', 'msg', 'args', 'levelname', 'levelno', 'pathname', 
                          'filename', 'module', 'lineno', 'funcName', 'created', 
                          'msecs', 'relativeCreated', 'thread', 'threadName', 
                          'processName', 'process', 'getMessage', 'exc_info', 'exc_text', 'stack_info']:
                # 값도 위생 처리
                if isinstance(value, str):
                    value = self._sanitize_message(value)
                log_entry[key] = value
        
        # 예외 정보 추가
        if record.exc_info:
            log_entry["exception"] = self._sanitize_message(self.formatException(record.exc_info))
        
        return json.dumps(log_entry, ensure_ascii=False)

# 전역 인스턴스
global_logging_manager = GlobalLoggingManager()

# 편의 함수들
def get_duri_logger(name: str = "duri-core") -> logging.Logger:
    """DuRi 로거 반환"""
    return global_logging_manager.get_logger(name)

def get_context_logger(*, deploy_id: Optional[str] = None, 
                      cycle_id: Optional[str] = None, 
                      trace_id: Optional[str] = None, 
                      name: str = "duri-core"):
    """컨텍스트 로거 반환 - 필드 자동주입"""
    return global_logging_manager.get_context_logger(
        deploy_id=deploy_id, cycle_id=cycle_id, trace_id=trace_id, name=name
    )

def log_system_event(event_type: str, message: str, level: str = "INFO",
                    deploy_id: Optional[str] = None, cycle_id: Optional[str] = None,
                    trace_id: Optional[str] = None):
    """시스템 이벤트 로깅"""
    global_logging_manager.log_system_event(event_type, message, level, deploy_id, cycle_id, trace_id)

def flush_logs():
    """로그 강제 flush"""
    global_logging_manager.flush_all()

def utc_now() -> str:
    """UTC 시간 ISO8601 형식"""
    return GlobalLoggingManager.utc_now()
