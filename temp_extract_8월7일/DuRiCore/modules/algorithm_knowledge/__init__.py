"""
알고리즘 지식 시스템 모듈
DuRi의 학습한 지식을 알고리즘화하여 저장하고 재사용하는 시스템
"""

from .algorithm_knowledge_base import (
    AlgorithmKnowledge,
    AlgorithmConnection,
    ProblemPattern,
    AlgorithmKnowledgeBase
)

from .algorithm_selection_engine import (
    ProblemContext,
    AlgorithmRecommendation,
    CombinedAlgorithm,
    AlgorithmSelectionEngine
)

from .algorithm_evolution_system import (
    LearningSession,
    AlgorithmImprovement,
    NewAlgorithm,
    AlgorithmEvolutionSystem
)

from .integrated_algorithm_system import IntegratedAlgorithmSystem

__all__ = [
    # 기본 데이터 구조
    'AlgorithmKnowledge',
    'AlgorithmConnection', 
    'ProblemPattern',
    
    # 선택 엔진
    'ProblemContext',
    'AlgorithmRecommendation',
    'CombinedAlgorithm',
    'AlgorithmSelectionEngine',
    
    # 진화 시스템
    'LearningSession',
    'AlgorithmImprovement',
    'NewAlgorithm',
    'AlgorithmEvolutionSystem',
    
    # 통합 시스템
    'IntegratedAlgorithmSystem'
]

__version__ = "1.0.0"
__author__ = "DuRi AI Team"
__description__ = "알고리즘화된 지식 저장 및 재사용 시스템"
