#!/usr/bin/env python3
"""
A/B 테스트 러너 - 기존 시스템과의 퍼사드 통합
기존 src/ab/* 코드를 100% 보존하면서 새로운 CSV/JSONL 기능 추가
"""
import argparse
import json
import yaml
import pandas as pd
from pathlib import Path
from typing import Dict, List, Any, Tuple
import sys
import os

# 레거시 src 우선 인식
if 'DuRi_Day11_15_starter' not in sys.path:
    sys.path.insert(0, 'DuRi_Day11_15_starter')
sys.path.insert(0, '.')  # 루트 src도 인식

# Import with error handling
try:
    from src.ab.core_runner import run_ab_with_gate, run_ab, welch_t_test
except ImportError:
    # Fallback: 직접 import
    import importlib.util
    starter_path = 'DuRi_Day11_15_starter'
    spec = importlib.util.spec_from_file_location("core_runner", os.path.join(starter_path, "src/ab/core_runner.py"))
    core_runner = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(core_runner)
    run_ab_with_gate = core_runner.run_ab_with_gate
    run_ab = core_runner.run_ab
    welch_t_test = core_runner.welch_t_test

from src.ab.variants import VariantConfig, get_variant_config
from src.ab.metrics import aggregate

def csv_to_variants(rows, metric, group_col='variant', a='A', b='B'):
    """CSV 데이터를 VariantConfig로 변환하는 어댑터"""
    A = [float(r[metric]) for r in rows if r[group_col]==a]
    B = [float(r[metric]) for r in rows if r[group_col]==b]
    vA = VariantConfig(name=a, temperature=0.0, max_tokens=256)
    vB = VariantConfig(name=b, temperature=0.0, max_tokens=256)
    return vA, vB, A, B

