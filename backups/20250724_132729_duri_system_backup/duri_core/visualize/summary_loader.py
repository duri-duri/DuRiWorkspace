#!/usr/bin/env python3
"""
Data Loading and Validation for Emotion Summary Analysis
"""

import json
import os
from typing import Dict, List, Optional, Tuple
from datetime import datetime
from duri_common.logger import get_logger

logger = get_logger("duri_core.visualize.loader")


class DataLoader:
    """데이터 로딩 및 검증 클래스"""
    
    def __init__(self, stats_path: str, evolution_path: str):
        """
        초기화
        
        Args:
            stats_path (str): 액션 통계 파일 경로
            evolution_path (str): 진화 로그 파일 경로
        """
        self.stats_path = stats_path
        self.evolution_path = evolution_path
        self.stats_data = None
        self.evolution_data = None
    
    def load_data(self) -> bool:
        """
        통계 및 진화 로그 데이터 로드
        
        Returns:
            bool: 로드 성공 여부
        """
        try:
            # 액션 통계 로드
            if os.path.exists(self.stats_path):
                with open(self.stats_path, 'r', encoding='utf-8') as f:
                    self.stats_data = json.load(f)
                logger.info(f"액션 통계 로드 완료: {self.stats_path}")
            else:
                logger.warning(f"액션 통계 파일이 존재하지 않음: {self.stats_path}")
                self.stats_data = {"emotions": {}, "actions": {}, "emotion_action_pairs": {}}
            
            # 진화 로그 로드
            if os.path.exists(self.evolution_path):
                with open(self.evolution_path, 'r', encoding='utf-8') as f:
                    self.evolution_data = json.load(f)
                logger.info(f"진화 로그 로드 완료: {self.evolution_path}")
            else:
                logger.warning(f"진화 로그 파일이 존재하지 않음: {self.evolution_path}")
                self.evolution_data = []
            
            return True
            
        except Exception as e:
            logger.error(f"데이터 로드 실패: {e}")
            return False
    
    def validate_stats_data(self) -> Tuple[bool, List[str]]:
        """
        통계 데이터 유효성 검사
        
        Returns:
            Tuple[bool, List[str]]: (유효성 여부, 오류 메시지 목록)
        """
        errors = []
        
        if not self.stats_data:
            errors.append("통계 데이터가 로드되지 않음")
            return False, errors
        
        # 필수 키 확인
        required_keys = ["emotions", "actions", "emotion_action_pairs"]
        for key in required_keys:
            if key not in self.stats_data:
                errors.append(f"필수 키 누락: {key}")
        
        # 감정 데이터 구조 검사
        emotions_data = self.stats_data.get("emotions", {})
        for emotion, stats in emotions_data.items():
            if not isinstance(stats, dict):
                errors.append(f"감정 통계가 딕셔너리가 아님: {emotion}")
                continue
            
            required_stats = ["total", "success", "fail"]
            for stat in required_stats:
                if stat not in stats:
                    errors.append(f"감정 {emotion}에 필수 통계 누락: {stat}")
                elif not isinstance(stats[stat], int):
                    errors.append(f"감정 {emotion}의 {stat}이 정수가 아님")
        
        return len(errors) == 0, errors
    
    def validate_evolution_data(self) -> Tuple[bool, List[str]]:
        """
        진화 로그 데이터 유효성 검사
        
        Returns:
            Tuple[bool, List[str]]: (유효성 여부, 오류 메시지 목록)
        """
        errors = []
        
        if not isinstance(self.evolution_data, list):
            errors.append("진화 로그가 리스트가 아님")
            return False, errors
        
        for i, entry in enumerate(self.evolution_data):
            if not isinstance(entry, dict):
                errors.append(f"진화 로그 항목 {i}가 딕셔너리가 아님")
                continue
            
            # 필수 필드 확인
            if "emotion" not in entry:
                errors.append(f"진화 로그 항목 {i}에 emotion 필드 누락")
            
            if "decision" not in entry:
                errors.append(f"진화 로그 항목 {i}에 decision 필드 누락")
            elif not isinstance(entry["decision"], dict):
                errors.append(f"진화 로그 항목 {i}의 decision이 딕셔너리가 아님")
        
        return len(errors) == 0, errors
    
    def get_data_summary(self) -> Dict:
        """
        로드된 데이터의 요약 정보 반환
        
        Returns:
            Dict: 데이터 요약 정보
        """
        stats_summary = {
            "emotion_count": len(self.stats_data.get("emotions", {})),
            "action_count": len(self.stats_data.get("actions", {})),
            "pair_count": len(self.stats_data.get("emotion_action_pairs", {}))
        }
        
        evolution_summary = {
            "total_entries": len(self.evolution_data),
            "valid_entries": sum(1 for entry in self.evolution_data if isinstance(entry, dict))
        }
        
        return {
            "stats": stats_summary,
            "evolution": evolution_summary,
            "loaded_at": datetime.now().isoformat()
        }
    
    def get_stats_data(self) -> Dict:
        """통계 데이터 반환"""
        return self.stats_data
    
    def get_evolution_data(self) -> List:
        """진화 로그 데이터 반환"""
        return self.evolution_data


def load_and_validate_data(stats_path: str, evolution_path: str) -> Tuple[Optional[DataLoader], List[str]]:
    """
    데이터 로드 및 검증 (편의 함수)
    
    Args:
        stats_path (str): 액션 통계 파일 경로
        evolution_path (str): 진화 로그 파일 경로
    
    Returns:
        Tuple[Optional[DataLoader], List[str]]: (로더 객체 또는 None, 오류 메시지 목록)
    """
    loader = DataLoader(stats_path, evolution_path)
    
    if not loader.load_data():
        return None, ["데이터 로드 실패"]
    
    errors = []
    
    # 통계 데이터 검증
    stats_valid, stats_errors = loader.validate_stats_data()
    if not stats_valid:
        errors.extend(stats_errors)
    
    # 진화 로그 검증
    evolution_valid, evolution_errors = loader.validate_evolution_data()
    if not evolution_valid:
        errors.extend(evolution_errors)
    
    if errors:
        logger.warning(f"데이터 검증 오류: {errors}")
        return None, errors
    
    return loader, [] 