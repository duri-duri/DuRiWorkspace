from fastapi import APIRouter, HTTPException, Depends
from typing import List, Dict, Any
import logging

from ..services.config_service import config_service
from ..models.config_model import (
    ConfigResponse,
    ConfigUpdateRequest,
    ConfigListResponse,
    ConfigValidationResponse
)

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/services", response_model=ConfigListResponse, tags=["config"])
async def get_all_services():
    """모든 서비스 목록 조회"""
    try:
        return config_service.get_all_services()
    except Exception as e:
        logger.error(f"서비스 목록 조회 실패: {e}")
        raise HTTPException(status_code=500, detail=f"서비스 목록 조회 실패: {str(e)}")


@router.get("/services/{service_name}", response_model=ConfigResponse, tags=["config"])
async def get_service_config(service_name: str):
    """서비스 설정 조회"""
    try:
        config = config_service.get_service_config(service_name)
        if not config:
            raise HTTPException(status_code=404, detail=f"서비스를 찾을 수 없음: {service_name}")
        return config
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"설정 조회 실패 ({service_name}): {e}")
        raise HTTPException(status_code=500, detail=f"설정 조회 실패: {str(e)}")


@router.put("/services/{service_name}", response_model=ConfigResponse, tags=["config"])
async def update_service_config(service_name: str, update_data: ConfigUpdateRequest):
    """서비스 설정 업데이트"""
    try:
        # 설정 유효성 검증
        current_config = config_service.get_service_config(service_name)
        if not current_config:
            raise HTTPException(status_code=404, detail=f"서비스를 찾을 수 없음: {service_name}")
        
        # 업데이트할 데이터 준비
        current_dict = current_config.config.dict()
        update_dict = update_data.dict(exclude_unset=True)
        updated_dict = {**current_dict, **update_dict}
        
        # 커스텀 설정 병합
        if 'custom_config' in update_dict and 'custom_config' in current_dict:
            updated_dict['custom_config'] = {
                **current_dict['custom_config'],
                **update_dict['custom_config']
            }
        
        # 유효성 검증
        validation = config_service.validate_config(service_name, updated_dict)
        if not validation.is_valid:
            raise HTTPException(
                status_code=400, 
                detail=f"설정 유효성 검증 실패: {', '.join(validation.errors)}"
            )
        
        # 설정 업데이트
        updated_config = config_service.update_service_config(service_name, update_data)
        if not updated_config:
            raise HTTPException(status_code=500, detail="설정 업데이트 실패")
        
        return updated_config
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"설정 업데이트 실패 ({service_name}): {e}")
        raise HTTPException(status_code=500, detail=f"설정 업데이트 실패: {str(e)}")


@router.post("/services/{service_name}/validate", response_model=ConfigValidationResponse, tags=["config"])
async def validate_service_config(service_name: str, config_data: Dict[str, Any]):
    """설정 유효성 검증"""
    try:
        return config_service.validate_config(service_name, config_data)
    except Exception as e:
        logger.error(f"설정 검증 실패 ({service_name}): {e}")
        raise HTTPException(status_code=500, detail=f"설정 검증 실패: {str(e)}")


@router.post("rollback/{service_name}", response_model=ConfigResponse, tags=["config"])
async def rollback_service_config(service_name: str, backup_id: int = None):
    """서비스 설정을 백업으로 롤백"""
    try:
        success = config_service.backup_service.rollback_to_backup(service_name, backup_id)
        if not success:
            raise HTTPException(status_code=404, detail=f"롤백할 백업을 찾을 수 없음: {service_name}")
        
        # 롤백된 설정 조회
        config = config_service.get_service_config(service_name)
        if not config:
            raise HTTPException(status_code=500, detail="롤백 후 설정 조회 실패")
        
        return config
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"설정 롤백 실패 ({service_name}): {e}")
        raise HTTPException(status_code=500, detail=f"설정 롤백 실패: {str(e)}")


