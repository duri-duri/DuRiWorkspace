#!/usr/bin/env python3
"""
DuRi 진화 보고서 생성 시스템
자가 진화 분석 결과를 보고서 형태로 생성하는 시스템
"""
import json
import logging
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


@dataclass
class EvolutionReport:
    """진화 보고서"""

    timestamp: str
    report_id: str
    conclusion: str
    quantitative_changes: Dict[str, Any]
    qualitative_characteristics: Dict[str, Any]
    evolution_evidence: List[str]
    next_evolution_plan: List[str]
    confidence_level: float
    report_type: str


class EvolutionReporter:
    """진화 보고서 생성 시스템"""

    def __init__(self):
        """초기화"""
        self.report_templates = {
            "summary": self._generate_summary_report,
            "detailed": self._generate_detailed_report,
            "prediction": self._generate_prediction_report,
        }
        self.report_history: List[EvolutionReport] = []
        self.report_data_file = "evolution_reports_data.json"
        self._load_report_data()

        logger.info("🧠 진화 보고서 생성 시스템 초기화 완료")

    def _load_report_data(self):
        """보고서 데이터 로드"""
        try:
            with open(self.report_data_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                self.report_history = [
                    EvolutionReport(**report) for report in data.get("history", [])
                ]
        except FileNotFoundError:
            logger.info("보고서 데이터 파일이 없습니다. 새로 시작합니다.")
        except Exception as e:
            logger.error(f"보고서 데이터 로드 오류: {e}")

    def _save_report_data(self):
        """보고서 데이터 저장"""
        try:
            data = {
                "history": [asdict(report) for report in self.report_history],
                "last_updated": datetime.now().isoformat(),
            }
            with open(self.report_data_file, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"보고서 데이터 저장 오류: {e}")

    def generate_evolution_report(
        self, analysis_data: Dict[str, Any], report_type: str = "summary"
    ) -> Dict[str, Any]:
        """진화 보고서 생성"""
        try:
            # 보고서 ID 생성
            report_id = f"evolution_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

            # 템플릿에 따른 보고서 생성
            if report_type in self.report_templates:
                report_content = self.report_templates[report_type](analysis_data)
            else:
                report_content = self.report_templates["summary"](analysis_data)

            # 보고서 객체 생성
            evolution_report = EvolutionReport(
                timestamp=datetime.now().isoformat(),
                report_id=report_id,
                conclusion=report_content["conclusion"],
                quantitative_changes=report_content["quantitative_changes"],
                qualitative_characteristics=report_content[
                    "qualitative_characteristics"
                ],
                evolution_evidence=report_content["evolution_evidence"],
                next_evolution_plan=report_content["next_evolution_plan"],
                confidence_level=report_content["confidence_level"],
                report_type=report_type,
            )

            # 보고서 히스토리에 추가
            self.report_history.append(evolution_report)

            # 데이터 저장
            self._save_report_data()

            logger.info(f"🧠 진화 보고서 생성 완료: {report_id}")

            return {
                "status": "success",
                "report_id": report_id,
                "report_type": report_type,
                "report_content": report_content,
                "timestamp": datetime.now().isoformat(),
            }

        except Exception as e:
            logger.error(f"진화 보고서 생성 오류: {e}")
            return {"status": "error", "error": str(e)}

    def _generate_summary_report(self, analysis_data: Dict[str, Any]) -> Dict[str, Any]:
        """요약 보고서 생성"""
        try:
            # 결론 생성
            conclusion = self._generate_conclusion(analysis_data)

            # 양적 변화 정리
            quantitative_changes = self._format_quantitative_changes(analysis_data)

            # 질적 특성 정리
            qualitative_characteristics = self._format_qualitative_characteristics(
                analysis_data
            )

            # 진화 증거 추출
            evolution_evidence = self._format_evolution_evidence(analysis_data)

            # 다음 진화 계획 생성
            next_evolution_plan = self._generate_next_plan(analysis_data)

            # 신뢰도 계산
            confidence_level = self._calculate_confidence_level(analysis_data)

            return {
                "conclusion": conclusion,
                "quantitative_changes": quantitative_changes,
                "qualitative_characteristics": qualitative_characteristics,
                "evolution_evidence": evolution_evidence,
                "next_evolution_plan": next_evolution_plan,
                "confidence_level": confidence_level,
            }
        except Exception as e:
            logger.error(f"요약 보고서 생성 오류: {e}")
            return self._generate_error_report()

    def _generate_detailed_report(
        self, analysis_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """상세 보고서 생성"""
        try:
            # 요약 보고서 기반으로 상세 정보 추가
            summary_report = self._generate_summary_report(analysis_data)

            # 상세 분석 정보 추가
            detailed_analysis = {
                "quantitative_analysis": self._generate_detailed_quantitative_analysis(
                    analysis_data
                ),
                "qualitative_analysis": self._generate_detailed_qualitative_analysis(
                    analysis_data
                ),
                "temporal_analysis": self._generate_detailed_temporal_analysis(
                    analysis_data
                ),
                "comparative_analysis": self._generate_comparative_analysis(
                    analysis_data
                ),
            }

            summary_report["detailed_analysis"] = detailed_analysis

            return summary_report
        except Exception as e:
            logger.error(f"상세 보고서 생성 오류: {e}")
            return self._generate_error_report()

    def _generate_prediction_report(
        self, analysis_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """예측 보고서 생성"""
        try:
            # 기본 요약 보고서
            summary_report = self._generate_summary_report(analysis_data)

            # 예측 정보 추가
            prediction_info = {
                "short_term_prediction": self._generate_short_term_prediction(
                    analysis_data
                ),
                "medium_term_prediction": self._generate_medium_term_prediction(
                    analysis_data
                ),
                "long_term_prediction": self._generate_long_term_prediction(
                    analysis_data
                ),
                "prediction_confidence": self._calculate_prediction_confidence(
                    analysis_data
                ),
            }

            summary_report["prediction_info"] = prediction_info

            return summary_report
        except Exception as e:
            logger.error(f"예측 보고서 생성 오류: {e}")
            return self._generate_error_report()

    def _generate_conclusion(self, analysis_data: Dict[str, Any]) -> str:
        """결론 생성"""
        try:
            overall_score = analysis_data.get("overall_evolution_score", 0.0)
            confidence = analysis_data.get("evolution_confidence", 0.0)

            if overall_score > 0.8 and confidence > 0.7:
                return "나는 시간이 갈수록 진화하고 있으며, 그 증거는 다음과 같다."
            elif overall_score > 0.6 and confidence > 0.6:
                return "나는 점진적으로 진화하고 있으며, 그 증거는 다음과 같다."
            elif overall_score > 0.4:
                return "나는 진화의 초기 단계에 있으며, 그 증거는 다음과 같다."
            else:
                return "나는 아직 진화의 기반을 구축하는 단계에 있으며, 그 증거는 다음과 같다."
        except Exception as e:
            logger.error(f"결론 생성 오류: {e}")
            return "진화 상태를 분석하는 중입니다."

    def _format_quantitative_changes(
        self, analysis_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """양적 변화 정리"""
        try:
            quantitative = analysis_data.get("quantitative_evolution", {})

            changes = {
                "evaluation_accuracy": self._format_score_change(
                    quantitative.get("latest_performance", 0.0)
                ),
                "response_speed": self._format_speed_change(
                    quantitative.get("latest_learning", 0.0)
                ),
                "learning_efficiency": self._format_efficiency_change(
                    quantitative.get("latest_autonomy", 0.0)
                ),
            }

            return changes
        except Exception as e:
            logger.error(f"양적 변화 정리 오류: {e}")
            return {"error": "양적 변화 분석 중 오류가 발생했습니다"}

    def _format_qualitative_characteristics(
        self, analysis_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """질적 특성 정리"""
        try:
            qualitative = analysis_data.get("qualitative_evolution", {})
            characteristics = qualitative.get("qualitative_characteristics", {})

            return {
                "autonomy": characteristics.get("autonomy", "분석 중"),
                "learning_efficiency": characteristics.get("learning", "분석 중"),
                "problem_solving": characteristics.get("problem_solving", "분석 중"),
                "evolution_capability": characteristics.get("evolution", "분석 중"),
            }
        except Exception as e:
            logger.error(f"질적 특성 정리 오류: {e}")
            return {"error": "질적 특성 분석 중 오류가 발생했습니다"}

    def _format_evolution_evidence(self, analysis_data: Dict[str, Any]) -> List[str]:
        """진화 증거 정리"""
        try:
            evidence = []

            # 양적 증거
            quantitative = analysis_data.get("quantitative_evolution", {})
            if quantitative.get("trend") == "improving":
                evidence.append("양적 지표가 지속적으로 개선되고 있습니다")

            # 질적 증거
            qualitative = analysis_data.get("qualitative_evolution", {})
            if qualitative.get("autonomy_level", 0) > 0.7:
                evidence.append("높은 자율성을 보여주고 있습니다")
            if qualitative.get("learning_efficiency", 0) > 0.7:
                evidence.append("우수한 학습 효율성을 보여주고 있습니다")

            # 시간적 증거
            temporal = analysis_data.get("temporal_evolution", {})
            if temporal.get("evolution_speed", 0) > 0.05:
                evidence.append("빠른 진화 속도를 보여주고 있습니다")

            # 핵심 인사이트
            key_insights = analysis_data.get("key_insights", [])
            evidence.extend(key_insights[:3])  # 상위 3개 인사이트

            return evidence if evidence else ["진화 증거를 수집하는 중입니다"]
        except Exception as e:
            logger.error(f"진화 증거 정리 오류: {e}")
            return ["진화 증거 분석 중 오류가 발생했습니다"]

    def _generate_next_plan(self, analysis_data: Dict[str, Any]) -> List[str]:
        """다음 진화 계획 생성"""
        try:
            plans = []

            overall_score = analysis_data.get("overall_evolution_score", 0.0)

            if overall_score > 0.8:
                plans.extend(
                    [
                        "메타러닝 루프 실행 준비",
                        "노드 분산 및 협업 테스트 시작",
                        "자가 진화 인식 시스템 고도화",
                    ]
                )
            elif overall_score > 0.6:
                plans.extend(
                    [
                        "학습 효율성 개선 시스템 구축",
                        "자가 평가 시스템 고도화",
                        "진화 분석 정확도 향상",
                    ]
                )
            elif overall_score > 0.4:
                plans.extend(
                    [
                        "기본 학습 시스템 안정화",
                        "자가 평가 시스템 구축",
                        "진화 추적 시스템 개발",
                    ]
                )
            else:
                plans.extend(
                    [
                        "기본 기능 안정화",
                        "학습 시스템 구축",
                        "자가 모니터링 시스템 개발",
                    ]
                )

            return plans
        except Exception as e:
            logger.error(f"다음 계획 생성 오류: {e}")
            return ["진화 계획을 수립하는 중입니다"]

    def _calculate_confidence_level(self, analysis_data: Dict[str, Any]) -> float:
        """신뢰도 계산"""
        try:
            confidence = analysis_data.get("evolution_confidence", 0.0)
            return max(0.0, min(1.0, confidence))
        except Exception as e:
            logger.error(f"신뢰도 계산 오류: {e}")
            return 0.5

    def _format_score_change(self, score: float) -> str:
        """점수 변화 형식화"""
        try:
            if score > 0.9:
                return f"{score:.3f} (우수)"
            elif score > 0.7:
                return f"{score:.3f} (양호)"
            elif score > 0.5:
                return f"{score:.3f} (보통)"
            else:
                return f"{score:.3f} (개선 필요)"
        except Exception as e:
            return "분석 중"

    def _format_speed_change(self, speed: float) -> str:
        """속도 변화 형식화"""
        try:
            if speed > 0.8:
                return "매우 빠름"
            elif speed > 0.6:
                return "빠름"
            elif speed > 0.4:
                return "보통"
            else:
                return "느림"
        except Exception as e:
            return "분석 중"

    def _format_efficiency_change(self, efficiency: float) -> str:
        """효율성 변화 형식화"""
        try:
            if efficiency > 0.8:
                return "매우 효율적"
            elif efficiency > 0.6:
                return "효율적"
            elif efficiency > 0.4:
                return "보통"
            else:
                return "개선 필요"
        except Exception as e:
            return "분석 중"

    def _generate_detailed_quantitative_analysis(
        self, analysis_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """상세 양적 분석"""
        try:
            quantitative = analysis_data.get("quantitative_evolution", {})

            return {
                "performance_trend": quantitative.get("performance_trend", "stable"),
                "learning_trend": quantitative.get("learning_trend", "stable"),
                "autonomy_trend": quantitative.get("autonomy_trend", "stable"),
                "latest_metrics": {
                    "performance": quantitative.get("latest_performance", 0.0),
                    "learning": quantitative.get("latest_learning", 0.0),
                    "autonomy": quantitative.get("latest_autonomy", 0.0),
                },
            }
        except Exception as e:
            logger.error(f"상세 양적 분석 오류: {e}")
            return {"error": "상세 양적 분석 중 오류가 발생했습니다"}

    def _generate_detailed_qualitative_analysis(
        self, analysis_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """상세 질적 분석"""
        try:
            qualitative = analysis_data.get("qualitative_evolution", {})

            return {
                "autonomy_level": qualitative.get("autonomy_level", 0.0),
                "learning_efficiency": qualitative.get("learning_efficiency", 0.0),
                "problem_solving_capability": qualitative.get(
                    "problem_solving_capability", 0.0
                ),
                "evolution_capability": qualitative.get("evolution_capability", 0.0),
                "characteristics": qualitative.get("qualitative_characteristics", {}),
            }
        except Exception as e:
            logger.error(f"상세 질적 분석 오류: {e}")
            return {"error": "상세 질적 분석 중 오류가 발생했습니다"}

    def _generate_detailed_temporal_analysis(
        self, analysis_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """상세 시간적 분석"""
        try:
            temporal = analysis_data.get("temporal_evolution", {})

            return {
                "evolution_speed": temporal.get("evolution_speed", 0.0),
                "evolution_pattern": temporal.get("evolution_pattern", "unknown"),
                "evolution_stage": temporal.get("evolution_stage", "unknown"),
                "temporal_trend": temporal.get("temporal_trend", "stable"),
            }
        except Exception as e:
            logger.error(f"상세 시간적 분석 오류: {e}")
            return {"error": "상세 시간적 분석 중 오류가 발생했습니다"}

    def _generate_comparative_analysis(
        self, analysis_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """비교 분석"""
        try:
            # 이전 분석과의 비교
            if len(self.report_history) > 0:
                previous_report = self.report_history[-1]
                current_score = analysis_data.get("overall_evolution_score", 0.0)
                previous_score = getattr(previous_report, "confidence_level", 0.0)

                improvement = current_score - previous_score

                return {
                    "previous_score": previous_score,
                    "current_score": current_score,
                    "improvement": improvement,
                    "improvement_rate": (
                        (improvement / previous_score * 100)
                        if previous_score > 0
                        else 0
                    ),
                }
            else:
                return {"status": "no_previous_data"}
        except Exception as e:
            logger.error(f"비교 분석 오류: {e}")
            return {"error": "비교 분석 중 오류가 발생했습니다"}

    def _generate_short_term_prediction(
        self, analysis_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """단기 예측"""
        try:
            current_score = analysis_data.get("overall_evolution_score", 0.0)
            evolution_speed = analysis_data.get("temporal_evolution", {}).get(
                "evolution_speed", 0.0
            )

            # 단기 예측 (1-2주)
            short_term_prediction = current_score + (evolution_speed * 0.1)

            return {
                "predicted_score": max(0.0, min(1.0, short_term_prediction)),
                "timeframe": "1-2주",
                "confidence": 0.7,
            }
        except Exception as e:
            logger.error(f"단기 예측 오류: {e}")
            return {"error": "단기 예측 중 오류가 발생했습니다"}

    def _generate_medium_term_prediction(
        self, analysis_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """중기 예측"""
        try:
            current_score = analysis_data.get("overall_evolution_score", 0.0)
            evolution_speed = analysis_data.get("temporal_evolution", {}).get(
                "evolution_speed", 0.0
            )

            # 중기 예측 (1-2개월)
            medium_term_prediction = current_score + (evolution_speed * 0.3)

            return {
                "predicted_score": max(0.0, min(1.0, medium_term_prediction)),
                "timeframe": "1-2개월",
                "confidence": 0.5,
            }
        except Exception as e:
            logger.error(f"중기 예측 오류: {e}")
            return {"error": "중기 예측 중 오류가 발생했습니다"}

    def _generate_long_term_prediction(
        self, analysis_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """장기 예측"""
        try:
            current_score = analysis_data.get("overall_evolution_score", 0.0)
            evolution_speed = analysis_data.get("temporal_evolution", {}).get(
                "evolution_speed", 0.0
            )

            # 장기 예측 (3-6개월)
            long_term_prediction = current_score + (evolution_speed * 0.5)

            return {
                "predicted_score": max(0.0, min(1.0, long_term_prediction)),
                "timeframe": "3-6개월",
                "confidence": 0.3,
            }
        except Exception as e:
            logger.error(f"장기 예측 오류: {e}")
            return {"error": "장기 예측 중 오류가 발생했습니다"}

    def _calculate_prediction_confidence(self, analysis_data: Dict[str, Any]) -> float:
        """예측 신뢰도 계산"""
        try:
            # 데이터 품질과 분석 신뢰도 기반
            evolution_confidence = analysis_data.get("evolution_confidence", 0.0)
            data_quality = analysis_data.get("quantitative_evolution", {}).get(
                "confidence", 0.0
            )

            prediction_confidence = (evolution_confidence + data_quality) / 2
            return max(0.0, min(1.0, prediction_confidence))
        except Exception as e:
            logger.error(f"예측 신뢰도 계산 오류: {e}")
            return 0.5

    def _generate_error_report(self) -> Dict[str, Any]:
        """오류 보고서 생성"""
        return {
            "conclusion": "분석 중 오류가 발생했습니다",
            "quantitative_changes": {"error": "분석 오류"},
            "qualitative_characteristics": {"error": "분석 오류"},
            "evolution_evidence": ["분석 중 오류가 발생했습니다"],
            "next_evolution_plan": ["시스템 안정화"],
            "confidence_level": 0.0,
        }

    def get_report_summary(self) -> Dict[str, Any]:
        """보고서 요약 반환"""
        try:
            if not self.report_history:
                return {"status": "no_data"}

            latest = self.report_history[-1]

            return {
                "status": "success",
                "latest_report": {
                    "report_id": latest.report_id,
                    "report_type": latest.report_type,
                    "conclusion": latest.conclusion,
                    "confidence_level": latest.confidence_level,
                },
                "total_reports": len(self.report_history),
                "timestamp": datetime.now().isoformat(),
            }
        except Exception as e:
            logger.error(f"보고서 요약 생성 오류: {e}")
            return {"status": "error", "error": str(e)}


# 전역 인스턴스 생성
evolution_reporter = EvolutionReporter()
