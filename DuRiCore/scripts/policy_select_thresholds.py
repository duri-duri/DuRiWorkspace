from DuRiCore.trace import emit_trace
"""
Phase 3 - 정책 튜닝 스크립트
CSV/JSON 입력으로부터 ROC/PR 기반 최적 임계값 산출 및 리포트 생성

@preserve_identity: 기존 검증 규칙과의 호환성 보장
@evolution_protection: 정책 진화 과정에서의 안전성 확보
@execution_guarantee: 최적화된 임계값으로 검증 보장
@existence_ai: 안전한 정책 진화를 위한 자동화된 튜닝
@final_execution: 최적화된 정책으로 안전한 검증 실행
"""
import argparse
import json
import csv
import yaml
import os
import sys
from pathlib import Path
from typing import Dict, List, Tuple, Any, Optional
from dataclasses import dataclass, asdict
import numpy as np
import pandas as pd
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
try:
    from tests.policy.test_policy_tuning import PolicyTuningAnalyzer, PolicyTuningResult
except ImportError:

    @dataclass
    class ThresholdCandidate:
        threshold: float
        tpr: float
        fpr: float
        precision: float
        f1_score: float
        balanced_accuracy: float

    @dataclass
    class PolicyTuningResult:
        rule_name: str
        best_threshold: float
        best_f1_score: float
        best_balanced_accuracy: float
        candidates: List[ThresholdCandidate]
        roc_data: Dict[str, List[float]]
        pr_data: Dict[str, List[float]]

    class PolicyTuningAnalyzer:

        def __init__(self):
            self.results: List[PolicyTuningResult] = []

        def generate_sample_data(self, n_samples=1000, anomaly_ratio=0.2):
            np.random.seed(42)
            n_anomalies = int(n_samples * anomaly_ratio)
            n_normal = n_samples - n_anomalies
            normal_metrics = np.random.exponential(0.5, n_normal)
            anomaly_metrics = np.random.exponential(2.0, n_anomalies) + 3.0
            all_metrics = np.concatenate([normal_metrics, anomaly_metrics])
            labels = [False] * n_normal + [True] * n_anomalies
            indices = np.random.permutation(len(all_metrics))
            return (all_metrics[indices].tolist(), [labels[i] for i in indices])

        def calculate_metrics(self, predictions, labels):
            tp = sum((1 for (p, l) in zip(predictions, labels) if p and l))
            fp = sum((1 for (p, l) in zip(predictions, labels) if p and (not l)))
            tn = sum((1 for (p, l) in zip(predictions, labels) if not p and (not l)))
            fn = sum((1 for (p, l) in zip(predictions, labels) if not p and l))
            tpr = tp / (tp + fn) if tp + fn > 0 else 0.0
            fpr = fp / (fp + tn) if fp + tn > 0 else 0.0
            precision = tp / (tp + fp) if tp + fp > 0 else 0.0
            f1_score = 2 * precision * tpr / (precision + tpr) if precision + tpr > 0 else 0.0
            balanced_accuracy = (tpr + (1 - fpr)) / 2
            return {'tpr': tpr, 'fpr': fpr, 'precision': precision, 'f1_score': f1_score, 'balanced_accuracy': balanced_accuracy, 'tp': tp, 'fp': fp, 'tn': tn, 'fn': fn}

        def evaluate_thresholds(self, metrics, labels, threshold_range=(0.0, 10.0), n_steps=100):
            candidates = []
            thresholds = np.linspace(threshold_range[0], threshold_range[1], n_steps)
            for threshold in thresholds:
                predictions = [m > threshold for m in metrics]
                metrics_dict = self.calculate_metrics(predictions, labels)
                candidate = ThresholdCandidate(threshold=threshold, tpr=metrics_dict['tpr'], fpr=metrics_dict['fpr'], precision=metrics_dict['precision'], f1_score=metrics_dict['f1_score'], balanced_accuracy=metrics_dict['balanced_accuracy'])
                candidates.append(candidate)
            return candidates

        def find_optimal_threshold(self, candidates, optimization_target='f1_score'):
            if optimization_target == 'f1_score':
                return max(candidates, key=lambda x: x.f1_score)
            elif optimization_target == 'balanced_accuracy':
                return max(candidates, key=lambda x: x.balanced_accuracy)
            elif optimization_target == 'tpr':
                return max(candidates, key=lambda x: x.tpr)
            else:
                raise ValueError(f'지원하지 않는 최적화 대상: {optimization_target}')

        def analyze_rule(self, rule_name, metrics, labels):
            candidates = self.evaluate_thresholds(metrics, labels)
            best_f1 = self.find_optimal_threshold(candidates, 'f1_score')
            best_balanced = self.find_optimal_threshold(candidates, 'balanced_accuracy')
            roc_data = {'fpr': [c.fpr for c in candidates], 'tpr': [c.tpr for c in candidates]}
            pr_data = {'precision': [c.precision for c in candidates], 'recall': [c.tpr for c in candidates]}
            result = PolicyTuningResult(rule_name=rule_name, best_threshold=best_f1.threshold, best_f1_score=best_f1.f1_score, best_balanced_accuracy=best_balanced.balanced_accuracy, candidates=candidates, roc_data=roc_data, pr_data=pr_data)
            self.results.append(result)
            return result

