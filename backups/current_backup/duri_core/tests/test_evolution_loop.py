#!/usr/bin/env python3
"""
Evolution 루프 테스트
"""

import unittest
import json
import os
from evolution.evolution_controller import EvolutionController

class TestEvolutionLoop(unittest.TestCase):
    """Evolution 루프 테스트 클래스"""
    
    def setUp(self):
        """테스트 설정"""
        self.controller = EvolutionController()
        
    def tearDown(self):
        """테스트 정리"""
        # 테스트 중 생성된 파일들 정리
        test_files = ["evolution_log.json", "experience_stats.json"]
        for file in test_files:
            if os.path.exists(file):
                os.remove(file)
    
    def test_run_loop_basic(self):
        """기본 run_loop 테스트"""
        emotion = "happy"
        action = "dance"
        
        result = self.controller.run_loop(emotion, action)
        
        # 결과 구조 확인
        self.assertIsInstance(result, dict)
        self.assertIn('success', result)
        self.assertIn('details', result)
        self.assertIsInstance(result['success'], bool)
        self.assertIsInstance(result['details'], str)
        
        # 상세 내용 확인
        self.assertIn(emotion, result['details'])
        self.assertIn(action, result['details'])
    
    def test_run_loop_multiple_emotions(self):
        """여러 감정으로 run_loop 테스트"""
        test_cases = [
            ("happy", "dance"),
            ("sad", "comfort"),
            ("angry", "calm_down"),
            ("fear", "reassure")
        ]
        
        for emotion, action in test_cases:
            with self.subTest(emotion=emotion, action=action):
                result = self.controller.run_loop(emotion, action)
                
                self.assertIsInstance(result, dict)
                self.assertIn('success', result)
                self.assertIn('details', result)
                self.assertIn(emotion, result['details'])
                self.assertIn(action, result['details'])
    
    def test_log_file_creation(self):
        """로그 파일 생성 확인"""
        emotion = "happy"
        action = "dance"
        
        # 로그 파일이 없음을 확인
        self.assertFalse(os.path.exists("evolution_log.json"))
        
        # run_loop 실행
        self.controller.run_loop(emotion, action)
        
        # 로그 파일이 생성되었는지 확인
        self.assertTrue(os.path.exists("evolution_log.json"))
        
        # 로그 내용 확인
        with open("evolution_log.json", 'r', encoding='utf-8') as f:
            lines = f.readlines()
            self.assertGreater(len(lines), 0)
            
            # 마지막 로그 엔트리 확인
            last_entry = json.loads(lines[-1])
            self.assertIn('timestamp', last_entry)
            self.assertEqual(last_entry['emotion'], emotion)
            self.assertEqual(last_entry['action'], action)
            self.assertIn('result', last_entry)
    
    def test_stats_file_creation(self):
        """통계 파일 생성 확인"""
        emotion = "happy"
        action = "dance"
        
        # 통계 파일이 없음을 확인
        self.assertFalse(os.path.exists("experience_stats.json"))
        
        # run_loop 실행
        self.controller.run_loop(emotion, action)
        
        # 통계 파일이 생성되었는지 확인
        self.assertTrue(os.path.exists("experience_stats.json"))
        
        # 통계 내용 확인
        with open("experience_stats.json", 'r', encoding='utf-8') as f:
            stats = json.load(f)
            key = f"{emotion}_{action}"
            self.assertIn(key, stats)
            
            stat_entry = stats[key]
            self.assertEqual(stat_entry['emotion'], emotion)
            self.assertEqual(stat_entry['action'], action)
            self.assertIn('success_count', stat_entry)
            self.assertIn('fail_count', stat_entry)
            self.assertIn('total_count', stat_entry)
            self.assertIn('success_rate', stat_entry)
            self.assertEqual(stat_entry['total_count'], 1)
    
    def test_stats_accumulation(self):
        """통계 누적 확인"""
        emotion = "happy"
        action = "dance"
        
        # 여러 번 실행
        for _ in range(5):
            self.controller.run_loop(emotion, action)
        
        # 통계 확인
        stats = self.controller.get_experience_stats(emotion, action)
        key = f"{emotion}_{action}"
        
        self.assertIn(key, stats)
        stat_entry = stats[key]
        self.assertEqual(stat_entry['total_count'], 5)
        self.assertGreaterEqual(stat_entry['success_count'], 0)
        self.assertGreaterEqual(stat_entry['fail_count'], 0)
        self.assertEqual(stat_entry['success_count'] + stat_entry['fail_count'], 5)
    
    def test_get_experience_stats(self):
        """경험 통계 조회 테스트"""
        # 여러 감정-행동 조합으로 테스트
        test_cases = [
            ("happy", "dance"),
            ("sad", "comfort"),
            ("happy", "sing")
        ]
        
        for emotion, action in test_cases:
            self.controller.run_loop(emotion, action)
        
        # 전체 통계 조회
        all_stats = self.controller.get_experience_stats()
        self.assertIsInstance(all_stats, dict)
        self.assertGreater(len(all_stats), 0)
        
        # 특정 감정 통계 조회
        happy_stats = self.controller.get_experience_stats(emotion="happy")
        self.assertIsInstance(happy_stats, dict)
        self.assertGreater(len(happy_stats), 0)
        
        # 모든 happy 관련 키 확인
        for key in happy_stats.keys():
            self.assertIn("happy", key)

if __name__ == '__main__':
    unittest.main() 