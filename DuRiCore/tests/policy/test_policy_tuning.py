from DuRiCore.trace import emit_trace
"""
정책 튜닝 테스트 - ROC/PR 곡선 기반 임계값 최적화
Phase 3: 운영 수준의 정밀도 확보

@precision_tuning: ROC/PR 곡선 기반 임계값 최적화
@performance_validation: 성능 지표 검증
@threshold_selection: 최적 임계값 선택
"""
import asyncio
import json
import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Any
import logging

def pytest_mark_asyncio(func):
    """pytest.mark.asyncio 대체용 데코레이터"""
    return func

def pytest_fixture(autouse=False):
    """pytest.fixture 대체용 데코레이터"""

    def decorator(func):
        return func
    return decorator
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class PolicyTuningTest:
    """정책 튜닝 테스트 클래스"""

    def __init__(self):
        """테스트 인스턴스 초기화"""
        self.sample_data = None
        self.thresholds = None
        self.results = {}

    def generate_sample_data(self, n_samples: int=1000) -> pd.DataFrame:
        """테스트용 샘플 데이터 생성"""
        np.random.seed(42)
        n_normal = int(n_samples * 0.7)
        normal_data = {'latency_ms': np.random.normal(100, 20, n_normal), 'error_rate': np.random.normal(0.5, 0.2, n_normal), 'memory_mb': np.random.normal(512, 100, n_normal), 'cpu_pct': np.random.normal(30, 10, n_normal), 'label': ['normal'] * n_normal}
        n_anomaly = n_samples - n_normal
        anomaly_data = {'latency_ms': np.random.normal(300, 100, n_anomaly), 'error_rate': np.random.normal(5.0, 2.0, n_anomaly), 'memory_mb': np.random.normal(1024, 200, n_anomaly), 'cpu_pct': np.random.normal(80, 15, n_anomaly), 'label': ['anomaly'] * n_anomaly}
        all_data = {}
        for key in normal_data:
            all_data[key] = list(normal_data[key]) + list(anomaly_data[key])
        df = pd.DataFrame(all_data)
        df['label_binary'] = (df['label'] == 'anomaly').astype(int)
        return df

    def calculate_metrics(self, y_true: List[int], y_pred: List[int]) -> Dict[str, float]:
        """성능 지표 계산"""
        tp = sum((1 for (t, p) in zip(y_true, y_pred) if t == 1 and p == 1))
        tn = sum((1 for (t, p) in zip(y_true, y_pred) if t == 0 and p == 0))
        fp = sum((1 for (t, p) in zip(y_true, y_pred) if t == 0 and p == 1))
        fn = sum((1 for (t, p) in zip(y_true, y_pred) if t == 1 and p == 0))
        total = len(y_true)
        metrics = {'tp': tp, 'tn': tn, 'fp': fp, 'fn': fn, 'total': total, 'accuracy': (tp + tn) / total if total > 0 else 0, 'precision': tp / (tp + fp) if tp + fp > 0 else 0, 'recall': tp / (tp + fn) if tp + fn > 0 else 0, 'f1_score': 2 * tp / (2 * tp + fp + fn) if 2 * tp + fp + fn > 0 else 0, 'fp_rate': fp / (fp + tn) if fp + tn > 0 else 0, 'fn_rate': fn / (fn + tp) if fn + tp > 0 else 0}
        return metrics

    def evaluate_thresholds(self, data: pd.DataFrame, metric: str, thresholds: List[float]) -> List[Dict[str, Any]]:
        """임계값별 성능 평가"""
        results = []
        for threshold in thresholds:
            if metric == 'latency_ms':
                y_pred = (data[metric] > threshold).astype(int)
            elif metric == 'error_rate':
                y_pred = (data[metric] > threshold).astype(int)
            elif metric == 'memory_mb':
                y_pred = (data[metric] > threshold).astype(int)
            elif metric == 'cpu_pct':
                y_pred = (data[metric] > threshold).astype(int)
            else:
                continue
            metrics = self.calculate_metrics(data['label_binary'].tolist(), y_pred.tolist())
            results.append({'threshold': threshold, 'metric': metric, **metrics})
        return results

    def find_optimal_thresholds(self, data: pd.DataFrame) -> Dict[str, Dict[str, Any]]:
        """최적 임계값 찾기 (FP ≤ 2%, FN ≤ 5% 기준)"""
        optimal_thresholds = {}
        metrics_to_test = ['latency_ms', 'error_rate', 'memory_mb', 'cpu_pct']
        for metric in metrics_to_test:
            min_val = data[metric].min()
            max_val = data[metric].max()
            thresholds = np.linspace(min_val, max_val, 100)
            results = self.evaluate_thresholds(data, metric, thresholds)
            valid_thresholds = [r for r in results if r['fp_rate'] <= 0.02 and r['fn_rate'] <= 0.05]
            if valid_thresholds:
                best = max(valid_thresholds, key=lambda x: x['f1_score'])
                optimal_thresholds[metric] = best
            else:
                closest = min(results, key=lambda x: abs(x['fp_rate'] - 0.02) + abs(x['fn_rate'] - 0.05))
                optimal_thresholds[metric] = closest
        return optimal_thresholds

    def generate_roc_data(self, data: pd.DataFrame, metric: str) -> Tuple[List[float], List[float]]:
        """ROC 곡선 데이터 생성"""
        thresholds = np.linspace(data[metric].min(), data[metric].max(), 100)
        tpr_list = []
        fpr_list = []
        for threshold in thresholds:
            y_pred = (data[metric] > threshold).astype(int)
            metrics = self.calculate_metrics(data['label_binary'].tolist(), y_pred.tolist())
            tpr_list.append(metrics['recall'])
            fpr_list.append(metrics['fp_rate'])
        return (fpr_list, tpr_list)

    def generate_pr_data(self, data: pd.DataFrame, metric: str) -> Tuple[List[float], List[float]]:
        """PR 곡선 데이터 생성"""
        thresholds = np.linspace(data[metric].min(), data[metric].max(), 100)
        precision_list = []
        recall_list = []
        for threshold in thresholds:
            y_pred = (data[metric] > threshold).astype(int)
            metrics = self.calculate_metrics(data['label_binary'].tolist(), y_pred.tolist())
            precision_list.append(metrics['precision'])
            recall_list.append(metrics['recall'])
        return (recall_list, precision_list)

