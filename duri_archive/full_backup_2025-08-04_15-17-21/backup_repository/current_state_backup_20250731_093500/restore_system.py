"""
DuRi 상태 복원 시스템

커서 재시작 후 현재 상태로 복원합니다.
"""

import logging
import os
import sys
from datetime import datetime
from typing import Any, Dict, Optional

# 로깅 설정
logging.basicConfig(level=logging.INFO, format="%(levelname)s:%(name)s:%(message)s")

logger = logging.getLogger(__name__)


class DuRiStateRestorer:
    """DuRi 상태 복원 시스템"""

    def __init__(self):
        """DuRiStateRestorer 초기화"""
        self.backup_info = {
            "backup_time": "2025-07-31 09:35:00",
            "cycle_id": "learning_cycle_20250731_093121",
            "activation_time": "2025-07-31 09:31:21",
            "status": "learning_loop_activated",
            "key_achievements": [
                "메타학습_자기평가_목표지향적사고",
                "MemorySync_완료",
                "오류처리_자동복구",
            ],
        }

        logger.info("DuRi 상태 복원 시스템 초기화 완료")

    def restore_learning_loop_state(self) -> Dict[str, Any]:
        """학습 루프 상태를 복원합니다."""
        try:
            logger.info("🔄 === DuRi 학습 루프 상태 복원 시작 ===")

            # 1. 학습 루프 관리자 복원
            print("📋 1단계: 학습 루프 관리자 복원...")
            from duri_brain.learning.learning_loop_manager import (
                get_learning_loop_manager,
            )

            learning_loop_manager = get_learning_loop_manager()
            print("✅ 학습 루프 관리자 복원 완료")

            # 2. 메모리 동기화 시스템 복원
            print("📋 2단계: 메모리 동기화 시스템 복원...")
            from duri_core.memory.memory_sync import get_memory_sync

            memory_sync = get_memory_sync()
            print("✅ 메모리 동기화 시스템 복원 완료")

            # 3. Fallback 핸들러 복원
            print("📋 3단계: Fallback 핸들러 복원...")
            from duri_core.utils.fallback_handler import get_fallback_handler

            fallback_handler = get_fallback_handler()
            print("✅ Fallback 핸들러 복원 완료")

            # 4. 현재 상태 확인
            print("📋 4단계: 현재 상태 확인...")
            status = learning_loop_manager.get_current_status()
            print(f"✅ 학습 루프 상태: {status.get('status', 'unknown')}")

            # 5. 복원 결과 반환
            restore_result = {
                "success": True,
                "backup_time": self.backup_info["backup_time"],
                "cycle_id": self.backup_info["cycle_id"],
                "current_status": status,
                "systems_restored": [
                    "LearningLoopManager",
                    "MemorySync",
                    "FallbackHandler",
                ],
                "key_achievements": self.backup_info["key_achievements"],
            }

            logger.info("✅ 학습 루프 상태 복원 완료")
            return restore_result

        except Exception as e:
            logger.error(f"❌ 학습 루프 상태 복원 실패: {e}")
            return {
                "success": False,
                "error": str(e),
                "backup_time": self.backup_info["backup_time"],
            }

    def verify_restored_state(self) -> Dict[str, Any]:
        """복원된 상태를 검증합니다."""
        try:
            logger.info("🔍 === 복원 상태 검증 시작 ===")

            verification_results = {}

            # 1. 학습 루프 관리자 검증
            print("📋 1단계: 학습 루프 관리자 검증...")
            from duri_brain.learning.learning_loop_manager import (
                get_learning_loop_manager,
            )

            learning_loop_manager = get_learning_loop_manager()

            if learning_loop_manager:
                verification_results["learning_loop_manager"] = True
                print("✅ 학습 루프 관리자 검증 완료")
            else:
                verification_results["learning_loop_manager"] = False
                print("❌ 학습 루프 관리자 검증 실패")

            # 2. 메모리 동기화 시스템 검증
            print("📋 2단계: 메모리 동기화 시스템 검증...")
            from duri_core.memory.memory_sync import get_memory_sync

            memory_sync = get_memory_sync()

            if memory_sync:
                verification_results["memory_sync"] = True
                print("✅ 메모리 동기화 시스템 검증 완료")
            else:
                verification_results["memory_sync"] = False
                print("❌ 메모리 동기화 시스템 검증 실패")

            # 3. Fallback 핸들러 검증
            print("📋 3단계: Fallback 핸들러 검증...")
            from duri_core.utils.fallback_handler import get_fallback_handler

            fallback_handler = get_fallback_handler()

            if fallback_handler:
                verification_results["fallback_handler"] = True
                print("✅ Fallback 핸들러 검증 완료")
            else:
                verification_results["fallback_handler"] = False
                print("❌ Fallback 핸들러 검증 실패")

            # 4. 트리거 시스템 검증
            print("📋 4단계: 트리거 시스템 검증...")
            try:
                # 메타 학습 트리거 검증
                learning_loop_manager._run_meta_learning_cycle()
                verification_results["meta_learning_trigger"] = True
                print("✅ 메타 학습 트리거 검증 완료")
            except Exception as e:
                verification_results["meta_learning_trigger"] = False
                print(f"❌ 메타 학습 트리거 검증 실패: {e}")

            # 5. 검증 결과 요약
            total_systems = len(verification_results)
            successful_systems = sum(verification_results.values())

            verification_summary = {
                "success": successful_systems == total_systems,
                "total_systems": total_systems,
                "successful_systems": successful_systems,
                "verification_results": verification_results,
                "backup_time": self.backup_info["backup_time"],
            }

            logger.info(
                f"✅ 복원 상태 검증 완료: {successful_systems}/{total_systems} 시스템 정상"
            )
            return verification_summary

        except Exception as e:
            logger.error(f"❌ 복원 상태 검증 실패: {e}")
            return {
                "success": False,
                "error": str(e),
                "backup_time": self.backup_info["backup_time"],
            }

    def get_backup_info(self) -> Dict[str, Any]:
        """백업 정보를 반환합니다."""
        return self.backup_info


