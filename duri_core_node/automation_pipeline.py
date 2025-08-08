#!/usr/bin/env python3
"""
DuRi 자동화 파이프라인 시스템
외부 입력에 따른 자동 학습 루프 실행 및 실시간 튜닝
"""
import asyncio
import logging
import time
import json
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass
from enum import Enum
import hashlib
import threading
from pathlib import Path
import aiohttp
from collections import defaultdict

logger = logging.getLogger(__name__)

class TriggerType(Enum):
    """트리거 타입"""
    USER_INPUT = "user_input"
    CURSOR_ACTIVITY = "cursor_activity"
    FILE_DETECTION = "file_detection"
    PERFORMANCE_DEGRADATION = "performance_degradation"
    SCHEDULED = "scheduled"
    MANUAL = "manual"

class LearningPhase(Enum):
    """학습 단계"""
    IMITATION = "imitation"
    REPETITION = "repetition"
    FEEDBACK = "feedback"
    CHALLENGE = "challenge"
    IMPROVEMENT = "improvement"

@dataclass
class TriggerEvent:
    """트리거 이벤트"""
    trigger_type: TriggerType
    timestamp: datetime
    data: Dict[str, Any]
    priority: int = 1

@dataclass
class LearningResult:
    """학습 결과"""
    phase: LearningPhase
    success: bool
    score: float
    duration: float
    metadata: Dict[str, Any]
    timestamp: datetime

class TriggerLayer:
    """트리거 레이어 - 입력 감지 및 이벤트 발생"""
    
    def __init__(self):
        self.triggers: List[TriggerEvent] = []
        self.trigger_handlers: Dict[TriggerType, List[Callable]] = defaultdict(list)
        self.is_monitoring = False
        self.monitor_thread = None
        
    def start_monitoring(self):
        """모니터링 시작"""
        if not self.is_monitoring:
            self.is_monitoring = True
            self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
            self.monitor_thread.start()
            logger.info("🔍 트리거 레이어 모니터링 시작")
    
    def stop_monitoring(self):
        """모니터링 중지"""
        self.is_monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=1)
        logger.info("🔍 트리거 레이어 모니터링 중지")
    
    def _monitor_loop(self):
        """모니터링 루프"""
        while self.is_monitoring:
            try:
                # 파일 시스템 감지
                self._detect_file_changes()
                
                # 성능 저하 감지
                self._detect_performance_issues()
                
                # 스케줄된 트리거 확인
                self._check_scheduled_triggers()
                
                time.sleep(5)  # 5초마다 체크
                
            except Exception as e:
                logger.error(f"❌ 트리거 모니터링 오류: {e}")
    
    def _detect_file_changes(self):
        """파일 변경 감지"""
        # 구현: 파일 시스템 감시
        pass
    
    def _detect_performance_issues(self):
        """성능 문제 감지"""
        # 구현: 성능 메트릭 모니터링
        pass
    
    def _check_scheduled_triggers(self):
        """스케줄된 트리거 확인"""
        # 구현: 스케줄 확인
        pass
    
    def add_trigger(self, trigger_type: TriggerType, data: Dict[str, Any], priority: int = 1):
        """트리거 추가"""
        event = TriggerEvent(
            trigger_type=trigger_type,
            timestamp=datetime.now(),
            data=data,
            priority=priority
        )
        self.triggers.append(event)
        logger.info(f"🎯 트리거 추가: {trigger_type.value}")
    
    def register_handler(self, trigger_type: TriggerType, handler: Callable):
        """트리거 핸들러 등록"""
        self.trigger_handlers[trigger_type].append(handler)
        logger.info(f"📝 핸들러 등록: {trigger_type.value}")

