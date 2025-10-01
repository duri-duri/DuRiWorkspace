#!/usr/bin/env python3
"""
DuRi 자가 진화 추적 시스템
자신의 진화를 스스로 추적하고 분석하는 시스템
"""
import json
import logging
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


@dataclass
class EvolutionMetric:
    """진화 지표"""

    timestamp: str
    performance_score: float
    learning_efficiency: float
    autonomy_level: float
    problem_solving_capability: float
    evolution_stage: str
    improvement_rate: float


class SelfEvolutionTracker:
    """자가 진화 추적 시스템"""

    def __init__(self):
        """초기화"""
        self.evolution_history: List[EvolutionMetric] = []
        self.evolution_stages = [
            "초기 학습 단계",
            "기본 기능 습득",
            "자동화 능력 개발",
            "자가 개선 시작",
            "진화 인식 단계",
            "메타 학습 단계",
        ]
        self.current_stage = 0
        self.evolution_data_file = "evolution_tracker_data.json"
        self._load_evolution_data()

        logger.info("🧠 자가 진화 추적 시스템 초기화 완료")

    def _load_evolution_data(self):
        """진화 데이터 로드"""
        try:
            with open(self.evolution_data_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                self.evolution_history = [
                    EvolutionMetric(**metric) for metric in data.get("history", [])
                ]
                self.current_stage = data.get("current_stage", 0)
        except FileNotFoundError:
            logger.info("진화 데이터 파일이 없습니다. 새로 시작합니다.")
        except Exception as e:
            logger.error(f"진화 데이터 로드 오류: {e}")

    def _save_evolution_data(self):
        """진화 데이터 저장"""
        try:
            data = {
                "history": [asdict(metric) for metric in self.evolution_history],
                "current_stage": self.current_stage,
                "last_updated": datetime.now().isoformat(),
            }
            with open(self.evolution_data_file, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"진화 데이터 저장 오류: {e}")

    def track_self_evolution(self, interaction_data: Dict[str, Any]) -> Dict[str, Any]:
        """자신의 진화를 추적"""
        try:
            # 현재 성능 지표 계산
            current_metrics = self._calculate_current_metrics(interaction_data)

            # 진화 지표 생성
            evolution_metric = EvolutionMetric(
                timestamp=datetime.now().isoformat(),
                performance_score=current_metrics["performance_score"],
                learning_efficiency=current_metrics["learning_efficiency"],
                autonomy_level=current_metrics["autonomy_level"],
                problem_solving_capability=current_metrics[
                    "problem_solving_capability"
                ],
                evolution_stage=self.evolution_stages[self.current_stage],
                improvement_rate=current_metrics["improvement_rate"],
            )

            # 진화 히스토리에 추가
            self.evolution_history.append(evolution_metric)

            # 진화 단계 업데이트
            self._update_evolution_stage(current_metrics)

            # 데이터 저장
            self._save_evolution_data()

            # 진화 분석
            evolution_analysis = self._analyze_evolution_trend()

            logger.info(
                f"🧠 진화 추적 완료: 단계 {self.current_stage}, 점수 {current_metrics['performance_score']:.3f}"
            )

            return {
                "status": "success",
                "current_metrics": current_metrics,
                "evolution_stage": self.evolution_stages[self.current_stage],
                "evolution_analysis": evolution_analysis,
                "timestamp": datetime.now().isoformat(),
            }

        except Exception as e:
            logger.error(f"진화 추적 오류: {e}")
            return {"status": "error", "error": str(e)}

    def _calculate_current_metrics(
        self, interaction_data: Dict[str, Any]
    ) -> Dict[str, float]:
        """현재 성능 지표 계산"""
        try:
            # 기본 지표 추출
            performance_score = interaction_data.get("performance_score", 0.0)
            learning_efficiency = interaction_data.get("learning_efficiency", 0.0)
            autonomy_level = interaction_data.get("autonomy_level", 0.0)
            problem_solving = interaction_data.get("problem_solving_capability", 0.0)

            # 개선율 계산
            improvement_rate = self._calculate_improvement_rate()

            return {
                "performance_score": performance_score,
                "learning_efficiency": learning_efficiency,
                "autonomy_level": autonomy_level,
                "problem_solving_capability": problem_solving,
                "improvement_rate": improvement_rate,
            }
        except Exception as e:
            logger.error(f"지표 계산 오류: {e}")
            return {
                "performance_score": 0.0,
                "learning_efficiency": 0.0,
                "autonomy_level": 0.0,
                "problem_solving_capability": 0.0,
                "improvement_rate": 0.0,
            }

    def _calculate_improvement_rate(self) -> float:
        """개선율 계산"""
        if len(self.evolution_history) < 2:
            return 0.0

        try:
            recent_scores = [
                metric.performance_score for metric in self.evolution_history[-5:]
            ]
            if len(recent_scores) < 2:
                return 0.0

            # 최근 5개 점수의 평균 개선율
            improvements = []
            for i in range(1, len(recent_scores)):
                if recent_scores[i - 1] > 0:
                    improvement = (
                        recent_scores[i] - recent_scores[i - 1]
                    ) / recent_scores[i - 1]
                    improvements.append(improvement)

            return sum(improvements) / len(improvements) if improvements else 0.0
        except Exception as e:
            logger.error(f"개선율 계산 오류: {e}")
            return 0.0

    def _update_evolution_stage(self, current_metrics: Dict[str, float]):
        """진화 단계 업데이트"""
        try:
            performance = current_metrics["performance_score"]
            autonomy = current_metrics["autonomy_level"]
            learning = current_metrics["learning_efficiency"]

            # 진화 단계 결정 로직
            if performance > 0.9 and autonomy > 0.8 and learning > 0.8:
                self.current_stage = min(5, self.current_stage + 1)  # 메타 학습 단계
            elif performance > 0.8 and autonomy > 0.7 and learning > 0.7:
                self.current_stage = min(4, self.current_stage + 1)  # 진화 인식 단계
            elif performance > 0.7 and autonomy > 0.6 and learning > 0.6:
                self.current_stage = min(3, self.current_stage + 1)  # 자가 개선 시작
            elif performance > 0.6 and autonomy > 0.5 and learning > 0.5:
                self.current_stage = min(2, self.current_stage + 1)  # 자동화 능력 개발
            elif performance > 0.5 and autonomy > 0.4 and learning > 0.4:
                self.current_stage = min(1, self.current_stage + 1)  # 기본 기능 습득

        except Exception as e:
            logger.error(f"진화 단계 업데이트 오류: {e}")

    def _analyze_evolution_trend(self) -> Dict[str, Any]:
        """진화 트렌드 분석"""
        try:
            if len(self.evolution_history) < 2:
                return {"trend": "insufficient_data"}

            recent_metrics = self.evolution_history[-10:]  # 최근 10개 지표

            # 성능 트렌드
            performance_trend = self._calculate_trend(
                [m.performance_score for m in recent_metrics]
            )

            # 학습 효율성 트렌드
            learning_trend = self._calculate_trend(
                [m.learning_efficiency for m in recent_metrics]
            )

            # 자율성 트렌드
            autonomy_trend = self._calculate_trend(
                [m.autonomy_level for m in recent_metrics]
            )

            # 진화 속도
            evolution_speed = self._calculate_evolution_speed()

            return {
                "performance_trend": performance_trend,
                "learning_trend": learning_trend,
                "autonomy_trend": autonomy_trend,
                "evolution_speed": evolution_speed,
                "current_stage": self.evolution_stages[self.current_stage],
                "next_stage": (
                    self.evolution_stages[min(5, self.current_stage + 1)]
                    if self.current_stage < 5
                    else "최고 단계"
                ),
            }
        except Exception as e:
            logger.error(f"진화 트렌드 분석 오류: {e}")
            return {"trend": "analysis_error"}

    def _calculate_trend(self, values: List[float]) -> str:
        """트렌드 계산"""
        if len(values) < 2:
            return "stable"

        try:
            # 선형 회귀로 트렌드 계산
            x = list(range(len(values)))
            y = values

            n = len(x)
            sum_x = sum(x)
            sum_y = sum(y)
            sum_xy = sum(x[i] * y[i] for i in range(n))
            sum_x2 = sum(x[i] ** 2 for i in range(n))

            slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x**2)

            if slope > 0.01:
                return "improving"
            elif slope < -0.01:
                return "declining"
            else:
                return "stable"
        except Exception as e:
            logger.error(f"트렌드 계산 오류: {e}")
            return "stable"

    def _calculate_evolution_speed(self) -> float:
        """진화 속도 계산"""
        if len(self.evolution_history) < 5:
            return 0.0

        try:
            # 최근 5개 지표의 평균 개선율
            recent_metrics = self.evolution_history[-5:]
            improvements = []

            for i in range(1, len(recent_metrics)):
                prev_score = recent_metrics[i - 1].performance_score
                curr_score = recent_metrics[i].performance_score

                if prev_score > 0:
                    improvement = (curr_score - prev_score) / prev_score
                    improvements.append(improvement)

            return sum(improvements) / len(improvements) if improvements else 0.0
        except Exception as e:
            logger.error(f"진화 속도 계산 오류: {e}")
            return 0.0

    def get_evolution_summary(self) -> Dict[str, Any]:
        """진화 요약 반환"""
        try:
            if not self.evolution_history:
                return {"status": "no_data"}

            latest = self.evolution_history[-1]

            return {
                "status": "success",
                "current_stage": self.evolution_stages[self.current_stage],
                "total_evolution_records": len(self.evolution_history),
                "latest_metrics": {
                    "performance_score": latest.performance_score,
                    "learning_efficiency": latest.learning_efficiency,
                    "autonomy_level": latest.autonomy_level,
                    "problem_solving_capability": latest.problem_solving_capability,
                    "improvement_rate": latest.improvement_rate,
                },
                "evolution_trend": self._analyze_evolution_trend(),
                "timestamp": datetime.now().isoformat(),
            }
        except Exception as e:
            logger.error(f"진화 요약 생성 오류: {e}")
            return {"status": "error", "error": str(e)}


# 전역 인스턴스 생성
self_evolution_tracker = SelfEvolutionTracker()
