#!/usr/bin/env python3
"""
DuRi 주기적 무결성 검증 시스템
"""

import asyncio
import time
from typing import Dict, Any
from DuRiCore.deployment.deployment_integrity import deployment_integrity
from DuRiCore.global_logging_manager import get_duri_logger, log_system_event

logger = get_duri_logger("periodic_verification")

class PeriodicVerification:
    """주기적 무결성 검증 클래스"""
    
    def __init__(self, interval_hours: float = 1.0):
        self.interval_hours = interval_hours
        self.interval_seconds = interval_hours * 3600
        self.is_running = False
        self.verification_count = 0
        self.last_verification = None
        self.last_result = None
        
    async def start_verification_loop(self):
        """검증 루프 시작"""
        if self.is_running:
            logger.warning("검증 루프가 이미 실행 중입니다")
            return
        
        self.is_running = True
        logger.info(f"주기적 무결성 검증 시작 (간격: {self.interval_hours}시간)")
        
        # 앱 시작 시 즉시 1회 검증
        await self.run_verification("startup")
        
        # 주기적 검증 루프
        while self.is_running:
            try:
                await asyncio.sleep(self.interval_seconds)
                if self.is_running:  # 종료 신호 확인
                    await self.run_verification("periodic")
            except asyncio.CancelledError:
                logger.info("검증 루프 취소됨")
                break
            except Exception as e:
                logger.error(f"검증 루프 오류: {e}")
                await asyncio.sleep(60)  # 오류 시 1분 대기 후 재시도
    
    def stop_verification_loop(self):
        """검증 루프 중지"""
        self.is_running = False
        logger.info("주기적 무결성 검증 중지")
    
    async def run_verification(self, trigger: str = "manual") -> Dict[str, Any]:
        """무결성 검증 실행"""
        try:
            logger.info(f"무결성 검증 시작 (트리거: {trigger})")
            
            # 무결성 검증 실행
            result = deployment_integrity.verify_integrity()
            
            # 결과 기록
            self.verification_count += 1
            self.last_verification = time.time()
            self.last_result = result
            
            # 검증 결과 로깅
            if result.get("integrity_verified", False):
                logger.info(f"무결성 검증 통과 (트리거: {trigger})")
                log_system_event(
                    "INTEGRITY_VERIFICATION", 
                    f"무결성 검증 통과 - {result['summary']}", 
                    "INFO",
                    deploy_id=result.get("deployment_id"),
                    cycle_id=f"VERIFY_{int(time.time())}"
                )
            else:
                logger.error(f"무결성 검증 실패 (트리거: {trigger})")
                log_system_event(
                    "INTEGRITY_VERIFICATION", 
                    f"무결성 검증 실패 - {result['summary']}", 
                    "ERROR",
                    deploy_id=result.get("deployment_id"),
                    cycle_id=f"VERIFY_{int(time.time())}"
                )
                
                # 실패 시 알람 발송 (Slack/Email 연동)
                await self.send_alert(result, trigger)
            
            return result
            
        except Exception as e:
            logger.error(f"무결성 검증 실행 실패: {e}")
            log_system_event(
                "INTEGRITY_VERIFICATION", 
                f"무결성 검증 실행 실패: {e}", 
                "ERROR",
                cycle_id=f"VERIFY_{int(time.time())}"
            )
            return {
                "status": "error",
                "message": f"검증 실행 실패: {e}",
                "integrity_verified": False
            }
    
    async def send_alert(self, result: Dict[str, Any], trigger: str):
        """무결성 검증 실패 시 알람 발송"""
        try:
            # 실제로는 Slack/Email API 호출
            # 여기서는 로그로 시뮬레이션
            
            alert_message = f"""
🚨 DuRi 무결성 검증 실패 알람

트리거: {trigger}
배포 ID: {result.get('deployment_id', 'unknown')}
상태: {result.get('status', 'unknown')}
요약: {result.get('summary', {})}

수정된 파일: {result.get('modified_files', [])}
누락된 파일: {result.get('missing_files', [])}

즉시 확인이 필요합니다.
"""
            
            logger.error(f"무결성 검증 실패 알람: {alert_message}")
            
            # 실제 구현 시:
            # await slack_client.send_message(alert_message)
            # await email_client.send_alert(alert_message)
            
        except Exception as e:
            logger.error(f"알람 발송 실패: {e}")
    
    def get_verification_stats(self) -> Dict[str, Any]:
        """검증 통계 반환"""
        return {
            "is_running": self.is_running,
            "interval_hours": self.interval_hours,
            "verification_count": self.verification_count,
            "last_verification": self.last_verification,
            "last_result": self.last_result
        }

# 전역 인스턴스
periodic_verification = PeriodicVerification()

# 편의 함수들
async def start_periodic_verification():
    """주기적 검증 시작"""
    await periodic_verification.start_verification_loop()

def stop_periodic_verification():
    """주기적 검증 중지"""
    periodic_verification.stop_verification_loop()

async def run_manual_verification():
    """수동 검증 실행"""
    return await periodic_verification.run_verification("manual")

def get_verification_stats():
    """검증 통계 반환"""
    return periodic_verification.get_verification_stats()
