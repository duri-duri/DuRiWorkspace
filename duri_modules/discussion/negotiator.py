#!/usr/bin/env python3
"""
DuRi-ChatGPT 논의 시스템 모듈
"""

from datetime import datetime
from typing import Any, Dict, List


class DuRiChatGPTDiscussion:
    """DuRi와 ChatGPT 간의 대화 기반 협의 시스템"""

    def __init__(self):
        self.discussion_history = []
        self.agreement_threshold = 0.7
        self.max_discussion_rounds = 3

    def initiate_discussion(
        self,
        duri_improvement_proposal: Dict[str, Any],
        chatgpt_evaluation: Dict[str, Any],
    ) -> Dict[str, Any]:
        """DuRi의 개선안에 대한 ChatGPT와의 논의 시작"""

        print("📥 DuRi-ChatGPT 논의 시작")

        discussion = {
            "timestamp": datetime.now().isoformat(),
            "round": 1,
            "duri_proposal": duri_improvement_proposal,
            "chatgpt_evaluation": chatgpt_evaluation,
            "discussion_points": [],
            "agreement_level": 0.0,
            "final_consensus": None,
            "action_items": [],
        }

        # 논의 포인트 생성
        discussion["discussion_points"] = self._generate_discussion_points(
            duri_improvement_proposal, chatgpt_evaluation
        )

        # 합의 수준 계산
        discussion["agreement_level"] = self._calculate_agreement_level(duri_improvement_proposal, chatgpt_evaluation)

        # 최종 합의 도출
        discussion["final_consensus"] = self._reach_consensus(discussion)

        # 실행 항목 생성
        discussion["action_items"] = self._generate_action_items(discussion["final_consensus"])

        # 논의 기록 저장
        self.discussion_history.append(discussion)

        print(f"✅ DuRi-ChatGPT 논의 완료: 합의 수준 {discussion['agreement_level']:.2f}")

        return discussion

    def _generate_discussion_points(
        self, duri_proposal: Dict[str, Any], chatgpt_eval: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """논의 포인트 생성"""
        points = []

        # DuRi의 개선안 분석
        duri_improvements = duri_proposal.get("specific_improvements", [])
        chatgpt_suggestions = chatgpt_eval.get("suggestions", [])

        # 일치하는 개선안 찾기
        common_improvements = []
        for duri_imp in duri_improvements:
            for chatgpt_sug in chatgpt_suggestions:
                if self._similar_improvements(duri_imp, chatgpt_sug):
                    common_improvements.append(
                        {
                            "type": "agreement",
                            "duri_suggestion": duri_imp,
                            "chatgpt_suggestion": chatgpt_sug,
                            "priority": "high",
                        }
                    )

        # 추가 제안사항
        additional_suggestions = []
        for chatgpt_sug in chatgpt_suggestions:
            if not any(self._similar_improvements(duri_imp, chatgpt_sug) for duri_imp in duri_improvements):
                additional_suggestions.append(
                    {
                        "type": "chatgpt_additional",
                        "suggestion": chatgpt_sug,
                        "priority": "medium",
                    }
                )

        # DuRi의 고유 제안
        duri_unique = []
        for duri_imp in duri_improvements:
            if not any(self._similar_improvements(duri_imp, chatgpt_sug) for chatgpt_sug in chatgpt_suggestions):
                duri_unique.append(
                    {
                        "type": "duri_unique",
                        "suggestion": duri_imp,
                        "priority": "medium",
                    }
                )

        points.extend(common_improvements)
        points.extend(additional_suggestions)
        points.extend(duri_unique)

        return points

    def _similar_improvements(self, improvement1: str, improvement2: str) -> bool:
        """두 개선안이 유사한지 판단"""
        keywords1 = set(improvement1.lower().split())
        keywords2 = set(improvement2.lower().split())

        # 키워드 유사도 계산
        intersection = keywords1.intersection(keywords2)
        union = keywords1.union(keywords2)

        if len(union) == 0:
            return False

        similarity = len(intersection) / len(union)
        return similarity > 0.3  # 30% 이상 유사하면 같은 개선안으로 간주

    def _calculate_agreement_level(self, duri_proposal: Dict[str, Any], chatgpt_eval: Dict[str, Any]) -> float:
        """합의 수준 계산"""
        duri_improvements = set(duri_proposal.get("specific_improvements", []))
        chatgpt_suggestions = set(chatgpt_eval.get("suggestions", []))

        # 유사한 제안 수 계산
        similar_count = 0
        for duri_imp in duri_improvements:
            for chatgpt_sug in chatgpt_suggestions:
                if self._similar_improvements(duri_imp, chatgpt_sug):
                    similar_count += 1
                    break

        # 합의 수준 계산
        total_suggestions = len(duri_improvements) + len(chatgpt_suggestions)
        if total_suggestions == 0:
            return 1.0

        agreement_level = (similar_count * 2) / total_suggestions
        return min(agreement_level, 1.0)

    def _reach_consensus(self, discussion: Dict[str, Any]) -> Dict[str, Any]:
        """최종 합의 도출"""
        consensus = {
            "agreement_level": discussion["agreement_level"],
            "accepted_improvements": [],
            "rejected_improvements": [],
            "compromise_suggestions": [],
            "implementation_plan": [],
        }

        # 합의 수준에 따른 처리
        if discussion["agreement_level"] >= self.agreement_threshold:
            # 높은 합의 - 대부분의 제안 수용
            for point in discussion["discussion_points"]:
                if point["type"] == "agreement":
                    consensus["accepted_improvements"].append(point["duri_suggestion"])
                elif point["type"] in ["chatgpt_additional", "duri_unique"]:
                    consensus["accepted_improvements"].append(point["suggestion"])
        else:
            # 낮은 합의 - 타협안 생성
            for point in discussion["discussion_points"]:
                if point["type"] == "agreement":
                    consensus["accepted_improvements"].append(point["duri_suggestion"])
                else:
                    consensus["compromise_suggestions"].append(point["suggestion"])

        # 구현 계획 생성
        consensus["implementation_plan"] = self._generate_implementation_plan(consensus)

        return consensus

    def _generate_implementation_plan(self, consensus: Dict[str, Any]) -> List[Dict[str, Any]]:
        """구현 계획 생성"""
        plan = []

        for improvement in consensus["accepted_improvements"]:
            plan.append(
                {
                    "action": improvement,
                    "priority": "high",
                    "estimated_effort": "medium",
                    "dependencies": [],
                }
            )

        for suggestion in consensus["compromise_suggestions"]:
            plan.append(
                {
                    "action": suggestion,
                    "priority": "medium",
                    "estimated_effort": "low",
                    "dependencies": [],
                }
            )

        return plan

    def _generate_action_items(self, consensus: Dict[str, Any]) -> List[Dict[str, Any]]:
        """실행 항목 생성"""
        action_items = []

        for item in consensus["implementation_plan"]:
            action_items.append(
                {
                    "description": item["action"],
                    "priority": item["priority"],
                    "status": "pending",
                    "assigned_to": "duri_system",
                    "deadline": "immediate",
                }
            )

        return action_items


# 모듈 인스턴스 생성
duri_chatgpt_discussion = DuRiChatGPTDiscussion()
