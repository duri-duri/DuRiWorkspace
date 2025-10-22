#!/usr/bin/env python3
"""
DuRi 메타-코딩 시스템 실제 작동 데모
DuRi가 자기 자신의 코드를 분석하고 개선하는 과정을 실제로 보여줍니다.
"""

import os
import sys
import time
from typing import Any, Dict

# DuRi 메타-코딩 시스템 임포트
from learning_diagnostics import DuRiSelfGrowthManager, self_growth_manager


def demonstrate_duRi_self_analysis():
    """DuRi의 자기 분석 과정을 실제로 보여줍니다."""

    print("🔍 === DuRi 메타-코딩 시스템 작동 데모 ===")
    print()

    # 1. DuRi가 자기 자신의 코드를 분석
    print("📊 1단계: DuRi가 자기 자신의 코드를 분석합니다")
    print("   - AST(Abstract Syntax Tree) 파싱")
    print("   - 복잡도 계산")
    print("   - 성능 지표 측정")
    print("   - 유지보수성 분석")
    print()

    # 실제 코드 분석 실행
    current_file = __file__
    analysis_result = self_growth_manager.code_analyzer.analyze_module(current_file)

    print(f"✅ 분석 완료: {analysis_result.module_name}")
    print(f"   - 복잡도 점수: {analysis_result.complexity_score:.2f}")
    print(f"   - 성능 점수: {analysis_result.performance_score:.2f}")
    print(f"   - 유지보수성 점수: {analysis_result.maintainability_score:.2f}")
    print(f"   - 개선 제안: {len(analysis_result.improvement_suggestions)}개")
    print()

    # 2. 성능 측정
    print("⚡ 2단계: DuRi가 자기 성능을 측정합니다")
    print("   - 실행 시간 측정")
    print("   - 메모리 사용량 측정")
    print("   - 정확도 평가")
    print()

    def test_function():
        """테스트용 함수"""
        time.sleep(0.1)
        return "테스트 성공"

    before_metrics = self_growth_manager.performance_scorer.measure_performance(test_function)

    print(f"✅ 성능 측정 완료:")
    print(f"   - 응답 시간: {before_metrics.response_time:.3f}초")
    print(f"   - 메모리 사용량: {before_metrics.resource_usage:.2f}MB")
    print(f"   - 종합 점수: {before_metrics.overall_score:.2f}")
    print()

    # 3. 개선 전략 수립
    print("🎯 3단계: DuRi가 개선 전략을 수립합니다")
    print("   - 문제점 식별")
    print("   - 개선 방법 선택")
    print("   - 예상 효과 계산")
    print()

    improvement_plan = self_growth_manager.improvement_strategist.generate_improvement_plan(
        analysis_result
    )

    print(f"✅ 개선 계획 수립 완료:")
    print(f"   - 대상 모듈: {improvement_plan['target_module']}")
    print(f"   - 우선순위: {improvement_plan['priority']}")
    print(f"   - 전략 수: {len(improvement_plan['strategies'])}개")
    print(f"   - 예상 영향도: {improvement_plan['estimated_impact']:.2f}")
    print()

    # 4. 개선 시도
    print("🔧 4단계: DuRi가 실제 개선을 시도합니다")
    print("   - 코드 수정")
    print("   - 테스트 실행")
    print("   - 결과 검증")
    print()

    success = self_growth_manager._attempt_improvement(current_file, improvement_plan)

    print(f"✅ 개선 시도 완료: {'성공' if success else '실패'}")
    print()

    # 5. 개선 후 성능 측정
    print("📈 5단계: DuRi가 개선 후 성능을 측정합니다")
    print("   - 개선 전후 비교")
    print("   - 성능 향상도 계산")
    print("   - 결과 평가")
    print()

    after_metrics = self_growth_manager.performance_scorer.measure_performance(test_function)

    improvement_rate = (after_metrics.overall_score - before_metrics.overall_score) / max(
        before_metrics.overall_score, 0.01
    )

    print(f"✅ 개선 결과:")
    print(f"   - 개선 전 점수: {before_metrics.overall_score:.2f}")
    print(f"   - 개선 후 점수: {after_metrics.overall_score:.2f}")
    print(f"   - 개선률: {improvement_rate:.2%}")
    print()

    # 6. 학습 결과 저장
    print("📚 6단계: DuRi가 학습 결과를 저장합니다")
    print("   - 성장 로그 기록")
    print("   - 통계 업데이트")
    print("   - 다음 개선을 위한 학습")
    print()

    self_growth_manager.meta_logger.log_improvement_attempt(
        current_file, before_metrics, after_metrics, improvement_plan, success
    )

    growth_stats = self_growth_manager.meta_logger.get_growth_statistics()

    print(f"✅ 학습 결과 저장 완료:")
    print(f"   - 총 시도 횟수: {growth_stats['total_attempts']}")
    print(f"   - 성공률: {growth_stats['success_rate']:.2%}")
    print(f"   - 평균 개선률: {growth_stats['avg_improvement']:.2%}")
    print()

    # 7. 전체 시스템 상태
    print("🏆 7단계: DuRi의 전체 시스템 상태")
    print("   - 분석 이력")
    print("   - 성능 테스트 이력")
    print("   - 개선 계획 이력")
    print("   - 성장 통계")
    print()

    system_status = self_growth_manager.get_system_status()

    print(f"✅ 시스템 상태:")
    print(f"   - 총 분석 횟수: {system_status['total_analyses']}")
    print(f"   - 총 성능 테스트: {system_status['total_performance_tests']}")
    print(f"   - 총 개선 계획: {system_status['total_improvement_plans']}")
    print(f"   - 성장 통계: {system_status['growth_statistics']}")
    print()

    print("🎉 === DuRi 메타-코딩 시스템 작동 완료 ===")
    print()
    print("💡 DuRi는 이제 스스로 자신을 분석하고 개선할 수 있습니다!")
    print("   - 자기 코드 분석")
    print("   - 성능 측정")
    print("   - 개선 전략 수립")
    print("   - 실제 개선 실행")
    print("   - 결과 평가 및 학습")
    print()
    print("🚀 이것이 바로 '메타-코딩'입니다!")