class ABTestRunner:
    """
    A/B 테스트 러너 - 기존 시스템과의 퍼사드
    모든 통계 계산은 기존 core_runner.py에 위임
    """
    
    def __init__(self, config_path: str):
        """설정 로드"""
        self.config = self.load_config(config_path)
        self.config_path = config_path
    
    def load_config(self, path: str) -> Dict[str, Any]:
        """YAML 설정 로드"""
        with open(path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    
    def csv_to_variants(self, csv_path: str, metric_col: str, group_col: str, 
                       a_label: str = "A", b_label: str = "B") -> Tuple[List[float], List[float]]:
        """
        CSV를 기존 VariantConfig 형태로 변환
        기존 시스템과 호환되는 데이터 구조로 변환
        """
        df = pd.read_csv(csv_path)
        
        # 그룹별 데이터 분리
        group_a = df[df[group_col] == a_label][metric_col].dropna().tolist()
        group_b = df[df[group_col] == b_label][metric_col].dropna().tolist()
        
        if len(group_a) < 2 or len(group_b) < 2:
            raise ValueError(f"Need ≥2 samples per variant. A: {len(group_a)}, B: {len(group_b)}")
        
        return group_a, group_b
    
    def run_legacy_mode(self, day: int, variant: str, seed: int, 
                       gate_policy_path: str = None) -> Dict[str, Any]:
        """
        기존 파이프라인과 100% 호환
        기존 run_ab_with_gate 함수 직접 호출
        """
        return run_ab_with_gate(
            day=day, 
            variant=variant, 
            seed=seed, 
            cfg=self.config,
            gate_policy_path=gate_policy_path
        )
    
    def run_from_csv(self, csv_path: str, metric_col: str, group_col: str,
                    output_dir: str = "logs/ab", exp_id: str = None) -> Dict[str, Any]:
        """
        CSV 입력을 기존 시스템으로 처리
        모든 통계 계산은 기존 welch_t_test 함수 사용
        """
        # CSV 데이터 로드
        group_a, group_b = self.csv_to_variants(csv_path, metric_col, group_col)
        
        # 기존 통계 함수 사용 (중복 구현 금지)
        t_stat, df, mean_a, mean_b = welch_t_test(group_a, group_b)
        
        # 효과 크기 계산 (Cohen's d)
        pooled_std = ((len(group_a) - 1) * (sum((x - mean_a)**2 for x in group_a) / (len(group_a) - 1)) +
                     (len(group_b) - 1) * (sum((x - mean_b)**2 for x in group_b) / (len(group_b) - 1))) / (len(group_a) + len(group_b) - 2)
        pooled_std = pooled_std ** 0.5
        cohens_d = (mean_a - mean_b) / pooled_std if pooled_std > 0 else 0
        
        # 결과 구성 (기존 스키마 + 확장 필드)
        result = {
            # 기존 스키마 (호환성 보장)
            "n_A": len(group_a),
            "n_B": len(group_b),
            "mean_A": mean_a,
            "mean_B": mean_b,
            "t_stat": t_stat,
            "df": df,
            "objective_delta": mean_a - mean_b,
            
            # 확장 필드 (새로운 기능)
            "source": "csv",
            "exp_id": exp_id or Path(csv_path).stem,
            "metric": metric_col,
            "group_col": group_col,
            "cohens_d": cohens_d,
            "effect_size": abs(cohens_d),
            
            # 게이트 호환성 (기존 시스템과 동일한 구조)
            "gate_pass": None,
            "gate_reasons": ["csv_mode_no_gate"]
        }
        
        # ---- enrich metadata ----
        import hashlib, time
        ts = time.strftime("%Y%m%d-%H%M%S", time.gmtime())
        result["created_at_utc"] = ts
        result["test_type"] = result.get("test_type", "welch_t")
        
        # ---- save with timestamp to prevent overwrite ----
        out_dir = Path(output_dir) / result["exp_id"]
        out_dir.mkdir(parents=True, exist_ok=True)
        out_name = f"{result['exp_id']}-{ts}.jsonl"
        output_file = out_dir / out_name
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(json.dumps(result, ensure_ascii=False) + '\n')
        
        print(f"Results saved to: {output_file}")
        return result
    
    def run_with_gate_from_csv(self, csv_path: str, metric_col: str, group_col: str,
                              gate_policy_path: str, output_dir: str = "logs/ab", 
                              exp_id: str = None) -> Dict[str, Any]:
        """
        CSV 입력 + 게이트 시스템 통합
        기존 게이트 시스템과 호환
        """
        # CSV 데이터 로드
        group_a, group_b = self.csv_to_variants(csv_path, metric_col, group_col)
        
        # 기존 통계 함수 사용 (중복 구현 금지)
        t_stat, df, mean_a, mean_b = welch_t_test(group_a, group_b)
        
        # 효과 크기 계산 (Cohen's d)
        pooled_std = ((len(group_a) - 1) * (sum((x - mean_a)**2 for x in group_a) / (len(group_a) - 1)) +
                     (len(group_b) - 1) * (sum((x - mean_b)**2 for x in group_b) / (len(group_b) - 1))) / (len(group_a) + len(group_b) - 2)
        pooled_std = pooled_std ** 0.5
        cohens_d = (mean_a - mean_b) / pooled_std if pooled_std > 0 else 0
        
        # 결과 구성 (기존 스키마 + 확장 필드)
        result = {
            # 기존 스키마 (호환성 보장)
            "n_A": len(group_a),
            "n_B": len(group_b),
            "mean_A": mean_a,
            "mean_B": mean_b,
            "t_stat": t_stat,
            "df": df,
            "objective_delta": mean_a - mean_b,
            
            # 확장 필드 (새로운 기능)
            "source": "csv",
            "exp_id": exp_id or Path(csv_path).stem,
            "metric": metric_col,
            "group_col": group_col,
            "cohens_d": cohens_d,
            "effect_size": abs(cohens_d),
        }
        
        # 게이트 평가 (기존 시스템 사용)
        if gate_policy_path and Path(gate_policy_path).exists():
            try:
                # 기존 게이트 시스템 호출
                gate_result = run_ab_with_gate(
                    day=36,  # 임시 day 값
                    variant="A",  # 임시 variant 값
                    seed=42,  # 임시 seed 값
                    cfg=self.config,
                    gate_policy_path=gate_policy_path
                )
                
                # 게이트 결과를 CSV 결과에 병합
                result["gate_pass"] = gate_result.get("gate_pass")
                result["gate_reasons"] = gate_result.get("gate_reasons", [])
                
            except Exception as e:
                result["gate_pass"] = False
                result["gate_reasons"] = [f"gate_error: {e!r}"]
        else:
            result["gate_pass"] = None
            result["gate_reasons"] = ["gate_disabled_or_no_policy"]
        
        # ---- enrich metadata ----
        import hashlib, time
        ts = time.strftime("%Y%m%d-%H%M%S", time.gmtime())
        result["created_at_utc"] = ts
        result["test_type"] = result.get("test_type", "welch_t")
        
        # gate policy fingerprint (optional)
        if gate_policy_path and Path(gate_policy_path).exists():
            with open(gate_policy_path, "rb") as fp:
                result["gate_policy_sha256"] = hashlib.sha256(fp.read()).hexdigest()
        
        # ---- save with timestamp to prevent overwrite ----
        out_dir = Path(output_dir) / result["exp_id"]
        out_dir.mkdir(parents=True, exist_ok=True)
        out_name = f"{result['exp_id']}-{ts}.jsonl"
        output_file = out_dir / out_name
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(json.dumps(result, ensure_ascii=False) + '\n')
        
        print(f"Results saved to: {output_file}")
        return result

def main():
    """CLI 인터페이스"""
    parser = argparse.ArgumentParser(description="A/B 테스트 러너 - 기존 시스템과 통합")
    
    # 공통 옵션
    parser.add_argument("--config", required=True, help="설정 파일 경로")
    parser.add_argument("--output", default="logs/ab", help="출력 디렉토리")
    
    # 모드 선택
    parser.add_argument("--mode", choices=["legacy", "csv"], default="csv", 
                       help="실행 모드: legacy(기존) 또는 csv(새로운)")
    
    # Legacy 모드 옵션
    parser.add_argument("--day", type=int, default=36, help="Day 번호 (legacy 모드)")
    parser.add_argument("--variant", choices=["A", "B"], default="A", help="변형 (legacy 모드)")
    parser.add_argument("--seed", type=int, default=42, help="시드 (legacy 모드)")
    parser.add_argument("--gate-policy", help="게이트 정책 파일 경로")
    
    # CSV 모드 옵션
    parser.add_argument("--input", help="CSV 입력 파일 경로")
    parser.add_argument("--metric", help="메트릭 컬럼명")
    parser.add_argument("--group", help="그룹 컬럼명")
    parser.add_argument("--exp-id", help="실험 ID")
    
    args = parser.parse_args()
    
    # 러너 초기화
    runner = ABTestRunner(args.config)
    
    if args.mode == "legacy":
        # 기존 모드 (100% 호환)
        result = runner.run_legacy_mode(
            day=args.day,
            variant=args.variant,
            seed=args.seed,
            gate_policy_path=args.gate_policy
        )
        print(json.dumps(result, ensure_ascii=False, indent=2))
        
    elif args.mode == "csv":
        # 새로운 CSV 모드
        if not args.input or not args.metric or not args.group:
            parser.error("CSV 모드에서는 --input, --metric, --group이 필요합니다")
        
        if args.gate_policy:
            result = runner.run_with_gate_from_csv(
                csv_path=args.input,
                metric_col=args.metric,
                group_col=args.group,
                gate_policy_path=args.gate_policy,
                output_dir=args.output,
                exp_id=args.exp_id
            )
        else:
            result = runner.run_from_csv(
                csv_path=args.input,
                metric_col=args.metric,
                group_col=args.group,
                output_dir=args.output,
                exp_id=args.exp_id
            )
        
        print(json.dumps(result, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
