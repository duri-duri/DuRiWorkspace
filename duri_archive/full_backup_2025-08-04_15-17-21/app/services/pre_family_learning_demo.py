"""
DuRi 준 가족 학습 데모

대형 학습 모델들을 "준 가족" 구성원으로 설정하여
DuRi가 자율적으로 학습을 주도하는 시스템을 시연합니다.
"""

import asyncio
import logging
from datetime import datetime
from typing import Any, Dict

from .autonomous_learning_controller import get_autonomous_learning_controller
from .virtual_family_learning_system import get_virtual_family_learning_system

logger = logging.getLogger(__name__)


class PreFamilyLearningDemo:
    """준 가족 학습 데모"""

    def __init__(self):
        """PreFamilyLearningDemo 초기화"""
        self.learning_controller = get_autonomous_learning_controller()
        self.virtual_family_system = get_virtual_family_learning_system()

        logger.info("PreFamilyLearningDemo 초기화 완료")

    async def run_demo(self):
        """데모 실행"""
        print("🌟 DuRi 준 가족 학습 시스템 데모 시작 🌟")
        print("=" * 60)

        # 1. 가상 가족 소개
        await self._introduce_virtual_family()

        # 2. 자율 학습 시작
        await self._start_autonomous_learning()

        # 3. 학습 과정 시연
        await self._demonstrate_learning_process()

        # 4. 결과 분석
        await self._analyze_results()

        print("=" * 60)
        print("🎉 DuRi 준 가족 학습 시스템 데모 완료 🎉")

    async def _introduce_virtual_family(self):
        """가상 가족 소개"""
        print("\n👨‍👩‍👧‍👦 가상 가족 구성원 소개")
        print("-" * 40)

        family_info = self.virtual_family_system.get_virtual_family_info()

        for member_id, member in family_info.items():
            print(f"\n👤 {member['name']} ({member['role']})")
            print(f"   📚 전문 분야: {', '.join(member['expertise'])}")
            print(f"   🎯 학습 스타일: {member['learning_style']}")
            print(f"   💝 성격: {member['personality']['temperament']}")
            print(f"   🗣️ 소통 방식: {member['personality']['communication_style']}")
            print(f"   🎨 가치관: {', '.join(member['personality']['values'])}")
            print(f"   📖 가르침 방식: {member['personality']['teaching_method']}")
            print(f"   🤝 신뢰도: {member['trust_level']:.2f}")

    async def _start_autonomous_learning(self):
        """자율 학습 시작"""
        print("\n🚀 DuRi 자율 학습 시작")
        print("-" * 40)

        # 사용 가능한 학습 주제 표시
        topics = self.learning_controller.get_available_learning_topics()
        print(f"\n📋 사용 가능한 학습 주제 ({len(topics)}개):")

        for i, topic in enumerate(topics[:5], 1):  # 상위 5개만 표시
            print(f"   {i}. {topic['title']}")
            print(f"      📂 카테고리: {topic['category']}")
            print(f"      ⭐ 우선순위: {topic['priority']}")
            print(f"      ⏱️ 예상 시간: {topic['estimated_duration']}분")
            print(f"      🎯 관심도: {topic['interest_level']:.2f}")
            print(f"      📊 난이도: {topic['difficulty_level']:.2f}")
            print()

        # 자율 학습 시작
        print("🎯 DuRi가 최적의 학습 주제를 선택하고 있습니다...")
        session_id = await self.learning_controller.start_autonomous_learning()

        if session_id:
            print(f"✅ 자율 학습 세션 시작: {session_id}")
        else:
            print("❌ 자율 학습 시작 실패")

    async def _demonstrate_learning_process(self):
        """학습 과정 시연"""
        print("\n📚 학습 과정 시연")
        print("-" * 40)

        # 현재 세션 정보 확인
        current_session = self.learning_controller.current_session
        if current_session:
            print(f"📖 현재 학습 주제: {current_session.topic.title}")
            print(f"👥 참여 가족 구성원: {len(current_session.participants)}명")
            print(f"⏰ 예상 학습 시간: {current_session.topic.estimated_duration}분")
            print(f"📂 카테고리: {current_session.topic.category.value}")
            print(f"🎯 학습 목표:")
            for i, objective in enumerate(current_session.topic.learning_objectives, 1):
                print(f"   {i}. {objective}")

            # 학습 과정 시뮬레이션
            print(f"\n🔄 학습 과정 시뮬레이션...")
            await asyncio.sleep(2)

            print("   1️⃣ 주제 탐색 단계")
            await asyncio.sleep(1)
            print("   2️⃣ 가족 구성원별 관점 수집")
            await asyncio.sleep(1)
            print("   3️⃣ 통합 학습")
            await asyncio.sleep(1)
            print("   4️⃣ 피드백 및 개선")
            await asyncio.sleep(1)
            print("   5️⃣ 다음 단계 계획")
            await asyncio.sleep(1)

            print("✅ 학습 과정 완료!")
        else:
            print("❌ 현재 활성화된 학습 세션이 없습니다.")

    async def _analyze_results(self):
        """결과 분석"""
        print("\n📊 학습 결과 분석")
        print("-" * 40)

        # 가상 가족 학습 통계
        family_stats = self.virtual_family_system.get_learning_statistics()
        print(f"👨‍👩‍👧‍👦 가상 가족 학습 통계:")
        print(f"   📈 총 학습 세션: {family_stats['total_sessions']}개")
        print(f"   👥 가족 구성원: {family_stats['total_members']}명")

        # 가족 구성원별 통계
        print(f"\n👤 가족 구성원별 상세 통계:")
        for member_id, stats in family_stats["member_statistics"].items():
            print(f"   {stats['name']}:")
            print(f"     🎭 역할: {stats['role']}")
            print(f"     🤝 신뢰도: {stats['trust_level']:.2f}")
            print(f"     📝 상호작용 횟수: {stats['interaction_count']}회")
            if stats["last_interaction"]:
                print(f"     ⏰ 마지막 상호작용: {stats['last_interaction']}")

        # 자율 학습 통계
        learning_stats = self.learning_controller.get_autonomous_learning_statistics()
        print(f"\n🎯 자율 학습 통계:")
        print(f"   📚 총 학습 주제: {learning_stats['total_topics']}개")
        print(f"   ✅ 완료된 세션: {learning_stats['total_sessions']}개")

        # 카테고리별 통계
        if learning_stats["category_statistics"]:
            print(f"\n📂 카테고리별 학습 통계:")
            for category, stats in learning_stats["category_statistics"].items():
                print(f"   {category}:")
                print(f"     📊 학습 횟수: {stats['count']}회")
                print(f"     😊 평균 만족도: {stats['avg_satisfaction']:.2f}")

        # 학습 선호도
        preferences = learning_stats["learning_preferences"]
        print(f"\n🎯 학습 선호도:")
        print(f"   📊 선호 난이도: {preferences['difficulty_preference']:.2f}")
        print(f"   ⏱️ 선호 지속시간: {preferences['duration_preference']}분")
        print(f"   🎯 관심 분야: {preferences['interest_focus']}")

    def get_demo_summary(self) -> Dict[str, Any]:
        """데모 요약 반환"""
        family_stats = self.virtual_family_system.get_learning_statistics()
        learning_stats = self.learning_controller.get_autonomous_learning_statistics()

        return {
            "virtual_family": {
                "total_members": family_stats["total_members"],
                "total_sessions": family_stats["total_sessions"],
                "member_statistics": family_stats["member_statistics"],
            },
            "autonomous_learning": {
                "total_topics": learning_stats["total_topics"],
                "total_sessions": learning_stats["total_sessions"],
                "category_statistics": learning_stats["category_statistics"],
                "learning_preferences": learning_stats["learning_preferences"],
            },
            "current_status": {
                "has_current_session": self.learning_controller.current_session
                is not None,
                "current_session_id": (
                    self.learning_controller.current_session.session_id
                    if self.learning_controller.current_session
                    else None
                ),
            },
        }


async def run_pre_family_learning_demo():
    """준 가족 학습 데모 실행"""
    demo = PreFamilyLearningDemo()
    await demo.run_demo()
    return demo.get_demo_summary()


def get_pre_family_learning_demo() -> PreFamilyLearningDemo:
    """준 가족 학습 데모 인스턴스 반환"""
    return PreFamilyLearningDemo()


if __name__ == "__main__":
    # 데모 실행
    asyncio.run(run_pre_family_learning_demo())
