#!/usr/bin/env python3
"""
Tests for Decision Logic in DuRi Emotion Processing System

This module tests the decision-making logic to ensure:
- Known emotions return non-fallback actions
- Unknown emotions return fallback actions with proper reason
"""

import unittest
import tempfile
import os
import json
from unittest.mock import patch, MagicMock
from duri_core.core.decision import create_decision, apply_emotion_rules
from duri_core.core.stats import choose_best_action
from duri_common.config.emotion_labels import ALL_EMOTIONS, EmotionLevel, is_valid_emotion


class TestDecisionLogic(unittest.TestCase):
    """의사결정 로직 테스트 클래스"""
    
    def setUp(self):
        """테스트 설정"""
        # 임시 파일들 생성
        self.temp_dir = tempfile.mkdtemp()
        self.evolution_log_path = os.path.join(self.temp_dir, "test_evolution_log.json")
        self.stats_path = os.path.join(self.temp_dir, "test_action_stats.json")
        
        # 테스트용 진화 로그 생성
        self.test_evolution_log = [
            {
                "emotion": "happy",
                "decision": {"action": "reflect", "confidence": 0.95},
                "result": "success"
            },
            {
                "emotion": "angry",
                "decision": {"action": "wait", "confidence": 0.6},
                "result": "fail"
            }
        ]
        
        with open(self.evolution_log_path, 'w') as f:
            json.dump(self.test_evolution_log, f)
        
        # 테스트용 액션 통계 생성
        self.test_stats = {
            "emotions": {
                "happy": {"total": 10, "success": 9, "fail": 1},
                "angry": {"total": 8, "success": 3, "fail": 5},
                "curious": {"total": 5, "success": 4, "fail": 1}
            },
            "actions": {
                "reflect": {"total": 15, "success": 13, "fail": 2},
                "wait": {"total": 8, "success": 3, "fail": 5},
                "console": {"total": 5, "success": 4, "fail": 1}
            },
            "emotion_action_pairs": {
                "happy_reflect": {"total": 8, "success": 7, "fail": 1},
                "angry_wait": {"total": 6, "success": 2, "fail": 4},
                "curious_observe": {"total": 4, "success": 3, "fail": 1}
            }
        }
        
        with open(self.stats_path, 'w') as f:
            json.dump(self.test_stats, f)
    
    def tearDown(self):
        """테스트 정리"""
        # 임시 파일들 삭제
        if os.path.exists(self.evolution_log_path):
            os.remove(self.evolution_log_path)
        if os.path.exists(self.stats_path):
            os.remove(self.stats_path)
        if os.path.exists(self.temp_dir):
            os.rmdir(self.temp_dir)
    
    def test_known_emotions_return_non_fallback_actions(self):
        """알려진 감정들이 fallback이 아닌 액션을 반환하는지 테스트"""
        known_emotions = ["happy", "sad", "angry", "curiosity", "frustration", "regret"]
        
        for emotion in known_emotions:
            with self.subTest(emotion=emotion):
                # 감정이 유효한지 확인
                self.assertTrue(is_valid_emotion(emotion), f"감정 '{emotion}'이 유효해야 함")
                
                # 통계 기반 의사결정 테스트
                decision = create_decision(emotion, self.evolution_log_path, self.stats_path)
                
                # fallback이 아닌지 확인
                self.assertNotIn("fallback", decision, f"감정 '{emotion}'에 대해 fallback이 반환되면 안 됨")
                self.assertNotIn("reason", decision, f"감정 '{emotion}'에 대해 reason이 반환되면 안 됨")
                
                # 필수 필드 확인
                self.assertIn("action", decision, f"감정 '{emotion}'에 대해 action이 있어야 함")
                self.assertIn("confidence", decision, f"감정 '{emotion}'에 대해 confidence가 있어야 함")
                
                # 액션이 유효한지 확인
                valid_actions = ["reflect", "wait", "console", "act", "observe"]
                self.assertIn(decision["action"], valid_actions, f"감정 '{emotion}'의 액션이 유효해야 함")
                
                # 신뢰도가 유효한지 확인
                self.assertGreaterEqual(decision["confidence"], 0.0, f"감정 '{emotion}'의 신뢰도가 0 이상이어야 함")
                self.assertLessEqual(decision["confidence"], 1.0, f"감정 '{emotion}'의 신뢰도가 1 이하여야 함")
    
    def test_unknown_emotions_return_fallback_actions(self):
        """알 수 없는 감정들이 fallback 액션을 반환하는지 테스트"""
        unknown_emotions = ["invalid_emotion", "test123", "unknown_feeling", "fake_emotion"]
        
        for emotion in unknown_emotions:
            with self.subTest(emotion=emotion):
                # 감정이 유효하지 않은지 확인
                self.assertFalse(is_valid_emotion(emotion), f"감정 '{emotion}'이 유효하지 않아야 함")
                
                # 통계 기반 의사결정 테스트
                decision = create_decision(emotion, self.evolution_log_path, self.stats_path)
                
                # fallback 필드 확인
                self.assertIn("fallback", decision, f"알 수 없는 감정 '{emotion}'에 대해 fallback이 있어야 함")
                self.assertTrue(decision["fallback"], f"알 수 없는 감정 '{emotion}'의 fallback이 True여야 함")
                
                # reason 필드 확인
                self.assertIn("reason", decision, f"알 수 없는 감정 '{emotion}'에 대해 reason이 있어야 함")
                self.assertIn(emotion, decision["reason"], f"reason에 감정명 '{emotion}'이 포함되어야 함")
                
                # 필수 필드 확인
                self.assertIn("action", decision, f"알 수 없는 감정 '{emotion}'에 대해 action이 있어야 함")
                self.assertIn("confidence", decision, f"알 수 없는 감정 '{emotion}'에 대해 confidence가 있어야 함")
                
                # fallback 액션이 observe인지 확인
                self.assertEqual(decision["action"], "observe", f"알 수 없는 감정 '{emotion}'의 fallback 액션이 'observe'여야 함")
                
                # fallback 신뢰도가 0.5인지 확인
                self.assertEqual(decision["confidence"], 0.5, f"알 수 없는 감정 '{emotion}'의 fallback 신뢰도가 0.5여야 함")
    
    def test_decision_without_stats_path(self):
        """통계 파일 경로가 없을 때의 의사결정 테스트"""
        known_emotions = ["happy", "angry", "curiosity"]
        
        for emotion in known_emotions:
            with self.subTest(emotion=emotion):
                # 통계 경로 없이 의사결정
                decision = create_decision(emotion, self.evolution_log_path, stats_path=None)
                
                # fallback이 아닌지 확인
                self.assertNotIn("fallback", decision, f"감정 '{emotion}'에 대해 fallback이 반환되면 안 됨")
                
                # 필수 필드 확인
                self.assertIn("action", decision, f"감정 '{emotion}'에 대해 action이 있어야 함")
                self.assertIn("confidence", decision, f"감정 '{emotion}'에 대해 confidence가 있어야 함")
                self.assertIn("method", decision, f"감정 '{emotion}'에 대해 method가 있어야 함")
                
                # method가 rule_based인지 확인
                self.assertEqual(decision["method"], "rule_based", f"감정 '{emotion}'의 method가 'rule_based'여야 함")
    
    def test_decision_with_invalid_stats_path(self):
        """유효하지 않은 통계 파일 경로로 의사결정 테스트"""
        emotion = "happy"
        
        # 존재하지 않는 통계 파일 경로 사용
        invalid_stats_path = "/path/to/nonexistent/stats.json"
        
        # 의사결정 생성 (예외가 발생하지 않아야 함)
        decision = create_decision(emotion, self.evolution_log_path, invalid_stats_path)
        
        # fallback이 아닌지 확인 (기본 로직으로 fallback)
        self.assertNotIn("fallback", decision, f"감정 '{emotion}'에 대해 fallback이 반환되면 안 됨")
        
        # 필수 필드 확인
        self.assertIn("action", decision, f"감정 '{emotion}'에 대해 action이 있어야 함")
        self.assertIn("confidence", decision, f"감정 '{emotion}'에 대해 confidence가 있어야 함")
        self.assertIn("method", decision, f"감정 '{emotion}'에 대해 method가 있어야 함")
        
        # method가 rule_based인지 확인
        self.assertEqual(decision["method"], "rule_based", f"감정 '{emotion}'의 method가 'rule_based'여야 함")
    
    def test_apply_emotion_rules(self):
        """감정별 규칙 적용 테스트"""
        # 테스트용 통계 기반 의사결정
        stats_decision = {
            "action": "reflect",
            "confidence": 0.4,
            "method": "statistics"
        }
        
        # 분노 관련 감정 테스트
        anger_emotions = ["angry", "frustration"]
        for emotion in anger_emotions:
            with self.subTest(emotion=emotion):
                result = apply_emotion_rules(emotion, stats_decision)
                
                # 규칙이 적용되었는지 확인
                self.assertTrue(result["rule_applied"], f"감정 '{emotion}'에 대해 규칙이 적용되어야 함")
                self.assertEqual(result["action"], "wait", f"감정 '{emotion}'의 액션이 'wait'여야 함")
                self.assertEqual(result["confidence"], 0.6, f"감정 '{emotion}'의 신뢰도가 0.6이어야 함")
                self.assertEqual(result["original_action"], "reflect", f"감정 '{emotion}'의 원본 액션이 'reflect'여야 함")
        
        # 슬픔 관련 감정 테스트
        sadness_emotions = ["sad", "regret", "guilt", "shame"]
        for emotion in sadness_emotions:
            with self.subTest(emotion=emotion):
                result = apply_emotion_rules(emotion, stats_decision)
                
                # 규칙이 적용되었는지 확인
                self.assertTrue(result["rule_applied"], f"감정 '{emotion}'에 대해 규칙이 적용되어야 함")
                self.assertEqual(result["action"], "console", f"감정 '{emotion}'의 액션이 'console'이어야 함")
                self.assertEqual(result["confidence"], 0.7, f"감정 '{emotion}'의 신뢰도가 0.7이어야 함")
    
    def test_choose_best_action_pure_statistics(self):
        """순수 통계 기반 액션 선택 테스트"""
        emotion = "happy"
        
        # 통계 기반 액션 선택
        decision = choose_best_action(emotion, self.stats_path)
        
        # 필수 필드 확인
        self.assertIn("action", decision, f"감정 '{emotion}'에 대해 action이 있어야 함")
        self.assertIn("confidence", decision, f"감정 '{emotion}'에 대해 confidence가 있어야 함")
        self.assertIn("method", decision, f"감정 '{emotion}'에 대해 method가 있어야 함")
        
        # method가 statistics인지 확인
        self.assertEqual(decision["method"], "statistics", f"감정 '{emotion}'의 method가 'statistics'여야 함")
        
        # fallback이 아닌지 확인
        self.assertNotIn("fallback", decision, f"감정 '{emotion}'에 대해 fallback이 없어야 함")
    
    def test_emotion_level_validation(self):
        """감정 레벨 검증 테스트"""
        # Level 1 감정들
        level_1_emotions = ["happy", "sad", "angry", "fear", "surprise", "disgust", "shame", "curiosity"]
        for emotion in level_1_emotions:
            with self.subTest(emotion=emotion):
                self.assertTrue(is_valid_emotion(emotion), f"Level 1 감정 '{emotion}'이 유효해야 함")
        
        # Level 2 감정들
        level_2_emotions = ["frustration", "relief", "envy", "boredom", "pride"]
        for emotion in level_2_emotions:
            with self.subTest(emotion=emotion):
                self.assertTrue(is_valid_emotion(emotion), f"Level 2 감정 '{emotion}'이 유효해야 함")
        
        # Level 3 감정들
        level_3_emotions = ["regret", "guilt", "empathy", "nostalgia", "awe"]
        for emotion in level_3_emotions:
            with self.subTest(emotion=emotion):
                self.assertTrue(is_valid_emotion(emotion), f"Level 3 감정 '{emotion}'이 유효해야 함")
        
        # 알 수 없는 감정들
        unknown_emotions = ["invalid", "test123", "fake_emotion"]
        for emotion in unknown_emotions:
            with self.subTest(emotion=emotion):
                self.assertFalse(is_valid_emotion(emotion), f"알 수 없는 감정 '{emotion}'이 유효하지 않아야 함")
    
    def test_decision_methods(self):
        """다양한 의사결정 방법 테스트"""
        emotion = "happy"
        
        # 1. 통계 기반 의사결정 (통계 파일 있음)
        decision_with_stats = create_decision(emotion, self.evolution_log_path, self.stats_path)
        self.assertEqual(decision_with_stats["method"], "statistics_with_rules", 
                        "통계 파일이 있을 때 method가 'statistics_with_rules'여야 함")
        
        # 2. 규칙 기반 의사결정 (통계 파일 없음)
        decision_without_stats = create_decision(emotion, self.evolution_log_path, stats_path=None)
        self.assertEqual(decision_without_stats["method"], "rule_based", 
                        "통계 파일이 없을 때 method가 'rule_based'여야 함")
        
        # 3. Fallback 의사결정 (알 수 없는 감정)
        decision_fallback = create_decision("invalid_emotion", self.evolution_log_path, self.stats_path)
        self.assertEqual(decision_fallback["method"], "fallback", 
                        "알 수 없는 감정에 대해 method가 'fallback'이어야 함")


if __name__ == "__main__":
    # 테스트 실행
    unittest.main(verbosity=2) 