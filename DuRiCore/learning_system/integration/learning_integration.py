#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DuRiCore Phase 2-3: 학습 통합 시스템 (Learning Integration System)

모든 학습 전략들을 통합하고 조율하는 시스템입니다.
- 학습 전략 통합
- 학습 프로세스 조율
- 학습 결과 통합
- 학습 성과 최적화
"""

import json
import time
import logging
import asyncio
from typing import Dict, List, Any, Optional, Tuple, Union
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from collections import defaultdict
import numpy as np

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class IntegrationType(Enum):
    """통합 유형"""
    SEQUENTIAL = "sequential"  # 순차적 통합
    PARALLEL = "parallel"      # 병렬적 통합
    HIERARCHICAL = "hierarchical"  # 계층적 통합
    ADAPTIVE = "adaptive"      # 적응적 통합

class IntegrationStatus(Enum):
    """통합 상태"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"

@dataclass
class LearningStrategyResult:
    """학습 전략 결과"""
    strategy_id: str
    strategy_name: str
    strategy_type: str
    success: bool
    performance_score: float
    duration: float
    insights: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)

@dataclass
class IntegrationSession:
    """통합 세션"""
    session_id: str
    integration_type: IntegrationType
    start_time: datetime
    end_time: Optional[datetime] = None
    duration: Optional[float] = None
    strategies_executed: int = 0
    successful_strategies: int = 0
    overall_performance: float = 0.0
    integration_insights: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)

@dataclass
class IntegratedLearningResult:
    """통합 학습 결과"""
    result_id: str
    session_id: str
    strategy_results: List[LearningStrategyResult]
    overall_performance: float
    integration_quality: float
    learning_insights: List[str] = field(default_factory=list)
    optimization_suggestions: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)

