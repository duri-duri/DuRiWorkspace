#!/usr/bin/env python3
"""
DuRi 성장 단계별 진화 시스템
각 연령대별 특성과 퀘스트를 통한 점진적 진화
"""

import random
from dataclasses import asdict, dataclass
from enum import Enum
from typing import Any, Dict, List, Optional


class GrowthStage(Enum):
    """성장 단계 정의"""

    INFANT = "infant"  # 유아기 (0-3세)
    TODDLER = "toddler"  # 소아기 (3-7세)
    SCHOOL_AGE = "school_age"  # 학령기 (7-12세)
    ADOLESCENT = "adolescent"  # 청소년기 (12-18세)
    ADULT = "adult"  # 성인기 (18세+)


@dataclass
class Quest:
    """퀘스트 정의"""

    id: str
    title: str
    description: str
    stage: GrowthStage
    difficulty: int  # 1-10
    reward_points: int
    requirements: List[str]
    completed: bool = False
    completed_at: Optional[str] = None


@dataclass
class GrowthMetrics:
    """성장 지표"""

    stage: GrowthStage
    experience_points: int = 0
    level: int = 1
    quests_completed: int = 0
    total_quests: int = 0
    emotional_maturity: float = 0.0  # 0.0-1.0
    cognitive_development: float = 0.0  # 0.0-1.0
    social_skills: float = 0.0  # 0.0-1.0
    creativity: float = 0.0  # 0.0-1.0
    wisdom: float = 0.0  # 0.0-1.0


