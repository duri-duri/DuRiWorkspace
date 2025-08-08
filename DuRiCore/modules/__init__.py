#!/usr/bin/env python3
"""
DuRi Core Modules Package
통합된 모듈 시스템을 제공합니다.
"""

from .judgment_system import JudgmentTraceLogger, JudgmentTrace, StrategicLearningEngine
from .thought_flow import DuRiThoughtFlow, SelfReflectionLoop, ReflectionInsight
from .memory import MemoryManager
from .evolution import SelfEvolutionManager, EvolutionStep
from .integrated_learning_system import IntegratedLearningSystem, LearningCycle

__version__ = "2.0.0"
__author__ = "DuRi"

__all__ = [
    # Judgment System
    'JudgmentTraceLogger',
    'JudgmentTrace', 
    'StrategicLearningEngine',
    
    # Thought Flow
    'DuRiThoughtFlow',
    'SelfReflectionLoop',
    'ReflectionInsight',
    
    # Memory
    'MemoryManager',
    
    # Evolution
    'SelfEvolutionManager',
    'EvolutionStep',
    
    # Integrated Learning System
    'IntegratedLearningSystem',
    'LearningCycle'
]
