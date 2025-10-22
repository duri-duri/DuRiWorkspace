#!/usr/bin/env python3
"""
DuRi 초기 학습 데이터 주입 스크립트

학습 시스템이 의미 있는 평가를 할 수 있도록
성공/실패 케이스를 혼합한 초기 데이터를 주입합니다.
"""

import logging
import random
from datetime import datetime, timedelta
from typing import Any, Dict, List

from duri_brain.learning.auto_retrospector import get_auto_retrospector
# DuRi 모듈 import
from duri_core.memory.memory_sync import get_memory_sync

# 로깅 설정
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class LearningDataInitializer:
    """학습 데이터 초기화 클래스"""

    def __init__(self):
        """초기화"""
        self.memory_sync = get_memory_sync()
        self.auto_retrospector = get_auto_retrospector()

        # 초기 데이터 설정
        self.initial_data_count = 20  # 총 20개의 초기 데이터
        self.success_ratio = 0.6  # 60% 성공, 40% 실패

        logger.info("📊 학습 데이터 초기화 시스템 시작")

    def generate_initial_experiences(self) -> List[Dict[str, Any]]:
        """초기 경험 데이터 생성"""
        experiences = []

        # 성공 케이스들
        success_cases = [
            {
                "source": "system_bootstrap",
                "context": "DuRi 시스템 기동",
                "outcome": "success",
                "details": "학습 시스템 정상 활성화",
                "confidence": 0.95,
                "learning_value": 0.8,
            },
            {
                "source": "memory_initialization",
                "context": "메모리 시스템 초기화",
                "outcome": "success",
                "details": "경험 데이터 저장 시스템 정상 작동",
                "confidence": 0.9,
                "learning_value": 0.7,
            },
            {
                "source": "autonomous_learning",
                "context": "자율 학습 모듈 활성화",
                "outcome": "success",
                "details": "24/7 자동 학습 시스템 시작",
                "confidence": 0.85,
                "learning_value": 0.75,
            },
            {
                "source": "meta_learning",
                "context": "메타 학습 분석",
                "outcome": "success",
                "details": "학습 패턴 분석 및 개선안 생성",
                "confidence": 0.8,
                "learning_value": 0.6,
            },
            {
                "source": "realtime_learning",
                "context": "실시간 학습",
                "outcome": "success",
                "details": "즉시 반응 학습 시스템 정상 작동",
                "confidence": 0.9,
                "learning_value": 0.8,
            },
            {
                "source": "strategy_optimization",
                "context": "전략 최적화",
                "outcome": "success",
                "details": "학습 전략 자동 조정 성공",
                "confidence": 0.75,
                "learning_value": 0.65,
            },
            {
                "source": "performance_monitoring",
                "context": "성능 모니터링",
                "outcome": "success",
                "details": "시스템 성능 추적 및 최적화",
                "confidence": 0.85,
                "learning_value": 0.7,
            },
            {
                "source": "error_recovery",
                "context": "오류 복구",
                "outcome": "success",
                "details": "시스템 오류 자동 복구 성공",
                "confidence": 0.8,
                "learning_value": 0.75,
            },
            {
                "source": "knowledge_integration",
                "context": "지식 통합",
                "outcome": "success",
                "details": "새로운 지식 기존 지식과 통합",
                "confidence": 0.9,
                "learning_value": 0.8,
            },
            {
                "source": "adaptive_learning",
                "context": "적응적 학습",
                "outcome": "success",
                "details": "환경 변화에 따른 학습 방법 자동 조정",
                "confidence": 0.85,
                "learning_value": 0.7,
            },
            {
                "source": "pattern_recognition",
                "context": "패턴 인식",
                "outcome": "success",
                "details": "학습 패턴 자동 인식 및 활용",
                "confidence": 0.8,
                "learning_value": 0.65,
            },
            {
                "source": "goal_achievement",
                "context": "목표 달성",
                "outcome": "success",
                "details": "학습 목표 설정 및 달성",
                "confidence": 0.9,
                "learning_value": 0.8,
            },
        ]

        # 실패 케이스들
        failure_cases = [
            {
                "source": "initial_learning_attempt",
                "context": "초기 학습 시도",
                "outcome": "failure",
                "details": "학습 데이터 부족으로 인한 초기 실패",
                "confidence": 0.3,
                "learning_value": 0.5,
            },
            {
                "source": "memory_overflow",
                "context": "메모리 오버플로우",
                "outcome": "failure",
                "details": "대용량 데이터 처리 중 메모리 부족",
                "confidence": 0.4,
                "learning_value": 0.6,
            },
            {
                "source": "pattern_mismatch",
                "context": "패턴 불일치",
                "outcome": "failure",
                "details": "예상과 다른 패턴으로 인한 학습 실패",
                "confidence": 0.5,
                "learning_value": 0.7,
            },
            {
                "source": "resource_constraint",
                "context": "리소스 제약",
                "outcome": "failure",
                "details": "시스템 리소스 부족으로 인한 학습 중단",
                "confidence": 0.6,
                "learning_value": 0.65,
            },
            {
                "source": "timeout_error",
                "context": "타임아웃 오류",
                "outcome": "failure",
                "details": "학습 프로세스 시간 초과",
                "confidence": 0.4,
                "learning_value": 0.55,
            },
            {
                "source": "data_corruption",
                "context": "데이터 손상",
                "outcome": "failure",
                "details": "학습 데이터 손상으로 인한 실패",
                "confidence": 0.3,
                "learning_value": 0.5,
            },
            {
                "source": "algorithm_error",
                "context": "알고리즘 오류",
                "outcome": "failure",
                "details": "학습 알고리즘 내부 오류",
                "confidence": 0.5,
                "learning_value": 0.6,
            },
            {
                "source": "inconsistent_state",
                "context": "일관성 없는 상태",
                "outcome": "failure",
                "details": "시스템 상태 불일치로 인한 학습 실패",
                "confidence": 0.4,
                "learning_value": 0.55,
            },
        ]

        # 성공/실패 비율에 따라 데이터 선택
        success_count = int(self.initial_data_count * self.success_ratio)
        failure_count = self.initial_data_count - success_count

        # 성공 케이스 선택
        selected_success = random.sample(success_cases, min(success_count, len(success_cases)))
        experiences.extend(selected_success)

        # 실패 케이스 선택
        selected_failure = random.sample(failure_cases, min(failure_count, len(failure_cases)))
        experiences.extend(selected_failure)

        # 시간대 분산을 위한 타임스탬프 추가
        base_time = datetime.now() - timedelta(days=7)  # 1주일 전부터
        for i, experience in enumerate(experiences):
            experience["timestamp"] = (base_time + timedelta(hours=i * 2)).isoformat()
            experience["session_id"] = f"initial_session_{i:03d}"

        return experiences

    def inject_initial_data(self) -> Dict[str, Any]:
        """초기 데이터 주입"""
        try:
            logger.info("📥 초기 학습 데이터 주입 시작")

            # 기존 데이터 확인
            existing_experiences = self.memory_sync.get_recent_experiences(limit=50)
            if len(existing_experiences) > 10:
                logger.warning(f"이미 {len(existing_experiences)}개의 경험 데이터가 존재합니다.")
                return {
                    "status": "warning",
                    "message": f"이미 {len(existing_experiences)}개의 경험 데이터가 존재합니다.",
                    "injected_count": 0,
                }

            # 초기 데이터 생성
            initial_experiences = self.generate_initial_experiences()

            # 메모리에 저장
            injected_count = 0
            for experience in initial_experiences:
                try:
                    self.memory_sync.save_experience(experience)
                    injected_count += 1
                except Exception as e:
                    logger.error(f"경험 데이터 저장 실패: {e}")

            # 종합 분석 실행
            analysis_result = self.auto_retrospector.run_comprehensive_analysis()

            logger.info(f"✅ 초기 데이터 주입 완료: {injected_count}개")
            logger.info(f"📊 초기 분석 결과 - 성공률: {analysis_result.get('success_rate', 0):.2%}")

            return {
                "status": "success",
                "injected_count": injected_count,
                "analysis_result": analysis_result,
                "message": f"{injected_count}개의 초기 학습 데이터 주입 완료",
            }

        except Exception as e:
            logger.error(f"초기 데이터 주입 중 오류: {e}")
            return {
                "status": "error",
                "message": f"초기 데이터 주입 실패: {e}",
                "injected_count": 0,
            }

    def verify_learning_system(self) -> Dict[str, Any]:
        """학습 시스템 검증"""
        try:
            # 경험 데이터 확인
            experiences = self.memory_sync.get_recent_experiences(limit=100)
            experience_count = len(experiences)

            # 학습률 계산
            if experiences:
                success_count = sum(1 for e in experiences if e.get("outcome") == "success")
                learning_rate = success_count / len(experiences)
            else:
                learning_rate = 0.0

            # 종합 분석 실행
            analysis_result = self.auto_retrospector.run_comprehensive_analysis()

            return {
                "experience_count": experience_count,
                "learning_rate": learning_rate,
                "analysis_result": analysis_result,
                "system_ready": experience_count >= 10 and learning_rate > 0.0,
            }

        except Exception as e:
            logger.error(f"학습 시스템 검증 중 오류: {e}")
            return {
                "experience_count": 0,
                "learning_rate": 0.0,
                "analysis_result": {},
                "system_ready": False,
            }


def main():
    """메인 함수"""
    print("🚀 DuRi 초기 학습 데이터 주입 시작")

    initializer = LearningDataInitializer()

    # 초기 데이터 주입
    result = initializer.inject_initial_data()

    print(f"\n📊 주입 결과:")
    print(f"  상태: {result['status']}")
    print(f"  주입된 데이터 수: {result['injected_count']}개")
    print(f"  메시지: {result['message']}")

    if result["status"] == "success":
        # 학습 시스템 검증
        verification = initializer.verify_learning_system()

        print(f"\n🔍 시스템 검증 결과:")
        print(f"  경험 데이터 수: {verification['experience_count']}개")
        print(f"  학습률: {verification['learning_rate']:.2%}")
        print(f"  시스템 준비 완료: {'✅' if verification['system_ready'] else '❌'}")

        if verification["system_ready"]:
            print("\n🎉 학습 시스템이 준비되었습니다!")
            print("이제 24/7 자가 학습을 시작할 수 있습니다.")
        else:
            print("\n⚠️ 학습 시스템이 아직 준비되지 않았습니다.")
            print("추가 데이터 주입이 필요할 수 있습니다.")

    print("\n✅ 초기화 완료")


if __name__ == "__main__":
    main()
