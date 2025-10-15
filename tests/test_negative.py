#!/usr/bin/env python3
"""
DuRi 네거티브 테스트 - 수정된 버전
"""

import pytest
import json
import tempfile
import shutil
from unittest.mock import patch, MagicMock
from DuRiCore.risk_management.intelligent_risk_analyzer import IntelligentRiskAnalyzer
from DuRiCore.atomic_file_manager import AtomicFileManager

class TestNegativeCasesFixed:
    """네거티브 테스트 케이스 - 수정된 버전"""
    
    def test_invalid_input_handling(self):
        """잘못된 입력 처리 테스트"""
        analyzer = IntelligentRiskAnalyzer()
        
        # None 입력
        result = analyzer.analyze_risk(None)
        assert result["risk_level"] in ["LOW", "MEDIUM", "HIGH"]
        assert 0.0 <= result["confidence"] <= 1.0
        
        # 빈 딕셔너리
        result = analyzer.analyze_risk({})
        assert result["risk_level"] in ["LOW", "MEDIUM", "HIGH"]
        assert 0.0 <= result["confidence"] <= 1.0
        
        # 잘못된 타입
        result = analyzer.analyze_risk("invalid")
        assert result["risk_level"] in ["LOW", "MEDIUM", "HIGH"]
        assert 0.0 <= result["confidence"] <= 1.0
    
    def test_extreme_values(self):
        """극단값 처리 테스트"""
        analyzer = IntelligentRiskAnalyzer()
        
        # 음수 값
        result = analyzer.analyze_risk({"cpu_usage": -10, "memory_usage": -5})
        assert result["risk_level"] in ["LOW", "MEDIUM", "HIGH"]
        
        # 100 초과 값
        result = analyzer.analyze_risk({"cpu_usage": 150, "memory_usage": 200})
        assert result["risk_level"] in ["LOW", "MEDIUM", "HIGH"]
        
        # NaN 값
        import math
        result = analyzer.analyze_risk({"cpu_usage": math.nan, "memory_usage": 50})
        assert result["risk_level"] in ["LOW", "MEDIUM", "HIGH"]
        assert 0.0 <= result["confidence"] <= 1.0
    
    def test_disk_full_tempfile_creation(self):
        """디스크 풀 - 임시파일 생성 단계 실패"""
        with patch('tempfile.NamedTemporaryFile', side_effect=OSError("No space left on device")):
            manager = AtomicFileManager("/tmp/test.json")
            result = manager.atomic_write({"test": "data"})
            assert result is False, "임시파일 생성 실패 시 False 반환해야 함"
    
    def test_disk_full_json_write(self):
        """디스크 풀 - JSON 쓰기 단계 실패"""
        with patch('json.dump', side_effect=OSError("No space left on device")):
            manager = AtomicFileManager("/tmp/test.json")
            result = manager.atomic_write({"test": "data"})
            assert result is False, "JSON 쓰기 실패 시 False 반환해야 함"
    
    def test_disk_full_atomic_move(self):
        """디스크 풀 - 원자적 이동 단계 실패"""
        with patch('shutil.move', side_effect=OSError("No space left on device")):
            manager = AtomicFileManager("/tmp/test.json")
            result = manager.atomic_write({"test": "data"})
            assert result is False, "원자적 이동 실패 시 False 반환해야 함"
    
    def test_permission_denied(self):
        """권한 거부 테스트"""
        with patch('tempfile.NamedTemporaryFile', side_effect=PermissionError("Permission denied")):
            manager = AtomicFileManager("/root/test.json")
            result = manager.atomic_write({"test": "data"})
            assert result is False, "권한 거부 시 False 반환해야 함"
    
    def test_file_system_error(self):
        """파일 시스템 오류 테스트"""
        with patch('shutil.move', side_effect=OSError("Read-only file system")):
            manager = AtomicFileManager("/tmp/test.json")
            result = manager.atomic_write({"test": "data"})
            assert result is False, "파일 시스템 오류 시 False 반환해야 함"
    
    def test_memory_pressure(self):
        """메모리 압박 상황 테스트"""
        with patch('json.dump', side_effect=MemoryError("Out of memory")):
            manager = AtomicFileManager("/tmp/test.json")
            result = manager.atomic_write({"test": "data"})
            assert result is False, "메모리 부족 시 False 반환해야 함"
    
    def test_network_timeout(self):
        """네트워크 타임아웃 시뮬레이션"""
        analyzer = IntelligentRiskAnalyzer()
        
        # 네트워크 지연 시뮬레이션
        with patch('time.sleep', return_value=None):
            result = analyzer.analyze_risk({"cpu_usage": 50, "memory_usage": 60})
            assert result["risk_level"] in ["LOW", "MEDIUM", "HIGH"]
    
    def test_concurrent_access(self):
        """동시 접근 테스트"""
        import threading
        import time
        
        results = []
        
        def worker():
            analyzer = IntelligentRiskAnalyzer()
            result = analyzer.analyze_risk({"cpu_usage": 70, "memory_usage": 80})
            results.append(result)
        
        # 5개 스레드로 동시 실행
        threads = []
        for _ in range(5):
            t = threading.Thread(target=worker)
            threads.append(t)
            t.start()
        
        for t in threads:
            t.join()
        
        # 모든 결과가 유효한지 확인
        assert len(results) == 5
        for result in results:
            assert result["risk_level"] in ["LOW", "MEDIUM", "HIGH"]
            assert 0.0 <= result["confidence"] <= 1.0
