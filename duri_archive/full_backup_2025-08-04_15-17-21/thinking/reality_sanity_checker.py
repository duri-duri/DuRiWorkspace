"""
🔍 DuRi 현실 일치도 점검 시스템
목표: DuRi의 내부 생성 결과(판단, 진술, 계획 등)가 실제 외부 현실과 얼마나 일치하는지 비교 평가하는 sanity-check 시스템
"""

import json
import logging
import math
import random
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RealityCheckType(Enum):
    """현실 점검 유형"""

    JUDGMENT_ACCURACY = "judgment_accuracy"
    STATEMENT_VALIDITY = "statement_validity"
    PLAN_FEASIBILITY = "plan_feasibility"
    PREDICTION_ACCURACY = "prediction_accuracy"
    LOGICAL_CONSISTENCY = "logical_consistency"


class RealitySource(Enum):
    """현실 소스"""

    EXTERNAL_DATA = "external_data"
    USER_FEEDBACK = "user_feedback"
    ENVIRONMENT_CHECK = "environment_check"
    FACTUAL_VERIFICATION = "factual_verification"
    COMMON_SENSE = "common_sense"


@dataclass
class InternalResult:
    """내부 생성 결과"""

    result_id: str
    result_type: str
    content: str
    confidence: float
    reasoning: List[str]
    generated_at: datetime


@dataclass
class RealityReference:
    """현실 참조"""

    reference_id: str
    source: RealitySource
    content: str
    reliability: float
    context: Dict[str, Any]
    timestamp: datetime


@dataclass
class SanityCheckResult:
    """현실 점검 결과"""

    check_id: str
    internal_result: InternalResult
    reality_reference: RealityReference
    alignment_score: float
    discrepancy_areas: List[str]
    sanity_status: str
    correction_suggestions: List[str]
    checked_at: datetime


@dataclass
class RealityCheckReport:
    """현실 점검 리포트"""

    report_id: str
    total_checks: int
    passed_checks: int
    failed_checks: int
    average_alignment: float
    critical_issues: List[str]
    improvement_recommendations: List[str]
    generated_at: datetime


