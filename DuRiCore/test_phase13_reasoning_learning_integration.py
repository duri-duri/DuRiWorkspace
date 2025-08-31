#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DuRi Phase 13: Reasoning + Learning 통합 실행 흐름 테스트

Phase 13에서 구현된 reasoning + learning 통합 시스템의 
기능과 성능을 검증하는 테스트 스크립트
"""

import asyncio
import json
import time
import logging
from datetime import datetime
from typing import Dict, List, Any

# 테스트 대상 모듈 import
try:
    from phase13_reasoning_learning_integration import (
        ReasoningLearningIntegrationSystem,
        IntegrationResult,
        IntegrationPhase,
        IntegrationStatus
    )
except ImportError as e:
    logging.error(f"Phase 13 모듈 import 실패: {e}")
    exit(1)

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class Phase13TestRunner:
    """Phase 13 테스트 실행기"""
    
    def __init__(self):
        self.test_results = []
        self.integration_system = None
        self.test_start_time = None
        
    async def run_all_tests(self) -> Dict[str, Any]:
        """모든 테스트 실행"""
        logger.info("🚀 Phase 13 테스트 시작")
        
        self.test_start_time = time.time()
        
        # 시스템 초기화
        self.integration_system = ReasoningLearningIntegrationSystem()
        
        # 테스트 실행
        test_results = {
            "test_system_initialization": await self.test_system_initialization(),
            "test_reasoning_learning_integration": await self.test_reasoning_learning_integration(),
            "test_feedback_loop": await self.test_feedback_loop(),
            "test_optimization": await self.test_optimization(),
            "test_performance_metrics": await self.test_performance_metrics(),
            "test_error_handling": await self.test_error_handling()
        }
        
        # 전체 결과 종합
        total_tests = len(test_results)
        passed_tests = sum(1 for result in test_results.values() if result.get("success", False))
        
        overall_result = {
            "phase": "Phase 13",
            "description": "Reasoning + Learning 통합 실행 흐름 구성",
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "failed_tests": total_tests - passed_tests,
            "success_rate": (passed_tests / total_tests) * 100 if total_tests > 0 else 0,
            "test_results": test_results,
            "execution_time": time.time() - self.test_start_time,
            "timestamp": datetime.now().isoformat()
        }
        
        logger.info(f"✅ Phase 13 테스트 완료: {passed_tests}/{total_tests} 성공")
        return overall_result
    
    async def test_system_initialization(self) -> Dict[str, Any]:
        """시스템 초기화 테스트"""
        logger.info("🧪 시스템 초기화 테스트 시작")
        
        try:
            # 시스템 초기화
            success = await self.integration_system.initialize_systems()
            
            if success:
                logger.info("✅ 시스템 초기화 성공")
                return {
                    "test_name": "시스템 초기화",
                    "success": True,
                    "message": "모든 시스템이 성공적으로 초기화되었습니다"
                }
            else:
                logger.error("❌ 시스템 초기화 실패")
                return {
                    "test_name": "시스템 초기화",
                    "success": False,
                    "message": "시스템 초기화에 실패했습니다"
                }
                
        except Exception as e:
            logger.error(f"❌ 시스템 초기화 테스트 실패: {e}")
            return {
                "test_name": "시스템 초기화",
                "success": False,
                "message": f"시스템 초기화 테스트 중 오류 발생: {str(e)}"
            }
    
    async def test_reasoning_learning_integration(self) -> Dict[str, Any]:
        """Reasoning + Learning 통합 테스트"""
        logger.info("🧪 Reasoning + Learning 통합 테스트 시작")
        
        try:
            # 테스트 데이터
            test_input = {
                "query": "복잡한 문제 해결을 위한 추론과 학습 통합 테스트",
                "context": "통합 시스템 테스트",
                "parameters": {
                    "complexity": "high",
                    "priority": "critical"
                }
            }
            
            test_context = {
                "user_id": "test_user",
                "session_id": "test_session",
                "resource_constraints": {
                    "memory_limit": "1GB",
                    "time_limit": "30s"
                }
            }
            
            # 통합 실행 흐름 실행
            result = await self.integration_system.execute_integration_flow(test_input, test_context)
            
            # 결과 검증
            if result.success:
                logger.info("✅ Reasoning + Learning 통합 성공")
                return {
                    "test_name": "Reasoning + Learning 통합",
                    "success": True,
                    "message": "통합 실행 흐름이 성공적으로 완료되었습니다",
                    "details": {
                        "reasoning_quality": result.reasoning_quality,
                        "learning_effectiveness": result.learning_effectiveness,
                        "integration_score": result.integration_score,
                        "execution_time": result.execution_time,
                        "feedback_loop_count": result.feedback_loop_count,
                        "optimization_applied": result.optimization_applied
                    }
                }
            else:
                logger.error(f"❌ Reasoning + Learning 통합 실패: {result.error_message}")
                return {
                    "test_name": "Reasoning + Learning 통합",
                    "success": False,
                    "message": f"통합 실행 흐름 실패: {result.error_message}"
                }
                
        except Exception as e:
            logger.error(f"❌ Reasoning + Learning 통합 테스트 실패: {e}")
            return {
                "test_name": "Reasoning + Learning 통합",
                "success": False,
                "message": f"통합 테스트 중 오류 발생: {str(e)}"
            }
    
    async def test_feedback_loop(self) -> Dict[str, Any]:
        """피드백 루프 테스트"""
        logger.info("🧪 피드백 루프 테스트 시작")
        
        try:
            # 테스트 데이터
            test_input = {
                "query": "피드백 루프 테스트",
                "context": "피드백 테스트",
                "parameters": {
                    "enable_feedback": True,
                    "max_iterations": 3
                }
            }
            
            test_context = {
                "user_id": "test_user",
                "session_id": "feedback_test_session"
            }
            
            # 통합 실행 흐름 실행
            result = await self.integration_system.execute_integration_flow(test_input, test_context)
            
            # 피드백 루프 검증
            if result.success and result.feedback_loop_count > 0:
                logger.info("✅ 피드백 루프 성공")
                return {
                    "test_name": "피드백 루프",
                    "success": True,
                    "message": "피드백 루프가 성공적으로 작동했습니다",
                    "details": {
                        "feedback_loop_count": result.feedback_loop_count,
                        "integration_score": result.integration_score
                    }
                }
            else:
                logger.warning("⚠️ 피드백 루프가 작동하지 않았습니다")
                return {
                    "test_name": "피드백 루프",
                    "success": False,
                    "message": "피드백 루프가 작동하지 않았습니다"
                }
                
        except Exception as e:
            logger.error(f"❌ 피드백 루프 테스트 실패: {e}")
            return {
                "test_name": "피드백 루프",
                "success": False,
                "message": f"피드백 루프 테스트 중 오류 발생: {str(e)}"
            }
    
    async def test_optimization(self) -> Dict[str, Any]:
        """최적화 테스트"""
        logger.info("🧪 최적화 테스트 시작")
        
        try:
            # 테스트 데이터
            test_input = {
                "query": "최적화 테스트",
                "context": "최적화 테스트",
                "parameters": {
                    "enable_optimization": True,
                    "optimization_threshold": 0.7
                }
            }
            
            test_context = {
                "user_id": "test_user",
                "session_id": "optimization_test_session"
            }
            
            # 통합 실행 흐름 실행
            result = await self.integration_system.execute_integration_flow(test_input, test_context)
            
            # 최적화 검증
            if result.success and result.optimization_applied:
                logger.info("✅ 최적화 성공")
                return {
                    "test_name": "최적화",
                    "success": True,
                    "message": "최적화가 성공적으로 적용되었습니다",
                    "details": {
                        "optimization_applied": result.optimization_applied,
                        "integration_score": result.integration_score
                    }
                }
            else:
                logger.warning("⚠️ 최적화가 적용되지 않았습니다")
                return {
                    "test_name": "최적화",
                    "success": False,
                    "message": "최적화가 적용되지 않았습니다"
                }
                
        except Exception as e:
            logger.error(f"❌ 최적화 테스트 실패: {e}")
            return {
                "test_name": "최적화",
                "success": False,
                "message": f"최적화 테스트 중 오류 발생: {str(e)}"
            }
    
    async def test_performance_metrics(self) -> Dict[str, Any]:
        """성능 메트릭 테스트"""
        logger.info("🧪 성능 메트릭 테스트 시작")
        
        try:
            # 성능 메트릭 가져오기
            metrics = self.integration_system.get_performance_metrics()
            
            # 메트릭 검증
            if metrics and "total_sessions" in metrics:
                logger.info("✅ 성능 메트릭 성공")
                return {
                    "test_name": "성능 메트릭",
                    "success": True,
                    "message": "성능 메트릭이 성공적으로 수집되었습니다",
                    "details": metrics
                }
            else:
                logger.error("❌ 성능 메트릭 수집 실패")
                return {
                    "test_name": "성능 메트릭",
                    "success": False,
                    "message": "성능 메트릭 수집에 실패했습니다"
                }
                
        except Exception as e:
            logger.error(f"❌ 성능 메트릭 테스트 실패: {e}")
            return {
                "test_name": "성능 메트릭",
                "success": False,
                "message": f"성능 메트릭 테스트 중 오류 발생: {str(e)}"
            }
    
    async def test_error_handling(self) -> Dict[str, Any]:
        """에러 처리 테스트"""
        logger.info("🧪 에러 처리 테스트 시작")
        
        try:
            # 잘못된 입력으로 테스트
            invalid_input = None
            invalid_context = {}
            
            # 통합 실행 흐름 실행
            result = await self.integration_system.execute_integration_flow(invalid_input, invalid_context)
            
            # 에러 처리 검증
            if not result.success and result.error_message:
                logger.info("✅ 에러 처리 성공")
                return {
                    "test_name": "에러 처리",
                    "success": True,
                    "message": "에러가 적절히 처리되었습니다",
                    "details": {
                        "error_message": result.error_message
                    }
                }
            else:
                logger.warning("⚠️ 에러 처리가 예상대로 작동하지 않았습니다")
                return {
                    "test_name": "에러 처리",
                    "success": False,
                    "message": "에러 처리가 예상대로 작동하지 않았습니다"
                }
                
        except Exception as e:
            logger.error(f"❌ 에러 처리 테스트 실패: {e}")
            return {
                "test_name": "에러 처리",
                "success": False,
                "message": f"에러 처리 테스트 중 오류 발생: {str(e)}"
            }

async def main():
    """메인 테스트 실행 함수"""
    logger.info("🚀 Phase 13 테스트 실행기 시작")
    
    # 테스트 실행기 생성
    test_runner = Phase13TestRunner()
    
    # 모든 테스트 실행
    results = await test_runner.run_all_tests()
    
    # 결과 출력
    print("\n" + "="*80)
    print("📊 Phase 13 테스트 결과")
    print("="*80)
    print(f"🎯 Phase: {results['phase']}")
    print(f"📝 설명: {results['description']}")
    print(f"📈 성공률: {results['success_rate']:.1f}% ({results['passed_tests']}/{results['total_tests']})")
    print(f"⏱️ 실행 시간: {results['execution_time']:.3f}초")
    print(f"🕒 타임스탬프: {results['timestamp']}")
    
    print("\n📋 상세 결과:")
    print("-"*80)
    
    for test_name, test_result in results['test_results'].items():
        status = "✅ 성공" if test_result.get('success', False) else "❌ 실패"
        print(f"{status} - {test_result.get('test_name', test_name)}")
        if test_result.get('message'):
            print(f"    📝 {test_result['message']}")
        if test_result.get('details'):
            print(f"    📊 {test_result['details']}")
        print()
    
    # 결과 저장
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"test_results_phase13_reasoning_learning_integration_{timestamp}.json"
    
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2, default=str)
        print(f"💾 테스트 결과가 {filename}에 저장되었습니다")
    except Exception as e:
        logger.error(f"❌ 결과 저장 실패: {e}")
    
    print("="*80)
    
    # 성공 여부 반환
    return results['success_rate'] >= 80.0

if __name__ == "__main__":
    # 테스트 실행
    success = asyncio.run(main())
    
    if success:
        print("🎉 Phase 13 테스트가 성공적으로 완료되었습니다!")
        exit(0)
    else:
        print("⚠️ Phase 13 테스트에서 일부 실패가 발생했습니다.")
        exit(1)