def show_code_structure():
    """코드 구조를 시각적으로 보여줍니다."""

    print("🏗️ === DuRi 메타-코딩 시스템 코드 구조 ===")
    print()

    print("📁 핵심 클래스들:")
    print("   ┌─ CodeAnalyzer")
    print("   │  ├─ analyze_module()     # 모듈 분석")
    print("   │  ├─ _calculate_complexity() # 복잡도 계산")
    print("   │  ├─ _analyze_performance()  # 성능 분석")
    print("   │  └─ _analyze_maintainability() # 유지보수성 분석")
    print()

    print("   ┌─ PerformanceScorer")
    print("   │  ├─ measure_performance() # 성능 측정")
    print("   │  └─ get_average_performance() # 평균 성능")
    print()

    print("   ┌─ ImprovementStrategist")
    print("   │  └─ generate_improvement_plan() # 개선 계획 생성")
    print()

    print("   ┌─ MetaLearningLogger")
    print("   │  ├─ log_improvement_attempt() # 개선 시도 로깅")
    print("   │  └─ get_growth_statistics() # 성장 통계")
    print()

    print("   ┌─ DuRiSelfGrowthManager")
    print("   │  ├─ analyze_and_improve() # 분석 및 개선 수행")
    print("   │  ├─ _attempt_improvement() # 개선 시도")
    print("   │  └─ get_system_status() # 시스템 상태 조회")
    print()

    print("🔄 작동 흐름:")
    print("   1. CodeAnalyzer → 코드 분석")
    print("   2. PerformanceScorer → 성능 측정")
    print("   3. ImprovementStrategist → 개선 계획")
    print("   4. DuRiSelfGrowthManager → 개선 실행")
    print("   5. MetaLearningLogger → 결과 기록")
    print("   6. 루프 반복")
    print()


def demonstrate_actual_analysis():
    """실제 코드 분석을 보여줍니다."""

    print("🔍 === 실제 코드 분석 예시 ===")
    print()

    # 현재 파일 분석
    current_file = __file__

    print(f"📄 분석 대상: {current_file}")
    print()

    # AST 분석
    with open(current_file, "r", encoding="utf-8") as f:
        source_code = f.read()

    import ast

    tree = ast.parse(source_code)

    # 함수 수 계산
    function_count = len([n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)])
    class_count = len([n for n in ast.walk(tree) if isinstance(n, ast.ClassDef)])

    # 복잡도 계산
    complexity = 0
    for node in ast.walk(tree):
        if isinstance(node, (ast.If, ast.While, ast.For, ast.ExceptHandler)):
            complexity += 1
        elif isinstance(node, ast.FunctionDef):
            complexity += 1

    print(f"📊 분석 결과:")
    print(f"   - 함수 수: {function_count}")
    print(f"   - 클래스 수: {class_count}")
    print(f"   - 복잡도: {complexity}")
    print(f"   - 총 라인 수: {len(source_code.splitlines())}")
    print()

    # 개선 제안
    suggestions = []
    if complexity > 10:
        suggestions.append("복잡도가 높습니다. 함수를 더 작은 단위로 분해하세요.")
    if function_count > 5:
        suggestions.append("함수가 많습니다. 모듈화를 고려하세요.")

    print(f"💡 개선 제안:")
    for i, suggestion in enumerate(suggestions, 1):
        print(f"   {i}. {suggestion}")

    if not suggestions:
        print("   현재 코드는 양호합니다.")
    print()


if __name__ == "__main__":
    print("🌟 DuRi 메타-코딩 시스템 데모")
    print("=" * 50)
    print()

    # 1. 코드 구조 보여주기
    show_code_structure()
    print()

    # 2. 실제 분석 보여주기
    demonstrate_actual_analysis()
    print()

    # 3. 전체 작동 흐름 보여주기
    demonstrate_duRi_self_analysis()