class TestPolicyTuning:
    """정책 튜닝 테스트 클래스"""

    def __init__(self):
        """테스트 인스턴스 초기화"""
        self.tuner = PolicyTuningTest()
        self.sample_data = None

    @pytest_mark_asyncio
    async def test_sample_data_generation(self):
        """샘플 데이터 생성 테스트"""
        data = self.tuner.generate_sample_data(1000)
        assert len(data) == 1000
        assert 'label' in data.columns
        assert 'label_binary' in data.columns
        assert 'latency_ms' in data.columns
        assert 'error_rate' in data.columns
        assert 'memory_mb' in data.columns
        assert 'cpu_pct' in data.columns
        normal_count = (data['label'] == 'normal').sum()
        anomaly_count = (data['label'] == 'anomaly').sum()
        assert normal_count > 0
        assert anomaly_count > 0
        assert normal_count + anomaly_count == 1000
        assert data['label_binary'].isin([0, 1]).all()
        self.sample_data = data
        emit_trace('info', ' '.join(map(str, [f'✅ 샘플 데이터 생성 완료: {len(data)}개, 정상: {normal_count}, 이상: {anomaly_count}'])))

    @pytest_mark_asyncio
    async def test_metrics_calculation(self):
        """성능 지표 계산 테스트"""
        if self.sample_data is None:
            self.sample_data = self.tuner.generate_sample_data(100)
        y_true = self.sample_data['label_binary'].tolist()
        y_pred = [1 if x > 0.5 else 0 for x in np.random.random(len(y_true))]
        metrics = self.tuner.calculate_metrics(y_true, y_pred)
        assert 'accuracy' in metrics
        assert 'precision' in metrics
        assert 'recall' in metrics
        assert 'f1_score' in metrics
        assert 'fp_rate' in metrics
        assert 'fn_rate' in metrics
        assert 0 <= metrics['accuracy'] <= 1
        assert 0 <= metrics['precision'] <= 1
        assert 0 <= metrics['recall'] <= 1
        assert 0 <= metrics['f1_score'] <= 1
        assert 0 <= metrics['fp_rate'] <= 1
        assert 0 <= metrics['fn_rate'] <= 1
        emit_trace('info', ' '.join(map(str, [f"✅ 성능 지표 계산 완료: accuracy={metrics['accuracy']:.3f}, f1={metrics['f1_score']:.3f}"])))

    @pytest_mark_asyncio
    async def test_threshold_evaluation(self):
        """임계값 평가 테스트"""
        if self.sample_data is None:
            self.sample_data = self.tuner.generate_sample_data(100)
        thresholds = [50, 100, 150, 200, 250]
        results = self.tuner.evaluate_thresholds(self.sample_data, 'latency_ms', thresholds)
        assert len(results) == len(thresholds)
        for result in results:
            assert 'threshold' in result
            assert 'metric' in result
            assert 'accuracy' in result
            assert 'precision' in result
            assert 'recall' in result
            assert 'f1_score' in result
            assert 'fp_rate' in result
            assert 'fn_rate' in result
        emit_trace('info', ' '.join(map(str, [f'✅ 임계값 평가 완료: {len(results)}개 임계값 테스트'])))

    @pytest_mark_asyncio
    async def test_optimal_threshold_finding(self):
        """최적 임계값 찾기 테스트"""
        if self.sample_data is None:
            self.sample_data = self.tuner.generate_sample_data(1000)
        optimal_thresholds = self.tuner.find_optimal_thresholds(self.sample_data)
        assert len(optimal_thresholds) > 0
        for (metric, result) in optimal_thresholds.items():
            assert 'threshold' in result
            assert 'f1_score' in result
            assert 'fp_rate' in result
            assert 'fn_rate' in result
            emit_trace('info', ' '.join(map(str, [f"📊 {metric}: 임계값={result['threshold']:.2f}, F1={result['f1_score']:.3f}, FP={result['fp_rate']:.3f}, FN={result['fn_rate']:.3f}"])))
        emit_trace('info', ' '.join(map(str, [f'✅ 최적 임계값 찾기 완료: {len(optimal_thresholds)}개 메트릭'])))

    @pytest_mark_asyncio
    async def test_roc_curve_generation(self):
        """ROC 곡선 데이터 생성 테스트"""
        if self.sample_data is None:
            self.sample_data = self.tuner.generate_sample_data(100)
        (fpr, tpr) = self.tuner.generate_roc_data(self.sample_data, 'latency_ms')
        assert len(fpr) == len(tpr)
        assert len(fpr) > 0
        assert all((0 <= x <= 1 for x in fpr))
        assert all((0 <= x <= 1 for x in tpr))
        emit_trace('info', ' '.join(map(str, [f'✅ ROC 곡선 데이터 생성 완료: {len(fpr)}개 포인트'])))

    @pytest_mark_asyncio
    async def test_pr_curve_generation(self):
        """PR 곡선 데이터 생성 테스트"""
        if self.sample_data is None:
            self.sample_data = self.tuner.generate_sample_data(100)
        (recall, precision) = self.tuner.generate_pr_data(self.sample_data, 'latency_ms')
        assert len(recall) == len(precision)
        assert len(recall) > 0
        assert all((0 <= x <= 1 for x in recall))
        assert all((0 <= x <= 1 for x in precision))
        emit_trace('info', ' '.join(map(str, [f'✅ PR 곡선 데이터 생성 완료: {len(recall)}개 포인트'])))

