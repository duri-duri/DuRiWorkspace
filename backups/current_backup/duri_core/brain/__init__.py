"""
DuRi Brain - 감정-판단-반응 루프 관리 시스템

Brain은 감정 입력의 발생 시점과 내용을 기록하고, 
Core가 내린 판단 이후 외부 반응(결과, 피드백)을 수집하여 
다시 Core에게 전달하는 역할을 담당합니다.
"""

from .emotion_recorder import EmotionRecorder
from .feedback_collector import FeedbackCollector
from .loop_manager import LoopManager
from .brain_controller import BrainController
from .action_processor import BrainService, brain_service

__all__ = [
    'EmotionRecorder',
    'FeedbackCollector', 
    'LoopManager',
    'BrainController',
    'BrainService',
    'brain_service'
] 