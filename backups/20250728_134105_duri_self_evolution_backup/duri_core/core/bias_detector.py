#!/usr/bin/env python3
"""
Bias Detector - Core 편향 감지기

의사결정 과정에서 발생할 수 있는 편향을 감지하고 분석하는 역할을 합니다.
"""

import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum
from duri_common.logger import get_logger
from duri_common.config.config import Config

logger = get_logger("duri_core.bias_detector")


class BiasType(Enum):
    """편향 타입"""
    EMOTION_BIAS = "emotion_bias"           # 특정 감정에 대한 편향
    ACTION_BIAS = "action_bias"             # 특정 행동에 대한 편향
    TEMPORAL_BIAS = "temporal_bias"         # 시간적 편향
    INTENSITY_BIAS = "intensity_bias"       # 강도 편향
    PATTERN_BIAS = "pattern_bias"           # 패턴 편향
    FREQUENCY_BIAS = "frequency_bias"       # 빈도 편향


@dataclass
class BiasDetection:
    """편향 감지 결과"""
    bias_type: BiasType
    confidence: float  # 0.0 ~ 1.0
    description: str
    evidence: Dict[str, Any]
    severity: str  # "low", "medium", "high", "critical"
    timestamp: str
    recommendations: List[str]


@dataclass
class BiasPattern:
    """편향 패턴"""
    pattern_id: str
    bias_type: BiasType
    emotion: Optional[str]
    action: Optional[str]
    frequency: int
    avg_confidence: float
    first_detected: str
    last_detected: str
    severity: str
    description: str


