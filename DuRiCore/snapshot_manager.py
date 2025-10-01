#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DuRi 리팩토링 Phase 1 - 스냅샷 관리 시스템

시스템 상태를 스냅샷으로 저장하고 복구하는 기능을 제공합니다.
- 시스템 상태 저장/로드
- 스냅샷 목록 관리
- 자동 정리 기능
"""

from dataclasses import asdict, dataclass, field
from datetime import datetime, timedelta
import hashlib
import json
import logging
import os
from pathlib import Path
import shutil
import time
from typing import Any, Dict, List, Optional

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class SnapshotInfo:
    """스냅샷 정보"""

    name: str
    timestamp: datetime
    size: int
    description: str = ""
    tags: List[str] = field(default_factory=list)
    checksum: str = ""


@dataclass
class SnapshotData:
    """스냅샷 데이터"""

    snapshot_info: SnapshotInfo
    system_state: Dict[str, Any]
    performance_metrics: Dict[str, Any]
    error_logs: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)


class SnapshotManager:
    """스냅샷 관리 시스템"""

    def __init__(self, snapshot_dir: str = "snapshots"):
        self.snapshot_dir = Path(snapshot_dir)
        self.snapshot_dir.mkdir(exist_ok=True)
        self.snapshots_file = self.snapshot_dir / "snapshots.json"
        self.snapshots: Dict[str, SnapshotInfo] = {}
        self._load_snapshots()

        logger.info(f"스냅샷 관리 시스템 초기화 완료: {self.snapshot_dir}")

    def _load_snapshots(self):
        """저장된 스냅샷 목록 로드"""
        if self.snapshots_file.exists():
            try:
                with open(self.snapshots_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    for snapshot_data in data.get("snapshots", []):
                        snapshot_info = SnapshotInfo(
                            name=snapshot_data["name"],
                            timestamp=datetime.fromisoformat(
                                snapshot_data["timestamp"]
                            ),
                            size=snapshot_data["size"],
                            description=snapshot_data.get("description", ""),
                            tags=snapshot_data.get("tags", []),
                            checksum=snapshot_data.get("checksum", ""),
                        )
                        self.snapshots[snapshot_info.name] = snapshot_info
                logger.info(f"스냅샷 목록 로드 완료: {len(self.snapshots)}개")
            except Exception as e:
                logger.error(f"스냅샷 목록 로드 실패: {e}")

    def _save_snapshots(self):
        """스냅샷 목록 저장"""
        try:
            data = {
                "snapshots": [
                    {
                        "name": info.name,
                        "timestamp": info.timestamp.isoformat(),
                        "size": info.size,
                        "description": info.description,
                        "tags": info.tags,
                        "checksum": info.checksum,
                    }
                    for info in self.snapshots.values()
                ]
            }
            with open(self.snapshots_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            logger.info("스냅샷 목록 저장 완료")
        except Exception as e:
            logger.error(f"스냅샷 목록 저장 실패: {e}")

    def save_snapshot(
        self,
        name: str,
        data: Dict[str, Any],
        description: str = "",
        tags: List[str] = None,
    ) -> bool:
        """스냅샷 저장"""
        try:
            # 스냅샷 데이터 생성
            snapshot_data = SnapshotData(
                snapshot_info=SnapshotInfo(
                    name=name,
                    timestamp=datetime.now(),
                    size=0,
                    description=description,
                    tags=tags or [],
                ),
                system_state=data.get("system_state", {}),
                performance_metrics=data.get("performance_metrics", {}),
                error_logs=data.get("error_logs", []),
            )

            # 파일로 저장
            snapshot_file = self.snapshot_dir / f"{name}.json"
            snapshot_data_dict = asdict(snapshot_data)
            snapshot_data_dict["snapshot_info"][
                "timestamp"
            ] = snapshot_data.snapshot_info.timestamp.isoformat()
            snapshot_data_dict["created_at"] = snapshot_data.created_at.isoformat()

            with open(snapshot_file, "w", encoding="utf-8") as f:
                json.dump(snapshot_data_dict, f, indent=2, ensure_ascii=False)

            # 스냅샷 정보 업데이트
            snapshot_data.snapshot_info.size = snapshot_file.stat().st_size
            snapshot_data.snapshot_info.checksum = self._calculate_checksum(
                snapshot_file
            )

            self.snapshots[name] = snapshot_data.snapshot_info
            self._save_snapshots()

            logger.info(
                f"스냅샷 저장 완료: {name} ({snapshot_data.snapshot_info.size} bytes)"
            )
            return True

        except Exception as e:
            logger.error(f"스냅샷 저장 실패: {e}")
            return False

    def load_snapshot(self, name: str) -> Optional[Dict[str, Any]]:
        """스냅샷 로드"""
        try:
            snapshot_file = self.snapshot_dir / f"{name}.json"
            if not snapshot_file.exists():
                logger.error(f"스냅샷 파일이 존재하지 않음: {name}")
                return None

            with open(snapshot_file, "r", encoding="utf-8") as f:
                data = json.load(f)

            # 체크섬 검증
            if self.snapshots.get(name):
                expected_checksum = self.snapshots[name].checksum
                actual_checksum = self._calculate_checksum(snapshot_file)
                if expected_checksum != actual_checksum:
                    logger.warning(f"스냅샷 체크섬 불일치: {name}")

            logger.info(f"스냅샷 로드 완료: {name}")
            return data

        except Exception as e:
            logger.error(f"스냅샷 로드 실패: {e}")
            return None

    def list_snapshots(self) -> List[SnapshotInfo]:
        """스냅샷 목록 반환"""
        return list(self.snapshots.values())

    def delete_snapshot(self, name: str) -> bool:
        """스냅샷 삭제"""
        try:
            snapshot_file = self.snapshot_dir / f"{name}.json"
            if snapshot_file.exists():
                snapshot_file.unlink()

            if name in self.snapshots:
                del self.snapshots[name]
                self._save_snapshots()

            logger.info(f"스냅샷 삭제 완료: {name}")
            return True

        except Exception as e:
            logger.error(f"스냅샷 삭제 실패: {e}")
            return False

    def cleanup_old_snapshots(self, keep_count: int = 10) -> int:
        """오래된 스냅샷 정리"""
        try:
            # 시간순으로 정렬
            sorted_snapshots = sorted(
                self.snapshots.values(), key=lambda x: x.timestamp, reverse=True
            )

            # 삭제할 스냅샷 찾기
            snapshots_to_delete = sorted_snapshots[keep_count:]

            deleted_count = 0
            for snapshot in snapshots_to_delete:
                if self.delete_snapshot(snapshot.name):
                    deleted_count += 1

            logger.info(f"오래된 스냅샷 정리 완료: {deleted_count}개 삭제")
            return deleted_count

        except Exception as e:
            logger.error(f"스냅샷 정리 실패: {e}")
            return 0

    def _calculate_checksum(self, file_path: Path) -> str:
        """파일 체크섬 계산"""
        try:
            with open(file_path, "rb") as f:
                content = f.read()
                return hashlib.md5(content).hexdigest()
        except Exception:
            return ""

    def get_snapshot_info(self, name: str) -> Optional[SnapshotInfo]:
        """스냅샷 정보 반환"""
        return self.snapshots.get(name)

    def search_snapshots(
        self, tags: List[str] = None, description: str = ""
    ) -> List[SnapshotInfo]:
        """스냅샷 검색"""
        results = []

        for snapshot in self.snapshots.values():
            # 태그 검색
            if tags:
                if not any(tag in snapshot.tags for tag in tags):
                    continue

            # 설명 검색
            if description:
                if description.lower() not in snapshot.description.lower():
                    continue

            results.append(snapshot)

        return results

    def get_system_status(self) -> Dict[str, Any]:
        """시스템 상태 반환"""
        return {
            "snapshot_dir": str(self.snapshot_dir),
            "total_snapshots": len(self.snapshots),
            "total_size": sum(s.size for s in self.snapshots.values()),
            "oldest_snapshot": (
                min(s.timestamp for s in self.snapshots.values())
                if self.snapshots
                else None
            ),
            "newest_snapshot": (
                max(s.timestamp for s in self.snapshots.values())
                if self.snapshots
                else None
            ),
        }


# 전역 스냅샷 매니저 인스턴스
snapshot_manager = SnapshotManager()


def save_system_snapshot(
    name: str,
    system_data: Dict[str, Any],
    description: str = "",
    tags: List[str] = None,
) -> bool:
    """시스템 스냅샷 저장 (편의 함수)"""
    return snapshot_manager.save_snapshot(name, system_data, description, tags)


def load_system_snapshot(name: str) -> Optional[Dict[str, Any]]:
    """시스템 스냅샷 로드 (편의 함수)"""
    return snapshot_manager.load_snapshot(name)


def list_system_snapshots() -> List[SnapshotInfo]:
    """시스템 스냅샷 목록 (편의 함수)"""
    return snapshot_manager.list_snapshots()
