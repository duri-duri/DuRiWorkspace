from DuRiCore.trace import emit_trace
class BaseRunError(Exception):
    code: str = 'unknown'

    def __init__(self, message: str='', *, code: str | None=None):
        super().__init__(message)
        if code:
            self.code = code

class ValidationError(BaseRunError):
    pass

class TransientError(BaseRunError):
    pass

class SystemError(BaseRunError):
    pass