#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DuRi 사회적 지능 시스템 빠른 테스트
"""

import asyncio
import logging
import sys
import time

# 로깅 설정
logging.basicConfig(
    level=logging.ERROR,  # ERROR 레벨로 설정하여 로그 최소화
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


async def quick_test():
    """빠른 테스트"""
    print("🧪 DuRi 사회적 지능 시스템 빠른 테스트 시작")

    try:
        # 1. 시스템 import 테스트
        print("📦 시스템 import 중...")
        from social_intelligence_system import SocialIntelligenceSystem

        print("✅ 시스템 import 성공")

        # 2. 시스템 초기화 테스트
        print("🔧 시스템 초기화 중...")
        start_time = time.time()

        # 간단한 초기화
        social_intelligence = SocialIntelligenceSystem()
        init_time = time.time() - start_time
        print(f"✅ 시스템 초기화 성공 (소요시간: {init_time:.2f}초)")

        # 3. 기본 기능 테스트
        print("🧠 기본 기능 테스트 중...")

        # 테스트 데이터
        test_interaction = {
            "interaction_id": "quick_test_1",
            "context_data": {
                "formality": 0.5,
                "professionalism": 0.5,
                "participants": ["user", "duri"],
                "interaction_type": "conversation",
                "goals": ["communication", "understanding"],
            },
        }

        # 사회적 상호작용 처리 테스트
        start_time = time.time()
        result = await social_intelligence.process_social_interaction(
            interaction_data=test_interaction,
            context_data=test_interaction.get("context_data", {}),
        )
        process_time = time.time() - start_time

        # 결과 출력
        print(f"\n📊 테스트 결과:")
        print(f"   ✅ 성공 여부: {result.success}")
        print(f"   🧠 사회적 지능 점수: {result.context_understanding:.2f}")
        print(f"   📊 공감 점수: {result.empathy_score:.2f}")
        print(f"   🤝 신뢰 구축: {result.trust_building:.2f}")
        print(f"   💬 의사소통 품질: {result.communication_quality:.2f}")
        print(f"   💡 인사이트: {len(result.insights)}개")
        print(f"   ⏱️ 처리 시간: {process_time:.2f}초")

        if result.success:
            print("\n🎯 사회적 지능 시스템 테스트 성공!")
        else:
            print(f"\n❌ 테스트 실패: {result.error_message}")

        return True

    except ImportError as e:
        print(f"❌ Import 오류: {e}")
        return False
    except Exception as e:
        print(f"❌ 테스트 오류: {e}")
        import traceback

        traceback.print_exc()
        return False


async def main():
    """메인 함수"""
    print("🚀 DuRi 사회적 지능 시스템 빠른 테스트 시작")
    print("=" * 50)

    success = await quick_test()

    print("=" * 50)
    if success:
        print("🎉 테스트가 성공적으로 완료되었습니다!")
    else:
        print("⚠️ 테스트 중 문제가 발생했습니다.")

    return success


if __name__ == "__main__":
    try:
        result = asyncio.run(main())
        sys.exit(0 if result else 1)
    except KeyboardInterrupt:
        print("\n⚠️ 테스트가 사용자에 의해 중단되었습니다.")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 예상치 못한 오류: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
