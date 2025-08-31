#!/usr/bin/env python3
"""
DuRi Self Reflection Engine
자가 반영 엔진 - 판단, 감정, 성장 결과를 구조화된 일지로 기록
"""

import logging
import json
from datetime import datetime
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict
from enum import Enum

logger = logging.getLogger(__name__)

class ReflectionType(Enum):
    """반영 유형"""
    JUDGMENT = "judgment"
    EMOTION = "emotion"
    GROWTH = "growth"
    QUEST = "quest"
    INTEGRATION = "integration"

class ReflectionLevel(Enum):
    """반영 수준"""
    SURFACE = "surface"      # 표면적 관찰
    ANALYSIS = "analysis"    # 분석적 성찰
    INSIGHT = "insight"      # 깊은 통찰
    TRANSFORMATION = "transformation"  # 변화적 성찰

@dataclass
class ReflectionEntry:
    """반영 일지 항목"""
    timestamp: str
    reflection_type: ReflectionType
    reflection_level: ReflectionLevel
    content: Dict[str, Any]
    insights: List[str]
    action_items: List[str]
    emotional_state: str
    growth_impact: float
    confidence_score: float

class SelfReflectionEngine:
    """자가 반영 엔진"""
    
    def __init__(self):
        self.reflection_log = []
        self.insight_patterns = {}
        self.growth_trajectory = []
        self.emotional_trends = []
        logger.info("자가 반영 엔진 초기화 완료")
    
    def create_reflection(self, 
                         reflection_type: ReflectionType,
                         data: Dict[str, Any],
                         emotional_state: str = "neutral",
                         growth_impact: float = 0.0) -> ReflectionEntry:
        """반영 일지 생성"""
        timestamp = datetime.now().isoformat()
        
        # 반영 수준 결정
        reflection_level = self._determine_reflection_level(data, emotional_state, growth_impact)
        
        # 통찰 생성
        insights = self._generate_insights(data, reflection_type, emotional_state)
        
        # 행동 항목 생성
        action_items = self._generate_action_items(insights, reflection_type)
        
        # 신뢰도 점수 계산
        confidence_score = self._calculate_confidence_score(data, insights)
        
        entry = ReflectionEntry(
            timestamp=timestamp,
            reflection_type=reflection_type,
            reflection_level=reflection_level,
            content=data,
            insights=insights,
            action_items=action_items,
            emotional_state=emotional_state,
            growth_impact=growth_impact,
            confidence_score=confidence_score
        )
        
        self.reflection_log.append(entry)
        self._update_patterns(entry)
        
        logger.info(f"반영 일지 생성 완료: {reflection_type.value} - {reflection_level.value}")
        return entry
    
    def _determine_reflection_level(self, data: Dict[str, Any], emotional_state: str, growth_impact: float) -> ReflectionLevel:
        """반영 수준 결정"""
        # 데이터 복잡도와 감정 상태, 성장 영향도 기반으로 수준 결정
        data_complexity = len(data.keys())
        emotional_intensity = self._calculate_emotional_intensity(emotional_state)
        
        if data_complexity > 10 and emotional_intensity > 0.7 and growth_impact > 0.8:
            return ReflectionLevel.TRANSFORMATION
        elif data_complexity > 5 and emotional_intensity > 0.5 and growth_impact > 0.5:
            return ReflectionLevel.INSIGHT
        elif data_complexity > 3 and emotional_intensity > 0.3 and growth_impact > 0.3:
            return ReflectionLevel.ANALYSIS
        else:
            return ReflectionLevel.SURFACE
    
    def _calculate_emotional_intensity(self, emotional_state: str) -> float:
        """감정 강도 계산"""
        intensity_map = {
            "joy": 0.8, "excitement": 0.9, "happiness": 0.7,
            "anger": 0.8, "frustration": 0.6, "irritation": 0.5,
            "fear": 0.7, "anxiety": 0.6, "worry": 0.5,
            "sadness": 0.6, "disappointment": 0.5, "melancholy": 0.4,
            "surprise": 0.6, "amazement": 0.8, "shock": 0.9,
            "neutral": 0.3, "calm": 0.2, "peaceful": 0.1
        }
        return intensity_map.get(emotional_state, 0.5)
    
    def _generate_insights(self, data: Dict[str, Any], reflection_type: ReflectionType, emotional_state: str) -> List[str]:
        """통찰 생성"""
        insights = []
        
        if reflection_type == ReflectionType.JUDGMENT:
            bias_score = data.get("overall_bias_score", 0.0)
            if bias_score > 0.5:
                insights.append("판단에 편향이 감지되었습니다. 객관성을 높여야 합니다.")
            else:
                insights.append("판단이 비교적 객관적입니다.")
        
        elif reflection_type == ReflectionType.EMOTION:
            if emotional_state in ["joy", "happiness"]:
                insights.append("긍정적인 감정 상태가 학습에 도움이 됩니다.")
            elif emotional_state in ["anger", "frustration"]:
                insights.append("부정적인 감정이 감지되었습니다. 조절이 필요합니다.")
        
        elif reflection_type == ReflectionType.GROWTH:
            current_level = data.get("current_level", 1)
            experience_points = data.get("experience_points", 0)
            if experience_points > 100:
                insights.append("충분한 경험을 쌓았습니다. 다음 단계로 나아갈 준비가 되었습니다.")
            else:
                insights.append("더 많은 경험이 필요합니다.")
        
        elif reflection_type == ReflectionType.QUEST:
            quest_status = data.get("status", "unknown")
            if quest_status == "completed":
                insights.append("퀘스트를 성공적으로 완료했습니다. 성장이 확인됩니다.")
            elif quest_status == "failed":
                insights.append("퀘스트 실패를 통해 개선점을 발견했습니다.")
        
        return insights
    
    def _generate_action_items(self, insights: List[str], reflection_type: ReflectionType) -> List[str]:
        """행동 항목 생성"""
        action_items = []
        
        for insight in insights:
            if "편향" in insight:
                action_items.append("다양한 관점에서 상황을 재검토하세요.")
            elif "감정" in insight:
                action_items.append("감정 조절 기법을 연습하세요.")
            elif "경험" in insight:
                action_items.append("새로운 도전을 시도해보세요.")
            elif "퀘스트" in insight:
                action_items.append("다음 퀘스트를 준비하세요.")
        
        return action_items
    
    def _calculate_confidence_score(self, data: Dict[str, Any], insights: List[str]) -> float:
        """신뢰도 점수 계산"""
        # 데이터 품질과 통찰의 깊이를 기반으로 신뢰도 계산
        data_completeness = min(1.0, len(data) / 10.0)
        insight_quality = min(1.0, len(insights) / 3.0)
        
        return (data_completeness + insight_quality) / 2.0
    
    def _update_patterns(self, entry: ReflectionEntry):
        """패턴 업데이트"""
        # 반영 패턴 분석
        pattern_key = f"{entry.reflection_type.value}_{entry.reflection_level.value}"
        if pattern_key not in self.insight_patterns:
            self.insight_patterns[pattern_key] = []
        
        self.insight_patterns[pattern_key].append({
            "timestamp": entry.timestamp,
            "insights": entry.insights,
            "confidence": entry.confidence_score
        })
    
    def get_recent_reflections(self, limit: int = 10) -> List[ReflectionEntry]:
        """최근 반영 일지 조회"""
        return self.reflection_log[-limit:] if self.reflection_log else []
    
    def get_reflections_by_type(self, reflection_type: ReflectionType) -> List[ReflectionEntry]:
        """유형별 반영 일지 조회"""
        return [entry for entry in self.reflection_log if entry.reflection_type == reflection_type]
    
    def get_growth_trajectory(self) -> List[Dict[str, Any]]:
        """성장 궤적 조회"""
        return self.growth_trajectory
    
    def get_emotional_trends(self) -> List[Dict[str, Any]]:
        """감정 트렌드 조회"""
        return self.emotional_trends
    
    def export_reflection_log(self, filepath: str):
        """반영 일지 내보내기"""
        export_data = {
            "reflections": [asdict(entry) for entry in self.reflection_log],
            "patterns": self.insight_patterns,
            "growth_trajectory": self.growth_trajectory,
            "emotional_trends": self.emotional_trends
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"반영 일지 내보내기 완료: {filepath}")
    
    def get_reflection_summary(self) -> Dict[str, Any]:
        """반영 요약"""
        if not self.reflection_log:
            return {"message": "반영 일지가 없습니다."}
        
        total_reflections = len(self.reflection_log)
        type_counts = {}
        level_counts = {}
        avg_confidence = 0.0
        avg_growth_impact = 0.0
        
        for entry in self.reflection_log:
            type_counts[entry.reflection_type.value] = type_counts.get(entry.reflection_type.value, 0) + 1
            level_counts[entry.reflection_level.value] = level_counts.get(entry.reflection_level.value, 0) + 1
            avg_confidence += entry.confidence_score
            avg_growth_impact += entry.growth_impact
        
        avg_confidence /= total_reflections
        avg_growth_impact /= total_reflections
        
        return {
            "total_reflections": total_reflections,
            "type_distribution": type_counts,
            "level_distribution": level_counts,
            "average_confidence": avg_confidence,
            "average_growth_impact": avg_growth_impact,
            "recent_insights": [entry.insights for entry in self.reflection_log[-5:]]
        } 
 
 