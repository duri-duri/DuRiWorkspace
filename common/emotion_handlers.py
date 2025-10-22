"""
Common emotion handling utilities for DuRi system.
This module provides core functionality for emotion vector handling, logging, and communication.
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Optional, Tuple

import requests
import yaml

from .emotion_vector import EmotionVector


class EmotionLogger:
    def __init__(self, base_path: str = "/home/duri/emotion_data"):
        self.base_path = base_path
        self.date = datetime.now().strftime("%Y-%m-%d")
        self.log_path = os.path.join(base_path, self.date, "emotion_change_log.json")
        os.makedirs(os.path.dirname(self.log_path), exist_ok=True)

    def log_change(self, old_vector: EmotionVector, new_vector: EmotionVector) -> None:
        """Log emotion vector changes"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "old_emotions": old_vector.get_dominant_emotions(),
            "new_emotions": new_vector.get_dominant_emotions(),
            "importance_delta": new_vector.compute_importance() - old_vector.compute_importance(),
        }

        with open(self.log_path, "a") as f:
            json.dump(log_entry, f)
            f.write("\n")


class EmotionTransmitter:
    def __init__(self, dest_url: str = "http://192.168.0.15:8080/emotion"):
        self.date = datetime.now().strftime("%Y-%m-%d")
        self.emotion_path = f"/home/duri/emotion_data/{self.date}/emotion_vector.json"
        self.queue_path = "/home/duri/emotion_queue/pending_emotions.json"
        self.policy_path = "/home/duri/../config/importance_policy.yaml"
        self.dest_url = dest_url

    def load_importance_threshold(self, default: float = 0.3) -> float:
        """Load importance threshold from policy file"""
        try:
            with open(self.policy_path, "r") as f:
                return yaml.safe_load(f).get("importance_threshold", default)
        except:
            return default

    def send_emotion(self, vector: EmotionVector) -> bool:
        """Send emotion vector to destination"""
        data = {
            "emotion": vector.to_dict(),
            "importance_score": vector.compute_importance(),
            "dominant_emotions": vector.get_dominant_emotions(),
            "timestamp": datetime.now().isoformat(),
        }

        try:
            res = requests.post(self.dest_url, json=data)
            if res.status_code != 200:
                raise Exception(f"HTTP {res.status_code}")
            return True
        except Exception as e:
            print(f"[!] 전송 실패: {e} → 큐에 저장")
            self._save_to_queue(data)
            return False

    def _save_to_queue(self, data: Dict) -> None:
        """Save failed transmission to queue"""
        os.makedirs(os.path.dirname(self.queue_path), exist_ok=True)
        with open(self.queue_path, "a") as q:
            q.write(json.dumps(data) + "\n")


class EmotionReceiver:
    def __init__(self, base_path: str = "/home/duri/emotion_data"):
        self.base_path = base_path

    def save_received_vector(self, vector: EmotionVector, source: str) -> str:
        """Save received emotion vector"""
        date = datetime.now().strftime("%Y-%m-%d")
        target_dir = os.path.join(self.base_path, date, source)
        os.makedirs(target_dir, exist_ok=True)

        return vector.save(target_dir)


class EmotionDeltaHandler:
    def __init__(self, base_path: str = "/home/duri/emotion_data"):
        self.base_path = base_path
        self.date = datetime.now().strftime("%Y-%m-%d")

    def compute_delta(
        self, old_vector: EmotionVector, new_vector: EmotionVector
    ) -> Dict[str, float]:
        """Compute delta between two emotion vectors"""
        delta = {}
        for dim in EmotionVector.DIMENSIONS:
            delta[dim] = new_vector.values[dim] - old_vector.values[dim]
        return delta

    def update_from_delta(
        self, current_vector: EmotionVector, delta: Dict[str, float]
    ) -> EmotionVector:
        """Apply delta to current emotion vector"""
        new_values = current_vector.values.copy()
        for dim, change in delta.items():
            if dim in new_values:
                new_values[dim] = max(0.0, min(1.0, new_values[dim] + change))
        return EmotionVector(new_values)
