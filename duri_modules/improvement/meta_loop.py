#!/usr/bin/env python3
"""
메타 루프 시스템 - 개선 결과 재평가 및 학습 효과 측정
"""

from datetime import datetime
from typing import Any, Dict


class MetaLoopSystem:
    """개선 결과를 다시 평가하는 메타 루프 시스템"""

    def __init__(self):
        self.meta_evaluation_history = []
        self.improvement_tracking = {}

    def evaluate_improvement_effect(
        self,
        original_response: str,
        improved_response: str,
        user_question: str,
        original_evaluation: Dict[str, Any],
    ) -> Dict[str, Any]:
        """개선 효과 평가"""

        print("🔄 메타 루프: 개선 효과 평가 시작")

        # 개선된 응답에 대한 새로운 평가
        from ..evaluation.evaluator import chatgpt_evaluator

        new_evaluation = chatgpt_evaluator.evaluate_response(improved_response, user_question)

        # 개선 효과 분석
        improvement_analysis = self._analyze_improvement_effect(original_evaluation, new_evaluation)

        # 메타 평가 결과
        meta_result = {
            "timestamp": datetime.now().isoformat(),
            "original_evaluation": original_evaluation,
            "new_evaluation": new_evaluation,
            "improvement_analysis": improvement_analysis,
            "meta_score": improvement_analysis.get("overall_improvement", 0.0),
        }

        # 메타 평가 기록 저장
        self.meta_evaluation_history.append(meta_result)

        print("✅ 메타 루프: 개선 효과 평가 완료")
        print(f"   📈 전체 개선도: {improvement_analysis.get('overall_improvement', 0):.3f}")
        print(f"   🎯 개선된 영역: {len(improvement_analysis.get('improved_dimensions', []))}개")

        return meta_result

    def _analyze_improvement_effect(self, original_eval: Dict[str, Any], new_eval: Dict[str, Any]) -> Dict[str, Any]:
        """개선 효과 분석"""

        original_scores = original_eval.get("scores", {})
        new_scores = new_eval.get("scores", {})

        # 각 차원별 개선도 계산
        dimension_improvements = {}
        improved_dimensions = []
        declined_dimensions = []

        for dimension in original_scores:
            original_score = original_scores.get(dimension, 0)
            new_score = new_scores.get(dimension, 0)
            improvement = new_score - original_score

            dimension_improvements[dimension] = {
                "original": original_score,
                "new": new_score,
                "improvement": improvement,
                "improvement_percentage": ((improvement / original_score * 100) if original_score > 0 else 0),
            }

            if improvement > 0:
                improved_dimensions.append(dimension)
            elif improvement < 0:
                declined_dimensions.append(dimension)

        # 전체 개선도 계산
        total_original = sum(original_scores.values())
        total_new = sum(new_scores.values())
        overall_improvement = (total_new - total_original) / len(original_scores) if original_scores else 0

        # 개선 성공 여부 판단
        improvement_success = overall_improvement > 0.1  # 10% 이상 개선

        return {
            "dimension_improvements": dimension_improvements,
            "improved_dimensions": improved_dimensions,
            "declined_dimensions": declined_dimensions,
            "overall_improvement": overall_improvement,
            "improvement_success": improvement_success,
            "total_original_score": total_original,
            "total_new_score": total_new,
        }

    def generate_improvement_feedback(self, meta_result: Dict[str, Any]) -> Dict[str, Any]:
        """개선 피드백 생성"""

        analysis = meta_result.get("improvement_analysis", {})

        feedback = {
            "timestamp": datetime.now().isoformat(),
            "improvement_success": analysis.get("improvement_success", False),
            "overall_improvement": analysis.get("overall_improvement", 0),
            "recommendations": [],
            "lessons_learned": [],
        }

        # 개선 성공 시
        if analysis.get("improvement_success", False):
            feedback["recommendations"].append("개선이 성공적으로 이루어졌습니다. 이 패턴을 학습에 반영하세요.")
            feedback["lessons_learned"].append("이번 개선 방법이 효과적이었습니다.")
        else:
            feedback["recommendations"].append("개선이 기대에 미치지 못했습니다. 다른 접근 방법을 시도해보세요.")
            feedback["lessons_learned"].append("이번 개선 방법은 효과적이지 않았습니다.")

        # 개선된 영역 분석
        improved_dims = analysis.get("improved_dimensions", [])
        if improved_dims:
            feedback["recommendations"].append(f"다음 영역에서 개선이 확인되었습니다: {', '.join(improved_dims)}")

        # 악화된 영역 분석
        declined_dims = analysis.get("declined_dimensions", [])
        if declined_dims:
            feedback["recommendations"].append(f"다음 영역에서 악화가 확인되었습니다: {', '.join(declined_dims)}")

        return feedback

    def get_meta_learning_statistics(self) -> Dict[str, Any]:
        """메타 학습 통계"""

        if not self.meta_evaluation_history:
            return {"total_meta_evaluations": 0, "success_rate": 0.0}

        total_evaluations = len(self.meta_evaluation_history)
        successful_improvements = sum(
            1
            for result in self.meta_evaluation_history
            if result.get("improvement_analysis", {}).get("improvement_success", False)
        )

        success_rate = successful_improvements / total_evaluations if total_evaluations > 0 else 0

        # 평균 개선도
        avg_improvement = (
            sum(
                result.get("improvement_analysis", {}).get("overall_improvement", 0)
                for result in self.meta_evaluation_history
            )
            / total_evaluations
            if total_evaluations > 0
            else 0
        )

        return {
            "total_meta_evaluations": total_evaluations,
            "successful_improvements": successful_improvements,
            "success_rate": success_rate,
            "average_improvement": avg_improvement,
            "recent_meta_evaluations": self.meta_evaluation_history[-5:],  # 최근 5개
        }


# 모듈 인스턴스 생성
meta_loop_system = MetaLoopSystem()
