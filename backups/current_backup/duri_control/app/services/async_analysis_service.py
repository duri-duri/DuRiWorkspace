"""
DuRi Memory System - Async Analysis Service
비동기 분석 서비스 (FastAPI BackgroundTasks 기반)
"""
import logging
import asyncio
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from fastapi import BackgroundTasks
from sqlalchemy.orm import Session

from ..database.database import get_db_session
from ..decorators.memory_logger import log_important_event, log_system_event

logger = logging.getLogger(__name__)

class AsyncAnalysisService:
    """비동기 분석 서비스"""
    
    def __init__(self):
        self.analysis_queue: List[Dict[str, Any]] = []
        self.completed_analyses: Dict[str, Any] = {}
        self.analysis_status: Dict[str, str] = {}
    
    async def schedule_pattern_analysis(
        self, 
        background_tasks: BackgroundTasks,
        memory_type: str = None,
        time_window: int = 24,
        min_frequency: int = 3
    ) -> Dict[str, Any]:
        """패턴 분석 스케줄링"""
        try:
            analysis_id = f"pattern_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            # 백그라운드 작업 등록
            background_tasks.add_task(
                self._execute_pattern_analysis,
                analysis_id,
                memory_type,
                time_window,
                min_frequency
            )
            
            # 상태 초기화
            self.analysis_status[analysis_id] = "scheduled"
            
            log_important_event(
                f"패턴 분석 스케줄링: {analysis_id}",
                f"타입: {memory_type}, 시간창: {time_window}시간",
                importance_score=60
            )
            
            return {
                "analysis_id": analysis_id,
                "status": "scheduled",
                "type": "pattern_analysis",
                "parameters": {
                    "memory_type": memory_type,
                    "time_window": time_window,
                    "min_frequency": min_frequency
                }
            }
            
        except Exception as e:
            logger.error(f"패턴 분석 스케줄링 실패: {e}")
            return {"error": str(e)}
    
    async def schedule_correlation_analysis(
        self,
        background_tasks: BackgroundTasks,
        memory_type: str = None,
        time_window: int = 24
    ) -> Dict[str, Any]:
        """상관관계 분석 스케줄링"""
        try:
            analysis_id = f"correlation_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            # 백그라운드 작업 등록
            background_tasks.add_task(
                self._execute_correlation_analysis,
                analysis_id,
                memory_type,
                time_window
            )
            
            # 상태 초기화
            self.analysis_status[analysis_id] = "scheduled"
            
            log_important_event(
                f"상관관계 분석 스케줄링: {analysis_id}",
                f"타입: {memory_type}, 시간창: {time_window}시간",
                importance_score=55
            )
            
            return {
                "analysis_id": analysis_id,
                "status": "scheduled",
                "type": "correlation_analysis",
                "parameters": {
                    "memory_type": memory_type,
                    "time_window": time_window
                }
            }
            
        except Exception as e:
            logger.error(f"상관관계 분석 스케줄링 실패: {e}")
            return {"error": str(e)}
    
    async def schedule_performance_monitoring(
        self,
        background_tasks: BackgroundTasks
    ) -> Dict[str, Any]:
        """성능 모니터링 스케줄링"""
        try:
            analysis_id = f"performance_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            # 백그라운드 작업 등록
            background_tasks.add_task(
                self._execute_performance_monitoring,
                analysis_id
            )
            
            # 상태 초기화
            self.analysis_status[analysis_id] = "scheduled"
            
            log_system_event(
                f"성능 모니터링 스케줄링: {analysis_id}",
                "백그라운드 성능 분석 시작",
                importance_score=50
            )
            
            return {
                "analysis_id": analysis_id,
                "status": "scheduled",
                "type": "performance_monitoring"
            }
            
        except Exception as e:
            logger.error(f"성능 모니터링 스케줄링 실패: {e}")
            return {"error": str(e)}
    
    async def schedule_comprehensive_analysis(
        self,
        background_tasks: BackgroundTasks,
        memory_type: str = None,
        time_window: int = 24
    ) -> Dict[str, Any]:
        """종합 분석 스케줄링"""
        try:
            analysis_id = f"comprehensive_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            # 백그라운드 작업 등록
            background_tasks.add_task(
                self._execute_comprehensive_analysis,
                analysis_id,
                memory_type,
                time_window
            )
            
            # 상태 초기화
            self.analysis_status[analysis_id] = "scheduled"
            
            log_important_event(
                f"종합 분석 스케줄링: {analysis_id}",
                f"타입: {memory_type}, 시간창: {time_window}시간",
                importance_score=70
            )
            
            return {
                "analysis_id": analysis_id,
                "status": "scheduled",
                "type": "comprehensive_analysis",
                "parameters": {
                    "memory_type": memory_type,
                    "time_window": time_window
                }
            }
            
        except Exception as e:
            logger.error(f"종합 분석 스케줄링 실패: {e}")
            return {"error": str(e)}
    
    async def get_analysis_status(self, analysis_id: str) -> Dict[str, Any]:
        """분석 상태 조회"""
        try:
            status = self.analysis_status.get(analysis_id, "not_found")
            result = self.completed_analyses.get(analysis_id, {})
            
            return {
                "analysis_id": analysis_id,
                "status": status,
                "result": result if status == "completed" else None,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"분석 상태 조회 실패: {e}")
            return {"error": str(e)}
    
    async def get_all_analysis_status(self) -> Dict[str, Any]:
        """모든 분석 상태 조회"""
        try:
            return {
                "total_analyses": len(self.analysis_status),
                "completed": len([s for s in self.analysis_status.values() if s == "completed"]),
                "running": len([s for s in self.analysis_status.values() if s == "running"]),
                "scheduled": len([s for s in self.analysis_status.values() if s == "scheduled"]),
                "analyses": self.analysis_status
            }
            
        except Exception as e:
            logger.error(f"전체 분석 상태 조회 실패: {e}")
            return {"error": str(e)}
    
    # 백그라운드 실행 메서드들
    async def _execute_pattern_analysis(
        self,
        analysis_id: str,
        memory_type: str = None,
        time_window: int = 24,
        min_frequency: int = 3
    ):
        """패턴 분석 실행 (백그라운드)"""
        try:
            self.analysis_status[analysis_id] = "running"
            
            # 데이터베이스 세션 생성
            db = next(get_db_session())
            from .memory_service import MemoryService
            from .intelligent_analysis_service import intelligent_analysis_service
            
            memory_service = MemoryService(db)
            
            # 패턴 분석 실행
            result = intelligent_analysis_service.analyze_memory_patterns(
                memory_type=memory_type,
                time_window=time_window,
                min_frequency=min_frequency
            )
            
            # 결과 저장
            self.completed_analyses[analysis_id] = result
            self.analysis_status[analysis_id] = "completed"
            
            log_important_event(
                f"패턴 분석 완료: {analysis_id}",
                f"결과: {len(result.get('patterns', []))}개 패턴 발견",
                importance_score=65
            )
            
        except Exception as e:
            logger.error(f"패턴 분석 실행 실패: {e}")
            self.analysis_status[analysis_id] = "failed"
            self.completed_analyses[analysis_id] = {"error": str(e)}
    
    async def _execute_correlation_analysis(
        self,
        analysis_id: str,
        memory_type: str = None,
        time_window: int = 24
    ):
        """상관관계 분석 실행 (백그라운드)"""
        try:
            self.analysis_status[analysis_id] = "running"
            
            # 데이터베이스 세션 생성
            db = next(get_db_session())
            from .memory_service import MemoryService
            from .intelligent_analysis_service import intelligent_analysis_service
            
            memory_service = MemoryService(db)
            
            # 상관관계 분석 실행
            result = intelligent_analysis_service.analyze_memory_correlations(
                memory_type=memory_type,
                time_window=time_window
            )
            
            # 결과 저장
            self.completed_analyses[analysis_id] = result
            self.analysis_status[analysis_id] = "completed"
            
            log_important_event(
                f"상관관계 분석 완료: {analysis_id}",
                f"결과: {len(result.get('correlations', []))}개 상관관계 발견",
                importance_score=60
            )
            
        except Exception as e:
            logger.error(f"상관관계 분석 실행 실패: {e}")
            self.analysis_status[analysis_id] = "failed"
            self.completed_analyses[analysis_id] = {"error": str(e)}
    
    async def _execute_performance_monitoring(
        self,
        analysis_id: str
    ):
        """성능 모니터링 실행 (백그라운드)"""
        try:
            self.analysis_status[analysis_id] = "running"
            
            # 데이터베이스 세션 생성
            db = next(get_db_session())
            from .memory_service import MemoryService
            from .advanced_memory_service import advanced_memory_service
            
            memory_service = MemoryService(db)
            
            # 성능 모니터링 실행
            result = advanced_memory_service.monitor_performance()
            
            # 결과 저장
            self.completed_analyses[analysis_id] = result
            self.analysis_status[analysis_id] = "completed"
            
            log_system_event(
                f"성능 모니터링 완료: {analysis_id}",
                f"총 메모리: {result.get('total_memories', 0)}개",
                importance_score=45
            )
            
        except Exception as e:
            logger.error(f"성능 모니터링 실행 실패: {e}")
            self.analysis_status[analysis_id] = "failed"
            self.completed_analyses[analysis_id] = {"error": str(e)}
    
    async def _execute_comprehensive_analysis(
        self,
        analysis_id: str,
        memory_type: str = None,
        time_window: int = 24
    ):
        """종합 분석 실행 (백그라운드)"""
        try:
            self.analysis_status[analysis_id] = "running"
            
            # 데이터베이스 세션 생성
            db = next(get_db_session())
            from .memory_service import MemoryService
            from .intelligent_analysis_service import intelligent_analysis_service
            from .advanced_memory_service import advanced_memory_service
            
            memory_service = MemoryService(db)
            
            # 종합 분석 실행
            pattern_result = intelligent_analysis_service.analyze_memory_patterns(
                memory_type=memory_type,
                time_window=time_window
            )
            
            correlation_result = intelligent_analysis_service.analyze_memory_correlations(
                memory_type=memory_type,
                time_window=time_window
            )
            
            performance_result = advanced_memory_service.monitor_performance()
            
            # 종합 결과 구성
            comprehensive_result = {
                "analysis_timestamp": datetime.now().isoformat(),
                "pattern_analysis": pattern_result,
                "correlation_analysis": correlation_result,
                "performance_monitoring": performance_result,
                "summary": {
                    "total_patterns": len(pattern_result.get('patterns', [])),
                    "total_correlations": len(correlation_result.get('correlations', [])),
                    "total_memories": performance_result.get('total_memories', 0)
                }
            }
            
            # 결과 저장
            self.completed_analyses[analysis_id] = comprehensive_result
            self.analysis_status[analysis_id] = "completed"
            
            log_important_event(
                f"종합 분석 완료: {analysis_id}",
                f"패턴: {comprehensive_result['summary']['total_patterns']}개, 상관관계: {comprehensive_result['summary']['total_correlations']}개",
                importance_score=75
            )
            
        except Exception as e:
            logger.error(f"종합 분석 실행 실패: {e}")
            self.analysis_status[analysis_id] = "failed"
            self.completed_analyses[analysis_id] = {"error": str(e)}

# 전역 인스턴스
async_analysis_service = AsyncAnalysisService() 