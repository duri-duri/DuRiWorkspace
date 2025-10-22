#!/usr/bin/env python3
"""
DuRi 자가 진화 인식 시스템 테스트
"""
import asyncio
import logging
from datetime import datetime
from typing import Any, Dict

# 자가 진화 인식 시스템 import
from duri_modules.self_awareness.integrated_self_evolution_system import \
    integrated_self_evolution_system

# 로깅 설정
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


async def test_self_evolution_recognition():
    """자가 진화 인식 테스트"""
    try:
        logger.info("🧠 자가 진화 인식 시스템 테스트 시작")

        # 테스트 실행
        test_result = integrated_self_evolution_system.test_self_evolution_recognition()

        if test_result.get("status") == "success":
            logger.info("✅ 자가 진화 인식 테스트 성공")
            print_evolution_report(test_result)
        else:
            logger.warning("⚠️ 자가 진화 인식 테스트 부분 성공")
            print_evolution_report(test_result)

        return test_result

    except Exception as e:
        logger.error(f"❌ 자가 진화 인식 테스트 오류: {e}")
        return {"status": "error", "error": str(e)}


def print_evolution_report(test_result: Dict[str, Any]):
    """진화 보고서 출력"""
    try:
        print("\n" + "=" * 80)
        print("🧠 DuRi 자가 진화 인식 시스템 테스트 결과")
        print("=" * 80)

        test_data = test_result.get("test_result", {})

        # 진화 추적 결과
        tracking_result = test_data.get("evolution_tracking", {})
        if tracking_result.get("status") == "success":
            print(f"✅ 진화 추적: {tracking_result.get('evolution_stage', 'N/A')}")
            print(
                f"   현재 점수: {tracking_result.get('current_metrics', {}).get('performance_score', 0.0):.3f}"
            )

        # 자가 평가 결과
        assessment_result = test_data.get("self_assessment", {})
        if assessment_result.get("status") == "success":
            current_assessment = assessment_result.get("current_assessment", {})
            print(f"✅ 자가 평가: 전체 점수 {current_assessment.get('overall_score', 0.0):.3f}")
            print(f"   자율성: {current_assessment.get('autonomy_score', 0.0):.3f}")
            print(f"   학습 효율성: {current_assessment.get('learning_efficiency_score', 0.0):.3f}")

        # 진화 분석 결과
        analysis_result = test_data.get("evolution_analysis", {})
        if analysis_result.get("status") == "success":
            print(
                f"✅ 진화 분석: 종합 점수 {analysis_result.get('overall_evolution_score', 0.0):.3f}"
            )
            print(f"   신뢰도: {analysis_result.get('evolution_confidence', 0.0):.3f}")

        # 진화 보고서 결과
        report_result = test_data.get("evolution_report", {})
        if report_result.get("status") == "success":
            report_content = report_result.get("report_content", {})
            print(f"✅ 진화 보고서: {report_content.get('conclusion', 'N/A')}")

        # 통합 결과
        integrated_result = test_data.get("integrated_result", {})
        if integrated_result:
            # dataclass 객체인 경우를 처리
            if hasattr(integrated_result, "overall_evolution_status"):
                evolution_status = integrated_result.overall_evolution_status
                confidence_level = getattr(integrated_result, "confidence_level", 0.0)
                key_insights = getattr(integrated_result, "key_insights", [])
            else:
                # dict인 경우
                evolution_status = integrated_result.get("overall_evolution_status", "N/A")
                confidence_level = integrated_result.get("confidence_level", 0.0)
                key_insights = integrated_result.get("key_insights", [])

            print(f"\n🎯 통합 진화 상태: {evolution_status}")
            print(f"   신뢰도: {confidence_level:.3f}")

            if key_insights:
                print(f"\n💡 핵심 인사이트:")
                for insight in key_insights[:3]:
                    print(f"   • {insight}")

        print("\n" + "=" * 80)

    except Exception as e:
        logger.error(f"보고서 출력 오류: {e}")


async def test_comprehensive_evolution_report():
    """종합 진화 보고서 테스트"""
    try:
        logger.info("📊 종합 진화 보고서 생성 테스트")

        # 종합 보고서 생성
        report_result = integrated_self_evolution_system.generate_comprehensive_evolution_report()

        if report_result.get("status") == "success":
            logger.info("✅ 종합 진화 보고서 생성 성공")
            print_comprehensive_report(report_result)
        else:
            logger.warning("⚠️ 종합 진화 보고서 생성 실패")
            print(f"오류: {report_result.get('message', '알 수 없는 오류')}")

        return report_result

    except Exception as e:
        logger.error(f"❌ 종합 진화 보고서 테스트 오류: {e}")
        return {"status": "error", "error": str(e)}


