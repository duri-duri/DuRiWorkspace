#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SocialIntelligenceSystem 자동 등록 테스트

이 모듈은 SocialIntelligenceSystem이 새로운 자동 등록 방식으로 제대로 등록되는지 테스트합니다.
"""

import asyncio
import logging
import sys
from pathlib import Path

# 현재 디렉토리를 sys.path에 추가
sys.path.append(str(Path(__file__).parent))

# 로깅 설정
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


async def test_social_intelligence_registration():
    """SocialIntelligenceSystem 자동 등록 테스트"""
    logger.info("🧪 SocialIntelligenceSystem 자동 등록 테스트 시작")

    try:
        from module_registry import ModulePriority, ModuleRegistry

        # 레지스트리 인스턴스 가져오기
        registry = ModuleRegistry.get_instance()

        # SocialIntelligenceSystem import (자동 등록 트리거)
        logger.info("📦 SocialIntelligenceSystem import 중...")
        from social_intelligence_system import SocialIntelligenceSystem

        # 자동 등록 확인
        module_info = registry.get_module("social_intelligence_system")
        if module_info:
            logger.info("✅ SocialIntelligenceSystem 자동 등록 성공")
            logger.info(f"   - 이름: {module_info.name}")
            logger.info(f"   - 의존성: {module_info.dependencies}")
            logger.info(f"   - 우선순위: {module_info.priority.value}")
            logger.info(f"   - 버전: {module_info.version}")
            logger.info(f"   - 설명: {module_info.description}")
            logger.info(f"   - 상태: {module_info.state.value}")
        else:
            logger.error("❌ SocialIntelligenceSystem 자동 등록 실패")
            return False

        # 모듈 로드 테스트
        logger.info("🔧 SocialIntelligenceSystem 로드 중...")
        success = await registry.load_module("social_intelligence_system")
        if success:
            logger.info("✅ SocialIntelligenceSystem 로드 성공")
        else:
            logger.error("❌ SocialIntelligenceSystem 로드 실패")
            return False

        # 모듈 초기화 테스트
        logger.info("🚀 SocialIntelligenceSystem 초기화 중...")
        success = await registry.initialize_module("social_intelligence_system")
        if success:
            logger.info("✅ SocialIntelligenceSystem 초기화 성공")
        else:
            logger.error("❌ SocialIntelligenceSystem 초기화 실패")
            return False

        # 모듈 실행 테스트
        logger.info("🎯 SocialIntelligenceSystem 실행 테스트 중...")
        module_instance = registry.get_module_instance("social_intelligence_system")
        if module_instance:
            # 테스트 컨텍스트
            test_context = {
                "context_data": {
                    "formality": 0.5,
                    "professionalism": 0.5,
                    "participants": ["user", "duri"],
                    "interaction_type": "conversation",
                    "goals": ["communication", "understanding"],
                }
            }

            result = await module_instance.execute(test_context)
            logger.info(f"✅ SocialIntelligenceSystem 실행 성공: {result.get('status', 'unknown')}")
        else:
            logger.error("❌ SocialIntelligenceSystem 인스턴스를 가져올 수 없습니다")
            return False

        return True

    except Exception as e:
        logger.error(f"❌ SocialIntelligenceSystem 자동 등록 테스트 실패: {e}")
        import traceback

        traceback.print_exc()
        return False


async def test_all_registered_modules():
    """모든 등록된 모듈 확인"""
    logger.info("📊 모든 등록된 모듈 확인")

    try:
        from module_registry import ModuleRegistry

        registry = ModuleRegistry.get_instance()
        all_modules = registry.get_all_modules()

        logger.info(f"📈 등록된 모듈 수: {len(all_modules)}")

        for name, info in all_modules.items():
            logger.info(f"   - {name}: {info.state.value} (의존성: {info.dependencies})")

        return True

    except Exception as e:
        logger.error(f"❌ 모듈 목록 확인 실패: {e}")
        return False


async def main():
    """메인 함수"""
    logger.info("🚀 SocialIntelligenceSystem 자동 등록 테스트 시작")
    print("=" * 60)

    # 테스트 실행
    tests = [
        (
            "SocialIntelligenceSystem 자동 등록 테스트",
            test_social_intelligence_registration,
        ),
        ("모든 등록된 모듈 확인", test_all_registered_modules),
    ]

    results = {}
    for test_name, test_func in tests:
        print(f"\n🧪 {test_name} 실행 중...")
        try:
            result = await test_func()
            results[test_name] = result
            status = "✅ 성공" if result else "❌ 실패"
            print(f"   {status}")
        except Exception as e:
            results[test_name] = False
            print(f"   ❌ 예외 발생: {e}")

    # 결과 요약
    print("\n" + "=" * 60)
    print("📊 테스트 결과 요약:")
    for test_name, result in results.items():
        status = "✅ 성공" if result else "❌ 실패"
        print(f"   {test_name}: {status}")

    success_count = sum(1 for result in results.values() if result)
    total_count = len(results)

    print(f"\n🎯 전체 결과: {success_count}/{total_count} 성공")

    if success_count == total_count:
        print("🎉 모든 테스트가 성공했습니다!")
    else:
        print("⚠️ 일부 테스트가 실패했습니다.")

    return success_count == total_count


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
