"""
백업 관리자 모듈
ML 통합 과정의 데이터와 모델을 안전하게 백업하고 복원합니다.
"""

import os
import shutil
import json
import pickle
import hashlib
import time
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from pathlib import Path
import zipfile
import tarfile

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class BackupInfo:
    """백업 정보 데이터 클래스"""
    backup_id: str
    timestamp: float
    description: str
    size_bytes: int
    checksum: str
    backup_type: str
    metadata: Dict[str, Any]
    file_path: str

class BackupStrategy:
    """백업 전략 기본 클래스"""
    
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
    
    def should_backup(self, data: Any, context: Dict[str, Any]) -> bool:
        """백업 여부 결정 - 하위 클래스에서 구현"""
        raise NotImplementedError("하위 클래스에서 구현해야 합니다")
    
    def get_backup_priority(self, data: Any, context: Dict[str, Any]) -> int:
        """백업 우선순위 반환 - 하위 클래스에서 구현"""
        raise NotImplementedError("하위 클래스에서 구현해야 합니다")

class TimeBasedBackupStrategy(BackupStrategy):
    """시간 기반 백업 전략"""
    
    def __init__(self, interval_hours: int = 24, max_backups: int = 7):
        super().__init__("TimeBased", f"{interval_hours}시간마다 백업, 최대 {max_backups}개 유지")
        self.interval_hours = interval_hours
        self.max_backups = max_backups
    
    def should_backup(self, data: Any, context: Dict[str, Any]) -> bool:
        """시간 간격에 따른 백업 여부 결정"""
        last_backup_time = context.get('last_backup_time', 0)
        current_time = time.time()
        
        # 마지막 백업으로부터 지정된 시간이 지났는지 확인
        return (current_time - last_backup_time) >= (self.interval_hours * 3600)
    
    def get_backup_priority(self, data: Any, context: Dict[str, Any]) -> int:
        """백업 우선순위 반환 (낮을수록 높은 우선순위)"""
        last_backup_time = context.get('last_backup_time', 0)
        current_time = time.time()
        
        # 마지막 백업으로부터 지난 시간이 길수록 높은 우선순위
        hours_since_last = (current_time - last_backup_time) / 3600
        return int(hours_since_last / self.interval_hours)

class ChangeBasedBackupStrategy(BackupStrategy):
    """변경 기반 백업 전략"""
    
    def __init__(self, change_threshold: float = 0.1):
        super().__init__("ChangeBased", f"변경률 {change_threshold*100}% 이상일 때 백업")
        self.change_threshold = change_threshold
    
    def should_backup(self, data: Any, context: Dict[str, Any]) -> bool:
        """데이터 변경률에 따른 백업 여부 결정"""
        current_checksum = context.get('current_checksum', '')
        last_backup_checksum = context.get('last_backup_checksum', '')
        
        # 체크섬이 다르면 백업 필요
        return current_checksum != last_backup_checksum
    
    def get_backup_priority(self, data: Any, context: Dict[str, Any]) -> int:
        """백업 우선순위 반환"""
        current_checksum = context.get('current_checksum', '')
        last_backup_checksum = context.get('last_backup_checksum', '')
        
        if current_checksum != last_backup_checksum:
            return 1  # 변경이 있으면 높은 우선순위
        return 999  # 변경이 없으면 낮은 우선순위

