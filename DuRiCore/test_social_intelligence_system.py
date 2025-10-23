#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DuRi 30일 진화 계획 - Day 11: 사회적 지능 시스템 테스트

Day 11에서 구현된 사회적 지능 시스템의 기능을 테스트하는 스크립트

테스트 항목:
1. 사회적 맥락 이해 테스트
2. 인간 상호작용 최적화 테스트
3. 사회적 적응 능력 테스트
4. 협력 및 협업 능력 테스트
5. 성능 테스트
6. 통합 테스트
"""

import asyncio
import json
import logging
import time
from datetime import datetime

# Day 11 시스템 import
try:
    from social_intelligence_system import (
        InteractionType,  # noqa: F401
        RelationshipType,  # noqa: F401
        SocialContext,  # noqa: F401
        SocialIntelligenceResult,  # noqa: F401
        SocialIntelligenceSystem,
        SocialInteraction,  # noqa: F401
    )
    from social_intelligence_system import SocialContext as SocialContextEnum  # noqa: F401
except ImportError as e:
    print(f"❌ Day 11 시스템 import 실패: {e}")
    exit(1)

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Day11TestRunner:
    """Day 11 테스트 러너"""

    def __init__(self):
        self.test_results = []
        self.start_time = None
        self.end_time = None

    async def run_all_tests(self):
        """모든 테스트 실행"""
        print("🧪 Day 11 사회적 지능 시스템 테스트 시작")
        print("=" * 60)

        self.start_time = time.time()

        # 테스트 실행
        await self.test_social_context_understanding()
        await self.test_human_interaction_optimization()
        await self.test_social_adaptation()
        await self.test_collaboration_effectiveness()
        await self.test_performance()
        await self.test_integration()

        self.end_time = time.time()

        # 결과 출력
        await self.print_test_results()

    async def test_social_context_understanding(self):
        """사회적 맥락 이해 테스트"""
        print("\n🔍 테스트 1: 사회적 맥락 이해")

        try:
            social_intelligence = SocialIntelligenceSystem()

            # 다양한 사회적 맥락 테스트
            test_contexts = [
                {
                    "formality": 0.8,
                    "professionalism": 0.7,
                    "participants": ["user", "duri"],
                    "interaction_type": "conversation",
                    "goals": ["information_sharing", "problem_solving"],
                },
                {
                    "formality": 0.2,
                    "personal": 0.8,
                    "participants": ["friend1", "friend2", "duri"],
                    "interaction_type": "collaboration",
                    "goals": ["social_bonding", "entertainment"],
                },
                {
                    "formality": 0.6,
                    "professionalism": 0.8,
                    "participants": ["colleague1", "colleague2", "duri"],
                    "interaction_type": "collaboration",
                    "goals": ["project_work", "decision_making"],
                },
            ]

            success_count = 0
            total_count = len(test_contexts)

            for i, context_data in enumerate(test_contexts, 1):
                print(f"  📝 맥락 {i}: {context_data.get('interaction_type', 'unknown')}")

                context = await social_intelligence.understand_social_context(context_data)

                if context and hasattr(context, "context_type"):
                    success_count += 1
                    print(f"    ✅ 성공 - 맥락 유형: {context.context_type.value}")
                else:
                    print("    ❌ 실패 - 맥락 이해 실패")

            success_rate = success_count / total_count * 100

            if success_rate >= 80:
                print(f"✅ 성공 - 사회적 맥락 이해 성공률: {success_rate:.1f}%")
                self.test_results.append(
                    {
                        "test_name": "사회적 맥락 이해",
                        "status": "성공",
                        "message": f"사회적 맥락 이해 성공률: {success_rate:.1f}%",
                    }
                )
            else:
                print(f"⚠️ 부분 성공 - 사회적 맥락 이해 성공률: {success_rate:.1f}%")
                self.test_results.append(
                    {
                        "test_name": "사회적 맥락 이해",
                        "status": "부분 성공",
                        "message": f"사회적 맥락 이해 성공률: {success_rate:.1f}%",
                    }
                )

        except Exception as e:
            print(f"❌ 오류 - 사회적 맥락 이해 테스트 중 오류 발생: {e}")
            self.test_results.append(
                {
                    "test_name": "사회적 맥락 이해",
                    "status": "오류",
                    "message": f"사회적 맥락 이해 테스트 중 오류 발생: {e}",
                }
            )

    async def test_human_interaction_optimization(self):
        """인간 상호작용 최적화 테스트"""
        print("\n🤝 테스트 2: 인간 상호작용 최적화")

        try:
            social_intelligence = SocialIntelligenceSystem()

            # 테스트 맥락 생성
            context = await social_intelligence.understand_social_context(
                {
                    "formality": 0.5,
                    "participants": ["user", "duri"],
                    "interaction_type": "conversation",
                }
            )

            # 상호작용 최적화 테스트
            interaction_data = {
                "message": "안녕하세요! 오늘 날씨가 정말 좋네요.",
                "emotion": "positive",
                "urgency": "low",
            }

            optimization_result = await social_intelligence.optimize_human_interaction(context, interaction_data)

            if optimization_result and "communication_style" in optimization_result:
                print("✅ 성공 - 인간 상호작용 최적화 완료")
                print(f"  📊 의사소통 스타일: {optimization_result['communication_style']}")
                print(f"  💭 감정적 반응: {optimization_result.get('emotional_response', {})}")
                self.test_results.append(
                    {
                        "test_name": "인간 상호작용 최적화",
                        "status": "성공",
                        "message": "인간 상호작용 최적화가 성공적으로 완료되었습니다",
                    }
                )
            else:
                print("❌ 실패 - 인간 상호작용 최적화 실패")
                self.test_results.append(
                    {
                        "test_name": "인간 상호작용 최적화",
                        "status": "실패",
                        "message": "인간 상호작용 최적화에 실패했습니다",
                    }
                )

        except Exception as e:
            print(f"❌ 오류 - 인간 상호작용 최적화 테스트 중 오류 발생: {e}")
            self.test_results.append(
                {
                    "test_name": "인간 상호작용 최적화",
                    "status": "오류",
                    "message": f"인간 상호작용 최적화 테스트 중 오류 발생: {e}",
                }
            )

    async def test_social_adaptation(self):
        """사회적 적응 능력 테스트"""
        print("\n🔄 테스트 3: 사회적 적응 능력")

        try:
            social_intelligence = SocialIntelligenceSystem()

            # 테스트 맥락 생성
            context = await social_intelligence.understand_social_context(
                {
                    "formality": 0.3,
                    "personal": 0.7,
                    "participants": ["friend", "duri"],
                    "interaction_type": "conversation",
                }
            )

            # 사회적 상황 적응 테스트
            situation_data = {
                "situation": "casual_conversation",
                "mood": "relaxed",
                "topic": "hobbies",
            }

            adaptation_result = await social_intelligence.adapt_to_social_situation(context, situation_data)

            if adaptation_result and "adaptation_strategy" in adaptation_result:
                print("✅ 성공 - 사회적 적응 능력 확인")
                print(f"  📊 적응 전략: {adaptation_result['adaptation_strategy']}")
                print(f"  🎯 행동 조정: {adaptation_result.get('behavior_adjustment', {})}")
                self.test_results.append(
                    {
                        "test_name": "사회적 적응 능력",
                        "status": "성공",
                        "message": "사회적 적응 능력이 정상적으로 작동합니다",
                    }
                )
            else:
                print("❌ 실패 - 사회적 적응 능력 확인 실패")
                self.test_results.append(
                    {
                        "test_name": "사회적 적응 능력",
                        "status": "실패",
                        "message": "사회적 적응 능력 확인에 실패했습니다",
                    }
                )

        except Exception as e:
            print(f"❌ 오류 - 사회적 적응 능력 테스트 중 오류 발생: {e}")
            self.test_results.append(
                {
                    "test_name": "사회적 적응 능력",
                    "status": "오류",
                    "message": f"사회적 적응 능력 테스트 중 오류 발생: {e}",
                }
            )

    async def test_collaboration_effectiveness(self):
        """협력 및 협업 능력 테스트"""
        print("\n👥 테스트 4: 협력 및 협업 능력")

        try:
            social_intelligence = SocialIntelligenceSystem()

            # 테스트 맥락 생성
            context = await social_intelligence.understand_social_context(
                {
                    "formality": 0.6,
                    "professionalism": 0.7,
                    "participants": ["colleague1", "colleague2", "duri"],
                    "interaction_type": "collaboration",
                }
            )

            # 협업 능력 테스트
            collaboration_data = {
                "project": "software_development",
                "team_size": 3,
                "goals": ["code_review", "bug_fixing", "feature_development"],
            }

            collaboration_result = await social_intelligence.collaborate_effectively(context, collaboration_data)

            if collaboration_result and "collaboration_strategy" in collaboration_result:
                print("✅ 성공 - 협력 및 협업 능력 확인")
                print(f"  📊 협업 전략: {collaboration_result['collaboration_strategy']}")
                print(f"  🎭 역할 최적화: {collaboration_result.get('role_optimization', {})}")
                self.test_results.append(
                    {
                        "test_name": "협력 및 협업 능력",
                        "status": "성공",
                        "message": "협력 및 협업 능력이 정상적으로 작동합니다",
                    }
                )
            else:
                print("❌ 실패 - 협력 및 협업 능력 확인 실패")
                self.test_results.append(
                    {
                        "test_name": "협력 및 협업 능력",
                        "status": "실패",
                        "message": "협력 및 협업 능력 확인에 실패했습니다",
                    }
                )

        except Exception as e:
            print(f"❌ 오류 - 협력 및 협업 능력 테스트 중 오류 발생: {e}")
            self.test_results.append(
                {
                    "test_name": "협력 및 협업 능력",
                    "status": "오류",
                    "message": f"협력 및 협업 능력 테스트 중 오류 발생: {e}",
                }
            )

    async def test_performance(self):
        """성능 테스트"""
        print("\n⚡ 테스트 5: 성능 테스트")

        try:
            social_intelligence = SocialIntelligenceSystem()

            # 성능 테스트 실행
            test_interactions = [
                {
                    "interaction_id": "perf_test_1",
                    "context_data": {
                        "formality": 0.5,
                        "participants": ["user", "duri"],
                        "interaction_type": "conversation",
                    },
                },
                {
                    "interaction_id": "perf_test_2",
                    "context_data": {
                        "formality": 0.8,
                        "participants": ["colleague", "duri"],
                        "interaction_type": "collaboration",
                    },
                },
                {
                    "interaction_id": "perf_test_3",
                    "context_data": {
                        "formality": 0.2,
                        "participants": ["friend", "duri"],
                        "interaction_type": "conversation",
                    },
                },
            ]

            response_times = []

            for i, test_interaction in enumerate(test_interactions):
                start_time = time.time()
                result = await social_intelligence.process_social_interaction(  # noqa: F841
                    interaction_data=test_interaction,
                    context_data=test_interaction.get("context_data", {}),
                )
                end_time = time.time()

                response_time = end_time - start_time
                response_times.append(response_time)

                print(f"  📝 성능 테스트 {i+1}: {response_time:.3f}초")

            # 성능 메트릭 계산
            avg_response_time = sum(response_times) / len(response_times)
            max_response_time = max(response_times)
            min_response_time = min(response_times)  # noqa: F841

            # 성능 기준 평가
            if avg_response_time < 2.0 and max_response_time < 5.0:
                print("✅ 성공 - 성능이 목표 기준을 달성했습니다")
                self.test_results.append(
                    {
                        "test_name": "성능 테스트",
                        "status": "성공",
                        "message": f"평균 응답 시간: {avg_response_time:.3f}초, 최대 응답 시간: {max_response_time:.3f}초",  # noqa: E501
                    }
                )
            else:
                print("⚠️ 부분 성공 - 성능이 목표 기준에 미달합니다")
                self.test_results.append(
                    {
                        "test_name": "성능 테스트",
                        "status": "부분 성공",
                        "message": f"평균 응답 시간: {avg_response_time:.3f}초, 최대 응답 시간: {max_response_time:.3f}초",  # noqa: E501
                    }
                )

        except Exception as e:
            print(f"❌ 오류 - 성능 테스트 중 오류 발생: {e}")
            self.test_results.append(
                {
                    "test_name": "성능 테스트",
                    "status": "오류",
                    "message": f"성능 테스트 중 오류 발생: {e}",
                }
            )

    async def test_integration(self):
        """통합 테스트"""
        print("\n🔗 테스트 6: 통합 테스트")

        try:
            social_intelligence = SocialIntelligenceSystem()

            # 통합 테스트 실행
            comprehensive_interaction = {
                "interaction_id": "integration_test",
                "context_data": {
                    "formality": 0.6,
                    "professionalism": 0.7,
                    "participants": ["user", "colleague", "duri"],
                    "interaction_type": "collaboration",
                    "goals": ["project_work", "problem_solving", "team_building"],
                    "emotional_atmosphere": {"professional": 0.7, "friendly": 0.5},
                },
            }

            result = await social_intelligence.process_social_interaction(
                interaction_data=comprehensive_interaction,
                context_data=comprehensive_interaction.get("context_data", {}),
            )

            if result.success:
                print("✅ 성공 - 통합 테스트 완료")
                print(f"  📊 맥락 이해: {result.context_understanding:.2f}")
                print(f"  🤝 상호작용 최적화: {result.interaction_optimization:.2f}")
                print(f"  🔄 사회적 적응: {result.social_adaptation:.2f}")
                print(f"  👥 협업 효과성: {result.collaboration_effectiveness:.2f}")
                print(f"  💭 공감 점수: {result.empathy_score:.2f}")
                print(f"  🤝 신뢰 구축: {result.trust_building:.2f}")
                print(f"  💬 의사소통 품질: {result.communication_quality:.2f}")
                print(f"  📈 관계 개선: {result.relationship_improvement:.2f}")

                self.test_results.append(
                    {
                        "test_name": "통합 테스트",
                        "status": "성공",
                        "message": f"통합 점수: {(result.context_understanding + result.interaction_optimization + result.social_adaptation + result.collaboration_effectiveness) / 4:.2f}",  # noqa: E501
                    }
                )
            else:
                print("❌ 실패 - 통합 테스트 실패")
                self.test_results.append(
                    {
                        "test_name": "통합 테스트",
                        "status": "실패",
                        "message": f"통합 테스트 실패: {result.error_message}",
                    }
                )

        except Exception as e:
            print(f"❌ 오류 - 통합 테스트 중 오류 발생: {e}")
            self.test_results.append(
                {
                    "test_name": "통합 테스트",
                    "status": "오류",
                    "message": f"통합 테스트 중 오류 발생: {e}",
                }
            )

    async def print_test_results(self):
        """테스트 결과 출력"""
        print("\n" + "=" * 60)
        print("📊 Day 11 테스트 결과 요약")
        print("=" * 60)

        # 결과 통계
        total_tests = len(self.test_results)
        successful_tests = sum(1 for result in self.test_results if result["status"] == "성공")
        partial_success_tests = sum(1 for result in self.test_results if result["status"] == "부분 성공")
        failed_tests = sum(1 for result in self.test_results if result["status"] in ["실패", "오류"])

        success_rate = (successful_tests + partial_success_tests * 0.5) / total_tests * 100

        print(f"📈 전체 테스트 수: {total_tests}")
        print(f"✅ 성공: {successful_tests}")
        print(f"⚠️ 부분 성공: {partial_success_tests}")
        print(f"❌ 실패: {failed_tests}")
        print(f"📊 성공률: {success_rate:.1f}%")

        # 상세 결과
        print("\n📋 상세 결과:")
        for i, result in enumerate(self.test_results, 1):
            status_emoji = {
                "성공": "✅",
                "부분 성공": "⚠️",
                "실패": "❌",
                "오류": "🚨",
            }.get(result["status"], "❓")

            print(f"  {i}. {status_emoji} {result['test_name']}: {result['message']}")

        # 실행 시간
        execution_time = self.end_time - self.start_time
        print(f"\n⏱️ 총 실행 시간: {execution_time:.2f}초")

        # 결과 저장
        test_report = {
            "phase": "Day 11",
            "description": "사회적 지능 시스템",
            "timestamp": datetime.now().isoformat(),
            "execution_time": execution_time,
            "total_tests": total_tests,
            "successful_tests": successful_tests,
            "partial_success_tests": partial_success_tests,
            "failed_tests": failed_tests,
            "success_rate": success_rate,
            "test_results": self.test_results,
        }

        # 결과를 JSON 파일로 저장
        filename = f"test_results_day11_social_intelligence_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(test_report, f, ensure_ascii=False, indent=2)

        print(f"\n💾 테스트 결과가 {filename}에 저장되었습니다")

        # 최종 평가
        if success_rate >= 80:
            print("\n🎉 Day 11 테스트 성공! 사회적 지능 시스템이 정상적으로 작동합니다.")
        elif success_rate >= 60:
            print("\n⚠️ Day 11 테스트 부분 성공! 일부 기능에 개선이 필요합니다.")
        else:
            print("\n❌ Day 11 테스트 실패! 주요 기능에 문제가 있습니다.")


async def main():
    """메인 함수"""
    test_runner = Day11TestRunner()
    await test_runner.run_all_tests()


if __name__ == "__main__":
    asyncio.run(main())
