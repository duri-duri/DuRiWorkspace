"""
표준화된 응답 시스템
중복된 오류 처리 로직을 통합하고 판단 로고 시스템을 제공합니다.
"""

import json
import logging
from datetime import datetime
from enum import Enum
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


class ResponseType(Enum):
    """응답 유형"""

    SUCCESS = "success"
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"
    JUDGMENT = "judgment"
    PREDICTION = "prediction"
    FEEDBACK = "feedback"
    MEMORY = "memory"
    SYSTEM = "system"


class ErrorSeverity(Enum):
    """오류 심각도"""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class JudgmentLogo:
    """판단 로고 - 표준화된 응답 형식"""

    def __init__(
        self,
        type: str,
        confidence: float,
        data: Dict[str, Any],
        timestamp: Optional[datetime] = None,
    ):
        self.type = type
        self.confidence = max(0.0, min(1.0, confidence))  # 0.0-1.0 범위 보장
        self.data = data
        self.timestamp = timestamp or datetime.now()

    def to_dict(self) -> Dict[str, Any]:
        """딕셔너리 형태로 변환"""
        return {
            "type": self.type,
            "confidence": self.confidence,
            "timestamp": self.timestamp.isoformat(),
            "data": self.data,
        }

    def to_json(self) -> str:
        """JSON 문자열로 변환"""
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=2)


class StandardResponse:
    """표준화된 응답 시스템"""

    @staticmethod
    def success(data: Dict[str, Any] = None, message: str = "성공") -> Dict[str, Any]:
        """성공 응답"""
        return {
            "type": ResponseType.SUCCESS.value,
            "success": True,
            "message": message,
            "data": data or {},
            "timestamp": datetime.now().isoformat(),
        }

    @staticmethod
    def error(
        error_type: str,
        message: str,
        severity: ErrorSeverity = ErrorSeverity.MEDIUM,
        details: Dict[str, Any] = None,
    ) -> Dict[str, Any]:
        """오류 응답"""
        return {
            "type": ResponseType.ERROR.value,
            "success": False,
            "error_type": error_type,
            "message": message,
            "severity": severity.value,
            "details": details or {},
            "timestamp": datetime.now().isoformat(),
        }

    @staticmethod
    def judgment(
        judgment_type: str,
        confidence: float,
        reasoning: str,
        alternatives: list = None,
        data: Dict[str, Any] = None,
    ) -> Dict[str, Any]:
        """판단 응답"""
        return {
            "type": ResponseType.JUDGMENT.value,
            "judgment_type": judgment_type,
            "confidence": max(0.0, min(1.0, confidence)),
            "reasoning": reasoning,
            "alternatives": alternatives or [],
            "data": data or {},
            "timestamp": datetime.now().isoformat(),
        }

    @staticmethod
    def prediction(
        prediction_type: str,
        predicted_outcome: str,
        confidence: float,
        timeframe: str = "미정",
        supporting_evidence: list = None,
    ) -> Dict[str, Any]:
        """예측 응답"""
        return {
            "type": ResponseType.PREDICTION.value,
            "prediction_type": prediction_type,
            "predicted_outcome": predicted_outcome,
            "confidence": max(0.0, min(1.0, confidence)),
            "timeframe": timeframe,
            "supporting_evidence": supporting_evidence or [],
            "timestamp": datetime.now().isoformat(),
        }

    @staticmethod
    def feedback(
        feedback_type: str,
        message: str,
        priority: str = "medium",
        actionable_items: list = None,
    ) -> Dict[str, Any]:
        """피드백 응답"""
        return {
            "type": ResponseType.FEEDBACK.value,
            "feedback_type": feedback_type,
            "message": message,
            "priority": priority,
            "actionable_items": actionable_items or [],
            "timestamp": datetime.now().isoformat(),
        }

    @staticmethod
    def memory_operation(
        operation: str,
        memory_id: str = None,
        success: bool = True,
        data: Dict[str, Any] = None,
    ) -> Dict[str, Any]:
        """메모리 작업 응답"""
        return {
            "type": ResponseType.MEMORY.value,
            "operation": operation,
            "memory_id": memory_id,
            "success": success,
            "data": data or {},
            "timestamp": datetime.now().isoformat(),
        }

    @staticmethod
    def system_status(
        status: str,
        components: Dict[str, Any] = None,
        performance_metrics: Dict[str, float] = None,
    ) -> Dict[str, Any]:
        """시스템 상태 응답"""
        return {
            "type": ResponseType.SYSTEM.value,
            "status": status,
            "components": components or {},
            "performance_metrics": performance_metrics or {},
            "timestamp": datetime.now().isoformat(),
        }