class BackupManager:
    """백업 관리자 메인 클래스"""
    
    def __init__(self, backup_dir: str = "backups", max_storage_gb: float = 10.0):
        self.backup_dir = Path(backup_dir)
        self.max_storage_bytes = max_storage_gb * 1024 * 1024 * 1024  # GB to bytes
        
        # 백업 디렉토리 생성
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        
        # 백업 전략 등록
        self.backup_strategies: List[BackupStrategy] = [
            TimeBasedBackupStrategy(interval_hours=24, max_backups=7),
            ChangeBasedBackupStrategy(change_threshold=0.1)
        ]
        
        # 백업 히스토리
        self.backup_history: List[BackupInfo] = []
        self.backup_metadata_file = self.backup_dir / "backup_metadata.json"
        
        # 메타데이터 로드
        self._load_backup_metadata()
    
    def _load_backup_metadata(self):
        """백업 메타데이터 로드"""
        try:
            if self.backup_metadata_file.exists():
                with open(self.backup_metadata_file, 'r', encoding='utf-8') as f:
                    metadata = json.load(f)
                    self.backup_history = [
                        BackupInfo(**info) for info in metadata.get('backup_history', [])
                    ]
                logger.info(f"백업 메타데이터 로드 완료: {len(self.backup_history)}개 백업")
        except Exception as e:
            logger.warning(f"백업 메타데이터 로드 실패: {str(e)}")
            self.backup_history = []
    
    def _save_backup_metadata(self):
        """백업 메타데이터 저장"""
        try:
            metadata = {
                'backup_history': [
                    {
                        'backup_id': backup.backup_id,
                        'timestamp': backup.timestamp,
                        'description': backup.description,
                        'size_bytes': backup.size_bytes,
                        'checksum': backup.checksum,
                        'backup_type': backup.backup_type,
                        'metadata': backup.metadata,
                        'file_path': backup.file_path
                    }
                    for backup in self.backup_history
                ],
                'last_updated': time.time()
            }
            
            with open(self.backup_metadata_file, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, ensure_ascii=False, indent=2)
            
            logger.info("백업 메타데이터 저장 완료")
        
        except Exception as e:
            logger.error(f"백업 메타데이터 저장 실패: {str(e)}")
    
    def _generate_backup_id(self) -> str:
        """고유한 백업 ID 생성"""
        timestamp = int(time.time() * 1000)
        random_suffix = hashlib.md5(f"{timestamp}".encode()).hexdigest()[:8]
        return f"backup_{timestamp}_{random_suffix}"
    
    def _calculate_checksum(self, data: Any) -> str:
        """데이터 체크섬 계산"""
        if isinstance(data, (str, bytes)):
            content = data.encode() if isinstance(data, str) else data
        else:
            content = pickle.dumps(data)
        
        return hashlib.md5(content).hexdigest()
    
    def _get_file_size(self, file_path: str) -> int:
        """파일 크기 반환 (바이트)"""
        try:
            return os.path.getsize(file_path)
        except OSError:
            return 0
    
    def _compress_file(self, source_path: str, target_path: str) -> bool:
        """파일 압축"""
        try:
            if target_path.endswith('.zip'):
                with zipfile.ZipFile(target_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                    zipf.write(source_path, os.path.basename(source_path))
            elif target_path.endswith('.tar.gz'):
                with tarfile.open(target_path, 'w:gz') as tarf:
                    tarf.add(source_path, arcname=os.path.basename(source_path))
            else:
                # 압축하지 않고 복사
                shutil.copy2(source_path, target_path)
            
            return True
        
        except Exception as e:
            logger.error(f"파일 압축 실패: {str(e)}")
            return False
    
    def create_backup(self, data: Any, description: str = "", backup_type: str = "data", 
                      compress: bool = True, context: Dict[str, Any] = None) -> Optional[BackupInfo]:
        """백업 생성"""
        try:
            # 백업 전략 확인
            if context and not self._should_create_backup(data, context):
                logger.info("백업 전략에 따라 백업을 건너뜁니다")
                return None
            
            # 백업 ID 생성
            backup_id = self._generate_backup_id()
            
            # 백업 파일명 생성
            timestamp_str = datetime.fromtimestamp(time.time()).strftime("%Y%m%d_%H%M%S")
            backup_filename = f"{backup_id}_{timestamp_str}.pkl"
            
            if compress:
                backup_filename += ".gz"
            
            backup_path = self.backup_dir / backup_filename
            
            # 데이터 저장
            with open(backup_path, 'wb') as f:
                pickle.dump(data, f)
            
            # 압축 (필요한 경우)
            if compress and not backup_filename.endswith('.gz'):
                compressed_path = str(backup_path) + '.gz'
                if self._compress_file(str(backup_path), compressed_path):
                    os.remove(backup_path)  # 원본 파일 삭제
                    backup_path = Path(compressed_path)
                    backup_filename = backup_filename + '.gz'
            
            # 백업 정보 생성
            backup_info = BackupInfo(
                backup_id=backup_id,
                timestamp=time.time(),
                description=description,
                size_bytes=self._get_file_size(str(backup_path)),
                checksum=self._calculate_checksum(data),
                backup_type=backup_type,
                metadata=context or {},
                file_path=str(backup_path)
            )
            
            # 백업 히스토리에 추가
            self.backup_history.append(backup_info)
            
            # 메타데이터 저장
            self._save_backup_metadata()
            
            # 저장 공간 정리
            self._cleanup_old_backups()
            
            logger.info(f"백업 생성 완료: {backup_id} - {description}")
            return backup_info
        
        except Exception as e:
            logger.error(f"백업 생성 실패: {str(e)}")
            return None
    
    def _should_create_backup(self, data: Any, context: Dict[str, Any]) -> bool:
        """백업 전략에 따른 백업 여부 결정"""
        for strategy in self.backup_strategies:
            if strategy.should_backup(data, context):
                return True
        return False
    
    def restore_backup(self, backup_id: str) -> Optional[Any]:
        """백업 복원"""
        try:
            # 백업 정보 찾기
            backup_info = next((b for b in self.backup_history if b.backup_id == backup_id), None)
            
            if not backup_info:
                logger.error(f"백업을 찾을 수 없습니다: {backup_id}")
                return None
            
            # 백업 파일 확인
            if not os.path.exists(backup_info.file_path):
                logger.error(f"백업 파일이 존재하지 않습니다: {backup_info.file_path}")
                return None
            
            # 데이터 로드
            with open(backup_info.file_path, 'rb') as f:
                data = pickle.load(f)
            
            # 체크섬 검증
            current_checksum = self._calculate_checksum(data)
            if current_checksum != backup_info.checksum:
                logger.warning(f"백업 체크섬 불일치: {backup_id}")
            
            logger.info(f"백업 복원 완료: {backup_id}")
            return data
        
        except Exception as e:
            logger.error(f"백업 복원 실패: {str(e)}")
            return None
    
    def list_backups(self, backup_type: str = None) -> List[BackupInfo]:
        """백업 목록 반환"""
        if backup_type:
            return [b for b in self.backup_history if b.backup_type == backup_type]
        return self.backup_history.copy()
    
    def get_backup_info(self, backup_id: str) -> Optional[BackupInfo]:
        """특정 백업 정보 반환"""
        return next((b for b in self.backup_history if b.backup_id == backup_id), None)
    
    def delete_backup(self, backup_id: str) -> bool:
        """백업 삭제"""
        try:
            backup_info = self.get_backup_info(backup_id)
            if not backup_info:
                logger.error(f"백업을 찾을 수 없습니다: {backup_id}")
                return False
            
            # 파일 삭제
            if os.path.exists(backup_info.file_path):
                os.remove(backup_info.file_path)
            
            # 히스토리에서 제거
            self.backup_history = [b for b in self.backup_history if b.backup_id != backup_id]
            
            # 메타데이터 저장
            self._save_backup_metadata()
            
            logger.info(f"백업 삭제 완료: {backup_id}")
            return True
        
        except Exception as e:
            logger.error(f"백업 삭제 실패: {str(e)}")
            return False
    
    def _cleanup_old_backups(self):
        """오래된 백업 정리"""
        try:
            # 저장 공간 확인
            total_size = sum(b.size_bytes for b in self.backup_history)
            
            if total_size <= self.max_storage_bytes:
                return
            
            # 백업을 시간순으로 정렬 (오래된 것부터)
            sorted_backups = sorted(self.backup_history, key=lambda x: x.timestamp)
            
            # 저장 공간이 허용 범위 내로 들어올 때까지 오래된 백업 삭제
            for backup in sorted_backups:
                if total_size <= self.max_storage_bytes:
                    break
                
                if self.delete_backup(backup.backup_id):
                    total_size -= backup.size_bytes
            
            logger.info("오래된 백업 정리 완료")
        
        except Exception as e:
            logger.error(f"백업 정리 실패: {str(e)}")
    
    def get_backup_statistics(self) -> Dict[str, Any]:
        """백업 통계 정보 반환"""
        if not self.backup_history:
            return {"message": "백업 데이터가 없습니다"}
        
        total_backups = len(self.backup_history)
        total_size = sum(b.size_bytes for b in self.backup_history)
        
        # 백업 타입별 통계
        type_stats = {}
        for backup in self.backup_history:
            backup_type = backup.backup_type
            if backup_type not in type_stats:
                type_stats[backup_type] = {'count': 0, 'total_size': 0}
            type_stats[backup_type]['count'] += 1
            type_stats[backup_type]['total_size'] += backup.size_bytes
        
        # 최근 백업 정보
        recent_backups = sorted(self.backup_history, key=lambda x: x.timestamp, reverse=True)[:5]
        
        return {
            "total_backups": total_backups,
            "total_size_bytes": total_size,
            "total_size_gb": total_size / (1024**3),
            "type_statistics": type_stats,
            "recent_backups": [
                {
                    "backup_id": b.backup_id,
                    "timestamp": b.timestamp,
                    "description": b.description,
                    "size_bytes": b.size_bytes
                }
                for b in recent_backups
            ],
            "storage_usage_percent": (total_size / self.max_storage_bytes) * 100
        }
    
    def export_backup_catalog(self, filepath: str = None) -> str:
        """백업 카탈로그 내보내기"""
        if not filepath:
            timestamp = int(time.time())
            filepath = f"backup_catalog_{timestamp}.json"
        
        catalog_data = {
            "backup_statistics": self.get_backup_statistics(),
            "all_backups": [
                {
                    "backup_id": backup.backup_id,
                    "timestamp": backup.timestamp,
                    "description": backup.description,
                    "size_bytes": backup.size_bytes,
                    "checksum": backup.checksum,
                    "backup_type": backup.backup_type,
                    "metadata": backup.metadata
                }
                for backup in self.backup_history
            ],
            "export_timestamp": time.time()
        }
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(catalog_data, f, ensure_ascii=False, indent=2)
            
            logger.info(f"백업 카탈로그 내보내기 완료: {filepath}")
            return filepath
        
        except Exception as e:
            logger.error(f"백업 카탈로그 내보내기 실패: {str(e)}")
            raise

# 사용 예시
if __name__ == "__main__":
    # 백업 관리자 인스턴스 생성
    backup_mgr = BackupManager(backup_dir="test_backups", max_storage_gb=1.0)
    
    # 샘플 데이터 백업
    sample_data = {
        "model_performance": {"accuracy": 0.85, "f1_score": 0.82},
        "training_data": "sample_training_data",
        "timestamp": time.time()
    }
    
    # 백업 생성
    backup_info = backup_mgr.create_backup(
        data=sample_data,
        description="샘플 모델 데이터 백업",
        backup_type="model_data"
    )
    
    if backup_info:
        print(f"백업 생성 완료: {backup_info.backup_id}")
        print(f"설명: {backup_info.description}")
        print(f"크기: {backup_info.size_bytes} bytes")
        print(f"체크섬: {backup_info.checksum}")
    
    # 백업 목록 출력
    backups = backup_mgr.list_backups()
    print(f"\n총 백업 수: {len(backups)}")
    
    # 백업 통계 출력
    stats = backup_mgr.get_backup_statistics()
    print(f"\n=== 백업 통계 ===")
    print(f"총 백업 수: {stats['total_backups']}")
    print(f"총 크기: {stats['total_size_gb']:.2f} GB")
    print(f"저장 공간 사용률: {stats['storage_usage_percent']:.1f}%")