class LearningIntegrationSystem:
    """학습 통합 시스템"""
    
    def __init__(self):
        """초기화"""
        self.strategy_results: List[LearningStrategyResult] = []
        self.integration_sessions: List[IntegrationSession] = []
        self.integrated_results: List[IntegratedLearningResult] = []
        
        # 성능 메트릭
        self.performance_metrics = {
            'total_integration_sessions': 0,
            'successful_integration_sessions': 0,
            'average_integration_quality': 0.0,
            'average_overall_performance': 0.0,
            'total_strategies_executed': 0,
            'successful_strategies': 0
        }
        
        logger.info("학습 통합 시스템 초기화 완료")
    
    async def integrate_learning_strategies(self, strategies: List[Dict[str, Any]], 
                                          integration_type: IntegrationType = IntegrationType.ADAPTIVE) -> str:
        """학습 전략 통합"""
        session_id = f"integration_session_{int(time.time())}_{integration_type.value}"
        start_time = datetime.now()
        
        try:
            # 통합 세션 생성
            session = IntegrationSession(
                session_id=session_id,
                integration_type=integration_type,
                start_time=start_time
            )
            
            # 전략별 실행
            strategy_results = []
            for strategy in strategies:
                result = await self._execute_learning_strategy(strategy)
                strategy_results.append(result)
                
                if result.success:
                    session.successful_strategies += 1
                session.strategies_executed += 1
            
            # 통합 결과 생성
            integrated_result = await self._create_integrated_result(session_id, strategy_results)
            
            # 세션 완료
            end_time = datetime.now()
            session.end_time = end_time
            session.duration = (end_time - start_time).total_seconds()
            session.overall_performance = integrated_result.overall_performance
            
            # 결과 저장
            self.strategy_results.extend(strategy_results)
            self.integration_sessions.append(session)
            self.integrated_results.append(integrated_result)
            
            # 성능 메트릭 업데이트
            await self._update_performance_metrics(session, integrated_result)
            
            logger.info(f"학습 전략 통합 완료: {session_id} (성과: {integrated_result.overall_performance:.2f})")
            return session_id
            
        except Exception as e:
            logger.error(f"학습 전략 통합 실패: {e}")
            return ""
    
    async def _execute_learning_strategy(self, strategy: Dict[str, Any]) -> LearningStrategyResult:
        """학습 전략 실행"""
        strategy_id = strategy.get('strategy_id', f"strategy_{int(time.time())}")
        strategy_name = strategy.get('strategy_name', 'Unknown Strategy')
        strategy_type = strategy.get('strategy_type', 'general')
        
        start_time = time.time()
        
        try:
            # 전략 실행 시뮬레이션
            await asyncio.sleep(0.1)  # 실제 실행 시간 시뮬레이션
            
            # 성과 점수 계산
            performance_score = strategy.get('performance_score', 0.7)
            success = performance_score > 0.5
            
            # 통찰 생성
            insights = await self._generate_strategy_insights(strategy)
            
            duration = time.time() - start_time
            
            result = LearningStrategyResult(
                strategy_id=strategy_id,
                strategy_name=strategy_name,
                strategy_type=strategy_type,
                success=success,
                performance_score=performance_score,
                duration=duration,
                insights=insights,
                metadata=strategy
            )
            
            return result
            
        except Exception as e:
            logger.error(f"전략 실행 실패: {strategy_name} - {e}")
            return LearningStrategyResult(
                strategy_id=strategy_id,
                strategy_name=strategy_name,
                strategy_type=strategy_type,
                success=False,
                performance_score=0.0,
                duration=time.time() - start_time,
                insights=[f"실행 실패: {e}"],
                metadata=strategy
            )
    
    async def _generate_strategy_insights(self, strategy: Dict[str, Any]) -> List[str]:
        """전략 통찰 생성"""
        insights = []
        
        strategy_type = strategy.get('strategy_type', 'general')
        
        if strategy_type == 'self_directed':
            insights.append("자기 주도적 학습을 통해 독립적인 학습 능력이 향상되었습니다.")
        elif strategy_type == 'adaptive':
            insights.append("적응적 학습을 통해 상황에 맞는 학습 방식을 적용했습니다.")
        elif strategy_type == 'meta_cognition':
            insights.append("메타 인식을 통해 학습 과정을 체계적으로 분석했습니다.")
        elif strategy_type == 'cognitive_meta':
            insights.append("인지 메타 학습을 통해 학습 패턴을 최적화했습니다.")
        else:
            insights.append("일반적인 학습 전략을 통해 지식을 획득했습니다.")
        
        return insights
    
    async def _create_integrated_result(self, session_id: str, 
                                      strategy_results: List[LearningStrategyResult]) -> IntegratedLearningResult:
        """통합 결과 생성"""
        result_id = f"integrated_result_{int(time.time())}_{session_id}"
        
        # 전체 성과 계산
        if strategy_results:
            overall_performance = sum(r.performance_score for r in strategy_results) / len(strategy_results)
        else:
            overall_performance = 0.0
        
        # 통합 품질 계산
        integration_quality = await self._calculate_integration_quality(strategy_results)
        
        # 학습 통찰 수집
        learning_insights = []
        for result in strategy_results:
            learning_insights.extend(result.insights)
        
        # 최적화 제안 생성
        optimization_suggestions = await self._generate_optimization_suggestions(strategy_results)
        
        integrated_result = IntegratedLearningResult(
            result_id=result_id,
            session_id=session_id,
            strategy_results=strategy_results,
            overall_performance=overall_performance,
            integration_quality=integration_quality,
            learning_insights=learning_insights,
            optimization_suggestions=optimization_suggestions
        )
        
        return integrated_result
    
    async def _calculate_integration_quality(self, strategy_results: List[LearningStrategyResult]) -> float:
        """통합 품질 계산"""
        if not strategy_results:
            return 0.0
        
        # 성공률 기반 품질 계산
        success_rate = sum(1 for r in strategy_results if r.success) / len(strategy_results)
        
        # 성과 점수 기반 품질 계산
        average_performance = sum(r.performance_score for r in strategy_results) / len(strategy_results)
        
        # 통합 품질은 성공률과 평균 성과의 조합
        integration_quality = (success_rate * 0.6) + (average_performance * 0.4)
        
        return integration_quality
    
    async def _generate_optimization_suggestions(self, strategy_results: List[LearningStrategyResult]) -> List[str]:
        """최적화 제안 생성"""
        suggestions = []
        
        # 성과가 낮은 전략들에 대한 제안
        low_performance_strategies = [r for r in strategy_results if r.performance_score < 0.6]
        if low_performance_strategies:
            suggestions.append(f"{len(low_performance_strategies)}개 전략의 성과 개선이 필요합니다.")
        
        # 실패한 전략들에 대한 제안
        failed_strategies = [r for r in strategy_results if not r.success]
        if failed_strategies:
            suggestions.append(f"{len(failed_strategies)}개 전략의 재설계가 필요합니다.")
        
        # 전반적인 최적화 제안
        if strategy_results:
            avg_performance = sum(r.performance_score for r in strategy_results) / len(strategy_results)
            if avg_performance < 0.7:
                suggestions.append("전체적인 학습 전략 최적화가 권장됩니다.")
        
        return suggestions
    
    async def _update_performance_metrics(self, session: IntegrationSession, 
                                        integrated_result: IntegratedLearningResult):
        """성능 메트릭 업데이트"""
        self.performance_metrics['total_integration_sessions'] += 1
        
        if session.successful_strategies > 0:
            self.performance_metrics['successful_integration_sessions'] += 1
        
        self.performance_metrics['total_strategies_executed'] += session.strategies_executed
        self.performance_metrics['successful_strategies'] += session.successful_strategies
        
        # 평균 통합 품질 업데이트
        all_qualities = [r.integration_quality for r in self.integrated_results]
        if all_qualities:
            self.performance_metrics['average_integration_quality'] = sum(all_qualities) / len(all_qualities)
        
        # 평균 전체 성과 업데이트
        all_performances = [r.overall_performance for r in self.integrated_results]
        if all_performances:
            self.performance_metrics['average_overall_performance'] = sum(all_performances) / len(all_performances)
    
    async def get_integration_status(self, session_id: str = None) -> Dict[str, Any]:
        """통합 상태 조회"""
        if session_id:
            # 특정 세션 상태 조회
            for session in self.integration_sessions:
                if session.session_id == session_id:
                    return {
                        "session_id": session.session_id,
                        "integration_type": session.integration_type.value,
                        "status": "completed" if session.end_time else "in_progress",
                        "strategies_executed": session.strategies_executed,
                        "successful_strategies": session.successful_strategies,
                        "overall_performance": session.overall_performance,
                        "duration": session.duration
                    }
            return {"error": "세션을 찾을 수 없음"}
        
        # 전체 상태 반환
        return {
            "total_sessions": len(self.integration_sessions),
            "total_strategies": len(self.strategy_results),
            "total_integrated_results": len(self.integrated_results),
            "performance_metrics": self.performance_metrics,
            "recent_sessions": [
                {
                    "session_id": s.session_id,
                    "integration_type": s.integration_type.value,
                    "strategies_executed": s.strategies_executed,
                    "successful_strategies": s.successful_strategies,
                    "overall_performance": s.overall_performance,
                    "duration": s.duration
                }
                for s in self.integration_sessions[-5:]  # 최근 5개 세션
            ]
        }
    
    async def get_integration_report(self) -> Dict[str, Any]:
        """통합 리포트 생성"""
        if not self.integrated_results:
            return {"error": "통합 결과가 없습니다"}
        
        # 최근 결과 분석
        recent_results = self.integrated_results[-10:]  # 최근 10개 결과
        
        avg_overall_performance = sum(r.overall_performance for r in recent_results) / len(recent_results)
        avg_integration_quality = sum(r.integration_quality for r in recent_results) / len(recent_results)
        
        # 전략별 성과 분석
        strategy_performance = defaultdict(list)
        for result in recent_results:
            for strategy_result in result.strategy_results:
                strategy_performance[strategy_result.strategy_type].append(strategy_result.performance_score)
        
        strategy_avg_performance = {}
        for strategy_type, scores in strategy_performance.items():
            strategy_avg_performance[strategy_type] = sum(scores) / len(scores)
        
        return {
            "performance_summary": {
                "average_overall_performance": avg_overall_performance,
                "average_integration_quality": avg_integration_quality,
                "total_integrated_results": len(self.integrated_results)
            },
            "strategy_performance": strategy_avg_performance,
            "recent_results": [
                {
                    "result_id": r.result_id,
                    "session_id": r.session_id,
                    "overall_performance": r.overall_performance,
                    "integration_quality": r.integration_quality,
                    "strategies_count": len(r.strategy_results)
                }
                for r in recent_results
            ]
        }
    
    async def optimize_integration_process(self) -> Dict[str, Any]:
        """통합 프로세스 최적화"""
        if not self.integrated_results:
            return {"error": "최적화할 데이터가 없습니다"}
        
        # 최적화 분석
        optimization_analysis = {
            "total_results": len(self.integrated_results),
            "average_performance": self.performance_metrics['average_overall_performance'],
            "average_quality": self.performance_metrics['average_integration_quality'],
            "success_rate": self.performance_metrics['successful_strategies'] / max(self.performance_metrics['total_strategies_executed'], 1)
        }
        
        # 최적화 제안
        optimization_suggestions = []
        
        if optimization_analysis['average_performance'] < 0.7:
            optimization_suggestions.append("전체적인 성과 개선이 필요합니다.")
        
        if optimization_analysis['average_quality'] < 0.7:
            optimization_suggestions.append("통합 품질 향상이 필요합니다.")
        
        if optimization_analysis['success_rate'] < 0.8:
            optimization_suggestions.append("전략 성공률 개선이 필요합니다.")
        
        return {
            "optimization_analysis": optimization_analysis,
            "optimization_suggestions": optimization_suggestions,
            "optimization_status": "completed"
        }
