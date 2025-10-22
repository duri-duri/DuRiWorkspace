#!/usr/bin/env python3
"""
DuRiCore Phase 5 Day 7 - 사용자 피드백 수집기
사용자 피드백 수집, 피드백 분석 및 처리, 개선 제안 생성
"""

import asyncio
import json
import logging
import math
import random
import statistics
import time
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple, Union

logger = logging.getLogger(__name__)


class FeedbackType(Enum):
    """피드백 타입 열거형"""

    PERFORMANCE = "performance"
    USABILITY = "usability"
    FUNCTIONALITY = "functionality"
    RELIABILITY = "reliability"
    SATISFACTION = "satisfaction"


class FeedbackPriority(Enum):
    """피드백 우선순위 열거형"""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class FeedbackStatus(Enum):
    """피드백 상태 열거형"""

    RECEIVED = "received"
    ANALYZING = "analyzing"
    PROCESSING = "processing"
    IMPLEMENTED = "implemented"
    REJECTED = "rejected"


@dataclass
class UserFeedback:
    """사용자 피드백"""

    feedback_id: str
    user_id: str
    feedback_type: FeedbackType
    priority: FeedbackPriority
    status: FeedbackStatus
    content: str
    rating: float
    timestamp: datetime
    metadata: Dict[str, Any]


@dataclass
class FeedbackAnalysis:
    """피드백 분석"""

    analysis_id: str
    feedback_id: str
    sentiment_score: float
    key_topics: List[str]
    improvement_areas: List[str]
    user_satisfaction: float
    created_at: datetime


@dataclass
class ImprovementSuggestion:
    """개선 제안"""

    suggestion_id: str
    feedback_analysis: FeedbackAnalysis
    suggestion_type: str
    priority: FeedbackPriority
    description: str
    expected_impact: float
    implementation_effort: float
    created_at: datetime


@dataclass
class FeedbackReport:
    """피드백 보고서"""

    report_id: str
    total_feedback: int
    average_satisfaction: float
    top_improvement_areas: List[str]
    implemented_suggestions: int
    recommendations: List[str]
    created_at: datetime


