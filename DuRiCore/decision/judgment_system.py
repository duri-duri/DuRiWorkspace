#!/usr/bin/env python3
"""
DuRi 판단 시스템 - 간단한 버전
StrategicLearningEngine과 연동하여 판단 및 학습을 수행
"""

import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from learning.strategic_learning_engine import StrategicLearningEngine


class JudgmentSystem:
    def __init__(self):
        self.strategic_learner = StrategicLearningEngine()

    def judge(self, situation):
        """
        상황을 분석하여 판단을 내리고 전략 학습 시스템에 기록
        """
        if "위협" in situation:
            action = "도움 요청"
            reason = "상황이 위험해 보여서"
        elif "우호" in situation:
            action = "대화 시도"
            reason = "우호적인 분위기로 판단"
        else:
            action = "상황 분석 대기"
            reason = "판단 근거 부족"

        # 전략 학습 시스템에 판단 기록
        self.strategic_learner.observe_decision(situation, action, reason)
        return action