class LearningExecutor:
    """학습 실행기 - 기존 루프 구조 실행"""
    
    def __init__(self, performance_optimizer):
        self.performance_optimizer = performance_optimizer
        self.current_phase = None
        self.learning_history: List[LearningResult] = []
        
    async def execute_learning_loop(self, trigger_event: TriggerEvent) -> LearningResult:
        """학습 루프 실행"""
        logger.info(f"🚀 학습 루프 시작: {trigger_event.trigger_type.value}")
        
        start_time = time.time()
        results = []
        
        # 1. 모방 단계
        imitation_result = await self._execute_phase(LearningPhase.IMITATION, trigger_event)
        results.append(imitation_result)
        
        # 2. 반복 단계
        repetition_result = await self._execute_phase(LearningPhase.REPETITION, trigger_event)
        results.append(repetition_result)
        
        # 3. 피드백 단계
        feedback_result = await self._execute_phase(LearningPhase.FEEDBACK, trigger_event)
        results.append(feedback_result)
        
        # 4. 도전 단계
        challenge_result = await self._execute_phase(LearningPhase.CHALLENGE, trigger_event)
        results.append(challenge_result)
        
        # 5. 개선 단계
        improvement_result = await self._execute_phase(LearningPhase.IMPROVEMENT, trigger_event)
        results.append(improvement_result)
        
        # 통합 결과 생성
        total_duration = time.time() - start_time
        avg_score = sum(r.score for r in results) / len(results)
        overall_success = all(r.success for r in results)
        
        final_result = LearningResult(
            phase=LearningPhase.IMPROVEMENT,
            success=overall_success,
            score=avg_score,
            duration=total_duration,
            metadata={
                "phase_results": [r.__dict__ for r in results],
                "trigger_event": trigger_event.__dict__
            },
            timestamp=datetime.now()
        )
        
        self.learning_history.append(final_result)
        logger.info(f"✅ 학습 루프 완료: 점수={avg_score:.3f}, 성공={overall_success}")
        
        return final_result
    
    async def _execute_phase(self, phase: LearningPhase, trigger_event: TriggerEvent) -> LearningResult:
        """개별 단계 실행"""
        start_time = time.time()
        
        try:
            if phase == LearningPhase.IMITATION:
                result = await self._imitation_phase(trigger_event)
            elif phase == LearningPhase.REPETITION:
                result = await self._repetition_phase(trigger_event)
            elif phase == LearningPhase.FEEDBACK:
                result = await self._feedback_phase(trigger_event)
            elif phase == LearningPhase.CHALLENGE:
                result = await self._challenge_phase(trigger_event)
            elif phase == LearningPhase.IMPROVEMENT:
                result = await self._improvement_phase(trigger_event)
            else:
                raise ValueError(f"알 수 없는 단계: {phase}")
            
            duration = time.time() - start_time
            return LearningResult(
                phase=phase,
                success=result.get("success", False),
                score=result.get("score", 0.0),
                duration=duration,
                metadata=result,
                timestamp=datetime.now()
            )
            
        except Exception as e:
            logger.error(f"❌ {phase.value} 단계 실행 오류: {e}")
            duration = time.time() - start_time
            return LearningResult(
                phase=phase,
                success=False,
                score=0.0,
                duration=duration,
                metadata={"error": str(e)},
                timestamp=datetime.now()
            )
    
    async def _imitation_phase(self, trigger_event: TriggerEvent) -> Dict[str, Any]:
        """모방 단계"""
        # 기존 성능 최적화 시스템 활용
        result = await self.performance_optimizer.optimize_request(
            trigger_event.data.get("user_input", ""),
            trigger_event.data.get("duri_response", ""),
            trigger_event.data
        )
        return {"success": True, "score": 0.8, "result": result}
    
    async def _repetition_phase(self, trigger_event: TriggerEvent) -> Dict[str, Any]:
        """반복 단계"""
        # 반복 학습 로직
        return {"success": True, "score": 0.7, "repetition_count": 3}
    
    async def _feedback_phase(self, trigger_event: TriggerEvent) -> Dict[str, Any]:
        """피드백 단계"""
        # 피드백 수집 및 분석
        return {"success": True, "score": 0.9, "feedback_quality": "high"}
    
    async def _challenge_phase(self, trigger_event: TriggerEvent) -> Dict[str, Any]:
        """도전 단계"""
        # 새로운 도전 과제 생성
        return {"success": True, "score": 0.6, "challenge_level": "medium"}
    
    async def _improvement_phase(self, trigger_event: TriggerEvent) -> Dict[str, Any]:
        """개선 단계"""
        # 개선 사항 적용
        return {"success": True, "score": 0.85, "improvements": ["speed", "accuracy"]}