async def run_policy_tuning_tests():
    """정책 튜닝 테스트 실행"""
    emit_trace('info', ' '.join(map(str, ['🧪 정책 튜닝 테스트 시작'])))
    emit_trace('info', ' '.join(map(str, ['=' * 60])))
    test_instance = TestPolicyTuning()
    test_methods = ['test_sample_data_generation', 'test_metrics_calculation', 'test_threshold_evaluation', 'test_optimal_threshold_finding', 'test_roc_curve_generation', 'test_pr_curve_generation']
    passed = 0
    failed = 0
    for method_name in test_methods:
        try:
            emit_trace('info', ' '.join(map(str, [f'🔍 {method_name} 실행 중...'])))
            await getattr(test_instance, method_name)()
            emit_trace('info', ' '.join(map(str, [f'✅ {method_name} 통과'])))
            passed += 1
        except Exception as e:
            emit_trace('info', ' '.join(map(str, [f'❌ {method_name} 실패: {e}'])))
            failed += 1
    emit_trace('info', ' '.join(map(str, ['=' * 60])))
    emit_trace('info', ' '.join(map(str, [f'📊 테스트 결과: {passed}개 통과, {failed}개 실패'])))
    if failed == 0:
        emit_trace('info', ' '.join(map(str, ['🎉 모든 정책 튜닝 테스트 통과!'])))
    else:
        emit_trace('info', ' '.join(map(str, ['⚠️ 일부 테스트 실패. 수정이 필요합니다.'])))
    return (passed, failed)
if __name__ == '__main__':
    asyncio.run(run_policy_tuning_tests())