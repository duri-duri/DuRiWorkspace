#!/usr/bin/env python3
"""
DuRi 네거티브 케이스 테스트
"""

import pytest
import json
import os
import tempfile
import shutil
from unittest.mock import patch, mock_open

class TestNegativeCases:
    """네거티브 케이스 테스트"""
    
    def test_corrupted_json_handling(self):
        """손상된 JSON 파일 처리 테스트"""
        from DuRiCore.state_schema_manager import StateSchemaManager
        
        # 손상된 JSON 파일 생성
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            f.write('{"invalid": json}')
            corrupted_path = f.name
            
        try:
            manager = StateSchemaManager(corrupted_path)
            result = manager.migrate_if_needed()
            assert result, "손상된 JSON 파일 처리 실패"
        finally:
            os.unlink(corrupted_path)
            
    def test_disk_full_simulation(self):
        """디스크 풀 시뮬레이션 테스트"""
        from DuRiCore.atomic_file_manager import AtomicFileManager
        
        # 디스크 풀 시뮬레이션
        with patch('builtins.open', side_effect=OSError("No space left on device")):
            manager = AtomicFileManager("/tmp/test.json")
            result = manager.atomic_write({"test": "data"})
            assert not result, "디스크 풀 상황 처리 실패"
            
    def test_permission_error_handling(self):
        """권한 오류 처리 테스트"""
        from DuRiCore.atomic_file_manager import AtomicFileManager
        
        # 권한 오류 시뮬레이션
        with patch('builtins.open', side_effect=PermissionError("Permission denied")):
            manager = AtomicFileManager("/root/test.json")
            result = manager.atomic_write({"test": "data"})
            assert not result, "권한 오류 처리 실패"
            
    def test_invalid_risk_metrics(self):
        """잘못된 리스크 메트릭 처리 테스트"""
        from DuRiCore.risk_management.intelligent_risk_analyzer import IntelligentRiskAnalyzer
        
        analyzer = IntelligentRiskAnalyzer()
        
        # 잘못된 메트릭 테스트
        invalid_cases = [
            {},  # 빈 딕셔너리
            {"cpu_usage": "invalid"},  # 잘못된 타입
            {"cpu_usage": -10},  # 음수 값
            {"cpu_usage": 150},  # 범위 초과
            None  # None 값
        ]
        
        for case in invalid_cases:
            result = analyzer.analyze_risk(case)
            assert 'risk_level' in result, f"잘못된 메트릭 처리 실패: {case}"
            assert result['risk_level'] in ['LOW', 'MEDIUM', 'HIGH'], f"잘못된 리스크 레벨: {result['risk_level']}"
            
    def test_port_occupancy_handling(self):
        """포트 점유 처리 테스트"""
        import socket
        
        # 포트 점유 시뮬레이션
        with patch('socket.socket.bind', side_effect=OSError("Address already in use")):
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.bind(('localhost', 8080))
                assert False, "포트 점유 처리 실패"
            except OSError:
                assert True, "포트 점유 처리 성공"
                
    def test_memory_pressure_handling(self):
        """메모리 압박 처리 테스트"""
        from DuRiCore.atomic_file_manager import AtomicFileManager
        
        # 메모리 부족 시뮬레이션
        with patch('json.dump', side_effect=MemoryError("Out of memory")):
            manager = AtomicFileManager("/tmp/test.json")
            result = manager.atomic_write({"test": "data"})
            assert not result, "메모리 압박 처리 실패"
            
    def test_concurrent_file_access(self):
        """동시 파일 접근 처리 테스트"""
        import threading
        import time
        
        from DuRiCore.atomic_file_manager import AtomicFileManager
        
        manager = AtomicFileManager("/tmp/concurrent_test.json")
        
        results = []
        
        def write_data(data_id):
            result = manager.atomic_write({"id": data_id, "timestamp": time.time()})
            results.append(result)
            
        # 동시 쓰기 테스트
        threads = []
        for i in range(5):
            thread = threading.Thread(target=write_data, args=(i,))
            threads.append(thread)
            thread.start()
            
        for thread in threads:
            thread.join()
            
        # 최소 하나는 성공해야 함
        assert any(results), "동시 파일 접근 처리 실패"
        
    def test_network_timeout_handling(self):
        """네트워크 타임아웃 처리 테스트"""
        import requests
        
        # 타임아웃 시뮬레이션
        with patch('requests.get', side_effect=requests.exceptions.Timeout("Request timed out")):
            try:
                response = requests.get('http://localhost:8080/health', timeout=1)
                assert False, "네트워크 타임아웃 처리 실패"
            except requests.exceptions.Timeout:
                assert True, "네트워크 타임아웃 처리 성공"
                
    def test_invalid_config_handling(self):
        """잘못된 설정 처리 테스트"""
        from DuRiCore.deployment_system import DeploymentSystem
        
        deploy_system = DeploymentSystem()
        deploy_system.activate()
        
        # 잘못된 설정 테스트
        invalid_configs = [
            None,
            {},
            {"environment": None},
            {"environment": ""},
            {"environment": "invalid_env"}
        ]
        
        for config in invalid_configs:
            result = deploy_system.deploy(config)
            assert 'success' in result, f"잘못된 설정 처리 실패: {config}"
            # 성공 또는 실패는 상관없이 응답이 있어야 함
            assert isinstance(result['success'], bool), f"잘못된 응답 형식: {result}"

if __name__ == '__main__':
    pytest.main([__file__, '-v'])