class BiasDetector:
    """편향 감지기"""
    
    def __init__(self, data_dir: str = "bias_data"):
        """
        BiasDetector 초기화
        
        Args:
            data_dir (str): 데이터 저장 디렉토리
        """
        self.data_dir = data_dir
        self.detections_dir = os.path.join(data_dir, "detections")
        self.patterns_dir = os.path.join(data_dir, "patterns")
        self.history_file = os.path.join(data_dir, "bias_history.json")
        
        # 디렉토리 생성
        os.makedirs(self.detections_dir, exist_ok=True)
        os.makedirs(self.patterns_dir, exist_ok=True)
        
        # 편향 임계값 설정
        self.thresholds = {
            'emotion_frequency': 0.7,    # 특정 감정이 70% 이상
            'action_frequency': 0.6,     # 특정 행동이 60% 이상
            'intensity_threshold': 0.8,  # 강도가 80% 이상
            'temporal_window': 24,       # 24시간 내
            'pattern_confidence': 0.8    # 패턴 신뢰도 80% 이상
        }
        
        # 감지 히스토리 로드
        self.detection_history = self._load_detection_history()
        
        logger.info(f"BiasDetector 초기화 완료: {data_dir}")
    
    def detect_emotion_bias(self, emotion_history: List[Dict[str, Any]]) -> Optional[BiasDetection]:
        """
        감정 편향 감지
        
        Args:
            emotion_history: 감정 히스토리 리스트
        
        Returns:
            Optional[BiasDetection]: 감지된 편향
        """
        if not emotion_history:
            return None
        
        # 감정별 빈도 계산
        emotion_counts = {}
        total_emotions = len(emotion_history)
        
        for entry in emotion_history:
            emotion = entry.get('emotion', 'unknown')
            emotion_counts[emotion] = emotion_counts.get(emotion, 0) + 1
        
        # 가장 빈번한 감정 찾기
        most_frequent_emotion = max(emotion_counts.items(), key=lambda x: x[1])
        frequency_ratio = most_frequent_emotion[1] / total_emotions
        
        if frequency_ratio > self.thresholds['emotion_frequency']:
            confidence = min(1.0, frequency_ratio * 1.2)
            severity = self._calculate_severity(frequency_ratio)
            
            return BiasDetection(
                bias_type=BiasType.EMOTION_BIAS,
                confidence=confidence,
                description=f"감정 편향 감지: '{most_frequent_emotion[0]}' 감정이 {frequency_ratio:.1%} 비율로 나타남",
                evidence={
                    'emotion': most_frequent_emotion[0],
                    'frequency': most_frequent_emotion[1],
                    'total_count': total_emotions,
                    'frequency_ratio': frequency_ratio,
                    'all_emotions': emotion_counts
                },
                severity=severity,
                timestamp=datetime.now().isoformat(),
                recommendations=[
                    "다양한 감정 표현을 권장합니다",
                    "감정 다양성 훈련을 고려해보세요",
                    "감정 표현의 균형을 맞춰보세요"
                ]
            )
        
        return None
    
    def detect_action_bias(self, action_history: List[Dict[str, Any]]) -> Optional[BiasDetection]:
        """
        행동 편향 감지
        
        Args:
            action_history: 행동 히스토리 리스트
        
        Returns:
            Optional[BiasDetection]: 감지된 편향
        """
        if not action_history:
            return None
        
        # 행동별 빈도 계산
        action_counts = {}
        total_actions = len(action_history)
        
        for entry in action_history:
            action = entry.get('action', 'unknown')
            action_counts[action] = action_counts.get(action, 0) + 1
        
        # 가장 빈번한 행동 찾기
        most_frequent_action = max(action_counts.items(), key=lambda x: x[1])
        frequency_ratio = most_frequent_action[1] / total_actions
        
        if frequency_ratio > self.thresholds['action_frequency']:
            confidence = min(1.0, frequency_ratio * 1.2)
            severity = self._calculate_severity(frequency_ratio)
            
            return BiasDetection(
                bias_type=BiasType.ACTION_BIAS,
                confidence=confidence,
                description=f"행동 편향 감지: '{most_frequent_action[0]}' 행동이 {frequency_ratio:.1%} 비율로 나타남",
                evidence={
                    'action': most_frequent_action[0],
                    'frequency': most_frequent_action[1],
                    'total_count': total_actions,
                    'frequency_ratio': frequency_ratio,
                    'all_actions': action_counts
                },
                severity=severity,
                timestamp=datetime.now().isoformat(),
                recommendations=[
                    "다양한 행동 패턴을 시도해보세요",
                    "행동 다양성 훈련을 고려해보세요",
                    "새로운 행동 전략을 개발해보세요"
                ]
            )
        
        return None
    
    def detect_temporal_bias(self, emotion_history: List[Dict[str, Any]]) -> Optional[BiasDetection]:
        """
        시간적 편향 감지
        
        Args:
            emotion_history: 감정 히스토리 리스트
        
        Returns:
            Optional[BiasDetection]: 감지된 편향
        """
        if len(emotion_history) < 10:  # 최소 10개 이상 필요
            return None
        
        # 최근 24시간 내 감정 분석
        now = datetime.now()
        recent_emotions = []
        
        for entry in emotion_history:
            timestamp_str = entry.get('timestamp')
            if timestamp_str:
                try:
                    timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
                    if now - timestamp < timedelta(hours=self.thresholds['temporal_window']):
                        recent_emotions.append(entry)
                except:
                    continue
        
        if len(recent_emotions) < 5:  # 최근 5개 이상 필요
            return None
        
        # 최근 감정의 다양성 분석
        recent_emotion_types = set(entry.get('emotion') for entry in recent_emotions)
        diversity_ratio = len(recent_emotion_types) / len(recent_emotions)
        
        if diversity_ratio < 0.3:  # 다양성이 30% 미만
            confidence = 1.0 - diversity_ratio
            severity = self._calculate_severity(1.0 - diversity_ratio)
            
            return BiasDetection(
                bias_type=BiasType.TEMPORAL_BIAS,
                confidence=confidence,
                description=f"시간적 편향 감지: 최근 {self.thresholds['temporal_window']}시간 내 감정 다양성이 낮음 ({diversity_ratio:.1%})",
                evidence={
                    'recent_emotions': len(recent_emotions),
                    'emotion_types': len(recent_emotion_types),
                    'diversity_ratio': diversity_ratio,
                    'emotion_types_list': list(recent_emotion_types)
                },
                severity=severity,
                timestamp=datetime.now().isoformat(),
                recommendations=[
                    "시간대별 다양한 감정 표현을 시도해보세요",
                    "감정 변화 패턴을 모니터링해보세요",
                    "정기적인 감정 다양성 체크를 해보세요"
                ]
            )
        
        return None
    
    def detect_intensity_bias(self, emotion_history: List[Dict[str, Any]]) -> Optional[BiasDetection]:
        """
        강도 편향 감지
        
        Args:
            emotion_history: 감정 히스토리 리스트
        
        Returns:
            Optional[BiasDetection]: 감지된 편향
        """
        if not emotion_history:
            return None
        
        # 강도 정보 추출
        intensities = []
        for entry in emotion_history:
            intensity = entry.get('intensity', 0.5)
            if isinstance(intensity, (int, float)):
                intensities.append(float(intensity))
        
        if len(intensities) < 5:  # 최소 5개 이상 필요
            return None
        
        # 강도 통계 계산
        avg_intensity = sum(intensities) / len(intensities)
        high_intensity_count = sum(1 for i in intensities if i > self.thresholds['intensity_threshold'])
        high_intensity_ratio = high_intensity_count / len(intensities)
        
        if high_intensity_ratio > 0.8:  # 80% 이상이 높은 강도
            confidence = min(1.0, high_intensity_ratio * 1.2)
            severity = self._calculate_severity(high_intensity_ratio)
            
            return BiasDetection(
                bias_type=BiasType.INTENSITY_BIAS,
                confidence=confidence,
                description=f"강도 편향 감지: 평균 강도 {avg_intensity:.2f}, 높은 강도 비율 {high_intensity_ratio:.1%}",
                evidence={
                    'avg_intensity': avg_intensity,
                    'high_intensity_count': high_intensity_count,
                    'total_count': len(intensities),
                    'high_intensity_ratio': high_intensity_ratio,
                    'intensity_range': [min(intensities), max(intensities)]
                },
                severity=severity,
                timestamp=datetime.now().isoformat(),
                recommendations=[
                    "감정 강도의 균형을 맞춰보세요",
                    "중간 강도의 감정 표현을 연습해보세요",
                    "감정 강도 조절 훈련을 고려해보세요"
                ]
            )
        
        return None
    
    def detect_pattern_bias(self, emotion_history: List[Dict[str, Any]], action_history: List[Dict[str, Any]]) -> Optional[BiasDetection]:
        """
        패턴 편향 감지
        
        Args:
            emotion_history: 감정 히스토리 리스트
            action_history: 행동 히스토리 리스트
        
        Returns:
            Optional[BiasDetection]: 감지된 편향
        """
        if len(emotion_history) < 10 or len(action_history) < 10:
            return None
        
        # 감정-행동 조합 패턴 분석
        emotion_action_pairs = {}
        
        # 최근 20개 항목만 분석
        recent_emotions = emotion_history[-20:]
        recent_actions = action_history[-20:]
        
        for i, emotion_entry in enumerate(recent_emotions):
            if i < len(recent_actions):
                emotion = emotion_entry.get('emotion', 'unknown')
                action = recent_actions[i].get('action', 'unknown')
                pair = f"{emotion}_{action}"
                emotion_action_pairs[pair] = emotion_action_pairs.get(pair, 0) + 1
        
        # 가장 빈번한 패턴 찾기
        if emotion_action_pairs:
            most_frequent_pattern = max(emotion_action_pairs.items(), key=lambda x: x[1])
            pattern_ratio = most_frequent_pattern[1] / len(recent_emotions)
            
            if pattern_ratio > 0.5:  # 50% 이상이 같은 패턴
                confidence = min(1.0, pattern_ratio * 1.5)
                severity = self._calculate_severity(pattern_ratio)
                
                return BiasDetection(
                    bias_type=BiasType.PATTERN_BIAS,
                    confidence=confidence,
                    description=f"패턴 편향 감지: '{most_frequent_pattern[0]}' 패턴이 {pattern_ratio:.1%} 비율로 나타남",
                    evidence={
                        'pattern': most_frequent_pattern[0],
                        'frequency': most_frequent_pattern[1],
                        'total_count': len(recent_emotions),
                        'pattern_ratio': pattern_ratio,
                        'all_patterns': emotion_action_pairs
                    },
                    severity=severity,
                    timestamp=datetime.now().isoformat(),
                    recommendations=[
                        "다양한 감정-행동 조합을 시도해보세요",
                        "패턴 다양성 훈련을 고려해보세요",
                        "새로운 반응 패턴을 개발해보세요"
                    ]
                )
        
        return None
    
    def run_bias_detection(self, emotion_history: List[Dict[str, Any]], action_history: List[Dict[str, Any]]) -> List[BiasDetection]:
        """
        전체 편향 감지 실행
        
        Args:
            emotion_history: 감정 히스토리 리스트
            action_history: 행동 히스토리 리스트
        
        Returns:
            List[BiasDetection]: 감지된 편향 목록
        """
        detections = []
        
        # 1. 감정 편향 감지
        emotion_bias = self.detect_emotion_bias(emotion_history)
        if emotion_bias:
            detections.append(emotion_bias)
        
        # 2. 행동 편향 감지
        action_bias = self.detect_action_bias(action_history)
        if action_bias:
            detections.append(action_bias)
        
        # 3. 시간적 편향 감지
        temporal_bias = self.detect_temporal_bias(emotion_history)
        if temporal_bias:
            detections.append(temporal_bias)
        
        # 4. 강도 편향 감지
        intensity_bias = self.detect_intensity_bias(emotion_history)
        if intensity_bias:
            detections.append(intensity_bias)
        
        # 5. 패턴 편향 감지
        pattern_bias = self.detect_pattern_bias(emotion_history, action_history)
        if pattern_bias:
            detections.append(pattern_bias)
        
        # 감지 결과 저장
        for detection in detections:
            self._save_detection(detection)
        
        logger.info(f"편향 감지 완료: {len(detections)}개 편향 감지됨")
        return detections
    
    def get_bias_summary(self) -> Dict[str, Any]:
        """
        편향 요약 정보 조회
        
        Returns:
            Dict[str, Any]: 편향 요약 정보
        """
        try:
            # 최근 7일간의 감지 결과 분석
            recent_detections = []
            week_ago = datetime.now() - timedelta(days=7)
            
            for detection in self.detection_history:
                try:
                    detection_time = datetime.fromisoformat(detection['timestamp'].replace('Z', '+00:00'))
                    if detection_time > week_ago:
                        recent_detections.append(detection)
                except:
                    continue
            
            # 편향 타입별 통계
            bias_type_counts = {}
            severity_counts = {}
            
            for detection in recent_detections:
                bias_type = detection.get('bias_type', 'unknown')
                severity = detection.get('severity', 'unknown')
                
                bias_type_counts[bias_type] = bias_type_counts.get(bias_type, 0) + 1
                severity_counts[severity] = severity_counts.get(severity, 0) + 1
            
            return {
                'total_detections': len(recent_detections),
                'bias_type_distribution': bias_type_counts,
                'severity_distribution': severity_counts,
                'detection_period': '7 days',
                'last_updated': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"편향 요약 조회 실패: {e}")
            return {}
    
    def _calculate_severity(self, ratio: float) -> str:
        """편향 심각도 계산"""
        if ratio > 0.9:
            return "critical"
        elif ratio > 0.7:
            return "high"
        elif ratio > 0.5:
            return "medium"
        else:
            return "low"
    
    def _save_detection(self, detection: BiasDetection):
        """감지 결과 저장"""
        try:
            detection_data = {
                'bias_type': detection.bias_type.value,
                'confidence': detection.confidence,
                'description': detection.description,
                'evidence': detection.evidence,
                'severity': detection.severity,
                'timestamp': detection.timestamp,
                'recommendations': detection.recommendations
            }
            
            # 개별 파일로 저장
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"detection_{detection.bias_type.value}_{timestamp}.json"
            filepath = os.path.join(self.detections_dir, filename)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(detection_data, f, indent=2, ensure_ascii=False)
            
            # 히스토리에 추가
            self.detection_history.append(detection_data)
            self._save_detection_history()
            
        except Exception as e:
            logger.error(f"감지 결과 저장 실패: {e}")
    
    def _load_detection_history(self) -> List[Dict[str, Any]]:
        """감지 히스토리 로드"""
        try:
            if os.path.exists(self.history_file):
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            logger.error(f"감지 히스토리 로드 실패: {e}")
        
        return []
    
    def _save_detection_history(self):
        """감지 히스토리 저장"""
        try:
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(self.detection_history, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"감지 히스토리 저장 실패: {e}")


def create_bias_detector() -> BiasDetector:
    """BiasDetector 인스턴스 생성"""
    bias_data_dir = os.path.join(Config.get_evolution_dir(), "bias_data")
    return BiasDetector(bias_data_dir) 