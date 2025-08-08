"""
DuRi 답변 반성 시스템 (ResponseReflector)

답변 품질 평가 및 개선 방안 제시를 위한 시스템입니다.
"""

import logging
from typing import Dict, Any, List
from datetime import datetime
from collections import defaultdict

logger = logging.getLogger(__name__)

class ResponseReflector:
    """답변 품질 평가 및 반성 시스템"""
    
    def __init__(self):
        """ResponseReflector 초기화"""
        self.reflection_history = []
        self.improvement_suggestions = []
        
        logger.info("📝 ResponseReflector 초기화 완료")
    
    def reflect_on_response(self, conversation: str, response_quality: float, learning_value: float) -> Dict[str, Any]:
        """답변에 대한 자기 성찰 수행"""
        try:
            logger.info("🤔 답변 품질 반성 시작")
            
            reflection = {
                "timestamp": datetime.now().isoformat(),
                "conversation": conversation,
                "response_quality": response_quality,
                "learning_value": learning_value,
                "self_questions": [],
                "improvement_areas": [],
                "action_plan": [],
                "overall_assessment": ""
            }
            
            # 자기 질문들
            reflection["self_questions"] = [
                "내 답변이 사용자의 질문을 충분히 해결했을까?",
                "더 구체적인 예제가 필요하지 않았을까?",
                "사용자의 수준에 맞는 설명이었을까?",
                "실용적인 정보를 제공했을까?"
            ]
            
            # 개선 영역 분석
            reflection["improvement_areas"] = self._analyze_improvement_areas(
                conversation, response_quality, learning_value
            )
            
            # 액션 플랜 생성
            reflection["action_plan"] = self._generate_action_plan(reflection["improvement_areas"])
            
            # 전체 평가
            reflection["overall_assessment"] = self._generate_overall_assessment(reflection)
            
            # 성찰 기록 저장
            self.reflection_history.append(reflection)
            
            logger.info(f"✅ 답변 품질 반성 완료 - 개선 영역: {len(reflection['improvement_areas'])}개")
            return reflection
            
        except Exception as e:
            logger.error(f"❌ 답변 품질 반성 오류: {e}")
            return {
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
                "improvement_areas": [],
                "action_plan": []
            }
    
    def _analyze_improvement_areas(self, conversation: str, response_quality: float, learning_value: float) -> List[str]:
        """개선 영역 분석"""
        improvement_areas = []
        
        # 답변 품질 분석
        if response_quality < 0.5:
            improvement_areas.append("답변 품질이 낮음 - 더 상세한 설명 필요")
        elif response_quality < 0.7:
            improvement_areas.append("답변 품질 개선 여지 있음 - 더 구체적인 설명 필요")
        
        # 학습 가치 분석
        if learning_value < 0.3:
            improvement_areas.append("학습 가치가 낮음 - 더 교육적인 내용 필요")
        elif learning_value < 0.5:
            improvement_areas.append("학습 가치 개선 여지 있음 - 더 실용적인 내용 필요")
        
        # 대화 길이 분석
        if len(conversation.split()) < 10:
            improvement_areas.append("질문이 간단함 - 더 구체적인 예제 제공 필요")
        elif len(conversation.split()) < 20:
            improvement_areas.append("질문이 중간 수준 - 더 상세한 설명 필요")
        
        return improvement_areas
    
    def _generate_action_plan(self, improvement_areas: List[str]) -> List[str]:
        """개선 영역에 따른 액션 플랜 생성"""
        action_plan = []
        
        for area in improvement_areas:
            if "답변 품질" in area:
                action_plan.append("더 상세한 단계별 설명 추가")
                action_plan.append("코드 예제와 함께 설명")
                action_plan.append("실제 사용 사례 포함")
            elif "학습 가치" in area:
                action_plan.append("실습 예제 포함")
                action_plan.append("관련 개념 연결")
                action_plan.append("단계별 학습 가이드 제공")
            elif "구체적인 예제" in area:
                action_plan.append("실제 사용 사례 추가")
                action_plan.append("단계별 튜토리얼 제공")
                action_plan.append("코드 예제와 함께 설명")
            elif "상세한 설명" in area:
                action_plan.append("개념 설명 강화")
                action_plan.append("실용적 예제 추가")
                action_plan.append("관련 링크 및 참고자료 제공")
        
        return action_plan
    
    def _generate_overall_assessment(self, reflection: Dict[str, Any]) -> str:
        """전체 평가 생성"""
        response_quality = reflection["response_quality"]
        learning_value = reflection["learning_value"]
        improvement_areas = reflection["improvement_areas"]
        
        if response_quality >= 0.8 and learning_value >= 0.7:
            return "우수한 답변 - 높은 품질과 학습 가치"
        elif response_quality >= 0.6 and learning_value >= 0.5:
            return "양호한 답변 - 개선 여지 있음"
        elif len(improvement_areas) <= 2:
            return "보통의 답변 - 부분적 개선 필요"
        else:
            return "개선이 필요한 답변 - 전면적 개선 필요"
    
    def get_improvement_suggestions(self) -> List[str]:
        """전체 개선 제안 수집"""
        suggestions = []
        
        for reflection in self.reflection_history[-5:]:  # 최근 5개 성찰만
            suggestions.extend(reflection["action_plan"])
        
        return list(set(suggestions))  # 중복 제거
    
    def analyze_trends(self) -> Dict[str, Any]:
        """성찰 트렌드 분석"""
        if not self.reflection_history:
            return {"message": "아직 성찰 데이터가 없습니다"}
        
        recent_reflections = self.reflection_history[-10:]  # 최근 10개
        
        avg_response_quality = sum(r["response_quality"] for r in recent_reflections) / len(recent_reflections)
        avg_learning_value = sum(r["learning_value"] for r in recent_reflections) / len(recent_reflections)
        
        improvement_frequency = defaultdict(int)
        for reflection in recent_reflections:
            for area in reflection["improvement_areas"]:
                improvement_frequency[area] += 1
        
        return {
            "avg_response_quality": avg_response_quality,
            "avg_learning_value": avg_learning_value,
            "most_common_improvements": sorted(improvement_frequency.items(), key=lambda x: x[1], reverse=True)[:3],
            "total_reflections": len(self.reflection_history)
        }
    
    def get_reflection_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """반성 기록 조회"""
        return self.reflection_history[-limit:]

def get_response_reflector() -> ResponseReflector:
    """ResponseReflector 인스턴스를 반환합니다."""
    return ResponseReflector() 