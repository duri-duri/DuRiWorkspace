#!/usr/bin/env python3
"""
DuRi 퀘스트 계산기 - 퀘스트 채점 기준 및 평가 시스템
ChatGPT 보완 제안 기반 자율성 강화 퀘스트 시스템
"""

import logging
import time
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from collections import defaultdict

logger = logging.getLogger(__name__)

class QuestDifficulty(Enum):
    """퀘스트 난이도"""
    VERY_EASY = 1
    EASY = 2
    MEDIUM = 3
    HARD = 4
    VERY_HARD = 5

class QuestCategory(Enum):
    """퀘스트 카테고리"""
    EMOTIONAL = "emotional"      # 감정 관련
    COGNITIVE = "cognitive"      # 인지 관련
    SOCIAL = "social"            # 사회적 상호작용
    CREATIVE = "creative"        # 창의성
    PROBLEM_SOLVING = "problem_solving"  # 문제 해결
    SELF_REFLECTION = "self_reflection"  # 자기성찰

class QuestStatus(Enum):
    """퀘스트 상태"""
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    EXPIRED = "expired"

@dataclass
class QuestRequirement:
    """퀘스트 요구사항"""
    type: str  # "emotion_level", "cognitive_skill", "experience_count"
    value: Any
    operator: str  # ">=", "==", "<="
    description: str

@dataclass
class QuestReward:
    """퀘스트 보상"""
    experience_points: int
    growth_points: int
    skill_points: Dict[str, int]
    unlock_features: List[str]

@dataclass
class Quest:
    """퀘스트 정의"""
    id: str
    title: str
    description: str
    category: QuestCategory
    difficulty: QuestDifficulty
    requirements: List[QuestRequirement]
    rewards: QuestReward
    time_limit: Optional[int] = None  # 초 단위, None이면 무제한
    created_at: str = ""
    status: QuestStatus = QuestStatus.NOT_STARTED
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    progress: float = 0.0  # 0.0 ~ 1.0
    attempts: int = 0
    max_attempts: int = 3

@dataclass
class QuestEvaluation:
    """퀘스트 평가 결과"""
    quest_id: str
    score: float  # 0.0 ~ 1.0
    passed: bool
    feedback: Dict[str, Any]
    completion_time: Optional[float] = None  # 초 단위
    timestamp: str = ""

