#!/usr/bin/env python3
"""
DuRiCore Phase 5 Day 5 - 학습 패턴 분석 시스템
성공/실패 패턴 식별, 행동-성과 상관관계 분석, 학습 효과성 평가
"""

import asyncio
import logging
import statistics
import time
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


class PatternType(Enum):
    """패턴 타입 열거형"""

    SUCCESS = "success"
    FAILURE = "failure"
    IMPROVEMENT = "improvement"
    DECLINE = "decline"
    STABLE = "stable"


class LearningEffectiveness(Enum):
    """학습 효과성 열거형"""

    HIGH = "high"  # 높음 (0.8-1.0)
    MEDIUM = "medium"  # 중간 (0.5-0.8)
    LOW = "low"  # 낮음 (0.0-0.5)


@dataclass
class LearningPattern:
    """학습 패턴"""

    pattern_id: str
    pattern_type: PatternType
    frequency: float
    success_rate: float
    average_performance: float
    key_factors: List[str]
    confidence: float
    created_at: datetime


@dataclass
class PerformanceCorrelation:
    """성과 상관관계"""

    correlation_id: str
    factor_a: str
    factor_b: str
    correlation_coefficient: float
    significance: float
    sample_size: int
    confidence_interval: Tuple[float, float]
    created_at: datetime


@dataclass
class LearningEffectivenessReport:
    """학습 효과성 보고서"""

    report_id: str
    overall_effectiveness: LearningEffectiveness
    effectiveness_score: float
    improvement_rate: float
    stability_score: float
    key_insights: List[str]
    recommendations: List[str]
    created_at: datetime


