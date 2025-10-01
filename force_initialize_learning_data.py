#!/usr/bin/env python3
"""
DuRi 강제 초기 학습 데이터 주입 스크립트

기존 데이터가 있어도 강제로 초기 학습 데이터를 주입합니다.
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


class ForceLearningDataInitializer:
    """강제 학습 데이터 초기화 클래스"""

    def __init__(self):
        """초기화"""
        self.memory_sync = get_memory_sync()
        self.auto_retrospector = get_auto_retrospector()

        # 초기 데이터 설정
        self.initial_data_count = 30  # 총 30개의 초기 데이터
        self.success_ratio = 0.7  # 70% 성공, 30% 실패

        logger.info("📊 강제 학습 데이터 초기화 시스템 시작")

    def generate_force_initial_experiences(self) -> List[Dict[str, Any]]:
        """강제 초기 경험 데이터 생성"""
        experiences = []

        # 성공 케이스들 (더 다양한 타입)
        success_cases = [
            {
                "source": "system_bootstrap",
                "context": "DuRi 시스템 기동",
                "outcome": "success",
                "details": "학습 시스템 정상 활성화",
                "confidence": 0.95,
                "learning_value": 0.8,
                "experience_type": "system_initialization",
            },
            {
                "source": "memory_initialization",
                "context": "메모리 시스템 초기화",
                "outcome": "success",
                "details": "경험 데이터 저장 시스템 정상 작동",
                "confidence": 0.9,
                "learning_value": 0.7,
                "experience_type": "memory_management",
            },
            {
                "source": "autonomous_learning",
                "context": "자율 학습 모듈 활성화",
                "outcome": "success",
                "details": "24/7 자동 학습 시스템 시작",
                "confidence": 0.85,
                "learning_value": 0.75,
                "experience_type": "autonomous_learning",
            },
            {
                "source": "meta_learning",
                "context": "메타 학습 분석",
                "outcome": "success",
                "details": "학습 패턴 분석 및 개선안 생성",
                "confidence": 0.8,
                "learning_value": 0.6,
                "experience_type": "meta_learning",
            },
            {
                "source": "realtime_learning",
                "context": "실시간 학습",
                "outcome": "success",
                "details": "즉시 반응 학습 시스템 정상 작동",
                "confidence": 0.9,
                "learning_value": 0.8,
                "experience_type": "realtime_learning",
            },
            {
                "source": "strategy_optimization",
                "context": "전략 최적화",
                "outcome": "success",
                "details": "학습 전략 자동 조정 성공",
                "confidence": 0.75,
                "learning_value": 0.65,
                "experience_type": "strategy_optimization",
            },
            {
                "source": "performance_monitoring",
                "context": "성능 모니터링",
                "outcome": "success",
                "details": "시스템 성능 추적 및 최적화",
                "confidence": 0.85,
                "learning_value": 0.7,
                "experience_type": "performance_monitoring",
            },
            {
                "source": "error_recovery",
                "context": "오류 복구",
                "outcome": "success",
                "details": "시스템 오류 자동 복구 성공",
                "confidence": 0.8,
                "learning_value": 0.75,
                "experience_type": "error_recovery",
            },
            {
                "source": "knowledge_integration",
                "context": "지식 통합",
                "outcome": "success",
                "details": "새로운 지식 기존 지식과 통합",
                "confidence": 0.9,
                "learning_value": 0.8,
                "experience_type": "knowledge_integration",
            },
            {
                "source": "adaptive_learning",
                "context": "적응적 학습",
                "outcome": "success",
                "details": "환경 변화에 따른 학습 방법 자동 조정",
                "confidence": 0.85,
                "learning_value": 0.7,
                "experience_type": "adaptive_learning",
            },
            {
                "source": "pattern_recognition",
                "context": "패턴 인식",
                "outcome": "success",
                "details": "학습 패턴 자동 인식 및 활용",
                "confidence": 0.8,
                "learning_value": 0.65,
                "experience_type": "pattern_recognition",
            },
            {
                "source": "goal_achievement",
                "context": "목표 달성",
                "outcome": "success",
                "details": "학습 목표 설정 및 달성",
                "confidence": 0.9,
                "learning_value": 0.8,
                "experience_type": "goal_achievement",
            },
            {
                "source": "emotional_judgment",
                "context": "감정적 판단",
                "outcome": "success",
                "details": "감정적 맥락에서의 판단 성공",
                "confidence": 0.75,
                "learning_value": 0.6,
                "experience_type": "emotional_judgment",
            },
            {
                "source": "ethical_judgment",
                "context": "윤리적 판단",
                "outcome": "success",
                "details": "윤리적 원칙에 따른 판단 성공",
                "confidence": 0.8,
                "learning_value": 0.7,
                "experience_type": "ethical_judgment",
            },
            {
                "source": "creativity_session",
                "context": "창의성 세션",
                "outcome": "success",
                "details": "창의적 아이디어 생성 성공",
                "confidence": 0.7,
                "learning_value": 0.6,
                "experience_type": "creativity_session",
            },
            {
                "source": "autonomous_goal",
                "context": "자율 목표 설정",
                "outcome": "success",
                "details": "자율적으로 목표 설정 및 달성",
                "confidence": 0.85,
                "learning_value": 0.75,
                "experience_type": "autonomous_goal",
            },
            {
                "source": "meta_reflection",
                "context": "메타 반성",
                "outcome": "success",
                "details": "자기 학습 과정에 대한 반성 성공",
                "confidence": 0.8,
                "learning_value": 0.7,
                "experience_type": "meta_reflection",
            },
            {
                "source": "strategy_evolution",
                "context": "전략 진화",
                "outcome": "success",
                "details": "학습 전략의 진화적 개선 성공",
                "confidence": 0.75,
                "learning_value": 0.65,
                "experience_type": "strategy_evolution",
            },
            {
                "source": "system_optimization",
                "context": "시스템 최적화",
                "outcome": "success",
                "details": "전체 시스템 성능 최적화 성공",
                "confidence": 0.9,
                "learning_value": 0.8,
                "experience_type": "system_optimization",
            },
            {
                "source": "learning_breakthrough",
                "context": "학습 돌파구",
                "outcome": "success",
                "details": "새로운 학습 방법 발견 및 적용",
                "confidence": 0.85,
                "learning_value": 0.75,
                "experience_type": "learning_breakthrough",
            },
        ]

        # 실패 케이스들 (더 다양한 타입)
        failure_cases = [
            {
                "source": "initial_learning_attempt",
                "context": "초기 학습 시도",
                "outcome": "failure",
                "details": "학습 데이터 부족으로 인한 초기 실패",
                "confidence": 0.3,
                "learning_value": 0.5,
                "experience_type": "learning_attempt",
            },
            {
                "source": "memory_overflow",
                "context": "메모리 오버플로우",
                "outcome": "failure",
                "details": "대용량 데이터 처리 중 메모리 부족",
                "confidence": 0.4,
                "learning_value": 0.6,
                "experience_type": "memory_management",
            },
            {
                "source": "pattern_mismatch",
                "context": "패턴 불일치",
                "outcome": "failure",
                "details": "예상과 다른 패턴으로 인한 학습 실패",
                "confidence": 0.5,
                "learning_value": 0.7,
                "experience_type": "pattern_recognition",
            },
            {
                "source": "resource_constraint",
                "context": "리소스 제약",
                "outcome": "failure",
                "details": "시스템 리소스 부족으로 인한 학습 중단",
                "confidence": 0.6,
                "learning_value": 0.65,
                "experience_type": "resource_management",
            },
            {
                "source": "timeout_error",
                "context": "타임아웃 오류",
                "outcome": "failure",
                "details": "학습 프로세스 시간 초과",
                "confidence": 0.4,
                "learning_value": 0.55,
                "experience_type": "performance_monitoring",
            },
            {
                "source": "data_corruption",
                "context": "데이터 손상",
                "outcome": "failure",
                "details": "학습 데이터 손상으로 인한 실패",
                "confidence": 0.3,
                "learning_value": 0.5,
                "experience_type": "data_management",
            },
            {
                "source": "algorithm_error",
                "context": "알고리즘 오류",
                "outcome": "failure",
                "details": "학습 알고리즘 내부 오류",
                "confidence": 0.5,
                "learning_value": 0.6,
                "experience_type": "algorithm_learning",
            },
            {
                "source": "inconsistent_state",
                "context": "일관성 없는 상태",
                "outcome": "failure",
                "details": "시스템 상태 불일치로 인한 학습 실패",
                "confidence": 0.4,
                "learning_value": 0.55,
                "experience_type": "system_health",
            },
            {
                "source": "emotional_conflict",
                "context": "감정적 갈등",
                "outcome": "failure",
                "details": "감정적 판단 과정에서의 갈등 발생",
                "confidence": 0.6,
                "learning_value": 0.7,
                "experience_type": "emotional_judgment",
            },
            {
                "source": "ethical_dilemma",
                "context": "윤리적 딜레마",
                "outcome": "failure",
                "details": "윤리적 판단 과정에서의 딜레마 발생",
                "confidence": 0.5,
                "learning_value": 0.65,
                "experience_type": "ethical_judgment",
            },
        ]

        # 성공/실패 비율에 따라 데이터 선택
        success_count = int(self.initial_data_count * self.success_ratio)
        failure_count = self.initial_data_count - success_count

        # 성공 케이스 선택
        selected_success = random.sample(
            success_cases, min(success_count, len(success_cases))
        )
        experiences.extend(selected_success)

        # 실패 케이스 선택
        selected_failure = random.sample(
            failure_cases, min(failure_count, len(failure_cases))
        )
        experiences.extend(selected_failure)

        # 시간대 분산을 위한 타임스탬프 추가
        base_time = datetime.now() - timedelta(days=14)  # 2주일 전부터
        for i, experience in enumerate(experiences):
            experience["timestamp"] = (base_time + timedelta(hours=i * 3)).isoformat()
            experience["session_id"] = f"force_initial_session_{i:03d}"

        return experiences

    def force_inject_initial_data(self) -> Dict[str, Any]:
        """강제 초기 데이터 주입"""
        try:
            logger.info("📥 강제 초기 학습 데이터 주입 시작")

            # 기존 데이터 확인
            existing_experiences = self.memory_sync.get_recent_experiences(limit=100)
            logger.info(f"기존 경험 데이터 수: {len(existing_experiences)}개")

            # 강제 초기 데이터 생성
            initial_experiences = self.generate_force_initial_experiences()

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

            logger.info(f"✅ 강제 초기 데이터 주입 완료: {injected_count}개")
            logger.info(
                f"📊 강제 초기 분석 결과 - 성공률: {analysis_result.get('success_rate', 0):.2%}"
            )

            return {
                "status": "success",
                "injected_count": injected_count,
                "analysis_result": analysis_result,
                "message": f"{injected_count}개의 강제 초기 학습 데이터 주입 완료",
            }

        except Exception as e:
            logger.error(f"강제 초기 데이터 주입 중 오류: {e}")
            return {
                "status": "error",
                "message": f"강제 초기 데이터 주입 실패: {e}",
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
                success_count = sum(
                    1 for e in experiences if e.get("outcome") == "success"
                )
                learning_rate = success_count / len(experiences)
            else:
                learning_rate = 0.0

            # 종합 분석 실행
            analysis_result = self.auto_retrospector.run_comprehensive_analysis()

            return {
                "experience_count": experience_count,
                "learning_rate": learning_rate,
                "analysis_result": analysis_result,
                "system_ready": experience_count >= 20 and learning_rate > 0.0,
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
    print("🚀 DuRi 강제 초기 학습 데이터 주입 시작")

    initializer = ForceLearningDataInitializer()

    # 강제 초기 데이터 주입
    result = initializer.force_inject_initial_data()

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

    print("\n✅ 강제 초기화 완료")


if __name__ == "__main__":
    main()