@router.get("backup/{service_name}", tags=["config"])
async def get_backup_history(service_name: str, limit: int = 10):
    """서비스 백업 히스토리 조회"""
    try:
        backups = config_service.backup_service.get_backup_history(service_name, limit)
        return {
            "service_name": service_name,
            "backups": backups,
            "total_backups": len(backups)
        }
    except Exception as e:
        logger.error(f"백업 히스토리 조회 실패 ({service_name}): {e}")
        raise HTTPException(status_code=500, detail=f"백업 히스토리 조회 실패: {str(e)}")


@router.post("/services/{service_name}/reset", response_model=ConfigResponse, tags=["config"])
async def reset_service_config(service_name: str):
    """서비스 설정을 기본값으로 초기화"""
    try:
        config = config_service.reset_to_default(service_name)
        if not config:
            raise HTTPException(status_code=404, detail=f"기본 설정이 없는 서비스: {service_name}")
        return config
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"설정 초기화 실패 ({service_name}): {e}")
        raise HTTPException(status_code=500, detail=f"설정 초기화 실패: {str(e)}")


@router.delete("/services/{service_name}", tags=["config"])
async def delete_service_config(service_name: str):
    """서비스 설정 삭제"""
    try:
        success = config_service.delete_service_config(service_name)
        if not success:
            raise HTTPException(status_code=404, detail=f"삭제할 설정이 없음: {service_name}")
        
        return {"status": "success", "message": f"설정 삭제 완료: {service_name}"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"설정 삭제 실패 ({service_name}): {e}")
        raise HTTPException(status_code=500, detail=f"설정 삭제 실패: {str(e)}")


@router.get("/services/{service_name}/export", tags=["config"])
async def export_service_config(service_name: str):
    """서비스 설정 내보내기 (JSON 형식)"""
    try:
        config = config_service.get_service_config(service_name)
        if not config:
            raise HTTPException(status_code=404, detail=f"서비스를 찾을 수 없음: {service_name}")
        
        return {
            "service_name": config.service_name,
            "config": config.config.dict(),
            "version": config.version,
            "last_updated": config.last_updated.isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"설정 내보내기 실패 ({service_name}): {e}")
        raise HTTPException(status_code=500, detail=f"설정 내보내기 실패: {str(e)}")


@router.post("/services/{service_name}/import", response_model=ConfigResponse, tags=["config"])
async def import_service_config(service_name: str, config_data: Dict[str, Any]):
    """서비스 설정 가져오기 (JSON 형식)"""
    try:
        # 설정 유효성 검증
        validation = config_service.validate_config(service_name, config_data)
        if not validation.is_valid:
            raise HTTPException(
                status_code=400, 
                detail=f"설정 유효성 검증 실패: {', '.join(validation.errors)}"
            )
        
        # ConfigUpdateRequest로 변환
        from ..models.config_model import ConfigUpdateRequest
        update_request = ConfigUpdateRequest(**config_data)
        
        # 설정 업데이트
        updated_config = config_service.update_service_config(service_name, update_request)
        if not updated_config:
            raise HTTPException(status_code=500, detail="설정 가져오기 실패")
        
        return updated_config
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"설정 가져오기 실패 ({service_name}): {e}")
        raise HTTPException(status_code=500, detail=f"설정 가져오기 실패: {str(e)}")


@router.get("/health", tags=["config"])
async def config_service_health():
    """설정 서비스 상태 확인"""
    try:
        # 데이터베이스 연결 테스트
        services = config_service.get_all_services()
        return {
            "status": "healthy",
            "database": "connected",
            "total_services": services.total_services,
            "available_services": services.services
        }
    except Exception as e:
        logger.error(f"설정 서비스 상태 확인 실패: {e}")
        raise HTTPException(status_code=500, detail=f"설정 서비스 상태 확인 실패: {str(e)}") 