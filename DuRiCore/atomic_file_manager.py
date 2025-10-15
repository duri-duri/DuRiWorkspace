#!/usr/bin/env python3
"""
DuRi 원자적 파일 관리자 - 프로덕션 내구성 강화
"""

import tempfile
import shutil
import json
import os
import fcntl
import time
from typing import Any, Dict, Optional
from DuRiCore.global_logging_manager import get_duri_logger

logger = get_duri_logger("atomic_file_manager")

class AtomicFileManager:
    """원자적 파일 관리자 - 프로덕션 내구성 강화"""
    
    def __init__(self, file_path: str):
        """초기화"""
        self.file_path = file_path
        self.temp_dir = os.path.dirname(file_path) or "."
        self.lock_file = f"{file_path}.lock"
        logger.info(f"AtomicFileManager 초기화: {file_path}")
    
    def _acquire_lock(self, timeout: float = 5.0) -> bool:
        """파일 잠금 획득 (fcntl 기반)"""
        try:
            os.makedirs(os.path.dirname(self.lock_file) or ".", exist_ok=True)
            self.lock_fd = open(self.lock_file, 'w')
            start_time = time.time()
            
            while time.time() - start_time < timeout:
                try:
                    fcntl.flock(self.lock_fd.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
                    logger.debug(f"파일 잠금 획득: {self.lock_file}")
                    return True
                except IOError:
                    time.sleep(0.1)
            
            logger.warning(f"파일 잠금 획득 타임아웃: {self.lock_file}")
            return False
            
        except Exception as e:
            logger.error(f"파일 잠금 획득 실패: {e}")
            return False
    
    def _release_lock(self):
        """파일 잠금 해제"""
        try:
            if hasattr(self, 'lock_fd') and self.lock_fd:
                fcntl.flock(self.lock_fd.fileno(), fcntl.LOCK_UN)
                self.lock_fd.close()
                logger.debug(f"파일 잠금 해제: {self.lock_file}")
        except Exception as e:
            logger.warning(f"파일 잠금 해제 실패: {e}")
    
    def _ensure_durability(self, file_path: str):
        """파일 내구성 보장 - fsync 적용"""
        try:
            # 파일 디스크립터로 열어서 fsync
            with open(file_path, 'r+b') as f:
                os.fsync(f.fileno())
                logger.debug(f"파일 fsync 완료: {file_path}")
            
            # 부모 디렉토리도 fsync (파일명 변경 내구성)
            parent_dir = os.path.dirname(file_path)
            if parent_dir:
                parent_fd = os.open(parent_dir, os.O_RDONLY)
                try:
                    os.fsync(parent_fd)
                    logger.debug(f"디렉토리 fsync 완료: {parent_dir}")
                finally:
                    os.close(parent_fd)
                    
        except Exception as e:
            logger.warning(f"fsync 실패: {e}")
    
    def atomic_write(self, data: Dict[str, Any]) -> bool:
        """원자적 쓰기 - 프로덕션 내구성 강화"""
        if not self._acquire_lock():
            return False
        
        temp_path = None
        
        try:
            # 1) 임시 파일 생성
            with tempfile.NamedTemporaryFile(
                mode='w', 
                encoding='utf-8',
                dir=self.temp_dir, 
                delete=False, 
                suffix='.tmp'
            ) as temp_file:
                # 2) 데이터 쓰기
                json.dump(data, temp_file, ensure_ascii=False, indent=2)
                temp_file.flush()  # 버퍼 플러시
                os.fsync(temp_file.fileno())  # 전원 장애 대비
                temp_path = temp_file.name
                logger.debug(f"임시 파일 생성 완료: {temp_path}")
            
            # 3) 원자적 이동
            shutil.move(temp_path, self.file_path)
            
            # 4) 대상 파일과 디렉토리 fsync
            with open(self.file_path, 'rb', buffering=0) as _f:
                os.fsync(_f.fileno())
            dir_fd = os.open(os.path.dirname(self.file_path) or ".", os.O_RDONLY)
            try:
                os.fsync(dir_fd)
            finally:
                os.close(dir_fd)
            
            logger.info(f"원자적 쓰기 완료: {self.file_path}")
            return True
            
        except OSError as e:
            # 디스크 풀/권한 문제 등 I/O 예외 → 실패 처리
            logger.error(f"I/O 오류로 원자적 쓰기 실패: {e}")
            if temp_path and os.path.exists(temp_path):
                try:
                    os.unlink(temp_path)
                    logger.debug(f"임시 파일 정리 완료: {temp_path}")
                except OSError as cleanup_error:
                    logger.warning(f"임시 파일 정리 실패: {cleanup_error}")
            return False
            
        except Exception as e:
            # 기타 예외 처리
            logger.error(f"원자적 쓰기 실패: {e}")
            if temp_path and os.path.exists(temp_path):
                try:
                    os.unlink(temp_path)
                    logger.debug(f"임시 파일 정리 완료: {temp_path}")
                except OSError as cleanup_error:
                    logger.warning(f"임시 파일 정리 실패: {cleanup_error}")
            return False
            
        finally:
            self._release_lock()
    
    def atomic_append(self, data: Dict[str, Any]) -> bool:
        """원자적 추가 - 프로덕션 내구성 강화"""
        if not self._acquire_lock():
            return False
        
        temp_path = None
        
        try:
            # 기존 데이터 로드
            existing_data = []
            if os.path.exists(self.file_path):
                try:
                    with open(self.file_path, 'r', encoding='utf-8') as f:
                        existing_data = json.load(f)
                        if not isinstance(existing_data, list):
                            existing_data = [existing_data]
                except (json.JSONDecodeError, OSError) as e:
                    logger.warning(f"기존 데이터 로드 실패, 새로 시작: {e}")
                    existing_data = []
            
            # 새 데이터 추가
            existing_data.append(data)
            
            # 1) 임시 파일 생성
            with tempfile.NamedTemporaryFile(
                mode='w', 
                encoding='utf-8',
                dir=self.temp_dir, 
                delete=False, 
                suffix='.tmp'
            ) as temp_file:
                # 2) 데이터 쓰기
                json.dump(existing_data, temp_file, ensure_ascii=False, indent=2)
                temp_file.flush()  # 버퍼 플러시
                os.fsync(temp_file.fileno())  # 전원 장애 대비
                temp_path = temp_file.name
                logger.debug(f"임시 파일 생성 완료: {temp_path}")
            
            # 3) 원자적 이동
            shutil.move(temp_path, self.file_path)
            
            # 4) 대상 파일과 디렉토리 fsync
            with open(self.file_path, 'rb', buffering=0) as _f:
                os.fsync(_f.fileno())
            dir_fd = os.open(os.path.dirname(self.file_path) or ".", os.O_RDONLY)
            try:
                os.fsync(dir_fd)
            finally:
                os.close(dir_fd)
            
            logger.info(f"원자적 추가 완료: {self.file_path}")
            return True
            
        except OSError as e:
            # I/O 예외 처리
            logger.error(f"I/O 오류로 원자적 추가 실패: {e}")
            if temp_path and os.path.exists(temp_path):
                try:
                    os.unlink(temp_path)
                    logger.debug(f"임시 파일 정리 완료: {temp_path}")
                except OSError as cleanup_error:
                    logger.warning(f"임시 파일 정리 실패: {cleanup_error}")
            return False
            
        except Exception as e:
            # 기타 예외 처리
            logger.error(f"원자적 추가 실패: {e}")
            if temp_path and os.path.exists(temp_path):
                try:
                    os.unlink(temp_path)
                    logger.debug(f"임시 파일 정리 완료: {temp_path}")
                except OSError as cleanup_error:
                    logger.warning(f"임시 파일 정리 실패: {cleanup_error}")
            return False
            
        finally:
            self._release_lock()
    
    def atomic_read(self) -> Optional[Dict[str, Any]]:
        """원자적 읽기 - 프로덕션 내구성 강화"""
        if not self._acquire_lock():
            return None
        
        try:
            if not os.path.exists(self.file_path):
                logger.debug(f"파일이 존재하지 않음: {self.file_path}")
                return None
            
            with open(self.file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                logger.debug(f"원자적 읽기 완료: {self.file_path}")
                return data
                
        except OSError as e:
            logger.error(f"I/O 오류로 원자적 읽기 실패: {e}")
            return None
            
        except json.JSONDecodeError as e:
            logger.error(f"JSON 파싱 오류로 원자적 읽기 실패: {e}")
            return None
            
        except Exception as e:
            logger.error(f"원자적 읽기 실패: {e}")
            return None
            
        finally:
            self._release_lock()
    
    def get_file_info(self) -> Dict[str, Any]:
        """파일 정보 반환"""
        try:
            if not os.path.exists(self.file_path):
                return {"exists": False, "size": 0, "modified": None}
            
            stat = os.stat(self.file_path)
            return {
                "exists": True,
                "size": stat.st_size,
                "modified": stat.st_mtime,
                "path": self.file_path
            }
            
        except OSError as e:
            logger.error(f"파일 정보 조회 실패: {e}")
            return {"exists": False, "size": 0, "modified": None, "error": str(e)}
