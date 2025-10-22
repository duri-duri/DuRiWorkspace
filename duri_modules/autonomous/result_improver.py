import json
import logging
import os
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


@dataclass
class ImprovementAction:
    action_type: str  # 'code_change', 'structure_change', 'content_addition'
    target_file: Optional[str]
    description: str
    priority: str  # 'high', 'medium', 'low'
    estimated_effort: str  # 'quick', 'medium', 'complex'
    implementation_guide: List[str]


@dataclass
class CodeImprovement:
    file_path: str
    original_code: str
    improved_code: str
    changes: List[str]
    reasoning: str
    confidence: float


class ResultImprover:
    def __init__(self):
        self.improvement_history = []
        self.successful_improvements = []
        self.failed_improvements = []

        logger.info("🔧 DuRi 결과 개선 시스템 초기화 완료")

    def analyze_improvement_suggestions(
        self, evaluation_result: Dict[str, Any]
    ) -> List[ImprovementAction]:
        """평가 결과에서 개선 제안을 분석하여 실행 가능한 액션으로 변환"""
        try:
            actions = []

            # ChatGPT 평가에서 개선 제안 추출
            chatgpt_eval = evaluation_result.get("evaluation", {}).get("chatgpt_evaluation", {})
            suggestions = chatgpt_eval.get("suggestions", [])

            # 자기성찰에서 개선 제안 추출
            self_reflection = evaluation_result.get("evaluation", {}).get("self_reflection", {})
            improvement_proposal = self_reflection.get("improvement_proposal", {})

            # ChatGPT 제안을 액션으로 변환
            for suggestion in suggestions:
                action = self._convert_suggestion_to_action(suggestion, "chatgpt")
                if action:
                    actions.append(action)

            # 자기성찰 제안을 액션으로 변환
            specific_improvements = improvement_proposal.get("specific_improvements", [])
            for improvement in specific_improvements:
                action = self._convert_suggestion_to_action(improvement, "self_reflection")
                if action:
                    actions.append(action)

            # 우선순위 정렬
            actions.sort(key=lambda x: self._get_priority_score(x.priority), reverse=True)

            logger.info(f"📋 개선 액션 생성 완료: {len(actions)}개")
            return actions

        except Exception as e:
            logger.error(f"❌ 개선 제안 분석 오류: {e}")
            return []

    def _convert_suggestion_to_action(
        self, suggestion: str, source: str
    ) -> Optional[ImprovementAction]:
        """개선 제안을 실행 가능한 액션으로 변환"""
        try:
            # 제안 유형 분류
            if "코드" in suggestion or "code" in suggestion.lower():
                return ImprovementAction(
                    action_type="code_change",
                    target_file=None,
                    description=suggestion,
                    priority="high",
                    estimated_effort="medium",
                    implementation_guide=[
                        "코드 예제 추가",
                        "구체적인 구현 방법 제시",
                        "에러 처리 포함",
                    ],
                )
            elif "구조" in suggestion or "structure" in suggestion.lower():
                return ImprovementAction(
                    action_type="structure_change",
                    target_file=None,
                    description=suggestion,
                    priority="medium",
                    estimated_effort="quick",
                    implementation_guide=[
                        "단계별 번호 매기기",
                        "중요 포인트 강조",
                        "논리적 순서 정리",
                    ],
                )
            elif "설명" in suggestion or "explanation" in suggestion.lower():
                return ImprovementAction(
                    action_type="content_addition",
                    target_file=None,
                    description=suggestion,
                    priority="medium",
                    estimated_effort="quick",
                    implementation_guide=[
                        "이유와 근거 추가",
                        "배경 정보 제공",
                        "실용적 예시 포함",
                    ],
                )
            else:
                return ImprovementAction(
                    action_type="content_addition",
                    target_file=None,
                    description=suggestion,
                    priority="low",
                    estimated_effort="quick",
                    implementation_guide=["일반적인 개선 적용", "사용자 피드백 반영"],
                )

        except Exception as e:
            logger.error(f"❌ 제안 변환 오류: {e}")
            return None

    def _get_priority_score(self, priority: str) -> int:
        """우선순위 점수 계산"""
        priority_map = {"high": 3, "medium": 2, "low": 1}
        return priority_map.get(priority, 1)

    def execute_improvement_action(
        self, action: ImprovementAction, context: Dict[str, Any]
    ) -> bool:
        """개선 액션 실행"""
        try:
            logger.info(f"🔧 개선 액션 실행: {action.action_type} - {action.description}")

            if action.action_type == "code_change":
                return self._execute_code_change(action, context)
            elif action.action_type == "structure_change":
                return self._execute_structure_change(action, context)
            elif action.action_type == "content_addition":
                return self._execute_content_addition(action, context)
            else:
                logger.warning(f"⚠️ 알 수 없는 액션 타입: {action.action_type}")
                return False

        except Exception as e:
            logger.error(f"❌ 개선 액션 실행 오류: {e}")
            return False

    def _execute_code_change(self, action: ImprovementAction, context: Dict[str, Any]) -> bool:
        """코드 변경 실행"""
        try:
            # 코드 예제 생성
            example_code = self._generate_code_example(action.description, context)

            # 개선된 응답 생성
            improved_response = self._improve_response_with_code(
                context.get("original_response", ""), example_code
            )

            # 결과 저장
            improvement = CodeImprovement(
                file_path="improved_response.txt",
                original_code=context.get("original_response", ""),
                improved_code=improved_response,
                changes=[f"코드 예제 추가: {action.description}"],
                reasoning="사용자 요청에 대한 구체적인 코드 예제 제공",
                confidence=0.8,
            )

            self.successful_improvements.append(improvement)
            logger.info(f"✅ 코드 변경 완료: {action.description}")
            return True

        except Exception as e:
            logger.error(f"❌ 코드 변경 오류: {e}")
            return False

    def _execute_structure_change(self, action: ImprovementAction, context: Dict[str, Any]) -> bool:
        """구조 변경 실행"""
        try:
            # 구조화된 응답 생성
            structured_response = self._structure_response(context.get("original_response", ""))

            improvement = CodeImprovement(
                file_path="structured_response.txt",
                original_code=context.get("original_response", ""),
                improved_code=structured_response,
                changes=[f"구조 개선: {action.description}"],
                reasoning="단계별 구조화된 설명 제공",
                confidence=0.7,
            )

            self.successful_improvements.append(improvement)
            logger.info(f"✅ 구조 변경 완료: {action.description}")
            return True

        except Exception as e:
            logger.error(f"❌ 구조 변경 오류: {e}")
            return False

    def _execute_content_addition(self, action: ImprovementAction, context: Dict[str, Any]) -> bool:
        """내용 추가 실행"""
        try:
            # 개선된 내용 생성
            enhanced_response = self._enhance_response(
                context.get("original_response", ""), action.description
            )

            improvement = CodeImprovement(
                file_path="enhanced_response.txt",
                original_code=context.get("original_response", ""),
                improved_code=enhanced_response,
                changes=[f"내용 개선: {action.description}"],
                reasoning="더 상세하고 유용한 설명 제공",
                confidence=0.6,
            )

            self.successful_improvements.append(improvement)
            logger.info(f"✅ 내용 추가 완료: {action.description}")
            return True

        except Exception as e:
            logger.error(f"❌ 내용 추가 오류: {e}")
            return False

    def _generate_code_example(self, description: str, context: Dict[str, Any]) -> str:
        """코드 예제 생성"""
        # 간단한 코드 예제 템플릿
        code_template = f"""
# {description}
def example_implementation():
    \"\"\"
    {description}에 대한 예제 구현
    \"\"\"
    try:
        # 기본 구현
        result = "성공적인 구현"
        print(f"결과: {{result}}")
        return result
    except Exception as e:
        print(f"오류 발생: {{e}}")
        return None

# 사용 예제
if __name__ == "__main__":
    example_implementation()
"""
        return code_template

    def _improve_response_with_code(self, original_response: str, code_example: str) -> str:
        """코드 예제를 포함한 개선된 응답 생성"""
        improved = f"{original_response}\n\n## 코드 예제\n```python\n{code_example}\n```\n\n이 예제를 참고하여 실제 프로젝트에 적용해보세요."
        return improved

    def _structure_response(self, original_response: str) -> str:
        """구조화된 응답 생성"""
        structured = f"""## 개요
{original_response}

## 단계별 가이드
1. **첫 번째 단계**: 기본 설정
2. **두 번째 단계**: 핵심 기능 구현
3. **세 번째 단계**: 테스트 및 검증

## 중요 포인트
- 핵심 개념 이해
- 실용적 적용
- 지속적 개선

## 다음 단계
구체적인 구현을 통해 학습을 완성하세요."""
        return structured

    def _enhance_response(self, original_response: str, improvement: str) -> str:
        """응답 내용 개선"""
        enhanced = f"{original_response}\n\n## 개선 사항\n{improvement}\n\n## 추가 설명\n이 개선사항을 통해 더 나은 결과를 얻을 수 있습니다."
        return enhanced

    def get_improvement_summary(self) -> Dict[str, Any]:
        """개선 결과 요약"""
        return {
            "total_improvements": len(self.successful_improvements) + len(self.failed_improvements),
            "successful_improvements": len(self.successful_improvements),
            "failed_improvements": len(self.failed_improvements),
            "success_rate": len(self.successful_improvements)
            / max(1, len(self.successful_improvements) + len(self.failed_improvements)),
            "recent_improvements": [
                {
                    "type": imp.changes[0] if imp.changes else "unknown",
                    "confidence": imp.confidence,
                    "reasoning": imp.reasoning,
                }
                for imp in self.successful_improvements[-5:]  # 최근 5개
            ],
        }