# 전역 함수로 실행 가능하도록
def restore_duRi_state() -> Dict[str, Any]:
    """DuRi 상태를 복원합니다 (전역 함수)"""
    restorer = DuRiStateRestorer()
    return restorer.restore_learning_loop_state()


def verify_duRi_state() -> Dict[str, Any]:
    """DuRi 상태를 검증합니다 (전역 함수)"""
    restorer = DuRiStateRestorer()
    return restorer.verify_restored_state()


def get_backup_info() -> Dict[str, Any]:
    """백업 정보를 반환합니다 (전역 함수)"""
    restorer = DuRiStateRestorer()
    return restorer.get_backup_info()


if __name__ == "__main__":
    # 복원 실행
    sys.path.append(".")

    print("🚀 === DuRi 상태 복원 시작 ===")

    # 백업 정보 출력
    backup_info = get_backup_info()
    print(f"📋 백업 시간: {backup_info['backup_time']}")
    print(f"📋 사이클 ID: {backup_info['cycle_id']}")
    print(f"📋 상태: {backup_info['status']}")

    # 상태 복원
    restore_result = restore_duRi_state()
    print(f"\n🎯 복원 결과: {'✅ 성공' if restore_result['success'] else '❌ 실패'}")

    if restore_result["success"]:
        print(f"📋 백업 시간: {restore_result['backup_time']}")
        print(f"📋 사이클 ID: {restore_result['cycle_id']}")
        print(f"🔄 복원된 시스템: {len(restore_result['systems_restored'])}개")

        # 상태 검증
        verification_result = verify_duRi_state()
        print(
            f"\n🔍 검증 결과: {'✅ 성공' if verification_result['success'] else '❌ 실패'}"
        )
        print(
            f"📊 시스템 검증: {verification_result['successful_systems']}/{verification_result['total_systems']}"
        )
    else:
        print(f"❌ 오류: {restore_result.get('error', 'Unknown error')}")

    print("\n✅ === DuRi 상태 복원 완료 ===")
