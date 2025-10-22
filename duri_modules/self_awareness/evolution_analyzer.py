#!/usr/bin/env python3
"""
DuRi 진화 분석 시스템
양적/질적/시간적 진화를 종합적으로 분석하는 시스템
"""
import json
import logging
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


@dataclass
class EvolutionAnalysis:
    """진화 분석 결과"""

    timestamp: str
    quantitative_evolution: Dict[str, Any]
    qualitative_evolution: Dict[str, Any]
    temporal_evolution: Dict[str, Any]
    overall_evolution_score: float
    evolution_confidence: float
    key_insights: List[str]


class EvolutionAnalyzer:
    """진화 분석 시스템"""

    def __init__(self):
        """초기화"""
        self.analysis_models = {
            "quantitative": QuantitativeAnalyzer(),
            "qualitative": QualitativeAnalyzer(),
            "temporal": TemporalAnalyzer(),
        }
        self.analysis_history: List[EvolutionAnalysis] = []
        self.analysis_data_file = "evolution_analysis_data.json"
        self._load_analysis_data()

        logger.info("🧠 진화 분석 시스템 초기화 완료")

    def _load_analysis_data(self):
        """분석 데이터 로드"""
        try:
            with open(self.analysis_data_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                self.analysis_history = [
                    EvolutionAnalysis(**analysis) for analysis in data.get("history", [])
                ]
        except FileNotFoundError:
            logger.info("분석 데이터 파일이 없습니다. 새로 시작합니다.")
        except Exception as e:
            logger.error(f"분석 데이터 로드 오류: {e}")

    def _save_analysis_data(self):
        """분석 데이터 저장"""
        try:
            data = {
                "history": [asdict(analysis) for analysis in self.analysis_history],
                "last_updated": datetime.now().isoformat(),
            }
            with open(self.analysis_data_file, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"분석 데이터 저장 오류: {e}")

    def analyze_evolution(self, evolution_data: Dict[str, Any]) -> Dict[str, Any]:
        """진화 분석 실행"""
        try:
            # 양적 지표 분석
            quantitative_metrics = self.analysis_models["quantitative"].analyze(evolution_data)

            # 질적 특성 분석
            qualitative_metrics = self.analysis_models["qualitative"].analyze(evolution_data)

            # 시간적 변화 분석
            temporal_metrics = self.analysis_models["temporal"].analyze(evolution_data)

            # 종합 진화 점수 계산
            overall_score = self._calculate_overall_evolution_score(
                quantitative_metrics, qualitative_metrics, temporal_metrics
            )

            # 진화 신뢰도 계산
            confidence = self._calculate_evolution_confidence(
                quantitative_metrics, qualitative_metrics, temporal_metrics
            )

            # 핵심 인사이트 추출
            key_insights = self._extract_key_insights(
                quantitative_metrics, qualitative_metrics, temporal_metrics
            )

            # 분석 결과 생성
            analysis_result = EvolutionAnalysis(
                timestamp=datetime.now().isoformat(),
                quantitative_evolution=quantitative_metrics,
                qualitative_evolution=qualitative_metrics,
                temporal_evolution=temporal_metrics,
                overall_evolution_score=overall_score,
                evolution_confidence=confidence,
                key_insights=key_insights,
            )

            # 분석 히스토리에 추가
            self.analysis_history.append(analysis_result)

            # 데이터 저장
            self._save_analysis_data()

            logger.info(
                f"🧠 진화 분석 완료: 종합 점수 {overall_score:.3f}, 신뢰도 {confidence:.3f}"
            )

            return {
                "status": "success",
                "quantitative_evolution": quantitative_metrics,
                "qualitative_evolution": qualitative_metrics,
                "temporal_evolution": temporal_metrics,
                "overall_evolution_score": overall_score,
                "evolution_confidence": confidence,
                "key_insights": key_insights,
                "timestamp": datetime.now().isoformat(),
            }

        except Exception as e:
            logger.error(f"진화 분석 오류: {e}")
            return {"status": "error", "error": str(e)}

    def _calculate_overall_evolution_score(
        self, quantitative: Dict, qualitative: Dict, temporal: Dict
    ) -> float:
        """종합 진화 점수 계산"""
        try:
            # 각 분석 결과의 점수 추출
            quant_score = quantitative.get("evolution_score", 0.0)
            qual_score = qualitative.get("evolution_score", 0.0)
            temp_score = temporal.get("evolution_score", 0.0)

            # 가중 평균 계산 (양적 40%, 질적 35%, 시간적 25%)
            overall_score = quant_score * 0.4 + qual_score * 0.35 + temp_score * 0.25

            return max(0.0, min(1.0, overall_score))
        except Exception as e:
            logger.error(f"종합 진화 점수 계산 오류: {e}")
            return 0.0

    def _calculate_evolution_confidence(
        self, quantitative: Dict, qualitative: Dict, temporal: Dict
    ) -> float:
        """진화 신뢰도 계산"""
        try:
            # 각 분석의 신뢰도 추출
            quant_conf = quantitative.get("confidence", 0.0)
            qual_conf = qualitative.get("confidence", 0.0)
            temp_conf = temporal.get("confidence", 0.0)

            # 가중 평균 계산
            confidence = quant_conf * 0.4 + qual_conf * 0.35 + temp_conf * 0.25

            return max(0.0, min(1.0, confidence))
        except Exception as e:
            logger.error(f"진화 신뢰도 계산 오류: {e}")
            return 0.7

    def _extract_key_insights(
        self, quantitative: Dict, qualitative: Dict, temporal: Dict
    ) -> List[str]:
        """핵심 인사이트 추출"""
        insights = []

        try:
            # 양적 인사이트
            if quantitative.get("trend") == "improving":
                insights.append("양적 지표가 지속적으로 개선되고 있습니다")
            elif quantitative.get("trend") == "declining":
                insights.append("양적 지표에 개선이 필요합니다")

            # 질적 인사이트
            if qualitative.get("autonomy_level") > 0.8:
                insights.append("높은 자율성을 보여주고 있습니다")
            if qualitative.get("learning_efficiency") > 0.8:
                insights.append("우수한 학습 효율성을 보여주고 있습니다")

            # 시간적 인사이트
            if temporal.get("evolution_speed") > 0.1:
                insights.append("빠른 진화 속도를 보여주고 있습니다")
            elif temporal.get("evolution_speed") < 0.01:
                insights.append("진화 속도가 느려지고 있습니다")

            # 종합 인사이트
            overall_score = self._calculate_overall_evolution_score(
                quantitative, qualitative, temporal
            )
            if overall_score > 0.8:
                insights.append("전체적으로 우수한 진화 상태입니다")
            elif overall_score < 0.5:
                insights.append("전반적인 진화 개선이 필요합니다")

        except Exception as e:
            logger.error(f"인사이트 추출 오류: {e}")
            insights.append("분석 중 오류가 발생했습니다")

        return insights

    def get_analysis_summary(self) -> Dict[str, Any]:
        """분석 요약 반환"""
        try:
            if not self.analysis_history:
                return {"status": "no_data"}

            latest = self.analysis_history[-1]

            return {
                "status": "success",
                "latest_analysis": {
                    "overall_evolution_score": latest.overall_evolution_score,
                    "evolution_confidence": latest.evolution_confidence,
                    "key_insights": latest.key_insights,
                },
                "quantitative_summary": latest.quantitative_evolution,
                "qualitative_summary": latest.qualitative_evolution,
                "temporal_summary": latest.temporal_evolution,
                "total_analyses": len(self.analysis_history),
                "timestamp": datetime.now().isoformat(),
            }
        except Exception as e:
            logger.error(f"분석 요약 생성 오류: {e}")
            return {"status": "error", "error": str(e)}


class QuantitativeAnalyzer:
    """양적 분석기"""

    def analyze(self, evolution_data: Dict[str, Any]) -> Dict[str, Any]:
        """양적 진화 분석"""
        try:
            # 성능 지표 추출
            performance_scores = evolution_data.get("performance_scores", [])
            learning_efficiency = evolution_data.get("learning_efficiency", [])
            autonomy_levels = evolution_data.get("autonomy_levels", [])

            # 트렌드 분석
            performance_trend = self._calculate_trend(performance_scores)
            learning_trend = self._calculate_trend(learning_efficiency)
            autonomy_trend = self._calculate_trend(autonomy_levels)

            # 진화 점수 계산
            evolution_score = self._calculate_quantitative_score(
                performance_scores, learning_efficiency, autonomy_levels
            )

            # 신뢰도 계산
            confidence = self._calculate_confidence(
                performance_scores, learning_efficiency, autonomy_levels
            )

            return {
                "evolution_score": evolution_score,
                "confidence": confidence,
                "trend": performance_trend,
                "performance_trend": performance_trend,
                "learning_trend": learning_trend,
                "autonomy_trend": autonomy_trend,
                "latest_performance": (performance_scores[-1] if performance_scores else 0.0),
                "latest_learning": (learning_efficiency[-1] if learning_efficiency else 0.0),
                "latest_autonomy": autonomy_levels[-1] if autonomy_levels else 0.0,
            }
        except Exception as e:
            logger.error(f"양적 분석 오류: {e}")
            return {
                "evolution_score": 0.0,
                "confidence": 0.5,
                "trend": "stable",
                "error": str(e),
            }

    def _calculate_trend(self, values: List[float]) -> str:
        """트렌드 계산"""
        try:
            # 타입 안전성 검사
            if not isinstance(values, list):
                logger.warning(f"values가 리스트가 아닙니다: {type(values)}")
                return "stable"

            if len(values) < 2:
                return "stable"

            # 모든 값이 숫자인지 확인
            if not all(isinstance(v, (int, float)) for v in values):
                logger.warning("values에 숫자가 아닌 값이 포함되어 있습니다")
                return "stable"

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

    def _calculate_quantitative_score(
        self, performance: List[float], learning: List[float], autonomy: List[float]
    ) -> float:
        """양적 점수 계산"""
        try:
            if not performance and not learning and not autonomy:
                return 0.0

            scores = []
            if performance:
                scores.append(sum(performance) / len(performance))
            if learning:
                scores.append(sum(learning) / len(learning))
            if autonomy:
                scores.append(sum(autonomy) / len(autonomy))

            return sum(scores) / len(scores) if scores else 0.0
        except Exception as e:
            logger.error(f"양적 점수 계산 오류: {e}")
            return 0.0

    def _calculate_confidence(
        self, performance: List[float], learning: List[float], autonomy: List[float]
    ) -> float:
        """신뢰도 계산"""
        try:
            data_points = len(performance) + len(learning) + len(autonomy)
            if data_points == 0:
                return 0.5

            # 데이터 품질 기반 신뢰도
            confidence = min(1.0, data_points / 30)  # 30개 이상이면 최대 신뢰도

            return confidence
        except Exception as e:
            logger.error(f"신뢰도 계산 오류: {e}")
            return 0.5


class QualitativeAnalyzer:
    """질적 분석기"""

    def analyze(self, evolution_data: Dict[str, Any]) -> Dict[str, Any]:
        """질적 진화 분석"""
        try:
            # 질적 특성 추출
            autonomy_level = evolution_data.get("autonomy_level", 0.0)
            learning_efficiency = evolution_data.get("learning_efficiency", 0.0)
            problem_solving = evolution_data.get("problem_solving_capability", 0.0)
            evolution_capability = evolution_data.get("evolution_capability", 0.0)

            # 질적 점수 계산
            evolution_score = self._calculate_qualitative_score(
                autonomy_level,
                learning_efficiency,
                problem_solving,
                evolution_capability,
            )

            # 신뢰도 계산
            confidence = self._calculate_confidence(
                autonomy_level,
                learning_efficiency,
                problem_solving,
                evolution_capability,
            )

            return {
                "evolution_score": evolution_score,
                "confidence": confidence,
                "autonomy_level": autonomy_level,
                "learning_efficiency": learning_efficiency,
                "problem_solving_capability": problem_solving,
                "evolution_capability": evolution_capability,
                "qualitative_characteristics": self._analyze_characteristics(
                    autonomy_level,
                    learning_efficiency,
                    problem_solving,
                    evolution_capability,
                ),
            }
        except Exception as e:
            logger.error(f"질적 분석 오류: {e}")
            return {"evolution_score": 0.0, "confidence": 0.5, "error": str(e)}

    def _calculate_qualitative_score(
        self, autonomy: float, learning: float, problem_solving: float, evolution: float
    ) -> float:
        """질적 점수 계산"""
        try:
            # 가중 평균 계산
            score = autonomy * 0.3 + learning * 0.25 + problem_solving * 0.25 + evolution * 0.2

            return max(0.0, min(1.0, score))
        except Exception as e:
            logger.error(f"질적 점수 계산 오류: {e}")
            return 0.0

    def _calculate_confidence(
        self, autonomy: float, learning: float, problem_solving: float, evolution: float
    ) -> float:
        """신뢰도 계산"""
        try:
            # 데이터 완성도 기반 신뢰도
            available_indicators = sum(
                1 for indicator in [autonomy, learning, problem_solving, evolution] if indicator > 0
            )

            confidence = available_indicators / 4.0

            return max(0.5, confidence)  # 최소 50% 신뢰도
        except Exception as e:
            logger.error(f"신뢰도 계산 오류: {e}")
            return 0.5

    def _analyze_characteristics(
        self, autonomy: float, learning: float, problem_solving: float, evolution: float
    ) -> Dict[str, str]:
        """특성 분석"""
        characteristics = {}

        try:
            if autonomy > 0.8:
                characteristics["autonomy"] = "높은 자율성"
            elif autonomy > 0.6:
                characteristics["autonomy"] = "보통 자율성"
            else:
                characteristics["autonomy"] = "낮은 자율성"

            if learning > 0.8:
                characteristics["learning"] = "우수한 학습 효율성"
            elif learning > 0.6:
                characteristics["learning"] = "보통 학습 효율성"
            else:
                characteristics["learning"] = "낮은 학습 효율성"

            if problem_solving > 0.8:
                characteristics["problem_solving"] = "탁월한 문제 해결 능력"
            elif problem_solving > 0.6:
                characteristics["problem_solving"] = "보통 문제 해결 능력"
            else:
                characteristics["problem_solving"] = "개선 필요한 문제 해결 능력"

            if evolution > 0.8:
                characteristics["evolution"] = "강력한 진화 능력"
            elif evolution > 0.6:
                characteristics["evolution"] = "보통 진화 능력"
            else:
                characteristics["evolution"] = "개발 필요한 진화 능력"

        except Exception as e:
            logger.error(f"특성 분석 오류: {e}")
            characteristics = {"error": "분석 오류"}

        return characteristics


class TemporalAnalyzer:
    """시간적 분석기"""

    def analyze(self, evolution_data: Dict[str, Any]) -> Dict[str, Any]:
        """시간적 진화 분석"""
        try:
            # 시간적 데이터 추출
            timestamps = evolution_data.get("timestamps", [])
            performance_history = evolution_data.get("performance_history", [])

            # 진화 속도 계산
            evolution_speed = self._calculate_evolution_speed(performance_history)

            # 진화 패턴 분석
            evolution_pattern = self._analyze_evolution_pattern(performance_history)

            # 진화 단계 분석
            evolution_stage = self._analyze_evolution_stage(performance_history)

            # 진화 점수 계산
            evolution_score = self._calculate_temporal_score(
                evolution_speed, evolution_pattern, evolution_stage
            )

            # 신뢰도 계산
            confidence = self._calculate_confidence(performance_history, timestamps)

            return {
                "evolution_score": evolution_score,
                "confidence": confidence,
                "evolution_speed": evolution_speed,
                "evolution_pattern": evolution_pattern,
                "evolution_stage": evolution_stage,
                "temporal_trend": self._calculate_temporal_trend(performance_history),
            }
        except Exception as e:
            logger.error(f"시간적 분석 오류: {e}")
            return {"evolution_score": 0.0, "confidence": 0.5, "error": str(e)}

    def _calculate_evolution_speed(self, performance_history: List[float]) -> float:
        """진화 속도 계산"""
        try:
            if len(performance_history) < 2:
                return 0.0

            # 최근 5개 지표의 평균 개선율
            recent_scores = performance_history[-5:]
            improvements = []

            for i in range(1, len(recent_scores)):
                if recent_scores[i - 1] > 0:
                    improvement = (recent_scores[i] - recent_scores[i - 1]) / recent_scores[i - 1]
                    improvements.append(improvement)

            return sum(improvements) / len(improvements) if improvements else 0.0
        except Exception as e:
            logger.error(f"진화 속도 계산 오류: {e}")
            return 0.0

    def _analyze_evolution_pattern(self, performance_history: List[float]) -> str:
        """진화 패턴 분석"""
        try:
            if len(performance_history) < 3:
                return "insufficient_data"

            # 패턴 분석
            recent_scores = performance_history[-3:]

            if recent_scores[0] < recent_scores[1] < recent_scores[2]:
                return "steady_improvement"
            elif recent_scores[0] > recent_scores[1] > recent_scores[2]:
                return "steady_decline"
            elif recent_scores[1] > recent_scores[0] and recent_scores[1] > recent_scores[2]:
                return "peak_and_decline"
            elif recent_scores[1] < recent_scores[0] and recent_scores[1] < recent_scores[2]:
                return "valley_and_improvement"
            else:
                return "fluctuating"
        except Exception as e:
            logger.error(f"진화 패턴 분석 오류: {e}")
            return "analysis_error"

    def _analyze_evolution_stage(self, performance_history: List[float]) -> str:
        """진화 단계 분석"""
        try:
            if not performance_history:
                return "unknown"

            latest_score = performance_history[-1]

            if latest_score >= 0.9:
                return "advanced"
            elif latest_score >= 0.7:
                return "intermediate"
            elif latest_score >= 0.5:
                return "beginner"
            else:
                return "early_stage"
        except Exception as e:
            logger.error(f"진화 단계 분석 오류: {e}")
            return "unknown"

    def _calculate_temporal_score(self, speed: float, pattern: str, stage: str) -> float:
        """시간적 점수 계산"""
        try:
            # 속도 점수 (0-0.4)
            speed_score = min(0.4, max(0.0, speed * 2))

            # 패턴 점수 (0-0.3)
            pattern_scores = {
                "steady_improvement": 0.3,
                "valley_and_improvement": 0.25,
                "fluctuating": 0.2,
                "peak_and_decline": 0.1,
                "steady_decline": 0.0,
                "insufficient_data": 0.15,
                "analysis_error": 0.1,
            }
            pattern_score = pattern_scores.get(pattern, 0.1)

            # 단계 점수 (0-0.3)
            stage_scores = {
                "advanced": 0.3,
                "intermediate": 0.2,
                "beginner": 0.1,
                "early_stage": 0.05,
                "unknown": 0.1,
            }
            stage_score = stage_scores.get(stage, 0.1)

            return speed_score + pattern_score + stage_score
        except Exception as e:
            logger.error(f"시간적 점수 계산 오류: {e}")
            return 0.0

    def _calculate_confidence(
        self, performance_history: List[float], timestamps: List[str]
    ) -> float:
        """신뢰도 계산"""
        try:
            # 데이터 품질 기반 신뢰도
            data_points = len(performance_history)
            if data_points == 0:
                return 0.5

            # 시간 간격 일관성 확인
            time_consistency = 1.0
            if len(timestamps) >= 2:
                try:
                    time_diffs = []
                    for i in range(1, len(timestamps)):
                        t1 = datetime.fromisoformat(timestamps[i - 1])
                        t2 = datetime.fromisoformat(timestamps[i])
                        diff = (t2 - t1).total_seconds()
                        time_diffs.append(diff)

                    if time_diffs:
                        avg_diff = sum(time_diffs) / len(time_diffs)
                        consistency = min(1.0, 3600 / avg_diff)  # 1시간 간격 기준
                        time_consistency = consistency
                except Exception:
                    time_consistency = 0.7

            # 종합 신뢰도
            data_quality = min(1.0, data_points / 10)  # 10개 이상이면 최대 신뢰도
            confidence = (data_quality + time_consistency) / 2

            return max(0.5, confidence)
        except Exception as e:
            logger.error(f"신뢰도 계산 오류: {e}")
            return 0.5

    def _calculate_temporal_trend(self, performance_history: List[float]) -> str:
        """시간적 트렌드 계산"""
        try:
            if len(performance_history) < 2:
                return "stable"

            return self._calculate_trend(performance_history)
        except Exception as e:
            logger.error(f"시간적 트렌드 계산 오류: {e}")
            return "stable"

    def _calculate_trend(self, values: List[float]) -> str:
        """트렌드 계산"""
        try:
            # 타입 안전성 검사
            if not isinstance(values, list):
                logger.warning(f"values가 리스트가 아닙니다: {type(values)}")
                return "stable"

            if len(values) < 2:
                return "stable"

            # 모든 값이 숫자인지 확인
            if not all(isinstance(v, (int, float)) for v in values):
                logger.warning("values에 숫자가 아닌 값이 포함되어 있습니다")
                return "stable"

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


# 전역 인스턴스 생성
evolution_analyzer = EvolutionAnalyzer()