class UserFeedbackCollector:
    """사용자 피드백 수집기"""

    def __init__(self):
        self.feedback_database = {}
        self.feedback_analysis = {}
        self.improvement_suggestions = []

        # 피드백 설정
        self.min_feedback_length = 10
        self.max_feedback_length = 1000
        self.sentiment_threshold = 0.3

        # 피드백 가중치
        self.feedback_weights = {
            FeedbackType.PERFORMANCE: 0.3,
            FeedbackType.USABILITY: 0.25,
            FeedbackType.FUNCTIONALITY: 0.2,
            FeedbackType.RELIABILITY: 0.15,
            FeedbackType.SATISFACTION: 0.1,
        }

        # 우선순위 임계값
        self.priority_thresholds = {
            FeedbackPriority.LOW: 0.3,
            FeedbackPriority.MEDIUM: 0.6,
            FeedbackPriority.HIGH: 0.8,
            FeedbackPriority.CRITICAL: 1.0,
        }

        logger.info("사용자 피드백 수집기 초기화 완료")

    async def collect_user_feedback(self, feedback_data: Dict[str, Any]) -> UserFeedback:
        """사용자 피드백 수집"""
        try:
            logger.info("사용자 피드백 수집 시작")

            # 피드백 유효성 검증
            validation_result = await self._validate_feedback_data(feedback_data)
            if not validation_result["valid"]:
                raise ValueError(f"피드백 데이터 유효성 검증 실패: {validation_result['error']}")

            # 피드백 생성
            feedback = UserFeedback(
                feedback_id=f"feedback_{int(time.time())}_{random.randint(1000, 9999)}",
                user_id=feedback_data.get("user_id", "anonymous"),
                feedback_type=FeedbackType(feedback_data.get("feedback_type", "satisfaction")),
                priority=await self._determine_feedback_priority(feedback_data),
                status=FeedbackStatus.RECEIVED,
                content=feedback_data.get("content", ""),
                rating=feedback_data.get("rating", 0.0),
                timestamp=datetime.now(),
                metadata=feedback_data.get("metadata", {}),
            )

            # 피드백 저장
            self.feedback_database[feedback.feedback_id] = feedback

            logger.info(f"사용자 피드백 수집 완료: {feedback.feedback_id}")
            return feedback

        except Exception as e:
            logger.error(f"사용자 피드백 수집 실패: {e}")
            raise

    async def analyze_feedback_patterns(
        self, feedback_history: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """피드백 패턴 분석"""
        try:
            logger.info("피드백 패턴 분석 시작")

            analysis_result = {
                "overall_satisfaction": 0.0,
                "feedback_distribution": {},
                "trend_analysis": {},
                "common_issues": [],
                "improvement_opportunities": [],
            }

            if not feedback_history:
                return analysis_result

            # 전체 만족도 계산
            satisfaction_scores = [feedback.get("rating", 0.0) for feedback in feedback_history]
            analysis_result["overall_satisfaction"] = statistics.mean(satisfaction_scores)

            # 피드백 분포 분석
            feedback_distribution = await self._analyze_feedback_distribution(feedback_history)
            analysis_result["feedback_distribution"] = feedback_distribution

            # 트렌드 분석
            trend_analysis = await self._analyze_feedback_trends(feedback_history)
            analysis_result["trend_analysis"] = trend_analysis

            # 공통 이슈 식별
            common_issues = await self._identify_common_issues(feedback_history)
            analysis_result["common_issues"] = common_issues

            # 개선 기회 식별
            improvement_opportunities = await self._identify_improvement_opportunities(
                feedback_history
            )
            analysis_result["improvement_opportunities"] = improvement_opportunities

            logger.info("피드백 패턴 분석 완료")
            return analysis_result

        except Exception as e:
            logger.error(f"피드백 패턴 분석 실패: {e}")
            return {"error": str(e)}

    async def generate_improvement_suggestions(
        self, feedback_analysis: Dict[str, Any]
    ) -> List[ImprovementSuggestion]:
        """개선 제안 생성"""
        try:
            logger.info("개선 제안 생성 시작")

            suggestions = []

            # 만족도 기반 제안
            satisfaction_suggestions = await self._generate_satisfaction_based_suggestions(
                feedback_analysis
            )
            suggestions.extend(satisfaction_suggestions)

            # 이슈 기반 제안
            issue_suggestions = await self._generate_issue_based_suggestions(feedback_analysis)
            suggestions.extend(issue_suggestions)

            # 트렌드 기반 제안
            trend_suggestions = await self._generate_trend_based_suggestions(feedback_analysis)
            suggestions.extend(trend_suggestions)

            # 우선순위 정렬
            suggestions.sort(key=lambda x: self._calculate_suggestion_priority(x), reverse=True)

            self.improvement_suggestions.extend(suggestions)

            logger.info(f"개선 제안 생성 완료: {len(suggestions)}개")
            return suggestions

        except Exception as e:
            logger.error(f"개선 제안 생성 실패: {e}")
            return []

    async def validate_feedback_implementation(
        self, implementation_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """피드백 구현 검증"""
        try:
            logger.info("피드백 구현 검증 시작")

            validation_result = {
                "implementation_success": False,
                "user_satisfaction_change": 0.0,
                "implementation_metrics": {},
                "validation_confidence": 0.0,
            }

            # 구현 성공 여부 확인
            implementation_success = await self._check_implementation_success(implementation_data)
            validation_result["implementation_success"] = implementation_success

            # 사용자 만족도 변화 측정
            satisfaction_change = await self._measure_satisfaction_change(implementation_data)
            validation_result["user_satisfaction_change"] = satisfaction_change

            # 구현 지표 분석
            implementation_metrics = await self._analyze_implementation_metrics(implementation_data)
            validation_result["implementation_metrics"] = implementation_metrics

            # 검증 신뢰도 계산
            validation_confidence = await self._calculate_validation_confidence(implementation_data)
            validation_result["validation_confidence"] = validation_confidence

            logger.info(f"피드백 구현 검증 완료: {implementation_success}")
            return validation_result

        except Exception as e:
            logger.error(f"피드백 구현 검증 실패: {e}")
            return {"error": str(e)}

    async def _validate_feedback_data(self, feedback_data: Dict[str, Any]) -> Dict[str, Any]:
        """피드백 데이터 유효성 검증"""
        validation_result = {"valid": True, "error": ""}

        # 필수 필드 확인
        required_fields = ["content", "feedback_type"]
        for field in required_fields:
            if field not in feedback_data:
                validation_result["valid"] = False
                validation_result["error"] = f"필수 필드 누락: {field}"
                return validation_result

        # 내용 길이 확인
        content = feedback_data.get("content", "")
        if len(content) < self.min_feedback_length:
            validation_result["valid"] = False
            validation_result["error"] = (
                f"피드백 내용이 너무 짧습니다 (최소 {self.min_feedback_length}자)"
            )
            return validation_result

        if len(content) > self.max_feedback_length:
            validation_result["valid"] = False
            validation_result["error"] = (
                f"피드백 내용이 너무 깁니다 (최대 {self.max_feedback_length}자)"
            )
            return validation_result

        # 피드백 타입 확인
        feedback_type = feedback_data.get("feedback_type", "")
        if feedback_type not in [ft.value for ft in FeedbackType]:
            validation_result["valid"] = False
            validation_result["error"] = f"유효하지 않은 피드백 타입: {feedback_type}"
            return validation_result

        return validation_result

    async def _determine_feedback_priority(self, feedback_data: Dict[str, Any]) -> FeedbackPriority:
        """피드백 우선순위 결정"""
        # 기본 우선순위
        base_priority = FeedbackPriority.MEDIUM

        # 피드백 타입에 따른 우선순위 조정
        feedback_type = FeedbackType(feedback_data.get("feedback_type", "satisfaction"))
        if feedback_type == FeedbackType.RELIABILITY:
            base_priority = FeedbackPriority.HIGH
        elif feedback_type == FeedbackType.PERFORMANCE:
            base_priority = FeedbackPriority.HIGH
        elif feedback_type == FeedbackType.SATISFACTION:
            base_priority = FeedbackPriority.MEDIUM

        # 평점에 따른 우선순위 조정
        rating = feedback_data.get("rating", 0.0)
        if rating < 0.3:
            base_priority = FeedbackPriority.CRITICAL
        elif rating < 0.6:
            base_priority = FeedbackPriority.HIGH
        elif rating < 0.8:
            base_priority = FeedbackPriority.MEDIUM
        else:
            base_priority = FeedbackPriority.LOW

        return base_priority

    async def _analyze_feedback_distribution(
        self, feedback_history: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """피드백 분포 분석"""
        distribution = {
            "feedback_types": {},
            "priority_levels": {},
            "rating_distribution": {},
        }

        # 피드백 타입별 분포
        for feedback in feedback_history:
            feedback_type = feedback.get("feedback_type", "satisfaction")
            distribution["feedback_types"][feedback_type] = (
                distribution["feedback_types"].get(feedback_type, 0) + 1
            )

        # 우선순위별 분포
        for feedback in feedback_history:
            priority = feedback.get("priority", "medium")
            distribution["priority_levels"][priority] = (
                distribution["priority_levels"].get(priority, 0) + 1
            )

        # 평점 분포
        rating_ranges = {"low": 0, "medium": 0, "high": 0}
        for feedback in feedback_history:
            rating = feedback.get("rating", 0.0)
            if rating < 0.4:
                rating_ranges["low"] += 1
            elif rating < 0.7:
                rating_ranges["medium"] += 1
            else:
                rating_ranges["high"] += 1

        distribution["rating_distribution"] = rating_ranges

        return distribution

    async def _analyze_feedback_trends(
        self, feedback_history: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """피드백 트렌드 분석"""
        trends = {
            "satisfaction_trend": "stable",
            "feedback_volume_trend": "stable",
            "priority_trend": "stable",
        }

        if len(feedback_history) < 2:
            return trends

        # 만족도 트렌드
        ratings = [feedback.get("rating", 0.0) for feedback in feedback_history]
        if len(ratings) >= 2:
            recent_avg = statistics.mean(ratings[-5:]) if len(ratings) >= 5 else ratings[-1]
            previous_avg = statistics.mean(ratings[:-5]) if len(ratings) >= 10 else ratings[0]

            if recent_avg > previous_avg * 1.1:
                trends["satisfaction_trend"] = "improving"
            elif recent_avg < previous_avg * 0.9:
                trends["satisfaction_trend"] = "declining"

        # 피드백 볼륨 트렌드
        if len(feedback_history) >= 10:
            recent_volume = len(feedback_history[-5:])
            previous_volume = len(feedback_history[-10:-5])

            if recent_volume > previous_volume * 1.2:
                trends["feedback_volume_trend"] = "increasing"
            elif recent_volume < previous_volume * 0.8:
                trends["feedback_volume_trend"] = "decreasing"

        return trends

    async def _identify_common_issues(self, feedback_history: List[Dict[str, Any]]) -> List[str]:
        """공통 이슈 식별"""
        common_issues = []

        # 피드백 내용에서 키워드 추출 (시뮬레이션)
        issue_keywords = {
            "performance": ["slow", "lag", "delay", "performance"],
            "usability": ["difficult", "confusing", "hard to use", "usability"],
            "reliability": ["crash", "error", "bug", "unstable"],
            "functionality": ["missing", "need", "want", "feature"],
        }

        for feedback in feedback_history:
            content = feedback.get("content", "").lower()
            rating = feedback.get("rating", 0.0)

            # 낮은 평점의 피드백에서 이슈 식별
            if rating < 0.6:
                for issue_type, keywords in issue_keywords.items():
                    if any(keyword in content for keyword in keywords):
                        if issue_type not in common_issues:
                            common_issues.append(issue_type)

        return common_issues

    async def _identify_improvement_opportunities(
        self, feedback_history: List[Dict[str, Any]]
    ) -> List[str]:
        """개선 기회 식별"""
        opportunities = []

        # 피드백 분포 분석
        feedback_types = [
            feedback.get("feedback_type", "satisfaction") for feedback in feedback_history
        ]
        type_counts = {}
        for ft in feedback_types:
            type_counts[ft] = type_counts.get(ft, 0) + 1

        # 가장 많은 피드백이 있는 영역
        if type_counts:
            most_common_type = max(type_counts, key=type_counts.get)
            opportunities.append(f"increase_{most_common_type}_focus")

        # 평점이 낮은 영역
        low_rating_feedback = [f for f in feedback_history if f.get("rating", 0.0) < 0.5]
        if low_rating_feedback:
            low_rating_types = [f.get("feedback_type", "satisfaction") for f in low_rating_feedback]
            most_common_low = max(set(low_rating_types), key=low_rating_types.count)
            opportunities.append(f"improve_{most_common_low}_experience")

        return opportunities

    async def _generate_satisfaction_based_suggestions(
        self, feedback_analysis: Dict[str, Any]
    ) -> List[ImprovementSuggestion]:
        """만족도 기반 제안 생성"""
        suggestions = []

        overall_satisfaction = feedback_analysis.get("overall_satisfaction", 0.0)

        if overall_satisfaction < 0.6:
            suggestion = ImprovementSuggestion(
                suggestion_id=f"satisfaction_suggestion_{int(time.time())}",
                feedback_analysis=None,  # 실제로는 분석 결과를 연결
                suggestion_type="satisfaction_improvement",
                priority=FeedbackPriority.HIGH,
                description="전체 사용자 만족도가 낮습니다. 사용자 경험 개선이 필요합니다.",
                expected_impact=0.2,
                implementation_effort=0.7,
                created_at=datetime.now(),
            )
            suggestions.append(suggestion)

        return suggestions

    async def _generate_issue_based_suggestions(
        self, feedback_analysis: Dict[str, Any]
    ) -> List[ImprovementSuggestion]:
        """이슈 기반 제안 생성"""
        suggestions = []

        common_issues = feedback_analysis.get("common_issues", [])

        for issue in common_issues:
            suggestion = ImprovementSuggestion(
                suggestion_id=f"issue_suggestion_{issue}_{int(time.time())}",
                feedback_analysis=None,
                suggestion_type=f"{issue}_improvement",
                priority=(
                    FeedbackPriority.HIGH
                    if issue in ["reliability", "performance"]
                    else FeedbackPriority.MEDIUM
                ),
                description=f"{issue} 관련 이슈가 자주 보고되고 있습니다. 개선이 필요합니다.",
                expected_impact=0.15,
                implementation_effort=0.6,
                created_at=datetime.now(),
            )
            suggestions.append(suggestion)

        return suggestions

    async def _generate_trend_based_suggestions(
        self, feedback_analysis: Dict[str, Any]
    ) -> List[ImprovementSuggestion]:
        """트렌드 기반 제안 생성"""
        suggestions = []

        trend_analysis = feedback_analysis.get("trend_analysis", {})
        satisfaction_trend = trend_analysis.get("satisfaction_trend", "stable")

        if satisfaction_trend == "declining":
            suggestion = ImprovementSuggestion(
                suggestion_id=f"trend_suggestion_{int(time.time())}",
                feedback_analysis=None,
                suggestion_type="trend_reversal",
                priority=FeedbackPriority.CRITICAL,
                description="사용자 만족도가 하락하고 있습니다. 즉시 대응이 필요합니다.",
                expected_impact=0.25,
                implementation_effort=0.8,
                created_at=datetime.now(),
            )
            suggestions.append(suggestion)

        return suggestions

    async def _calculate_suggestion_priority(self, suggestion: ImprovementSuggestion) -> float:
        """제안 우선순위 계산"""
        priority_scores = {
            FeedbackPriority.LOW: 0.25,
            FeedbackPriority.MEDIUM: 0.5,
            FeedbackPriority.HIGH: 0.75,
            FeedbackPriority.CRITICAL: 1.0,
        }

        base_priority = priority_scores.get(suggestion.priority, 0.5)
        impact_multiplier = suggestion.expected_impact
        effort_divider = 1.0 + suggestion.implementation_effort

        return (base_priority * impact_multiplier) / effort_divider

    async def _check_implementation_success(self, implementation_data: Dict[str, Any]) -> bool:
        """구현 성공 여부 확인"""
        success_indicators = implementation_data.get("success_indicators", {})

        # 성공 지표 확인
        if "user_satisfaction_improvement" in success_indicators:
            improvement = success_indicators["user_satisfaction_improvement"]
            return improvement > 0.1  # 10% 이상 개선

        return True  # 기본적으로 성공으로 간주

    async def _measure_satisfaction_change(self, implementation_data: Dict[str, Any]) -> float:
        """만족도 변화 측정"""
        before_satisfaction = implementation_data.get("before_satisfaction", 0.0)
        after_satisfaction = implementation_data.get("after_satisfaction", 0.0)

        if before_satisfaction > 0:
            return (after_satisfaction - before_satisfaction) / before_satisfaction

        return 0.0

    async def _analyze_implementation_metrics(
        self, implementation_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """구현 지표 분석"""
        metrics = {
            "implementation_time": implementation_data.get("implementation_time", 0.0),
            "user_adoption_rate": implementation_data.get("user_adoption_rate", 0.0),
            "error_reduction": implementation_data.get("error_reduction", 0.0),
            "performance_improvement": implementation_data.get("performance_improvement", 0.0),
        }

        return metrics

    async def _calculate_validation_confidence(self, implementation_data: Dict[str, Any]) -> float:
        """검증 신뢰도 계산"""
        confidence_factors = []

        # 데이터 품질
        if "data_quality" in implementation_data:
            confidence_factors.append(implementation_data["data_quality"])

        # 샘플 크기
        if "sample_size" in implementation_data:
            sample_size = implementation_data["sample_size"]
            sample_confidence = min(sample_size / 100.0, 1.0)
            confidence_factors.append(sample_confidence)

        # 측정 기간
        if "measurement_duration" in implementation_data:
            duration = implementation_data["measurement_duration"]
            duration_confidence = min(duration / 86400.0, 1.0)  # 1일 이상이면 최대 신뢰도
            confidence_factors.append(duration_confidence)

        return statistics.mean(confidence_factors) if confidence_factors else 0.5


async def test_user_feedback_collector():
    """사용자 피드백 수집기 테스트"""
    print("=== 사용자 피드백 수집기 테스트 시작 ===")

    feedback_collector = UserFeedbackCollector()

    # 1. 사용자 피드백 수집 테스트
    print("1. 사용자 피드백 수집 테스트")
    feedback_data = {
        "user_id": "user_001",
        "feedback_type": "performance",
        "content": "시스템 응답 시간이 너무 느립니다. 개선이 필요합니다.",
        "rating": 0.4,
        "metadata": {"browser": "chrome", "os": "windows"},
    }

    feedback = await feedback_collector.collect_user_feedback(feedback_data)
    print(f"   - 피드백 ID: {feedback.feedback_id}")
    print(f"   - 우선순위: {feedback.priority}")
    print(f"   - 평점: {feedback.rating}")

    # 2. 피드백 패턴 분석 테스트
    print("2. 피드백 패턴 분석 테스트")
    feedback_history = [
        {
            "feedback_type": "performance",
            "rating": 0.6,
            "content": "성능이 개선되었습니다.",
        },
        {"feedback_type": "usability", "rating": 0.8, "content": "사용하기 편합니다."},
        {
            "feedback_type": "reliability",
            "rating": 0.3,
            "content": "오류가 자주 발생합니다.",
        },
        {
            "feedback_type": "satisfaction",
            "rating": 0.7,
            "content": "전반적으로 만족합니다.",
        },
    ]

    pattern_analysis = await feedback_collector.analyze_feedback_patterns(feedback_history)
    print(f"   - 전체 만족도: {pattern_analysis.get('overall_satisfaction', 0.0):.3f}")
    print(f"   - 공통 이슈: {len(pattern_analysis.get('common_issues', []))}개")
    print(f"   - 개선 기회: {len(pattern_analysis.get('improvement_opportunities', []))}개")

    # 3. 개선 제안 생성 테스트
    print("3. 개선 제안 생성 테스트")
    suggestions = await feedback_collector.generate_improvement_suggestions(pattern_analysis)
    print(f"   - 생성된 제안: {len(suggestions)}개")

    for suggestion in suggestions[:3]:  # 상위 3개만 출력
        print(f"     - {suggestion.description}")
        print(
            f"       우선순위: {suggestion.priority}, 예상 영향: {suggestion.expected_impact:.3f}"
        )

    # 4. 피드백 구현 검증 테스트
    print("4. 피드백 구현 검증 테스트")
    implementation_data = {
        "before_satisfaction": 0.6,
        "after_satisfaction": 0.8,
        "implementation_time": 3600.0,  # 1시간
        "user_adoption_rate": 0.85,
        "error_reduction": 0.3,
        "performance_improvement": 0.25,
        "data_quality": 0.9,
        "sample_size": 150,
        "measurement_duration": 172800,  # 2일
    }

    validation_result = await feedback_collector.validate_feedback_implementation(
        implementation_data
    )
    print(f"   - 구현 성공: {validation_result.get('implementation_success', False)}")
    print(f"   - 만족도 변화: {validation_result.get('user_satisfaction_change', 0.0):.3f}")
    print(f"   - 검증 신뢰도: {validation_result.get('validation_confidence', 0.0):.3f}")

    print("=== 사용자 피드백 수집기 테스트 완료 ===")


if __name__ == "__main__":
    asyncio.run(test_user_feedback_collector())