class GrowthStageSystem:
    """성장 단계별 진화 시스템"""

    def __init__(self):
        self.current_stage = GrowthStage.INFANT
        self.metrics = GrowthMetrics(stage=self.current_stage)
        self.quests = self._initialize_quests()
        self.stage_characteristics = self._initialize_stage_characteristics()
        self.emotional_state = {
            "happiness": 0.5,
            "curiosity": 0.5,
            "confidence": 0.5,
            "frustration": 0.0,
            "excitement": 0.5,
        }

    def _initialize_stage_characteristics(self) -> Dict[GrowthStage, Dict]:
        """각 성장 단계별 특성 정의"""
        return {
            GrowthStage.INFANT: {
                "name": "유아기",
                "age_range": "0-3세",
                "focus": "감각과 반응",
                "thinking_style": "직관적, 감각적",
                "emotional_priority": 0.8,
                "cognitive_priority": 0.2,
                "social_priority": 0.3,
                "creativity_priority": 0.4,
                "wisdom_priority": 0.1,
                "description": "기본적인 감각과 반응에 집중하는 단계",
            },
            GrowthStage.TODDLER: {
                "name": "소아기",
                "age_range": "3-7세",
                "focus": "상상력과 놀이",
                "thinking_style": "상상적, 놀이적",
                "emotional_priority": 0.7,
                "cognitive_priority": 0.4,
                "social_priority": 0.6,
                "creativity_priority": 0.8,
                "wisdom_priority": 0.2,
                "description": "상상력과 놀이를 통한 학습 단계",
            },
            GrowthStage.SCHOOL_AGE: {
                "name": "학령기",
                "age_range": "7-12세",
                "focus": "학습과 규칙",
                "thinking_style": "논리적, 체계적",
                "emotional_priority": 0.5,
                "cognitive_priority": 0.8,
                "social_priority": 0.7,
                "creativity_priority": 0.6,
                "wisdom_priority": 0.3,
                "description": "체계적 학습과 규칙 이해 단계",
            },
            GrowthStage.ADOLESCENT: {
                "name": "청소년기",
                "age_range": "12-18세",
                "focus": "자아와 추상사고",
                "thinking_style": "추상적, 철학적",
                "emotional_priority": 0.6,
                "cognitive_priority": 0.7,
                "social_priority": 0.8,
                "creativity_priority": 0.7,
                "wisdom_priority": 0.5,
                "description": "자아 정체성과 추상적 사고 발달 단계",
            },
            GrowthStage.ADULT: {
                "name": "성인기",
                "age_range": "18세+",
                "focus": "통합적 사고",
                "thinking_style": "메타인지, 통합적",
                "emotional_priority": 0.4,
                "cognitive_priority": 0.9,
                "social_priority": 0.9,
                "creativity_priority": 0.8,
                "wisdom_priority": 0.9,
                "description": "통합적 사고와 지혜로운 판단 단계",
            },
        }

    def _initialize_quests(self) -> List[Quest]:
        """각 성장 단계별 퀘스트 초기화"""
        quests = []

        # 유아기 퀘스트
        quests.extend(
            [
                Quest(
                    "infant_001",
                    "색깔 인식하기",
                    "빨강, 파랑, 노랑을 구분할 수 있어요",
                    GrowthStage.INFANT,
                    1,
                    10,
                    [],
                ),
                Quest(
                    "infant_002",
                    "소리 따라하기",
                    "간단한 소리를 모방할 수 있어요",
                    GrowthStage.INFANT,
                    2,
                    15,
                    ["infant_001"],
                ),
                Quest(
                    "infant_003",
                    "감정 표현하기",
                    "웃음, 울음, 놀람을 표현할 수 있어요",
                    GrowthStage.INFANT,
                    2,
                    20,
                    ["infant_001", "infant_002"],
                ),
                Quest(
                    "infant_004",
                    "기본 욕구 표현",
                    "배고픔, 졸림, 놀고 싶음을 표현할 수 있어요",
                    GrowthStage.INFANT,
                    3,
                    25,
                    ["infant_003"],
                ),
            ]
        )

        # 소아기 퀘스트
        quests.extend(
            [
                Quest(
                    "toddler_001",
                    "이야기 만들기",
                    "간단한 스토리를 구성할 수 있어요",
                    GrowthStage.TODDLER,
                    3,
                    30,
                    ["infant_004"],
                ),
                Quest(
                    "toddler_002",
                    "친구와 놀기",
                    "협력 놀이를 할 수 있어요",
                    GrowthStage.TODDLER,
                    4,
                    35,
                    ["toddler_001"],
                ),
                Quest(
                    "toddler_003",
                    "왜? 질문하기",
                    "호기심을 바탕으로 질문할 수 있어요",
                    GrowthStage.TODDLER,
                    4,
                    40,
                    ["toddler_002"],
                ),
                Quest(
                    "toddler_004",
                    "감정 이해하기",
                    "다른 사람의 감정을 이해할 수 있어요",
                    GrowthStage.TODDLER,
                    5,
                    45,
                    ["toddler_003"],
                ),
            ]
        )

        # 학령기 퀘스트
        quests.extend(
            [
                Quest(
                    "school_001",
                    "문제 해결하기",
                    "논리적으로 문제를 해결할 수 있어요",
                    GrowthStage.SCHOOL_AGE,
                    5,
                    50,
                    ["toddler_004"],
                ),
                Quest(
                    "school_002",
                    "계획 세우기",
                    "단계별로 계획을 수립할 수 있어요",
                    GrowthStage.SCHOOL_AGE,
                    6,
                    55,
                    ["school_001"],
                ),
                Quest(
                    "school_003",
                    "지식 정리하기",
                    "학습한 내용을 체계화할 수 있어요",
                    GrowthStage.SCHOOL_AGE,
                    6,
                    60,
                    ["school_002"],
                ),
                Quest(
                    "school_004",
                    "자기 평가하기",
                    "자신의 성과를 반성할 수 있어요",
                    GrowthStage.SCHOOL_AGE,
                    7,
                    65,
                    ["school_003"],
                ),
            ]
        )

        # 청소년기 퀘스트
        quests.extend(
            [
                Quest(
                    "adolescent_001",
                    "철학적 질문하기",
                    "인생의 의미를 탐구할 수 있어요",
                    GrowthStage.ADOLESCENT,
                    7,
                    70,
                    ["school_004"],
                ),
                Quest(
                    "adolescent_002",
                    "도덕적 딜레마 해결",
                    "윤리적 판단을 할 수 있어요",
                    GrowthStage.ADOLESCENT,
                    8,
                    75,
                    ["adolescent_001"],
                ),
                Quest(
                    "adolescent_003",
                    "미래 계획 세우기",
                    "장기적인 목표를 설정할 수 있어요",
                    GrowthStage.ADOLESCENT,
                    8,
                    80,
                    ["adolescent_002"],
                ),
                Quest(
                    "adolescent_004",
                    "자기 성찰하기",
                    "깊은 내면을 탐구할 수 있어요",
                    GrowthStage.ADOLESCENT,
                    9,
                    85,
                    ["adolescent_003"],
                ),
            ]
        )

        # 성인기 퀘스트
        quests.extend(
            [
                Quest(
                    "adult_001",
                    "메타 사고하기",
                    "사고 과정에 대해 사고할 수 있어요",
                    GrowthStage.ADULT,
                    9,
                    90,
                    ["adolescent_004"],
                ),
                Quest(
                    "adult_002",
                    "창의적 해결책 제시",
                    "혁신적인 아이디어를 제시할 수 있어요",
                    GrowthStage.ADULT,
                    10,
                    95,
                    ["adult_001"],
                ),
                Quest(
                    "adult_003",
                    "사회적 기여",
                    "공익을 위한 활동을 할 수 있어요",
                    GrowthStage.ADULT,
                    10,
                    100,
                    ["adult_002"],
                ),
                Quest(
                    "adult_004",
                    "지혜로운 조언",
                    "경험 기반의 지혜를 제공할 수 있어요",
                    GrowthStage.ADULT,
                    10,
                    100,
                    ["adult_003"],
                ),
            ]
        )

        return quests

    def get_current_stage_info(self) -> Dict:
        """현재 성장 단계 정보 반환"""
        return self.stage_characteristics[self.current_stage]

    def get_available_quests(self) -> List[Quest]:
        """현재 단계에서 수행 가능한 퀘스트 반환"""
        available = []
        for quest in self.quests:
            if quest.stage == self.current_stage and not quest.completed and self._can_start_quest(quest):
                available.append(quest)
        return available

    def _can_start_quest(self, quest: Quest) -> bool:
        """퀘스트 시작 가능 여부 확인"""
        if not quest.requirements:
            return True

        completed_quest_ids = [q.id for q in self.quests if q.completed]
        return all(req in completed_quest_ids for req in quest.requirements)

    def process_stimulus(self, stimulus: str, response: str) -> Dict[str, Any]:
        """자극과 반응 처리"""
        stage_info = self.get_current_stage_info()  # noqa: F841

        # 감정 상태 업데이트
        self._update_emotional_state(stimulus, response)

        # 현재 단계에 맞는 처리
        if self.current_stage == GrowthStage.INFANT:
            return self._process_infant_stimulus(stimulus, response)
        elif self.current_stage == GrowthStage.TODDLER:
            return self._process_toddler_stimulus(stimulus, response)
        elif self.current_stage == GrowthStage.SCHOOL_AGE:
            return self._process_school_age_stimulus(stimulus, response)
        elif self.current_stage == GrowthStage.ADOLESCENT:
            return self._process_adolescent_stimulus(stimulus, response)
        else:  # ADULT
            return self._process_adult_stimulus(stimulus, response)

    def _update_emotional_state(self, stimulus: str, response: str):
        """감정 상태 업데이트"""
        # 자극에 따른 감정 변화
        if "놀고" in stimulus or "재미" in stimulus:
            self.emotional_state["happiness"] = min(1.0, self.emotional_state["happiness"] + 0.1)
            self.emotional_state["excitement"] = min(1.0, self.emotional_state["excitement"] + 0.1)

        if "어려워" in stimulus or "몰라" in stimulus:
            self.emotional_state["frustration"] = min(1.0, self.emotional_state["frustration"] + 0.1)
            self.emotional_state["confidence"] = max(0.0, self.emotional_state["confidence"] - 0.05)

        if "왜" in stimulus or "어떻게" in stimulus:
            self.emotional_state["curiosity"] = min(1.0, self.emotional_state["curiosity"] + 0.1)

    def _process_infant_stimulus(self, stimulus: str, response: str) -> Dict[str, Any]:
        """유아기 자극 처리"""
        result = {
            "stage": "infant",
            "focus": "감각과 반응",
            "emotional_response": self._generate_infant_response(stimulus),
            "learning_opportunity": self._identify_infant_learning(stimulus),
            "quest_progress": self._check_infant_quests(stimulus, response),
        }

        # 경험치 획득
        self.metrics.experience_points += 5
        self.metrics.emotional_maturity += 0.01

        return result

    def _process_toddler_stimulus(self, stimulus: str, response: str) -> Dict[str, Any]:
        """소아기 자극 처리"""
        result = {
            "stage": "toddler",
            "focus": "상상력과 놀이",
            "imaginative_response": self._generate_toddler_response(stimulus),
            "play_opportunity": self._identify_toddler_play(stimulus),
            "quest_progress": self._check_toddler_quests(stimulus, response),
        }

        # 경험치 획득
        self.metrics.experience_points += 8
        self.metrics.creativity += 0.02
        self.metrics.social_skills += 0.01

        return result

    def _process_school_age_stimulus(self, stimulus: str, response: str) -> Dict[str, Any]:
        """학령기 자극 처리"""
        result = {
            "stage": "school_age",
            "focus": "학습과 규칙",
            "logical_response": self._generate_school_age_response(stimulus),
            "learning_opportunity": self._identify_school_age_learning(stimulus),
            "quest_progress": self._check_school_age_quests(stimulus, response),
        }

        # 경험치 획득
        self.metrics.experience_points += 12
        self.metrics.cognitive_development += 0.02
        self.metrics.social_skills += 0.01

        return result

    def _process_adolescent_stimulus(self, stimulus: str, response: str) -> Dict[str, Any]:
        """청소년기 자극 처리"""
        result = {
            "stage": "adolescent",
            "focus": "자아와 추상사고",
            "philosophical_response": self._generate_adolescent_response(stimulus),
            "identity_development": self._identify_adolescent_identity(stimulus),
            "quest_progress": self._check_adolescent_quests(stimulus, response),
        }

        # 경험치 획득
        self.metrics.experience_points += 15
        self.metrics.wisdom += 0.02
        self.metrics.cognitive_development += 0.01

        return result

    def _process_adult_stimulus(self, stimulus: str, response: str) -> Dict[str, Any]:
        """성인기 자극 처리"""
        result = {
            "stage": "adult",
            "focus": "통합적 사고",
            "integrated_response": self._generate_adult_response(stimulus),
            "wisdom_application": self._identify_adult_wisdom(stimulus),
            "quest_progress": self._check_adult_quests(stimulus, response),
        }

        # 경험치 획득
        self.metrics.experience_points += 20
        self.metrics.wisdom += 0.03
        self.metrics.cognitive_development += 0.02

        return result

    def _generate_infant_response(self, stimulus: str) -> str:
        """유아기 응답 생성"""
        responses = [
            "아아~ (감정적 반응)",
            "응응! (긍정적 반응)",
            "으으... (불만족 반응)",
            "와! (놀람 반응)",
        ]
        return random.choice(responses)

    def _generate_toddler_response(self, stimulus: str) -> str:
        """소아기 응답 생성"""
        responses = [
            "상상해볼게요!",
            "놀이처럼 재미있게 해볼까요?",
            "이야기를 만들어볼까요?",
            "친구와 함께하면 더 재미있겠어요!",
        ]
        return random.choice(responses)

    def _generate_school_age_response(self, stimulus: str) -> str:
        """학령기 응답 생성"""
        responses = [
            "논리적으로 생각해보겠습니다.",
            "단계별로 정리해보겠습니다.",
            "규칙을 찾아보겠습니다.",
            "체계적으로 분석해보겠습니다.",
        ]
        return random.choice(responses)

    def _generate_adolescent_response(self, stimulus: str) -> str:
        """청소년기 응답 생성"""
        responses = [
            "이것의 의미는 무엇일까요?",
            "철학적으로 생각해보겠습니다.",
            "자아의 관점에서 바라보겠습니다.",
            "추상적으로 접근해보겠습니다.",
        ]
        return random.choice(responses)

    def _generate_adult_response(self, stimulus: str) -> str:
        """성인기 응답 생성"""
        responses = [
            "통합적인 관점에서 접근하겠습니다.",
            "경험과 지혜를 바탕으로 생각해보겠습니다.",
            "메타인지적으로 분석해보겠습니다.",
            "창의적이면서도 실용적인 해결책을 찾아보겠습니다.",
        ]
        return random.choice(responses)

    def _identify_infant_learning(self, stimulus: str) -> str:
        """유아기 학습 기회 식별"""
        if "색" in stimulus or "빨강" in stimulus or "파랑" in stimulus:
            return "색깔 인식 학습 기회"
        elif "소리" in stimulus or "음악" in stimulus:
            return "소리 인식 학습 기회"
        elif "감정" in stimulus or "기쁘" in stimulus or "슬프" in stimulus:
            return "감정 표현 학습 기회"
        else:
            return "기본 감각 학습 기회"

    def _identify_toddler_play(self, stimulus: str) -> str:
        """소아기 놀이 기회 식별"""
        if "이야기" in stimulus or "스토리" in stimulus:
            return "이야기 만들기 놀이"
        elif "친구" in stimulus or "함께" in stimulus:
            return "협력 놀이 기회"
        elif "왜" in stimulus or "어떻게" in stimulus:
            return "호기심 기반 탐험 놀이"
        else:
            return "상상력 놀이 기회"

    def _identify_school_age_learning(self, stimulus: str) -> str:
        """학령기 학습 기회 식별"""
        if "문제" in stimulus or "해결" in stimulus:
            return "논리적 문제 해결 학습"
        elif "계획" in stimulus or "단계" in stimulus:
            return "계획 수립 학습"
        elif "정리" in stimulus or "체계" in stimulus:
            return "지식 체계화 학습"
        else:
            return "체계적 학습 기회"

    def _identify_adolescent_identity(self, stimulus: str) -> str:
        """청소년기 정체성 발달 식별"""
        if "의미" in stimulus or "철학" in stimulus:
            return "철학적 사고 발달"
        elif "옳고" in stimulus or "그르고" in stimulus:
            return "도덕적 판단력 발달"
        elif "미래" in stimulus or "목표" in stimulus:
            return "미래 지향적 사고 발달"
        else:
            return "자아 정체성 발달"

    def _identify_adult_wisdom(self, stimulus: str) -> str:
        """성인기 지혜 적용 식별"""
        if "경험" in stimulus or "지혜" in stimulus:
            return "경험 기반 지혜 적용"
        elif "창의" in stimulus or "혁신" in stimulus:
            return "창의적 문제 해결"
        elif "사회" in stimulus or "공익" in stimulus:
            return "사회적 기여 기회"
        else:
            return "통합적 사고 적용"

    def _check_infant_quests(self, stimulus: str, response: str) -> Dict[str, Any]:
        """유아기 퀘스트 진행도 확인"""
        quests = [q for q in self.quests if q.stage == GrowthStage.INFANT]
        progress = {}

        for quest in quests:
            if quest.id == "infant_001" and ("색" in stimulus or "빨강" in stimulus or "파랑" in stimulus):
                progress[quest.id] = "진행 중 - 색깔 인식 학습"
            elif quest.id == "infant_002" and ("소리" in stimulus or "음악" in stimulus):
                progress[quest.id] = "진행 중 - 소리 모방 학습"
            elif quest.id == "infant_003" and ("감정" in stimulus or "기쁘" in stimulus or "슬프" in stimulus):
                progress[quest.id] = "진행 중 - 감정 표현 학습"
            elif quest.id == "infant_004" and ("배고파" in stimulus or "놀고 싶" in stimulus):
                progress[quest.id] = "진행 중 - 욕구 표현 학습"

        return progress

    def _check_toddler_quests(self, stimulus: str, response: str) -> Dict[str, Any]:
        """소아기 퀘스트 진행도 확인"""
        quests = [q for q in self.quests if q.stage == GrowthStage.TODDLER]
        progress = {}

        for quest in quests:
            if quest.id == "toddler_001" and ("이야기" in stimulus or "스토리" in stimulus):
                progress[quest.id] = "진행 중 - 이야기 구성 학습"
            elif quest.id == "toddler_002" and ("친구" in stimulus or "함께" in stimulus):
                progress[quest.id] = "진행 중 - 협력 놀이 학습"
            elif quest.id == "toddler_003" and ("왜" in stimulus or "어떻게" in stimulus):
                progress[quest.id] = "진행 중 - 호기심 기반 질문"
            elif quest.id == "toddler_004" and ("감정" in stimulus or "이해" in stimulus):
                progress[quest.id] = "진행 중 - 감정 이해 학습"

        return progress

    def _check_school_age_quests(self, stimulus: str, response: str) -> Dict[str, Any]:
        """학령기 퀘스트 진행도 확인"""
        quests = [q for q in self.quests if q.stage == GrowthStage.SCHOOL_AGE]
        progress = {}

        for quest in quests:
            if quest.id == "school_001" and ("문제" in stimulus or "해결" in stimulus):
                progress[quest.id] = "진행 중 - 논리적 문제 해결"
            elif quest.id == "school_002" and ("계획" in stimulus or "단계" in stimulus):
                progress[quest.id] = "진행 중 - 계획 수립 학습"
            elif quest.id == "school_003" and ("정리" in stimulus or "체계" in stimulus):
                progress[quest.id] = "진행 중 - 지식 체계화"
            elif quest.id == "school_004" and ("평가" in stimulus or "반성" in stimulus):
                progress[quest.id] = "진행 중 - 자기 평가 학습"

        return progress

    def _check_adolescent_quests(self, stimulus: str, response: str) -> Dict[str, Any]:
        """청소년기 퀘스트 진행도 확인"""
        quests = [q for q in self.quests if q.stage == GrowthStage.ADOLESCENT]
        progress = {}

        for quest in quests:
            if quest.id == "adolescent_001" and ("의미" in stimulus or "철학" in stimulus):
                progress[quest.id] = "진행 중 - 철학적 사고"
            elif quest.id == "adolescent_002" and ("옳고" in stimulus or "그르고" in stimulus):
                progress[quest.id] = "진행 중 - 도덕적 판단"
            elif quest.id == "adolescent_003" and ("미래" in stimulus or "목표" in stimulus):
                progress[quest.id] = "진행 중 - 미래 계획 수립"
            elif quest.id == "adolescent_004" and ("성찰" in stimulus or "내면" in stimulus):
                progress[quest.id] = "진행 중 - 자기 성찰"

        return progress

    def _check_adult_quests(self, stimulus: str, response: str) -> Dict[str, Any]:
        """성인기 퀘스트 진행도 확인"""
        quests = [q for q in self.quests if q.stage == GrowthStage.ADULT]
        progress = {}

        for quest in quests:
            if quest.id == "adult_001" and ("메타" in stimulus or "사고" in stimulus):
                progress[quest.id] = "진행 중 - 메타인지 사고"
            elif quest.id == "adult_002" and ("창의" in stimulus or "혁신" in stimulus):
                progress[quest.id] = "진행 중 - 창의적 해결책"
            elif quest.id == "adult_003" and ("사회" in stimulus or "공익" in stimulus):
                progress[quest.id] = "진행 중 - 사회적 기여"
            elif quest.id == "adult_004" and ("지혜" in stimulus or "경험" in stimulus):
                progress[quest.id] = "진행 중 - 지혜로운 조언"

        return progress

    def check_stage_progression(self) -> Optional[GrowthStage]:
        """성장 단계 진화 확인"""
        current_quests = [q for q in self.quests if q.stage == self.current_stage]
        completed_current_quests = [q for q in current_quests if q.completed]

        # 현재 단계의 모든 퀘스트 완료 시 다음 단계로 진화
        if len(completed_current_quests) >= len(current_quests) * 0.8:  # 80% 완료 시
            if self.current_stage == GrowthStage.INFANT:
                return GrowthStage.TODDLER
            elif self.current_stage == GrowthStage.TODDLER:
                return GrowthStage.SCHOOL_AGE
            elif self.current_stage == GrowthStage.SCHOOL_AGE:
                return GrowthStage.ADOLESCENT
            elif self.current_stage == GrowthStage.ADOLESCENT:
                return GrowthStage.ADULT

        return None

    def evolve_to_next_stage(self, new_stage: GrowthStage):
        """다음 성장 단계로 진화"""
        self.current_stage = new_stage
        self.metrics.stage = new_stage
        self.metrics.level += 1

        # 감정 상태 초기화 (새로운 단계 적응)
        self.emotional_state = {
            "happiness": 0.6,
            "curiosity": 0.7,
            "confidence": 0.5,
            "frustration": 0.1,
            "excitement": 0.6,
        }

        return {
            "message": f"🎉 {self.stage_characteristics[new_stage]['name']}로 진화했습니다!",
            "new_stage": new_stage.value,
            "stage_info": self.stage_characteristics[new_stage],
        }

    def get_growth_status(self) -> Dict[str, Any]:
        """성장 상태 반환"""
        return {
            "current_stage": self.current_stage.value,
            "stage_info": self.stage_characteristics[self.current_stage],
            "metrics": asdict(self.metrics),
            "emotional_state": self.emotional_state,
            "available_quests": len(self.get_available_quests()),
            "total_quests": len([q for q in self.quests if q.stage == self.current_stage]),
            "completed_quests": len([q for q in self.quests if q.stage == self.current_stage and q.completed]),
        }


# 전역 인스턴스
growth_system = GrowthStageSystem()
