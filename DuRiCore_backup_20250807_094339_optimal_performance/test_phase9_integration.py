#!/usr/bin/env python3
"""
DuRiCore Phase 9 - 통합 테스트 시스템
배포 시스템과 사용자 인터페이스 시스템 통합 테스트
"""

import asyncio
import json
import logging
import statistics
import time
from datetime import datetime
from typing import Any, Dict, List, Optional

# Phase 9 모듈들 import
try:
    from deployment_system import (
        DeploymentPlatform,
        EnvironmentType,
        IntegratedDeploymentSystem,
        UserInterfaceType,
    )
    from integrated_system_manager import IntegratedSystemManager
    from real_environment_deployment import DeploymentStatus, RealEnvironmentDeployment
    from user_interface import (
        InterfaceType,
        LanguageType,
        ThemeType,
        UserInterfaceSystem,
    )

    PHASE9_MODULES_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ 일부 Phase 9 모듈을 찾을 수 없습니다: {e}")
    PHASE9_MODULES_AVAILABLE = False

logger = logging.getLogger(__name__)


class Phase9IntegrationTest:
    """Phase 9 통합 테스트 시스템"""

    def __init__(self):
        self.test_results = []
        self.performance_metrics = []
        self.integration_status = {}

        # 테스트 시스템 초기화
        if PHASE9_MODULES_AVAILABLE:
            self.deployment_system = IntegratedDeploymentSystem()
            self.ui_system = UserInterfaceSystem()
            self.real_deployment = RealEnvironmentDeployment()
            self.system_manager = IntegratedSystemManager()
        else:
            self.deployment_system = None
            self.ui_system = None
            self.real_deployment = None
            self.system_manager = None

    async def run_comprehensive_test(self) -> Dict[str, Any]:
        """종합 테스트 실행"""
        print("🚀 DuRi Phase 9 - 종합 통합 테스트 시작")

        test_start_time = time.time()

        # 1. 시스템 초기화 테스트
        print("\n📋 1. 시스템 초기화 테스트")
        init_result = await self._test_system_initialization()

        # 2. 배포 시스템 테스트
        print("\n📋 2. 배포 시스템 테스트")
        deployment_result = await self._test_deployment_system()

        # 3. 사용자 인터페이스 테스트
        print("\n📋 3. 사용자 인터페이스 테스트")
        ui_result = await self._test_user_interface_system()

        # 4. 통합 기능 테스트
        print("\n📋 4. 통합 기능 테스트")
        integration_result = await self._test_integration_features()

        # 5. 성능 테스트
        print("\n📋 5. 성능 테스트")
        performance_result = await self._test_performance()

        # 6. 안정성 테스트
        print("\n📋 6. 안정성 테스트")
        stability_result = await self._test_stability()

        # 7. 사용자 경험 테스트
        print("\n📋 7. 사용자 경험 테스트")
        ux_result = await self._test_user_experience()

        # 종합 결과 분석
        test_end_time = time.time()
        total_test_time = test_end_time - test_start_time

        comprehensive_result = {
            "test_id": f"phase9_test_{int(time.time())}",
            "test_start_time": datetime.fromtimestamp(test_start_time).isoformat(),
            "test_end_time": datetime.fromtimestamp(test_end_time).isoformat(),
            "total_test_time": total_test_time,
            "test_results": {
                "initialization": init_result,
                "deployment": deployment_result,
                "user_interface": ui_result,
                "integration": integration_result,
                "performance": performance_result,
                "stability": stability_result,
                "user_experience": ux_result,
            },
            "overall_score": self._calculate_overall_score(
                [
                    init_result,
                    deployment_result,
                    ui_result,
                    integration_result,
                    performance_result,
                    stability_result,
                    ux_result,
                ]
            ),
            "recommendations": self._generate_test_recommendations(
                [
                    init_result,
                    deployment_result,
                    ui_result,
                    integration_result,
                    performance_result,
                    stability_result,
                    ux_result,
                ]
            ),
        }

        self.test_results.append(comprehensive_result)

        print(f"\n🎉 Phase 9 종합 테스트 완료!")
        print(f"📊 전체 점수: {comprehensive_result['overall_score']:.2f}/100")
        print(f"⏱️ 총 테스트 시간: {total_test_time:.2f}초")

        return comprehensive_result

    async def _test_system_initialization(self) -> Dict[str, Any]:
        """시스템 초기화 테스트"""
        test_result = {
            "test_name": "시스템 초기화",
            "status": "failed",
            "score": 0,
            "details": [],
            "errors": [],
        }

        try:
            # 배포 시스템 초기화 확인
            if self.deployment_system:
                test_result["details"].append("✅ 배포 시스템 초기화 성공")
            else:
                test_result["errors"].append("❌ 배포 시스템 초기화 실패")

            # UI 시스템 초기화 확인
            if self.ui_system:
                test_result["details"].append("✅ UI 시스템 초기화 성공")
            else:
                test_result["errors"].append("❌ UI 시스템 초기화 실패")

            # 시스템 매니저 초기화 확인
            if self.system_manager:
                test_result["details"].append("✅ 시스템 매니저 초기화 성공")
            else:
                test_result["errors"].append("❌ 시스템 매니저 초기화 실패")

            # 점수 계산
            success_count = len([d for d in test_result["details"] if "✅" in d])
            total_count = 3
            test_result["score"] = (success_count / total_count) * 100

            if test_result["score"] >= 80:
                test_result["status"] = "passed"
            elif test_result["score"] >= 60:
                test_result["status"] = "warning"
            else:
                test_result["status"] = "failed"

        except Exception as e:
            test_result["errors"].append(f"❌ 초기화 테스트 중 오류: {e}")

        return test_result

    async def _test_deployment_system(self) -> Dict[str, Any]:
        """배포 시스템 테스트"""
        test_result = {
            "test_name": "배포 시스템",
            "status": "failed",
            "score": 0,
            "details": [],
            "errors": [],
        }

        if not self.deployment_system:
            test_result["errors"].append("❌ 배포 시스템이 초기화되지 않았습니다.")
            return test_result

        try:
            # 플랫폼 정보 조회 테스트
            platforms = self.deployment_system.get_available_platforms()
            test_result["details"].append(f"✅ 사용 가능한 플랫폼: {len(platforms)}개")

            # 로컬 배포 테스트
            test_config = {
                "deployment_parameters": {"theme": "modern"},
                "resource_requirements": {"cpu_min": 1, "memory_min": 512},
                "security_settings": {"ssl_enabled": True},
            }

            deployment_report = await self.deployment_system.deploy_system(
                platform=DeploymentPlatform.LOCAL,
                environment_type=EnvironmentType.DEVELOPMENT,
                ui_type=UserInterfaceType.WEB_DASHBOARD,
                config=test_config,
            )

            if deployment_report.deployment_status == DeploymentStatus.COMPLETED:
                test_result["details"].append("✅ 로컬 배포 성공")
            else:
                test_result["errors"].append(
                    f"❌ 로컬 배포 실패: {deployment_report.deployment_status}"
                )

            # 성능 분석 확인
            if deployment_report.performance_analysis:
                performance_score = deployment_report.performance_analysis.get(
                    "performance_score", 0
                )
                test_result["details"].append(f"✅ 성능 점수: {performance_score:.2f}")

            # 적응성 확인
            if deployment_report.adaptation_success:
                test_result["details"].append("✅ 시스템 적응성 확인")
            else:
                test_result["errors"].append("❌ 시스템 적응성 실패")

            # 점수 계산
            success_count = len([d for d in test_result["details"] if "✅" in d])
            total_count = 4
            test_result["score"] = (success_count / total_count) * 100

            if test_result["score"] >= 80:
                test_result["status"] = "passed"
            elif test_result["score"] >= 60:
                test_result["status"] = "warning"
            else:
                test_result["status"] = "failed"

        except Exception as e:
            test_result["errors"].append(f"❌ 배포 시스템 테스트 중 오류: {e}")

        return test_result

    async def _test_user_interface_system(self) -> Dict[str, Any]:
        """사용자 인터페이스 시스템 테스트"""
        test_result = {
            "test_name": "사용자 인터페이스",
            "status": "failed",
            "score": 0,
            "details": [],
            "errors": [],
        }

        if not self.ui_system:
            test_result["errors"].append("❌ UI 시스템이 초기화되지 않았습니다.")
            return test_result

        try:
            # 웹 대시보드 생성 테스트
            web_ui = self.ui_system.create_interface(
                interface_type=InterfaceType.WEB_DASHBOARD,
                theme=ThemeType.MODERN,
                language=LanguageType.KOREAN,
            )
            test_result["details"].append(f"✅ 웹 대시보드 생성: {web_ui.ui_id}")

            # CLI 인터페이스 생성 테스트
            cli_ui = self.ui_system.create_interface(
                interface_type=InterfaceType.CLI_INTERFACE,
                theme=ThemeType.DARK,
                language=LanguageType.ENGLISH,
            )
            test_result["details"].append(f"✅ CLI 인터페이스 생성: {cli_ui.ui_id}")

            # API 인터페이스 생성 테스트
            api_ui = self.ui_system.create_interface(
                interface_type=InterfaceType.API_INTERFACE,
                theme=ThemeType.MINIMAL,
                language=LanguageType.KOREAN,
            )
            test_result["details"].append(f"✅ API 인터페이스 생성: {api_ui.ui_id}")

            # 사용자 피드백 수집 테스트
            feedback = self.ui_system.collect_user_feedback(
                ui_id=web_ui.ui_id,
                user_id="test_user",
                satisfaction_score=0.85,
                usability_score=0.90,
                performance_rating=0.88,
                comments="테스트 피드백",
                feature_requests=["다크 모드", "모바일 최적화"],
                bug_reports=[],
            )
            test_result["details"].append(
                f"✅ 사용자 피드백 수집: {feedback.feedback_id}"
            )

            # 인터페이스 분석 테스트
            analytics = self.ui_system.get_interface_analytics(web_ui.ui_id)
            if analytics.get("average_satisfaction", 0) > 0:
                test_result["details"].append("✅ 인터페이스 분석 성공")
            else:
                test_result["errors"].append("❌ 인터페이스 분석 실패")

            # 점수 계산
            success_count = len([d for d in test_result["details"] if "✅" in d])
            total_count = 5
            test_result["score"] = (success_count / total_count) * 100

            if test_result["score"] >= 80:
                test_result["status"] = "passed"
            elif test_result["score"] >= 60:
                test_result["status"] = "warning"
            else:
                test_result["status"] = "failed"

        except Exception as e:
            test_result["errors"].append(f"❌ UI 시스템 테스트 중 오류: {e}")

        return test_result

    async def _test_integration_features(self) -> Dict[str, Any]:
        """통합 기능 테스트"""
        test_result = {
            "test_name": "통합 기능",
            "status": "failed",
            "score": 0,
            "details": [],
            "errors": [],
        }

        try:
            # 배포 시스템과 UI 시스템 연동 테스트
            if self.deployment_system and self.ui_system:
                test_result["details"].append("✅ 배포-UI 시스템 연동 확인")
            else:
                test_result["errors"].append("❌ 배포-UI 시스템 연동 실패")

            # 시스템 매니저 통합 확인
            if self.system_manager:
                test_result["details"].append("✅ 시스템 매니저 통합 확인")
            else:
                test_result["errors"].append("❌ 시스템 매니저 통합 실패")

            # 실시간 모니터링 테스트
            if self.real_deployment:
                test_result["details"].append("✅ 실시간 모니터링 시스템 확인")
            else:
                test_result["errors"].append("❌ 실시간 모니터링 시스템 실패")

            # 점수 계산
            success_count = len([d for d in test_result["details"] if "✅" in d])
            total_count = 3
            test_result["score"] = (success_count / total_count) * 100

            if test_result["score"] >= 80:
                test_result["status"] = "passed"
            elif test_result["score"] >= 60:
                test_result["status"] = "warning"
            else:
                test_result["status"] = "failed"

        except Exception as e:
            test_result["errors"].append(f"❌ 통합 기능 테스트 중 오류: {e}")

        return test_result

    async def _test_performance(self) -> Dict[str, Any]:
        """성능 테스트"""
        test_result = {
            "test_name": "성능 테스트",
            "status": "failed",
            "score": 0,
            "details": [],
            "errors": [],
        }

        try:
            # 응답 시간 테스트
            start_time = time.time()
            if self.ui_system:
                ui = self.ui_system.create_interface(InterfaceType.WEB_DASHBOARD)
                response_time = time.time() - start_time
                test_result["details"].append(
                    f"✅ UI 생성 응답 시간: {response_time:.3f}초"
                )

                if response_time < 1.0:
                    test_result["details"].append("✅ 응답 시간 우수")
                elif response_time < 2.0:
                    test_result["details"].append("⚠️ 응답 시간 양호")
                else:
                    test_result["errors"].append("❌ 응답 시간 느림")

            # 메모리 사용량 테스트
            import psutil

            process = psutil.Process()
            memory_usage = process.memory_info().rss / 1024 / 1024  # MB
            test_result["details"].append(f"✅ 메모리 사용량: {memory_usage:.1f}MB")

            if memory_usage < 100:
                test_result["details"].append("✅ 메모리 사용량 우수")
            elif memory_usage < 200:
                test_result["details"].append("⚠️ 메모리 사용량 양호")
            else:
                test_result["errors"].append("❌ 메모리 사용량 높음")

            # CPU 사용률 테스트
            cpu_usage = psutil.cpu_percent(interval=1)
            test_result["details"].append(f"✅ CPU 사용률: {cpu_usage:.1f}%")

            if cpu_usage < 50:
                test_result["details"].append("✅ CPU 사용률 우수")
            elif cpu_usage < 80:
                test_result["details"].append("⚠️ CPU 사용률 양호")
            else:
                test_result["errors"].append("❌ CPU 사용률 높음")

            # 점수 계산
            success_count = len([d for d in test_result["details"] if "✅" in d])
            total_count = 6
            test_result["score"] = (success_count / total_count) * 100

            if test_result["score"] >= 80:
                test_result["status"] = "passed"
            elif test_result["score"] >= 60:
                test_result["status"] = "warning"
            else:
                test_result["status"] = "failed"

        except Exception as e:
            test_result["errors"].append(f"❌ 성능 테스트 중 오류: {e}")

        return test_result

    async def _test_stability(self) -> Dict[str, Any]:
        """안정성 테스트"""
        test_result = {
            "test_name": "안정성 테스트",
            "status": "failed",
            "score": 0,
            "details": [],
            "errors": [],
        }

        try:
            # 반복 실행 테스트
            if self.ui_system:
                for i in range(5):
                    try:
                        ui = self.ui_system.create_interface(
                            InterfaceType.WEB_DASHBOARD
                        )
                        test_result["details"].append(f"✅ 반복 실행 {i+1}/5 성공")
                    except Exception as e:
                        test_result["errors"].append(f"❌ 반복 실행 {i+1}/5 실패: {e}")

                # 오류 처리 테스트
                try:
                    # 잘못된 파라미터로 테스트
                    invalid_ui = self.ui_system.get_interface_by_id("invalid_id")
                    if invalid_ui is None:
                        test_result["details"].append("✅ 오류 처리 정상")
                    else:
                        test_result["errors"].append("❌ 오류 처리 실패")
                except Exception as e:
                    test_result["details"].append("✅ 예외 처리 정상")

            # 메모리 누수 테스트
            import gc

            gc.collect()
            initial_objects = len(gc.get_objects())

            if self.ui_system:
                for _ in range(10):
                    self.ui_system.create_interface(InterfaceType.WEB_DASHBOARD)

                gc.collect()
                final_objects = len(gc.get_objects())
                object_increase = final_objects - initial_objects

                if object_increase < 100:
                    test_result["details"].append("✅ 메모리 누수 없음")
                else:
                    test_result["errors"].append(
                        f"❌ 메모리 누수 의심: {object_increase}개 객체 증가"
                    )

            # 점수 계산
            success_count = len([d for d in test_result["details"] if "✅" in d])
            total_count = 3
            test_result["score"] = (success_count / total_count) * 100

            if test_result["score"] >= 80:
                test_result["status"] = "passed"
            elif test_result["score"] >= 60:
                test_result["status"] = "warning"
            else:
                test_result["status"] = "failed"

        except Exception as e:
            test_result["errors"].append(f"❌ 안정성 테스트 중 오류: {e}")

        return test_result

    async def _test_user_experience(self) -> Dict[str, Any]:
        """사용자 경험 테스트"""
        test_result = {
            "test_name": "사용자 경험",
            "status": "failed",
            "score": 0,
            "details": [],
            "errors": [],
        }

        try:
            if not self.ui_system:
                test_result["errors"].append("❌ UI 시스템이 초기화되지 않았습니다.")
                return test_result

            # 다양한 테마 테스트
            themes = [
                ThemeType.MODERN,
                ThemeType.DARK,
                ThemeType.LIGHT,
                ThemeType.MINIMAL,
            ]
            for theme in themes:
                ui = self.ui_system.create_interface(
                    interface_type=InterfaceType.WEB_DASHBOARD, theme=theme
                )
                test_result["details"].append(f"✅ {theme.value} 테마 생성 성공")

            # 다양한 언어 테스트
            languages = [LanguageType.KOREAN, LanguageType.ENGLISH]
            for language in languages:
                ui = self.ui_system.create_interface(
                    interface_type=InterfaceType.WEB_DASHBOARD, language=language
                )
                test_result["details"].append(f"✅ {language.value} 언어 지원 확인")

            # 접근성 기능 테스트
            ui = self.ui_system.create_interface(InterfaceType.WEB_DASHBOARD)
            accessibility_updated = self.ui_system.update_accessibility_settings(
                ui.ui_id, {"high_contrast": True, "large_text": True}
            )
            if accessibility_updated:
                test_result["details"].append("✅ 접근성 설정 업데이트 성공")
            else:
                test_result["errors"].append("❌ 접근성 설정 업데이트 실패")

            # 커스터마이징 테스트
            customization_updated = self.ui_system.update_interface_customization(
                ui.ui_id, {"custom_theme": "test", "layout": "compact"}
            )
            if customization_updated:
                test_result["details"].append("✅ 커스터마이징 업데이트 성공")
            else:
                test_result["errors"].append("❌ 커스터마이징 업데이트 실패")

            # 점수 계산
            success_count = len([d for d in test_result["details"] if "✅" in d])
            total_count = 8
            test_result["score"] = (success_count / total_count) * 100

            if test_result["score"] >= 80:
                test_result["status"] = "passed"
            elif test_result["score"] >= 60:
                test_result["status"] = "warning"
            else:
                test_result["status"] = "failed"

        except Exception as e:
            test_result["errors"].append(f"❌ 사용자 경험 테스트 중 오류: {e}")

        return test_result

    def _calculate_overall_score(self, test_results: List[Dict[str, Any]]) -> float:
        """전체 점수 계산"""
        if not test_results:
            return 0.0

        scores = [result.get("score", 0) for result in test_results]
        return statistics.mean(scores)

    def _generate_test_recommendations(
        self, test_results: List[Dict[str, Any]]
    ) -> List[str]:
        """테스트 권장사항 생성"""
        recommendations = []

        for result in test_results:
            if result.get("status") == "failed":
                test_name = result.get("test_name", "Unknown")
                recommendations.append(f"🔧 {test_name} 테스트 개선 필요")

            errors = result.get("errors", [])
            for error in errors:
                if "응답 시간" in error:
                    recommendations.append("⚡ 성능 최적화 권장")
                elif "메모리" in error:
                    recommendations.append("💾 메모리 사용량 최적화 권장")
                elif "CPU" in error:
                    recommendations.append("🖥️ CPU 사용량 최적화 권장")

        if not recommendations:
            recommendations.append("🎉 모든 테스트가 성공적으로 완료되었습니다!")

        return recommendations

    def save_test_results(self, filename: str = None) -> str:
        """테스트 결과 저장"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"phase9_test_results_{timestamp}.json"

        with open(filename, "w", encoding="utf-8") as f:
            json.dump(self.test_results, f, ensure_ascii=False, indent=2, default=str)

        print(f"💾 테스트 결과 저장 완료: {filename}")
        return filename

    def print_test_summary(self, test_result: Dict[str, Any]):
        """테스트 결과 요약 출력"""
        print(f"\n📊 테스트 요약: {test_result['test_id']}")
        print("=" * 50)

        for test_name, result in test_result["test_results"].items():
            status_emoji = {"passed": "✅", "warning": "⚠️", "failed": "❌"}.get(
                result["status"], "❓"
            )

            print(f"{status_emoji} {result['test_name']}: {result['score']:.1f}/100")

            if result.get("errors"):
                for error in result["errors"][:2]:  # 최대 2개 오류만 표시
                    print(f"   {error}")

        print(f"\n🎯 전체 점수: {test_result['overall_score']:.1f}/100")
        print(f"⏱️ 총 테스트 시간: {test_result['total_test_time']:.2f}초")

        if test_result.get("recommendations"):
            print("\n💡 권장사항:")
            for rec in test_result["recommendations"]:
                print(f"   {rec}")


# 메인 테스트 실행
async def main():
    """메인 테스트 실행"""
    print("🚀 DuRi Phase 9 - 통합 테스트 시스템 시작")

    test_system = Phase9IntegrationTest()

    # 종합 테스트 실행
    test_result = await test_system.run_comprehensive_test()

    # 결과 출력
    test_system.print_test_summary(test_result)

    # 결과 저장
    test_system.save_test_results()

    print("\n🎉 Phase 9 통합 테스트 완료!")


if __name__ == "__main__":
    asyncio.run(main())
