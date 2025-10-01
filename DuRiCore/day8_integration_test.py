#!/usr/bin/env python3
"""
DuRi Phase 1-3 Week 3 Day 8 통합 테스트
Day 8에서 구현된 모든 시스템을 통합하고 테스트하는 스크립트

구현된 시스템:
1. 고급 시스템 상호작용 시스템 (advanced_system_interaction.py)
2. 실시간 학습 및 적응 시스템 (adaptive_learning_system.py)
3. 사용자 인터페이스 시스템 (user_interface_system.py)
4. 성능 모니터링 시스템 (performance_monitoring_system.py)
"""

import asyncio
from datetime import datetime
import json
import logging
import time
from typing import Any, Dict, List

from adaptive_learning_system import (
    AdaptationType,
    AdaptiveLearningSystem,
    LearningType,
)

# Day 8 시스템들 import
from advanced_system_interaction import (
    AdvancedSystemInteraction,
    InteractionType,
    WorkflowStatus,
)
from performance_monitoring_system import (
    AlertLevel,
    MetricType,
    PerformanceMonitoringSystem,
)
from user_interface_system import (
    InputType,
    InterfaceMode,
    OutputType,
    UserInterfaceSystem,
)

# 로깅 설정
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class Day8IntegrationTest:
    """Day 8 통합 테스트 클래스"""

    def __init__(self):
        """초기화"""
        self.advanced_interaction = AdvancedSystemInteraction()
        self.adaptive_learning = AdaptiveLearningSystem()
        self.user_interface = UserInterfaceSystem()
        self.performance_monitoring = PerformanceMonitoringSystem()

        # 테스트 결과
        self.test_results = {
            "advanced_interaction": {},
            "adaptive_learning": {},
            "user_interface": {},
            "performance_monitoring": {},
            "integration": {},
        }

        logger.info("Day 8 통합 테스트 초기화 완료")

    async def run_all_tests(self):
        """모든 테스트 실행"""
        print("=== DuRi Phase 1-3 Week 3 Day 8 통합 테스트 시작 ===")

        # 1. 고급 시스템 상호작용 테스트
        print("\n1. 고급 시스템 상호작용 테스트")
        await self.test_advanced_system_interaction()

        # 2. 실시간 학습 및 적응 테스트
        print("\n2. 실시간 학습 및 적응 테스트")
        await self.test_adaptive_learning_system()

        # 3. 사용자 인터페이스 테스트
        print("\n3. 사용자 인터페이스 테스트")
        await self.test_user_interface_system()

        # 4. 성능 모니터링 테스트
        print("\n4. 성능 모니터링 테스트")
        await self.test_performance_monitoring_system()

        # 5. 시스템 통합 테스트
        print("\n5. 시스템 통합 테스트")
        await self.test_system_integration()

        # 6. 최종 결과 출력
        print("\n6. 최종 결과 출력")
        await self.print_final_results()

        print("\n=== Day 8 통합 테스트 완료 ===")

        return self.test_results

    async def test_advanced_system_interaction(self):
        """고급 시스템 상호작용 테스트"""
        try:
            # 가상 시스템 등록
            class MockSystem:
                def __init__(self, name: str):
                    self.name = name
                    self.data = {}

                async def get_data(self, key: str):
                    return {"system": self.name, "key": key, "value": f"data_{key}"}

                async def receive_data(self, data):
                    self.data[datetime.now().isoformat()] = data
                    return {"system": self.name, "received": True}

                async def process_data(self):
                    return {"system": self.name, "processed": len(self.data)}

            # 시스템 등록
            systems = ["lida_attention", "realtime_learning", "dynamic_reasoning"]
            for system_name in systems:
                mock_system = MockSystem(system_name)
                await self.advanced_interaction.register_system(
                    system_name, mock_system
                )

            # 데이터 공유 상호작용 테스트
            data_share_id = await self.advanced_interaction.create_interaction(
                InteractionType.DATA_SHARE,
                "lida_attention",
                "realtime_learning",
                {"data_key": "attention_data"},
            )

            data_share_result = await self.advanced_interaction.execute_interaction(
                data_share_id
            )

            # 워크플로우 테스트
            workflow_steps = [
                {
                    "name": "데이터 수집",
                    "system": "lida_attention",
                    "action": "get_data",
                    "parameters": {"key": "test"},
                },
                {
                    "name": "데이터 처리",
                    "system": "realtime_learning",
                    "action": "process_data",
                    "parameters": {},
                },
                {
                    "name": "결과 분석",
                    "system": "dynamic_reasoning",
                    "action": "process_data",
                    "parameters": {},
                },
            ]

            workflow_id = await self.advanced_interaction.create_workflow(
                "테스트 워크플로우", workflow_steps
            )
            workflow_result = await self.advanced_interaction.execute_workflow(
                workflow_id
            )

            # 메트릭 확인
            interaction_metrics = self.advanced_interaction.get_interaction_metrics()
            workflow_metrics = self.advanced_interaction.get_workflow_metrics()
            system_status = self.advanced_interaction.get_system_status()

            self.test_results["advanced_interaction"] = {
                "success": True,
                "data_share_result": data_share_result,
                "workflow_result": workflow_result,
                "interaction_metrics": interaction_metrics,
                "workflow_metrics": workflow_metrics,
                "system_status": system_status,
            }

            print(f"✅ 고급 시스템 상호작용 테스트 성공")

        except Exception as e:
            logger.error(f"고급 시스템 상호작용 테스트 실패: {e}")
            self.test_results["advanced_interaction"] = {
                "success": False,
                "error": str(e),
            }

    async def test_adaptive_learning_system(self):
        """실시간 학습 및 적응 테스트"""
        try:
            # 가상 시스템 등록
            class MockSystem:
                def __init__(self, name: str):
                    self.name = name
                    self.parameters = {}

                async def adapt(self, changes: Dict[str, Any]):
                    self.parameters.update(changes)
                    return {"system": self.name, "adapted": True}

            # 시스템 등록
            systems = ["lida_attention", "realtime_learning", "dynamic_reasoning"]
            for system_name in systems:
                mock_system = MockSystem(system_name)
                await self.adaptive_learning.register_system(system_name, mock_system)

            # 학습 데이터 수집 테스트
            data_ids = []
            for i in range(5):
                data_id = await self.adaptive_learning.collect_learning_data(
                    "training_data",
                    {"input": f"data_{i}", "output": f"result_{i}"},
                    "test_source",
                    quality_score=0.8,
                )
                data_ids.append(data_id)

            # 학습 모델 생성 및 학습 테스트
            model_id = await self.adaptive_learning.create_learning_model(
                "neural_network", {"layers": [64, 32, 16], "learning_rate": 0.01}
            )

            result_id = await self.adaptive_learning.train_model(
                model_id, LearningType.SUPERVISED, data_ids
            )

            # 학습 성과 평가 테스트
            performance_metrics = (
                await self.adaptive_learning.evaluate_learning_performance(model_id)
            )

            # 시스템 적응 테스트
            adaptation_id = await self.adaptive_learning.adapt_system(
                "lida_attention",
                AdaptationType.INCREMENTAL,
                {"learning_rate": 0.02, "batch_size": 64},
            )

            # 학습 권장사항 테스트
            recommendations = await self.adaptive_learning.get_learning_recommendations(
                "lida_attention"
            )

            # 메트릭 확인
            learning_metrics = self.adaptive_learning.get_learning_metrics()
            system_status = self.adaptive_learning.get_system_status()

            self.test_results["adaptive_learning"] = {
                "success": True,
                "performance_metrics": performance_metrics,
                "recommendations": recommendations,
                "learning_metrics": learning_metrics,
                "system_status": system_status,
            }

            print(f"✅ 실시간 학습 및 적응 테스트 성공")

        except Exception as e:
            logger.error(f"실시간 학습 및 적응 테스트 실패: {e}")
            self.test_results["adaptive_learning"] = {"success": False, "error": str(e)}

    async def test_user_interface_system(self):
        """사용자 인터페이스 테스트"""
        try:
            # 가상 시스템 등록
            class MockSystem:
                def __init__(self, name: str):
                    self.name = name

                def get_system_status(self):
                    return {"system": self.name, "status": "active"}

            # 시스템 등록
            systems = ["lida_attention", "realtime_learning", "dynamic_reasoning"]
            for system_name in systems:
                mock_system = MockSystem(system_name)
                await self.user_interface.register_system(system_name, mock_system)

            # 인터페이스 세션 생성 테스트
            session_id = await self.user_interface.create_interface_session(
                "user_001", InterfaceMode.CONSOLE
            )

            # 사용자 입력 처리 테스트
            input_id = await self.user_interface.process_user_input(
                InputType.TEXT, "시스템 상태 확인", "user_001", session_id
            )

            # 시스템 출력 생성 테스트
            output_id = await self.user_interface.generate_system_output(
                OutputType.TEXT,
                "시스템이 정상적으로 작동 중입니다.",
                "user_001",
                session_id,
            )

            # 시스템 상태 표시 테스트
            system_status = await self.user_interface.display_system_status(session_id)

            # 결과 시각화 테스트
            test_data = [{"x": 1, "y": 10}, {"x": 2, "y": 20}, {"x": 3, "y": 30}]
            visualization = await self.user_interface.visualize_results(
                test_data, "chart"
            )

            # 사용자 상호작용 처리 테스트
            interaction_result = await self.user_interface.handle_user_interaction(
                "command", {"command": "status"}, session_id
            )

            # 사용자 피드백 수집 테스트
            feedback_id = await self.user_interface.collect_user_feedback(
                "user_001", session_id, 4.5, "매우 만족스러운 인터페이스입니다."
            )

            # 메트릭 확인
            interface_metrics = self.user_interface.get_interface_metrics()
            system_status_ui = self.user_interface.get_system_status()

            self.test_results["user_interface"] = {
                "success": True,
                "system_status": system_status,
                "visualization": visualization,
                "interaction_result": interaction_result,
                "interface_metrics": interface_metrics,
                "system_status_ui": system_status_ui,
            }

            print(f"✅ 사용자 인터페이스 테스트 성공")

        except Exception as e:
            logger.error(f"사용자 인터페이스 테스트 실패: {e}")
            self.test_results["user_interface"] = {"success": False, "error": str(e)}

    async def test_performance_monitoring_system(self):
        """성능 모니터링 테스트"""
        try:
            # 가상 시스템 등록
            class MockSystem:
                def __init__(self, name: str):
                    self.name = name

                def get_system_status(self):
                    return {"system": self.name, "status": "active"}

            # 시스템 등록
            systems = ["lida_attention", "realtime_learning", "dynamic_reasoning"]
            for system_name in systems:
                mock_system = MockSystem(system_name)
                await self.performance_monitoring.register_system(
                    system_name, mock_system
                )

            # 성능 메트릭 수집 테스트
            metric_ids = []
            for i in range(5):
                metric_id = (
                    await self.performance_monitoring.collect_performance_metric(
                        MetricType.PERFORMANCE,
                        "cpu_usage",
                        75.0 + i * 2,
                        "%",
                        "test_system",
                    )
                )
                metric_ids.append(metric_id)

            # 성능 알림 생성 테스트
            alert_id = await self.performance_monitoring.generate_performance_alert(
                AlertLevel.WARNING, "CPU 사용률이 높습니다.", "cpu_usage", 80.0, 85.0
            )

            # 최적화 제안 생성 테스트
            suggestion_id = (
                await self.performance_monitoring.generate_optimization_suggestion(
                    "cpu",
                    "CPU 최적화",
                    "CPU 사용률을 줄이기 위해 불필요한 프로세스를 종료하세요.",
                    15.0,
                    "high",
                )
            )

            # 성능 트렌드 분석 테스트
            trend_analysis = (
                await self.performance_monitoring.analyze_performance_trends(
                    "cpu_usage"
                )
            )

            # 성능 보고서 생성 테스트
            report_id = await self.performance_monitoring.generate_performance_report(
                "comprehensive"
            )

            # 시스템 건강 점수 계산 테스트
            health_score = await self.performance_monitoring.get_system_health_score()

            # 성능 권장사항 생성 테스트
            recommendations = (
                await self.performance_monitoring.get_performance_recommendations()
            )

            # 메트릭 확인
            monitoring_metrics = self.performance_monitoring.get_monitoring_metrics()
            system_status = self.performance_monitoring.get_system_status()

            self.test_results["performance_monitoring"] = {
                "success": True,
                "trend_analysis": trend_analysis,
                "health_score": health_score,
                "recommendations": recommendations,
                "monitoring_metrics": monitoring_metrics,
                "system_status": system_status,
            }

            print(f"✅ 성능 모니터링 테스트 성공")

        except Exception as e:
            logger.error(f"성능 모니터링 테스트 실패: {e}")
            self.test_results["performance_monitoring"] = {
                "success": False,
                "error": str(e),
            }

    async def test_system_integration(self):
        """시스템 통합 테스트"""
        try:
            # 모든 시스템을 서로 연결
            systems = {
                "advanced_interaction": self.advanced_interaction,
                "adaptive_learning": self.adaptive_learning,
                "user_interface": self.user_interface,
                "performance_monitoring": self.performance_monitoring,
            }

            # 시스템 간 상호작용 테스트
            integration_results = {}

            # 1. 고급 상호작용과 적응적 학습 연결
            if self.test_results["advanced_interaction"].get(
                "success", False
            ) and self.test_results["adaptive_learning"].get("success", False):

                # 학습 데이터를 상호작용 시스템에 전달
                learning_data = {
                    "type": "integration_test",
                    "content": "통합 테스트 데이터",
                }
                interaction_id = await self.advanced_interaction.create_interaction(
                    InteractionType.DATA_SHARE,
                    "adaptive_learning",
                    "advanced_interaction",
                    learning_data,
                )

                integration_results["learning_interaction"] = interaction_id

            # 2. 사용자 인터페이스와 성능 모니터링 연결
            if self.test_results["user_interface"].get(
                "success", False
            ) and self.test_results["performance_monitoring"].get("success", False):

                # 성능 메트릭을 사용자 인터페이스에 표시
                performance_status = (
                    await self.performance_monitoring.get_system_health_score()
                )
                ui_output = await self.user_interface.generate_system_output(
                    OutputType.TEXT,
                    f"시스템 건강 점수: {performance_status:.1f}%",
                    "user_001",
                )

                integration_results["performance_ui"] = ui_output

            # 3. 전체 시스템 통합 상태 확인
            total_systems = 4
            successful_systems = sum(
                1
                for result in self.test_results.values()
                if result.get("success", False)
            )
            integration_score = (successful_systems / total_systems) * 100

            self.test_results["integration"] = {
                "success": integration_score >= 75,
                "integration_score": integration_score,
                "successful_systems": successful_systems,
                "total_systems": total_systems,
                "integration_results": integration_results,
            }

            print(f"✅ 시스템 통합 테스트 성공 (통합 점수: {integration_score:.1f}%)")

        except Exception as e:
            logger.error(f"시스템 통합 테스트 실패: {e}")
            self.test_results["integration"] = {"success": False, "error": str(e)}

    async def print_final_results(self):
        """최종 결과 출력"""
        print("\n" + "=" * 60)
        print("🎯 Day 8 통합 테스트 최종 결과")
        print("=" * 60)

        # 각 시스템별 결과
        for system_name, result in self.test_results.items():
            if system_name == "integration":
                continue

            status = "✅ 성공" if result.get("success", False) else "❌ 실패"
            print(f"\n📊 {system_name.replace('_', ' ').title()}: {status}")

            if result.get("success", False):
                if system_name == "advanced_interaction":
                    metrics = result.get("interaction_metrics", {})
                    print(f"   - 상호작용 수: {metrics.get('total_interactions', 0)}")
                    print(
                        f"   - 성공률: {metrics.get('successful_interactions', 0)}/{metrics.get('total_interactions', 1)}"
                    )

                elif system_name == "adaptive_learning":
                    metrics = result.get("learning_metrics", {})
                    print(
                        f"   - 학습 세션: {metrics.get('total_learning_sessions', 0)}"
                    )
                    print(f"   - 적응 수: {metrics.get('total_adaptations', 0)}")

                elif system_name == "user_interface":
                    metrics = result.get("interface_metrics", {})
                    print(f"   - 입력 수: {metrics.get('total_inputs', 0)}")
                    print(f"   - 출력 수: {metrics.get('total_outputs', 0)}")
                    print(
                        f"   - 사용자 만족도: {metrics.get('user_satisfaction', 0):.1f}"
                    )

                elif system_name == "performance_monitoring":
                    metrics = result.get("monitoring_metrics", {})
                    print(
                        f"   - 메트릭 수: {metrics.get('total_metrics_collected', 0)}"
                    )
                    print(f"   - 알림 수: {metrics.get('total_alerts_generated', 0)}")
                    print(
                        f"   - 시스템 건강 점수: {metrics.get('system_health_score', 0):.1f}%"
                    )
            else:
                print(f"   - 오류: {result.get('error', '알 수 없는 오류')}")

        # 통합 결과
        integration_result = self.test_results["integration"]
        if integration_result.get("success", False):
            print(f"\n🎉 시스템 통합: ✅ 성공")
            print(
                f"   - 통합 점수: {integration_result.get('integration_score', 0):.1f}%"
            )
            print(
                f"   - 성공한 시스템: {integration_result.get('successful_systems', 0)}/{integration_result.get('total_systems', 0)}"
            )
        else:
            print(f"\n❌ 시스템 통합: 실패")
            print(f"   - 오류: {integration_result.get('error', '알 수 없는 오류')}")

        print("\n" + "=" * 60)

        # Day 8 목표 달성도 평가
        await self.evaluate_day8_objectives()

    async def evaluate_day8_objectives(self):
        """Day 8 목표 달성도 평가"""
        print("\n🎯 Day 8 목표 달성도 평가")
        print("-" * 40)

        objectives = {
            "시스템 간 고급 상호작용": self.test_results["advanced_interaction"].get(
                "success", False
            ),
            "실시간 학습 및 적응": self.test_results["adaptive_learning"].get(
                "success", False
            ),
            "사용자 인터페이스": self.test_results["user_interface"].get(
                "success", False
            ),
            "성능 모니터링": self.test_results["performance_monitoring"].get(
                "success", False
            ),
            "시스템 통합": self.test_results["integration"].get("success", False),
        }

        achieved_objectives = sum(objectives.values())
        total_objectives = len(objectives)
        achievement_rate = (achieved_objectives / total_objectives) * 100

        for objective, achieved in objectives.items():
            status = "✅ 달성" if achieved else "❌ 미달성"
            print(f"   {objective}: {status}")

        print(
            f"\n📈 전체 달성도: {achievement_rate:.1f}% ({achieved_objectives}/{total_objectives})"
        )

        if achievement_rate >= 80:
            print("🎉 Day 8 목표를 성공적으로 달성했습니다!")
        elif achievement_rate >= 60:
            print("⚠️ Day 8 목표를 부분적으로 달성했습니다. 추가 개선이 필요합니다.")
        else:
            print("❌ Day 8 목표 달성에 실패했습니다. 재검토가 필요합니다.")


async def main():
    """메인 함수"""
    test_runner = Day8IntegrationTest()
    results = await test_runner.run_all_tests()
    return results


if __name__ == "__main__":
    asyncio.run(main())
