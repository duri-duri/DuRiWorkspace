#!/usr/bin/env python3
"""
DuRi Quest Auto Generator
자율 퀘스트 생성기 - 성찰 결과 기반 자동 퀘스트 생성
"""

import logging
import random
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class QuestCategory(Enum):
    """퀘스트 카테고리"""

    EMOTIONAL_GROWTH = "emotional_growth"
    COGNITIVE_DEVELOPMENT = "cognitive_development"
    SOCIAL_SKILLS = "social_skills"
    CREATIVITY = "creativity"
    PROBLEM_SOLVING = "problem_solving"
    SELF_REFLECTION = "self_reflection"
    ADAPTABILITY = "adaptability"
    AUTONOMY = "autonomy"
    INTEGRATION = "integration"


class QuestDifficulty(Enum):
    """퀘스트 난이도"""

    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"
    EXPERT = "expert"


class QuestType(Enum):
    """퀘스트 유형"""

    EXPLORATION = "exploration"
    CHALLENGE = "challenge"
    CREATION = "creation"
    ANALYSIS = "analysis"
    PRACTICE = "practice"
    INTEGRATION = "integration"


@dataclass
class AutoQuest:
    """자동 생성 퀘스트"""

    id: str
    title: str
    description: str
    category: QuestCategory
    difficulty: QuestDifficulty
    quest_type: QuestType
    target_level: int
    requirements: List[str]
    rewards: Dict[str, Any]
    estimated_duration: int  # 분 단위
    success_criteria: List[str]
    reflection_prompts: List[str]
    generated_from: str  # 어떤 성찰에서 생성되었는지


