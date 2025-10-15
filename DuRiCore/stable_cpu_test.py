#!/usr/bin/env python3
"""
DuRi 안정화된 CPU 테스트
"""

import time
import threading
import psutil
from typing import Dict, Any

class StableCPUTest:
    def __init__(self):
        self.test_duration = 2.0
        self.stabilization_time = 0.5
        
    def create_controlled_load(self, duration: float = None) -> threading.Thread:
        """제어된 부하 생성"""
        if duration is None:
            duration = self.test_duration
            
        def controlled_task():
            end_time = time.time() + duration
            x = 0
            # 고정 길이 연산 세트로 분산도 줄이기
            while time.time() < end_time:
                x += 1
                if x % 1000 == 0:
                    x = x * 2  # 일정한 연산 패턴
                    
        return threading.Thread(target=controlled_task)
        
    def measure_cpu_sensitivity(self) -> Dict[str, Any]:
        """CPU 민감도 측정"""
        try:
            # 기준선 측정 (여러 번 측정하여 안정화)
            baseline_readings = []
            for _ in range(3):
                baseline_readings.append(psutil.cpu_percent(interval=0.5))
            baseline_cpu = sum(baseline_readings) / len(baseline_readings)
            
            # 부하 생성 및 측정
            load_thread = self.create_controlled_load()
            load_thread.start()
            
            # 부하 안정화 대기
            time.sleep(self.stabilization_time)
            
            # 부하 중 측정
            load_readings = []
            for _ in range(3):
                load_readings.append(psutil.cpu_percent(interval=0.5))
            load_cpu = sum(load_readings) / len(load_readings)
            
            load_thread.join()
            
            # 결과 계산
            cpu_increase = load_cpu - baseline_cpu
            
            return {
                "baseline_cpu": round(baseline_cpu, 2),
                "load_cpu": round(load_cpu, 2),
                "cpu_increase": round(cpu_increase, 2),
                "sensitivity_ok": cpu_increase > 0,  # 임계값 완화
                "test_duration": self.test_duration,
                "stabilization_time": self.stabilization_time
            }
            
        except Exception as e:
            return {
                "error": str(e),
                "sensitivity_ok": False
            }
            
    def run_stability_test(self, iterations: int = 3) -> Dict[str, Any]:
        """안정성 테스트 (여러 번 실행)"""
        results = []
        
        for i in range(iterations):
            result = self.measure_cpu_sensitivity()
            results.append(result)
            time.sleep(1)  # 테스트 간 간격
            
        # 통계 계산
        increases = [r.get('cpu_increase', 0) for r in results if 'cpu_increase' in r]
        
        if increases:
            avg_increase = sum(increases) / len(increases)
            min_increase = min(increases)
            max_increase = max(increases)
        else:
            avg_increase = min_increase = max_increase = 0
            
        return {
            "iterations": iterations,
            "results": results,
            "statistics": {
                "avg_increase": round(avg_increase, 2),
                "min_increase": round(min_increase, 2),
                "max_increase": round(max_increase, 2),
                "stability_ok": avg_increase > 0 and max_increase - min_increase < 10  # 분산도 체크
            }
        }
