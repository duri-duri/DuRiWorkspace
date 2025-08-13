from DuRiCore.trace import emit_trace
from dataclasses import dataclass

class BaseRunError(Exception):
    code: str = 'unknown'

    def __init__(self, message: str='', *, code: str | None=None):
        super().__init__(message)
        if code:
            self.code = code

class ValidationError(BaseRunError):
    """도메인 규칙 위반(입력 불일치/임계 초과). 재시도 없음."""
    pass

class TransientError(BaseRunError):
    """일시적 실패(네트워크/레이트리밋/타임아웃). 짧은 재시도."""
    pass

class SystemError(BaseRunError):
    """예상외 시스템 오류. 재시도 없음 + 알람."""
    pass

@dataclass(frozen=True)
class ErrorPolicy:
    transient_max_attempts: int = 2
    backoff_ms: tuple[int, ...] = (5, 20)
    alert_on_system_error: bool = True