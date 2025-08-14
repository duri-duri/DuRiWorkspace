import json
import logging
import requests
import smtplib
import uuid
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import psycopg2
from psycopg2.extras import RealDictCursor

from ..models.notify_model import (
    NotificationConfig, AlertMessage, NotificationRequest, 
    NotificationResponse, NotificationStatus, AlertLevel,
    NotificationType, ServiceStatus, ResourceType,
    DEFAULT_NOTIFICATION_CONFIG
)

logger = logging.getLogger(__name__)


class NotifyService:
    """알림 서비스"""
    
    def __init__(self, db_config: Dict[str, Any]):
        self.db_config = db_config
        self.config = DEFAULT_NOTIFICATION_CONFIG
        self.alert_history: List[AlertMessage] = []
        self.last_alert_time: Optional[datetime] = None
        self.alerts_this_hour = 0
        self.hour_start = datetime.now()
        self._init_notification_table()
        self._load_config()
    
    def _get_connection(self):
        """데이터베이스 연결 획득"""
        try:
            conn = psycopg2.connect(**self.db_config)
            return conn
        except Exception as e:
            logger.error(f"데이터베이스 연결 실패: {e}")
            raise
    
    def _init_notification_table(self):
        """알림 테이블 초기화"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # 알림 설정 테이블
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS notification_configs (
                    id SERIAL PRIMARY KEY,
                    config_data JSONB NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # 알림 히스토리 테이블
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS alert_history (
                    id VARCHAR(100) PRIMARY KEY,
                    timestamp TIMESTAMP NOT NULL,
                    level VARCHAR(20) NOT NULL,
                    title TEXT NOT NULL,
                    message TEXT NOT NULL,
                    service_name VARCHAR(100),
                    resource_type VARCHAR(20),
                    current_value FLOAT,
                    threshold_value FLOAT,
                    metadata JSONB,
                    sent_to JSONB,
                    failed_to JSONB
                )
            """)
            
            # 인덱스 생성
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_alert_history_timestamp 
                ON alert_history(timestamp DESC)
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_alert_history_level 
                ON alert_history(level, timestamp DESC)
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_alert_history_service 
                ON alert_history(service_name, timestamp DESC)
            """)
            
            conn.commit()
            cursor.close()
            conn.close()
            
            logger.info("알림 테이블 초기화 완료")
            
        except Exception as e:
            logger.error(f"알림 테이블 초기화 실패: {e}")
            raise
    
    def _load_config(self):
        """알림 설정 로드"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            
            cursor.execute("""
                SELECT config_data FROM notification_configs 
                ORDER BY updated_at DESC LIMIT 1
            """)
            
            result = cursor.fetchone()
            cursor.close()
            conn.close()
            
            if result:
                self.config = NotificationConfig(**result['config_data'])
                logger.info("알림 설정 로드 완료")
            else:
                logger.info("기본 알림 설정 사용")
                
        except Exception as e:
            logger.error(f"알림 설정 로드 실패: {e}")
    
    def update_config(self, new_config: NotificationConfig) -> bool:
        """알림 설정 업데이트"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO notification_configs (config_data, updated_at)
                VALUES (%s, %s)
            """, (
                json.dumps(new_config.dict()),
                datetime.now()
            ))
            
            conn.commit()
            cursor.close()
            conn.close()
            
            self.config = new_config
            logger.info("알림 설정 업데이트 완료")
            return True
            
        except Exception as e:
            logger.error(f"알림 설정 업데이트 실패: {e}")
            return False
    
    def send_notification(self, request: NotificationRequest) -> NotificationResponse:
        """알림 전송"""
        if not self.config.enabled:
            return NotificationResponse(
                success=False,
                message="알림이 비활성화되어 있습니다",
                sent_to=[],
                failed_to=[],
                timestamp=datetime.now()
            )
        
        # 쿨다운 체크
        if self._is_in_cooldown():
            return NotificationResponse(
                success=False,
                message="알림 쿨다운 기간입니다",
                sent_to=[],
                failed_to=[],
                timestamp=datetime.now()
            )
        
        # 시간당 알림 수 체크
        if self._is_rate_limited():
            return NotificationResponse(
                success=False,
                message="시간당 알림 수 제한에 도달했습니다",
                sent_to=[],
                failed_to=[],
                timestamp=datetime.now()
            )
        
        # 알림 메시지 생성
        alert_id = str(uuid.uuid4())
        alert_message = AlertMessage(
            id=alert_id,
            timestamp=datetime.now(),
            level=request.level,
            title=request.title,
            message=request.message,
            service_name=request.service_name,
            resource_type=request.resource_type,
            current_value=request.current_value,
            threshold_value=request.threshold_value,
            metadata=request.metadata
        )
        
        sent_to = []
        failed_to = []
        
        # 각 알림 타입별로 전송
        for notification_type in self.config.notification_types:
            try:
                if notification_type == NotificationType.SLACK:
                    if self._send_slack_notification(alert_message):
                        sent_to.append("slack")
                    else:
                        failed_to.append("slack")
                        
                elif notification_type == NotificationType.EMAIL:
                    if self._send_email_notification(alert_message):
                        sent_to.append("email")
                    else:
                        failed_to.append("email")
                        
                elif notification_type == NotificationType.LOG:
                    if self._send_log_notification(alert_message):
                        sent_to.append("log")
                    else:
                        failed_to.append("log")
                        
                elif notification_type == NotificationType.WEBHOOK:
                    if self._send_webhook_notification(alert_message):
                        sent_to.append("webhook")
                    else:
                        failed_to.append("webhook")
                        
            except Exception as e:
                logger.error(f"알림 전송 실패 ({notification_type}): {e}")
                failed_to.append(notification_type)
        
        # 알림 히스토리 저장
        self._save_alert_history(alert_message, sent_to, failed_to)
        
        # 알림 통계 업데이트
        self._update_alert_stats()
        
        success = len(sent_to) > 0
        message = f"알림 전송 완료: {len(sent_to)}개 성공, {len(failed_to)}개 실패"
        
        return NotificationResponse(
            success=success,
            message=message,
            sent_to=sent_to,
            failed_to=failed_to,
            timestamp=datetime.now()
        )
    
    def _send_slack_notification(self, alert: AlertMessage) -> bool:
        """Slack 알림 전송"""
        if not self.config.slack_webhook_url:
            return False
        
        try:
            # Slack 메시지 포맷
            color_map = {
                AlertLevel.INFO: "#36a64f",
                AlertLevel.WARNING: "#ffa500",
                AlertLevel.ERROR: "#ff0000",
                AlertLevel.CRITICAL: "#8b0000"
            }
            
            attachments = [{
                "color": color_map.get(alert.level, "#36a64f"),
                "title": alert.title,
                "text": alert.message,
                "fields": []
            }]
            
            if alert.service_name:
                attachments[0]["fields"].append({
                    "title": "서비스",
                    "value": alert.service_name,
                    "short": True
                })
            
            if alert.resource_type:
                attachments[0]["fields"].append({
                    "title": "리소스",
                    "value": alert.resource_type.value,
                    "short": True
                })
            
            if alert.current_value is not None:
                attachments[0]["fields"].append({
                    "title": "현재 값",
                    "value": f"{alert.current_value:.2f}%",
                    "short": True
                })
            
            if alert.threshold_value is not None:
                attachments[0]["fields"].append({
                    "title": "임계값",
                    "value": f"{alert.threshold_value:.2f}%",
                    "short": True
                })
            
            payload = {
                "channel": self.config.slack_channel,
                "username": self.config.slack_username,
                "attachments": attachments
            }
            
            response = requests.post(
                str(self.config.slack_webhook_url),
                json=payload,
                timeout=10
            )
            
            return response.status_code == 200
            
        except Exception as e:
            logger.error(f"Slack 알림 전송 실패: {e}")
            return False
    
    def _send_email_notification(self, alert: AlertMessage) -> bool:
        """이메일 알림 전송"""
        if not all([
            self.config.email_smtp_server,
            self.config.email_username,
            self.config.email_password,
            self.config.email_recipients
        ]):
            return False
        
        try:
            msg = MIMEMultipart()
            msg['From'] = self.config.email_from or self.config.email_username
            msg['To'] = ", ".join(self.config.email_recipients)
            msg['Subject'] = f"[DuRi Alert] {alert.title}"
            
            # 이메일 본문 생성
            body = f"""
            <html>
            <body>
                <h2>{alert.title}</h2>
                <p><strong>시간:</strong> {alert.timestamp.strftime('%Y-%m-%d %H:%M:%S')}</p>
                <p><strong>레벨:</strong> {alert.level.value.upper()}</p>
                <p><strong>메시지:</strong> {alert.message}</p>
            """
            
            if alert.service_name:
                body += f"<p><strong>서비스:</strong> {alert.service_name}</p>"
            
            if alert.resource_type:
                body += f"<p><strong>리소스:</strong> {alert.resource_type.value}</p>"
            
            if alert.current_value is not None:
                body += f"<p><strong>현재 값:</strong> {alert.current_value:.2f}%</p>"
            
            if alert.threshold_value is not None:
                body += f"<p><strong>임계값:</strong> {alert.threshold_value:.2f}%</p>"
            
            body += "</body></html>"
            
            msg.attach(MIMEText(body, 'html'))
            
            # SMTP 서버 연결 및 전송
            server = smtplib.SMTP(self.config.email_smtp_server, self.config.email_smtp_port)
            server.starttls()
            server.login(self.config.email_username, self.config.email_password)
            server.send_message(msg)
            server.quit()
            
            return True
            
        except Exception as e:
            logger.error(f"이메일 알림 전송 실패: {e}")
            return False
    
    def _send_log_notification(self, alert: AlertMessage) -> bool:
        """로그 알림 전송"""
        try:
            log_level_map = {
                AlertLevel.INFO: logging.INFO,
                AlertLevel.WARNING: logging.WARNING,
                AlertLevel.ERROR: logging.ERROR,
                AlertLevel.CRITICAL: logging.CRITICAL
            }
            
            log_level = log_level_map.get(alert.level, logging.INFO)
            
            logger.log(log_level, f"ALERT: {alert.title} - {alert.message}")
            
            return True
            
        except Exception as e:
            logger.error(f"로그 알림 전송 실패: {e}")
            return False
    
    def _send_webhook_notification(self, alert: AlertMessage) -> bool:
        """웹훅 알림 전송"""
        # 웹훅 URL이 설정되어 있지 않으면 스킵
        return False
    
    def _save_alert_history(self, alert: AlertMessage, sent_to: List[str], failed_to: List[str]):
        """알림 히스토리 저장"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO alert_history 
                (id, timestamp, level, title, message, service_name, 
                 resource_type, current_value, threshold_value, metadata, sent_to, failed_to)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                alert.id,
                alert.timestamp,
                alert.level.value,
                alert.title,
                alert.message,
                alert.service_name,
                alert.resource_type.value if alert.resource_type else None,
                alert.current_value,
                alert.threshold_value,
                json.dumps(alert.metadata),
                json.dumps(sent_to),
                json.dumps(failed_to)
            ))
            
            conn.commit()
            cursor.close()
            conn.close()
            
        except Exception as e:
            logger.error(f"알림 히스토리 저장 실패: {e}")
    
    def _is_in_cooldown(self) -> bool:
        """쿨다운 상태 확인"""
        if not self.last_alert_time:
            return False
        
        time_since_last = datetime.now() - self.last_alert_time
        return time_since_last.total_seconds() < self.config.alert_cooldown
    
    def _is_rate_limited(self) -> bool:
        """속도 제한 확인"""
        # 시간이 바뀌었으면 카운터 리셋
        current_hour = datetime.now().replace(minute=0, second=0, microsecond=0)
        if current_hour > self.hour_start:
            self.alerts_this_hour = 0
            self.hour_start = current_hour
        
        return self.alerts_this_hour >= self.config.max_alerts_per_hour
    
    def _update_alert_stats(self):
        """알림 통계 업데이트"""
        self.last_alert_time = datetime.now()
        self.alerts_this_hour += 1
    
    def get_status(self) -> NotificationStatus:
        """알림 상태 조회"""
        cooldown_remaining = None
        if self.last_alert_time:
            time_since_last = datetime.now() - self.last_alert_time
            remaining = self.config.alert_cooldown - time_since_last.total_seconds()
            cooldown_remaining = max(0, int(remaining))
        
        return NotificationStatus(
            enabled=self.config.enabled,
            active_config=self.config,
            total_alerts_sent=len(self.alert_history),
            alerts_last_hour=self.alerts_this_hour,
            last_alert_time=self.last_alert_time,
            cooldown_active=self._is_in_cooldown(),
            cooldown_remaining=cooldown_remaining
        )
    
    def check_service_status_change(self, service_name: str, previous_status: ServiceStatus, current_status: ServiceStatus):
        """서비스 상태 변화 감지"""
        if not self.config.service_status_alerts:
            return
        
        if previous_status == current_status:
            return
        
        # 상태가 악화된 경우에만 알림
        status_severity = {
            ServiceStatus.HEALTHY: 0,
            ServiceStatus.DEGRADED: 1,
            ServiceStatus.UNHEALTHY: 2,
            ServiceStatus.OFFLINE: 3
        }
        
        if status_severity[current_status] > status_severity[previous_status]:
            level = AlertLevel.ERROR if current_status in [ServiceStatus.UNHEALTHY, ServiceStatus.OFFLINE] else AlertLevel.WARNING
            
            request = NotificationRequest(
                level=level,
                title=f"서비스 상태 변화: {service_name}",
                message=f"서비스 {service_name}의 상태가 {previous_status.value}에서 {current_status.value}로 변경되었습니다.",
                service_name=service_name,
                metadata={
                    "previous_status": previous_status.value,
                    "current_status": current_status.value
                }
            )
            
            self.send_notification(request)
    
    def check_resource_threshold(self, resource_type: ResourceType, current_value: float, service_name: Optional[str] = None):
        """리소스 임계값 체크"""
        if not self.config.resource_alerts:
            return
        
        threshold_key = resource_type.value
        threshold_value = self.config.thresholds.get(threshold_key, 80.0)
        
        if current_value >= threshold_value:
            level = AlertLevel.CRITICAL if current_value >= threshold_value * 1.2 else AlertLevel.WARNING
            
            request = NotificationRequest(
                level=level,
                title=f"리소스 사용량 경고: {resource_type.value}",
                message=f"{resource_type.value} 사용량이 {current_value:.1f}%로 임계값 {threshold_value}%를 초과했습니다.",
                service_name=service_name,
                resource_type=resource_type,
                current_value=current_value,
                threshold_value=threshold_value
            )
            
            self.send_notification(request)


# 전역 알림 서비스 인스턴스
notify_service = None

def get_notify_service() -> NotifyService:
    """알림 서비스 인스턴스 반환"""
    global notify_service
    if notify_service is None:
        # 기본 DB 설정으로 초기화
        db_config = {
            'host': 'duri-postgres',
            'port': 5432,
            'database': 'duri',
            'user': 'duri',
            'password': 'duri'
        }
        notify_service = NotifyService(db_config)
    return notify_service 