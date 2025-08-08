"""
🧠 Insight Engine 자기 반영 시스템
목표: Insight Engine이 자신의 실패를 반영하고 학습하는 구조
"""

import logging
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum
from datetime import datetime, timedelta
import json
import random

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class InsightOutcome(Enum):
    """통찰 결과"""
    SUCCESS = "success"
    PARTIAL_SUCCESS = "partial_success"
    FAILURE = "failure"
    NO_INSIGHT = "no_insight"

class ReflectionType(Enum):
    """반영 유형"""
    SESSION_ANALYSIS = "session_analysis"
    PATTERN_RECOGNITION = "pattern_recognition"
    STRATEGY_ADJUSTMENT = "strategy_adjustment"
    PARAMETER_OPTIMIZATION = "parameter_optimization"

@dataclass
class InsightSessionRecord:
    """통찰 세션 기록"""
    session_id: str
    problem: str
    trigger_type: str
    phases_completed: List[str]
    candidates_generated: int
    final_insight: Optional[str]
    outcome: InsightOutcome
    duration: float
    confidence: float
    timestamp: datetime

@dataclass
class ReflectionInsight:
    """반영 통찰"""
    reflection_type: ReflectionType
    insight: str
    confidence: float
    action_plan: str
    expected_improvement: float
    timestamp: datetime

