from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional
import logging

from ..services.backup_service import get_backup_service, init_backup_service
from ..models.backup_model import (
    BackupCreateRequest, BackupResponse, BackupListResponse,
    BackupRestoreRequest, BackupRestoreResponse
)

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/full", response_model=dict, tags=["backup"])
async def create_full_backup(request: BackupCreateRequest):
    """전체 백업 수행"""
    try:
        backup_service = get_backup_service()
        backup_id = backup_service.create_full_backup(request)
        return {
            "status": "success",
            "backup_id": backup_id,
            "message": f"백업이 성공적으로 생성되었습니다: {backup_id}"
        }
    except Exception as e:
        logger.error(f"전체 백업 생성 실패: {e}")
        raise HTTPException(status_code=500, detail=f"백업 생성 실패: {str(e)}")


@router.get("/list", response_model=BackupListResponse, tags=["backup"])
async def get_backup_list(limit: int = 50):
    """백업 리스트 조회"""
    try:
        backup_service = get_backup_service()
        return backup_service.get_backup_list(limit)
    except Exception as e:
        logger.error(f"백업 목록 조회 실패: {e}")
        raise HTTPException(status_code=500, detail=f"백업 목록 조회 실패: {str(e)}")


@router.get("/health", response_model=dict, tags=["backup"])
async def backup_health_check():
    """백업 시스템 상태 확인"""
    try:
        backup_service = get_backup_service()
        
        # 백업 디렉토리 확인
        import os
        backup_dir_exists = os.path.exists(backup_service.backup_dir)
        
        # 스케줄러 상태 확인
        scheduler_running = backup_service.scheduler.running
        
        # 최근 백업 확인
        recent_backups = backup_service.get_backup_list(limit=5)
        
        return {
            "status": "healthy",
            "backup_directory": backup_service.backup_dir,
            "backup_directory_exists": backup_dir_exists,
            "scheduler_running": scheduler_running,
            "recent_backups_count": recent_backups.total_backups,
            "total_backup_size_mb": recent_backups.total_size_mb
        }
    except Exception as e:
        logger.error(f"백업 시스템 상태 확인 실패: {e}")
        return {
            "status": "unhealthy",
            "error": str(e)
        }


@router.post("/restore/{backup_id}", response_model=BackupRestoreResponse, tags=["backup"])
async def restore_backup(backup_id: str, request: BackupRestoreRequest):
    """특정 백업 복원"""
    try:
        backup_service = get_backup_service()
        return backup_service.restore_backup(backup_id, request)
    except Exception as e:
        logger.error(f"백업 복원 실패: {e}")
        raise HTTPException(status_code=500, detail=f"백업 복원 실패: {str(e)}")


@router.get("/{backup_id}", response_model=dict, tags=["backup"])
async def get_backup_details(backup_id: str):
    """백업 상세 정보 조회"""
    try:
        backup_service = get_backup_service()
        backup_data = backup_service._get_backup_data(backup_id)
        if not backup_data:
            raise HTTPException(status_code=404, detail=f"백업을 찾을 수 없음: {backup_id}")
        
        return {
            "backup_id": backup_data.backup_id,
            "backup_type": backup_data.backup_type,
            "status": backup_data.status,
            "created_at": backup_data.created_at,
            "completed_at": backup_data.completed_at,
            "description": backup_data.description,
            "size_mb": backup_data.size_mb,
            "config_snapshot": backup_data.config_snapshot.dict() if backup_data.config_snapshot else None,
            "database_snapshot": backup_data.database_snapshot.dict() if backup_data.database_snapshot else None,
            "service_statuses": [status.dict() for status in backup_data.service_statuses],
            "error_message": backup_data.error_message
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"백업 상세 정보 조회 실패: {e}")
        raise HTTPException(status_code=500, detail=f"백업 상세 정보 조회 실패: {str(e)}")


@router.delete("/{backup_id}", response_model=dict, tags=["backup"])
async def delete_backup(backup_id: str):
    """백업 삭제"""
    try:
        backup_service = get_backup_service()
        # 백업 데이터 조회
        backup_data = backup_service._get_backup_data(backup_id)
        if not backup_data:
            raise HTTPException(status_code=404, detail=f"백업을 찾을 수 없음: {backup_id}")
        
        # 백업 파일 삭제
        import os
        backup_file = os.path.join(backup_service.backup_dir, f"{backup_id}.json")
        if os.path.exists(backup_file):
            os.remove(backup_file)
        
        # DB 레코드 삭제
        import psycopg2
        conn = backup_service._get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM full_backups WHERE backup_id = %s", (backup_id,))
        conn.commit()
        cursor.close()
        conn.close()
        
        return {
            "status": "success",
            "message": f"백업이 성공적으로 삭제되었습니다: {backup_id}"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"백업 삭제 실패: {e}")
        raise HTTPException(status_code=500, detail=f"백업 삭제 실패: {str(e)}")


@router.post("/schedule", response_model=dict, tags=["backup"])
async def schedule_backup():
    """백업 스케줄 설정"""
    try:
        backup_service = get_backup_service()
        # 스케줄러 상태 확인
        jobs = backup_service.scheduler.get_jobs()
        
        return {
            "status": "success",
            "scheduler_running": backup_service.scheduler.running,
            "active_jobs": len(jobs),
            "jobs": [
                {
                    "id": job.id,
                    "next_run_time": str(job.next_run_time),
                    "trigger": str(job.trigger)
                }
                for job in jobs
            ]
        }
    except Exception as e:
        logger.error(f"백업 스케줄 조회 실패: {e}")
        raise HTTPException(status_code=500, detail=f"백업 스케줄 조회 실패: {str(e)}") 