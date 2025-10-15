#!/usr/bin/env python3
"""
DuRi 속성기반 테스트 - Hypothesis 사용
"""

import pytest
import tempfile
import os
import json
from hypothesis import given, strategies as st, settings
from DuRiCore.atomic_file_manager import AtomicFileManager
from DuRiCore.risk_management.intelligent_risk_analyzer import IntelligentRiskAnalyzer

class TestPropertyBased:
    """속성기반 테스트"""
    
    @given(st.dictionaries(
        st.text(min_size=1, max_size=10), 
        st.one_of(st.text(), st.integers(), st.floats(), st.booleans())
    ))
    @settings(max_examples=50, deadline=5000)
    def test_atomic_write_property(self, data):
        """원자적 쓰기 속성 테스트"""
        with tempfile.NamedTemporaryFile(delete=False, suffix='.json') as tmp:
            try:
                manager = AtomicFileManager(tmp.name)
                result = manager.atomic_write(data)
                
                # 속성 1: 결과는 항상 boolean
                assert isinstance(result, bool)
                
                # 속성 2: 성공 시 읽기 결과는 원본과 동일
                if result:
                    read_data = manager.atomic_read()
                    assert read_data == data
                
                # 속성 3: 실패 시에도 파일 시스템이 깨끗해야 함
                if not result:
                    assert not os.path.exists(tmp.name) or os.path.getsize(tmp.name) == 0
                    
            finally:
                if os.path.exists(tmp.name):
                    os.unlink(tmp.name)
    
    @given(st.lists(st.dictionaries(
        st.text(min_size=1, max_size=5), 
        st.text()
    ), min_size=0, max_size=10))
    @settings(max_examples=30, deadline=5000)
    def test_atomic_append_property(self, data_list):
        """원자적 추가 속성 테스트"""
        with tempfile.NamedTemporaryFile(delete=False, suffix='.json') as tmp:
            try:
                manager = AtomicFileManager(tmp.name)
                
                # 순차적으로 추가
                for data in data_list:
                    result = manager.atomic_append(data)
                    assert isinstance(result, bool)
                
                # 최종 결과 검증
                if data_list:
                    final_data = manager.atomic_read()
                    assert isinstance(final_data, list)
                    assert len(final_data) == len(data_list)
                    assert final_data == data_list
                    
            finally:
                if os.path.exists(tmp.name):
                    os.unlink(tmp.name)
    
    @given(st.dictionaries(
        st.sampled_from(['cpu_usage', 'memory_usage', 'disk_usage', 'network_usage']),
        st.one_of(
            st.floats(min_value=-100, max_value=200),
            st.integers(min_value=-100, max_value=200),
            st.just(None)
        )
    ))
    @settings(max_examples=100, deadline=3000)
    def test_risk_analyzer_property(self, metrics):
        """리스크 분석기 속성 테스트"""
        analyzer = IntelligentRiskAnalyzer()
        result = analyzer.analyze_risk(metrics)
        
        # 속성 1: 결과 구조 일관성
        assert isinstance(result, dict)
        assert 'risk_level' in result
        assert 'confidence' in result
        assert 'recommendations' in result
        
        # 속성 2: risk_level은 유효한 값
        assert result['risk_level'] in ['LOW', 'MEDIUM', 'HIGH']
        
        # 속성 3: confidence는 0~1 범위
        assert 0.0 <= result['confidence'] <= 1.0
        
        # 속성 4: recommendations는 리스트
        assert isinstance(result['recommendations'], list)
        
        # 속성 5: 모든 문자열은 비어있지 않음
        for rec in result['recommendations']:
            assert isinstance(rec, str)
            assert len(rec) > 0
    
    @given(st.text(min_size=1, max_size=100))
    @settings(max_examples=20, deadline=2000)
    def test_file_path_property(self, path_suffix):
        """파일 경로 속성 테스트"""
        # 안전한 경로 생성
        safe_path = f"/tmp/test_{path_suffix.replace('/', '_').replace('\\', '_')}.json"
        
        manager = AtomicFileManager(safe_path)
        result = manager.atomic_write({"test": "data"})
        
        # 속성: 경로가 안전해야 함
        assert isinstance(result, bool)
        
        # 정리
        if os.path.exists(safe_path):
            os.unlink(safe_path)
    
    def test_concurrent_access_property(self):
        """동시 접근 속성 테스트"""
        import threading
        import time
        
        results = []
        errors = []
        
        def worker(worker_id):
            try:
                analyzer = IntelligentRiskAnalyzer()
                for i in range(10):
                    result = analyzer.analyze_risk({
                        "cpu_usage": 50 + i,
                        "memory_usage": 60 + i
                    })
                    results.append((worker_id, i, result))
                    time.sleep(0.01)  # 짧은 지연
            except Exception as e:
                errors.append((worker_id, str(e)))
        
        # 5개 스레드로 동시 실행
        threads = []
        for i in range(5):
            t = threading.Thread(target=worker, args=(i,))
            threads.append(t)
            t.start()
        
        for t in threads:
            t.join()
        
        # 속성 검증
        assert len(errors) == 0, f"동시 접근 중 오류 발생: {errors}"
        assert len(results) == 50, f"예상 결과 수와 다름: {len(results)}"
        
        # 모든 결과가 유효한지 확인
        for worker_id, i, result in results:
            assert result['risk_level'] in ['LOW', 'MEDIUM', 'HIGH']
            assert 0.0 <= result['confidence'] <= 1.0
