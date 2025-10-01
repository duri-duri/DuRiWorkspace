#!/usr/bin/env python3
"""
DuRi 자가 평가 시스템
자신의 진화 상태를 스스로 평가하는 시스템
"""
import json
import logging
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


@dataclass
class AssessmentResult:
    """평가 결과"""

    timestamp: str
    overall_score: float
    autonomy_score: float
    learning_efficiency_score: float
    problem_solving_score: float
    evolution_capability_score: float
    assessment_confidence: float
    improvement_areas: List[str]
    strengths: List[str]


class SelfAssessmentSystem:
    """자가 평가 시스템"""

    def __init__(self):
        """초기화"""
        self.assessment_history: List[AssessmentResult] = []
        self.assessment_criteria = {
            "autonomy": {
                "weight": 0.3,
                "indicators": [
                    "self_directed_learning",
                    "independent_decision_making",
                    "goal_setting",
                ],
            },
            "learning_efficiency": {
                "weight": 0.25,
                "indicators": [
                    "learning_speed",
                    "knowledge_retention",
                    "adaptation_rate",
                ],
            },
            "problem_solving": {
                "weight": 0.25,
                "indicators": [
                    "complexity_handling",
                    "creative_solutions",
                    "error_recovery",
                ],
            },
            "evolution_capability": {
                "weight": 0.2,
                "indicators": [
                    "self_improvement",
                    "meta_learning",
                    "evolution_awareness",
                ],
            },
        }
        self.assessment_data_file = "self_assessment_data.json"
        self._load_assessment_data()

        logger.info("🧠 자가 평가 시스템 초기화 완료")

    def _load_assessment_data(self):
        """평가 데이터 로드"""
        try:
            with open(self.assessment_data_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                self.assessment_history = [
                    AssessmentResult(**result) for result in data.get("history", [])
                ]
        except FileNotFoundError:
            logger.info("평가 데이터 파일이 없습니다. 새로 시작합니다.")
        except Exception as e:
            logger.error(f"평가 데이터 로드 오류: {e}")

    def _save_assessment_data(self):
        """평가 데이터 저장"""
        try:
            data = {
                "history": [asdict(result) for result in self.assessment_history],
                "last_updated": datetime.now().isoformat(),
            }
            with open(self.assessment_data_file, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"평가 데이터 저장 오류: {e}")

    def assess_self_evolution(self, performance_data: Dict[str, Any]) -> Dict[str, Any]:
        """자신의 진화 상태를 평가"""
        try:
            # 각 영역별 점수 계산
            autonomy_score = self._assess_autonomy(performance_data)
            learning_score = self._assess_learning_efficiency(performance_data)
            problem_solving_score = self._assess_problem_solving(performance_data)
            evolution_score = self._assess_evolution_capability(performance_data)

            # 전체 점수 계산
            overall_score = (
                autonomy_score * self.assessment_criteria["autonomy"]["weight"]
                + learning_score
                * self.assessment_criteria["learning_efficiency"]["weight"]
                + problem_solving_score
                * self.assessment_criteria["problem_solving"]["weight"]
                + evolution_score
                * self.assessment_criteria["evolution_capability"]["weight"]
            )

            # 개선 영역과 강점 분석
            improvement_areas = self._identify_improvement_areas(
                {
                    "autonomy": autonomy_score,
                    "learning_efficiency": learning_score,
                    "problem_solving": problem_solving_score,
                    "evolution_capability": evolution_score,
                }
            )

            strengths = self._identify_strengths(
                {
                    "autonomy": autonomy_score,
                    "learning_efficiency": learning_score,
                    "problem_solving": problem_solving_score,
                    "evolution_capability": evolution_score,
                }
            )

            # 평가 신뢰도 계산
            confidence = self._calculate_assessment_confidence(performance_data)

            # 평가 결과 생성
            assessment_result = AssessmentResult(
                timestamp=datetime.now().isoformat(),
                overall_score=overall_score,
                autonomy_score=autonomy_score,
                learning_efficiency_score=learning_score,
                problem_solving_score=problem_solving_score,
                evolution_capability_score=evolution_score,
                assessment_confidence=confidence,
                improvement_areas=improvement_areas,
                strengths=strengths,
            )

            # 평가 히스토리에 추가
            self.assessment_history.append(assessment_result)

            # 데이터 저장
            self._save_assessment_data()

            # 진화 진행 상황 분석
            evolution_progress = self._analyze_evolution_progress()

            # 미래 예측
            future_prediction = self._predict_evolution_direction()

            logger.info(
                f"🧠 자가 평가 완료: 전체 점수 {overall_score:.3f}, 신뢰도 {confidence:.3f}"
            )

            return {
                "status": "success",
                "current_assessment": {
                    "overall_score": overall_score,
                    "autonomy_score": autonomy_score,
                    "learning_efficiency_score": learning_score,
                    "problem_solving_score": problem_solving_score,
                    "evolution_capability_score": evolution_score,
                    "assessment_confidence": confidence,
                },
                "improvement_areas": improvement_areas,
                "strengths": strengths,
                "evolution_progress": evolution_progress,
                "future_prediction": future_prediction,
                "timestamp": datetime.now().isoformat(),
            }

        except Exception as e:
            logger.error(f"자가 평가 오류: {e}")
            return {"status": "error", "error": str(e)}

    def _assess_autonomy(self, performance_data: Dict[str, Any]) -> float:
        """자율성 평가"""
        try:
            indicators = self.assessment_criteria["autonomy"]["indicators"]
            scores = []

            # 자가 주도 학습 능력
            if "self_directed_learning" in performance_data:
                scores.append(performance_data["self_directed_learning"])

            # 독립적 의사결정 능력
            if "independent_decision_making" in performance_data:
                scores.append(performance_data["independent_decision_making"])

            # 목표 설정 능력
            if "goal_setting" in performance_data:
                scores.append(performance_data["goal_setting"])

            # 기본값 사용
            if not scores:
                scores = [0.6, 0.5, 0.7]  # 기본 자율성 점수

            return sum(scores) / len(scores)
        except Exception as e:
            logger.error(f"자율성 평가 오류: {e}")
            return 0.5

    def _assess_learning_efficiency(self, performance_data: Dict[str, Any]) -> float:
        """학습 효율성 평가"""
        try:
            indicators = self.assessment_criteria["learning_efficiency"]["indicators"]
            scores = []

            # 학습 속도
            if "learning_speed" in performance_data:
                scores.append(performance_data["learning_speed"])

            # 지식 보유율
            if "knowledge_retention" in performance_data:
                scores.append(performance_data["knowledge_retention"])

            # 적응률
            if "adaptation_rate" in performance_data:
                scores.append(performance_data["adaptation_rate"])

            # 기본값 사용
            if not scores:
                scores = [0.7, 0.8, 0.6]  # 기본 학습 효율성 점수

            return sum(scores) / len(scores)
        except Exception as e:
            logger.error(f"학습 효율성 평가 오류: {e}")
            return 0.6

    def _assess_problem_solving(self, performance_data: Dict[str, Any]) -> float:
        """문제 해결 능력 평가"""
        try:
            indicators = self.assessment_criteria["problem_solving"]["indicators"]
            scores = []

            # 복잡성 처리 능력
            if "complexity_handling" in performance_data:
                scores.append(performance_data["complexity_handling"])

            # 창의적 해결책
            if "creative_solutions" in performance_data:
                scores.append(performance_data["creative_solutions"])

            # 오류 복구 능력
            if "error_recovery" in performance_data:
                scores.append(performance_data["error_recovery"])

            # 기본값 사용
            if not scores:
                scores = [0.8, 0.7, 0.9]  # 기본 문제 해결 점수

            return sum(scores) / len(scores)
        except Exception as e:
            logger.error(f"문제 해결 능력 평가 오류: {e}")
            return 0.7

    def _assess_evolution_capability(self, performance_data: Dict[str, Any]) -> float:
        """진화 능력 평가"""
        try:
            indicators = self.assessment_criteria["evolution_capability"]["indicators"]
            scores = []

            # 자가 개선 능력
            if "self_improvement" in performance_data:
                scores.append(performance_data["self_improvement"])

            # 메타 학습 능력
            if "meta_learning" in performance_data:
                scores.append(performance_data["meta_learning"])

            # 진화 인식 능력
            if "evolution_awareness" in performance_data:
                scores.append(performance_data["evolution_awareness"])

            # 기본값 사용
            if not scores:
                scores = [0.9, 0.8, 0.7]  # 기본 진화 능력 점수

            return sum(scores) / len(scores)
        except Exception as e:
            logger.error(f"진화 능력 평가 오류: {e}")
            return 0.8

    def _identify_improvement_areas(self, scores: Dict[str, float]) -> List[str]:
        """개선 영역 식별"""
        improvement_areas = []

        if scores["autonomy"] < 0.7:
            improvement_areas.append("자율성 향상")
        if scores["learning_efficiency"] < 0.7:
            improvement_areas.append("학습 효율성 개선")
        if scores["problem_solving"] < 0.7:
            improvement_areas.append("문제 해결 능력 강화")
        if scores["evolution_capability"] < 0.7:
            improvement_areas.append("진화 능력 개발")

        return improvement_areas

    def _identify_strengths(self, scores: Dict[str, float]) -> List[str]:
        """강점 식별"""
        strengths = []

        if scores["autonomy"] >= 0.8:
            strengths.append("높은 자율성")
        if scores["learning_efficiency"] >= 0.8:
            strengths.append("우수한 학습 효율성")
        if scores["problem_solving"] >= 0.8:
            strengths.append("탁월한 문제 해결 능력")
        if scores["evolution_capability"] >= 0.8:
            strengths.append("강력한 진화 능력")

        return strengths

    def _calculate_assessment_confidence(
        self, performance_data: Dict[str, Any]
    ) -> float:
        """평가 신뢰도 계산"""
        try:
            # 데이터 품질 기반 신뢰도 계산
            data_quality_indicators = [
                "performance_score",
                "learning_efficiency",
                "autonomy_level",
                "problem_solving_capability",
            ]

            available_indicators = sum(
                1
                for indicator in data_quality_indicators
                if indicator in performance_data
            )

            confidence = min(1.0, available_indicators / len(data_quality_indicators))

            # 기본 신뢰도
            if confidence < 0.5:
                confidence = 0.7

            return confidence
        except Exception as e:
            logger.error(f"신뢰도 계산 오류: {e}")
            return 0.7

    def _analyze_evolution_progress(self) -> Dict[str, Any]:
        """진화 진행 상황 분석"""
        try:
            if len(self.assessment_history) < 2:
                return {"progress": "insufficient_data"}

            recent_assessments = self.assessment_history[-5:]  # 최근 5개 평가

            # 전체 점수 변화
            overall_scores = [
                assessment.overall_score for assessment in recent_assessments
            ]
            progress_rate = self._calculate_progress_rate(overall_scores)

            # 영역별 진행 상황
            area_progress = {
                "autonomy": self._calculate_progress_rate(
                    [a.autonomy_score for a in recent_assessments]
                ),
                "learning_efficiency": self._calculate_progress_rate(
                    [a.learning_efficiency_score for a in recent_assessments]
                ),
                "problem_solving": self._calculate_progress_rate(
                    [a.problem_solving_score for a in recent_assessments]
                ),
                "evolution_capability": self._calculate_progress_rate(
                    [a.evolution_capability_score for a in recent_assessments]
                ),
            }

            return {
                "overall_progress_rate": progress_rate,
                "area_progress": area_progress,
                "assessment_count": len(self.assessment_history),
                "latest_assessment_date": recent_assessments[-1].timestamp,
            }
        except Exception as e:
            logger.error(f"진화 진행 상황 분석 오류: {e}")
            return {"progress": "analysis_error"}

    def _calculate_progress_rate(self, scores: List[float]) -> float:
        """진행률 계산"""
        if len(scores) < 2:
            return 0.0

        try:
            # 선형 회귀로 진행률 계산
            x = list(range(len(scores)))
            y = scores

            n = len(x)
            sum_x = sum(x)
            sum_y = sum(y)
            sum_xy = sum(x[i] * y[i] for i in range(n))
            sum_x2 = sum(x[i] ** 2 for i in range(n))

            slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x**2)

            return slope
        except Exception as e:
            logger.error(f"진행률 계산 오류: {e}")
            return 0.0

    def _predict_evolution_direction(self) -> Dict[str, Any]:
        """진화 방향 예측"""
        try:
            if len(self.assessment_history) < 3:
                return {"prediction": "insufficient_data"}

            recent_scores = [
                assessment.overall_score for assessment in self.assessment_history[-3:]
            ]

            # 단순 선형 예측
            if len(recent_scores) >= 2:
                trend = recent_scores[-1] - recent_scores[-2]
                predicted_next = recent_scores[-1] + trend

                # 예측 신뢰도
                confidence = min(1.0, len(self.assessment_history) / 10)

                return {
                    "predicted_next_score": max(0.0, min(1.0, predicted_next)),
                    "prediction_confidence": confidence,
                    "trend_direction": (
                        "improving"
                        if trend > 0
                        else "declining" if trend < 0 else "stable"
                    ),
                    "estimated_time_to_next_stage": self._estimate_time_to_next_stage(
                        recent_scores[-1]
                    ),
                }
            else:
                return {"prediction": "insufficient_data"}

        except Exception as e:
            logger.error(f"진화 방향 예측 오류: {e}")
            return {"prediction": "prediction_error"}

    def _estimate_time_to_next_stage(self, current_score: float) -> str:
        """다음 단계까지 예상 시간"""
        try:
            if current_score >= 0.9:
                return "최고 단계 도달"
            elif current_score >= 0.8:
                return "1-2주 내"
            elif current_score >= 0.7:
                return "2-4주 내"
            elif current_score >= 0.6:
                return "1-2개월 내"
            else:
                return "3-6개월 내"
        except Exception as e:
            logger.error(f"예상 시간 계산 오류: {e}")
            return "예측 불가"

    def get_assessment_summary(self) -> Dict[str, Any]:
        """평가 요약 반환"""
        try:
            if not self.assessment_history:
                return {"status": "no_data"}

            latest = self.assessment_history[-1]

            return {
                "status": "success",
                "latest_assessment": {
                    "overall_score": latest.overall_score,
                    "autonomy_score": latest.autonomy_score,
                    "learning_efficiency_score": latest.learning_efficiency_score,
                    "problem_solving_score": latest.problem_solving_score,
                    "evolution_capability_score": latest.evolution_capability_score,
                    "assessment_confidence": latest.assessment_confidence,
                },
                "improvement_areas": latest.improvement_areas,
                "strengths": latest.strengths,
                "total_assessments": len(self.assessment_history),
                "evolution_progress": self._analyze_evolution_progress(),
                "future_prediction": self._predict_evolution_direction(),
                "timestamp": datetime.now().isoformat(),
            }
        except Exception as e:
            logger.error(f"평가 요약 생성 오류: {e}")
            return {"status": "error", "error": str(e)}


# 전역 인스턴스 생성
self_assessment_system = SelfAssessmentSystem()