class InsightSelfReflector:
    """Insight Engine 자기 반영기"""
    
    def __init__(self):
        self.session_history = []
        self.failure_patterns = {}
        self.success_patterns = {}
        self.strategy_adjustments = []
        self.parameter_history = {
            "pause_duration": 3.0,
            "candidate_count": 3,
            "confidence_threshold": 0.6,
            "evaluation_weights": {
                "novelty": 0.3,
                "feasibility": 0.25,
                "impact": 0.25,
                "risk": 0.2
            }
        }
        
    def record_session(self, session_record: InsightSessionRecord):
        """세션 기록"""
        self.session_history.append(session_record)
        logger.info(f"📝 세션 기록: {session_record.session_id} - {session_record.outcome.value}")
        
    def analyze_recent_sessions(self, hours: int = 24) -> Dict[str, Any]:
        """최근 세션 분석"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        recent_sessions = [s for s in self.session_history if s.timestamp > cutoff_time]
        
        if not recent_sessions:
            return {"error": "분석할 세션이 없음"}
            
        # 성공률 계산
        success_count = len([s for s in recent_sessions if s.outcome == InsightOutcome.SUCCESS])
        total_count = len(recent_sessions)
        success_rate = success_count / total_count if total_count > 0 else 0
        
        # 평균 지표
        avg_duration = sum(s.duration for s in recent_sessions) / len(recent_sessions)
        avg_confidence = sum(s.confidence for s in recent_sessions if s.confidence) / len(recent_sessions)
        avg_candidates = sum(s.candidates_generated for s in recent_sessions) / len(recent_sessions)
        
        # 실패 패턴 분석
        failure_sessions = [s for s in recent_sessions if s.outcome in [InsightOutcome.FAILURE, InsightOutcome.NO_INSIGHT]]
        failure_patterns = self._analyze_failure_patterns(failure_sessions)
        
        # 성공 패턴 분석
        success_sessions = [s for s in recent_sessions if s.outcome == InsightOutcome.SUCCESS]
        success_patterns = self._analyze_success_patterns(success_sessions)
        
        return {
            "total_sessions": total_count,
            "success_rate": success_rate,
            "avg_duration": avg_duration,
            "avg_confidence": avg_confidence,
            "avg_candidates": avg_candidates,
            "failure_patterns": failure_patterns,
            "success_patterns": success_patterns
        }
        
    def _analyze_failure_patterns(self, failure_sessions: List[InsightSessionRecord]) -> Dict[str, Any]:
        """실패 패턴 분석"""
        if not failure_sessions:
            return {}
            
        patterns = {
            "common_problems": {},
            "phase_failures": {},
            "low_confidence_issues": 0,
            "timeout_issues": 0
        }
        
        # 문제 유형별 실패 횟수
        for session in failure_sessions:
            problem_type = self._categorize_problem(session.problem)
            patterns["common_problems"][problem_type] = patterns["common_problems"].get(problem_type, 0) + 1
            
            # 단계별 실패 분석
            for phase in session.phases_completed:
                patterns["phase_failures"][phase] = patterns["phase_failures"].get(phase, 0) + 1
                
            # 낮은 신뢰도 문제
            if session.confidence and session.confidence < 0.3:
                patterns["low_confidence_issues"] += 1
                
            # 시간 초과 문제
            if session.duration > 10.0:
                patterns["timeout_issues"] += 1
                
        return patterns
        
    def _analyze_success_patterns(self, success_sessions: List[InsightSessionRecord]) -> Dict[str, Any]:
        """성공 패턴 분석"""
        if not success_sessions:
            return {}
            
        patterns = {
            "optimal_duration": sum(s.duration for s in success_sessions) / len(success_sessions),
            "optimal_confidence": sum(s.confidence for s in success_sessions) / len(success_sessions),
            "optimal_candidates": sum(s.candidates_generated for s in success_sessions) / len(success_sessions),
            "successful_phases": {}
        }
        
        # 성공한 단계들
        for session in success_sessions:
            for phase in session.phases_completed:
                patterns["successful_phases"][phase] = patterns["successful_phases"].get(phase, 0) + 1
                
        return patterns
        
    def _categorize_problem(self, problem: str) -> str:
        """문제 유형 분류"""
        problem_lower = problem.lower()
        
        if any(word in problem_lower for word in ["학습", "성능", "효율"]):
            return "학습 성능 문제"
        elif any(word in problem_lower for word in ["메모리", "메모리 사용량"]):
            return "메모리 문제"
        elif any(word in problem_lower for word in ["비용", "예산", "LLM"]):
            return "비용 문제"
        elif any(word in problem_lower for word in ["응답", "시간", "속도"]):
            return "성능 문제"
        else:
            return "기타 문제"
            
    def generate_reflection_insights(self) -> List[ReflectionInsight]:
        """반영 통찰 생성"""
        logger.info("🧠 자기 반영 통찰 생성 시작")
        
        insights = []
        
        # 1. 세션 분석 기반 통찰
        session_analysis = self.analyze_recent_sessions()
        if "error" not in session_analysis:
            if session_analysis["success_rate"] < 0.5:
                insights.append(ReflectionInsight(
                    reflection_type=ReflectionType.SESSION_ANALYSIS,
                    insight="통찰 성공률이 낮음 - 파라미터 조정 필요",
                    confidence=0.8,
                    action_plan="평가 기준 완화 및 후보 수 증가",
                    expected_improvement=0.2,
                    timestamp=datetime.now()
                ))
                
        # 2. 패턴 인식 기반 통찰
        pattern_insight = self._recognize_patterns()
        if pattern_insight:
            insights.append(pattern_insight)
            
        # 3. 전략 조정 기반 통찰
        strategy_insight = self._adjust_strategies()
        if strategy_insight:
            insights.append(strategy_insight)
            
        # 4. 파라미터 최적화 기반 통찰
        parameter_insight = self._optimize_parameters()
        if parameter_insight:
            insights.append(parameter_insight)
            
        logger.info(f"🧠 {len(insights)}개의 반영 통찰 생성")
        return insights
        
    def _recognize_patterns(self) -> Optional[ReflectionInsight]:
        """패턴 인식"""
        if len(self.session_history) < 5:
            return None
            
        # 최근 실패 패턴 분석
        recent_failures = [s for s in self.session_history[-10:] if s.outcome in [InsightOutcome.FAILURE, InsightOutcome.NO_INSIGHT]]
        
        if len(recent_failures) >= 3:
            common_phase = max(set([phase for s in recent_failures for phase in s.phases_completed]), 
                             key=lambda x: sum(1 for s in recent_failures if x in s.phases_completed))
            
            return ReflectionInsight(
                reflection_type=ReflectionType.PATTERN_RECOGNITION,
                insight=f"반복적 실패 패턴 발견 - {common_phase} 단계에서 문제 발생",
                confidence=0.7,
                action_plan=f"{common_phase} 단계 개선 알고리즘 적용",
                expected_improvement=0.15,
                timestamp=datetime.now()
            )
        return None
        
    def _adjust_strategies(self) -> Optional[ReflectionInsight]:
        """전략 조정"""
        # 성공률이 낮을 때 전략 조정
        recent_sessions = self.session_history[-5:] if len(self.session_history) >= 5 else self.session_history
        if recent_sessions:
            success_rate = len([s for s in recent_sessions if s.outcome == InsightOutcome.SUCCESS]) / len(recent_sessions)
            
            if success_rate < 0.4:
                return ReflectionInsight(
                    reflection_type=ReflectionType.STRATEGY_ADJUSTMENT,
                    insight="성공률 저하로 인한 전략 조정 필요",
                    confidence=0.75,
                    action_plan="더 보수적인 평가 기준과 다양한 접근법 시도",
                    expected_improvement=0.25,
                    timestamp=datetime.now()
                )
        return None
        
    def _optimize_parameters(self) -> Optional[ReflectionInsight]:
        """파라미터 최적화"""
        # 성공한 세션들의 평균값을 기반으로 파라미터 조정
        successful_sessions = [s for s in self.session_history if s.outcome == InsightOutcome.SUCCESS]
        
        if len(successful_sessions) >= 3:
            avg_duration = sum(s.duration for s in successful_sessions) / len(successful_sessions)
            avg_confidence = sum(s.confidence for s in successful_sessions) / len(successful_sessions)
            
            # 현재 파라미터와 비교하여 조정 제안
            adjustments = []
            
            if abs(avg_duration - self.parameter_history["pause_duration"]) > 1.0:
                adjustments.append(f"일시정지 시간: {self.parameter_history['pause_duration']} → {avg_duration:.1f}")
                
            if abs(avg_confidence - self.parameter_history["confidence_threshold"]) > 0.1:
                adjustments.append(f"신뢰도 임계값: {self.parameter_history['confidence_threshold']} → {avg_confidence:.2f}")
                
            if adjustments:
                return ReflectionInsight(
                    reflection_type=ReflectionType.PARAMETER_OPTIMIZATION,
                    insight="성공 패턴 기반 파라미터 최적화",
                    confidence=0.8,
                    action_plan=f"파라미터 조정: {', '.join(adjustments)}",
                    expected_improvement=0.1,
                    timestamp=datetime.now()
                )
        return None
        
    def apply_reflection_insights(self, insights: List[ReflectionInsight]) -> Dict[str, Any]:
        """반영 통찰 적용"""
        logger.info(f"🔄 {len(insights)}개의 반영 통찰 적용")
        
        applied_changes = []
        
        for insight in insights:
            if insight.reflection_type == ReflectionType.PARAMETER_OPTIMIZATION:
                # 파라미터 조정
                if "일시정지 시간" in insight.action_plan:
                    new_duration = float(insight.action_plan.split("→")[1].strip().split()[0])
                    self.parameter_history["pause_duration"] = new_duration
                    applied_changes.append(f"일시정지 시간 조정: {new_duration}초")
                    
                if "신뢰도 임계값" in insight.action_plan:
                    new_threshold = float(insight.action_plan.split("→")[1].strip())
                    self.parameter_history["confidence_threshold"] = new_threshold
                    applied_changes.append(f"신뢰도 임계값 조정: {new_threshold}")
                    
            elif insight.reflection_type == ReflectionType.STRATEGY_ADJUSTMENT:
                # 전략 조정
                applied_changes.append("평가 기준 완화")
                self.parameter_history["evaluation_weights"]["feasibility"] += 0.1
                self.parameter_history["evaluation_weights"]["novelty"] -= 0.1
                
            elif insight.reflection_type == ReflectionType.PATTERN_RECOGNITION:
                # 패턴 인식 기반 조정
                applied_changes.append("실패 패턴 기반 알고리즘 개선")
                
        return {
            "applied_changes": applied_changes,
            "expected_improvement": sum(insight.expected_improvement for insight in insights) / len(insights) if insights else 0,
            "total_insights": len(insights)
        }
        
    def get_reflection_summary(self) -> Dict[str, Any]:
        """반영 요약"""
        recent_analysis = self.analyze_recent_sessions()
        recent_insights = self.generate_reflection_insights()
        
        return {
            "total_sessions": len(self.session_history),
            "recent_analysis": recent_analysis,
            "recent_insights": len(recent_insights),
            "parameter_history": self.parameter_history,
            "strategy_adjustments": len(self.strategy_adjustments)
        }

# 전역 인스턴스
_insight_reflector = None

def get_insight_reflector() -> InsightSelfReflector:
    """전역 반영기 인스턴스 반환"""
    global _insight_reflector
    if _insight_reflector is None:
        _insight_reflector = InsightSelfReflector()
    return _insight_reflector

if __name__ == "__main__":
    # 데모 실행
    reflector = get_insight_reflector()
    
    # 시뮬레이션 세션 기록
    sample_sessions = [
        InsightSessionRecord(
            session_id="test_001",
            problem="학습 성능 저하",
            trigger_type="repeated_failure",
            phases_completed=["cognitive_pause", "semantic_drift", "retrograde_reasoning"],
            candidates_generated=3,
            final_insight="방법론 혼합 전략",
            outcome=InsightOutcome.SUCCESS,
            duration=6.5,
            confidence=0.7,
            timestamp=datetime.now() - timedelta(hours=2)
        ),
        InsightSessionRecord(
            session_id="test_002",
            problem="메모리 사용량 증가",
            trigger_type="efficiency_drop",
            phases_completed=["cognitive_pause", "semantic_drift"],
            candidates_generated=2,
            final_insight=None,
            outcome=InsightOutcome.FAILURE,
            duration=4.2,
            confidence=0.3,
            timestamp=datetime.now() - timedelta(hours=1)
        )
    ]
    
    for session in sample_sessions:
        reflector.record_session(session)
    
    # 반영 통찰 생성
    insights = reflector.generate_reflection_insights()
    
    print(f"🧠 생성된 반영 통찰: {len(insights)}개")
    for i, insight in enumerate(insights, 1):
        print(f"   {i}. [{insight.reflection_type.value}] {insight.insight}")
        print(f"      액션: {insight.action_plan}")
        print(f"      예상 개선: {insight.expected_improvement:.1%}")
    
    # 통찰 적용
    applied = reflector.apply_reflection_insights(insights)
    print(f"\n🔄 적용된 변경사항: {applied['applied_changes']}")
    
    # 요약
    summary = reflector.get_reflection_summary()
    print(f"\n�� 반영 요약: {summary}") 