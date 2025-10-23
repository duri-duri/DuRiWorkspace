# 호환 레이어: 기존 코드를 보존하면서 import 에러만 해결


class ReasoningIntegration:
    """호환성을 위한 ReasoningIntegration 스텁"""

    def __init__(self, *args, **kwargs):
        pass

    def integrate(self, *args, **kwargs):
        return {"status": "stub", "message": "compatibility layer"}
