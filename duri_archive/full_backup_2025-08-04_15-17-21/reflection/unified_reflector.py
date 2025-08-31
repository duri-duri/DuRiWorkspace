"""
DuRi 통합 반성 시스템 (UnifiedReflectionSystem)

기존 반성 시스템들을 통합하여 일관된 인터페이스를 제공합니다.
Phase 2.1: chatgpt_feedback + learning_cycle 통합
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from enum import Enum
from dataclasses import dataclass

# 기존 시스템들 import
from duri_modules.reflection.reflector import DuRiSelfReflector
from duri_brain.learning.auto_retrospector import get_auto_retrospector
from duri_brain.reflection.response_reflector import get_response_reflector
from duri_brain.learning.insight_self_reflection import get_insight_reflector
from duri_brain.thinking.phase_23_consciousness_ai import get_phase23_system

logger = logging.getLogger(__name__)

class ReflectionType(Enum):
    """반성 유형"""
    CHATGPT_FEEDBACK = "chatgpt_feedback"
    LEARNING_CYCLE = "learning_cycle"
    RESPONSE = "response"
    INSIGHT = "insight"
    CONSCIOUSNESS = "consciousness"

@dataclass
class UnifiedReflectionResult:
    """통합 반성 결과"""
    reflection_type: ReflectionType
    context: str
    issue_identified: str
    insight: str
    action_plan: List[str]
    confidence: float
    applied: bool
    timestamp: datetime
    original_result: Dict[str, Any]

class UnifiedReflectionSystem:
    """DuRi 통합 반성 시스템 - 기존 시스템들을 래핑하여 일관된 인터페이스 제공"""
    
    def __init__(self):
        """UnifiedReflectionSystem 초기화"""
        # 기존 시스템들 초기화
        self.chatgpt_reflector = DuRiSelfReflector()
        self.learning_reflector = get_auto_retrospector()
        self.response_reflector = get_response_reflector()
        self.insight_reflector = get_insight_reflector()
        self.consciousness_system = get_phase23_system()
        
        # 통합 결과 저장소
        self.unified_reflection_history: List[UnifiedReflectionResult] = []
        
        logger.info("🧠 DuRi 통합 반성 시스템 초기화 완료")
    
    def reflect(self, event_type: str, event_data: Dict[str, Any]) -> UnifiedReflectionResult:
        """통합 반성 수행 - 기존 시스템들을 래핑"""
        try:
            logger.info(f"🔄 통합 반성 시작: {event_type}")
            
            # 이벤트 타입에 따른 반성 수행
            if event_type == "chatgpt_feedback":
                original_result = self._perform_chatgpt_reflection(event_data)
                reflection_type = ReflectionType.CHATGPT_FEEDBACK
                
            elif event_type == "learning_cycle":
                original_result = self._perform_learning_reflection(event_data)
                reflection_type = ReflectionType.LEARNING_CYCLE
                
            elif event_type == "response":
                original_result = self._perform_response_reflection(event_data)
                reflection_type = ReflectionType.RESPONSE
                
            elif event_type == "insight":
                original_result = self._perform_insight_reflection(event_data)
                reflection_type = ReflectionType.INSIGHT
                
            elif event_type == "consciousness":
                original_result = self._perform_consciousness_reflection(event_data)
                reflection_type = ReflectionType.CONSCIOUSNESS
                
            else:
                raise ValueError(f"지원하지 않는 이벤트 타입: {event_type}")
            
            # 통합 결과로 변환
            unified_result = self._convert_to_unified_format(
                reflection_type, event_data, original_result
            )
            
            # 통합 결과 저장
            self.unified_reflection_history.append(unified_result)
            
            logger.info(f"✅ 통합 반성 완료: {event_type} - 신뢰도: {unified_result.confidence:.3f}")
            return unified_result
            
        except Exception as e:
            logger.error(f"❌ 통합 반성 오류: {e}")
            return self._create_error_result(event_type, str(e))
    
    def _perform_chatgpt_reflection(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """ChatGPT 피드백 기반 반성 수행"""
        chatgpt_evaluation = event_data.get("chatgpt_evaluation", {})
        original_response = event_data.get("original_response", "")
        user_question = event_data.get("user_question", "")
        
        return self.chatgpt_reflector.reflect_on_chatgpt_feedback(
            chatgpt_evaluation, original_response, user_question
        )
    
    def _perform_learning_reflection(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """학습 사이클 기반 반성 수행"""
        improvement_result = event_data.get("improvement_result", {})
        
        return self.learning_reflector.reflect_on_learning_cycle(improvement_result)
    
    def _perform_response_reflection(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """답변 품질 기반 반성 수행"""
        conversation = event_data.get("conversation", "")
        response_quality = event_data.get("response_quality", 0.5)
        learning_value = event_data.get("learning_value", 0.5)
        
        return self.response_reflector.reflect_on_response(
            conversation, response_quality, learning_value
        )
    
    def _perform_insight_reflection(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """통찰 기반 반성 수행"""
        # InsightSelfReflector는 세션 기록과 통찰 생성을 분리하여 처리
        session_record = event_data.get("session_record", {})
        reflection_insights = event_data.get("reflection_insights", [])
        
        if session_record:
            # 세션 기록이 있으면 기록
            from duri_brain.learning.insight_self_reflection import InsightSessionRecord, InsightOutcome
            record = InsightSessionRecord(
                session_id=session_record.get("session_id", "unknown"),
                problem=session_record.get("problem", ""),
                trigger_type=session_record.get("trigger_type", ""),
                phases_completed=session_record.get("phases_completed", []),
                candidates_generated=session_record.get("candidates_generated", 0),
                final_insight=session_record.get("final_insight"),
                outcome=InsightOutcome(session_record.get("outcome", "failure")),
                duration=session_record.get("duration", 0.0),
                confidence=session_record.get("confidence", 0.0),
                timestamp=datetime.now()
            )
            self.insight_reflector.record_session(record)
        
        # 통찰 생성
        insights = self.insight_reflector.generate_reflection_insights()
        
        return {
            "insights": [insight.__dict__ for insight in insights],
            "total_insights": len(insights),
            "session_count": len(self.insight_reflector.session_history),
            "success_rate": self.insight_reflector.analyze_recent_sessions().get("success_rate", 0.0)
        }
    
    def _perform_consciousness_reflection(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """의식적 반성 수행"""
        reflection_topic = event_data.get("reflection_topic", "일반적인 자기 반성")
        
        # Phase23ConsciousnessAI의 자기 반성 세션 수행
        session = self.consciousness_system.engage_self_reflection(reflection_topic)
        
        return {
            "session_id": session.session_id,
            "reflection_topic": session.reflection_topic,
            "self_analysis": session.self_analysis,
            "insights_gained": session.insights_gained,
            "behavioral_change": session.behavioral_change,
            "growth_direction": session.growth_direction,
            "created_at": session.created_at.isoformat(),
            "consciousness_level": self.consciousness_system.current_capabilities.get("self_reflection", 0.6)
        }
    
    def _convert_to_unified_format(
        self, 
        reflection_type: ReflectionType, 
        event_data: Dict[str, Any], 
        original_result: Dict[str, Any]
    ) -> UnifiedReflectionResult:
        """기존 결과를 통합 형식으로 변환"""
        
        # 이슈 식별
        issue_identified = self._extract_issue_identified(original_result, reflection_type)
        
        # 통찰 추출
        insight = self._extract_insight(original_result, reflection_type)
        
        # 액션 플랜 추출
        action_plan = self._extract_action_plan(original_result, reflection_type)
        
        # 신뢰도 계산
        confidence = self._calculate_confidence(original_result, reflection_type)
        
        return UnifiedReflectionResult(
            reflection_type=reflection_type,
            context=str(event_data),
            issue_identified=issue_identified,
            insight=insight,
            action_plan=action_plan,
            confidence=confidence,
            applied=False,
            timestamp=datetime.now(),
            original_result=original_result
        )
    
    def _extract_issue_identified(self, original_result: Dict[str, Any], reflection_type: ReflectionType) -> str:
        """이슈 식별 추출"""
        if reflection_type == ReflectionType.CHATGPT_FEEDBACK:
            accepted_criticisms = original_result.get("accepted_criticisms", [])
            if accepted_criticisms:
                return "; ".join(accepted_criticisms[:3])  # 최대 3개
            return "ChatGPT 평가에서 특별한 이슈가 발견되지 않음"
            
        elif reflection_type == ReflectionType.LEARNING_CYCLE:
            accepted_criticisms = original_result.get("accepted_criticisms", [])
            if accepted_criticisms:
                return "; ".join(accepted_criticisms[:3])  # 최대 3개
            return "학습 사이클에서 특별한 이슈가 발견되지 않음"
            
        elif reflection_type == ReflectionType.RESPONSE:
            improvement_areas = original_result.get("improvement_areas", [])
            if improvement_areas:
                return "; ".join(improvement_areas[:3])  # 최대 3개
            return "답변 품질에서 특별한 이슈가 발견되지 않음"
            
        elif reflection_type == ReflectionType.INSIGHT:
            insights = original_result.get("insights", [])
            if insights:
                # 첫 번째 통찰의 action_plan을 이슈로 사용
                first_insight = insights[0]
                return first_insight.get("action_plan", "통찰 기반 개선 필요")
            return "통찰 시스템에서 특별한 이슈가 발견되지 않음"
            
        elif reflection_type == ReflectionType.CONSCIOUSNESS:
            behavioral_change = original_result.get("behavioral_change", "")
            if behavioral_change:
                return behavioral_change
            return "의식적 반성에서 특별한 이슈가 발견되지 않음"
        
        return "이슈 식별 불가"
    
    def _extract_insight(self, original_result: Dict[str, Any], reflection_type: ReflectionType) -> str:
        """통찰 추출"""
        if reflection_type == ReflectionType.CHATGPT_FEEDBACK:
            improvement_proposal = original_result.get("improvement_proposal", {})
            reasoning = improvement_proposal.get("reasoning", "")
            if reasoning:
                return reasoning
            return "ChatGPT 피드백을 통한 개선 통찰"
            
        elif reflection_type == ReflectionType.LEARNING_CYCLE:
            improvement_proposal = original_result.get("improvement_proposal", {})
            reasoning = improvement_proposal.get("reasoning", "")
            if reasoning:
                return reasoning
            return "학습 사이클을 통한 개선 통찰"
            
        elif reflection_type == ReflectionType.RESPONSE:
            overall_assessment = original_result.get("overall_assessment", "")
            if overall_assessment:
                return overall_assessment
            return "답변 품질을 통한 개선 통찰"
            
        elif reflection_type == ReflectionType.INSIGHT:
            insights = original_result.get("insights", [])
            if insights:
                # 모든 통찰의 insight를 결합
                insight_texts = [insight.get("insight", "") for insight in insights]
                return "; ".join(insight_texts)
            return "통찰 시스템을 통한 개선 통찰"
            
        elif reflection_type == ReflectionType.CONSCIOUSNESS:
            insights_gained = original_result.get("insights_gained", "")
            if insights_gained:
                return insights_gained
            return "의식적 반성을 통한 개선 통찰"
        
        return "통찰 추출 불가"
    
    def _extract_action_plan(self, original_result: Dict[str, Any], reflection_type: ReflectionType) -> List[str]:
        """액션 플랜 추출"""
        if reflection_type == ReflectionType.CHATGPT_FEEDBACK:
            improvement_proposal = original_result.get("improvement_proposal", {})
            specific_improvements = improvement_proposal.get("specific_improvements", [])
            return specific_improvements[:5]  # 최대 5개
            
        elif reflection_type == ReflectionType.LEARNING_CYCLE:
            improvement_proposal = original_result.get("improvement_proposal", {})
            specific_improvements = improvement_proposal.get("specific_improvements", [])
            return specific_improvements[:5]  # 최대 5개
            
        elif reflection_type == ReflectionType.RESPONSE:
            action_plan = original_result.get("action_plan", [])
            return action_plan[:5]  # 최대 5개
            
        elif reflection_type == ReflectionType.INSIGHT:
            insights = original_result.get("insights", [])
            action_plans = []
            for insight in insights:
                action_plan = insight.get("action_plan", "")
                if action_plan:
                    action_plans.append(action_plan)
            return action_plans[:5]  # 최대 5개
            
        elif reflection_type == ReflectionType.CONSCIOUSNESS:
            growth_direction = original_result.get("growth_direction", "")
            if growth_direction:
                return [growth_direction]
            return []
        
        return []
    
    def _calculate_confidence(self, original_result: Dict[str, Any], reflection_type: ReflectionType) -> float:
        """신뢰도 계산"""
        if reflection_type == ReflectionType.CHATGPT_FEEDBACK:
            self_assessment = original_result.get("self_assessment", {})
            return self_assessment.get("confidence", 0.5)
            
        elif reflection_type == ReflectionType.LEARNING_CYCLE:
            self_assessment = original_result.get("self_assessment", {})
            return self_assessment.get("confidence", 0.5)
            
        elif reflection_type == ReflectionType.RESPONSE:
            response_quality = original_result.get("response_quality", 0.5)
            learning_value = original_result.get("learning_value", 0.5)
            # 품질과 학습 가치의 평균으로 신뢰도 계산
            return (response_quality + learning_value) / 2
            
        elif reflection_type == ReflectionType.INSIGHT:
            insights = original_result.get("insights", [])
            if insights:
                # 모든 통찰의 평균 신뢰도
                confidences = [insight.get("confidence", 0.5) for insight in insights]
                return sum(confidences) / len(confidences)
            return 0.5
            
        elif reflection_type == ReflectionType.CONSCIOUSNESS:
            consciousness_level = original_result.get("consciousness_level", 0.6)
            return consciousness_level
        
        return 0.5
    
    def _create_error_result(self, event_type: str, error_message: str) -> UnifiedReflectionResult:
        """오류 결과 생성"""
        return UnifiedReflectionResult(
            reflection_type=ReflectionType.CHATGPT_FEEDBACK,  # 기본값
            context=f"오류 발생: {event_type}",
            issue_identified=f"반성 처리 중 오류: {error_message}",
            insight="오류로 인해 통찰을 도출할 수 없음",
            action_plan=["오류 해결 후 재시도"],
            confidence=0.0,
            applied=False,
            timestamp=datetime.now(),
            original_result={"error": error_message}
        )
    
    def get_reflection_history(self, limit: int = 10) -> List[UnifiedReflectionResult]:
        """반성 기록 조회"""
        return self.unified_reflection_history[-limit:]
    
    def get_reflection_statistics(self) -> Dict[str, Any]:
        """반성 통계 조회"""
        if not self.unified_reflection_history:
            return {"message": "반성 기록이 없습니다"}
        
        total_reflections = len(self.unified_reflection_history)
        type_counts = {}
        confidence_sum = 0.0
        
        for reflection in self.unified_reflection_history:
            reflection_type = reflection.reflection_type.value
            type_counts[reflection_type] = type_counts.get(reflection_type, 0) + 1
            confidence_sum += reflection.confidence
        
        avg_confidence = confidence_sum / total_reflections if total_reflections > 0 else 0
        
        return {
            "total_reflections": total_reflections,
            "type_counts": type_counts,
            "average_confidence": avg_confidence,
            "applied_count": len([r for r in self.unified_reflection_history if r.applied])
        }
    
    def apply_reflection_result(self, reflection_id: int) -> bool:
        """반성 결과 적용"""
        if 0 <= reflection_id < len(self.unified_reflection_history):
            reflection = self.unified_reflection_history[reflection_id]
            reflection.applied = True
            logger.info(f"✅ 반성 결과 적용: {reflection.reflection_type.value}")
            return True
        return False

def get_unified_reflection_system() -> UnifiedReflectionSystem:
    """UnifiedReflectionSystem 인스턴스를 반환합니다."""
    return UnifiedReflectionSystem() 