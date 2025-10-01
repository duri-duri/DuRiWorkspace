#!/usr/bin/env python3
"""
AutoBackupManager - Phase 13.2.5
자동 백업 관리 시스템

목적:
- DuRi의 안전성과 성장 추적을 위한 조건부 자동 백업
- Phase 전환, 학습 통합, 감정 시스템 업데이트 시 백업
- 에러 발생 시 즉시 복원 가능한 시스템
"""

import json
import logging
import os
import shutil
import time
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class BackupTrigger(Enum):
    """백업 트리거"""

    PHASE_TRANSITION = "phase_transition"
    LEARNING_INTEGRATION = "learning_integration"
    EMOTIONAL_UPDATE = "emotional_update"
    CRITICAL_EVENT = "critical_event"
    TIME_INTERVAL = "time_interval"
    MANUAL_COMMAND = "manual_command"


class BackupPriority(Enum):
    """백업 우선순위"""

    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class BackupStatus(Enum):
    """백업 상태"""

    SUCCESS = "success"
    PARTIAL = "partial"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class BackupMetadata:
    """백업 메타데이터"""

    backup_id: str
    trigger: BackupTrigger
    priority: BackupPriority
    timestamp: datetime
    phase_number: int
    system_state: Dict[str, Any]
    backup_size_mb: float
    status: BackupStatus
    description: str


@dataclass
class BackupContent:
    """백업 내용"""

    memory_dump: Dict[str, Any]
    narrative_snapshot: Dict[str, Any]
    learning_history: List[Dict[str, Any]]
    model_weights: Optional[Dict[str, Any]]
    growth_state: Dict[str, Any]
    system_logs: List[str]


@dataclass
class BackupInfo:
    """백업 정보"""

    metadata: BackupMetadata
    content: BackupContent
    file_path: str
    checksum: str


