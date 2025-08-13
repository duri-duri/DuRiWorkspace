import os
from duri_control.app.services.notify_service import NotifyService, NotificationType

def notify_if_enabled(title: str, message: str, webhook_env: str = "DURI_ALERT_WEBHOOK") -> None:
    """
    환경변수로 설정된 Webhook URL로 알림을 전송합니다.
    환경변수가 없거나 전송 실패 시에도 게이트 진행에 영향을 주지 않습니다.
    """
    url = os.getenv(webhook_env, "")
    if not url:
        return
    try:
        NotifyService.send(
            ntype=NotificationType.WEBHOOK,
            target=url,
            payload={"title": title, "message": message},
            timeout=3,
        )
    except Exception:
        # 알림 실패는 게이트에 영향 주지 않음
        pass