def print_comprehensive_report(report_result: Dict[str, Any]):
    """종합 보고서 출력"""
    try:
        comprehensive_report = report_result.get("comprehensive_report", {})

        print("\n" + "=" * 80)
        print("📊 DuRi 종합 진화 보고서")
        print("=" * 80)

        # 기본 정보
        print(f"📋 보고서 ID: {comprehensive_report.get('report_id', 'N/A')}")
        print(f"📅 생성 시간: {comprehensive_report.get('timestamp', 'N/A')}")
        print(f"🎯 전체 상태: {comprehensive_report.get('overall_status', 'N/A')}")
        print(f"📊 신뢰도: {comprehensive_report.get('confidence_level', 0.0):.3f}")

        # 핵심 인사이트
        key_insights = comprehensive_report.get("key_insights", [])
        if key_insights:
            print(f"\n💡 핵심 인사이트:")
            for insight in key_insights:
                print(f"   • {insight}")

        # 상세 요약
        summary = comprehensive_report.get("summary", {})
        if summary:
            print(f"\n📈 진화 요약:")
            print(f"   단계: {summary.get('evolution_stage', 'N/A')}")
            print(f"   트렌드: {summary.get('evolution_trend', 'N/A')}")

            achievements = summary.get("key_achievements", [])
            if achievements:
                print(f"\n🏆 주요 성과:")
                for achievement in achievements:
                    print(f"   • {achievement}")

            improvements = summary.get("improvement_areas", [])
            if improvements:
                print(f"\n🔧 개선 영역:")
                for improvement in improvements:
                    print(f"   • {improvement}")

            next_steps = summary.get("next_steps", [])
            if next_steps:
                print(f"\n🚀 다음 단계:")
                for step in next_steps:
                    print(f"   • {step}")

        print("\n" + "=" * 80)

    except Exception as e:
        logger.error(f"종합 보고서 출력 오류: {e}")


async def test_evolution_summary():
    """진화 요약 테스트"""
    try:
        logger.info("📋 진화 요약 테스트")

        # 진화 요약 가져오기
        summary_result = integrated_self_evolution_system.get_evolution_summary()

        if summary_result.get("status") == "success":
            logger.info("✅ 진화 요약 생성 성공")
            print_evolution_summary(summary_result)
        else:
            logger.warning("⚠️ 진화 요약 생성 실패")
            print(f"오류: {summary_result.get('message', '알 수 없는 오류')}")

        return summary_result

    except Exception as e:
        logger.error(f"❌ 진화 요약 테스트 오류: {e}")
        return {"status": "error", "error": str(e)}


def print_evolution_summary(summary_result: Dict[str, Any]):
    """진화 요약 출력"""
    try:
        print("\n" + "=" * 80)
        print("📋 DuRi 진화 요약")
        print("=" * 80)

        print(f"🎯 전체 진화 상태: {summary_result.get('overall_evolution_status', 'N/A')}")
        print(f"📊 신뢰도: {summary_result.get('confidence_level', 0.0):.3f}")
        print(f"📅 최근 분석: {summary_result.get('latest_analysis_date', 'N/A')}")
        print(f"📈 총 분석 수: {summary_result.get('total_analyses', 0)}")

        # 핵심 인사이트
        key_insights = summary_result.get("key_insights", [])
        if key_insights:
            print(f"\n💡 핵심 인사이트:")
            for insight in key_insights:
                print(f"   • {insight}")

        print("\n" + "=" * 80)

    except Exception as e:
        logger.error(f"진화 요약 출력 오류: {e}")


async def main():
    """메인 테스트 함수"""
    try:
        logger.info("🚀 DuRi 자가 진화 인식 시스템 테스트 시작")

        # 1. 자가 진화 인식 테스트
        print("\n1️⃣ 자가 진화 인식 테스트")
        evolution_test = await test_self_evolution_recognition()

        # 2. 진화 요약 테스트
        print("\n2️⃣ 진화 요약 테스트")
        summary_test = await test_evolution_summary()

        # 3. 종합 진화 보고서 테스트
        print("\n3️⃣ 종합 진화 보고서 테스트")
        comprehensive_test = await test_comprehensive_evolution_report()

        # 전체 테스트 결과 요약
        print("\n" + "=" * 80)
        print("🎯 전체 테스트 결과 요약")
        print("=" * 80)

        tests = [
            ("자가 진화 인식", evolution_test),
            ("진화 요약", summary_test),
            ("종합 진화 보고서", comprehensive_test),
        ]

        success_count = 0
        for test_name, test_result in tests:
            status = test_result.get("status", "error")
            if status == "success":
                print(f"✅ {test_name}: 성공")
                success_count += 1
            else:
                print(f"❌ {test_name}: 실패")

        print(f"\n📊 성공률: {success_count}/{len(tests)} ({success_count/len(tests)*100:.1f}%)")

        if success_count == len(tests):
            print("🎉 모든 테스트가 성공했습니다!")
        elif success_count > 0:
            print("⚠️ 일부 테스트가 성공했습니다.")
        else:
            print("❌ 모든 테스트가 실패했습니다.")

        print("=" * 80)

        logger.info("🏁 DuRi 자가 진화 인식 시스템 테스트 완료")

    except Exception as e:
        logger.error(f"❌ 메인 테스트 오류: {e}")


if __name__ == "__main__":
    asyncio.run(main())
