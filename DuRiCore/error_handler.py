#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DuRi 리팩토링 Phase 1 - 에러 핸들링 시스템

시스템에서 발생하는 오류를 안전하게 처리하고 로깅하는 기능을 제공합니다.
- 에러 핸들링
- 컨텍스트 로깅
- 에러 리포트 생성
- 자동 복구 시도
"""

import json
import logging
import sys
import time
import traceback
from dataclasses import asdict, dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Callable, Dict, List, Optional

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ErrorSeverity(Enum):
    """에러 심각도"""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ErrorCategory(Enum):
    """에러 카테고리"""

    SYSTEM = "system"
    NETWORK = "network"
    DATABASE = "database"
    VALIDATION = "validation"
    INTEGRATION = "integration"
    PERFORMANCE = "performance"
    UNKNOWN = "unknown"


@dataclass
class ErrorContext:
    """에러 컨텍스트"""

    system_name: str
    function_name: str
    line_number: int
    timestamp: datetime
    user_id: str = ""
    session_id: str = ""
    request_id: str = ""
    additional_data: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ErrorReport:
    """에러 리포트"""

    error_id: str
    error_type: str
    error_message: str
    error_traceback: str
    severity: ErrorSeverity
    category: ErrorCategory
    context: ErrorContext
    retry_count: int = 0
    resolved: bool = False
    resolution_time: Optional[datetime] = None
    created_at: datetime = field(default_factory=datetime.now)


class ErrorHandler:
    """에러 핸들링 시스템"""

    def __init__(self, log_file: str = "error_log.json", max_errors: int = 1000):
        self.log_file = log_file
        self.max_errors = max_errors
        self.errors: List[ErrorReport] = []
        self.error_handlers: Dict[ErrorCategory, List[Callable]] = {
            category: [] for category in ErrorCategory
        }
        self.recovery_strategies: Dict[ErrorCategory, Callable] = {}

        logger.info("에러 핸들링 시스템 초기화 완료")

    def handle_system_error(
        self,
        error: Exception,
        context: str,
        severity: ErrorSeverity = ErrorSeverity.MEDIUM,
        category: ErrorCategory = ErrorCategory.UNKNOWN,
    ) -> ErrorReport:
        """시스템 에러 처리"""
        try:
            # 에러 컨텍스트 생성
            error_context = self._create_error_context(context)

            # 에러 리포트 생성
            error_report = ErrorReport(
                error_id=f"error_{int(time.time())}",
                error_type=type(error).__name__,
                error_message=str(error),
                error_traceback=traceback.format_exc(),
                severity=severity,
                category=category,
                context=error_context,
            )

            # 에러 저장
            self._save_error(error_report)

            # 에러 핸들러 실행
            self._execute_error_handlers(error_report)

            # 복구 전략 시도
            if severity in [ErrorSeverity.HIGH, ErrorSeverity.CRITICAL]:
                self._attempt_recovery(error_report)

            logger.error(f"시스템 에러 처리 완료: {error_report.error_id} ({severity.value})")
            return error_report

        except Exception as e:
            logger.error(f"에러 처리 중 추가 에러 발생: {e}")
            return self._create_fallback_error_report(error, context)

    def log_error_with_context(self, error: Exception, context: Dict[str, Any]) -> ErrorReport:
        """컨텍스트와 함께 에러 로깅"""
        try:
            # 컨텍스트에서 정보 추출
            system_name = context.get("system_name", "unknown")
            function_name = context.get("function_name", "unknown")
            line_number = context.get("line_number", 0)
            user_id = context.get("user_id", "")
            session_id = context.get("session_id", "")
            request_id = context.get("request_id", "")

            # 에러 컨텍스트 생성
            error_context = ErrorContext(
                system_name=system_name,
                function_name=function_name,
                line_number=line_number,
                timestamp=datetime.now(),
                user_id=user_id,
                session_id=session_id,
                request_id=request_id,
                additional_data=context,
            )

            # 심각도 및 카테고리 결정
            severity = self._determine_severity(error, context)
            category = self._determine_category(error, context)

            # 에러 리포트 생성
            error_report = ErrorReport(
                error_id=f"error_{int(time.time())}",
                error_type=type(error).__name__,
                error_message=str(error),
                error_traceback=traceback.format_exc(),
                severity=severity,
                category=category,
                context=error_context,
            )

            # 에러 저장
            self._save_error(error_report)

            logger.error(f"컨텍스트 에러 로깅 완료: {error_report.error_id}")
            return error_report

        except Exception as e:
            logger.error(f"컨텍스트 에러 로깅 중 추가 에러 발생: {e}")
            return self._create_fallback_error_report(error, str(context))

    def create_error_report(self, error: Exception) -> Dict[str, Any]:
        """에러 리포트 생성"""
        try:
            error_report = ErrorReport(
                error_id=f"error_{int(time.time())}",
                error_type=type(error).__name__,
                error_message=str(error),
                error_traceback=traceback.format_exc(),
                severity=ErrorSeverity.MEDIUM,
                category=ErrorCategory.UNKNOWN,
                context=self._create_error_context("manual_report"),
            )

            return asdict(error_report)

        except Exception as e:
            logger.error(f"에러 리포트 생성 중 추가 에러 발생: {e}")
            return {
                "error_id": f"error_{int(time.time())}",
                "error_type": type(error).__name__,
                "error_message": str(error),
                "error_traceback": traceback.format_exc(),
                "severity": ErrorSeverity.CRITICAL.value,
                "category": ErrorCategory.UNKNOWN.value,
                "context": {
                    "system_name": "error_handler",
                    "function_name": "create_error_report",
                    "line_number": 0,
                    "timestamp": datetime.now().isoformat(),
                },
                "created_at": datetime.now().isoformat(),
            }

    def register_error_handler(self, category: ErrorCategory, handler: Callable):
        """에러 핸들러 등록"""
        if category not in self.error_handlers:
            self.error_handlers[category] = []
        self.error_handlers[category].append(handler)
        logger.info(f"에러 핸들러 등록 완료: {category.value}")

    def register_recovery_strategy(self, category: ErrorCategory, strategy: Callable):
        """복구 전략 등록"""
        self.recovery_strategies[category] = strategy
        logger.info(f"복구 전략 등록 완료: {category.value}")

    def get_error_statistics(self) -> Dict[str, Any]:
        """에러 통계 반환"""
        if not self.errors:
            return {
                "total_errors": 0,
                "errors_by_severity": {},
                "errors_by_category": {},
                "recent_errors": [],
            }

        # 심각도별 통계
        errors_by_severity = {}
        for severity in ErrorSeverity:
            errors_by_severity[severity.value] = len(
                [e for e in self.errors if e.severity == severity]
            )

        # 카테고리별 통계
        errors_by_category = {}
        for category in ErrorCategory:
            errors_by_category[category.value] = len(
                [e for e in self.errors if e.category == category]
            )

        # 최근 에러
        recent_errors = [
            {
                "error_id": e.error_id,
                "error_type": e.error_type,
                "error_message": e.error_message,
                "severity": e.severity.value,
                "category": e.category.value,
                "timestamp": e.created_at.isoformat(),
            }
            for e in sorted(self.errors, key=lambda x: x.created_at, reverse=True)[:10]
        ]

        return {
            "total_errors": len(self.errors),
            "errors_by_severity": errors_by_severity,
            "errors_by_category": errors_by_category,
            "recent_errors": recent_errors,
        }

    def _create_error_context(self, context: str) -> ErrorContext:
        """에러 컨텍스트 생성"""
        try:
            # 현재 스택 프레임 정보 추출
            frame = sys._getframe(2)  # 호출자 프레임
            return ErrorContext(
                system_name=frame.f_globals.get("__name__", "unknown"),
                function_name=frame.f_code.co_name,
                line_number=frame.f_lineno,
                timestamp=datetime.now(),
            )
        except Exception:
            return ErrorContext(
                system_name="unknown",
                function_name="unknown",
                line_number=0,
                timestamp=datetime.now(),
            )

    def _determine_severity(self, error: Exception, context: Dict[str, Any]) -> ErrorSeverity:
        """에러 심각도 결정"""
        error_type = type(error).__name__

        # 심각도 결정 로직
        if error_type in ["SystemError", "MemoryError", "OSError"]:
            return ErrorSeverity.CRITICAL
        elif error_type in ["ValueError", "TypeError", "AttributeError"]:
            return ErrorSeverity.MEDIUM
        elif error_type in ["Warning", "UserWarning"]:
            return ErrorSeverity.LOW
        else:
            return ErrorSeverity.MEDIUM

    def _determine_category(self, error: Exception, context: Dict[str, Any]) -> ErrorCategory:
        """에러 카테고리 결정"""
        error_type = type(error).__name__
        error_message = str(error).lower()

        # 카테고리 결정 로직
        if "network" in error_message or "connection" in error_message:
            return ErrorCategory.NETWORK
        elif "database" in error_message or "sql" in error_message:
            return ErrorCategory.DATABASE
        elif "validation" in error_message or "invalid" in error_message:
            return ErrorCategory.VALIDATION
        elif "integration" in error_message or "api" in error_message:
            return ErrorCategory.INTEGRATION
        elif "performance" in error_message or "timeout" in error_message:
            return ErrorCategory.PERFORMANCE
        else:
            return ErrorCategory.UNKNOWN

    def _save_error(self, error_report: ErrorReport):
        """에러 저장"""
        self.errors.append(error_report)

        # 최대 에러 수 제한
        if len(self.errors) > self.max_errors:
            self.errors = self.errors[-self.max_errors :]

        # 파일에 저장
        try:
            with open(self.log_file, "w", encoding="utf-8") as f:
                json.dump(
                    [asdict(e) for e in self.errors],
                    f,
                    indent=2,
                    ensure_ascii=False,
                    default=str,
                )
        except Exception as e:
            logger.error(f"에러 로그 파일 저장 실패: {e}")

    def _execute_error_handlers(self, error_report: ErrorReport):
        """에러 핸들러 실행"""
        handlers = self.error_handlers.get(error_report.category, [])
        for handler in handlers:
            try:
                handler(error_report)
            except Exception as e:
                logger.error(f"에러 핸들러 실행 실패: {e}")

    def _attempt_recovery(self, error_report: ErrorReport):
        """복구 시도"""
        strategy = self.recovery_strategies.get(error_report.category)
        if strategy:
            try:
                strategy(error_report)
                error_report.resolved = True
                error_report.resolution_time = datetime.now()
                logger.info(f"에러 복구 성공: {error_report.error_id}")
            except Exception as e:
                logger.error(f"에러 복구 실패: {e}")

    def _create_fallback_error_report(self, error: Exception, context: str) -> ErrorReport:
        """폴백 에러 리포트 생성"""
        return ErrorReport(
            error_id=f"error_{int(time.time())}",
            error_type=type(error).__name__,
            error_message=str(error),
            error_traceback=traceback.format_exc(),
            severity=ErrorSeverity.CRITICAL,
            category=ErrorCategory.UNKNOWN,
            context=ErrorContext(
                system_name="error_handler",
                function_name="fallback",
                line_number=0,
                timestamp=datetime.now(),
            ),
        )


# 전역 에러 핸들러 인스턴스
error_handler = ErrorHandler()


# 편의 함수들
def handle_error(
    error: Exception, context: str = "", severity: ErrorSeverity = ErrorSeverity.MEDIUM
) -> ErrorReport:
    """에러 처리 (편의 함수)"""
    return error_handler.handle_system_error(error, context, severity)


def log_error(error: Exception, context: Dict[str, Any]) -> ErrorReport:
    """에러 로깅 (편의 함수)"""
    return error_handler.log_error_with_context(error, context)


def create_error_report(error: Exception) -> Dict[str, Any]:
    """에러 리포트 생성 (편의 함수)"""
    return error_handler.create_error_report(error)


def get_error_statistics() -> Dict[str, Any]:
    """에러 통계 반환 (편의 함수)"""
    return error_handler.get_error_statistics()
