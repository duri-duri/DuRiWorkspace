#!/usr/bin/env python3
"""
Action Statistics and Decision Making for DuRi Emotion Processing System
"""

import os
import json
from typing import Dict, List, Optional, Tuple
from datetime import datetime
from duri_common.logger import get_logger
from duri_common.config.emotion_labels import ALL_EMOTIONS, is_valid_emotion

logger = get_logger("duri_core.stats")


def load_action_stats(stats_path: str) -> Dict:
    """
    액션 통계 데이터 로드
    
    Args:
        stats_path (str): 통계 파일 경로
    
    Returns:
        Dict: 액션 통계 데이터
    """
    try:
        if os.path.exists(stats_path):
            with open(stats_path, 'r') as f:
                return json.load(f)
    except Exception as e:
        logger.error(f"액션 통계 로드 실패: {e}")
    
    # 기본 통계 구조 반환
    return {
        "emotions": {},
        "actions": {},
        "emotion_action_pairs": {},
        "last_updated": datetime.now().isoformat()
    }


def save_action_stats(stats: Dict, stats_path: str) -> bool:
    """
    액션 통계 데이터 저장
    
    Args:
        stats (Dict): 저장할 통계 데이터
        stats_path (str): 저장할 파일 경로
    
    Returns:
        bool: 저장 성공 여부
    """
    try:
        os.makedirs(os.path.dirname(stats_path), exist_ok=True)
        stats["last_updated"] = datetime.now().isoformat()
        with open(stats_path, 'w') as f:
            json.dump(stats, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        logger.error(f"액션 통계 저장 실패: {e}")
        return False


def update_action_stats(
    emotion: str, 
    action: str, 
    result: str, 
    stats_path: str
) -> Dict:
    """
    액션 통계 업데이트
    
    Args:
        emotion (str): 감정
        action (str): 수행한 액션
        result (str): 결과 (success/fail)
        stats_path (str): 통계 파일 경로
    
    Returns:
        Dict: 업데이트된 통계 데이터
    """
    stats = load_action_stats(stats_path)
    
    # 감정별 통계 업데이트
    if emotion not in stats["emotions"]:
        stats["emotions"][emotion] = {"total": 0, "success": 0, "fail": 0}
    stats["emotions"][emotion]["total"] += 1
    stats["emotions"][emotion][result] += 1
    
    # 액션별 통계 업데이트
    if action not in stats["actions"]:
        stats["actions"][action] = {"total": 0, "success": 0, "fail": 0}
    stats["actions"][action]["total"] += 1
    stats["actions"][action][result] += 1
    
    # 감정-액션 쌍 통계 업데이트
    pair_key = f"{emotion}_{action}"
    if pair_key not in stats["emotion_action_pairs"]:
        stats["emotion_action_pairs"][pair_key] = {"total": 0, "success": 0, "fail": 0}
    stats["emotion_action_pairs"][pair_key]["total"] += 1
    stats["emotion_action_pairs"][pair_key][result] += 1
    
    # 통계 저장
    save_action_stats(stats, stats_path)
    logger.info(f"액션 통계 업데이트: {emotion} -> {action} ({result})")
    return stats


def calculate_success_rate(stats_data: Dict) -> float:
    """
    성공률 계산
    
    Args:
        stats_data (Dict): 통계 데이터
    
    Returns:
        float: 성공률 (0.0 ~ 1.0)
    """
    total = stats_data.get("total", 0)
    success = stats_data.get("success", 0)
    
    if total == 0:
        return 0.0
    
    return success / total


def choose_best_action(emotion: str, stats_path: str) -> Dict:
    """
    감정에 대한 최적 액션 선택 (순수 통계 기반)
    
    Args:
        emotion (str): 감정
        stats_path (str): 통계 파일 경로
    
    Returns:
        Dict: 선택된 액션과 신뢰도
    """
    stats = load_action_stats(stats_path)
    
    # 가능한 액션들
    available_actions = ["reflect", "wait", "console", "act", "observe"]
    
    # 감정-액션 쌍의 성공률 계산
    action_scores = {}
    
    for action in available_actions:
        pair_key = f"{emotion}_{action}"
        pair_stats = stats["emotion_action_pairs"].get(pair_key, {"total": 0, "success": 0, "fail": 0})
        
        # 성공률 계산
        success_rate = calculate_success_rate(pair_stats)
        
        # 액션별 기본 성공률 (경험 부족 시 사용)
        default_rates = {
            "reflect": 0.8,
            "wait": 0.6,
            "console": 0.7,
            "act": 0.5,
            "observe": 0.9
        }
        
        # 경험이 부족한 경우 기본 성공률 사용
        if pair_stats["total"] < 3:
            success_rate = default_rates.get(action, 0.5)
        
        action_scores[action] = success_rate
    
    # 최고 성공률을 가진 액션 선택
    best_action = max(action_scores, key=action_scores.get)
    confidence = action_scores[best_action]
    
    result = {
        "action": best_action,
        "confidence": round(confidence, 2),
        "method": "statistics"
    }
    
    logger.info(f"통계 기반 액션 선택: {emotion} -> {best_action} (신뢰도: {confidence:.2f})")
    return result


def get_action_recommendations(emotion: str, stats_path: str, top_n: int = 3) -> List[Dict]:
    """
    감정에 대한 액션 추천 목록 반환
    
    Args:
        emotion (str): 감정
        stats_path (str): 통계 파일 경로
        top_n (int): 반환할 추천 개수
    
    Returns:
        List[Dict]: 추천 액션 목록
    """
    stats = load_action_stats(stats_path)
    available_actions = ["reflect", "wait", "console", "act", "observe"]
    
    recommendations = []
    
    for action in available_actions:
        pair_key = f"{emotion}_{action}"
        pair_stats = stats["emotion_action_pairs"].get(pair_key, {"total": 0, "success": 0, "fail": 0})
        
        success_rate = calculate_success_rate(pair_stats)
        
        recommendations.append({
            "action": action,
            "success_rate": round(success_rate, 2),
            "total_attempts": pair_stats["total"],
            "success_count": pair_stats["success"],
            "fail_count": pair_stats["fail"]
        })
    
    # 성공률 기준으로 정렬
    recommendations.sort(key=lambda x: x["success_rate"], reverse=True)
    
    logger.debug(f"액션 추천 목록 생성: {emotion} -> {len(recommendations)}개 추천")
    return recommendations[:top_n]


def get_emotion_stats(emotion: str, stats_path: str) -> Dict:
    """
    특정 감정의 통계 정보 반환
    
    Args:
        emotion (str): 감정
        stats_path (str): 통계 파일 경로
    
    Returns:
        Dict: 감정 통계 정보
    """
    stats = load_action_stats(stats_path)
    
    emotion_stats = stats["emotions"].get(emotion, {"total": 0, "success": 0, "fail": 0})
    success_rate = calculate_success_rate(emotion_stats)
    
    return {
        "emotion": emotion,
        "total_occurrences": emotion_stats["total"],
        "success_count": emotion_stats["success"],
        "fail_count": emotion_stats["fail"],
        "success_rate": round(success_rate, 2),
        "recommendations": get_action_recommendations(emotion, stats_path)
    } 