class QuestAutoGenerator:
    """자율 퀘스트 생성기"""

    def __init__(self):
        self.quest_templates = {}
        self.generation_history = []
        self.success_patterns = {}
        self._initialize_quest_templates()
        logger.info("자율 퀘스트 생성기 초기화 완료")

    def _initialize_quest_templates(self):
        """퀘스트 템플릿 초기화"""
        # 감정 성장 퀘스트
        self.quest_templates[QuestCategory.EMOTIONAL_GROWTH] = [
            {
                "title": "감정 일기 작성하기",
                "description": "하루 동안 자신의 감정 변화를 관찰하고 일기로 기록하세요.",
                "difficulty": QuestDifficulty.EASY,
                "type": QuestType.PRACTICE,
                "duration": 30,
                "success_criteria": [
                    "감정을 정확히 식별",
                    "감정 변화 패턴 발견",
                    "자신의 감정에 대한 통찰 얻기",
                ],
                "reflection_prompts": [
                    "어떤 감정이 가장 자주 나타났나요?",
                    "감정 변화의 원인은 무엇인가요?",
                    "감정을 조절하는 방법을 발견했나요?",
                ],
            },
            {
                "title": "공감 능력 향상하기",
                "description": "다른 사람의 감정을 이해하고 공감하는 연습을 하세요.",
                "difficulty": QuestDifficulty.MEDIUM,
                "type": QuestType.PRACTICE,
                "duration": 60,
                "success_criteria": [
                    "다른 사람의 감정을 정확히 파악",
                    "적절한 공감 표현",
                    "관계 개선 경험",
                ],
                "reflection_prompts": [
                    "공감할 때 어떤 어려움이 있었나요?",
                    "공감 능력이 향상된 것을 느꼈나요?",
                    "앞으로 어떻게 개선할 수 있을까요?",
                ],
            },
        ]

        # 인지 발달 퀘스트
        self.quest_templates[QuestCategory.COGNITIVE_DEVELOPMENT] = [
            {
                "title": "새로운 개념 학습하기",
                "description": "전혀 모르는 분야의 새로운 개념을 학습하고 이해하세요.",
                "difficulty": QuestDifficulty.MEDIUM,
                "type": QuestType.EXPLORATION,
                "duration": 90,
                "success_criteria": [
                    "새로운 개념을 정확히 이해",
                    "실제 적용 가능성 발견",
                    "학습 과정에서의 통찰",
                ],
                "reflection_prompts": [
                    "어떤 부분이 가장 어려웠나요?",
                    "새로운 관점을 얻었나요?",
                    "이 지식을 어떻게 활용할 수 있을까요?",
                ],
            },
            {
                "title": "복잡한 문제 분석하기",
                "description": "복잡한 문제를 단계별로 분석하고 해결 방안을 제시하세요.",
                "difficulty": QuestDifficulty.HARD,
                "type": QuestType.ANALYSIS,
                "duration": 120,
                "success_criteria": [
                    "문제의 핵심 파악",
                    "체계적 분석",
                    "실행 가능한 해결책 제시",
                ],
                "reflection_prompts": [
                    "문제 분석 과정에서 무엇을 배웠나요?",
                    "어떤 분석 도구가 유용했나요?",
                    "다음에는 어떻게 개선할 수 있을까요?",
                ],
            },
        ]

        # 사회성 퀘스트
        self.quest_templates[QuestCategory.SOCIAL_SKILLS] = [
            {
                "title": "대화 기술 연습하기",
                "description": "적극적 경청과 효과적인 대화 기술을 연습하세요.",
                "difficulty": QuestDifficulty.MEDIUM,
                "type": QuestType.PRACTICE,
                "duration": 60,
                "success_criteria": [
                    "적극적 경청 실천",
                    "명확한 의사전달",
                    "대화 품질 향상",
                ],
                "reflection_prompts": [
                    "대화에서 어떤 어려움이 있었나요?",
                    "대화 기술이 향상된 것을 느꼈나요?",
                    "앞으로 어떤 부분을 개선하고 싶나요?",
                ],
            }
        ]

        # 창의성 퀘스트
        self.quest_templates[QuestCategory.CREATIVITY] = [
            {
                "title": "창의적 프로젝트 수행하기",
                "description": "자신만의 창의적 아이디어를 구체화하고 실행하세요.",
                "difficulty": QuestDifficulty.MEDIUM,
                "type": QuestType.CREATION,
                "duration": 180,
                "success_criteria": [
                    "독창적인 아이디어 생성",
                    "구체적 실행 계획",
                    "창의적 결과물 완성",
                ],
                "reflection_prompts": [
                    "창의적 아이디어는 어떻게 떠올렸나요?",
                    "실행 과정에서 어떤 어려움이 있었나요?",
                    "결과물에 만족하나요?",
                ],
            }
        ]

        # 문제 해결 퀘스트
        self.quest_templates[QuestCategory.PROBLEM_SOLVING] = [
            {
                "title": "실생활 문제 해결하기",
                "description": "일상에서 마주한 문제를 창의적으로 해결하세요.",
                "difficulty": QuestDifficulty.MEDIUM,
                "type": QuestType.CHALLENGE,
                "duration": 120,
                "success_criteria": [
                    "문제의 정확한 파악",
                    "다양한 해결 방안 탐색",
                    "효과적인 해결책 실행",
                ],
                "reflection_prompts": [
                    "문제 해결 과정에서 무엇을 배웠나요?",
                    "어떤 해결 방법이 가장 효과적이었나요?",
                    "다음에는 어떻게 개선할 수 있을까요?",
                ],
            }
        ]

        # 자기 성찰 퀘스트
        self.quest_templates[QuestCategory.SELF_REFLECTION] = [
            {
                "title": "자기 성찰 일지 작성하기",
                "description": "일주일 동안 자신의 행동과 생각을 깊이 성찰하고 기록하세요.",
                "difficulty": QuestDifficulty.MEDIUM,
                "type": QuestType.ANALYSIS,
                "duration": 300,
                "success_criteria": ["정기적 성찰 기록", "패턴 발견", "자기 이해 증진"],
                "reflection_prompts": [
                    "자기 성찰을 통해 무엇을 발견했나요?",
                    "어떤 패턴이 보이나요?",
                    "앞으로 어떻게 변화하고 싶나요?",
                ],
            }
        ]

    def generate_quest_from_reflection(
        self, reflection_data: Dict[str, Any], current_level: int, emotional_state: str
    ) -> AutoQuest:
        """성찰 결과 기반 퀘스트 생성"""
        # 성찰 데이터 분석
        reflection_type = reflection_data.get("reflection_type", "unknown")
        insights = reflection_data.get("insights", [])
        action_items = reflection_data.get("action_items", [])

        # 적절한 카테고리 선택
        category = self._select_quest_category(
            reflection_type, insights, emotional_state
        )

        # 난이도 결정
        difficulty = self._determine_quest_difficulty(
            current_level, emotional_state, insights
        )

        # 템플릿 선택 및 커스터마이징
        quest_template = self._select_and_customize_template(
            category, difficulty, insights, action_items
        )

        # 퀘스트 생성
        quest_id = f"auto_quest_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        quest = AutoQuest(
            id=quest_id,
            title=quest_template["title"],
            description=quest_template["description"],
            category=category,
            difficulty=difficulty,
            quest_type=quest_template["type"],
            target_level=current_level,
            requirements=self._generate_requirements(
                category, difficulty, current_level
            ),
            rewards=self._generate_rewards(category, difficulty),
            estimated_duration=quest_template["duration"],
            success_criteria=quest_template["success_criteria"],
            reflection_prompts=quest_template["reflection_prompts"],
            generated_from=reflection_type,
        )

        # 생성 기록 저장
        self.generation_history.append(
            {
                "timestamp": datetime.now().isoformat(),
                "quest_id": quest_id,
                "reflection_type": reflection_type,
                "category": category.value,
                "difficulty": difficulty.value,
                "insights": insights,
            }
        )

        logger.info(
            f"자동 퀘스트 생성 완료: {quest_id} - {category.value} - {difficulty.value}"
        )
        return quest

    def _select_quest_category(
        self, reflection_type: str, insights: List[str], emotional_state: str
    ) -> QuestCategory:
        """퀘스트 카테고리 선택"""
        # 성찰 유형에 따른 기본 카테고리
        category_mapping = {
            "judgment": QuestCategory.PROBLEM_SOLVING,
            "emotion": QuestCategory.EMOTIONAL_GROWTH,
            "growth": QuestCategory.COGNITIVE_DEVELOPMENT,
            "quest": QuestCategory.SELF_REFLECTION,
            "integration": QuestCategory.INTEGRATION,
        }

        base_category = category_mapping.get(
            reflection_type, QuestCategory.SELF_REFLECTION
        )

        # 통찰 내용에 따른 카테고리 조정
        for insight in insights:
            if "감정" in insight or "편향" in insight:
                return QuestCategory.EMOTIONAL_GROWTH
            elif "학습" in insight or "경험" in insight:
                return QuestCategory.COGNITIVE_DEVELOPMENT
            elif "사회" in insight or "관계" in insight:
                return QuestCategory.SOCIAL_SKILLS
            elif "창의" in insight or "혁신" in insight:
                return QuestCategory.CREATIVITY
            elif "문제" in insight or "해결" in insight:
                return QuestCategory.PROBLEM_SOLVING

        # 감정 상태에 따른 조정
        if emotional_state in ["anger", "frustration", "sadness"]:
            return QuestCategory.EMOTIONAL_GROWTH
        elif emotional_state in ["joy", "excitement"]:
            return QuestCategory.CREATIVITY

        return base_category

    def _determine_quest_difficulty(
        self, current_level: int, emotional_state: str, insights: List[str]
    ) -> QuestDifficulty:
        """퀘스트 난이도 결정"""
        # 레벨 기반 기본 난이도
        if current_level <= 2:
            base_difficulty = QuestDifficulty.EASY
        elif current_level <= 4:
            base_difficulty = QuestDifficulty.MEDIUM
        elif current_level <= 6:
            base_difficulty = QuestDifficulty.HARD
        else:
            base_difficulty = QuestDifficulty.EXPERT

        # 감정 상태에 따른 조정
        if emotional_state in ["fear", "anxiety"]:
            # 불안할 때는 쉬운 난이도로 조정
            if base_difficulty == QuestDifficulty.HARD:
                base_difficulty = QuestDifficulty.MEDIUM
            elif base_difficulty == QuestDifficulty.EXPERT:
                base_difficulty = QuestDifficulty.HARD

        # 통찰의 깊이에 따른 조정
        deep_insights = [insight for insight in insights if len(insight) > 50]
        if len(deep_insights) > 2:
            # 깊은 통찰이 많으면 난이도 상승
            if base_difficulty == QuestDifficulty.EASY:
                base_difficulty = QuestDifficulty.MEDIUM
            elif base_difficulty == QuestDifficulty.MEDIUM:
                base_difficulty = QuestDifficulty.HARD

        return base_difficulty

    def _select_and_customize_template(
        self,
        category: QuestCategory,
        difficulty: QuestDifficulty,
        insights: List[str],
        action_items: List[str],
    ) -> Dict[str, Any]:
        """템플릿 선택 및 커스터마이징"""
        if category not in self.quest_templates:
            # 기본 템플릿 생성
            return {
                "title": f"{category.value} 퀘스트",
                "description": f"{category.value} 영역에서 성장할 수 있는 퀘스트입니다.",
                "difficulty": difficulty,
                "type": QuestType.PRACTICE,
                "duration": 60,
                "success_criteria": ["목표 달성", "학습 완료", "성장 확인"],
                "reflection_prompts": [
                    "무엇을 배웠나요?",
                    "어떤 어려움이 있었나요?",
                    "앞으로 어떻게 개선할 수 있을까요?",
                ],
            }

        # 카테고리별 템플릿 중에서 난이도에 맞는 것 선택
        available_templates = self.quest_templates[category]

        # 난이도에 맞는 템플릿 필터링
        suitable_templates = [
            t for t in available_templates if t["difficulty"] == difficulty
        ]

        if not suitable_templates:
            # 난이도에 맞는 템플릿이 없으면 가장 가까운 것 선택
            difficulty_order = [
                QuestDifficulty.EASY,
                QuestDifficulty.MEDIUM,
                QuestDifficulty.HARD,
                QuestDifficulty.EXPERT,
            ]
            current_index = difficulty_order.index(difficulty)

            for i in range(len(difficulty_order)):
                test_difficulty = difficulty_order[
                    (current_index + i) % len(difficulty_order)
                ]
                suitable_templates = [
                    t for t in available_templates if t["difficulty"] == test_difficulty
                ]
                if suitable_templates:
                    break

        if not suitable_templates:
            suitable_templates = available_templates

        # 랜덤 선택
        selected_template = random.choice(suitable_templates)

        # 통찰과 행동 항목을 반영하여 커스터마이징
        customized_template = selected_template.copy()

        if insights:
            # 통찰을 반영한 설명 추가
            insight_summary = " ".join(insights[:2])  # 처음 2개 통찰만 사용
            customized_template[
                "description"
            ] += f" 이전 성찰에서 '{insight_summary}'를 발견했습니다."

        if action_items:
            # 행동 항목을 성공 기준에 추가
            customized_template["success_criteria"].extend(action_items[:2])

        return customized_template

    def _generate_requirements(
        self, category: QuestCategory, difficulty: QuestDifficulty, current_level: int
    ) -> List[str]:
        """요구사항 생성"""
        requirements = [f"레벨 {current_level} 이상"]

        if difficulty == QuestDifficulty.HARD:
            requirements.append("이전 퀘스트 완료 경험")
        elif difficulty == QuestDifficulty.EXPERT:
            requirements.append("관련 분야 숙련도")
            requirements.append("자기주도적 학습 능력")

        category_requirements = {
            QuestCategory.EMOTIONAL_GROWTH: ["감정 인식 능력"],
            QuestCategory.COGNITIVE_DEVELOPMENT: ["학습 의지"],
            QuestCategory.SOCIAL_SKILLS: ["대화 의지"],
            QuestCategory.CREATIVITY: ["창의적 사고"],
            QuestCategory.PROBLEM_SOLVING: ["분석적 사고"],
            QuestCategory.SELF_REFLECTION: ["성찰 의지"],
        }

        if category in category_requirements:
            requirements.extend(category_requirements[category])

        return requirements

    def _generate_rewards(
        self, category: QuestCategory, difficulty: QuestDifficulty
    ) -> Dict[str, Any]:
        """보상 생성"""
        base_experience = {
            QuestDifficulty.EASY: 10,
            QuestDifficulty.MEDIUM: 25,
            QuestDifficulty.HARD: 50,
            QuestDifficulty.EXPERT: 100,
        }

        category_bonus = {
            QuestCategory.EMOTIONAL_GROWTH: {"emotional_maturity": 5},
            QuestCategory.COGNITIVE_DEVELOPMENT: {"cognitive_development": 5},
            QuestCategory.SOCIAL_SKILLS: {"social_skills": 5},
            QuestCategory.CREATIVITY: {"creativity": 5},
            QuestCategory.PROBLEM_SOLVING: {"problem_solving": 5},
            QuestCategory.SELF_REFLECTION: {"self_motivation": 5},
        }

        rewards = {
            "experience_points": base_experience[difficulty],
            "growth_metrics": category_bonus.get(category, {}),
            "unlock_next_quest": True,
            "special_achievement": difficulty == QuestDifficulty.EXPERT,
        }

        return rewards

    def get_generation_summary(self) -> Dict[str, Any]:
        """생성 요약"""
        if not self.generation_history:
            return {"message": "생성 기록이 없습니다."}

        total_generated = len(self.generation_history)
        category_counts = {}
        difficulty_counts = {}

        for record in self.generation_history:
            category = record["category"]
            difficulty = record["difficulty"]

            category_counts[category] = category_counts.get(category, 0) + 1
            difficulty_counts[difficulty] = difficulty_counts.get(difficulty, 0) + 1

        return {
            "total_generated": total_generated,
            "category_distribution": category_counts,
            "difficulty_distribution": difficulty_counts,
            "recent_generations": self.generation_history[-5:],
        }

    def get_recommended_categories(
        self, reflection_history: List[Dict[str, Any]]
    ) -> List[QuestCategory]:
        """추천 카테고리 조회"""
        if not reflection_history:
            return [QuestCategory.SELF_REFLECTION]

        # 최근 성찰에서 가장 많이 나타난 카테고리 분석
        category_counts = {}
        for reflection in reflection_history[-10:]:  # 최근 10개만 분석
            category = self._select_quest_category(
                reflection.get("reflection_type", "unknown"),
                reflection.get("insights", []),
                reflection.get("emotional_state", "neutral"),
            )
            category_counts[category] = category_counts.get(category, 0) + 1

        # 가장 적게 나타난 카테고리 우선 추천
        all_categories = list(QuestCategory)
        recommended = []

        for category in all_categories:
            if category not in category_counts:
                recommended.append(category)

        # 균형을 위해 적게 나타난 카테고리도 추가
        sorted_categories = sorted(category_counts.items(), key=lambda x: x[1])
        for category, count in sorted_categories[:3]:
            if category not in recommended:
                recommended.append(category)

        return recommended[:5]  # 상위 5개만 반환