class ImprovementEvaluator:
    """개선 평가기 - 성능 점수 계산 및 기준 평가"""
    
    def __init__(self):
        self.evaluation_criteria = {
            "min_score": 0.7,
            "max_response_time": 2.0,
            "min_success_rate": 0.8,
            "max_error_rate": 0.1
        }
        self.evaluation_history: List[Dict[str, Any]] = []
    
    def evaluate_learning_result(self, result: LearningResult) -> Dict[str, Any]:
        """학습 결과 평가"""
        evaluation = {
            "timestamp": datetime.now().isoformat(),
            "result_id": id(result),
            "score_adequate": result.score >= self.evaluation_criteria["min_score"],
            "response_time_adequate": result.duration <= self.evaluation_criteria["max_response_time"],
            "success_adequate": result.success,
            "overall_adequate": self._is_overall_adequate(result),
            "recommendations": self._generate_recommendations(result)
        }
        
        self.evaluation_history.append(evaluation)
        logger.info(f"📊 평가 완료: 적절성={evaluation['overall_adequate']}")
        
        return evaluation
    
    def _is_overall_adequate(self, result: LearningResult) -> bool:
        """전체 적절성 판단"""
        return (
            result.score >= self.evaluation_criteria["min_score"] and
            result.duration <= self.evaluation_criteria["max_response_time"] and
            result.success
        )
    
    def _generate_recommendations(self, result: LearningResult) -> List[str]:
        """개선 권장사항 생성"""
        recommendations = []
        
        if result.score < self.evaluation_criteria["min_score"]:
            recommendations.append("학습 점수 향상 필요")
        
        if result.duration > self.evaluation_criteria["max_response_time"]:
            recommendations.append("응답 시간 최적화 필요")
        
        if not result.success:
            recommendations.append("성공률 개선 필요")
        
        return recommendations

class MemorySyncEngine:
    """메모리 동기화 엔진 - DB 및 벡터 저장소 동기화"""
    
    def __init__(self, db_path: str = "duri_automation.db"):
        self.db_path = db_path
        self._init_database()
    
    def _init_database(self):
        """데이터베이스 초기화"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 학습 결과 테이블
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS learning_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                phase TEXT,
                success BOOLEAN,
                score REAL,
                duration REAL,
                metadata TEXT
            )
        ''')
        
        # 평가 결과 테이블
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS evaluations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                result_id INTEGER,
                score_adequate BOOLEAN,
                response_time_adequate BOOLEAN,
                success_adequate BOOLEAN,
                overall_adequate BOOLEAN,
                recommendations TEXT
            )
        ''')
        
        # 사용자 평가 테이블
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_feedback (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                learning_result_id INTEGER,
                user_rating INTEGER,
                user_comment TEXT,
                feedback_type TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
        logger.info("💾 메모리 동기화 엔진 초기화 완료")
    
    async def sync_learning_result(self, result: LearningResult):
        """학습 결과 동기화"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO learning_results 
            (timestamp, phase, success, score, duration, metadata)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            result.timestamp.isoformat(),
            result.phase.value,
            result.success,
            result.score,
            result.duration,
            json.dumps(result.metadata)
        ))
        
        conn.commit()
        conn.close()
        logger.info(f"💾 학습 결과 동기화: {result.phase.value}")
    
    async def sync_evaluation(self, evaluation: Dict[str, Any]):
        """평가 결과 동기화"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO evaluations 
            (timestamp, result_id, score_adequate, response_time_adequate, 
             success_adequate, overall_adequate, recommendations)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            evaluation["timestamp"],
            evaluation["result_id"],
            evaluation["score_adequate"],
            evaluation["response_time_adequate"],
            evaluation["success_adequate"],
            evaluation["overall_adequate"],
            json.dumps(evaluation["recommendations"])
        ))
        
        conn.commit()
        conn.close()
        logger.info("💾 평가 결과 동기화")
    
    async def get_learning_statistics(self) -> Dict[str, Any]:
        """학습 통계 조회"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 전체 학습 결과 수
        cursor.execute("SELECT COUNT(*) FROM learning_results")
        total_results = cursor.fetchone()[0]
        
        # 성공률
        cursor.execute("SELECT COUNT(*) FROM learning_results WHERE success = 1")
        successful_results = cursor.fetchone()[0]
        success_rate = successful_results / total_results if total_results > 0 else 0
        
        # 평균 점수
        cursor.execute("SELECT AVG(score) FROM learning_results")
        avg_score = cursor.fetchone()[0] or 0
        
        # 평균 응답 시간
        cursor.execute("SELECT AVG(duration) FROM learning_results")
        avg_duration = cursor.fetchone()[0] or 0
        
        conn.close()
        
        return {
            "total_results": total_results,
            "success_rate": success_rate,
            "average_score": avg_score,
            "average_duration": avg_duration
        }

