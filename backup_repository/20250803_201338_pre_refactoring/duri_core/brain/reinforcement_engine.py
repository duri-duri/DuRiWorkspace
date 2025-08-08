#!/usr/bin/env python3
"""
Reinforcement Learning Engine for DuRi Brain
"""

import random
from typing import List, Dict, Optional
import os
import json
from duri_common.config.config import Config

class ReinforcementEngine:
    """
    ReinforcementEngine
    - 감정(emotion)을 입력받아 ε-greedy 정책에 따라 행동(action)을 선택
    - 경험 통계(성공률 등)를 기반으로 행동을 선택
    """
    def __init__(self, epsilon: float = 0.1):
        """
        Args:
            epsilon (float): 무작위 탐험 확률 (0~1)
        """
        self.epsilon = epsilon
        # 경험 통계: {emotion: {action: success_rate, ...}, ...}
        self.experience_stats: Dict[str, Dict[str, float]] = {}
        self.actions: List[str] = []  # 전체 가능한 행동 목록
        self._load_experience_stats()

    def _load_experience_stats(self):
        """
        experience_stats.json 파일을 불러와 감정-행동별 success/fail dict로 self.experience_stats를 구성
        actions 목록도 자동 추출
        """
        evolution_dir = Config.get_evolution_dir()
        stats_path = os.path.join(evolution_dir, "experience_stats.json")
        if not os.path.exists(stats_path):
            self.experience_stats = {}
            self.actions = []
            return
        with open(stats_path, "r", encoding="utf-8") as f:
            stats_data = json.load(f)
        # stats_data: {"happy_dance": {"emotion":..., "action":..., "success_count":..., ...}, ...}
        experience_stats: Dict[str, Dict[str, float]] = {}
        actions_set = set()
        for key, entry in stats_data.items():
            emotion = entry.get("emotion")
            action = entry.get("action")
            success_count = entry.get("success_count", 0)
            total_count = entry.get("total_count", 0)
            if not emotion or not action or total_count == 0:
                continue
            success_rate = success_count / total_count if total_count > 0 else 0.0
            if emotion not in experience_stats:
                experience_stats[emotion] = {}
            experience_stats[emotion][action] = success_rate
            actions_set.add(action)
        self.experience_stats = experience_stats
        self.actions = sorted(list(actions_set))

    def choose_action(self, emotion: str) -> Optional[str]:
        """
        ε-greedy 정책에 따라 행동 선택
        Args:
            emotion (str): 입력 감정
        Returns:
            action (str): 선택된 행동 (없으면 None)
        """
        action_stats = self.experience_stats.get(emotion, {})
        if not action_stats:
            # 경험 데이터가 없으면 전체 행동 중 무작위 선택
            if self.actions:
                return random.choice(self.actions)
            return None

        # ε 확률로 무작위 탐험
        if random.random() < self.epsilon:
            return random.choice(list(action_stats.keys()))

        # 1-ε 확률로 성공률이 가장 높은 행동 중 랜덤 선택
        max_rate = max(action_stats.values())
        best_actions = [a for a, r in action_stats.items() if r == max_rate]
        return random.choice(best_actions) 