# 호환 레이어: 기존 코드를 보존하면서 import 에러만 해결
# 실제 구현이 없을 때만 스텁 제공

try:
    # 실제 구현이 있다면 사용
    from duri_core.reasoning.integration.conflict_resolver import ConflictResolver
except ImportError:
    # 실제 구현이 없을 때만 스텁 제공
    class ConflictResolver:
        def __init__(self, *args, **kwargs):
            pass

        def resolve(self, *args, **kwargs):
            return {"status": "stub", "message": "compatibility layer"}
