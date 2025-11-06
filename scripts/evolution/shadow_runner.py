#!/usr/bin/env python3
"""
Shadow Runner - Shadow Proxy 비율 가변 및 쌍대 평가 로그
목적: cand vs prod 쌍대 평가 로그 생성
"""

import json
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict


@dataclass
class ShadowRun:
    """Shadow 실행 결과"""
    run_id: str
    timestamp: str
    shadow_proxy_ratio: float  # 0.0 ~ 1.0
    candidate_id: str
    production_id: str
    requests: List[Dict[str, any]]
    results: Dict[str, any]
    metrics: Dict[str, float]
    comparison: Dict[str, float]  # cand vs prod 비교 메트릭


class ShadowRunner:
    """Shadow Runner 클래스"""
    
    def __init__(self, base_dir: Path = Path('var/evolution/shadow')):
        self.base_dir = base_dir
        self.base_dir.mkdir(parents=True, exist_ok=True)
        self.log_file = self.base_dir / 'runs.jsonl'
    
    def run_comparison(self, candidate_id: str, production_id: str, 
                      shadow_proxy_ratio: float = 0.1,
                      num_requests: int = 100) -> ShadowRun:
        """
        Shadow 실행 및 비교
        
        Args:
            candidate_id: 후보 모델/설정 ID
            production_id: 프로덕션 모델/설정 ID
            shadow_proxy_ratio: Shadow 프록시 비율 (0.0 ~ 1.0)
            num_requests: 요청 수
            
        Returns:
            ShadowRun: 실행 결과
        """
        run_id = f"SR-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        
        # 실제 구현에서는 실제 요청을 라우팅하고 결과를 수집
        # 여기서는 스텁 구현
        requests = []
        results = {
            'candidate': {'success': 0, 'failure': 0, 'latency_p95': 0.0},
            'production': {'success': 0, 'failure': 0, 'latency_p95': 0.0},
        }
        
        # 메트릭 계산 (스텁)
        metrics = {
            'candidate_p@3': 0.0,
            'production_p@3': 0.0,
            'candidate_ndcg@3': 0.0,
            'production_ndcg@3': 0.0,
            'candidate_halluc_rate': 0.0,
            'production_halluc_rate': 0.0,
        }
        
        # 비교 메트릭
        comparison = {
            'p@3_delta': metrics['candidate_p@3'] - metrics['production_p@3'],
            'ndcg@3_delta': metrics['candidate_ndcg@3'] - metrics['production_ndcg@3'],
            'halluc_rate_delta': metrics['candidate_halluc_rate'] - metrics['production_halluc_rate'],
        }
        
        shadow_run = ShadowRun(
            run_id=run_id,
            timestamp=datetime.now().isoformat(),
            shadow_proxy_ratio=shadow_proxy_ratio,
            candidate_id=candidate_id,
            production_id=production_id,
            requests=requests,
            results=results,
            metrics=metrics,
            comparison=comparison,
        )
        
        # 로그 저장
        self.save_run(shadow_run)
        
        return shadow_run
    
    def save_run(self, run: ShadowRun):
        """실행 결과 저장"""
        with open(self.log_file, 'a') as f:
            json.dump(asdict(run), f, ensure_ascii=False)
            f.write('\n')
    
    def get_runs(self, candidate_id: Optional[str] = None,
                 limit: int = 100) -> List[ShadowRun]:
        """실행 결과 조회"""
        runs = []
        
        if not self.log_file.exists():
            return runs
        
        with open(self.log_file, 'r') as f:
            for line in f:
                try:
                    data = json.loads(line)
                    if candidate_id and data.get('candidate_id') != candidate_id:
                        continue
                    runs.append(ShadowRun(**data))
                except (json.JSONDecodeError, TypeError):
                    continue
        
        return runs[-limit:]
    
    def adjust_shadow_ratio(self, current_ratio: float, 
                           candidate_performance: float,
                           production_performance: float,
                           min_ratio: float = 0.1,
                           max_ratio: float = 0.3) -> float:
        """
        Shadow 프록시 비율 동적 조정
        
        Args:
            current_ratio: 현재 비율
            candidate_performance: 후보 성능 (p@3 등)
            production_performance: 프로덕션 성능
            min_ratio: 최소 비율
            max_ratio: 최대 비율
            
        Returns:
            조정된 비율
        """
        performance_delta = candidate_performance - production_performance
        
        # 후보가 더 좋으면 비율 증가, 같거나 나쁘면 유지/감소
        if performance_delta > 0.05:
            new_ratio = min(current_ratio * 1.2, max_ratio)
        elif performance_delta > 0.02:
            new_ratio = min(current_ratio * 1.1, max_ratio)
        elif performance_delta < -0.05:
            new_ratio = max(current_ratio * 0.9, min_ratio)
        else:
            new_ratio = current_ratio
        
        return new_ratio


if __name__ == '__main__':
    # 테스트
    runner = ShadowRunner()
    
    run = runner.run_comparison(
        candidate_id='cand-001',
        production_id='prod-main',
        shadow_proxy_ratio=0.1,
        num_requests=100
    )
    
    print(f"Shadow 실행 완료: {run.run_id}")
    print(f"비교 메트릭: {run.comparison}")

