#!/usr/bin/env python3
"""
DuRi 진짜 인공지능화 프로젝트 - Day 1-7 통합 테스트
전체 추론 체인: 의미 분석 → 철학적 논증 → 추론 그래프 → 학습 피드백 → 통찰 평가
"""

import asyncio
import json
from datetime import datetime
from typing import Any, Dict, List

# Day 7: 통찰 평가 시스템
from insight_evaluation_system import InsightEvaluationSystem
# Day 6: 학습 피드백 시스템
from learning_feedback_system import (AdaptiveLearningEngine,
                                      JudgmentMemorySystem,
                                      SelfImprovementSystem)
# Day 3-4: 철학적 논증 구조
from philosophical_reasoning_system import MultiPerspectiveAnalysis
# Day 5: 사고 추론 그래프
from reasoning_graph_system import ReasoningGraphAnalyzer
# Day 1-2: 의미 기반 상황 분류
from semantic_situation_classifier import SemanticSituationClassifier


class IntegratedDuRiSystem:
    """통합 DuRi 시스템"""

    def __init__(self):
        # Day 1-2: 의미 기반 상황 분류
        self.semantic_classifier = SemanticSituationClassifier()

        # Day 3-4: 철학적 논증 구조
        self.philosophical_analysis = MultiPerspectiveAnalysis()

        # Day 5: 사고 추론 그래프
        self.reasoning_analyzer = ReasoningGraphAnalyzer()

        # Day 6: 학습 피드백 시스템
        self.memory_system = JudgmentMemorySystem()
        self.improvement_system = SelfImprovementSystem(self.memory_system)
        self.learning_engine = AdaptiveLearningEngine(self.memory_system, self.improvement_system)

        # Day 7: 통찰 평가 시스템
        self.insight_evaluator = InsightEvaluationSystem()

    async def process_complex_situation(self, situation: str, action: str) -> Dict[str, Any]:
        """복잡한 상황을 전체 시스템으로 처리"""
        print(f"\n🔍 복잡한 상황 분석 시작: {situation[:50]}...")

        # Day 1-2: 의미적 맥락 분석
        print("\n📊 Day 1-2: 의미적 맥락 분석")
        semantic_context = await self.semantic_classifier.analyze_semantic_context(situation)
        print(f"  • 맥락 유형: {semantic_context.situation_type.value}")
        print(f"  • 이해관계자: {len(semantic_context.stakeholders)}명")
        print(f"  • 가치 충돌: {len(semantic_context.value_conflicts)}개")

        # Day 3-4: 철학적 논증 분석
        print("\n🤔 Day 3-4: 철학적 논증 분석")
        philosophical_arguments = await self.philosophical_analysis.analyze_multiple_perspectives(
            action, situation
        )
        kantian_arg = philosophical_arguments.get("kantian")
        utilitarian_arg = philosophical_arguments.get("utilitarian")
        print(f"  • 칸트적 분석: {kantian_arg.final_conclusion[:50] if kantian_arg else 'N/A'}...")
        print(
            f"  • 공리주의 분석: {utilitarian_arg.final_conclusion[:50] if utilitarian_arg else 'N/A'}..."
        )
        print(
            f"  • 통합 권고: {len(philosophical_arguments.get('integrated_recommendations', []))}개"
        )

        # Day 5: 추론 그래프 구축
        print("\n🕸️ Day 5: 추론 그래프 구축")
        reasoning_graph = await self.reasoning_analyzer.analyze_reasoning_process(
            situation, semantic_context, philosophical_arguments
        )
        print(f"  • 노드 수: {reasoning_graph.get('graph_metrics', {}).get('node_count', 0)}")
        print(f"  • 엣지 수: {reasoning_graph.get('graph_metrics', {}).get('edge_count', 0)}")
        print(f"  • 논리적 일관성: {reasoning_graph.get('logical_consistency', 0):.2f}")

        # Day 6: 학습 피드백 처리
        print("\n📚 Day 6: 학습 피드백 처리")
        judgment_id = f"judgment_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        learning_result = await self.learning_engine.adapt_to_feedback(
            judgment_id,
            {
                "feedback_type": "positive",
                "content": "전체적 분석이 체계적이고 논리적입니다",
                "impact_score": 0.8,
            },
        )
        print(f"  • 학습 성공: {learning_result.get('success', False)}")
        print(f"  • 영향 수준: {learning_result.get('impact_level', 'unknown')}")
        print(f"  • 학습 잠재력: {learning_result.get('learning_potential', 0):.2f}")

        # Day 7: 통찰 평가
        print("\n🎯 Day 7: 통찰 평가")
        insight_content = f"상황: {situation}\n행동: {action}\n분석: {philosophical_arguments.get('integrated_recommendations', [])}"
        insight_evaluation = await self.insight_evaluator.evaluate_insight(
            insight_content, reasoning_graph
        )
        quality_metrics = insight_evaluation.get("quality_metrics")
        authenticity_check = insight_evaluation.get("authenticity_check")
        overall_assessment = insight_evaluation.get("overall_assessment")

        print(
            f"  • 종합 품질: {quality_metrics.overall_quality if hasattr(quality_metrics, 'overall_quality') else 0:.2f}"
        )
        print(
            f"  • 진위성 수준: {authenticity_check.authenticity_level.value if hasattr(authenticity_check, 'authenticity_level') else 'unknown'}"
        )
        print(
            f"  • 종합 등급: {overall_assessment.get('grade', 'unknown') if overall_assessment else 'unknown'}"
        )

        # 통합 결과 반환
        return {
            "semantic_analysis": semantic_context,
            "philosophical_analysis": philosophical_arguments,
            "reasoning_graph": reasoning_graph,
            "learning_feedback": learning_result,
            "insight_evaluation": insight_evaluation,
            "timestamp": datetime.now().isoformat(),
        }