class QuestCalculator:
    """퀘스트 계산기 - 채점 기준 및 평가 시스템"""
    
    def __init__(self):
        self.evaluation_criteria = self._initialize_evaluation_criteria()
        self.scoring_weights = self._initialize_scoring_weights()
        self.feedback_templates = self._initialize_feedback_templates()
        
        logger.info("퀘스트 계산기 초기화 완료")
    
    def _initialize_evaluation_criteria(self) -> Dict[str, Dict[str, Any]]:
        """평가 기준 초기화"""
        return {
            "emotional": {
                "emotion_recognition": {"weight": 0.3, "description": "감정 인식 능력"},
                "emotion_regulation": {"weight": 0.3, "description": "감정 조절 능력"},
                "empathy_level": {"weight": 0.2, "description": "공감 능력"},
                "emotional_stability": {"weight": 0.2, "description": "감정적 안정성"}
            },
            "cognitive": {
                "problem_solving": {"weight": 0.4, "description": "문제 해결 능력"},
                "logical_thinking": {"weight": 0.3, "description": "논리적 사고"},
                "creativity": {"weight": 0.2, "description": "창의성"},
                "memory_retention": {"weight": 0.1, "description": "기억 보유력"}
            },
            "social": {
                "communication": {"weight": 0.3, "description": "의사소통 능력"},
                "cooperation": {"weight": 0.3, "description": "협력 능력"},
                "conflict_resolution": {"weight": 0.2, "description": "갈등 해결"},
                "leadership": {"weight": 0.2, "description": "리더십"}
            },
            "creative": {
                "originality": {"weight": 0.4, "description": "독창성"},
                "flexibility": {"weight": 0.3, "description": "유연성"},
                "elaboration": {"weight": 0.2, "description": "정교함"},
                "fluency": {"weight": 0.1, "description": "유창성"}
            },
            "problem_solving": {
                "analysis": {"weight": 0.3, "description": "분석 능력"},
                "strategy": {"weight": 0.3, "description": "전략 수립"},
                "execution": {"weight": 0.2, "description": "실행 능력"},
                "evaluation": {"weight": 0.2, "description": "평가 능력"}
            },
            "self_reflection": {
                "self_awareness": {"weight": 0.4, "description": "자기 인식"},
                "metacognition": {"weight": 0.3, "description": "메타인지"},
                "growth_mindset": {"weight": 0.2, "description": "성장 마인드셋"},
                "adaptability": {"weight": 0.1, "description": "적응력"}
            }
        }
    
    def _initialize_scoring_weights(self) -> Dict[str, float]:
        """채점 가중치 초기화"""
        return {
            "difficulty_multiplier": {
                QuestDifficulty.VERY_EASY: 1.0,
                QuestDifficulty.EASY: 1.2,
                QuestDifficulty.MEDIUM: 1.5,
                QuestDifficulty.HARD: 2.0,
                QuestDifficulty.VERY_HARD: 2.5
            },
            "time_bonus": {
                "fast_completion": 0.1,  # 빠른 완료 보너스
                "efficient_execution": 0.05  # 효율적 실행 보너스
            },
            "attempt_penalty": {
                "first_attempt": 0.0,
                "second_attempt": -0.1,
                "third_attempt": -0.2
            }
        }
    
    def _initialize_feedback_templates(self) -> Dict[str, str]:
        """피드백 템플릿 초기화"""
        return {
            "excellent": "훌륭합니다! 이 퀘스트를 완벽하게 수행했습니다. {score:.1%}의 점수로 통과입니다.",
            "good": "잘했습니다! 퀘스트를 성공적으로 완료했습니다. {score:.1%}의 점수입니다.",
            "satisfactory": "만족스럽습니다. 퀘스트를 통과했지만 개선 여지가 있습니다. {score:.1%}의 점수입니다.",
            "needs_improvement": "퀘스트를 통과했지만 더 많은 노력이 필요합니다. {score:.1%}의 점수입니다.",
            "failed": "퀘스트에 실패했습니다. 다시 시도해보세요. {score:.1%}의 점수입니다."
        }
    
    def calculate_quest_score(self, quest: Quest, performance_data: Dict[str, Any]) -> QuestEvaluation:
        """퀘스트 점수 계산"""
        try:
            logger.info(f"퀘스트 점수 계산 시작: {quest.id}")
            
            # 1. 기본 점수 계산
            base_score = self._calculate_base_score(quest, performance_data)
            
            # 2. 난이도 보정
            difficulty_adjusted_score = self._apply_difficulty_multiplier(base_score, quest.difficulty)
            
            # 3. 시간 보너스/페널티 적용
            time_adjusted_score = self._apply_time_adjustments(difficulty_adjusted_score, quest, performance_data)
            
            # 4. 시도 횟수 페널티 적용
            final_score = self._apply_attempt_penalty(time_adjusted_score, quest.attempts)
            
            # 5. 통과 여부 결정
            passed = final_score >= 0.7  # 70% 이상이면 통과
            
            # 6. 피드백 생성
            feedback = self._generate_feedback(quest, final_score, performance_data)
            
            evaluation = QuestEvaluation(
                quest_id=quest.id,
                score=final_score,
                passed=passed,
                feedback=feedback,
                completion_time=performance_data.get("completion_time"),
                timestamp=datetime.now().isoformat()
            )
            
            logger.info(f"퀘스트 점수 계산 완료: {quest.id}, 점수: {final_score:.3f}, 통과: {passed}")
            
            return evaluation
            
        except Exception as e:
            logger.error(f"퀘스트 점수 계산 오류: {e}")
            return self._create_error_evaluation(quest.id, str(e))
    
    def _calculate_base_score(self, quest: Quest, performance_data: Dict[str, Any]) -> float:
        """기본 점수 계산"""
        category = quest.category.value
        criteria = self.evaluation_criteria.get(category, {})
        
        total_score = 0.0
        total_weight = 0.0
        
        for criterion, config in criteria.items():
            weight = config["weight"]
            criterion_score = performance_data.get(criterion, 0.0)
            
            total_score += criterion_score * weight
            total_weight += weight
        
        if total_weight > 0:
            return total_score / total_weight
        else:
            return 0.0
    
    def _apply_difficulty_multiplier(self, base_score: float, difficulty: QuestDifficulty) -> float:
        """난이도 보정 적용"""
        multiplier = self.scoring_weights["difficulty_multiplier"].get(difficulty, 1.0)
        return min(1.0, base_score * multiplier)
    
    def _apply_time_adjustments(self, score: float, quest: Quest, performance_data: Dict[str, Any]) -> float:
        """시간 보정 적용"""
        adjusted_score = score
        
        # 시간 제한이 있는 경우
        if quest.time_limit and "completion_time" in performance_data:
            completion_time = performance_data["completion_time"]
            time_ratio = completion_time / quest.time_limit
            
            if time_ratio < 0.5:  # 50% 이내 완료
                adjusted_score += self.scoring_weights["time_bonus"]["fast_completion"]
            elif time_ratio < 0.8:  # 80% 이내 완료
                adjusted_score += self.scoring_weights["time_bonus"]["efficient_execution"]
        
        return min(1.0, adjusted_score)
    
    def _apply_attempt_penalty(self, score: float, attempts: int) -> float:
        """시도 횟수 페널티 적용"""
        if attempts <= 1:
            penalty = self.scoring_weights["attempt_penalty"]["first_attempt"]
        elif attempts == 2:
            penalty = self.scoring_weights["attempt_penalty"]["second_attempt"]
        else:
            penalty = self.scoring_weights["attempt_penalty"]["third_attempt"]
        
        return max(0.0, score + penalty)
    
    def _generate_feedback(self, quest: Quest, score: float, performance_data: Dict[str, Any]) -> Dict[str, Any]:
        """피드백 생성"""
        # 점수별 피드백 템플릿 선택
        if score >= 0.9:
            template_key = "excellent"
        elif score >= 0.8:
            template_key = "good"
        elif score >= 0.7:
            template_key = "satisfactory"
        elif score >= 0.6:
            template_key = "needs_improvement"
        else:
            template_key = "failed"
        
        feedback_text = self.feedback_templates[template_key].format(score=score)
        
        # 세부 피드백 생성
        detailed_feedback = {
            "overall_feedback": feedback_text,
            "score_breakdown": self._generate_score_breakdown(quest, performance_data),
            "improvement_suggestions": self._generate_improvement_suggestions(quest, performance_data),
            "strengths": self._identify_strengths(performance_data),
            "weaknesses": self._identify_weaknesses(performance_data)
        }
        
        return detailed_feedback
    
    def _generate_score_breakdown(self, quest: Quest, performance_data: Dict[str, Any]) -> Dict[str, float]:
        """점수 세부 분석"""
        category = quest.category.value
        criteria = self.evaluation_criteria.get(category, {})
        
        breakdown = {}
        for criterion, config in criteria.items():
            breakdown[criterion] = performance_data.get(criterion, 0.0)
        
        return breakdown
    
    def _generate_improvement_suggestions(self, quest: Quest, performance_data: Dict[str, Any]) -> List[str]:
        """개선 제안 생성"""
        suggestions = []
        category = quest.category.value
        
        if category == "emotional":
            if performance_data.get("emotion_regulation", 0.0) < 0.7:
                suggestions.append("감정 조절 능력을 향상시키기 위해 명상이나 호흡 운동을 시도해보세요.")
            if performance_data.get("empathy_level", 0.0) < 0.7:
                suggestions.append("다른 사람의 관점을 이해하는 연습을 통해 공감 능력을 키워보세요.")
        
        elif category == "cognitive":
            if performance_data.get("problem_solving", 0.0) < 0.7:
                suggestions.append("문제를 단계별로 분석하는 습관을 들여보세요.")
            if performance_data.get("creativity", 0.0) < 0.7:
                suggestions.append("다양한 관점에서 생각해보는 연습을 통해 창의성을 키워보세요.")
        
        return suggestions
    
    def _identify_strengths(self, performance_data: Dict[str, Any]) -> List[str]:
        """강점 식별"""
        strengths = []
        for criterion, score in performance_data.items():
            if score >= 0.8:
                strengths.append(f"{criterion}: {score:.1%}")
        return strengths
    
    def _identify_weaknesses(self, performance_data: Dict[str, Any]) -> List[str]:
        """약점 식별"""
        weaknesses = []
        for criterion, score in performance_data.items():
            if score < 0.6:
                weaknesses.append(f"{criterion}: {score:.1%}")
        return weaknesses
    
    def _create_error_evaluation(self, quest_id: str, error_message: str) -> QuestEvaluation:
        """오류 평가 생성"""
        return QuestEvaluation(
            quest_id=quest_id,
            score=0.0,
            passed=False,
            feedback={
                "error": error_message,
                "overall_feedback": "퀘스트 평가 중 오류가 발생했습니다."
            },
            timestamp=datetime.now().isoformat()
        )

# 전역 인스턴스
quest_calculator = QuestCalculator() 