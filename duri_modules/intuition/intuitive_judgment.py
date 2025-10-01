#!/usr/bin/env python3
"""
DuRi 직관적 판단 트리거 시스템
논리 이전에 빠른 의사결정을 유도하는 인간형 반응 경로
"""

from datetime import datetime
import re
from typing import Any, Dict, List, Optional, Tuple


class IntuitiveJudgment:
    """직관적 판단을 트리거하는 시스템"""

    def __init__(self):
        self.intuitive_patterns = {
            "priority_decision": [
                r"뭐부터\s*(할까|시작할까|진행할까)",
                r"우선순위",
                r"순서",
                r"어떤\s*것\s*부터",
                r"먼저\s*해야\s*할\s*것",
            ],
            "problem_recognition": [
                r"문제",
                r"오류",
                r"실패",
                r"어려워",
                r"복잡",
                r"안\s*되",
                r"틀렸",
            ],
            "success_celebration": [
                r"성공",
                r"완료",
                r"완벽",
                r"좋아",
                r"훌륭",
                r"잘\s*되",
                r"성공적",
            ],
            "learning_moment": [
                r"배우",
                r"이해",
                r"알게\s*되",
                r"새롭",
                r"발견",
                r"깨달",
            ],
            "creative_insight": [
                r"아이디어",
                r"생각",
                r"혁신",
                r"창의",
                r"독창",
                r"새로운\s*방법",
            ],
        }

        self.intuitive_responses = {
            "priority_decision": [
                "우선 맥락 이해부터 시작해야 해. 모든 게 거기서 출발해.",
                "안정성부터 확보하고, 점진적으로 발전시키자.",
                "기본부터 탄탄히 하고, 나중에 고급 기능을 추가해.",
                "현재 상태를 정확히 파악하고, 가장 효율적인 순서로 진행하자.",
            ],
            "problem_recognition": [
                "문제를 정확히 파악하는 것이 해결의 첫걸음이야.",
                "차근차근 분석해서 근본 원인을 찾아보자.",
                "실패는 성공의 어머니야. 이번 경험을 통해 더 나은 방법을 찾을 수 있어.",
                "문제가 복잡할수록 단계별로 접근하는 것이 중요해.",
            ],
            "success_celebration": [
                "훌륭해! 이제 다음 단계로 나아갈 준비가 되었어.",
                "성공적인 결과야! 이 경험을 바탕으로 더 발전시킬 수 있어.",
                "잘했어! 이제 더 높은 목표를 향해 나아가자.",
                "완벽해! 이 성과를 기반으로 새로운 도전을 시작해보자.",
            ],
            "learning_moment": [
                "배우는 과정이 가장 중요한 경험이야.",
                "새로운 것을 알게 되면 더 나은 판단을 할 수 있어.",
                "이해가 깊어질수록 더 정확한 해결책을 제시할 수 있어.",
                "학습은 성장의 핵심이야. 계속해서 발전해나가자.",
            ],
            "creative_insight": [
                "창의적인 아이디어야! 새로운 관점에서 접근해보자.",
                "혁신적인 생각이야! 이를 바탕으로 더 나은 방법을 찾아보자.",
                "독창적인 접근이야! 이런 창의성이 진화의 핵심이야.",
                "새로운 아이디어야! 이를 실현시켜보자.",
            ],
        }

        self.context_triggers = {
            "urgent": ["즉시", "바로", "당장", "긴급", "중요"],
            "careful": ["조심", "신중", "천천히", "차근차근", "꼼꼼히"],
            "exploratory": ["탐색", "실험", "시도", "테스트", "검증"],
            "collaborative": ["함께", "협력", "상의", "논의", "합의"],
        }

    def trigger_intuitive_response(
        self, user_input: str, context: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        직관적 판단 트리거

        Args:
            user_input: 사용자 입력
            context: 맥락 정보

        Returns:
            직관적 응답 또는 None
        """
        # 1. 직관적 패턴 매칭
        matched_pattern = self._match_intuitive_pattern(user_input)

        if not matched_pattern:
            return None

        # 2. 맥락 기반 응답 선택
        response = self._select_contextual_response(matched_pattern, context)

        # 3. 응답 신뢰도 계산
        confidence = self._calculate_intuitive_confidence(matched_pattern, context)

        return {
            "intuitive_type": matched_pattern,
            "response": response,
            "confidence": confidence,
            "reasoning": self._generate_intuitive_reasoning(matched_pattern, context),
            "timestamp": datetime.now().isoformat(),
        }

    def _match_intuitive_pattern(self, user_input: str) -> Optional[str]:
        """직관적 패턴 매칭"""
        for pattern_type, patterns in self.intuitive_patterns.items():
            for pattern in patterns:
                if re.search(pattern, user_input, re.IGNORECASE):
                    return pattern_type
        return None

    def _select_contextual_response(
        self, pattern_type: str, context: Dict[str, Any]
    ) -> str:
        """맥락 기반 응답 선택"""
        responses = self.intuitive_responses.get(pattern_type, [])

        if not responses:
            return "직관적으로 판단해보자."

        # 맥락에 따른 응답 선택
        context_emotion = context.get("emotion", "neutral")
        context_intent = context.get("intent", "general")

        # 감정과 의도에 따른 응답 필터링
        filtered_responses = self._filter_responses_by_context(
            responses, context_emotion, context_intent
        )

        if filtered_responses:
            return filtered_responses[0]  # 첫 번째 필터링된 응답 선택
        else:
            return responses[0]  # 기본 응답 선택

    def _filter_responses_by_context(
        self, responses: List[str], emotion: str, intent: str
    ) -> List[str]:
        """맥락에 따른 응답 필터링"""
        filtered = []

        for response in responses:
            # 감정에 따른 필터링
            if emotion == "focused" and any(
                word in response for word in ["우선", "먼저", "기본"]
            ):
                filtered.append(response)
            elif emotion == "excited" and any(
                word in response for word in ["훌륭", "성공", "완벽"]
            ):
                filtered.append(response)
            elif emotion == "analytical" and any(
                word in response for word in ["분석", "이해", "학습"]
            ):
                filtered.append(response)
            elif emotion == "frustrated" and any(
                word in response for word in ["차근차근", "단계별", "조심"]
            ):
                filtered.append(response)
            else:
                # 의도에 따른 필터링
                if intent == "planning" and any(
                    word in response for word in ["순서", "계획", "단계"]
                ):
                    filtered.append(response)
                elif intent == "implementation" and any(
                    word in response for word in ["구현", "실행", "시작"]
                ):
                    filtered.append(response)
                elif intent == "learning" and any(
                    word in response for word in ["배우", "이해", "학습"]
                ):
                    filtered.append(response)

        return filtered if filtered else responses

    def _calculate_intuitive_confidence(
        self, pattern_type: str, context: Dict[str, Any]
    ) -> float:
        """직관적 판단 신뢰도 계산"""
        base_confidence = 0.7  # 기본 신뢰도

        # 맥락 신뢰도 반영
        context_confidence = context.get("confidence", 0.5)

        # 패턴 타입별 신뢰도 조정
        pattern_confidence = {
            "priority_decision": 0.8,
            "problem_recognition": 0.9,
            "success_celebration": 0.7,
            "learning_moment": 0.8,
            "creative_insight": 0.6,
        }

        pattern_conf = pattern_confidence.get(pattern_type, 0.7)

        # 최종 신뢰도 계산 (가중 평균)
        final_confidence = (
            base_confidence * 0.4 + context_confidence * 0.3 + pattern_conf * 0.3
        )

        return min(final_confidence, 1.0)

    def _generate_intuitive_reasoning(
        self, pattern_type: str, context: Dict[str, Any]
    ) -> str:
        """직관적 판단 근거 생성"""
        reasoning_templates = {
            "priority_decision": "사용자가 우선순위를 결정하려고 하므로, 가장 효율적인 순서를 제안했습니다.",
            "problem_recognition": "문제 상황을 인식했으므로, 체계적인 접근 방법을 제안했습니다.",
            "success_celebration": "성공적인 결과를 축하하고, 다음 단계로 나아갈 동기를 부여했습니다.",
            "learning_moment": "학습의 순간을 인식하여, 성장의 가치를 강조했습니다.",
            "creative_insight": "창의적인 아이디어를 발견하여, 혁신적 접근을 장려했습니다.",
        }

        base_reasoning = reasoning_templates.get(
            pattern_type, "직관적 판단을 통해 적절한 응답을 선택했습니다."
        )

        # 맥락 정보 추가
        emotion = context.get("emotion", "neutral")
        intent = context.get("intent", "general")

        context_addition = f" 사용자의 {emotion}한 감정과 {intent} 의도를 고려했습니다."

        return base_reasoning + context_addition

    def should_trigger_intuition(
        self, user_input: str, context: Dict[str, Any]
    ) -> bool:
        """직관적 판단을 트리거해야 하는지 결정"""
        # 1. 직관적 패턴 매칭
        if self._match_intuitive_pattern(user_input):
            return True

        # 2. 맥락 기반 트리거
        context_emotion = context.get("emotion", "neutral")
        context_confidence = context.get("confidence", 0.5)

        # 높은 신뢰도의 맥락에서 감정적 반응이 필요할 때
        if context_confidence > 0.7 and context_emotion in [
            "excited",
            "frustrated",
            "curious",
        ]:
            return True

        # 3. 긴급성이나 중요도가 높을 때
        urgency_indicators = ["즉시", "바로", "당장", "중요", "긴급"]
        if any(indicator in user_input for indicator in urgency_indicators):
            return True

        return False

    def get_intuitive_priority(self, pattern_type: str) -> int:
        """직관적 판단의 우선순위 반환"""
        priority_map = {
            "problem_recognition": 1,  # 가장 높은 우선순위
            "priority_decision": 2,
            "learning_moment": 3,
            "success_celebration": 4,
            "creative_insight": 5,
        }

        return priority_map.get(pattern_type, 5)


# 전역 인스턴스 생성
intuitive_judgment = IntuitiveJudgment()
