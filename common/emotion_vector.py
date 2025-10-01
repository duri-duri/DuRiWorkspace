"""
Common emotion vector module for DuRi system.
This module provides core functionality for emotion vector handling.
"""

from datetime import datetime
import json
import os
from typing import Dict, List, Optional, Tuple

import yaml


class EmotionVector:
    # 기본 감정 차원들
    DIMENSIONS = [
        "joy",
        "anger",
        "fear",
        "trust",
        "surprise",
        "sadness",
        "anticipation",
        "disgust",
    ]

    def __init__(self, values: Optional[Dict[str, float]] = None):
        """
        감정 벡터 초기화
        :param values: 초기 감정 값들 (없으면 모두 0.0으로 초기화)
        """
        self.values = {dim: 0.0 for dim in self.DIMENSIONS}
        if values:
            for dim, val in values.items():
                if dim in self.DIMENSIONS:
                    self.values[dim] = max(
                        0.0, min(1.0, float(val))
                    )  # 0.0 ~ 1.0 범위 보장

    def to_dict(self) -> Dict[str, float]:
        """벡터를 딕셔너리로 변환"""
        return self.values.copy()

    @classmethod
    def from_keyword(cls, keyword: str) -> "EmotionVector":
        """
        키워드 기반 감정 벡터 생성
        :param keyword: 감정 키워드 (예: "칭찬", "분노", etc.)
        """
        vector = cls()

        # 기본 감정 매핑 (확장 가능)
        mappings = {
            "칭찬": {"joy": 0.8, "trust": 0.6},
            "분노": {"anger": 0.9, "disgust": 0.4},
            "기쁨": {"joy": 0.9, "anticipation": 0.3},
            "슬픔": {"sadness": 0.8, "fear": 0.2},
            "놀람": {"surprise": 0.9, "fear": 0.3},
            "신뢰": {"trust": 0.8, "joy": 0.3},
            "기대": {"anticipation": 0.7, "joy": 0.4},
            "혐오": {"disgust": 0.8, "anger": 0.3},
        }

        if keyword in mappings:
            for dim, val in mappings[keyword].items():
                vector.values[dim] = val

        return vector

    def compute_importance(self, threshold: float = 0.3) -> float:
        """
        감정 벡터의 중요도 점수 계산
        :param threshold: 기본 중요도 임계값
        :return: 0.0 ~ 1.0 사이의 중요도 점수
        """
        # 1. 감정 강도 (가장 강한 감정의 크기)
        max_intensity = max(self.values.values())

        # 2. 감정 복잡도 (활성화된 감정 차원 수)
        active_dimensions = sum(1 for v in self.values.values() if v > threshold)
        complexity_score = active_dimensions / len(self.DIMENSIONS)

        # 3. 최종 중요도 = 감정 강도(0.7) + 복잡도(0.3)
        importance = (max_intensity * 0.7) + (complexity_score * 0.3)
        return max(0.0, min(1.0, importance))

    def get_dominant_emotions(self, threshold: float = 0.3) -> List[Tuple[str, float]]:
        """
        임계값을 넘는 주요 감정들을 반환
        :return: [(감정이름, 강도)] 형태의 내림차순 정렬 리스트
        """
        dominant = [(dim, val) for dim, val in self.values.items() if val > threshold]
        return sorted(dominant, key=lambda x: x[1], reverse=True)

    def save(self, base_path: str = "/home/duri/emotion_data") -> str:
        """
        감정 벡터를 저장
        :param base_path: 저장 기본 경로
        :return: 저장된 파일 경로
        """
        today = datetime.now().strftime("%Y-%m-%d")
        target_dir = os.path.join(base_path, today)
        os.makedirs(target_dir, exist_ok=True)

        data = {
            "emotion": self.to_dict(),
            "importance_score": self.compute_importance(),
            "dominant_emotions": self.get_dominant_emotions(),
            "timestamp": datetime.now().isoformat(),
        }

        vector_path = os.path.join(target_dir, "emotion_vector.json")
        with open(vector_path, "w") as f:
            json.dump(data, f, indent=2)

        return vector_path

    @classmethod
    def load(cls, path: str) -> Optional["EmotionVector"]:
        """
        저장된 감정 벡터 로드
        :param path: 감정 벡터 파일 경로
        :return: EmotionVector 인스턴스 또는 None (실패 시)
        """
        try:
            with open(path, "r") as f:
                data = json.load(f)
                if isinstance(data, dict) and "emotion" in data:
                    return cls(data["emotion"])
                return cls(data)  # 직접 벡터 값이 저장된 경우
        except (json.JSONDecodeError, FileNotFoundError):
            return None