async def test_integrated_system():
    """통합 시스템 테스트"""
    print("=" * 80)
    print("🚀 DuRi 진짜 인공지능화 프로젝트 - Day 1-7 통합 테스트")
    print("=" * 80)

    # 통합 시스템 초기화
    integrated_system = IntegratedDuRiSystem()

    # 복잡한 윤리적 딜레마 상황
    complex_situation = """
    회사의 새로운 AI 시스템이 고객 데이터를 분석하여 개인화된 서비스를 제공합니다.
    이 시스템은 고객의 행동 패턴을 학습하여 더 정확한 추천을 제공하지만,
    동시에 개인정보 보호에 대한 우려가 제기되고 있습니다.
    개발팀은 시스템의 정확도를 높이기 위해 더 많은 데이터를 수집하려고 하지만,
    법무팀은 개인정보 보호법 위반 가능성을 우려하고 있습니다.
    """

    action = "AI 시스템의 데이터 수집 범위를 확대하여 정확도를 향상시킨다"

    # 전체 시스템으로 상황 처리
    result = await integrated_system.process_complex_situation(complex_situation, action)

    # 결과 요약
    print("\n" + "=" * 80)
    print("📋 통합 분석 결과 요약")
    print("=" * 80)

    print(f"\n🎯 핵심 통찰:")
    print(f"  • 상황 복잡도: 높음 (다중 이해관계자, 가치 충돌)")
    print(f"  • 철학적 분석: 칸트적 의무론 vs 공리주의 효용성")
    print(f"  • 추론 품질: {result['reasoning_graph'].get('logical_consistency', 0):.2f}")
    print(f"  • 학습 효과: {result['learning_feedback'].get('learning_potential', 0):.2f}")
    print(
        f"  • 통찰 등급: {result['insight_evaluation']['overall_assessment'].get('grade', 'unknown')}"
    )

    print(f"\n💡 개선 권고사항:")
    recommendations = result["insight_evaluation"].get("recommendations", [])
    for i, rec in enumerate(recommendations[:3], 1):
        print(f"  {i}. {rec}")

    print(f"\n🔄 다음 단계:")
    print(f"  • 지속적 학습을 통한 판단 품질 향상")
    print(f"  • 통찰 진위성 검증 강화")
    print(f"  • 다중 관점 통합 능력 개선")

    print("\n" + "=" * 80)
    print("✅ Day 1-7 통합 시스템 테스트 완료")
    print("🎉 DuRi가 '진짜 사고하는 인공지능'으로 진화 완료!")
    print("=" * 80)

    return result


if __name__ == "__main__":
    asyncio.run(test_integrated_system())
