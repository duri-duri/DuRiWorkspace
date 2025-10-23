"""
DuRi 자가학습 루프 중복 확인 및 상태 점검 시스템

기존 학습 루프가 존재하는지 확인하고, 중복 생성을 방지합니다.
"""

import asyncio
import json
import logging
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


@dataclass
class LearningLoopStatus:
    """학습 루프 상태"""

    exists: bool
    location: str
    type: str
    status: str
    functions: List[str]
    is_active: bool
    last_updated: Optional[datetime] = None


@dataclass
class DuplicationCheckResult:
    """중복 확인 결과"""

    has_duplicates: bool
    existing_loops: List[LearningLoopStatus]
    duplicate_functions: List[str]
    recommendations: List[str]


class DuRiLearningLoopChecker:
    """DuRi 학습 루프 중복 확인 및 상태 점검"""

    def __init__(self):
        """DuRiLearningLoopChecker 초기화"""
        self.existing_loops = []
        self.duplicate_functions = []
        self.recommendations = []

        logger.info("DuRi 학습 루프 확인 시스템 초기화 완료")

    def check_existing_learning_loops(self) -> List[LearningLoopStatus]:
        """기존 학습 루프 확인"""
        logger.info("🔍 === 기존 학습 루프 확인 ===")

        loops = []

        # 1. 메인 학습 루프 관리자 확인
        try:
            from duri_brain.learning.learning_loop_manager import \
                get_learning_loop_manager

            learning_loop_manager = get_learning_loop_manager()

            if learning_loop_manager:
                status = learning_loop_manager.get_current_status()
                loops.append(
                    LearningLoopStatus(
                        exists=True,
                        location="duri_brain/learning/learning_loop_manager.py",
                        type="LearningLoopManager",
                        status="활성" if status.get("is_running", False) else "비활성",
                        functions=[
                            "start_learning_loop",
                            "stop_learning_loop",
                            "_run_learning_loop",
                            "_execute_learning_cycle",
                            "_execute_imitation_stage",
                            "_execute_practice_stage",
                            "_execute_feedback_stage",
                            "_execute_challenge_stage",
                            "_execute_improvement_stage",
                        ],
                        is_active=status.get("is_running", False),
                        last_updated=datetime.now(),
                    )
                )
                logger.info("✅ 메인 학습 루프 관리자 발견")
            else:
                logger.warning("❌ 메인 학습 루프 관리자를 찾을 수 없습니다.")
        except Exception as e:
            logger.error(f"❌ 메인 학습 루프 확인 중 오류: {e}")

        # 2. 향상된 준 가족 학습 시스템 확인
        try:
            from duri_brain.app.services.enhanced_pre_family_learning_system import \
                EnhancedPreFamilyLearningSystem

            enhanced_system = EnhancedPreFamilyLearningSystem()

            loops.append(
                LearningLoopStatus(
                    exists=True,
                    location="duri_brain/app/services/enhanced_pre_family_learning_system.py",
                    type="EnhancedPreFamilyLearningSystem",
                    status="준비됨",
                    functions=[
                        "start_autonomous_learning_loop",
                        "_generate_autonomous_question",
                        "_get_response_from_pre_family",
                        "_evaluate_response",
                        "_check_identity_protection",
                        "_accept_and_learn",
                        "_reject_and_improve",
                    ],
                    is_active=False,
                    last_updated=datetime.now(),
                )
            )
            logger.info("✅ 향상된 준 가족 학습 시스템 발견")
        except Exception as e:
            logger.error(f"❌ 향상된 준 가족 학습 시스템 확인 중 오류: {e}")

        # 3. 자율 학습 컨트롤러 확인
        try:
            from duri_brain.app.services.autonomous_learning_controller import \
                AutonomousLearningController

            autonomous_controller = AutonomousLearningController()

            loops.append(
                LearningLoopStatus(
                    exists=True,
                    location="duri_brain/app/services/autonomous_learning_controller.py",
                    type="AutonomousLearningController",
                    status="준비됨",
                    functions=[
                        "start_autonomous_learning",
                        "select_learning_topic",
                        "choose_optimal_participants",
                        "monitor_learning_session",
                    ],
                    is_active=False,
                    last_updated=datetime.now(),
                )
            )
            logger.info("✅ 자율 학습 컨트롤러 발견")
        except Exception as e:
            logger.error(f"❌ 자율 학습 컨트롤러 확인 중 오류: {e}")

        # 4. 외부 학습 트리거 테스트 시스템 확인
        try:
            from cursor_core.test_external_learning_trigger import \
                DuRiLearningTestSystem

            test_system = DuRiLearningTestSystem()

            loops.append(
                LearningLoopStatus(
                    exists=True,
                    location="cursor_core/test_external_learning_trigger.py",
                    type="DuRiLearningTestSystem",
                    status="테스트용",
                    functions=[
                        "execute_learning_session",
                        "call_external_llm",
                        "log_external_call",
                        "generate_test_report",
                    ],
                    is_active=False,
                    last_updated=datetime.now(),
                )
            )
            logger.info("✅ 외부 학습 트리거 테스트 시스템 발견")
        except Exception as e:
            logger.error(f"❌ 외부 학습 트리거 테스트 시스템 확인 중 오류: {e}")

        # 5. 학습 진단 시스템 확인
        try:
            from cursor_core.learning_diagnostics import \
                DuRiLearningDiagnostics

            diagnostics = DuRiLearningDiagnostics()

            loops.append(
                LearningLoopStatus(
                    exists=True,
                    location="cursor_core/learning_diagnostics.py",
                    type="DuRiLearningDiagnostics",
                    status="진단용",
                    functions=[
                        "run_all_diagnostics",
                        "check_internal_learning_loop",
                        "check_external_llm_triggers",
                        "check_external_call_function",
                        "check_memory_response_storage",
                        "check_external_calls_logging",
                        "check_budget_status",
                    ],
                    is_active=False,
                    last_updated=datetime.now(),
                )
            )
            logger.info("✅ 학습 진단 시스템 발견")
        except Exception as e:
            logger.error(f"❌ 학습 진단 시스템 확인 중 오류: {e}")

        self.existing_loops = loops
        return loops

    def check_duplicate_functions(self) -> List[str]:
        """중복 함수 확인"""
        logger.info("🔍 === 중복 함수 확인 ===")

        all_functions = []
        duplicate_functions = []

        for loop in self.existing_loops:
            for func in loop.functions:
                if func in all_functions:
                    duplicate_functions.append(func)
                else:
                    all_functions.append(func)

        self.duplicate_functions = duplicate_functions

        if duplicate_functions:
            logger.warning(f"⚠️ 중복 함수 발견: {duplicate_functions}")
        else:
            logger.info("✅ 중복 함수 없음")

        return duplicate_functions

    def generate_recommendations(self) -> List[str]:
        """권장사항 생성"""
        logger.info("💡 === 권장사항 생성 ===")

        recommendations = []

        # 1. 기존 루프가 있는 경우
        if self.existing_loops:
            recommendations.append(
                "✅ 기존 학습 루프가 존재합니다. 중복 생성을 피하세요."
            )

            # 활성 루프 확인
            active_loops = [loop for loop in self.existing_loops if loop.is_active]
            if active_loops:
                recommendations.append(
                    f"🔄 현재 {len(active_loops)}개의 활성 학습 루프가 실행 중입니다."
                )
            else:
                recommendations.append(
                    "⏸️ 모든 학습 루프가 비활성 상태입니다. 필요시 활성화하세요."
                )

        # 2. 중복 함수가 있는 경우
        if self.duplicate_functions:
            recommendations.append(
                f"⚠️ 중복 함수가 발견되었습니다: {', '.join(self.duplicate_functions)}"
            )
            recommendations.append("🔧 중복 함수를 통합하거나 이름을 변경하세요.")

        # 3. 새로운 요청에 대한 권장사항
        recommendations.append("📋 새로운 학습 루프 요청 시:")
        recommendations.append("  - 기존 구조와 중복되지 않는지 확인")
        recommendations.append(
            "  - 독립된 함수로 구성 (listen/respond/evaluate/improve/store/call_external)"
        )
        recommendations.append("  - 중복 방지를 위한 상태 기록 포함")

        # 4. 상태 점검 권장사항
        recommendations.append("🔍 정기적인 상태 점검:")
        recommendations.append("  - 학습 루프 활성 상태 확인")
        recommendations.append("  - 트리거 상태 모니터링")
        recommendations.append("  - 성능 메트릭 추적")

        self.recommendations = recommendations
        return recommendations

    def check_learning_loop_structure(self) -> Dict[str, Any]:
        """학습 루프 구조 확인"""
        logger.info("🏗️ === 학습 루프 구조 확인 ===")

        structure_analysis = {
            "total_loops": len(self.existing_loops),
            "active_loops": len(
                [loop for loop in self.existing_loops if loop.is_active]
            ),
            "loop_types": [loop.type for loop in self.existing_loops],
            "total_functions": sum(len(loop.functions) for loop in self.existing_loops),
            "duplicate_functions": len(self.duplicate_functions),
            "structure_health": "양호" if not self.duplicate_functions else "주의 필요",
        }

        logger.info(f"📊 구조 분석 결과:")
        logger.info(f"  - 총 루프 수: {structure_analysis['total_loops']}")
        logger.info(f"  - 활성 루프 수: {structure_analysis['active_loops']}")
        logger.info(f"  - 총 함수 수: {structure_analysis['total_functions']}")
        logger.info(f"  - 중복 함수 수: {structure_analysis['duplicate_functions']}")
        logger.info(f"  - 구조 상태: {structure_analysis['structure_health']}")

        return structure_analysis

    def run_comprehensive_check(self) -> DuplicationCheckResult:
        """종합 점검 실행"""
        logger.info("🔍 === DuRi 학습 루프 종합 점검 시작 ===")

        # 1. 기존 루프 확인
        existing_loops = self.check_existing_learning_loops()

        # 2. 중복 함수 확인
        duplicate_functions = self.check_duplicate_functions()

        # 3. 구조 분석
        structure_analysis = self.check_learning_loop_structure()

        # 4. 권장사항 생성
        recommendations = self.generate_recommendations()

        # 5. 결과 생성
        has_duplicates = len(duplicate_functions) > 0

        result = DuplicationCheckResult(
            has_duplicates=has_duplicates,
            existing_loops=existing_loops,
            duplicate_functions=duplicate_functions,
            recommendations=recommendations,
        )

        # 6. 결과 출력
        self.print_comprehensive_results(result, structure_analysis)

        return result

    def print_comprehensive_results(
        self, result: DuplicationCheckResult, structure_analysis: Dict[str, Any]
    ):
        """종합 결과 출력"""
        logger.info("\n📊 === 종합 점검 결과 ===")

        if result.has_duplicates:
            logger.warning("⚠️ 중복이 발견되었습니다!")
        else:
            logger.info("✅ 중복 없음 - 안전합니다!")

        logger.info(f"\n📋 발견된 학습 루프 ({len(result.existing_loops)}개):")
        for i, loop in enumerate(result.existing_loops, 1):
            status_icon = "🟢" if loop.is_active else "⚪"
            logger.info(f"  {i}. {status_icon} {loop.type} ({loop.location})")
            logger.info(f"     상태: {loop.status}")
            logger.info(f"     함수: {len(loop.functions)}개")

        if result.duplicate_functions:
            logger.warning(f"\n⚠️ 중복 함수 ({len(result.duplicate_functions)}개):")
            for func in result.duplicate_functions:
                logger.warning(f"  - {func}")

        logger.info(f"\n💡 권장사항 ({len(result.recommendations)}개):")
        for rec in result.recommendations:
            logger.info(f"  {rec}")

        logger.info(f"\n🏗️ 구조 분석:")
        logger.info(f"  - 구조 상태: {structure_analysis['structure_health']}")
        logger.info(
            f"  - 활성 루프: {structure_analysis['active_loops']}/{structure_analysis['total_loops']}"
        )
        logger.info(f"  - 중복 함수: {structure_analysis['duplicate_functions']}개")


# 전역 함수로 실행 가능하도록
def check_duRi_learning_loops() -> DuplicationCheckResult:
    """DuRi 학습 루프 중복 확인 (전역 함수)"""
    checker = DuRiLearningLoopChecker()
    return checker.run_comprehensive_check()


if __name__ == "__main__":
    # 종합 점검 실행
    import sys

    sys.path.append(".")

    result = check_duRi_learning_loops()
    print(
        f"\n🎯 최종 결과: {'⚠️ 중복 발견' if result.has_duplicates else '✅ 중복 없음'}"
    )