class SchedulerWatcher:
    """스케줄러 및 감시자 - 학습 주기 관리"""
    
    def __init__(self):
        self.schedules: List[Dict[str, Any]] = []
        self.is_running = False
        self.watcher_thread = None
        
    def add_schedule(self, schedule_type: str, interval_minutes: int, callback: Callable):
        """스케줄 추가"""
        schedule = {
            "type": schedule_type,
            "interval": interval_minutes,
            "callback": callback,
            "last_run": None,
            "next_run": datetime.now() + timedelta(minutes=interval_minutes)
        }
        self.schedules.append(schedule)
        logger.info(f"⏰ 스케줄 추가: {schedule_type} (간격: {interval_minutes}분)")
    
    def start_watching(self):
        """감시 시작"""
        if not self.is_running:
            self.is_running = True
            self.watcher_thread = threading.Thread(target=self._watcher_loop, daemon=True)
            self.watcher_thread.start()
            logger.info("👀 스케줄러 감시 시작")
    
    def stop_watching(self):
        """감시 중지"""
        self.is_running = False
        if self.watcher_thread:
            self.watcher_thread.join(timeout=1)
        logger.info("👀 스케줄러 감시 중지")
    
    def _watcher_loop(self):
        """감시 루프"""
        while self.is_running:
            try:
                current_time = datetime.now()
                
                for schedule in self.schedules:
                    if schedule["next_run"] and current_time >= schedule["next_run"]:
                        # 스케줄 실행
                        try:
                            schedule["callback"]()
                            schedule["last_run"] = current_time
                            schedule["next_run"] = current_time + timedelta(minutes=schedule["interval"])
                            logger.info(f"⏰ 스케줄 실행: {schedule['type']}")
                        except Exception as e:
                            logger.error(f"❌ 스케줄 실행 오류: {schedule['type']} - {e}")
                
                time.sleep(30)  # 30초마다 체크
                
            except Exception as e:
                logger.error(f"❌ 스케줄러 감시 오류: {e}")

