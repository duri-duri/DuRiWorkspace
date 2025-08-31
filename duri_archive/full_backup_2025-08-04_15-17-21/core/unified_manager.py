#!/usr/bin/env python3
"""
DuRi 통합 관리자 - 완전한 생애 루프 구현
"입력 → 판단 → 시험 → 성장 → 자아 피드백"
"""

import logging
from typing import Dict, Any, Optional
from ..emotion.emotion_manager import EmotionManager
from ..growth.growth_manager import GrowthManager
from ..judgment.judgment_manager import JudgmentManager
from ..reflection.self_reflection_engine import SelfReflectionEngine
from ..reflection.milestone_tracker import MilestoneTracker
from ..reflection.performance_scorer import PerformanceScorer
from ..quest.auto_generator import QuestAutoGenerator

logger = logging.getLogger(__name__)

class UnifiedManager:
    """통합 관리자 - 완전한 생애 루프 구현"""
    
    def __init__(self):
        self.emotion_manager = EmotionManager()
        self.growth_manager = GrowthManager()
        self.judgment_manager = JudgmentManager()
        
        # Phase 2: 자가 반영 및 자율 퀘스트 시스템
        self.self_reflection_engine = SelfReflectionEngine()
        self.milestone_tracker = MilestoneTracker()
        self.performance_scorer = PerformanceScorer()
        self.quest_auto_generator = QuestAutoGenerator()
        
        # 모듈 간 연동 설정
        self._setup_module_connections()
        
        logger.info("통합 관리자 초기화 완료")
    
    def _setup_module_connections(self):
        """모듈 간 연동 설정"""
        # Growth ↔ Judgment 연동
        self.growth_manager.set_judgment_manager(self.judgment_manager)
        
        # Self Reflection 연동
        self.growth_manager.set_self_reflection(self.self_reflection_engine)
        
        logger.info("모듈 간 연동 설정 완료")
    
    def process_complete_cycle(self, user_input: str) -> Dict[str, Any]:
        """완전한 생애 루프 처리"""
        try:
            # 1. 입력 처리
            processed_input = self._preprocess_input(user_input)
            
            # 2. 감정 분석 (판단 기반)
            emotion_result = self.emotion_manager.analyze_emotion(processed_input)
            
            # 3. 성장 사이클 처리 (시험 포함)
            growth_result = self.growth_manager.process_growth_cycle(processed_input)
            
            # 4. 자가 반영 및 성과 측정
            reflection_entry = self._create_reflection_entry(emotion_result, growth_result)
            performance_score = self._measure_performance(emotion_result, growth_result)
            
            # 5. 자율 퀘스트 생성
            auto_quest = self._generate_auto_quest(reflection_entry, growth_result)
            
            # 6. 자아 피드백 생성
            self_feedback = self._generate_self_feedback(emotion_result, growth_result, reflection_entry, performance_score)
            
            # 7. 다음 사이클을 위한 준비
            next_cycle_preparation = self._prepare_next_cycle(self_feedback, auto_quest)
            
            return {
                "emotion": emotion_result,
                "growth": growth_result,
                "reflection": reflection_entry,
                "performance": performance_score,
                "auto_quest": auto_quest,
                "self_feedback": self_feedback,
                "next_cycle_preparation": next_cycle_preparation,
                "cycle_status": "completed"
            }
            
        except Exception as e:
            logger.error(f"생애 루프 처리 오류: {e}")
            return {
                "error": str(e),
                "cycle_status": "error"
            }
    
    def _preprocess_input(self, user_input: str) -> str:
        """입력 전처리"""
        # 간소화된 전처리
        processed = user_input.strip()
        return processed
    
    def _create_reflection_entry(self, emotion_result: Dict[str, Any], 
                                growth_result: Dict[str, Any]) -> Dict[str, Any]:
        """자가 반영 일지 생성"""
        from ..reflection.self_reflection_engine import ReflectionType
        
        # 감정 상태
        emotion_state = emotion_result.get("emotion_state", {})
        current_emotion = emotion_state.get("current_emotion", "neutral")
        
        # 성장 지표
        growth_metrics = growth_result.get("growth_metrics", {})
        if hasattr(growth_metrics, 'current_level'):
            current_level = growth_metrics.current_level
            experience_points = growth_metrics.experience_points
        else:
            current_level = growth_metrics.get("current_level", 1)
            experience_points = growth_metrics.get("experience_points", 0)
        
        # 성장 영향도 계산
        growth_impact = min(1.0, experience_points / 100.0)
        
        # 반영 데이터 구성
        reflection_data = {
            "emotion_state": current_emotion,
            "current_level": current_level,
            "experience_points": experience_points,
            "growth_impact": growth_impact,
            "emotion_analysis": emotion_result.get("emotion_analysis", {}),
            "growth_metrics": growth_metrics
        }
        
        # 자가 반영 일지 생성
        reflection_entry = self.self_reflection_engine.create_reflection(
            reflection_type=ReflectionType.INTEGRATION,
            data=reflection_data,
            emotional_state=current_emotion,
            growth_impact=growth_impact
        )
        
        # ReflectionEntry 객체를 딕셔너리로 변환
        from dataclasses import asdict
        return asdict(reflection_entry)
    
    def _measure_performance(self, emotion_result: Dict[str, Any], 
                            growth_result: Dict[str, Any]) -> Dict[str, Any]:
        """성과 측정"""
        # 루프 데이터 구성
        loop_data = {
            "duration": 1.0,  # 기본값
            "complexity": 0.5,
            "emotional_stability": 0.7,
            "emotional_insight": 0.6,
            "cognitive_complexity": 0.5,
            "social_interaction": 0.3,
            "empathy_level": 0.5,
            "communication_quality": 0.5,
            "creative_expression": 0.4,
            "innovative_thinking": 0.5,
            "artistic_sensitivity": 0.4,
            "problem_complexity": 0.5,
            "solution_effectiveness": 0.6,
            "change_response": 0.5,
            "learning_speed": 0.5,
            "stress_management": 0.5,
            "self_direction": 0.4,
            "decision_independence": 0.5,
            "initiative_level": 0.5
        }
        
        # 감정 상태
        emotion_state = emotion_result.get("emotion_state", {})
        current_emotion = emotion_state.get("current_emotion", "neutral")
        
        # 성장 지표
        growth_metrics = growth_result.get("growth_metrics", {})
        if hasattr(growth_metrics, 'current_level'):
            growth_metrics_dict = {
                "current_level": growth_metrics.current_level,
                "experience_points": growth_metrics.experience_points,
                "emotional_maturity": growth_metrics.emotional_maturity,
                "cognitive_development": growth_metrics.cognitive_development,
                "social_skills": growth_metrics.social_skills,
                "self_motivation": growth_metrics.self_motivation
            }
        else:
            growth_metrics_dict = growth_metrics
        
        # 판단 결과 (기본값)
        judgment_result = {
            "overall_bias_score": 0.0
        }
        
        # 성과 측정
        performance = self.performance_scorer.score_loop_performance(
            loop_data=loop_data,
            emotional_state=current_emotion,
            growth_metrics=growth_metrics_dict,
            judgment_result=judgment_result
        )
        
        # LoopPerformance 객체를 딕셔너리로 변환
        from dataclasses import asdict
        return asdict(performance)
    
    def _generate_auto_quest(self, reflection_entry: Dict[str, Any], 
                            growth_result: Dict[str, Any]) -> Dict[str, Any]:
        """자율 퀘스트 생성"""
        # 성찰 데이터
        reflection_data = {
            "reflection_type": reflection_entry.get("reflection_type", "integration"),
            "insights": reflection_entry.get("insights", []),
            "action_items": reflection_entry.get("action_items", [])
        }
        
        # 현재 레벨
        growth_metrics = growth_result.get("growth_metrics", {})
        if hasattr(growth_metrics, 'current_level'):
            current_level = growth_metrics.current_level
        else:
            current_level = growth_metrics.get("current_level", 1)
        
        # 감정 상태
        emotional_state = reflection_entry.get("emotional_state", "neutral")
        
        # 자율 퀘스트 생성
        auto_quest = self.quest_auto_generator.generate_quest_from_reflection(
            reflection_data=reflection_data,
            current_level=current_level,
            emotional_state=emotional_state
        )
        
        # AutoQuest 객체를 딕셔너리로 변환
        from dataclasses import asdict
        return asdict(auto_quest)
    
    def _generate_self_feedback(self, emotion_result: Dict[str, Any], 
                               growth_result: Dict[str, Any],
                               reflection_entry: Dict[str, Any],
                               performance_score: Dict[str, Any]) -> Dict[str, Any]:
        """자아 피드백 생성"""
        # 감정 상태 분석
        emotion_state = emotion_result.get("emotion_state", {})
        emotion_analysis = emotion_result.get("emotion_analysis", {})
        
        # 성장 상태 분석
        growth_metrics = growth_result.get("growth_metrics", {})
        if hasattr(growth_metrics, 'current_level'):
            growth_metrics = {
                "current_level": growth_metrics.current_level,
                "experience_points": growth_metrics.experience_points,
                "emotional_maturity": growth_metrics.emotional_maturity,
                "cognitive_development": growth_metrics.cognitive_development,
                "social_skills": growth_metrics.social_skills,
                "self_motivation": growth_metrics.self_motivation
            }
        quest_progress = growth_result.get("quest_progress", {})
        
        # 자아 피드백 생성 (Phase 2 확장)
        feedback = {
            "reflection_insights": reflection_entry.get("insights", []),
            "performance_rating": performance_score.get("overall_score", 0.0),
            "recommendations": performance_score.get("recommendations", []),
            "emotion_awareness": emotion_state.get("bias_detected", False),
            "growth_progress": quest_progress.get("progress", 0.0),
            "current_level": growth_metrics.get("current_level", 1),
            "recommendations": self._generate_recommendations(emotion_result, growth_result)
        }
        
        return feedback
    
    def _generate_recommendations(self, emotion_result: Dict[str, Any], 
                                 growth_result: Dict[str, Any]) -> list:
        """권장사항 생성"""
        recommendations = []
        
        # 감정 기반 권장사항
        emotion_state = emotion_result.get("emotion_state", {})
        if emotion_state.get("bias_detected", False):
            recommendations.append("감정 편향을 인식하고 객관적 판단을 시도하세요.")
        
        # 성장 기반 권장사항
        quest_progress = growth_result.get("quest_progress", {})
        if quest_progress.get("progress", 0.0) < 0.5:
            recommendations.append("퀘스트 진행도를 높이기 위해 더 많은 노력을 기울이세요.")
        
        # 기본 권장사항
        if not recommendations:
            recommendations.append("현재 상태가 양호합니다. 계속해서 성장해 나가세요.")
        
        return recommendations
    
    def _prepare_next_cycle(self, self_feedback: Dict[str, Any], auto_quest: Dict[str, Any]) -> Dict[str, Any]:
        """다음 사이클 준비"""
        return {
            "should_continue": True,
            "focus_areas": self._identify_focus_areas(self_feedback),
            "preparation_notes": "다음 사이클을 위한 준비가 완료되었습니다.",
            "auto_quest": auto_quest
        }
    
    def _identify_focus_areas(self, self_feedback: Dict[str, Any]) -> list:
        """중점 영역 식별"""
        focus_areas = []
        
        if self_feedback.get("emotion_awareness", False):
            focus_areas.append("감정 인식 및 조절")
        
        if self_feedback.get("growth_progress", 0.0) < 0.5:
            focus_areas.append("성장 가속화")
        
        if not focus_areas:
            focus_areas.append("균형잡힌 발전")
        
        return focus_areas
    
    def get_system_status(self) -> Dict[str, Any]:
        """시스템 상태 반환"""
        return {
            "emotion_status": self.emotion_manager.get_emotion_state(),
            "growth_status": self.growth_manager.get_growth_status(),
            "judgment_status": self.judgment_manager.get_judgment_status(),
            "system_health": self._assess_system_health()
        }
    
    def _assess_system_health(self) -> Dict[str, Any]:
        """시스템 건강도 평가"""
        # 각 모듈의 상태를 종합하여 시스템 건강도 평가
        emotion_state = self.emotion_manager.get_emotion_state()
        growth_status = self.growth_manager.get_growth_status()
        judgment_status = self.judgment_manager.get_judgment_status()
        
        # 간소화된 건강도 평가
        health_score = 0.0
        health_issues = []
        
        # 감정 상태 평가
        if emotion_state.get("bias_detected", False):
            health_score += 0.3
            health_issues.append("감정 편향 감지")
        else:
            health_score += 0.7
        
        # 성장 상태 평가
        current_level = growth_status.get("level_system", {}).get("current_level", 1)
        if current_level > 1:
            health_score += 0.7
        else:
            health_score += 0.3
            health_issues.append("초기 성장 단계")
        
        # 판단 상태 평가
        bias_metrics = judgment_status.get("bias_metrics", {})
        if bias_metrics.get("average_bias_score", 0.0) < 0.5:
            health_score += 0.7
        else:
            health_score += 0.3
            health_issues.append("편향 수준 높음")
        
        final_health_score = health_score / 3.0
        
        return {
            "overall_health": final_health_score,
            "health_issues": health_issues,
            "recommendations": self._generate_health_recommendations(health_issues)
        }
    
    def _generate_health_recommendations(self, health_issues: list) -> list:
        """건강도 기반 권장사항 생성"""
        recommendations = []
        
        for issue in health_issues:
            if "감정 편향" in issue:
                recommendations.append("감정 편향 완화 훈련을 수행하세요.")
            elif "초기 성장" in issue:
                recommendations.append("기본적인 성장에 집중하세요.")
            elif "편향 수준" in issue:
                recommendations.append("객관적 판단 능력을 향상시키세요.")
        
        if not recommendations:
            recommendations.append("시스템 상태가 양호합니다.")
        
        return recommendations
    
    def get_unified_response_format(self) -> Dict[str, Any]:
        """통합 응답 포맷 반환"""
        return {
            "status": "success",
            "data": {},
            "metadata": {
                "timestamp": "2024-01-01T00:00:00Z",
                "module": "unified_manager",
                "version": "1.0"
            }
        } 