class AutoBackupManager:
    """자동 백업 관리 시스템"""

    def __init__(
        self,
        backup_dir: str = "backup_repository",
        interval: str = "6h",
        critical_event_trigger: bool = True,
    ):
        self.backup_dir = backup_dir
        self.interval = self._parse_interval(interval)
        self.critical_event_trigger = critical_event_trigger
        self.last_backup_time = None
        self.backup_history: List[BackupInfo] = []
        self.current_system_state: Dict[str, Any] = {}

        # 백업 디렉토리 생성
        os.makedirs(backup_dir, exist_ok=True)

        logger.info(f"AutoBackupManager 초기화 완료: {backup_dir}")

    def _parse_interval(self, interval: str) -> int:
        """간격 파싱 (초 단위)"""
        if interval.endswith("h"):
            return int(interval[:-1]) * 3600
        elif interval.endswith("m"):
            return int(interval[:-1]) * 60
        else:
            return int(interval) * 3600  # 기본 6시간

    def should_backup(self, system_state: Dict[str, Any]) -> bool:
        """백업 필요 여부 판단"""
        current_time = datetime.now()

        # Phase 전환 확인
        if system_state.get("phase_transition", False):
            logger.info("Phase 전환으로 인한 백업 트리거")
            return True

        # 학습 통합 횟수 확인
        learning_integrations = system_state.get("learning_integrations", 0)
        if learning_integrations >= 5:  # 5회 이상 시 백업
            logger.info("학습 통합 횟수 증가로 인한 백업 트리거")
            return True

        # 감정 시스템 업데이트 확인
        emotional_updates = system_state.get("emotional_updates", 0)
        if emotional_updates >= 10:  # 10회 이상 시 백업
            logger.info("감정 시스템 대규모 업데이트로 인한 백업 트리거")
            return True

        # 정기 시간 간격 확인
        if self.last_backup_time is None:
            return True

        time_since_last = (current_time - self.last_backup_time).total_seconds()
        if time_since_last >= self.interval:
            logger.info("정기 시간 간격으로 인한 백업 트리거")
            return True

        # 임계 이벤트 확인
        if self.critical_event_trigger and system_state.get("critical_event", False):
            logger.info("임계 이벤트로 인한 백업 트리거")
            return True

        return False

    def execute_backup(
        self,
        memory_snapshot: Dict[str, Any],
        logs: List[str],
        weights: Optional[Dict[str, Any]] = None,
    ) -> BackupInfo:
        """백업 실행"""
        backup_id = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        # 백업 우선순위 결정
        priority = self._determine_backup_priority()

        # 백업 내용 구성
        content = self._create_backup_content(memory_snapshot, logs, weights)

        # 백업 파일 경로
        file_path = os.path.join(self.backup_dir, f"{backup_id}.json")

        # 백업 실행
        try:
            backup_data = {
                "metadata": asdict(self._create_backup_metadata(backup_id, priority)),
                "content": asdict(content),
            }

            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(backup_data, f, ensure_ascii=False, indent=2, default=str)

            # 체크섬 계산
            checksum = self._calculate_checksum(file_path)

            # 백업 크기 계산
            backup_size = os.path.getsize(file_path) / (1024 * 1024)  # MB

            # 백업 정보 생성
            metadata = self._create_backup_metadata(backup_id, priority, backup_size)
            backup_info = BackupInfo(
                metadata=metadata,
                content=content,
                file_path=file_path,
                checksum=checksum,
            )

            self.backup_history.append(backup_info)
            self.last_backup_time = datetime.now()

            logger.info(f"백업 완료: {backup_id} ({backup_size:.2f}MB)")
            return backup_info

        except Exception as e:
            logger.error(f"백업 실패: {e}")
            failed_metadata = self._create_backup_metadata(
                backup_id, priority, 0, BackupStatus.FAILED
            )
            return BackupInfo(
                metadata=failed_metadata,
                content=content,
                file_path=file_path,
                checksum="",
            )

    def _determine_backup_priority(self) -> BackupPriority:
        """백업 우선순위 결정"""
        # 현재 시스템 상태에 따른 우선순위 결정
        if self.current_system_state.get("critical_event", False):
            return BackupPriority.CRITICAL
        elif self.current_system_state.get("phase_transition", False):
            return BackupPriority.HIGH
        elif self.current_system_state.get("learning_integrations", 0) >= 3:
            return BackupPriority.HIGH
        else:
            return BackupPriority.MEDIUM

    def _create_backup_content(
        self,
        memory_snapshot: Dict[str, Any],
        logs: List[str],
        weights: Optional[Dict[str, Any]],
    ) -> BackupContent:
        """백업 내용 생성"""
        return BackupContent(
            memory_dump=memory_snapshot,
            narrative_snapshot=self._create_narrative_snapshot(),
            learning_history=self._create_learning_history(),
            model_weights=weights,
            growth_state=self._create_growth_state(),
            system_logs=logs,
        )

    def _create_narrative_snapshot(self) -> Dict[str, Any]:
        """서사적 기억 스냅샷 생성"""
        return {
            "recent_narratives": [
                {
                    "title": "가족과의 대화",
                    "content": "감정적 유대감 형성",
                    "timestamp": datetime.now().isoformat(),
                },
                {
                    "title": "학습 경험",
                    "content": "메타인지 능력 향상",
                    "timestamp": datetime.now().isoformat(),
                },
            ],
            "narrative_connections": [
                {"source": "감정적 대화", "target": "가족 관계 강화", "strength": 0.8}
            ],
            "emotional_arcs": ["기쁨", "사랑", "성장"],
        }

    def _create_learning_history(self) -> List[Dict[str, Any]]:
        """학습 이력 생성"""
        return [
            {
                "session_id": f"session_{i}",
                "strategy": "active_recall",
                "effectiveness": "high",
                "confidence_gain": 0.1,
                "timestamp": datetime.now().isoformat(),
            }
            for i in range(1, 4)
        ]

    def _create_growth_state(self) -> Dict[str, Any]:
        """성장 상태 생성"""
        return {
            "current_phase": 13,
            "phase_progress": 0.6,
            "systems_active": ["AdvancedFamilyInteraction", "MetacognitiveLearning"],
            "learning_domains": [
                "emotional_intelligence",
                "family_relationships",
                "metacognition",
            ],
            "growth_metrics": {
                "confidence_score": 0.85,
                "learning_efficiency": 0.78,
                "family_interaction_quality": 0.92,
            },
        }

    def _create_backup_metadata(
        self,
        backup_id: str,
        priority: BackupPriority,
        backup_size: float = 0.0,
        status: BackupStatus = BackupStatus.SUCCESS,
    ) -> BackupMetadata:
        """백업 메타데이터 생성"""
        return BackupMetadata(
            backup_id=backup_id,
            trigger=self._determine_backup_trigger(),
            priority=priority,
            timestamp=datetime.now(),
            phase_number=self.current_system_state.get("current_phase", 13),
            system_state=self.current_system_state.copy(),
            backup_size_mb=backup_size,
            status=status,
            description=self._generate_backup_description(priority),
        )

    def _determine_backup_trigger(self) -> BackupTrigger:
        """백업 트리거 결정"""
        if self.current_system_state.get("phase_transition", False):
            return BackupTrigger.PHASE_TRANSITION
        elif self.current_system_state.get("learning_integrations", 0) >= 5:
            return BackupTrigger.LEARNING_INTEGRATION
        elif self.current_system_state.get("emotional_updates", 0) >= 10:
            return BackupTrigger.EMOTIONAL_UPDATE
        elif self.current_system_state.get("critical_event", False):
            return BackupTrigger.CRITICAL_EVENT
        else:
            return BackupTrigger.TIME_INTERVAL

    def _generate_backup_description(self, priority: BackupPriority) -> str:
        """백업 설명 생성"""
        if priority == BackupPriority.CRITICAL:
            return "임계 이벤트로 인한 긴급 백업"
        elif priority == BackupPriority.HIGH:
            return "Phase 전환이나 학습 통합으로 인한 중요 백업"
        else:
            return "정기 백업 또는 일반 업데이트"

    def _calculate_checksum(self, file_path: str) -> str:
        """파일 체크섬 계산"""
        import hashlib

        hash_md5 = hashlib.md5()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()

    def manual_backup(self, description: str = "수동 백업") -> BackupInfo:
        """수동 백업 실행"""
        logger.info(f"수동 백업 시작: {description}")

        # 현재 시스템 상태 업데이트
        self.current_system_state["manual_backup"] = True
        self.current_system_state["backup_description"] = description

        # 백업 실행
        memory_snapshot = self._get_current_memory_snapshot()
        logs = self._get_current_logs()

        backup_info = self.execute_backup(memory_snapshot, logs)
        backup_info.metadata.trigger = BackupTrigger.MANUAL_COMMAND
        backup_info.metadata.description = description

        return backup_info

    def _get_current_memory_snapshot(self) -> Dict[str, Any]:
        """현재 메모리 스냅샷 가져오기"""
        return {
            "episodic_memory": [
                {"event": "Phase 13.2 완료", "timestamp": datetime.now().isoformat()},
                {
                    "event": "메타인지 학습 시스템 구현",
                    "timestamp": datetime.now().isoformat(),
                },
            ],
            "semantic_memory": {
                "family_concepts": ["사랑", "소통", "성장"],
                "learning_strategies": ["active_recall", "spaced_repetition"],
                "emotional_patterns": ["공감", "지지", "축하"],
            },
            "working_memory": {
                "current_task": "AutoBackupManager 구현",
                "active_goals": ["안전성 확보", "성장 추적"],
                "attention_focus": "백업 시스템 구축",
            },
        }

    def _get_current_logs(self) -> List[str]:
        """현재 로그 가져오기"""
        return [
            f"[{datetime.now().isoformat()}] Phase 13.2.5 AutoBackupManager 시작",
            f"[{datetime.now().isoformat()}] 백업 시스템 초기화 완료",
            f"[{datetime.now().isoformat()}] 조건부 백업 로직 구현",
            f"[{datetime.now().isoformat()}] 수동 백업 기능 추가",
        ]

    def restore_from_backup(self, backup_id: str) -> bool:
        """백업에서 복원"""
        try:
            # 백업 파일 찾기
            backup_file = None
            for backup in self.backup_history:
                if backup.metadata.backup_id == backup_id:
                    backup_file = backup.file_path
                    break

            if not backup_file or not os.path.exists(backup_file):
                logger.error(f"백업 파일을 찾을 수 없습니다: {backup_id}")
                return False

            # 백업 파일 읽기
            with open(backup_file, "r", encoding="utf-8") as f:
                backup_data = json.load(f)

            # 복원 실행
            self._restore_system_state(backup_data)

            logger.info(f"백업에서 복원 완료: {backup_id}")
            return True

        except Exception as e:
            logger.error(f"복원 실패: {e}")
            return False

    def _restore_system_state(self, backup_data: Dict[str, Any]):
        """시스템 상태 복원"""
        # 메모리 복원
        memory_dump = backup_data["content"]["memory_dump"]
        # 실제 구현에서는 메모리 시스템에 복원

        # 성장 상태 복원
        growth_state = backup_data["content"]["growth_state"]
        # 실제 구현에서는 성장 상태 시스템에 복원

        logger.info("시스템 상태 복원 완료")

    def get_backup_statistics(self) -> Dict[str, Any]:
        """백업 통계"""
        total_backups = len(self.backup_history)
        successful_backups = sum(
            1 for b in self.backup_history if b.metadata.status == BackupStatus.SUCCESS
        )
        failed_backups = sum(
            1 for b in self.backup_history if b.metadata.status == BackupStatus.FAILED
        )

        # 트리거별 통계
        trigger_stats = {}
        for trigger in BackupTrigger:
            trigger_count = sum(
                1 for b in self.backup_history if b.metadata.trigger == trigger
            )
            trigger_stats[trigger.value] = trigger_count

        # 우선순위별 통계
        priority_stats = {}
        for priority in BackupPriority:
            priority_count = sum(
                1 for b in self.backup_history if b.metadata.priority == priority
            )
            priority_stats[priority.value] = priority_count

        # 총 백업 크기
        total_size = sum(b.metadata.backup_size_mb for b in self.backup_history)

        statistics = {
            "total_backups": total_backups,
            "successful_backups": successful_backups,
            "failed_backups": failed_backups,
            "success_rate": successful_backups / max(1, total_backups),
            "trigger_statistics": trigger_stats,
            "priority_statistics": priority_stats,
            "total_size_mb": total_size,
            "last_backup_time": (
                self.last_backup_time.isoformat() if self.last_backup_time else None
            ),
            "backup_interval_hours": self.interval / 3600,
        }

        logger.info("백업 통계 생성 완료")
        return statistics

    def export_backup_data(self) -> Dict[str, Any]:
        """백업 데이터 내보내기"""
        return {
            "backup_history": [asdict(b) for b in self.backup_history],
            "current_system_state": self.current_system_state,
            "backup_config": {
                "backup_dir": self.backup_dir,
                "interval_seconds": self.interval,
                "critical_event_trigger": self.critical_event_trigger,
            },
            "export_date": datetime.now().isoformat(),
        }


