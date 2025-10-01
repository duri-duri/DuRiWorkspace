#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DuRiCore Phase 2-4: 성능 알림 관리 모듈

성능 알림을 생성하고 관리하는 모듈입니다.
- 성능 알림 생성
- 알림 규칙 관리
- 알림 전송
- 알림 이력 관리
"""

import asyncio
from collections import defaultdict, deque
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import json
import logging
import time
from typing import Any, Callable, Dict, List, Optional, Tuple, Union
import uuid

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AlertLevel(Enum):
    """알림 레벨"""

    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class AlertStatus(Enum):
    """알림 상태"""

    ACTIVE = "active"
    ACKNOWLEDGED = "acknowledged"
    RESOLVED = "resolved"
    EXPIRED = "expired"


class AlertChannel(Enum):
    """알림 채널"""

    LOG = "log"
    EMAIL = "email"
    WEBHOOK = "webhook"
    SMS = "sms"
    PUSH = "push"


@dataclass
class AlertRule:
    """알림 규칙"""

    rule_id: str
    rule_name: str
    metric_name: str
    condition: str  # >, <, >=, <=, ==, !=
    threshold: float
    alert_level: AlertLevel
    channels: List[AlertChannel] = field(default_factory=list)
    enabled: bool = True
    cooldown_period: timedelta = field(default_factory=lambda: timedelta(minutes=5))
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class PerformanceAlert:
    """성능 알림"""

    alert_id: str
    rule_id: str
    alert_level: AlertLevel
    alert_message: str
    metric_name: str
    current_value: float
    threshold: float
    timestamp: datetime = field(default_factory=datetime.now)
    status: AlertStatus = AlertStatus.ACTIVE
    acknowledged_by: Optional[str] = None
    acknowledged_at: Optional[datetime] = None
    resolved_by: Optional[str] = None
    resolved_at: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AlertNotification:
    """알림 전송"""

    notification_id: str
    alert_id: str
    channel: AlertChannel
    message: str
    recipient: str = ""
    sent_at: datetime = field(default_factory=datetime.now)
    status: str = "pending"  # pending, sent, failed
    retry_count: int = 0
    max_retries: int = 3


class PerformanceAlertManager:
    """성능 알림 관리자"""

    def __init__(self):
        """초기화"""
        self.alert_rules: Dict[str, AlertRule] = {}
        self.alerts: Dict[str, PerformanceAlert] = {}
        self.notifications: List[AlertNotification] = []
        self.alert_history: List[PerformanceAlert] = []

        # 알림 설정
        self.alert_config = {
            "max_alerts": 1000,
            "alert_retention_period": timedelta(days=30),
            "notification_retry_interval": timedelta(minutes=1),
            "max_notification_retries": 3,
            "default_cooldown": timedelta(minutes=5),
        }

        # 성능 메트릭
        self.performance_metrics = {
            "total_alerts_generated": 0,
            "total_notifications_sent": 0,
            "active_alerts": 0,
            "acknowledged_alerts": 0,
            "resolved_alerts": 0,
        }

        # 알림 핸들러
        self.alert_handlers: Dict[AlertChannel, Callable] = {}

        # 알림 큐
        self.alert_queue = asyncio.Queue()
        self.notification_queue = asyncio.Queue()

        logger.info("성능 알림 관리자 초기화 완료")

    async def add_alert_rule(
        self,
        rule_name: str,
        metric_name: str,
        condition: str,
        threshold: float,
        alert_level: AlertLevel,
        channels: List[AlertChannel] = None,
    ) -> str:
        """알림 규칙 추가"""
        try:
            rule_id = f"rule_{int(time.time())}_{uuid.uuid4().hex[:8]}"

            rule = AlertRule(
                rule_id=rule_id,
                rule_name=rule_name,
                metric_name=metric_name,
                condition=condition,
                threshold=threshold,
                alert_level=alert_level,
                channels=channels or [AlertChannel.LOG],
            )

            self.alert_rules[rule_id] = rule

            logger.info(f"알림 규칙 추가 완료: {rule_id} ({rule_name})")
            return rule_id

        except Exception as e:
            logger.error(f"알림 규칙 추가 실패: {e}")
            return ""

    async def remove_alert_rule(self, rule_id: str) -> bool:
        """알림 규칙 제거"""
        try:
            if rule_id in self.alert_rules:
                del self.alert_rules[rule_id]
                logger.info(f"알림 규칙 제거 완료: {rule_id}")
                return True
            else:
                logger.warning(f"알림 규칙을 찾을 수 없음: {rule_id}")
                return False

        except Exception as e:
            logger.error(f"알림 규칙 제거 실패: {e}")
            return False

    async def check_alert_conditions(
        self, metric_name: str, current_value: float
    ) -> List[PerformanceAlert]:
        """알림 조건 확인"""
        try:
            triggered_alerts = []

            for rule in self.alert_rules.values():
                if not rule.enabled or rule.metric_name != metric_name:
                    continue

                # 쿨다운 확인
                if await self._is_in_cooldown(rule.rule_id):
                    continue

                # 조건 확인
                if await self._evaluate_condition(
                    current_value, rule.condition, rule.threshold
                ):
                    alert = await self._create_alert(rule, current_value)
                    if alert:
                        triggered_alerts.append(alert)
                        await self.alert_queue.put(alert)

            return triggered_alerts

        except Exception as e:
            logger.error(f"알림 조건 확인 실패: {e}")
            return []

    async def _evaluate_condition(
        self, current_value: float, condition: str, threshold: float
    ) -> bool:
        """조건 평가"""
        try:
            if condition == ">":
                return current_value > threshold
            elif condition == "<":
                return current_value < threshold
            elif condition == ">=":
                return current_value >= threshold
            elif condition == "<=":
                return current_value <= threshold
            elif condition == "==":
                return abs(current_value - threshold) < 0.001
            elif condition == "!=":
                return abs(current_value - threshold) >= 0.001
            else:
                logger.warning(f"알 수 없는 조건: {condition}")
                return False

        except Exception as e:
            logger.error(f"조건 평가 실패: {e}")
            return False

    async def _create_alert(
        self, rule: AlertRule, current_value: float
    ) -> Optional[PerformanceAlert]:
        """알림 생성"""
        try:
            alert_id = f"alert_{int(time.time())}_{uuid.uuid4().hex[:8]}"

            alert_message = f"{rule.metric_name}이(가) {rule.condition} {rule.threshold} 조건을 만족했습니다. (현재값: {current_value})"

            alert = PerformanceAlert(
                alert_id=alert_id,
                rule_id=rule.rule_id,
                alert_level=rule.alert_level,
                alert_message=alert_message,
                metric_name=rule.metric_name,
                current_value=current_value,
                threshold=rule.threshold,
            )

            self.alerts[alert_id] = alert
            self.alert_history.append(alert)
            self.performance_metrics["total_alerts_generated"] += 1
            self.performance_metrics["active_alerts"] += 1

            logger.info(f"알림 생성 완료: {alert_id} ({rule.alert_level.value})")
            return alert

        except Exception as e:
            logger.error(f"알림 생성 실패: {e}")
            return None

    async def acknowledge_alert(self, alert_id: str, acknowledged_by: str) -> bool:
        """알림 승인"""
        try:
            if alert_id in self.alerts:
                alert = self.alerts[alert_id]
                alert.status = AlertStatus.ACKNOWLEDGED
                alert.acknowledged_by = acknowledged_by
                alert.acknowledged_at = datetime.now()

                self.performance_metrics["active_alerts"] -= 1
                self.performance_metrics["acknowledged_alerts"] += 1

                logger.info(f"알림 승인 완료: {alert_id} (승인자: {acknowledged_by})")
                return True
            else:
                logger.warning(f"알림을 찾을 수 없음: {alert_id}")
                return False

        except Exception as e:
            logger.error(f"알림 승인 실패: {e}")
            return False

    async def resolve_alert(self, alert_id: str, resolved_by: str) -> bool:
        """알림 해결"""
        try:
            if alert_id in self.alerts:
                alert = self.alerts[alert_id]
                alert.status = AlertStatus.RESOLVED
                alert.resolved_by = resolved_by
                alert.resolved_at = datetime.now()

                self.performance_metrics["acknowledged_alerts"] -= 1
                self.performance_metrics["resolved_alerts"] += 1

                logger.info(f"알림 해결 완료: {alert_id} (해결자: {resolved_by})")
                return True
            else:
                logger.warning(f"알림을 찾을 수 없음: {alert_id}")
                return False

        except Exception as e:
            logger.error(f"알림 해결 실패: {e}")
            return False

    async def send_notification(
        self, alert: PerformanceAlert, channel: AlertChannel
    ) -> bool:
        """알림 전송"""
        try:
            notification_id = f"notif_{int(time.time())}_{uuid.uuid4().hex[:8]}"

            # 알림 메시지 생성
            message = await self._format_alert_message(alert, channel)

            notification = AlertNotification(
                notification_id=notification_id,
                alert_id=alert.alert_id,
                channel=channel,
                message=message,
                max_retries=self.alert_config["max_notification_retries"],
            )

            self.notifications.append(notification)

            # 알림 핸들러 호출
            if channel in self.alert_handlers:
                try:
                    await self.alert_handlers[channel](notification)
                    notification.status = "sent"
                    self.performance_metrics["total_notifications_sent"] += 1
                    logger.info(f"알림 전송 완료: {notification_id} ({channel.value})")
                    return True
                except Exception as e:
                    notification.status = "failed"
                    logger.error(f"알림 전송 실패: {notification_id} - {e}")
                    return False
            else:
                # 기본 로그 핸들러
                logger.warning(f"알림 핸들러가 없음: {channel.value} - {message}")
                notification.status = "sent"
                return True

        except Exception as e:
            logger.error(f"알림 전송 실패: {e}")
            return False

    async def _format_alert_message(
        self, alert: PerformanceAlert, channel: AlertChannel
    ) -> str:
        """알림 메시지 포맷"""
        try:
            if channel == AlertChannel.LOG:
                return f"[{alert.alert_level.value.upper()}] {alert.alert_message}"
            elif channel == AlertChannel.EMAIL:
                return f"""
                성능 알림 - {alert.alert_level.value.upper()}

                메트릭: {alert.metric_name}
                현재값: {alert.current_value}
                임계값: {alert.threshold}
                메시지: {alert.alert_message}
                시간: {alert.timestamp.isoformat()}
                """
            else:
                return alert.alert_message

        except Exception as e:
            logger.error(f"알림 메시지 포맷 실패: {e}")
            return alert.alert_message

    async def _is_in_cooldown(self, rule_id: str) -> bool:
        """쿨다운 확인"""
        try:
            rule = self.alert_rules.get(rule_id)
            if not rule:
                return False

            # 최근 알림 확인
            recent_alerts = [
                a
                for a in self.alert_history
                if a.rule_id == rule_id
                and a.timestamp > datetime.now() - rule.cooldown_period
            ]

            return len(recent_alerts) > 0

        except Exception as e:
            logger.error(f"쿨다운 확인 실패: {e}")
            return False

    async def register_alert_handler(
        self, channel: AlertChannel, handler: Callable
    ) -> bool:
        """알림 핸들러 등록"""
        try:
            self.alert_handlers[channel] = handler
            logger.info(f"알림 핸들러 등록 완료: {channel.value}")
            return True

        except Exception as e:
            logger.error(f"알림 핸들러 등록 실패: {e}")
            return False

    async def get_active_alerts(self) -> List[PerformanceAlert]:
        """활성 알림 조회"""
        try:
            return [
                alert
                for alert in self.alerts.values()
                if alert.status == AlertStatus.ACTIVE
            ]

        except Exception as e:
            logger.error(f"활성 알림 조회 실패: {e}")
            return []

    async def get_alert_statistics(self) -> Dict[str, Any]:
        """알림 통계 조회"""
        try:
            stats = {
                "total_alerts": len(self.alerts),
                "active_alerts": len(
                    [a for a in self.alerts.values() if a.status == AlertStatus.ACTIVE]
                ),
                "acknowledged_alerts": len(
                    [
                        a
                        for a in self.alerts.values()
                        if a.status == AlertStatus.ACKNOWLEDGED
                    ]
                ),
                "resolved_alerts": len(
                    [
                        a
                        for a in self.alerts.values()
                        if a.status == AlertStatus.RESOLVED
                    ]
                ),
                "total_rules": len(self.alert_rules),
                "enabled_rules": len(
                    [r for r in self.alert_rules.values() if r.enabled]
                ),
                "performance_metrics": self.performance_metrics.copy(),
            }

            return stats

        except Exception as e:
            logger.error(f"알림 통계 조회 실패: {e}")
            return {}

    async def cleanup_expired_alerts(self) -> int:
        """만료된 알림 정리"""
        try:
            current_time = datetime.now()
            cutoff_time = current_time - self.alert_config["alert_retention_period"]

            expired_count = 0
            expired_alerts = []

            for alert_id, alert in self.alerts.items():
                if alert.timestamp < cutoff_time:
                    expired_alerts.append(alert_id)
                    alert.status = AlertStatus.EXPIRED
                    expired_count += 1

            # 만료된 알림 제거
            for alert_id in expired_alerts:
                del self.alerts[alert_id]

            logger.info(f"만료된 알림 정리 완료: {expired_count}개")
            return expired_count

        except Exception as e:
            logger.error(f"만료된 알림 정리 실패: {e}")
            return 0
