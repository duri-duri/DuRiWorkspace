#!/usr/bin/env python3
"""
Emotion Summary Visualization for DuRi System

This module provides a unified interface for emotion analysis and visualization.
It imports functionality from the specialized modules:
- summary_loader.py: Data loading and validation
- summary_analyzer.py: Analysis by emotion level
- summary_reporter.py: Report generation
"""

# Import the main functionality from the specialized modules
from .summary_reporter import create_emotion_summary, SummaryReporter
from .summary_analyzer import EmotionSummaryAnalyzer
from .summary_loader import DataLoader, load_and_validate_data

# Re-export the main classes and functions for backward compatibility
__all__ = [
    'create_emotion_summary',
    'SummaryReporter',
    'EmotionSummaryAnalyzer',
    'DataLoader',
    'load_and_validate_data'
]


if __name__ == "__main__":
    # 테스트 실행
    import sys
    
    if len(sys.argv) != 3:
        print("사용법: python emotion_summary.py <stats_path> <evolution_path>")
        sys.exit(1)
    
    stats_path = sys.argv[1]
    evolution_path = sys.argv[2]
    
    summary = create_emotion_summary(stats_path, evolution_path)
    print(json.dumps(summary, indent=2, ensure_ascii=False)) 