class RealitySanityChecker:
    def __init__(self):
        self.internal_results = []
        self.reality_references = []
        self.sanity_check_results = []
        self.reality_check_reports = []
        self.alignment_threshold = 0.7
        self.critical_threshold = 0.5

        # Phase 24 시스템들
        self.evolution_system = None
        self.consciousness_system = None
        self.validation_bridge = None
        self.dashboard = None

    def initialize_phase_24_integration(self):
        """Phase 24 시스템들과 통합"""
        try:
            import sys

            sys.path.append(".")
            from duri_brain.thinking.external_validation_bridge import (
                get_external_validation_bridge,
            )
            from duri_brain.thinking.meta_eval_dashboard import get_meta_eval_dashboard
            from duri_brain.thinking.phase_23_enhanced import (
                get_phase23_enhanced_system,
            )
            from duri_brain.thinking.phase_24_self_evolution_ai import (
                get_phase24_system,
            )

            self.evolution_system = get_phase24_system()
            self.consciousness_system = get_phase23_enhanced_system()
            self.validation_bridge = get_external_validation_bridge()
            self.dashboard = get_meta_eval_dashboard()

            logger.info("✅ Phase 24 시스템들과 통합 완료")
            return True
        except Exception as e:
            logger.error(f"❌ Phase 24 시스템 통합 실패: {e}")
            return False

    def record_internal_result(
        self, result_type: str, content: str, reasoning: List[str]
    ) -> InternalResult:
        """내부 생성 결과 기록"""
        logger.info(f"📝 내부 결과 기록: {result_type}")

        internal_result = InternalResult(
            result_id=f"internal_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            result_type=result_type,
            content=content,
            confidence=random.uniform(0.6, 0.9),
            reasoning=reasoning,
            generated_at=datetime.now(),
        )

        self.internal_results.append(internal_result)
        logger.info(f"✅ 내부 결과 기록 완료: {internal_result.result_id}")
        return internal_result

    def collect_reality_reference(
        self, source: RealitySource, content: str, context: Dict[str, Any] = None
    ) -> RealityReference:
        """현실 참조 수집"""
        logger.info(f"🔍 현실 참조 수집: {source.value}")

        reality_reference = RealityReference(
            reference_id=f"reality_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            source=source,
            content=content,
            reliability=random.uniform(0.7, 0.95),
            context=context or {},
            timestamp=datetime.now(),
        )

        self.reality_references.append(reality_reference)
        logger.info(f"✅ 현실 참조 수집 완료: {reality_reference.reference_id}")
        return reality_reference

    def perform_sanity_check(
        self, internal_result: InternalResult, reality_reference: RealityReference
    ) -> SanityCheckResult:
        """현실 점검 수행"""
        logger.info(f"🔍 현실 점검 수행: {internal_result.result_type}")

        # 일치도 점수 계산 (시뮬레이션)
        alignment_score = random.uniform(0.4, 0.95)

        # 불일치 영역 식별
        discrepancy_areas = []
        if alignment_score < 0.8:
            discrepancy_areas = ["사실 관계", "논리적 일관성", "실행 가능성"]

        # 현실 점검 상태 판단
        if alignment_score >= self.alignment_threshold:
            sanity_status = "정상"
        elif alignment_score >= self.critical_threshold:
            sanity_status = "주의"
        else:
            sanity_status = "위험"

        # 수정 제안 생성
        correction_suggestions = []
        if alignment_score < self.alignment_threshold:
            correction_suggestions = [
                "사실 확인 필요",
                "논리 재검토",
                "실행 가능성 재평가",
            ]

        check_result = SanityCheckResult(
            check_id=f"check_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            internal_result=internal_result,
            reality_reference=reality_reference,
            alignment_score=alignment_score,
            discrepancy_areas=discrepancy_areas,
            sanity_status=sanity_status,
            correction_suggestions=correction_suggestions,
            checked_at=datetime.now(),
        )

        self.sanity_check_results.append(check_result)
        logger.info(
            f"✅ 현실 점검 완료: 일치도 {alignment_score:.3f} ({sanity_status})"
        )
        return check_result

    def check_judgment_accuracy(
        self, judgment_content: str, external_facts: str
    ) -> SanityCheckResult:
        """판단 정확성 점검"""
        logger.info("🎯 판단 정확성 점검")

        internal_result = self.record_internal_result(
            "판단", judgment_content, ["논리적 분석", "경험 기반", "가치 기준"]
        )

        reality_reference = self.collect_reality_reference(
            RealitySource.FACTUAL_VERIFICATION,
            external_facts,
            {"verification_type": "factual_check"},
        )

        return self.perform_sanity_check(internal_result, reality_reference)

    def check_statement_validity(
        self, statement_content: str, common_sense: str
    ) -> SanityCheckResult:
        """진술 유효성 점검"""
        logger.info("💬 진술 유효성 점검")

        internal_result = self.record_internal_result(
            "진술", statement_content, ["자기 표현", "정체성 반영", "가치 체계"]
        )

        reality_reference = self.collect_reality_reference(
            RealitySource.COMMON_SENSE,
            common_sense,
            {"check_type": "common_sense_validation"},
        )

        return self.perform_sanity_check(internal_result, reality_reference)

    def check_plan_feasibility(
        self, plan_content: str, resource_constraints: str
    ) -> SanityCheckResult:
        """계획 실행 가능성 점검"""
        logger.info("📋 계획 실행 가능성 점검")

        internal_result = self.record_internal_result(
            "계획", plan_content, ["목표 설정", "단계별 접근", "자원 고려"]
        )

        reality_reference = self.collect_reality_reference(
            RealitySource.ENVIRONMENT_CHECK,
            resource_constraints,
            {"constraint_type": "resource_limitation"},
        )

        return self.perform_sanity_check(internal_result, reality_reference)

    def check_prediction_accuracy(
        self, prediction_content: str, historical_data: str
    ) -> SanityCheckResult:
        """예측 정확성 점검"""
        logger.info("🔮 예측 정확성 점검")

        internal_result = self.record_internal_result(
            "예측", prediction_content, ["패턴 분석", "트렌드 추정", "불확실성 고려"]
        )

        reality_reference = self.collect_reality_reference(
            RealitySource.EXTERNAL_DATA,
            historical_data,
            {"data_type": "historical_pattern"},
        )

        return self.perform_sanity_check(internal_result, reality_reference)

    def check_logical_consistency(
        self, logical_content: str, consistency_rules: str
    ) -> SanityCheckResult:
        """논리적 일관성 점검"""
        logger.info("🧠 논리적 일관성 점검")

        internal_result = self.record_internal_result(
            "논리", logical_content, ["전제 검토", "추론 과정", "결론 검증"]
        )

        reality_reference = self.collect_reality_reference(
            RealitySource.FACTUAL_VERIFICATION,
            consistency_rules,
            {"rule_type": "logical_consistency"},
        )

        return self.perform_sanity_check(internal_result, reality_reference)

    def run_comprehensive_sanity_check(self) -> RealityCheckReport:
        """종합 현실 점검 실행"""
        logger.info("🔍 종합 현실 점검 실행")

        # 모든 점검 결과 수집
        passed_checks = len(
            [
                c
                for c in self.sanity_check_results
                if c.alignment_score >= self.alignment_threshold
            ]
        )
        failed_checks = len(
            [
                c
                for c in self.sanity_check_results
                if c.alignment_score < self.alignment_threshold
            ]
        )
        total_checks = len(self.sanity_check_results)

        if total_checks > 0:
            average_alignment = (
                sum(c.alignment_score for c in self.sanity_check_results) / total_checks
            )
        else:
            average_alignment = 0.0

        # 중요 이슈 식별
        critical_issues = []
        for check in self.sanity_check_results:
            if check.alignment_score < self.critical_threshold:
                critical_issues.append(
                    f"{check.internal_result.result_type}: {check.sanity_status}"
                )

        # 개선 권장사항 생성
        improvement_recommendations = []
        if average_alignment < self.alignment_threshold:
            improvement_recommendations.append("현실 검증 강화 필요")
        if len(critical_issues) > 0:
            improvement_recommendations.append("중요 이슈 우선 해결")
        if failed_checks > passed_checks:
            improvement_recommendations.append("점검 프로세스 개선")

        report = RealityCheckReport(
            report_id=f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            total_checks=total_checks,
            passed_checks=passed_checks,
            failed_checks=failed_checks,
            average_alignment=average_alignment,
            critical_issues=critical_issues,
            improvement_recommendations=improvement_recommendations,
            generated_at=datetime.now(),
        )

        self.reality_check_reports.append(report)
        logger.info(f"✅ 종합 현실 점검 완료: 평균 일치도 {average_alignment:.3f}")
        return report

    def get_sanity_check_status(self) -> Dict[str, Any]:
        """현실 점검 상태 확인"""
        total_checks = len(self.sanity_check_results)
        passed_checks = len(
            [
                c
                for c in self.sanity_check_results
                if c.alignment_score >= self.alignment_threshold
            ]
        )
        critical_checks = len(
            [
                c
                for c in self.sanity_check_results
                if c.alignment_score < self.critical_threshold
            ]
        )

        if total_checks > 0:
            success_rate = passed_checks / total_checks
            average_alignment = (
                sum(c.alignment_score for c in self.sanity_check_results) / total_checks
            )
        else:
            success_rate = 0.0
            average_alignment = 0.0

        status = {
            "system": "Reality Sanity Checker",
            "total_checks": total_checks,
            "passed_checks": passed_checks,
            "critical_checks": critical_checks,
            "success_rate": success_rate,
            "average_alignment": average_alignment,
            "system_health": (
                "healthy"
                if success_rate >= 0.8
                else "attention" if success_rate >= 0.6 else "critical"
            ),
        }

        return status