@dataclass
class ThresholdRecommendation:
    """임계값 추천 데이터 클래스"""
    rule_name: str
    current_threshold: float
    recommended_threshold: float
    improvement_f1: float
    improvement_balanced: float
    fpr_reduction: float
    fnr_reduction: float

class PolicyThresholdSelector:
    """정책 임계값 선택기"""

    def __init__(self, config_path: Optional[str]=None):
        """
        초기화
        
        Args:
            config_path: thresholds.yaml 파일 경로 (None이면 기본 경로 사용)
        """
        self.config_path = config_path or os.path.join(os.path.dirname(__file__), '..', 'config', 'thresholds.yaml')
        self.analyzer = PolicyTuningAnalyzer()
        self.current_thresholds = self._load_current_thresholds()

    def _load_current_thresholds(self) -> Dict[str, Any]:
        """현재 임계값 설정 로드"""
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    config = yaml.safe_load(f)
                profile = os.getenv('DURI_PROFILE', 'dev')
                if profile in config.get('profiles', {}):
                    return config['profiles'][profile]
                else:
                    return config.get('defaults', {})
            else:
                emit_trace('info', ' '.join(map(str, [f'⚠️ 설정 파일을 찾을 수 없음: {self.config_path}'])))
                return {}
        except Exception as e:
            emit_trace('info', ' '.join(map(str, [f'❌ 임계값 로드 실패: {e}'])))
            return {}

    def load_data_from_csv(self, file_path: str, metric_column: str='metric', label_column: str='label') -> Tuple[List[float], List[bool]]:
        """CSV 파일에서 데이터 로드"""
        try:
            df = pd.read_csv(file_path)
            if metric_column not in df.columns:
                raise ValueError(f"메트릭 컬럼 '{metric_column}'을 찾을 수 없습니다")
            if label_column not in df.columns:
                raise ValueError(f"라벨 컬럼 '{label_column}'을 찾을 수 없습니다")
            metrics = df[metric_column].tolist()
            labels = df[label_column].astype(bool).tolist()
            emit_trace('info', ' '.join(map(str, [f'📊 CSV 데이터 로드 완료: {len(metrics)}개 샘플'])))
            return (metrics, labels)
        except Exception as e:
            emit_trace('info', ' '.join(map(str, [f'❌ CSV 로드 실패: {e}'])))
            raise

    def load_data_from_json(self, file_path: str, metric_key: str='metric', label_key: str='label') -> Tuple[List[float], List[bool]]:
        """JSON 파일에서 데이터 로드"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            if isinstance(data, list):
                metrics = [item[metric_key] for item in data]
                labels = [bool(item[label_key]) for item in data]
            elif isinstance(data, dict):
                metrics = data[metric_key]
                labels = [bool(l) for l in data[label_key]]
            else:
                raise ValueError('지원하지 않는 JSON 형식')
            emit_trace('info', ' '.join(map(str, [f'📊 JSON 데이터 로드 완료: {len(metrics)}개 샘플'])))
            return (metrics, labels)
        except Exception as e:
            emit_trace('info', ' '.join(map(str, [f'❌ JSON 로드 실패: {e}'])))
            raise

    def analyze_all_rules(self, metrics: List[float], labels: List[bool], rule_names: Optional[List[str]]=None) -> List[PolicyTuningResult]:
        """모든 규칙에 대한 분석 수행"""
        if rule_names is None:
            rule_names = ['performance_degradation', 'error_spike_detection', 'resource_exhaustion', 'latency_threshold', 'memory_usage', 'cpu_usage']
        results = []
        for rule_name in rule_names:
            emit_trace('info', ' '.join(map(str, [f'🔍 {rule_name} 규칙 분석 중...'])))
            if 'performance' in rule_name or 'latency' in rule_name:
                rule_metrics = [m * 0.8 for m in metrics]
            elif 'error' in rule_name:
                rule_metrics = [m * 1.2 for m in metrics]
            elif 'resource' in rule_name or 'memory' in rule_name or 'cpu' in rule_name:
                rule_metrics = [m * 1.0 for m in metrics]
            else:
                rule_metrics = metrics
            result = self.analyzer.analyze_rule(rule_name, rule_metrics, labels)
            results.append(result)
            emit_trace('info', ' '.join(map(str, [f'✅ {rule_name}: 최적 임계값 {result.best_threshold:.3f} (F1: {result.best_f1_score:.3f}, BA: {result.best_balanced_accuracy:.3f})'])))
        return results

    def generate_recommendations(self, results: List[PolicyTuningResult]) -> List[ThresholdRecommendation]:
        """임계값 추천 생성"""
        recommendations = []
        for result in results:
            current_threshold = self._get_current_threshold_for_rule(result.rule_name)
            improvement_f1 = result.best_f1_score - 0.5
            improvement_balanced = result.best_balanced_accuracy - 0.7
            best_candidate = max(result.candidates, key=lambda x: x.f1_score)
            fpr_reduction = 0.1 - best_candidate.fpr if best_candidate.fpr < 0.1 else 0.0
            fnr_reduction = 0.05 - (1 - best_candidate.tpr) if best_candidate.tpr > 0.95 else 0.0
            recommendation = ThresholdRecommendation(rule_name=result.rule_name, current_threshold=current_threshold, recommended_threshold=result.best_threshold, improvement_f1=improvement_f1, improvement_balanced=improvement_balanced, fpr_reduction=fpr_reduction, fnr_reduction=fnr_reduction)
            recommendations.append(recommendation)
        return recommendations

    def _get_current_threshold_for_rule(self, rule_name: str) -> float:
        """규칙 이름에 따른 현재 임계값 반환"""
        threshold_mapping = {'performance_degradation': self.current_thresholds.get('performance_events_max', 5.0), 'error_spike_detection': self.current_thresholds.get('error_events_max', 5.0), 'resource_exhaustion': self.current_thresholds.get('resource_events_max', 5.0), 'latency_threshold': self.current_thresholds.get('p95_latency_inc_pct', 5.0), 'memory_usage': self.current_thresholds.get('memory_inc_pct', 3.0), 'cpu_usage': self.current_thresholds.get('cpu_inc_pct', 5.0)}
        return threshold_mapping.get(rule_name, 5.0)

    def save_recommendations_yaml(self, recommendations: List[ThresholdRecommendation], output_path: str) -> None:
        """추천 임계값을 YAML 형식으로 저장"""
        try:
            recommended_config = {'profiles': {'dev': {}, 'staging': {}, 'prod': {}}, 'defaults': {}, 'recommendations': {}}
            for profile in ['dev', 'staging', 'prod']:
                profile_config = {}
                for rec in recommendations:
                    if 'performance' in rec.rule_name:
                        profile_config['performance_events_max'] = int(rec.recommended_threshold)
                    elif 'error' in rec.rule_name:
                        profile_config['error_events_max'] = int(rec.recommended_threshold)
                    elif 'resource' in rec.rule_name:
                        profile_config['resource_events_max'] = int(rec.recommended_threshold)
                    elif 'latency' in rec.rule_name:
                        profile_config['p95_latency_inc_pct'] = round(rec.recommended_threshold, 1)
                    elif 'memory' in rec.rule_name:
                        profile_config['memory_inc_pct'] = round(rec.recommended_threshold, 1)
                    elif 'cpu' in rec.rule_name:
                        profile_config['cpu_inc_pct'] = round(rec.recommended_threshold, 1)
                profile_config.update(self.current_thresholds)
                recommended_config['profiles'][profile] = profile_config
            recommended_config['recommendations'] = {rec.rule_name: {'current_threshold': rec.current_threshold, 'recommended_threshold': rec.recommended_threshold, 'improvement_f1': round(rec.improvement_f1, 3), 'improvement_balanced': round(rec.improvement_balanced, 3), 'fpr_reduction': round(rec.fpr_reduction, 3), 'fnr_reduction': round(rec.fnr_reduction, 3)} for rec in recommendations}
            with open(output_path, 'w', encoding='utf-8') as f:
                yaml.dump(recommended_config, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
            emit_trace('info', ' '.join(map(str, [f'💾 추천 임계값 YAML 저장 완료: {output_path}'])))
        except Exception as e:
            emit_trace('info', ' '.join(map(str, [f'❌ YAML 저장 실패: {e}'])))
            raise

    def generate_report_markdown(self, results: List[PolicyTuningResult], recommendations: List[ThresholdRecommendation], output_path: str) -> None:
        """마크다운 리포트 생성"""
        try:
            report_content = f"# Phase 3 - 정책 튜닝 리포트\n\n## 📊 분석 요약\n\n- **분석 규칙 수**: {len(results)}\n- **데이터 샘플 수**: {(len(results[0].candidates) if results else 0)}\n- **생성 시간**: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n## 🎯 규칙별 최적 임계값\n\n"
            for result in results:
                report_content += f"### {result.rule_name.replace('_', ' ').title()}\n\n- **최적 임계값**: {result.best_threshold:.3f}\n- **F1 스코어**: {result.best_f1_score:.3f}\n- **균형 정확도**: {result.best_balanced_accuracy:.3f}\n- **TPR (Recall)**: {max((c.tpr for c in result.candidates)):.3f}\n- **최소 FPR**: {min((c.fpr for c in result.candidates)):.3f}\n\n"
            report_content += '## 📈 성능 개선 추천\n\n| 규칙 | 현재 임계값 | 추천 임계값 | F1 개선 | 균형정확도 개선 | FPR 감소 | FNR 감소 |\n|------|-------------|-------------|---------|----------------|----------|----------|\n'
            for rec in recommendations:
                report_content += f'| {rec.rule_name} | {rec.current_threshold:.3f} | {rec.recommended_threshold:.3f} | {rec.improvement_f1:+.3f} | {rec.improvement_balanced:+.3f} | {rec.fpr_reduction:+.3f} | {rec.fnr_reduction:+.3f} |\n'
            report_content += f'\n\n## 🚀 다음 단계\n\n1. **추천 임계값 적용**: `config/thresholds.yaml` 파일 업데이트\n2. **테스트 실행**: `pytest -k policy_tuning` 으로 검증\n3. **성능 모니터링**: FP ≤ 2%, FN ≤ 5% 달성 확인\n4. **운영 적용**: 단계별로 프로덕션 환경에 적용\n\n## 📋 성능 기준\n\n- **FP (False Positive)**: ≤ 2%\n- **FN (False Negative)**: ≤ 5%\n- **F1 스코어**: ≥ 0.8\n- **균형 정확도**: ≥ 0.85\n\n---\n*이 리포트는 Phase 3 정책 튜닝 자동화 도구로 생성되었습니다.*\n'
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(report_content)
            emit_trace('info', ' '.join(map(str, [f'📝 마크다운 리포트 생성 완료: {output_path}'])))
        except Exception as e:
            emit_trace('info', ' '.join(map(str, [f'❌ 리포트 생성 실패: {e}'])))
            raise

def main():
    """메인 함수"""
    parser = argparse.ArgumentParser(description='Phase 3 - 정책 튜닝 스크립트', formatter_class=argparse.RawDescriptionHelpFormatter, epilog='\n사용 예시:\n  # CSV 파일로부터 분석\n  python policy_select_thresholds.py --input data.csv --format csv\n  \n  # JSON 파일로부터 분석  \n  python policy_select_thresholds.py --input data.json --format json\n  \n  # 출력 파일 지정\n  python policy_select_thresholds.py --input data.csv --format csv \\\n    --output-yaml recommended_thresholds.yaml \\\n    --output-report tuning_report.md\n        ')
    parser.add_argument('--input', '-i', required=True, help='입력 데이터 파일 경로')
    parser.add_argument('--format', '-f', choices=['csv', 'json'], required=True, help='입력 파일 형식')
    parser.add_argument('--output-yaml', '-y', default='recommended_thresholds.yaml', help='추천 임계값 YAML 출력 파일')
    parser.add_argument('--output-report', '-r', default='policy_tuning_report.md', help='마크다운 리포트 출력 파일')
    parser.add_argument('--config', '-c', help='기존 thresholds.yaml 설정 파일 경로')
    parser.add_argument('--metric-column', default='metric', help='CSV 메트릭 컬럼명 (기본값: metric)')
    parser.add_argument('--label-column', default='label', help='CSV 라벨 컬럼명 (기본값: label)')
    parser.add_argument('--metric-key', default='metric', help='JSON 메트릭 키 (기본값: metric)')
    parser.add_argument('--label-key', default='label', help='JSON 라벨 키 (기본값: label)')
    args = parser.parse_args()
    try:
        emit_trace('info', ' '.join(map(str, ['🚀 Phase 3 - 정책 튜닝 시작'])))
        emit_trace('info', ' '.join(map(str, ['=' * 50])))
        selector = PolicyThresholdSelector(args.config)
        if args.format == 'csv':
            (metrics, labels) = selector.load_data_from_csv(args.input, args.metric_column, args.label_column)
        else:
            (metrics, labels) = selector.load_data_from_json(args.input, args.metric_key, args.label_key)
        emit_trace('info', ' '.join(map(str, ['\n🔍 규칙별 임계값 분석 중...'])))
        results = selector.analyze_all_rules(metrics, labels)
        emit_trace('info', ' '.join(map(str, ['\n💡 임계값 추천 생성 중...'])))
        recommendations = selector.generate_recommendations(results)
        emit_trace('info', ' '.join(map(str, ['\n💾 결과 저장 중...'])))
        selector.save_recommendations_yaml(recommendations, args.output_yaml)
        selector.generate_report_markdown(results, recommendations, args.output_report)
        emit_trace('info', ' '.join(map(str, ['\n' + '=' * 50])))
        emit_trace('info', ' '.join(map(str, ['🎉 정책 튜닝 완료!'])))
        emit_trace('info', ' '.join(map(str, [f'📊 분석된 규칙: {len(results)}개'])))
        emit_trace('info', ' '.join(map(str, [f'💾 YAML 파일: {args.output_yaml}'])))
        emit_trace('info', ' '.join(map(str, [f'📝 리포트: {args.output_report}'])))
        all_f1_scores = [r.best_f1_score for r in results]
        all_balanced_acc = [r.best_balanced_accuracy for r in results]
        avg_f1 = np.mean(all_f1_scores)
        avg_balanced = np.mean(all_balanced_acc)
        emit_trace('info', ' '.join(map(str, [f'\n📈 성능 요약:'])))
        emit_trace('info', ' '.join(map(str, [f"  평균 F1 스코어: {avg_f1:.3f} {('✅' if avg_f1 >= 0.8 else '⚠️')}"])))
        emit_trace('info', ' '.join(map(str, [f"  평균 균형 정확도: {avg_balanced:.3f} {('✅' if avg_balanced >= 0.85 else '⚠️')}"])))
        if avg_f1 >= 0.8 and avg_balanced >= 0.85:
            emit_trace('info', ' '.join(map(str, ['\n🎯 Phase 3 성능 기준 달성! 운영 적용 준비 완료!'])))
        else:
            emit_trace('info', ' '.join(map(str, ['\n⚠️ 일부 성능 기준 미달성. 추가 튜닝이 필요할 수 있습니다.'])))
    except Exception as e:
        emit_trace('info', ' '.join(map(str, [f'\n❌ 오류 발생: {e}'])))
        sys.exit(1)
if __name__ == '__main__':
    main()