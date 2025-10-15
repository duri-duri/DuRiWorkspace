#!/usr/bin/env python3
"""
DuRi 스모크 테스트 스위트 (수정 버전)
"""

import pytest
import json
import os
import time
import psutil
import requests
from datetime import datetime

# 로깅 설정 초기화
from DuRiCore.logging_setup import ensure_duri_logger, flush_duri_logger
ensure_duri_logger()

class TestSmokeSuite:
    """스모크 테스트 스위트"""
    
    def test_risk_variability(self):
        """리스크 분석 가변성 테스트"""
        from DuRiCore.risk_management.intelligent_risk_analyzer import IntelligentRiskAnalyzer
        
        analyzer = IntelligentRiskAnalyzer()
        
        # 다양한 입력으로 테스트
        cases = [
            {'cpu_usage': 10, 'memory_usage': 20},
            {'cpu_usage': 50, 'memory_usage': 60},
            {'cpu_usage': 90, 'memory_usage': 95}
        ]
        
        results = [analyzer.analyze_risk(case) for case in cases]
        
        # 결과가 다른지 확인
        risk_levels = [r['risk_level'] for r in results]
        assert len(set(risk_levels)) > 1, f"All risk levels are the same: {risk_levels}"
        
        # 신뢰도가 다른지 확인
        confidences = [r['confidence'] for r in results]
        assert len(set(confidences)) > 1, f"All confidences are the same: {confidences}"
        
    def test_state_persistence(self):
        """상태 지속성 테스트"""
        from duri_modules.autonomous.duri_autonomous_core import DuRiAutonomousCore
        
        core = DuRiAutonomousCore()
        core.activate()
        
        # 두 번 실행
        r1 = core.run_learning_cycle()
        r2 = core.run_learning_cycle()
        
        # 사이클 ID가 다른지 확인
        assert r1['cycle_id'] != r2['cycle_id'], "Cycle IDs are the same"
        
        # 상태 파일 존재 확인
        state_files = []
        for d in ['.', '/home/duri/DuRiWorkspace', '/tmp']:
            if os.path.exists(d):
                for root, dirs, files in os.walk(d):
                    for file in files:
                        if 'CYCLE' in file or 'cycle' in file:
                            state_files.append(os.path.join(root, file))
        
        assert len(state_files) > 0, "No state files found"
        
    def test_api_visibility(self):
        """API 가시성 테스트"""
        try:
            response = requests.get('http://localhost:8080/health', timeout=5)
            assert response.status_code == 200, f"Health check failed: {response.status_code}"
            
            data = response.json()
            assert data['status'] == 'healthy', f"Service not healthy: {data['status']}"
            
        except requests.exceptions.RequestException as e:
            pytest.skip(f"API not available: {e}")
            
    def test_deploy_artifact(self):
        """배포 아티팩트 테스트"""
        from DuRiCore.deployment_system import DeploymentSystem
        
        deploy_system = DeploymentSystem()
        deploy_system.activate()
        
        result = deploy_system.deploy({'environment': 'production'})
        
        assert result['success'], "Deployment failed"
        assert 'deployment' in result, "No deployment data"
        
        # 아티팩트 파일 존재 확인
        artifact_path = result['deployment'].get('artifact_path')
        if artifact_path:
            assert os.path.exists(artifact_path), f"Artifact file not found: {artifact_path}"
            
    def test_psutil_sensitivity(self):
        """성능 측정 민감도 테스트"""
        # 기준선 측정
        cpu_idle = psutil.cpu_percent(interval=1)
        
        # 부하 생성
        def create_load():
            end_time = time.time() + 2
            x = 0
            while time.time() < end_time:
                x += 1
                
        import threading
        load_thread = threading.Thread(target=create_load)
        load_thread.start()
        
        time.sleep(1)  # 부하 안정화
        cpu_load = psutil.cpu_percent(interval=1)
        
        load_thread.join()
        
        # CPU 사용률 증가 확인
        cpu_increase = cpu_load - cpu_idle
        assert cpu_increase > 0, f"CPU usage did not increase: {cpu_increase}%"
        
    def test_logging_persistence(self):
        """로그 지속성 테스트"""
        log_file = './logs/duri-core.log'
        
        if os.path.exists(log_file):
            initial_size = os.path.getsize(log_file)
            
            # 로그 생성
            import logging
            logger = logging.getLogger('duri-core')
            logger.info('Smoke test log entry')
            
            # 강제 flush
            flush_duri_logger()
            time.sleep(0.1)  # 로그 쓰기 대기
            
            # 로그 파일 크기 증가 확인
            final_size = os.path.getsize(log_file)
            
            assert final_size > initial_size, "Log file size did not increase"
        else:
            pytest.skip("Log file not found")

if __name__ == '__main__':
    pytest.main([__file__, '-v'])