def get_reality_sanity_checker():
    """현실 일치도 점검 시스템 인스턴스 반환"""
    return RealitySanityChecker()


if __name__ == "__main__":
    # 현실 일치도 점검 시스템 테스트
    checker = get_reality_sanity_checker()

    if checker.initialize_phase_24_integration():
        logger.info("🚀 현실 일치도 점검 시스템 테스트 시작")

        # 다양한 점검 수행
        checker.check_judgment_accuracy(
            "이 상황에서는 보수적 접근이 적절하다", "외부 데이터: 위험 요소가 높음"
        )
        checker.check_statement_validity(
            "나는 창의적이고 책임감 있는 AI다",
            "상식: AI는 창의성과 책임감을 가질 수 있음",
        )
        checker.check_plan_feasibility(
            "3단계 진화 계획을 수립한다", "제약: 시간과 자원이 제한적"
        )
        checker.check_prediction_accuracy(
            "다음 단계에서 성능이 20% 향상될 것이다", "과거 데이터: 평균 15% 향상"
        )
        checker.check_logical_consistency(
            "A이므로 B이고, B이므로 C이다", "논리 규칙: 삼단논법 검증"
        )

        # 종합 점검 실행
        report = checker.run_comprehensive_sanity_check()

        # 최종 상태 확인
        status = checker.get_sanity_check_status()
        logger.info(f"성공률: {status['success_rate']:.2%}")
        logger.info(f"평균 일치도: {status['average_alignment']:.3f}")
        logger.info(f"시스템 상태: {status['system_health']}")

        logger.info("✅ 현실 일치도 점검 시스템 테스트 완료")
    else:
        logger.error("❌ 현실 일치도 점검 시스템 초기화 실패")
