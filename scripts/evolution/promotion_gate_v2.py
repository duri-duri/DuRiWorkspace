#!/usr/bin/env python3
"""
Promotion Gate v2 - 승격 함수 계산기
목적: 미분적 접근으로 L4.1 승격 의사결정 자동화
Usage: python scripts/evolution/promotion_gate_v2.py --dryrun --window 24h
"""

import json
import argparse
import sys
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, Optional, Tuple
import math

# 승격 함수 상수
WEIGHTS = {
    'NDCG@3': 0.35,
    'p@3': 0.25,
    'halluc_rate': -0.20,  # 음수 (낮을수록 좋음)
    'regression_rate': -0.10,  # 음수
    'p95_latency_z': -0.05,  # 음수 (Z-score, 낮을수록 좋음)
    'cost_eff': 0.05,
    'oracle_recall': 0.10,
}

# L4 Gate 임계값
L4_THRESHOLDS = {
    'NDCG@3': 0.78,
    'p@3': 0.72,
    'halluc_rate': 0.025,  # 2.5%
    'regression_rate': 0.01,  # 1.0%
    'p95_latency_z': 0.0,  # 기준선 이하 또는 +10% 이내
    'self_check_pass_rate': 0.98,
    'error_budget_burn_ok': True,
}

# L4.1 Gate (단순화)
L4_1_THRESHOLDS = {
    'p@3': 0.70,
    'MRR': 0.20,
    'NDCG@3': 0.15,
    'halluc_rate': 0.08,
    'cost_norm': 0.05,
    'stability': 0.90,
    'L4_score': 0.70,
}

# L4.0 프로모션 스코어 임계값 (7일 기준)
L4_0_PROMOTION_THRESHOLD = 0.82


def compute_promotion_score(metrics: Dict[str, float]) -> Tuple[float, Dict[str, float]]:
    """
    프로모션 스코어 계산
    
    Args:
        metrics: 메트릭 딕셔너리
        
    Returns:
        (prom_score, contributions): 프로모션 스코어와 각 항목 기여도
    """
    contributions = {}
    prom_score = 0.0
    
    for key, weight in WEIGHTS.items():
        value = metrics.get(key, 0.0)
        
        # 음수 가중치는 값이 낮을수록 좋음 (역정규화)
        if weight < 0:
            # 예: halluc_rate는 낮을수록 좋으므로 (1 - rate) 형태로 변환
            if key == 'halluc_rate':
                normalized = 1.0 - min(value, 1.0)  # 최대 1.0으로 제한
            elif key == 'regression_rate':
                normalized = 1.0 - min(value, 1.0)
            elif key == 'p95_latency_z':
                # Z-score는 절대값이 작을수록 좋음
                normalized = 1.0 / (1.0 + abs(value))
            else:
                normalized = 1.0 - value
            contribution = abs(weight) * normalized
        else:
            # 양수 가중치는 값이 높을수록 좋음
            contribution = weight * value
        
        contributions[key] = contribution
        prom_score += contribution
    
    return prom_score, contributions


def compute_l4_1_score(metrics: Dict[str, float]) -> Tuple[float, Dict[str, float]]:
    """
    L4.1 스코어 계산 (단순화된 버전)
    
    L4_score = 0.35·p@3 + 0.20·MRR + 0.15·NDCG@3 - 0.20·halluc_rate - 0.05·cost_norm + 0.05·stability
    """
    contributions = {}
    
    p_at_3 = metrics.get('p@3', 0.0)
    mrr = metrics.get('MRR', 0.0)
    ndcg_at_3 = metrics.get('NDCG@3', 0.0)
    halluc_rate = metrics.get('halluc_rate', 0.0)
    cost_norm = metrics.get('cost_norm', 0.0)
    stability = metrics.get('stability', 0.0)
    
    contributions['p@3'] = 0.35 * p_at_3
    contributions['MRR'] = 0.20 * mrr
    contributions['NDCG@3'] = 0.15 * ndcg_at_3
    contributions['halluc_rate'] = -0.20 * halluc_rate
    contributions['cost_norm'] = -0.05 * cost_norm
    contributions['stability'] = 0.05 * stability
    
    l4_score = (
        0.35 * p_at_3 +
        0.20 * mrr +
        0.15 * ndcg_at_3 -
        0.20 * halluc_rate -
        0.05 * cost_norm +
        0.05 * stability
    )
    
    return l4_score, contributions