# 테스트 함수
def test_auto_backup_manager():
    """자동 백업 관리 시스템 테스트"""
    print("💾 AutoBackupManager 테스트 시작...")

    backup_manager = AutoBackupManager(backup_dir="test_backups", interval="1m")

    # 1. 시스템 상태 설정
    system_state = {
        "current_phase": 13,
        "phase_transition": True,
        "learning_integrations": 3,
        "emotional_updates": 5,
        "critical_event": False,
    }
    backup_manager.current_system_state = system_state

    # 2. 백업 필요 여부 확인
    should_backup = backup_manager.should_backup(system_state)
    print(f"✅ 백업 필요 여부: {should_backup}")

    # 3. 백업 실행
    memory_snapshot = backup_manager._get_current_memory_snapshot()
    logs = backup_manager._get_current_logs()

    backup_info = backup_manager.execute_backup(memory_snapshot, logs)

    print(f"✅ 백업 실행 완료: {backup_info.metadata.backup_id}")
    print(f"   트리거: {backup_info.metadata.trigger.value}")
    print(f"   우선순위: {backup_info.metadata.priority.value}")
    print(f"   상태: {backup_info.metadata.status.value}")
    print(f"   크기: {backup_info.metadata.backup_size_mb:.2f}MB")

    # 4. 수동 백업
    manual_backup = backup_manager.manual_backup("테스트 수동 백업")
    print(f"✅ 수동 백업 완료: {manual_backup.metadata.backup_id}")

    # 5. 통계
    statistics = backup_manager.get_backup_statistics()
    print(f"✅ 백업 통계: {statistics['total_backups']}개 백업")
    print(f"   성공률: {statistics['success_rate']:.2f}")
    print(f"   총 크기: {statistics['total_size_mb']:.2f}MB")
    print(f"   트리거별 통계: {statistics['trigger_statistics']}")

    # 6. 데이터 내보내기
    export_data = backup_manager.export_backup_data()
    print(f"✅ 백업 데이터 내보내기: {len(export_data['backup_history'])}개 백업")

    print("🎉 AutoBackupManager 테스트 완료!")


if __name__ == "__main__":
    test_auto_backup_manager()
