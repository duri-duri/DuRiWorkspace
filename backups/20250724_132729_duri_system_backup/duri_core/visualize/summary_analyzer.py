#!/usr/bin/env python3
"""
Emotion Level Analysis for Summary Reports
"""

from typing import Dict, List, Optional, Tuple
from datetime import datetime
from collections import defaultdict
from duri_common.logger import get_logger
from duri_common.config.emotion_labels import (
    EMOTION_LEVELS,
    EmotionLevel,
    get_emotion_level,
    is_valid_emotion,
    get_emotions_by_level
)

logger = get_logger("duri_core.visualize.analyzer")


class EmotionSummaryAnalyzer:
    """감정 통계 분석기"""
    
    def __init__(self, stats_data: Dict, evolution_data: List):
        """
        초기화
        
        Args:
            stats_data (Dict): 액션 통계 데이터
            evolution_data (List): 진화 로그 데이터
        """
        self.stats_data = stats_data
        self.evolution_data = evolution_data
        
        # 감정 레벨별 매핑 (새로운 구조 사용)
        self.emotion_levels = EMOTION_LEVELS
        
        # 레벨별 감정 매핑 (빠른 검색용)
        self.emotion_to_level = {}
        for level, emotions in self.emotion_levels.items():
            for emotion in emotions:
                self.emotion_to_level[emotion.lower()] = level
    
    def get_emotion_level(self, emotion: str) -> EmotionLevel:
        """
        감정의 레벨 반환
        
        Args:
            emotion (str): 감정
            
        Returns:
            EmotionLevel: 감정 레벨 또는 UNKNOWN
        """
        return get_emotion_level(emotion)
    
    def analyze_by_emotion_level(self) -> Dict:
        """
        감정 레벨별 성공/실패 분석
        
        Returns:
            Dict: 레벨별 분석 결과
        """
        if not self.stats_data:
            logger.error("통계 데이터가 로드되지 않음")
            return {}
        
        # 레벨별 통계 초기화
        level_stats = {
            EmotionLevel.LEVEL_1: {"total": 0, "success": 0, "fail": 0, "emotions": {}},
            EmotionLevel.LEVEL_2: {"total": 0, "success": 0, "fail": 0, "emotions": {}},
            EmotionLevel.LEVEL_3: {"total": 0, "success": 0, "fail": 0, "emotions": {}}
        }
        
        # 알 수 없는 감정들을 위한 통계
        unknown_stats = {"total": 0, "success": 0, "fail": 0, "emotions": {}}
        
        # 액션 통계에서 감정별 데이터 분석
        emotions_data = self.stats_data.get("emotions", {})
        
        for emotion, stats in emotions_data.items():
            level = self.get_emotion_level(emotion)
            
            if level != EmotionLevel.UNKNOWN:
                # 알려진 감정
                level_stats[level]["total"] += stats.get("total", 0)
                level_stats[level]["success"] += stats.get("success", 0)
                level_stats[level]["fail"] += stats.get("fail", 0)
                level_stats[level]["emotions"][emotion] = stats
            else:
                # 알 수 없는 감정
                unknown_stats["total"] += stats.get("total", 0)
                unknown_stats["success"] += stats.get("success", 0)
                unknown_stats["fail"] += stats.get("fail", 0)
                unknown_stats["emotions"][emotion] = stats
        
        # 성공률 계산
        for level in [EmotionLevel.LEVEL_1, EmotionLevel.LEVEL_2, EmotionLevel.LEVEL_3]:
            total = level_stats[level]["total"]
            success = level_stats[level]["success"]
            level_stats[level]["success_rate"] = (success / total * 100) if total > 0 else 0.0
            level_stats[level]["emotion_count"] = len(level_stats[level]["emotions"])
        
        # 알 수 없는 감정 성공률 계산
        total_unknown = unknown_stats["total"]
        success_unknown = unknown_stats["success"]
        unknown_stats["success_rate"] = (success_unknown / total_unknown * 100) if total_unknown > 0 else 0.0
        unknown_stats["emotion_count"] = len(unknown_stats["emotions"])
        
        # 전체 통계 추가
        total_stats = {
            "total": sum(level_stats[level]["total"] for level in [EmotionLevel.LEVEL_1, EmotionLevel.LEVEL_2, EmotionLevel.LEVEL_3]),
            "success": sum(level_stats[level]["success"] for level in [EmotionLevel.LEVEL_1, EmotionLevel.LEVEL_2, EmotionLevel.LEVEL_3]),
            "fail": sum(level_stats[level]["fail"] for level in [EmotionLevel.LEVEL_1, EmotionLevel.LEVEL_2, EmotionLevel.LEVEL_3]),
            "emotion_count": sum(level_stats[level]["emotion_count"] for level in [EmotionLevel.LEVEL_1, EmotionLevel.LEVEL_2, EmotionLevel.LEVEL_3])
        }
        total_stats["success_rate"] = (total_stats["success"] / total_stats["total"] * 100) if total_stats["total"] > 0 else 0.0
        
        return {
            "level_1": level_stats[EmotionLevel.LEVEL_1],
            "level_2": level_stats[EmotionLevel.LEVEL_2],
            "level_3": level_stats[EmotionLevel.LEVEL_3],
            "unknown": unknown_stats,
            "total": total_stats,
            "analysis_timestamp": datetime.now().isoformat()
        }
    
    def analyze_evolution_by_level(self) -> Dict:
        """
        진화 로그를 감정 레벨별로 분석
        
        Returns:
            Dict: 레벨별 진화 분석 결과
        """
        if not self.evolution_data:
            logger.warning("진화 로그 데이터가 없음")
            return {}
        
        # 레벨별 진화 통계 초기화
        evolution_stats = {
            EmotionLevel.LEVEL_1: {"total_decisions": 0, "actions": defaultdict(int), "emotions": defaultdict(int)},
            EmotionLevel.LEVEL_2: {"total_decisions": 0, "actions": defaultdict(int), "emotions": defaultdict(int)},
            EmotionLevel.LEVEL_3: {"total_decisions": 0, "actions": defaultdict(int), "emotions": defaultdict(int)}
        }
        
        unknown_evolution = {"total_decisions": 0, "actions": defaultdict(int), "emotions": defaultdict(int)}
        
        # 진화 로그 분석
        for entry in self.evolution_data:
            if isinstance(entry, dict):
                emotion = entry.get("emotion", "").lower()
                decision = entry.get("decision", {})
                action = decision.get("action", "unknown")
                
                level = self.get_emotion_level(emotion)
                
                if level != EmotionLevel.UNKNOWN:
                    # 알려진 감정
                    evolution_stats[level]["total_decisions"] += 1
                    evolution_stats[level]["actions"][action] += 1
                    evolution_stats[level]["emotions"][emotion] += 1
                else:
                    # 알 수 없는 감정
                    unknown_evolution["total_decisions"] += 1
                    unknown_evolution["actions"][action] += 1
                    unknown_evolution["emotions"][emotion] += 1
        
        # defaultdict를 일반 dict로 변환
        for level in [EmotionLevel.LEVEL_1, EmotionLevel.LEVEL_2, EmotionLevel.LEVEL_3]:
            evolution_stats[level]["actions"] = dict(evolution_stats[level]["actions"])
            evolution_stats[level]["emotions"] = dict(evolution_stats[level]["emotions"])
        
        unknown_evolution["actions"] = dict(unknown_evolution["actions"])
        unknown_evolution["emotions"] = dict(unknown_evolution["emotions"])
        
        return {
            "level_1": evolution_stats[EmotionLevel.LEVEL_1],
            "level_2": evolution_stats[EmotionLevel.LEVEL_2],
            "level_3": evolution_stats[EmotionLevel.LEVEL_3],
            "unknown": unknown_evolution,
            "analysis_timestamp": datetime.now().isoformat()
        }
    
    def get_detailed_emotion_analysis(self) -> Dict:
        """
        감정별 상세 분석
        
        Returns:
            Dict: 감정별 상세 분석 결과
        """
        if not self.stats_data:
            return {}
        
        detailed_analysis = {}
        emotions_data = self.stats_data.get("emotions", {})
        
        for emotion, stats in emotions_data.items():
            level = self.get_emotion_level(emotion)
            success_rate = (stats.get("success", 0) / stats.get("total", 1) * 100) if stats.get("total", 0) > 0 else 0.0
            
            detailed_analysis[emotion] = {
                "level": level,
                "total": stats.get("total", 0),
                "success": stats.get("success", 0),
                "fail": stats.get("fail", 0),
                "success_rate": round(success_rate, 2),
                "is_valid": is_valid_emotion(emotion)
            }
        
        return detailed_analysis
    
    def get_action_analysis(self) -> Dict:
        """
        액션별 분석
        
        Returns:
            Dict: 액션별 분석 결과
        """
        if not self.stats_data:
            return {}
        
        actions_data = self.stats_data.get("actions", {})
        action_analysis = {}
        
        for action, stats in actions_data.items():
            success_rate = (stats.get("success", 0) / stats.get("total", 1) * 100) if stats.get("total", 0) > 0 else 0.0
            
            action_analysis[action] = {
                "total": stats.get("total", 0),
                "success": stats.get("success", 0),
                "fail": stats.get("fail", 0),
                "success_rate": round(success_rate, 2)
            }
        
        return action_analysis
    
    def get_emotion_action_pair_analysis(self) -> Dict:
        """
        감정-액션 쌍 분석
        
        Returns:
            Dict: 감정-액션 쌍 분석 결과
        """
        if not self.stats_data:
            return {}
        
        pairs_data = self.stats_data.get("emotion_action_pairs", {})
        pair_analysis = {}
        
        for pair_key, stats in pairs_data.items():
            success_rate = (stats.get("success", 0) / stats.get("total", 1) * 100) if stats.get("total", 0) > 0 else 0.0
            
            # 쌍 키에서 감정과 액션 분리
            parts = pair_key.split("_", 1)
            emotion = parts[0] if len(parts) > 0 else "unknown"
            action = parts[1] if len(parts) > 1 else "unknown"
            
            pair_analysis[pair_key] = {
                "emotion": emotion,
                "action": action,
                "total": stats.get("total", 0),
                "success": stats.get("success", 0),
                "fail": stats.get("fail", 0),
                "success_rate": round(success_rate, 2),
                "emotion_level": self.get_emotion_level(emotion)
            }
        
        return pair_analysis
    
    def get_high_failure_actions(self, threshold: float = 0.6) -> Dict:
        """
        실패율이 임계값을 초과하는 감정과 액션 반환
        
        Args:
            threshold (float): 실패율 임계값 (0.0 ~ 1.0, 기본값: 0.6)
        
        Returns:
            Dict: 높은 실패율을 가진 감정과 액션 정보
        """
        if not self.stats_data:
            return {}
        
        high_failure_items = {
            "emotions": [],
            "actions": [],
            "emotion_action_pairs": [],
            "threshold": threshold,
            "analysis_timestamp": datetime.now().isoformat()
        }
        
        # 감정별 높은 실패율 분석
        emotions_data = self.stats_data.get("emotions", {})
        for emotion, stats in emotions_data.items():
            total = stats.get("total", 0)
            if total > 0:
                failure_rate = stats.get("fail", 0) / total
                if failure_rate > threshold:
                    high_failure_items["emotions"].append({
                        "emotion": emotion,
                        "level": self.get_emotion_level(emotion),
                        "total": total,
                        "success": stats.get("success", 0),
                        "fail": stats.get("fail", 0),
                        "failure_rate": round(failure_rate, 3),
                        "success_rate": round(1 - failure_rate, 3)
                    })
        
        # 액션별 높은 실패율 분석
        actions_data = self.stats_data.get("actions", {})
        for action, stats in actions_data.items():
            total = stats.get("total", 0)
            if total > 0:
                failure_rate = stats.get("fail", 0) / total
                if failure_rate > threshold:
                    high_failure_items["actions"].append({
                        "action": action,
                        "total": total,
                        "success": stats.get("success", 0),
                        "fail": stats.get("fail", 0),
                        "failure_rate": round(failure_rate, 3),
                        "success_rate": round(1 - failure_rate, 3)
                    })
        
        # 감정-액션 쌍별 높은 실패율 분석
        pairs_data = self.stats_data.get("emotion_action_pairs", {})
        for pair_key, stats in pairs_data.items():
            total = stats.get("total", 0)
            if total > 0:
                failure_rate = stats.get("fail", 0) / total
                if failure_rate > threshold:
                    # 쌍 키에서 감정과 액션 분리
                    parts = pair_key.split("_", 1)
                    emotion = parts[0] if len(parts) > 0 else "unknown"
                    action = parts[1] if len(parts) > 1 else "unknown"
                    
                    high_failure_items["emotion_action_pairs"].append({
                        "pair_key": pair_key,
                        "emotion": emotion,
                        "action": action,
                        "emotion_level": self.get_emotion_level(emotion),
                        "total": total,
                        "success": stats.get("success", 0),
                        "fail": stats.get("fail", 0),
                        "failure_rate": round(failure_rate, 3),
                        "success_rate": round(1 - failure_rate, 3)
                    })
        
        # 결과 정렬 (실패율 기준 내림차순)
        high_failure_items["emotions"].sort(key=lambda x: x["failure_rate"], reverse=True)
        high_failure_items["actions"].sort(key=lambda x: x["failure_rate"], reverse=True)
        high_failure_items["emotion_action_pairs"].sort(key=lambda x: x["failure_rate"], reverse=True)
        
        # 요약 통계 추가
        high_failure_items["summary"] = {
            "total_high_failure_emotions": len(high_failure_items["emotions"]),
            "total_high_failure_actions": len(high_failure_items["actions"]),
            "total_high_failure_pairs": len(high_failure_items["emotion_action_pairs"]),
            "threshold_percentage": round(threshold * 100, 1)
        }
        
        logger.info(f"높은 실패율 분석 완료: 임계값 {threshold*100}% 초과 항목 {high_failure_items['summary']['total_high_failure_emotions']}개 감정, {high_failure_items['summary']['total_high_failure_actions']}개 액션, {high_failure_items['summary']['total_high_failure_pairs']}개 쌍")
        
        return high_failure_items
    
    def get_failure_analysis_by_level(self, threshold: float = 0.6) -> Dict:
        """
        레벨별 실패율 분석
        
        Args:
            threshold (float): 실패율 임계값 (0.0 ~ 1.0, 기본값: 0.6)
        
        Returns:
            Dict: 레벨별 실패율 분석 결과
        """
        if not self.stats_data:
            return {}
        
        level_failure_analysis = {
            "level_1": {"high_failure_emotions": [], "total_emotions": 0},
            "level_2": {"high_failure_emotions": [], "total_emotions": 0},
            "level_3": {"high_failure_emotions": [], "total_emotions": 0},
            "unknown": {"high_failure_emotions": [], "total_emotions": 0},
            "threshold": threshold,
            "analysis_timestamp": datetime.now().isoformat()
        }
        
        emotions_data = self.stats_data.get("emotions", {})
        
        for emotion, stats in emotions_data.items():
            level = self.get_emotion_level(emotion)
            total = stats.get("total", 0)
            
            if total > 0:
                failure_rate = stats.get("fail", 0) / total
                
                emotion_info = {
                    "emotion": emotion,
                    "total": total,
                    "success": stats.get("success", 0),
                    "fail": stats.get("fail", 0),
                    "failure_rate": round(failure_rate, 3),
                    "success_rate": round(1 - failure_rate, 3)
                }
                
                if level == EmotionLevel.LEVEL_1:
                    level_failure_analysis["level_1"]["total_emotions"] += 1
                    if failure_rate > threshold:
                        level_failure_analysis["level_1"]["high_failure_emotions"].append(emotion_info)
                elif level == EmotionLevel.LEVEL_2:
                    level_failure_analysis["level_2"]["total_emotions"] += 1
                    if failure_rate > threshold:
                        level_failure_analysis["level_2"]["high_failure_emotions"].append(emotion_info)
                elif level == EmotionLevel.LEVEL_3:
                    level_failure_analysis["level_3"]["total_emotions"] += 1
                    if failure_rate > threshold:
                        level_failure_analysis["level_3"]["high_failure_emotions"].append(emotion_info)
                else:
                    level_failure_analysis["unknown"]["total_emotions"] += 1
                    if failure_rate > threshold:
                        level_failure_analysis["unknown"]["high_failure_emotions"].append(emotion_info)
        
        # 각 레벨별로 실패율 기준 정렬
        for level_key in ["level_1", "level_2", "level_3", "unknown"]:
            level_failure_analysis[level_key]["high_failure_emotions"].sort(
                key=lambda x: x["failure_rate"], reverse=True
            )
        
        # 요약 통계 추가
        total_high_failure = sum(
            len(level_failure_analysis[level]["high_failure_emotions"]) 
            for level in ["level_1", "level_2", "level_3", "unknown"]
        )
        total_emotions = sum(
            level_failure_analysis[level]["total_emotions"] 
            for level in ["level_1", "level_2", "level_3", "unknown"]
        )
        
        level_failure_analysis["summary"] = {
            "total_high_failure_emotions": total_high_failure,
            "total_emotions": total_emotions,
            "high_failure_percentage": round((total_high_failure / total_emotions * 100), 1) if total_emotions > 0 else 0.0,
            "threshold_percentage": round(threshold * 100, 1)
        }
        
        return level_failure_analysis 