def check_l4_gate(metrics: Dict[str, float]) -> Tuple[bool, Dict[str, bool], list]:
    """
    L4 Gate 통과 여부 확인
    
    Returns:
        (passed, checks, failures): 통과 여부, 각 체크 결과, 실패 항목 리스트
    """
    checks = {}
    failures = []
    
    # 각 임계값 체크
    for key, threshold in L4_THRESHOLDS.items():
        if key == 'error_budget_burn_ok':
            checks[key] = metrics.get(key, False)
        else:
            value = metrics.get(key, 0.0)
            checks[key] = value >= threshold if isinstance(threshold, (int, float)) else value == threshold
            
            if not checks[key]:
                failures.append(f"{key}: {value} < {threshold}")
    
    # 프로모션 스코어 계산
    prom_score, _ = compute_promotion_score(metrics)
    prom_score_pass = prom_score >= 0.70  # 임의의 임계값
    
    checks['prom_score'] = prom_score_pass
    if not prom_score_pass:
        failures.append(f"prom_score: {prom_score} < 0.70")
    
    passed = all(checks.values()) and len(failures) == 0
    
    return passed, checks, failures


def check_l4_1_gate(metrics: Dict[str, float]) -> Tuple[bool, Dict[str, bool], list]:
    """
    L4.1 Gate 통과 여부 확인
    """
    checks = {}
    failures = []
    
    # L4.1 스코어 계산
    l4_score, _ = compute_l4_1_score(metrics)
    
    # 기본 체크
    checks['L4_score'] = l4_score >= L4_1_THRESHOLDS['L4_score']
    checks['halluc_rate'] = metrics.get('halluc_rate', 1.0) <= L4_1_THRESHOLDS['halluc_rate']
    checks['stability'] = metrics.get('stability', 0.0) >= L4_1_THRESHOLDS['stability']
    
    if not checks['L4_score']:
        failures.append(f"L4_score: {l4_score} < {L4_1_THRESHOLDS['L4_score']}")
    if not checks['halluc_rate']:
        failures.append(f"halluc_rate: {metrics.get('halluc_rate')} > {L4_1_THRESHOLDS['halluc_rate']}")
    if not checks['stability']:
        failures.append(f"stability: {metrics.get('stability')} < {L4_1_THRESHOLDS['stability']}")
    
    passed = all(checks.values())
    
    return passed, checks, failures, l4_score


def load_metrics_from_jsonl(jsonl_path: Path, window_hours: int = 24) -> Dict[str, float]:
    """
    JSONL 파일에서 메트릭 로드 (시간 윈도우 내)
    """
    if not jsonl_path.exists():
        return {}
    
    metrics_list = []
    cutoff_time = datetime.now() - timedelta(hours=window_hours)
    
    with open(jsonl_path, 'r') as f:
        for line in f:
            try:
                data = json.loads(line)
                ts = datetime.fromisoformat(data.get('timestamp', ''))
                if ts >= cutoff_time:
                    metrics_list.append(data.get('metrics', {}))
            except (json.JSONDecodeError, ValueError):
                continue
    
    if not metrics_list:
        return {}
    
    # 평균 계산
    avg_metrics = {}
    for key in set().union(*[m.keys() for m in metrics_list]):
        values = [m.get(key, 0.0) for m in metrics_list if isinstance(m.get(key), (int, float))]
        if values:
            avg_metrics[key] = sum(values) / len(values)
    
    return avg_metrics


