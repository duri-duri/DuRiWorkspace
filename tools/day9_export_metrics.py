#!/usr/bin/env python3
"""
Day 9: 메트릭 Export 함수
기존 Day 8 Prometheus Export에 Day 9 알림 지연 메트릭을 추가합니다.
"""

import json
import pathlib
import logging
from typing import Dict, Any, Optional

# 기존 시스템과의 연동을 위한 설정
from DuRiCore.core.config import load_thresholds

logger = logging.getLogger("day9_export")

def load_day9_summary(summary_path: str = "var/metrics/day9_summary.json") -> Dict[str, Any]:
    """
    Day 9 요약 메트릭을 로드합니다.
    
    Args:
        summary_path: Day 9 요약 파일 경로
    
    Returns:
        Dict: Day 9 메트릭 요약
    """
    try:
        path = pathlib.Path(summary_path)
        if not path.exists():
            logger.warning(f"Day 9 요약 파일이 존재하지 않음: {summary_path}")
            return {}
        
        with path.open('r', encoding='utf-8') as f:
            summary = json.load(f)
        
        logger.info(f"Day 9 요약 로드: {len(summary)} 항목")
        return summary
        
    except Exception as e:
        logger.error(f"Day 9 요약 로드 실패: {e}")
        return {}

def append_to_prometheus(metrics: Dict[str, Any], prometheus_path: str = "var/metrics/prometheus.txt"):
    """
    Day 9 메트릭을 기존 Prometheus Export에 추가합니다.
    
    Args:
        metrics: 추가할 Day 9 메트릭
        prometheus_path: Prometheus Export 파일 경로
    """
    try:
        prom_path = pathlib.Path(prometheus_path)
        prom_path.parent.mkdir(parents=True, exist_ok=True)
        
        # 기존 Prometheus 내용 읽기
        existing_content = ""
        if prom_path.exists():
            with prom_path.open('r', encoding='utf-8') as f:
                existing_content = f.read()
        
        # Day 9 메트릭 라인 생성
        day9_lines = []
        
        # 알림 지연 메트릭
        if metrics.get("p50_ms") is not None:
            day9_lines.append(f'alert_latency_p50_ms{{source="day9"}} {metrics["p50_ms"]:.3f}')
        
        if metrics.get("p95_ms") is not None:
            day9_lines.append(f'alert_latency_p95_ms{{source="day9"}} {metrics["p95_ms"]:.3f}')
        
        if metrics.get("max_ms") is not None:
            day9_lines.append(f'alert_latency_max_ms{{source="day9"}} {metrics["max_ms"]:.3f}')
        
        # 타임아웃 비율
        if metrics.get("timeout_rate") is not None:
            day9_lines.append(f'alert_timeout_rate{{source="day9"}} {metrics["timeout_rate"]:.6f}')
        
        # 통계 정보
        if metrics.get("count") is not None:
            day9_lines.append(f'alert_simulation_count{{source="day9"}} {metrics["count"]}')
        
        if metrics.get("ok") is not None:
            day9_lines.append(f'alert_simulation_ok{{source="day9"}} {metrics["ok"]}')
        
        if metrics.get("timeouts") is not None:
            day9_lines.append(f'alert_simulation_timeouts{{source="day9"}} {metrics["timeouts"]}')
        
        # Day 9 메트릭을 기존 내용에 추가
        new_content = existing_content
        if day9_lines:
            if existing_content and not existing_content.endswith('\n'):
                new_content += '\n'
            new_content += '\n'.join(day9_lines) + '\n'
        
        # 파일에 쓰기
        with prom_path.open('w', encoding='utf-8') as f:
            f.write(new_content)
        
        logger.info(f"Day 9 메트릭을 Prometheus Export에 추가: {len(day9_lines)} 항목")
        
        # 추가된 메트릭 출력
        print("[OK] Prometheus에 Day 9 메트릭 추가 완료:")
        for line in day9_lines:
            print(f"  {line}")
            
    except Exception as e:
        logger.error(f"Prometheus Export 업데이트 실패: {e}")
        raise

def export_day9_metrics(summary_path: str = "var/metrics/day9_summary.json", 
                       prometheus_path: str = "var/metrics/prometheus.txt"):
    """
    Day 9 메트릭을 기존 Prometheus Export에 통합합니다.
    
    Args:
        summary_path: Day 9 요약 파일 경로
        prometheus_path: Prometheus Export 파일 경로
    """
    try:
        # Day 9 요약 로드
        summary = load_day9_summary(summary_path)
        if not summary:
            logger.warning("Day 9 요약 데이터가 없어 Export를 건너뜁니다")
            return
        
        # Prometheus Export에 추가
        append_to_prometheus(summary, prometheus_path)
        
        logger.info("Day 9 메트릭 Export 완료")
        
    except Exception as e:
        logger.error(f"Day 9 메트릭 Export 실패: {e}")
        raise

def main():
    """메인 실행 함수"""
    try:
        # 기존 Day 9 설정 로드
        config = load_thresholds()
        day9_config = config.get("day9", {})
        
        logger.info("Day 9 설정 로드 완료")
        
        # 메트릭 Export 실행
        export_day9_metrics()
        
    except Exception as e:
        logger.error(f"Day 9 Export 실패: {e}")
        sys.exit(1)

if __name__ == "__main__":
    import sys
    main()
