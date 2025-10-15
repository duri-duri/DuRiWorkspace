#!/usr/bin/env python3
"""
DuRi 원자적 파일 관리자 - 방어 로직 강화 버전
"""

import tempfile
import shutil
import json
import os
from typing import Any, Dict, Optional
from DuRiCore.global_logging_manager import get_duri_logger

logger = get_duri_logger("atomic_file_manager")

class AtomicFileManager:
    """원자적 파일 관리자 - 방어 로직 강화"""
    
    def __init__(self, file_path: str):
        """초기화"""
        self.file_path = file_path
        self.temp_dir = os.path.dirname(file_path) or "."
        logger.info(f"AtomicFileManager 초기화: {file_path}")
    
    def atomic_write(self, data: Dict[str, Any]) -> bool:
        """원자적 쓰기 - 방어 로직 강화"""
        temp_path = None
        
        try:
            # 1) 임시 파일 생성 (여기서도 OSError 가능)
            with tempfile.NamedTemporaryFile(
                mode='w', 
                encoding='utf-8',
                dir=self.temp_dir, 
                delete=False, 
                suffix='.tmp'
            ) as temp_file:
                # 2) 쓰기 (json.dump 도중 OSError 가능)
                json.dump(data, temp_file, ensure_ascii=False, indent=2)
                temp_path = temp_file.name
                logger.debug(f"임시 파일 생성 완료: {temp_path}")
            
            # 3) 원자적 이동 (move 시 OSError 가능: 대상 디스크 풀 등)
            shutil.move(temp_path, self.file_path)
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
    
    def atomic_append(self, data: Dict[str, Any]) -> bool:
        """원자적 추가 - 방어 로직 강화"""
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
                # 2) 쓰기
                json.dump(existing_data, temp_file, ensure_ascii=False, indent=2)
                temp_path = temp_file.name
                logger.debug(f"임시 파일 생성 완료: {temp_path}")
            
            # 3) 원자적 이동
            shutil.move(temp_path, self.file_path)
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
    
    def atomic_read(self) -> Optional[Dict[str, Any]]:
        """원자적 읽기 - 방어 로직 강화"""
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