def main():
    parser = argparse.ArgumentParser(description='Promotion Gate v2 - 승격 함수 계산기')
    parser.add_argument('--dryrun', action='store_true', help='드라이런 모드 (실제 승격 안 함)')
    parser.add_argument('--window', type=int, default=24, help='시간 윈도우 (시간 단위)')
    parser.add_argument('--metrics-file', type=str, default='var/evolution/metrics.jsonl', help='메트릭 JSONL 파일 경로')
    parser.add_argument('--gate', choices=['L4', 'L4.1'], default='L4.1', help='Gate 버전')
    parser.add_argument('--output', type=str, help='결과 출력 파일 경로')
    parser.add_argument('--print', action='store_true', help='간단한 출력만 (검증용)')
    
    args = parser.parse_args()
    
    metrics_file = Path(args.metrics_file)
    metrics = load_metrics_from_jsonl(metrics_file, args.window)
    
    if not metrics:
        if args.print:
            print("NO_METRICS")
        else:
            print("⚠️  메트릭 데이터 없음 (빈 결과 또는 파일 없음)")
        sys.exit(1)
    
    if not args.print:
        print(f"=== Promotion Gate v2 ({args.gate}) ===")
        print(f"시간 윈도우: {args.window}시간")
        print(f"메트릭 파일: {metrics_file}")
        print(f"드라이런 모드: {args.dryrun}")
        print("")
    
    # 메트릭 출력
    print("로드된 메트릭:")
    for key, value in sorted(metrics.items()):
        print(f"  {key}: {value:.4f}")
    print("")
    
    # Gate 체크
    if args.gate == 'L4':
        passed, checks, failures = check_l4_gate(metrics)
        prom_score, contributions = compute_promotion_score(metrics)
        
        print("=== L4 Gate 체크 ===")
        print(f"프로모션 스코어: {prom_score:.4f}")
        print("")
        print("기여도:")
        for key, contrib in sorted(contributions.items(), key=lambda x: abs(x[1]), reverse=True):
            print(f"  {key}: {contrib:.4f} (가중치: {WEIGHTS.get(key, 0):.2f})")
        print("")
    else:  # L4.1
        passed, checks, failures, l4_score = check_l4_1_gate(metrics)
        _, contributions = compute_l4_1_score(metrics)
        
        print("=== L4.1 Gate 체크 ===")
        print(f"L4.1 스코어: {l4_score:.4f}")
        print("")
        print("기여도:")
        for key, contrib in sorted(contributions.items(), key=lambda x: abs(x[1]), reverse=True):
            print(f"  {key}: {contrib:.4f}")
        print("")
    
    print("Gate 체크 결과:")
    for key, result in checks.items():
        status = "✅" if result else "❌"
        print(f"  {status} {key}: {result}")
    print("")
    
    if failures:
        print("실패 항목:")
        for failure in failures:
            print(f"  - {failure}")
        print("")
    
    # 최종 결정
    score = prom_score if args.gate == 'L4' else l4_score
    
    # L4.0 프로모션 스코어 임계값 확인
    if args.gate == 'L4.1' and args.window >= 168:  # 7일 이상
        promotion_threshold = L4_0_PROMOTION_THRESHOLD
        if score >= promotion_threshold and passed:
            decision = "PROMOTE"
            print(f"✅ {decision}: Gate 통과 (스코어 {score:.4f} ≥ {promotion_threshold})")
        else:
            decision = "ROLLBACK" if not args.dryrun else "NO-GO"
            print(f"❌ {decision}: Gate 미통과 (스코어 {score:.4f} < {promotion_threshold} 또는 통과={passed})")
    elif passed:
        decision = "PROMOTE"
        print(f"✅ {decision}: Gate 통과")
    else:
        decision = "ROLLBACK" if not args.dryrun else "NO-GO"
        print(f"❌ {decision}: Gate 미통과")
    
    # 결과 저장
    result = {
        'timestamp': datetime.now().isoformat(),
        'gate_version': args.gate,
        'window_hours': args.window,
        'metrics': metrics,
        'score': prom_score if args.gate == 'L4' else l4_score,
        'contributions': contributions,
        'checks': checks,
        'failures': failures,
        'decision': decision,
        'passed': passed,
        'dryrun': args.dryrun,
    }
    
    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w') as f:
            json.dump(result, f, indent=2)
        print(f"\n결과 저장: {output_path}")
    
    # Prometheus 메트릭 export (간단한 형태)
    prom_metrics_file = Path('var/evolution/prom_metrics.prom')
    prom_metrics_file.parent.mkdir(parents=True, exist_ok=True)
    with open(prom_metrics_file, 'w') as f:
        score = prom_score if args.gate == 'L4' else l4_score
        f.write(f"# TYPE duri_promotion_score gauge\n")
        f.write(f"duri_promotion_score{{gate=\"{args.gate}\"}} {score}\n")
        f.write(f"# TYPE duri_promotion_gate_pass gauge\n")
        f.write(f"duri_promotion_gate_pass{{gate=\"{args.gate}\"}} {1 if passed else 0}\n")
        for key, value in metrics.items():
            f.write(f"# TYPE duri_promotion_metric_{key.lower().replace('@', '_at_').replace('-', '_')} gauge\n")
            f.write(f"duri_promotion_metric_{key.lower().replace('@', '_at_').replace('-', '_')} {value}\n")
    
    print(f"Prometheus 메트릭 저장: {prom_metrics_file}")
    
    sys.exit(0 if passed else 1)


if __name__ == '__main__':
    main()

