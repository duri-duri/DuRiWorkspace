"""
DuRi의 전략 연습 엔진

2-3단계 학습: 반복 → 피드백 기록
전략을 반복 적용하며 로그를 남기는 클래스입니다.
"""

import json
import logging
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


class PracticeType(Enum):
    """연습 유형"""

    REPETITION = "repetition"  # 단순 반복
    VARIATION = "variation"  # 변형 연습
    PROGRESSIVE = "progressive"  # 점진적 난이도 증가
    ADAPTIVE = "adaptive"  # 적응형 연습


@dataclass
class PracticeSession:
    """연습 세션"""

    strategy_id: str
    practice_type: PracticeType
    start_time: datetime
    end_time: Optional[datetime]
    iterations: int
    success_count: int
    failure_count: int
    performance_metrics: Dict[str, float]
    feedback_notes: List[str]
    confidence_change: float
    improvement_score: float = 0.0


@dataclass
class PracticeResult:
    """연습 결과"""

    session: PracticeSession
    strategy: Dict[str, Any]
    modified_strategy: Dict[str, Any]
    success_rate: float
    average_performance: float
    improvement_score: float
    recommendations: List[str]


class PracticeEngine:
    """
    DuRi의 전략 연습 엔진

    2-3단계 학습: 반복 → 피드백 기록
    전략을 반복 적용하며 로그를 남기는 클래스입니다.
    """

    def __init__(self):
        """PracticeEngine 초기화"""
        self.practice_sessions: List[PracticeSession] = []
        self.strategy_performance: Dict[str, List[float]] = {}
        self.feedback_logger = FeedbackLogger()
        self.performance_tracker = PerformanceTracker()

        logger.info("PracticeEngine 초기화 완료")

    def practice_strategy(
        self,
        strategy: Dict[str, Any],
        practice_type: PracticeType = PracticeType.REPETITION,
        iterations: int = 10,
        context: Optional[Dict[str, Any]] = None,
    ) -> PracticeResult:
        """
        전략을 연습합니다.

        Args:
            strategy: 연습할 전략
            practice_type: 연습 유형
            iterations: 반복 횟수
            context: 연습 컨텍스트

        Returns:
            PracticeResult: 연습 결과
        """
        session = PracticeSession(
            strategy_id=strategy.get("id", "unknown"),
            practice_type=practice_type,
            start_time=datetime.now(),
            end_time=None,
            iterations=iterations,
            success_count=0,
            failure_count=0,
            performance_metrics={},
            feedback_notes=[],
            confidence_change=0.0,
        )

        try:
            # 연습 실행
            modified_strategy = self._execute_practice(
                strategy, practice_type, iterations, context, session
            )

            # 성능 계산
            success_rate = session.success_count / iterations if iterations > 0 else 0
            avg_performance = (
                sum(session.performance_metrics.values())
                / len(session.performance_metrics)
                if session.performance_metrics
                else 0
            )

            # 개선 점수 계산
            improvement_score = self._calculate_improvement_score(session)
            session.improvement_score = improvement_score

            # 추천사항 생성
            recommendations = self._generate_recommendations(
                session, success_rate, avg_performance
            )

            session.end_time = datetime.now()
            self.practice_sessions.append(session)

            result = PracticeResult(
                session=session,
                strategy=strategy,
                modified_strategy=modified_strategy,
                success_rate=success_rate,
                average_performance=avg_performance,
                improvement_score=improvement_score,
                recommendations=recommendations,
            )

            # 피드백 로깅
            self.feedback_logger.log_practice_result(result)

            logger.info(
                f"전략 연습 완료: {practice_type.value}, 성공률: {success_rate:.2f}, 개선점수: {improvement_score:.2f}"
            )
            return result

        except Exception as e:
            logger.error(f"전략 연습 실패: {e}")
            session.end_time = datetime.now()
            session.feedback_notes.append(f"연습 실패: {str(e)}")
            self.practice_sessions.append(session)

            return PracticeResult(
                session=session,
                strategy=strategy,
                modified_strategy=strategy,
                success_rate=0.0,
                average_performance=0.0,
                improvement_score=0.0,
                recommendations=["연습 중 오류 발생"],
            )

    def _execute_practice(
        self,
        strategy: Dict[str, Any],
        practice_type: PracticeType,
        iterations: int,
        context: Optional[Dict[str, Any]],
        session: PracticeSession,
    ) -> Dict[str, Any]:
        """연습 실행"""
        modified_strategy = strategy.copy()

        for i in range(iterations):
            try:
                # 연습 유형에 따른 실행
                if practice_type == PracticeType.REPETITION:
                    result = self._execute_repetition(modified_strategy, i, context)
                elif practice_type == PracticeType.VARIATION:
                    result = self._execute_variation(modified_strategy, i, context)
                elif practice_type == PracticeType.PROGRESSIVE:
                    result = self._execute_progressive(modified_strategy, i, context)
                elif practice_type == PracticeType.ADAPTIVE:
                    result = self._execute_adaptive(modified_strategy, i, context)
                else:
                    result = self._execute_repetition(modified_strategy, i, context)

                # 결과 기록
                if result["success"]:
                    session.success_count += 1
                else:
                    session.failure_count += 1

                session.performance_metrics[f"iteration_{i}"] = result["performance"]
                session.feedback_notes.append(f"반복 {i+1}: {result['feedback']}")

                # 전략 수정
                if result.get("strategy_modifications"):
                    modified_strategy.update(result["strategy_modifications"])

            except Exception as e:
                session.failure_count += 1
                session.feedback_notes.append(f"반복 {i+1} 실패: {str(e)}")

        return modified_strategy

    def _execute_repetition(
        self,
        strategy: Dict[str, Any],
        iteration: int,
        context: Optional[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """단순 반복 실행"""
        # 실제 전략 실행 시뮬레이션
        performance = 0.7 + (iteration * 0.02)  # 점진적 개선
        success = performance > 0.6

        return {
            "success": success,
            "performance": performance,
            "feedback": f"반복 실행 {iteration + 1}회 완료",
            "strategy_modifications": {},
        }

    def _execute_variation(
        self,
        strategy: Dict[str, Any],
        iteration: int,
        context: Optional[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """변형 연습 실행"""
        # 파라미터 변형
        if "parameters" in strategy:
            for param, value in strategy["parameters"].items():
                if isinstance(value, (int, float)):
                    variation = value * 0.05 * (iteration + 1)
                    strategy["parameters"][param] = value + variation

        performance = 0.65 + (iteration * 0.03)
        success = performance > 0.6

        return {
            "success": success,
            "performance": performance,
            "feedback": f"변형 연습 {iteration + 1}회 완료",
            "strategy_modifications": strategy.get("parameters", {}),
        }

    def _execute_progressive(
        self,
        strategy: Dict[str, Any],
        iteration: int,
        context: Optional[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """점진적 난이도 증가"""
        difficulty_factor = 1.0 + (iteration * 0.1)
        performance = 0.8 / difficulty_factor
        success = performance > 0.5

        return {
            "success": success,
            "performance": performance,
            "feedback": f"점진적 난이도 {iteration + 1}회 완료 (난이도: {difficulty_factor:.1f})",
            "strategy_modifications": {},
        }

    def _execute_adaptive(
        self,
        strategy: Dict[str, Any],
        iteration: int,
        context: Optional[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """적응형 연습"""
        # 이전 성과에 따른 적응
        if iteration > 0 and hasattr(self, "_previous_performance"):
            if self._previous_performance > 0.8:
                # 성과가 좋으면 난이도 증가
                performance = 0.7 + (iteration * 0.05)
            else:
                # 성과가 나쁘면 난이도 감소
                performance = 0.6 + (iteration * 0.02)
        else:
            performance = 0.65

        self._previous_performance = performance
        success = performance > 0.6

        return {
            "success": success,
            "performance": performance,
            "feedback": f"적응형 연습 {iteration + 1}회 완료",
            "strategy_modifications": {},
        }

    def _calculate_improvement_score(self, session: PracticeSession) -> float:
        """개선 점수 계산"""
        if not session.performance_metrics:
            return 0.0

        performances = list(session.performance_metrics.values())
        if len(performances) < 2:
            return 0.0

        # 초기 성과와 최종 성과 비교
        initial_performance = performances[0]
        final_performance = performances[-1]

        improvement = (
            (final_performance - initial_performance) / initial_performance
            if initial_performance > 0
            else 0
        )
        return max(improvement, 0.0)

    def _generate_recommendations(
        self, session: PracticeSession, success_rate: float, avg_performance: float
    ) -> List[str]:
        """추천사항 생성"""
        recommendations = []

        if success_rate < 0.5:
            recommendations.append("성공률이 낮습니다. 더 많은 연습이 필요합니다.")

        if avg_performance < 0.6:
            recommendations.append("평균 성능이 낮습니다. 전략을 재검토하세요.")

        if session.improvement_score < 0.1:
            recommendations.append("개선이 미미합니다. 다른 연습 방법을 시도하세요.")

        if session.failure_count > session.success_count:
            recommendations.append("실패가 성공보다 많습니다. 기본기를 다지세요.")

        if not recommendations:
            recommendations.append("좋은 성과입니다! 다음 단계로 진행하세요.")

        return recommendations

    def get_practice_statistics(self) -> Dict[str, Any]:
        """연습 통계 반환"""
        total_sessions = len(self.practice_sessions)
        successful_sessions = len(
            [s for s in self.practice_sessions if s.success_count > s.failure_count]
        )

        type_counts = {}
        for session in self.practice_sessions:
            type_name = session.practice_type.value
            type_counts[type_name] = type_counts.get(type_name, 0) + 1

        avg_success_rate = (
            sum(
                s.success_count / s.iterations
                for s in self.practice_sessions
                if s.iterations > 0
            )
            / total_sessions
            if total_sessions > 0
            else 0
        )

        return {
            "total_sessions": total_sessions,
            "successful_sessions": successful_sessions,
            "success_rate": (
                successful_sessions / total_sessions if total_sessions > 0 else 0
            ),
            "type_distribution": type_counts,
            "average_success_rate": avg_success_rate,
            "total_iterations": sum(s.iterations for s in self.practice_sessions),
        }


class FeedbackLogger:
    """피드백 로거"""

    def __init__(self):
        self.feedback_history: List[Dict[str, Any]] = []

    def log_practice_result(self, result: PracticeResult):
        """연습 결과 로깅"""
        feedback_entry = {
            "timestamp": datetime.now(),
            "strategy_id": result.session.strategy_id,
            "practice_type": result.session.practice_type.value,
            "success_rate": result.success_rate,
            "average_performance": result.average_performance,
            "improvement_score": result.improvement_score,
            "recommendations": result.recommendations,
        }

        self.feedback_history.append(feedback_entry)
        logger.info(f"피드백 로깅 완료: {result.session.strategy_id}")


class PerformanceTracker:
    """성능 추적기"""

    def __init__(self):
        self.performance_history: Dict[str, List[float]] = {}

    def track_performance(self, strategy_id: str, performance: float):
        """성능 추적"""
        if strategy_id not in self.performance_history:
            self.performance_history[strategy_id] = []

        self.performance_history[strategy_id].append(performance)


# 싱글톤 인스턴스
_practice_engine = None


def get_practice_engine() -> PracticeEngine:
    """PracticeEngine 싱글톤 인스턴스 반환"""
    global _practice_engine
    if _practice_engine is None:
        _practice_engine = PracticeEngine()
    return _practice_engine
