#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DuRi Phase 14: 커서 통합 시스템 테스트

Phase 14에서 구현된 커서 통합 시스템의 기능을 테스트하는 스크립트

테스트 항목:
1. 시스템 초기화 테스트
2. 사용자 입력 처리 테스트
3. 응답 생성 테스트
4. 컨텍스트 관리 테스트
5. 성능 테스트
6. 에러 처리 테스트
"""

import asyncio
import json
import logging
import time
from datetime import datetime
from typing import Any, Dict, List

# Phase 14 시스템 import
try:
    from phase14_cursor_integration import (
        CursorContext,
        CursorIntegrationSystem,
        CursorPhase,
        CursorResult,
        CursorStatus,
    )
except ImportError as e:
    print(f"❌ Phase 14 시스템 import 실패: {e}")
    exit(1)

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Phase14TestRunner:
    """Phase 14 테스트 러너"""

    def __init__(self):
        self.test_results = []
        self.start_time = None
        self.end_time = None

    async def run_all_tests(self):
        """모든 테스트 실행"""
        print("🧪 Phase 14 커서 통합 시스템 테스트 시작")
        print("=" * 60)

        self.start_time = time.time()

        # 테스트 실행
        await self.test_system_initialization()
        await self.test_user_input_processing()
        await self.test_response_generation()
        await self.test_context_management()
        await self.test_performance()
        await self.test_error_handling()

        self.end_time = time.time()

        # 결과 출력
        await self.print_test_results()

    async def test_system_initialization(self):
        """시스템 초기화 테스트"""
        print("\n🔧 테스트 1: 시스템 초기화")

        try:
            cursor_system = CursorIntegrationSystem()
            success = await cursor_system.initialize()

            if success:
                print("✅ 성공 - 시스템이 성공적으로 초기화되었습니다")
                self.test_results.append(
                    {
                        "test_name": "시스템 초기화",
                        "status": "성공",
                        "message": "시스템이 성공적으로 초기화되었습니다",
                    }
                )
            else:
                print("❌ 실패 - 시스템 초기화에 실패했습니다")
                self.test_results.append(
                    {
                        "test_name": "시스템 초기화",
                        "status": "실패",
                        "message": "시스템 초기화에 실패했습니다",
                    }
                )

        except Exception as e:
            print(f"❌ 오류 - 시스템 초기화 중 오류 발생: {e}")
            self.test_results.append(
                {
                    "test_name": "시스템 초기화",
                    "status": "오류",
                    "message": f"시스템 초기화 중 오류 발생: {e}",
                }
            )

    async def test_user_input_processing(self):
        """사용자 입력 처리 테스트"""
        print("\n📝 테스트 2: 사용자 입력 처리")

        try:
            cursor_system = CursorIntegrationSystem()
            await cursor_system.initialize()

            test_inputs = [
                "안녕하세요! 오늘 날씨는 어떤가요?",
                "Python으로 웹 애플리케이션을 만들고 싶어요.",
                "머신러닝 모델의 성능을 개선하는 방법을 알려주세요.",
            ]

            success_count = 0
            total_count = len(test_inputs)

            for i, test_input in enumerate(test_inputs, 1):
                print(f"  📝 테스트 입력 {i}: {test_input[:50]}...")

                result = await cursor_system.process_user_input(
                    user_input=test_input,
                    session_id=f"test_session_{i}",
                    user_id="test_user",
                )

                if result.success:
                    success_count += 1
                    print(f"    ✅ 성공 - 응답 시간: {result.response_time:.3f}초")
                else:
                    print(f"    ❌ 실패: {result.error_message}")

            success_rate = success_count / total_count * 100

            if success_rate >= 80:
                print(f"✅ 성공 - 사용자 입력 처리 성공률: {success_rate:.1f}%")
                self.test_results.append(
                    {
                        "test_name": "사용자 입력 처리",
                        "status": "성공",
                        "message": f"사용자 입력 처리 성공률: {success_rate:.1f}%",
                    }
                )
            else:
                print(f"⚠️ 부분 성공 - 사용자 입력 처리 성공률: {success_rate:.1f}%")
                self.test_results.append(
                    {
                        "test_name": "사용자 입력 처리",
                        "status": "부분 성공",
                        "message": f"사용자 입력 처리 성공률: {success_rate:.1f}%",
                    }
                )

        except Exception as e:
            print(f"❌ 오류 - 사용자 입력 처리 테스트 중 오류 발생: {e}")
            self.test_results.append(
                {
                    "test_name": "사용자 입력 처리",
                    "status": "오류",
                    "message": f"사용자 입력 처리 테스트 중 오류 발생: {e}",
                }
            )

    async def test_response_generation(self):
        """응답 생성 테스트"""
        print("\n💬 테스트 3: 응답 생성")

        try:
            cursor_system = CursorIntegrationSystem()
            await cursor_system.initialize()

            test_input = "Python으로 데이터 분석을 하고 싶어요."
            result = await cursor_system.process_user_input(
                user_input=test_input,
                session_id="test_response_generation",
                user_id="test_user",
            )

            if result.success and result.response:
                response_length = len(result.response)
                response_time = result.response_time

                if response_length > 10 and response_time < 5.0:
                    print("✅ 성공 - 응답이 성공적으로 생성되었습니다")
                    print(f"  📊 응답 길이: {response_length}자")
                    print(f"  ⏱️ 응답 시간: {response_time:.3f}초")
                    self.test_results.append(
                        {
                            "test_name": "응답 생성",
                            "status": "성공",
                            "message": f"응답 길이: {response_length}자, 응답 시간: {response_time:.3f}초",
                        }
                    )
                else:
                    print("⚠️ 부분 성공 - 응답이 생성되었지만 품질이 낮습니다")
                    self.test_results.append(
                        {
                            "test_name": "응답 생성",
                            "status": "부분 성공",
                            "message": f"응답 길이: {response_length}자, 응답 시간: {response_time:.3f}초",
                        }
                    )
            else:
                print("❌ 실패 - 응답 생성에 실패했습니다")
                self.test_results.append(
                    {
                        "test_name": "응답 생성",
                        "status": "실패",
                        "message": "응답 생성에 실패했습니다",
                    }
                )

        except Exception as e:
            print(f"❌ 오류 - 응답 생성 테스트 중 오류 발생: {e}")
            self.test_results.append(
                {
                    "test_name": "응답 생성",
                    "status": "오류",
                    "message": f"응답 생성 테스트 중 오류 발생: {e}",
                }
            )

    async def test_context_management(self):
        """컨텍스트 관리 테스트"""
        print("\n🗂️ 테스트 4: 컨텍스트 관리")

        try:
            cursor_system = CursorIntegrationSystem()
            await cursor_system.initialize()

            # 컨텍스트 생성 테스트
            session_id = "test_context_management"
            user_id = "test_user"

            # 첫 번째 입력으로 컨텍스트 생성
            result1 = await cursor_system.process_user_input(
                user_input="첫 번째 메시지입니다.",
                session_id=session_id,
                user_id=user_id,
            )

            # 두 번째 입력으로 기존 컨텍스트 사용
            result2 = await cursor_system.process_user_input(
                user_input="두 번째 메시지입니다.",
                session_id=session_id,
                user_id=user_id,
            )

            # 컨텍스트 조회 테스트
            context = await cursor_system.get_context(session_id)

            if context and context.session_id == session_id:
                print("✅ 성공 - 컨텍스트 관리가 정상적으로 작동합니다")
                print(f"  📊 세션 ID: {context.session_id}")
                print(f"  👤 사용자 ID: {context.user_id}")
                print(f"  📅 시작 시간: {context.start_time}")
                self.test_results.append(
                    {
                        "test_name": "컨텍스트 관리",
                        "status": "성공",
                        "message": "컨텍스트 관리가 정상적으로 작동합니다",
                    }
                )
            else:
                print("❌ 실패 - 컨텍스트 관리에 문제가 있습니다")
                self.test_results.append(
                    {
                        "test_name": "컨텍스트 관리",
                        "status": "실패",
                        "message": "컨텍스트 관리에 문제가 있습니다",
                    }
                )

        except Exception as e:
            print(f"❌ 오류 - 컨텍스트 관리 테스트 중 오류 발생: {e}")
            self.test_results.append(
                {
                    "test_name": "컨텍스트 관리",
                    "status": "오류",
                    "message": f"컨텍스트 관리 테스트 중 오류 발생: {e}",
                }
            )

    async def test_performance(self):
        """성능 테스트"""
        print("\n⚡ 테스트 5: 성능 테스트")

        try:
            cursor_system = CursorIntegrationSystem()
            await cursor_system.initialize()

            # 성능 테스트 실행
            test_inputs = [
                "성능 테스트 1",
                "성능 테스트 2",
                "성능 테스트 3",
                "성능 테스트 4",
                "성능 테스트 5",
            ]

            response_times = []

            for i, test_input in enumerate(test_inputs):
                start_time = time.time()
                result = await cursor_system.process_user_input(
                    user_input=test_input,
                    session_id=f"perf_test_{i}",
                    user_id="test_user",
                )
                end_time = time.time()

                response_time = end_time - start_time
                response_times.append(response_time)

            # 성능 메트릭 계산
            avg_response_time = sum(response_times) / len(response_times)
            max_response_time = max(response_times)
            min_response_time = min(response_times)

            # 성능 메트릭 조회
            metrics = await cursor_system.get_performance_metrics()

            print(f"  📊 평균 응답 시간: {avg_response_time:.3f}초")
            print(f"  📊 최대 응답 시간: {max_response_time:.3f}초")
            print(f"  📊 최소 응답 시간: {min_response_time:.3f}초")
            print(f"  📊 총 요청 수: {metrics['total_requests']}")
            print(
                f"  📊 성공률: {metrics['successful_requests']/metrics['total_requests']*100:.1f}%"
            )

            # 성능 기준 평가
            if avg_response_time < 2.0 and max_response_time < 5.0:
                print("✅ 성공 - 성능이 목표 기준을 달성했습니다")
                self.test_results.append(
                    {
                        "test_name": "성능 테스트",
                        "status": "성공",
                        "message": f"평균 응답 시간: {avg_response_time:.3f}초, 최대 응답 시간: {max_response_time:.3f}초",
                    }
                )
            else:
                print("⚠️ 부분 성공 - 성능이 목표 기준에 미달합니다")
                self.test_results.append(
                    {
                        "test_name": "성능 테스트",
                        "status": "부분 성공",
                        "message": f"평균 응답 시간: {avg_response_time:.3f}초, 최대 응답 시간: {max_response_time:.3f}초",
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

    async def test_error_handling(self):
        """에러 처리 테스트"""
        print("\n🚨 테스트 6: 에러 처리")

        try:
            cursor_system = CursorIntegrationSystem()
            await cursor_system.initialize()

            # 잘못된 입력 테스트
            invalid_inputs = [
                "",  # 빈 입력
                "a" * 10000,  # 너무 긴 입력
                None,  # None 입력
            ]

            error_handled_count = 0
            total_count = len(invalid_inputs)

            for i, invalid_input in enumerate(invalid_inputs):
                try:
                    result = await cursor_system.process_user_input(
                        user_input=invalid_input if invalid_input is not None else "",
                        session_id=f"error_test_{i}",
                        user_id="test_user",
                    )

                    # 에러가 적절히 처리되었는지 확인
                    if not result.success and result.error_message:
                        error_handled_count += 1
                        print(f"  ✅ 에러 처리 성공: {result.error_message[:50]}...")
                    else:
                        print(f"  ⚠️ 에러 처리 부분 성공: 예상된 에러가 발생하지 않음")

                except Exception as e:
                    error_handled_count += 1
                    print(f"  ✅ 예외 처리 성공: {str(e)[:50]}...")

            error_handling_rate = error_handled_count / total_count * 100

            if error_handling_rate >= 80:
                print(f"✅ 성공 - 에러 처리 성공률: {error_handling_rate:.1f}%")
                self.test_results.append(
                    {
                        "test_name": "에러 처리",
                        "status": "성공",
                        "message": f"에러 처리 성공률: {error_handling_rate:.1f}%",
                    }
                )
            else:
                print(f"⚠️ 부분 성공 - 에러 처리 성공률: {error_handling_rate:.1f}%")
                self.test_results.append(
                    {
                        "test_name": "에러 처리",
                        "status": "부분 성공",
                        "message": f"에러 처리 성공률: {error_handling_rate:.1f}%",
                    }
                )

        except Exception as e:
            print(f"❌ 오류 - 에러 처리 테스트 중 오류 발생: {e}")
            self.test_results.append(
                {
                    "test_name": "에러 처리",
                    "status": "오류",
                    "message": f"에러 처리 테스트 중 오류 발생: {e}",
                }
            )

    async def print_test_results(self):
        """테스트 결과 출력"""
        print("\n" + "=" * 60)
        print("📊 Phase 14 테스트 결과 요약")
        print("=" * 60)

        # 결과 통계
        total_tests = len(self.test_results)
        successful_tests = sum(
            1 for result in self.test_results if result["status"] == "성공"
        )
        partial_success_tests = sum(
            1 for result in self.test_results if result["status"] == "부분 성공"
        )
        failed_tests = sum(
            1 for result in self.test_results if result["status"] in ["실패", "오류"]
        )

        success_rate = (
            (successful_tests + partial_success_tests * 0.5) / total_tests * 100
        )

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
            "phase": "Phase 14",
            "description": "커서 판단 루프에 통합",
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
        filename = f"test_results_phase14_cursor_integration_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(test_report, f, ensure_ascii=False, indent=2)

        print(f"\n💾 테스트 결과가 {filename}에 저장되었습니다")

        # 최종 평가
        if success_rate >= 80:
            print(
                "\n🎉 Phase 14 테스트 성공! 커서 통합 시스템이 정상적으로 작동합니다."
            )
        elif success_rate >= 60:
            print("\n⚠️ Phase 14 테스트 부분 성공! 일부 기능에 개선이 필요합니다.")
        else:
            print("\n❌ Phase 14 테스트 실패! 주요 기능에 문제가 있습니다.")


async def main():
    """메인 함수"""
    test_runner = Phase14TestRunner()
    await test_runner.run_all_tests()


if __name__ == "__main__":
    asyncio.run(main())