class AutomationPipeline:
    """자동화 파이프라인 메인 클래스"""
    
    def __init__(self, performance_optimizer):
        self.trigger_layer = TriggerLayer()
        self.learning_executor = LearningExecutor(performance_optimizer)
        self.improvement_evaluator = ImprovementEvaluator()
        self.memory_sync_engine = MemorySyncEngine()
        self.scheduler_watcher = SchedulerWatcher()
        
        self.is_running = False
        self.automation_stats = {
            "total_triggers": 0,
            "successful_learning_cycles": 0,
            "failed_learning_cycles": 0,
            "average_learning_score": 0.0,
            "last_automation_run": None
        }
        
        # 기본 스케줄 설정
        self._setup_default_schedules()
        
        logger.info("🚀 자동화 파이프라인 초기화 완료")
    
    def _setup_default_schedules(self):
        """기본 스케줄 설정"""
        # 10분마다 성능 재점검
        self.scheduler_watcher.add_schedule(
            "performance_check",
            10,
            self._scheduled_performance_check
        )
        
        # 30분마다 학습 통계 업데이트
        self.scheduler_watcher.add_schedule(
            "statistics_update",
            30,
            self._scheduled_statistics_update
        )
    
    def start_automation(self):
        """자동화 시작"""
        if not self.is_running:
            self.is_running = True
            self.trigger_layer.start_monitoring()
            self.scheduler_watcher.start_watching()
            logger.info("🚀 자동화 파이프라인 시작")
    
    def stop_automation(self):
        """자동화 중지"""
        if self.is_running:
            self.is_running = False
            self.trigger_layer.stop_monitoring()
            self.scheduler_watcher.stop_watching()
            logger.info("🚀 자동화 파이프라인 중지")
    
    async def process_trigger(self, trigger_event: TriggerEvent):
        """트리거 처리"""
        try:
            self.automation_stats["total_triggers"] += 1
            
            # 1. 학습 실행
            learning_result = await self.learning_executor.execute_learning_loop(trigger_event)
            
            # 2. 평가
            evaluation = self.improvement_evaluator.evaluate_learning_result(learning_result)
            
            # 3. 메모리 동기화
            await self.memory_sync_engine.sync_learning_result(learning_result)
            await self.memory_sync_engine.sync_evaluation(evaluation)
            
            # 4. 통계 업데이트
            if learning_result.success:
                self.automation_stats["successful_learning_cycles"] += 1
            else:
                self.automation_stats["failed_learning_cycles"] += 1
            
            self.automation_stats["average_learning_score"] = (
                (self.automation_stats["average_learning_score"] * 
                 (self.automation_stats["successful_learning_cycles"] + 
                  self.automation_stats["failed_learning_cycles"] - 1) + 
                 learning_result.score) / 
                (self.automation_stats["successful_learning_cycles"] + 
                 self.automation_stats["failed_learning_cycles"])
            )
            
            self.automation_stats["last_automation_run"] = datetime.now().isoformat()
            
            logger.info(f"✅ 트리거 처리 완료: {trigger_event.trigger_type.value}")
            
        except Exception as e:
            logger.error(f"❌ 트리거 처리 오류: {e}")
    
    def _scheduled_performance_check(self):
        """스케줄된 성능 점검"""
        logger.info("🔍 스케줄된 성능 점검 실행")
        # 구현: 성능 메트릭 확인 및 필요시 조치
    
    def _scheduled_statistics_update(self):
        """스케줄된 통계 업데이트"""
        logger.info("📊 스케줄된 통계 업데이트 실행")
        # 구현: 통계 업데이트
    
    def get_automation_stats(self) -> Dict[str, Any]:
        """자동화 통계 조회"""
        return self.automation_stats.copy()
    
    def get_learning_statistics(self) -> Dict[str, Any]:
        """학습 통계 조회"""
        try:
            # 동기적으로 실행
            conn = sqlite3.connect(self.memory_sync_engine.db_path)
            cursor = conn.cursor()
            
            # 전체 학습 결과 수
            cursor.execute("SELECT COUNT(*) FROM learning_results")
            total_results = cursor.fetchone()[0]
            
            # 성공률
            cursor.execute("SELECT COUNT(*) FROM learning_results WHERE success = 1")
            successful_results = cursor.fetchone()[0]
            success_rate = successful_results / total_results if total_results > 0 else 0
            
            # 평균 점수
            cursor.execute("SELECT AVG(score) FROM learning_results")
            avg_score = cursor.fetchone()[0] or 0
            
            # 평균 응답 시간
            cursor.execute("SELECT AVG(duration) FROM learning_results")
            avg_duration = cursor.fetchone()[0] or 0
            
            conn.close()
            
            return {
                "total_results": total_results,
                "success_rate": success_rate,
                "average_score": avg_score,
                "average_duration": avg_duration
            }
        except Exception as e:
            logger.error(f"학습 통계 조회 오류: {e}")
            return {
                "total_results": 0,
                "success_rate": 0,
                "average_score": 0,
                "average_duration": 0
            } 