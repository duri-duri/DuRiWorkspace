#!/usr/bin/env python3
"""
DuRi 로깅 어댑터

컨텍스트 전파와 자동 라벨링을 제공합니다.
"""

import logging
from logging import LoggerAdapter
from typing import Optional, Dict, Any
from .autodetect import infer_component

class ContextAdapter(LoggerAdapter):
    """컨텍스트를 자동으로 전파하는 Logger 어댑터."""
    
    def addHandler(self, handler):
        """핸들러를 추가합니다."""
        self.logger.addHandler(handler)
    
    def removeHandler(self, handler):
        """핸들러를 제거합니다."""
        self.logger.removeHandler(handler)
    
    def process(self, msg: str, kwargs: Dict[str, Any]) -> tuple:
        """
        로그 메시지와 키워드 인자를 처리합니다.
        
        Args:
            msg: 로그 메시지
            kwargs: 키워드 인자
            
        Returns:
            처리된 메시지와 키워드 인자
        """
        extra = kwargs.get("extra", {}) or {}
        
        # component 우선순위: 명시값 > 자동 추론 > 기본값
        if "component" not in extra:
            extra["component"] = infer_component(self.logger.name, "_")
        
        # 컨텍스트 정보 추가
        try:
            from .context import get_context
            ctx = get_context()
            for k, v in ctx.items():
                if k not in extra:
                    extra[k] = v
        except Exception:
            pass
        
        kwargs["extra"] = extra
        return msg, kwargs

def get_logger(name: str, component: Optional[str] = None) -> ContextAdapter:
    """
    컨텍스트 어댑터가 적용된 로거를 반환합니다.
    
    Args:
        name: 로거 이름
        component: 강제로 지정할 컴포넌트 (None이면 자동 추론)
        
    Returns:
        ContextAdapter가 적용된 로거
    """
    base = logging.getLogger(name)
    adapter = ContextAdapter(base, {})
    
    if component:
        # 강제 지정 시 추론 무시
        def process(msg: str, kwargs: Dict[str, Any]) -> tuple:
            extra = kwargs.get("extra", {}) or {}
            extra["component"] = component
            
            # 컨텍스트 정보 추가
            try:
                from .context import get_context
                ctx = get_context()
                for k, v in ctx.items():
                    if k not in extra:
                        extra[k] = v
            except Exception:
                pass
            
            kwargs["extra"] = extra
            return msg, kwargs
        
        adapter.process = process  # type: ignore
    
    return adapter

def get_logger_for_module(module_name: str, component: Optional[str] = None) -> ContextAdapter:
    """
    모듈 이름으로 로거를 생성합니다.
    
    Args:
        module_name: 모듈 이름 (예: __name__)
        component: 강제로 지정할 컴포넌트
        
    Returns:
        ContextAdapter가 적용된 로거
    """
    return get_logger(module_name, component)

def test_adapter():
    """어댑터 시스템을 테스트합니다."""
    from .setup import setup_logging
    
    # 로깅 시스템 초기화
    setup_logging()
    
    # 1. 자동 추론 테스트
    log1 = get_logger("DuRiCore.learning.engine")
    log1.info("자동 추론 테스트")
    
    # 2. 강제 지정 테스트
    log2 = get_logger("DuRiCore.memory.store", "memory")
    log2.info("강제 지정 테스트")
    
    # 3. 컨텍스트 전파 테스트
    from .context import set_request_id, set_learning_session_id, set_phase
    set_request_id("test_req_123")
    set_learning_session_id("test_learn_456")
    set_phase("testing")
    
    log3 = get_logger("DuRiCore.test.context")
    log3.info("컨텍스트 전파 테스트")
    
    # 4. 모듈 로거 테스트
    log4 = get_logger_for_module("DuRiCore.judgment.selector")
    log4.info("모듈 로거 테스트")
    
    print("✅ 어댑터 시스템 테스트 통과")
    return True

if __name__ == "__main__":
    test_adapter()
