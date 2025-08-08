import functools
import logging
import time
import traceback
from typing import Any, Callable, Dict, Optional
from datetime import datetime

from ..database.database import get_db_session

logger = logging.getLogger(__name__)


def log_to_memory(
    memory_type: str = "function_call",
    context: str = "",
    importance_score: int = 50,
    auto_capture_args: bool = True,
    auto_capture_result: bool = True,
    auto_capture_error: bool = True
):
    """
    함수 실행을 자동으로 Memory 시스템에 로깅하는 데코레이터
    
    Args:
        memory_type: 기억 타입 (function_call, api_request, error, etc.)
        context: 기억의 맥락 설명
        importance_score: 중요도 점수 (0-100)
        auto_capture_args: 함수 인자를 자동 캡처할지 여부
        auto_capture_result: 함수 결과를 자동 캡처할지 여부
        auto_capture_error: 오류를 자동 캡처할지 여부
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            function_name = func.__name__
            module_name = func.__module__
            
            # 함수 실행 정보 수집
            execution_info = {
                "function_name": function_name,
                "module_name": module_name,
                "start_time": datetime.now().isoformat(),
                "args_count": len(args),
                "kwargs_count": len(kwargs)
            }
            
            # 인자 캡처 (민감한 정보 제외)
            if auto_capture_args:
                safe_args = []
                for i, arg in enumerate(args):
                    if isinstance(arg, (str, int, float, bool)):
                        safe_args.append(str(arg)[:100])  # 100자 제한
                    else:
                        safe_args.append(f"<{type(arg).__name__}>")
                
                safe_kwargs = {}
                for key, value in kwargs.items():
                    if isinstance(value, (str, int, float, bool)):
                        safe_kwargs[key] = str(value)[:100]
                    else:
                        safe_kwargs[key] = f"<{type(value).__name__}>"
                
                execution_info["args"] = safe_args
                execution_info["kwargs"] = safe_kwargs
            
            try:
                # 함수 실행
                result = func(*args, **kwargs)
                execution_time = time.time() - start_time
                
                # 성공 정보 추가
                execution_info.update({
                    "status": "success",
                    "execution_time": execution_time,
                    "end_time": datetime.now().isoformat()
                })
                
                # 결과 캡처
                if auto_capture_result and result is not None:
                    if isinstance(result, (str, int, float, bool)):
                        execution_info["result"] = str(result)[:200]  # 200자 제한
                    else:
                        execution_info["result"] = f"<{type(result).__name__}>"
                
                # Memory에 로깅
                _save_to_memory(
                    memory_type=memory_type,
                    context=context or f"{module_name}.{function_name} 실행",
                    content=f"{function_name} 함수 실행 성공 (소요시간: {execution_time:.3f}초)",
                    raw_data=execution_info,
                    source="memory_logger",
                    tags=["auto_log", "function_call", "success"],
                    importance_score=importance_score
                )
                
                return result
                
            except Exception as e:
                execution_time = time.time() - start_time
                error_info = {
                    "error_type": type(e).__name__,
                    "error_message": str(e),
                    "traceback": traceback.format_exc()[:500]  # 500자 제한
                }
                
                execution_info.update({
                    "status": "error",
                    "execution_time": execution_time,
                    "end_time": datetime.now().isoformat(),
                    "error": error_info
                })
                
                # 오류 캡처
                if auto_capture_error:
                    _save_to_memory(
                        memory_type="error",
                        context=context or f"{module_name}.{function_name} 오류",
                        content=f"{function_name} 함수 실행 실패: {type(e).__name__} - {str(e)}",
                        raw_data=execution_info,
                        source="memory_logger",
                        tags=["auto_log", "function_call", "error"],
                        importance_score=min(importance_score + 20, 100)  # 오류는 중요도 증가
                    )
                
                # 원래 예외 재발생
                raise
                
        return wrapper
    return decorator


def log_api_request(
    endpoint: str = "",
    method: str = "GET",
    importance_score: int = 60
):
    """
    API 요청을 자동으로 로깅하는 데코레이터
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # API 요청 정보 수집
            request_info = {
                "endpoint": endpoint or func.__name__,
                "method": method,
                "timestamp": datetime.now().isoformat()
            }
            
            try:
                result = func(*args, **kwargs)
                
                # 성공 로깅
                _save_to_memory(
                    memory_type="api_request",
                    context=f"API 요청: {method} {endpoint}",
                    content=f"API 요청 성공: {method} {endpoint}",
                    raw_data=request_info,
                    source="memory_logger",
                    tags=["auto_log", "api_request", "success"],
                    importance_score=importance_score
                )
                
                return result
                
            except Exception as e:
                # 오류 로깅
                _save_to_memory(
                    memory_type="api_error",
                    context=f"API 오류: {method} {endpoint}",
                    content=f"API 요청 실패: {method} {endpoint} - {str(e)}",
                    raw_data={**request_info, "error": str(e)},
                    source="memory_logger",
                    tags=["auto_log", "api_request", "error"],
                    importance_score=min(importance_score + 30, 100)
                )
                raise
                
        return wrapper
    return decorator


def _save_to_memory(
    memory_type: str,
    context: str,
    content: str,
    raw_data: Dict[str, Any],
    source: str,
    tags: list,
    importance_score: int
):
    """Memory 시스템에 로그 저장"""
    try:
        db = next(get_db_session())
        from ..services.memory_service import MemoryService
        memory_service = MemoryService(db)
        
        memory_service.save_memory(
            type=memory_type,
            context=context,
            content=content,
            raw_data=raw_data,
            source=source,
            tags=tags,
            importance_score=importance_score
        )
        
        db.close()
        logger.debug(f"Memory 로그 저장 완료: {memory_type} - {content[:50]}...")
        
    except Exception as e:
        logger.error(f"Memory 로그 저장 실패: {e}")
        # Memory 저장 실패해도 원래 함수는 계속 실행


# 편의 함수들
def log_important_event(context: str, content: str, importance_score: int = 80):
    """중요한 이벤트를 로깅하는 편의 함수"""
    _save_to_memory(
        memory_type="important_event",
        context=context,
        content=content,
        raw_data={"event_type": "important_event"},
        source="memory_logger",
        tags=["auto_log", "important_event"],
        importance_score=importance_score
    )


def log_system_event(context: str, content: str, importance_score: int = 40):
    """시스템 이벤트를 로깅하는 편의 함수"""
    _save_to_memory(
        memory_type="system_event",
        context=context,
        content=content,
        raw_data={"event_type": "system_event"},
        source="memory_logger",
        tags=["auto_log", "system_event"],
        importance_score=importance_score
    )


def log_user_action(context: str, content: str, importance_score: int = 60):
    """사용자 액션을 로깅하는 편의 함수"""
    _save_to_memory(
        memory_type="user_action",
        context=context,
        content=content,
        raw_data={"event_type": "user_action"},
        source="memory_logger",
        tags=["auto_log", "user_action"],
        importance_score=importance_score
    ) 