class ErrorHandler:
    """통합 오류 처리기"""

    @staticmethod
    def handle_exception(
        e: Exception,
        context: str = "unknown",
        severity: ErrorSeverity = ErrorSeverity.MEDIUM,
    ) -> Dict[str, Any]:
        """예외 처리"""
        logger.error(f"오류 발생 ({context}): {str(e)}")
        return StandardResponse.error(
            error_type="exception",
            message=str(e),
            severity=severity,
            details={"context": context, "exception_type": type(e).__name__},
        )

    @staticmethod
    def handle_not_found(item_type: str, item_id: str = None, context: str = "unknown") -> Dict[str, Any]:
        """찾을 수 없음 오류"""
        message = f"{item_type}을(를) 찾을 수 없습니다."
        if item_id:
            message += f" (ID: {item_id})"

        return StandardResponse.error(
            error_type="not_found",
            message=message,
            severity=ErrorSeverity.MEDIUM,
            details={"item_type": item_type, "item_id": item_id, "context": context},
        )

    @staticmethod
    def handle_insufficient_data(
        operation: str, required_data: list = None, context: str = "unknown"
    ) -> Dict[str, Any]:
        """데이터 부족 오류"""
        message = f"{operation}을(를) 수행하기 위한 데이터가 부족합니다."
        if required_data:
            message += f" 필요 데이터: {', '.join(required_data)}"

        return StandardResponse.error(
            error_type="insufficient_data",
            message=message,
            severity=ErrorSeverity.LOW,
            details={
                "operation": operation,
                "required_data": required_data,
                "context": context,
            },
        )

    @staticmethod
    def handle_validation_error(field: str, expected: str, actual: str, context: str = "unknown") -> Dict[str, Any]:
        """검증 오류"""
        return StandardResponse.error(
            error_type="validation_error",
            message=f"검증 실패: {field} (예상: {expected}, 실제: {actual})",
            severity=ErrorSeverity.MEDIUM,
            details={
                "field": field,
                "expected": expected,
                "actual": actual,
                "context": context,
            },
        )


# 기존 문자열 반환 패턴을 판단 로고로 변환하는 헬퍼 함수들
class StringToLogoConverter:
    """문자열 반환 패턴을 판단 로고로 변환"""

    @staticmethod
    def prediction_error_to_logo(original_message: str) -> Dict[str, Any]:
        """예측 오류 메시지를 판단 로고로 변환"""
        if "예측을 생성할 수 없습니다" in original_message:
            return StandardResponse.error(
                error_type="prediction_failed",
                message="예측을 생성할 수 없습니다",
                severity=ErrorSeverity.MEDIUM,
                details={"reason": "insufficient_data"},
            )
        elif "패턴 분석 결과" in original_message:
            return StandardResponse.prediction(
                prediction_type="pattern_analysis",
                predicted_outcome=original_message,
                confidence=0.7,
                timeframe="short_term",
            )
        else:
            return StandardResponse.prediction(
                prediction_type="general",
                predicted_outcome=original_message,
                confidence=0.5,
                timeframe="unknown",
            )

    @staticmethod
    def feedback_message_to_logo(original_message: str) -> Dict[str, Any]:
        """피드백 메시지를 판단 로고로 변환"""
        if "긴급한 개선" in original_message:
            return StandardResponse.feedback(
                feedback_type="urgent_improvement",
                message=original_message,
                priority="high",
                actionable_items=["즉시 분석", "개선 실행", "결과 모니터링"],
            )
        elif "점진적 개선" in original_message:
            return StandardResponse.feedback(
                feedback_type="gradual_improvement",
                message=original_message,
                priority="medium",
                actionable_items=["상황 분석", "단계적 개선", "효과 측정"],
            )
        else:
            return StandardResponse.feedback(feedback_type="general", message=original_message, priority="low")

    @staticmethod
    def system_status_to_logo(status_message: str) -> Dict[str, Any]:
        """시스템 상태 메시지를 판단 로고로 변환"""
        if "성공" in status_message:
            return StandardResponse.system_status(status="success", performance_metrics={"success_rate": 1.0})
        elif "오류" in status_message:
            return StandardResponse.system_status(status="error", performance_metrics={"error_rate": 1.0})
        else:
            return StandardResponse.system_status(status="unknown", performance_metrics={"status": 0.5})


# 사용 예시
if __name__ == "__main__":
    # 성공 응답 예시
    success_response = StandardResponse.success(
        data={"result": "작업 완료"}, message="작업이 성공적으로 완료되었습니다"
    )
    print("성공 응답:", json.dumps(success_response, ensure_ascii=False, indent=2))

    # 오류 응답 예시
    error_response = StandardResponse.error(
        error_type="validation_error",
        message="입력 데이터가 유효하지 않습니다",
        severity=ErrorSeverity.MEDIUM,
    )
    print("오류 응답:", json.dumps(error_response, ensure_ascii=False, indent=2))

    # 판단 응답 예시
    judgment_response = StandardResponse.judgment(
        judgment_type="strategic_decision",
        confidence=0.85,
        reasoning="전략적 분석 결과",
        alternatives=["옵션 A", "옵션 B", "옵션 C"],
    )
    print("판단 응답:", json.dumps(judgment_response, ensure_ascii=False, indent=2))
