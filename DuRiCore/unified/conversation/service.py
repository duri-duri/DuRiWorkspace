from __future__ import annotations

from typing import Any, Dict


class UnifiedConversationService:
    """
    대화/커뮤니케이션 통합 게이트웨이:
      - 기존 unified_conversation_service.py 활용
      - intent 에 따라 하위 서비스에 위임
    """

    def __init__(self, router=None) -> None:
        self.router = router
        # 기존 통합 대화 서비스 활용
        try:
            from DuRiCore.unified_conversation_service import (
                UnifiedConversationService as ExistingService,
            )

            self.existing_service = ExistingService()
        except ImportError:
            self.existing_service = None

    def handle(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        intent = (payload or {}).get("intent", "general")

        # 기존 서비스가 있으면 활용
        if self.existing_service:
            try:
                return self.existing_service.process_message(payload)
            except Exception:
                pass

        # 폴백: 라우터 기반 처리
        target = (self.router or {}).get(intent)
        if callable(target):
            return target(payload)
        return {"result": "conversation:unknown_intent", "confidence": 0.5}