class LearningPatternAnalyzer:
    """학습 패턴 분석 시스템"""

    def __init__(self):
        self.pattern_database = {}
        self.correlation_cache = {}
        self.effectiveness_history = []

        # 분석 설정
        self.min_pattern_frequency = 0.1
        self.min_confidence_threshold = 0.7
        self.correlation_threshold = 0.3

        # 패턴 식별 가중치
        self.pattern_weights = {
            "success_rate": 0.4,
            "frequency": 0.3,
            "performance": 0.2,
            "consistency": 0.1,
        }

        logger.info("학습 패턴 분석 시스템 초기화 완료")

    async def analyze_success_patterns(self, behavior_traces: List[Dict[str, Any]]) -> List[LearningPattern]:
        """성공 패턴 분석"""
        try:
            success_patterns = []

            # 성공한 행동 추출
            successful_behaviors = [
                trace
                for trace in behavior_traces
                if trace.get("success", False) and trace.get("effectiveness_score", 0.0) > 0.7
            ]

            if not successful_behaviors:
                logger.warning("분석할 성공 패턴이 없습니다.")
                return success_patterns

            # 패턴 그룹화
            pattern_groups = await self._group_similar_behaviors(successful_behaviors)

            # 각 그룹에서 패턴 추출
            for group_id, behaviors in pattern_groups.items():
                pattern = await self._extract_pattern_from_group(group_id, behaviors, PatternType.SUCCESS)
                if pattern and pattern.confidence >= self.min_confidence_threshold:
                    success_patterns.append(pattern)
                    self.pattern_database[pattern.pattern_id] = pattern

            logger.info(f"성공 패턴 {len(success_patterns)}개 식별 완료")
            return success_patterns

        except Exception as e:
            logger.error(f"성공 패턴 분석 실패: {e}")
            raise

    async def analyze_failure_patterns(self, behavior_traces: List[Dict[str, Any]]) -> List[LearningPattern]:
        """실패 패턴 분석"""
        try:
            failure_patterns = []

            # 실패한 행동 추출
            failed_behaviors = [
                trace
                for trace in behavior_traces
                if not trace.get("success", True) or trace.get("effectiveness_score", 0.0) < 0.5
            ]

            if not failed_behaviors:
                logger.warning("분석할 실패 패턴이 없습니다.")
                return failure_patterns

            # 패턴 그룹화
            pattern_groups = await self._group_similar_behaviors(failed_behaviors)

            # 각 그룹에서 패턴 추출
            for group_id, behaviors in pattern_groups.items():
                pattern = await self._extract_pattern_from_group(group_id, behaviors, PatternType.FAILURE)
                if pattern and pattern.confidence >= self.min_confidence_threshold:
                    failure_patterns.append(pattern)
                    self.pattern_database[pattern.pattern_id] = pattern

            logger.info(f"실패 패턴 {len(failure_patterns)}개 식별 완료")
            return failure_patterns

        except Exception as e:
            logger.error(f"실패 패턴 분석 실패: {e}")
            raise

    async def identify_learning_effectiveness(
        self, performance_history: List[Dict[str, Any]]
    ) -> LearningEffectivenessReport:
        """학습 효과성 식별"""
        try:
            if not performance_history:
                return await self._create_empty_effectiveness_report()

            # 성능 트렌드 분석
            effectiveness_score = await self._calculate_effectiveness_score(performance_history)
            improvement_rate = await self._calculate_improvement_rate(performance_history)
            stability_score = await self._calculate_stability_score(performance_history)

            # 학습 효과성 등급 결정
            overall_effectiveness = await self._determine_effectiveness_level(effectiveness_score)

            # 주요 인사이트 추출
            key_insights = await self._extract_key_insights(performance_history)

            # 권장사항 생성
            recommendations = await self._generate_recommendations(
                effectiveness_score, improvement_rate, stability_score
            )

            # 보고서 생성
            report = LearningEffectivenessReport(
                report_id=f"effectiveness_report_{int(time.time())}",
                overall_effectiveness=overall_effectiveness,
                effectiveness_score=effectiveness_score,
                improvement_rate=improvement_rate,
                stability_score=stability_score,
                key_insights=key_insights,
                recommendations=recommendations,
                created_at=datetime.now(),
            )

            # 히스토리에 추가
            self.effectiveness_history.append(report)

            logger.info(f"학습 효과성 분석 완료: {overall_effectiveness.value}")
            return report

        except Exception as e:
            logger.error(f"학습 효과성 식별 실패: {e}")
            raise

    async def generate_pattern_recommendations(self, patterns: List[LearningPattern]) -> List[Dict[str, Any]]:
        """패턴 기반 권장사항 생성"""
        try:
            recommendations = []

            # 성공 패턴 기반 권장사항
            success_patterns = [p for p in patterns if p.pattern_type == PatternType.SUCCESS]
            for pattern in success_patterns:
                if pattern.success_rate > 0.8 and pattern.frequency > self.min_pattern_frequency:
                    recommendations.append(
                        {
                            "type": "success_pattern_replication",
                            "priority": "high",
                            "description": f"성공 패턴 '{pattern.pattern_id}' 확장 및 적용",
                            "pattern_id": pattern.pattern_id,
                            "expected_benefit": pattern.average_performance,
                            "confidence": pattern.confidence,
                        }
                    )

            # 실패 패턴 기반 권장사항
            failure_patterns = [p for p in patterns if p.pattern_type == PatternType.FAILURE]
            for pattern in failure_patterns:
                if pattern.frequency > self.min_pattern_frequency:
                    recommendations.append(
                        {
                            "type": "failure_pattern_avoidance",
                            "priority": "medium",
                            "description": f"실패 패턴 '{pattern.pattern_id}' 회피 및 개선",
                            "pattern_id": pattern.pattern_id,
                            "risk_level": 1.0 - pattern.success_rate,
                            "improvement_potential": 0.5,
                        }
                    )

            # 개선 패턴 기반 권장사항
            improvement_patterns = [p for p in patterns if p.pattern_type == PatternType.IMPROVEMENT]
            for pattern in improvement_patterns:
                recommendations.append(
                    {
                        "type": "improvement_pattern_acceleration",
                        "priority": "high",
                        "description": f"개선 패턴 '{pattern.pattern_id}' 가속화",
                        "pattern_id": pattern.pattern_id,
                        "improvement_rate": pattern.average_performance,
                        "sustainability": pattern.confidence,
                    }
                )

            return recommendations

        except Exception as e:
            logger.error(f"패턴 권장사항 생성 실패: {e}")
            raise

    async def _group_similar_behaviors(self, behaviors: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """유사한 행동 그룹화"""
        try:
            groups = {}

            for behavior in behaviors:
                # 행동 타입과 전략을 기준으로 그룹화
                behavior_type = behavior.get("behavior_type", "unknown")
                strategy = behavior.get("strategy", "unknown")
                group_key = f"{behavior_type}_{strategy}"

                if group_key not in groups:
                    groups[group_key] = []

                groups[group_key].append(behavior)

            return groups

        except Exception as e:
            logger.error(f"행동 그룹화 실패: {e}")
            raise

    async def _extract_pattern_from_group(
        self, group_id: str, behaviors: List[Dict[str, Any]], pattern_type: PatternType
    ) -> Optional[LearningPattern]:
        """그룹에서 패턴 추출"""
        try:
            if len(behaviors) < 2:
                return None

            # 기본 통계 계산
            success_rates = [b.get("success", False) for b in behaviors]
            effectiveness_scores = [b.get("effectiveness_score", 0.0) for b in behaviors]
            efficiency_scores = [b.get("efficiency_score", 0.0) for b in behaviors]  # noqa: F841

            # 패턴 특성 계산
            frequency = len(behaviors) / len(self.pattern_database) if self.pattern_database else 1.0
            success_rate = sum(success_rates) / len(success_rates)
            average_performance = statistics.mean(effectiveness_scores)

            # 주요 요소 식별
            key_factors = await self._identify_key_factors(behaviors)

            # 신뢰도 계산
            confidence = await self._calculate_pattern_confidence(
                frequency, success_rate, average_performance, len(behaviors)
            )

            pattern = LearningPattern(
                pattern_id=f"pattern_{group_id}_{pattern_type.value}",
                pattern_type=pattern_type,
                frequency=frequency,
                success_rate=success_rate,
                average_performance=average_performance,
                key_factors=key_factors,
                confidence=confidence,
                created_at=datetime.now(),
            )

            return pattern

        except Exception as e:
            logger.error(f"패턴 추출 실패: {e}")
            return None

    async def _identify_key_factors(self, behaviors: List[Dict[str, Any]]) -> List[str]:
        """주요 요소 식별"""
        try:
            factors = []

            # 공통 특성 분석
            common_characteristics = {}

            for behavior in behaviors:
                # 행동 타입
                behavior_type = behavior.get("behavior_type", "")
                if behavior_type:
                    common_characteristics["behavior_type"] = common_characteristics.get("behavior_type", 0) + 1

                # 전략
                strategy = behavior.get("strategy", "")
                if strategy:
                    common_characteristics["strategy"] = common_characteristics.get("strategy", 0) + 1

                # 우선순위
                priority = behavior.get("priority", 0.0)
                if priority > 0.7:
                    common_characteristics["high_priority"] = common_characteristics.get("high_priority", 0) + 1

            # 주요 요소 선별
            for factor, count in common_characteristics.items():
                if count >= len(behaviors) * 0.7:  # 70% 이상에서 공통
                    factors.append(factor)

            return factors

        except Exception as e:
            logger.error(f"주요 요소 식별 실패: {e}")
            return []

    async def _calculate_pattern_confidence(
        self,
        frequency: float,
        success_rate: float,
        average_performance: float,
        sample_size: int,
    ) -> float:
        """패턴 신뢰도 계산"""
        try:
            # 샘플 크기 기반 신뢰도
            size_confidence = min(sample_size / 10.0, 1.0)

            # 성공률 기반 신뢰도
            success_confidence = success_rate if success_rate > 0.5 else 1.0 - success_rate

            # 성능 기반 신뢰도
            performance_confidence = average_performance

            # 빈도 기반 신뢰도
            frequency_confidence = min(frequency * 10, 1.0)

            # 가중 평균
            confidence = (
                size_confidence * 0.3
                + success_confidence * 0.3
                + performance_confidence * 0.2
                + frequency_confidence * 0.2
            )

            return min(confidence, 1.0)

        except Exception as e:
            logger.error(f"패턴 신뢰도 계산 실패: {e}")
            return 0.0

    async def _calculate_effectiveness_score(self, performance_history: List[Dict[str, Any]]) -> float:
        """효과성 점수 계산"""
        try:
            if not performance_history:
                return 0.0

            # 최근 성능 데이터 추출
            recent_performance = performance_history[-10:] if len(performance_history) >= 10 else performance_history

            # 성공률과 효과성 점수 평균
            success_rates = [p.get("success", False) for p in recent_performance]
            effectiveness_scores = [p.get("metrics", {}).get("action_effectiveness", 0.0) for p in recent_performance]

            avg_success_rate = sum(success_rates) / len(success_rates) if success_rates else 0.0
            avg_effectiveness = statistics.mean(effectiveness_scores) if effectiveness_scores else 0.0

            # 가중 평균
            effectiveness_score = avg_success_rate * 0.6 + avg_effectiveness * 0.4

            return min(effectiveness_score, 1.0)

        except Exception as e:
            logger.error(f"효과성 점수 계산 실패: {e}")
            return 0.0

    async def _calculate_improvement_rate(self, performance_history: List[Dict[str, Any]]) -> float:
        """개선률 계산"""
        try:
            if len(performance_history) < 2:
                return 0.0

            # 최근 10개와 이전 10개 비교
            recent = performance_history[-10:] if len(performance_history) >= 10 else performance_history
            previous = (
                performance_history[-20:-10] if len(performance_history) >= 20 else performance_history[: -len(recent)]
            )

            if not previous:
                return 0.0

            # 평균 성능 비교
            recent_avg = statistics.mean([p.get("metrics", {}).get("action_effectiveness", 0.0) for p in recent])
            previous_avg = statistics.mean([p.get("metrics", {}).get("action_effectiveness", 0.0) for p in previous])

            if previous_avg == 0:
                return 0.0

            improvement_rate = (recent_avg - previous_avg) / previous_avg

            return max(improvement_rate, -1.0)  # 최대 -100% 하락

        except Exception as e:
            logger.error(f"개선률 계산 실패: {e}")
            return 0.0

    async def _calculate_stability_score(self, performance_history: List[Dict[str, Any]]) -> float:
        """안정성 점수 계산"""
        try:
            if len(performance_history) < 3:
                return 1.0

            # 최근 성능 데이터의 표준편차 계산
            recent_performance = performance_history[-10:] if len(performance_history) >= 10 else performance_history
            effectiveness_scores = [p.get("metrics", {}).get("action_effectiveness", 0.0) for p in recent_performance]

            if not effectiveness_scores:
                return 1.0

            # 변동계수 계산 (표준편차 / 평균)
            mean_score = statistics.mean(effectiveness_scores)
            if mean_score == 0:
                return 1.0

            std_score = statistics.stdev(effectiveness_scores) if len(effectiveness_scores) > 1 else 0.0
            coefficient_of_variation = std_score / mean_score

            # 안정성 점수 (변동계수가 낮을수록 안정적)
            stability_score = max(0.0, 1.0 - coefficient_of_variation)

            return stability_score

        except Exception as e:
            logger.error(f"안정성 점수 계산 실패: {e}")
            return 1.0

    async def _determine_effectiveness_level(self, effectiveness_score: float) -> LearningEffectiveness:
        """학습 효과성 등급 결정"""
        if effectiveness_score >= 0.8:
            return LearningEffectiveness.HIGH
        elif effectiveness_score >= 0.5:
            return LearningEffectiveness.MEDIUM
        else:
            return LearningEffectiveness.LOW

    async def _extract_key_insights(self, performance_history: List[Dict[str, Any]]) -> List[str]:
        """주요 인사이트 추출"""
        try:
            insights = []

            if not performance_history:
                return insights

            # 성능 트렌드 분석
            recent_performance = performance_history[-5:] if len(performance_history) >= 5 else performance_history
            effectiveness_trend = [p.get("metrics", {}).get("action_effectiveness", 0.0) for p in recent_performance]

            if len(effectiveness_trend) >= 2:
                if effectiveness_trend[-1] > effectiveness_trend[0]:
                    insights.append("행동 효과성이 지속적으로 향상되고 있습니다.")
                elif effectiveness_trend[-1] < effectiveness_trend[0]:
                    insights.append("행동 효과성이 감소 추세를 보이고 있습니다.")
                else:
                    insights.append("행동 효과성이 안정적으로 유지되고 있습니다.")

            # 성공률 분석
            success_count = sum(1 for p in recent_performance if p.get("success", False))
            success_rate = success_count / len(recent_performance)

            if success_rate > 0.8:
                insights.append("전체적인 성공률이 높은 수준을 유지하고 있습니다.")
            elif success_rate < 0.5:
                insights.append("성공률 개선이 필요한 상황입니다.")

            return insights

        except Exception as e:
            logger.error(f"주요 인사이트 추출 실패: {e}")
            return []

    async def _generate_recommendations(
        self,
        effectiveness_score: float,
        improvement_rate: float,
        stability_score: float,
    ) -> List[str]:
        """권장사항 생성"""
        try:
            recommendations = []

            # 효과성 기반 권장사항
            if effectiveness_score < 0.7:
                recommendations.append("전반적인 학습 효과성 향상을 위한 시스템 개선이 필요합니다.")

            # 개선률 기반 권장사항
            if improvement_rate < 0.05:
                recommendations.append("성능 개선을 위한 새로운 학습 전략 도입을 고려해보세요.")
            elif improvement_rate > 0.2:
                recommendations.append("현재의 긍정적인 개선 추세를 유지하기 위한 안정화가 필요합니다.")

            # 안정성 기반 권장사항
            if stability_score < 0.8:
                recommendations.append("성능 안정성 향상을 위한 일관성 있는 학습 패턴 확립이 필요합니다.")

            return recommendations

        except Exception as e:
            logger.error(f"권장사항 생성 실패: {e}")
            return []

    async def _create_empty_effectiveness_report(self) -> LearningEffectivenessReport:
        """빈 효과성 보고서 생성"""
        return LearningEffectivenessReport(
            report_id=f"empty_report_{int(time.time())}",
            overall_effectiveness=LearningEffectiveness.LOW,
            effectiveness_score=0.0,
            improvement_rate=0.0,
            stability_score=1.0,
            key_insights=["분석할 성능 데이터가 없습니다."],
            recommendations=["더 많은 학습 데이터를 수집해주세요."],
            created_at=datetime.now(),
        )


async def test_learning_pattern_analyzer():
    """학습 패턴 분석 시스템 테스트"""
    print("=== DuRiCore Phase 5 Day 5 - 학습 패턴 분석 시스템 테스트 ===")

    # 학습 패턴 분석 시스템 초기화
    analyzer = LearningPatternAnalyzer()

    # 테스트용 행동 추적 데이터
    test_behavior_traces = [
        {
            "action_id": "act_001",
            "behavior_type": "response",
            "strategy": "immediate",
            "success": True,
            "effectiveness_score": 0.9,
            "efficiency_score": 0.8,
            "priority": 0.9,
        },
        {
            "action_id": "act_002",
            "behavior_type": "response",
            "strategy": "immediate",
            "success": True,
            "effectiveness_score": 0.85,
            "efficiency_score": 0.75,
            "priority": 0.8,
        },
        {
            "action_id": "act_003",
            "behavior_type": "analysis",
            "strategy": "sequential",
            "success": False,
            "effectiveness_score": 0.4,
            "efficiency_score": 0.3,
            "priority": 0.6,
        },
        {
            "action_id": "act_004",
            "behavior_type": "learning",
            "strategy": "adaptive",
            "success": True,
            "effectiveness_score": 0.8,
            "efficiency_score": 0.7,
            "priority": 0.7,
        },
        {
            "action_id": "act_005",
            "behavior_type": "learning",
            "strategy": "adaptive",
            "success": True,
            "effectiveness_score": 0.85,
            "efficiency_score": 0.8,
            "priority": 0.8,
        },
    ]

    # 테스트용 성능 히스토리
    test_performance_history = [
        {
            "cycle_id": "cycle_001",
            "timestamp": datetime.now(),
            "success": True,
            "metrics": {"action_effectiveness": 0.8, "action_efficiency": 0.7},
        },
        {
            "cycle_id": "cycle_002",
            "timestamp": datetime.now(),
            "success": True,
            "metrics": {"action_effectiveness": 0.85, "action_efficiency": 0.75},
        },
        {
            "cycle_id": "cycle_003",
            "timestamp": datetime.now(),
            "success": False,
            "metrics": {"action_effectiveness": 0.4, "action_efficiency": 0.3},
        },
        {
            "cycle_id": "cycle_004",
            "timestamp": datetime.now(),
            "success": True,
            "metrics": {"action_effectiveness": 0.9, "action_efficiency": 0.8},
        },
        {
            "cycle_id": "cycle_005",
            "timestamp": datetime.now(),
            "success": True,
            "metrics": {"action_effectiveness": 0.95, "action_efficiency": 0.85},
        },
    ]

    # 1. 성공 패턴 분석 테스트
    print("\n1. 성공 패턴 분석 테스트")
    success_patterns = await analyzer.analyze_success_patterns(test_behavior_traces)

    print(f"성공 패턴 {len(success_patterns)}개 발견:")
    for pattern in success_patterns:
        print(f"- 패턴 ID: {pattern.pattern_id}")
        print(f"  타입: {pattern.pattern_type.value}")
        print(f"  빈도: {pattern.frequency:.3f}")
        print(f"  성공률: {pattern.success_rate:.3f}")
        print(f"  평균 성능: {pattern.average_performance:.3f}")
        print(f"  주요 요소: {pattern.key_factors}")
        print(f"  신뢰도: {pattern.confidence:.3f}")

    # 2. 실패 패턴 분석 테스트
    print("\n2. 실패 패턴 분석 테스트")
    failure_patterns = await analyzer.analyze_failure_patterns(test_behavior_traces)

    print(f"실패 패턴 {len(failure_patterns)}개 발견:")
    for pattern in failure_patterns:
        print(f"- 패턴 ID: {pattern.pattern_id}")
        print(f"  타입: {pattern.pattern_type.value}")
        print(f"  빈도: {pattern.frequency:.3f}")
        print(f"  성공률: {pattern.success_rate:.3f}")
        print(f"  평균 성능: {pattern.average_performance:.3f}")
        print(f"  주요 요소: {pattern.key_factors}")
        print(f"  신뢰도: {pattern.confidence:.3f}")

    # 3. 학습 효과성 분석 테스트
    print("\n3. 학습 효과성 분석 테스트")
    effectiveness_report = await analyzer.identify_learning_effectiveness(test_performance_history)

    print("학습 효과성 분석 결과:")
    print(f"- 전체 효과성: {effectiveness_report.overall_effectiveness.value}")
    print(f"- 효과성 점수: {effectiveness_report.effectiveness_score:.3f}")
    print(f"- 개선률: {effectiveness_report.improvement_rate:.3f}")
    print(f"- 안정성 점수: {effectiveness_report.stability_score:.3f}")
    print(f"- 주요 인사이트: {effectiveness_report.key_insights}")
    print(f"- 권장사항: {effectiveness_report.recommendations}")

    # 4. 패턴 권장사항 생성 테스트
    print("\n4. 패턴 권장사항 생성 테스트")
    all_patterns = success_patterns + failure_patterns
    recommendations = await analyzer.generate_pattern_recommendations(all_patterns)

    print(f"패턴 기반 권장사항 {len(recommendations)}개 생성:")
    for rec in recommendations:
        print(f"- 타입: {rec['type']}")
        print(f"  우선순위: {rec['priority']}")
        print(f"  설명: {rec['description']}")

    print("\n=== 테스트 완료 ===")


if __name__ == "__main__":
    asyncio.run(test_learning_pattern_analyzer())
