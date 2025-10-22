#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DuRi 사회적 지능 시스템 안전 테스트 러너
"""

import asyncio
import logging
import sys
import time
import traceback
from typing import Any, Dict

# 로깅 설정
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# 전역 변수로 시스템 인스턴스 관리
_social_intelligence_system = None


async def test_social_intelligence_safe():
    """사회적 지능 시스템 안전 테스트"""
    global _social_intelligence_system

    print("🧪 사회적 지능 시스템 안전 테스트 시작")

    try:
        # 1. 시스템 import 테스트 (안전한 방식)
        print("📦 시스템 import 중...")

        # 모듈 import를 try-except로 감싸서 안전하게 처리
        try:
            from social_intelligence_system import SocialIntelligenceSystem

            print("✅ 시스템 import 성공")
        except ImportError as e:
            print(f"❌ Import 오류: {e}")
            return False

        # 2. 시스템 초기화 테스트 (타임아웃 설정)
        print("🔧 시스템 초기화 중...")
        start_time = time.time()

        # 타임아웃을 설정하여 무한 루프 방지
        try:
            # 30초 타임아웃으로 초기화
            _social_intelligence_system = await asyncio.wait_for(
                _safe_initialize_system(SocialIntelligenceSystem), timeout=30.0
            )
            init_time = time.time() - start_time
            print(f"✅ 시스템 초기화 성공 (소요시간: {init_time:.2f}초)")
        except asyncio.TimeoutError:
            print("❌ 시스템 초기화 타임아웃 (30초 초과)")
            return False
        except Exception as e:
            print(f"❌ 시스템 초기화 실패: {e}")
            traceback.print_exc()
            return False

        # 3. 기본 기능 테스트
        print("🧠 기본 기능 테스트 중...")

        # 테스트 데이터
        test_interaction = {
            "interaction_id": "safe_test_1",
            "context_data": {
                "formality": 0.5,
                "professionalism": 0.5,
                "participants": ["user", "duri"],
                "interaction_type": "conversation",
                "goals": ["communication", "understanding"],
            },
        }

        # 사회적 상호작용 처리 테스트 (타임아웃 설정)
        try:
            start_time = time.time()
            result = await asyncio.wait_for(
                _social_intelligence_system.process_social_interaction(
                    interaction_data=test_interaction,
                    context_data=test_interaction.get("context_data", {}),
                ),
                timeout=60.0,
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

        except asyncio.TimeoutError:
            print("❌ 기능 테스트 타임아웃 (60초 초과)")
            return False
        except Exception as e:
            print(f"❌ 기능 테스트 실패: {e}")
            traceback.print_exc()
            return False

        # 4. 성능 요약 (타임아웃 설정)
        try:
            summary = await asyncio.wait_for(
                _social_intelligence_system.get_social_intelligence_summary(),
                timeout=30.0,
            )
            print(f"\n📈 성능 요약:")
            print(f"   총 상호작용: {summary['performance_metrics']['total_interactions']}")
            print(
                f"   성공률: {summary['performance_metrics']['successful_interactions']/summary['performance_metrics']['total_interactions']*100:.1f}%"
            )
            print(
                f"   평균 공감 점수: {summary['performance_metrics']['average_empathy_score']:.2f}"
            )
            print(f"   평균 신뢰 점수: {summary['performance_metrics']['average_trust_score']:.2f}")
        except asyncio.TimeoutError:
            print("⚠️ 성능 요약 타임아웃 (30초 초과)")
        except Exception as e:
            print(f"⚠️ 성능 요약 실패: {e}")

        return True

    except Exception as e:
        print(f"❌ 테스트 오류: {e}")
        traceback.print_exc()
        return False


async def _safe_initialize_system(SystemClass):
    """안전한 시스템 초기화"""
    try:
        # 시스템 초기화를 별도 스레드에서 실행
        loop = asyncio.get_event_loop()
        system = await loop.run_in_executor(None, SystemClass)
        return system
    except Exception as e:
        logger.error(f"시스템 초기화 중 오류: {e}")
        raise


async def main():
    """메인 함수"""
    print("🚀 DuRi 사회적 지능 시스템 안전 테스트 시작")
    print("=" * 50)

    success = await test_social_intelligence_safe()

    print("=" * 50)
    if success:
        print("🎉 모든 테스트가 성공적으로 완료되었습니다!")
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
        traceback.print_exc()
        sys.exit(1)
