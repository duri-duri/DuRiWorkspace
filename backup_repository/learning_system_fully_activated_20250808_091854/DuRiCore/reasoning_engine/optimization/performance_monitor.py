#!/usr/bin/env python3
"""
DuRi 추론 엔진 - 성능 모니터링
Phase 3 리팩토링: logical_reasoning_engine.py에서 분리
"""

import numpy as np
import logging
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import time
import statistics
import json
from datetime import datetime

from ..core.logical_processor import LogicalProcessor, SemanticPremise, LogicalStep, PremiseType, InferenceType

logger = logging.getLogger(__name__)

class PerformanceMetric(Enum):
    """성능 지표"""
    EXECUTION_TIME = "execution_time"
    MEMORY_USAGE = "memory_usage"
    ACCURACY = "accuracy"
    CONFIDENCE = "confidence"
    THROUGHPUT = "throughput"
    LATENCY = "latency"
    ERROR_RATE = "error_rate"

@dataclass
class PerformanceSnapshot:
    """성능 스냅샷"""
    timestamp: datetime
    metrics: Dict[str, float]
    context: Dict[str, Any]
    metadata: Dict[str, Any]

@dataclass
class PerformanceReport:
    """성능 보고서"""
    start_time: datetime
    end_time: datetime
    total_operations: int
    average_metrics: Dict[str, float]
    peak_metrics: Dict[str, float]
    trend_analysis: Dict[str, str]
    recommendations: List[str]

class PerformanceMonitor:
    """성능 모니터링 클래스"""
    
    def __init__(self, logical_processor: LogicalProcessor):
        """성능 모니터링 초기화"""
        self.logical_processor = logical_processor
        self.performance_history: List[PerformanceSnapshot] = []
        self.monitoring_active = False
        self.metrics_config = self._initialize_metrics_config()
        logger.info("성능 모니터링 초기화 완료")
    
    def _initialize_metrics_config(self) -> Dict[PerformanceMetric, Dict[str, Any]]:
        """성능 지표 설정 초기화"""
        return {
            PerformanceMetric.EXECUTION_TIME: {
                "unit": "seconds",
                "threshold": 1.0,
                "weight": 0.3
            },
            PerformanceMetric.MEMORY_USAGE: {
                "unit": "KB",
                "threshold": 1000.0,
                "weight": 0.2
            },
            PerformanceMetric.ACCURACY: {
                "unit": "percentage",
                "threshold": 0.8,
                "weight": 0.3
            },
            PerformanceMetric.CONFIDENCE: {
                "unit": "percentage",
                "threshold": 0.7,
                "weight": 0.2
            },
            PerformanceMetric.THROUGHPUT: {
                "unit": "operations/second",
                "threshold": 10.0,
                "weight": 0.2
            },
            PerformanceMetric.LATENCY: {
                "unit": "milliseconds",
                "threshold": 100.0,
                "weight": 0.2
            },
            PerformanceMetric.ERROR_RATE: {
                "unit": "percentage",
                "threshold": 0.05,
                "weight": 0.3
            }
        }
    
    def start_monitoring(self):
        """모니터링 시작"""
        self.monitoring_active = True
        self.performance_history.clear()
        logger.info("성능 모니터링 시작")
    
    def stop_monitoring(self):
        """모니터링 중지"""
        self.monitoring_active = False
        logger.info("성능 모니터링 중지")
    
    def record_performance(self, 
                          premises: List[SemanticPremise], 
                          steps: List[LogicalStep],
                          context: Dict[str, Any] = None) -> PerformanceSnapshot:
        """성능 기록"""
        if not self.monitoring_active:
            logger.warning("모니터링이 활성화되지 않았습니다")
            return None
        
        start_time = time.time()
        
        # 성능 지표 측정
        metrics = self._measure_all_metrics(premises, steps)
        
        # 컨텍스트 정보 추가
        if context is None:
            context = {}
        
        context.update({
            "premise_count": len(premises),
            "step_count": len(steps),
            "total_content_length": sum(len(p.content) for p in premises) + sum(len(s.conclusion) for s in steps)
        })
        
        # 메타데이터 생성
        metadata = {
            "version": "1.0",
            "processor_type": type(self.logical_processor).__name__,
            "vector_dimension": getattr(self.logical_processor, 'vector_dimension', 100)
        }
        
        snapshot = PerformanceSnapshot(
            timestamp=datetime.now(),
            metrics=metrics,
            context=context,
            metadata=metadata
        )
        
        self.performance_history.append(snapshot)
        
        # 성능 임계값 확인
        self._check_performance_thresholds(metrics)
        
        execution_time = time.time() - start_time
        logger.debug(f"성능 기록 완료: {execution_time:.3f}초")
        
        return snapshot
    
    def _measure_all_metrics(self, premises: List[SemanticPremise], steps: List[LogicalStep]) -> Dict[str, float]:
        """모든 성능 지표 측정"""
        metrics = {}
        
        # 실행 시간 측정
        start_time = time.time()
        self._simulate_reasoning_process(premises, steps)
        execution_time = time.time() - start_time
        metrics[PerformanceMetric.EXECUTION_TIME.value] = execution_time
        
        # 메모리 사용량 측정
        memory_usage = self._measure_memory_usage(premises, steps)
        metrics[PerformanceMetric.MEMORY_USAGE.value] = memory_usage
        
        # 정확도 측정
        accuracy = self._measure_accuracy(premises, steps)
        metrics[PerformanceMetric.ACCURACY.value] = accuracy
        
        # 신뢰도 측정
        confidence = self._measure_confidence(premises, steps)
        metrics[PerformanceMetric.CONFIDENCE.value] = confidence
        
        # 처리량 측정
        throughput = self._measure_throughput(premises, steps, execution_time)
        metrics[PerformanceMetric.THROUGHPUT.value] = throughput
        
        # 지연시간 측정
        latency = execution_time * 1000  # 밀리초 단위
        metrics[PerformanceMetric.LATENCY.value] = latency
        
        # 오류율 측정
        error_rate = self._measure_error_rate(premises, steps)
        metrics[PerformanceMetric.ERROR_RATE.value] = error_rate
        
        return metrics
    
    def _simulate_reasoning_process(self, premises: List[SemanticPremise], steps: List[LogicalStep]):
        """추론 과정 시뮬레이션"""
        # 실제 추론 과정을 시뮬레이션하여 성능 측정
        for premise in premises:
            # 전제 처리 시뮬레이션
            _ = self.logical_processor.encode_semantics(premise.content)
        
        for step in steps:
            # 논리적 단계 처리 시뮬레이션
            _ = self.logical_processor.calculate_similarity(
                step.semantic_vector, 
                np.zeros_like(step.semantic_vector)
            )
    
    def _measure_memory_usage(self, premises: List[SemanticPremise], steps: List[LogicalStep]) -> float:
        """메모리 사용량 측정"""
        total_memory = 0.0
        
        # 전제들의 메모리 사용량
        for premise in premises:
            # 의미 벡터 크기
            vector_memory = premise.semantic_vector.nbytes / 1024  # KB
            # 텍스트 크기
            text_memory = len(premise.content.encode('utf-8')) / 1024  # KB
            total_memory += vector_memory + text_memory
        
        # 논리적 단계들의 메모리 사용량
        for step in steps:
            # 의미 벡터 크기
            vector_memory = step.semantic_vector.nbytes / 1024  # KB
            # 텍스트 크기
            text_memory = len(step.conclusion.encode('utf-8')) / 1024  # KB
            total_memory += vector_memory + text_memory
        
        return total_memory
    
    def _measure_accuracy(self, premises: List[SemanticPremise], steps: List[LogicalStep]) -> float:
        """정확도 측정"""
        if not premises or not steps:
            return 0.0
        
        # 전제들의 일관성 평가
        premise_consistency = self._evaluate_premise_consistency(premises)
        
        # 논리적 단계들의 유효성 평가
        step_validity = self._evaluate_step_validity(steps)
        
        # 전체 정확도 계산
        accuracy = (premise_consistency + step_validity) / 2
        
        return accuracy
    
    def _evaluate_premise_consistency(self, premises: List[SemanticPremise]) -> float:
        """전제 일관성 평가"""
        if len(premises) < 2:
            return 1.0
        
        # 전제들 간의 의미적 유사도 계산
        similarities = []
        for i in range(len(premises)):
            for j in range(i + 1, len(premises)):
                similarity = self.logical_processor.calculate_similarity(
                    premises[i].semantic_vector, 
                    premises[j].semantic_vector
                )
                similarities.append(similarity)
        
        # 평균 유사도를 일관성으로 사용
        consistency = sum(similarities) / len(similarities) if similarities else 1.0
        
        return consistency
    
    def _evaluate_step_validity(self, steps: List[LogicalStep]) -> float:
        """논리적 단계 유효성 평가"""
        if not steps:
            return 1.0
        
        # 각 단계의 신뢰도와 논리적 강도 평가
        validities = []
        for step in steps:
            validity = (step.confidence + step.logical_strength) / 2
            validities.append(validity)
        
        # 평균 유효성 반환
        return sum(validities) / len(validities) if validities else 1.0
    
    def _measure_confidence(self, premises: List[SemanticPremise], steps: List[LogicalStep]) -> float:
        """신뢰도 측정"""
        if not premises and not steps:
            return 0.0
        
        # 전제들의 신뢰도
        premise_confidences = [premise.confidence for premise in premises]
        avg_premise_confidence = sum(premise_confidences) / len(premise_confidences) if premise_confidences else 0.0
        
        # 논리적 단계들의 신뢰도
        step_confidences = [step.confidence for step in steps]
        avg_step_confidence = sum(step_confidences) / len(step_confidences) if step_confidences else 0.0
        
        # 전체 신뢰도 계산
        if premises and steps:
            confidence = (avg_premise_confidence + avg_step_confidence) / 2
        elif premises:
            confidence = avg_premise_confidence
        else:
            confidence = avg_step_confidence
        
        return confidence
    
    def _measure_throughput(self, premises: List[SemanticPremise], steps: List[LogicalStep], execution_time: float) -> float:
        """처리량 측정"""
        if execution_time <= 0:
            return 0.0
        
        # 초당 처리할 수 있는 작업 수
        total_operations = len(premises) + len(steps)
        throughput = total_operations / execution_time
        
        return throughput
    
    def _measure_error_rate(self, premises: List[SemanticPremise], steps: List[LogicalStep]) -> float:
        """오류율 측정"""
        total_items = len(premises) + len(steps)
        if total_items == 0:
            return 0.0
        
        error_count = 0
        
        # 전제들의 오류 검사
        for premise in premises:
            if premise.confidence < 0.5 or len(premise.content.strip()) == 0:
                error_count += 1
        
        # 논리적 단계들의 오류 검사
        for step in steps:
            if step.confidence < 0.5 or len(step.conclusion.strip()) == 0:
                error_count += 1
        
        error_rate = error_count / total_items
        
        return error_rate
    
    def _check_performance_thresholds(self, metrics: Dict[str, float]):
        """성능 임계값 확인"""
        warnings = []
        
        for metric_name, value in metrics.items():
            metric_enum = PerformanceMetric(metric_name)
            if metric_enum in self.metrics_config:
                threshold = self.metrics_config[metric_enum]["threshold"]
                
                # 임계값 초과 확인
                if metric_enum in [PerformanceMetric.EXECUTION_TIME, PerformanceMetric.MEMORY_USAGE, PerformanceMetric.LATENCY, PerformanceMetric.ERROR_RATE]:
                    if value > threshold:
                        warnings.append(f"{metric_name}: {value:.2f} > {threshold:.2f}")
                else:
                    if value < threshold:
                        warnings.append(f"{metric_name}: {value:.2f} < {threshold:.2f}")
        
        if warnings:
            logger.warning(f"성능 임계값 초과: {', '.join(warnings)}")
    
    def generate_performance_report(self, start_time: datetime = None, end_time: datetime = None) -> PerformanceReport:
        """성능 보고서 생성"""
        if not self.performance_history:
            logger.warning("성능 이력이 없습니다")
            return None
        
        # 시간 범위 필터링
        if start_time is None:
            start_time = self.performance_history[0].timestamp
        if end_time is None:
            end_time = self.performance_history[-1].timestamp
        
        filtered_history = [
            snapshot for snapshot in self.performance_history
            if start_time <= snapshot.timestamp <= end_time
        ]
        
        if not filtered_history:
            logger.warning("지정된 시간 범위에 성능 데이터가 없습니다")
            return None
        
        # 평균 지표 계산
        average_metrics = self._calculate_average_metrics(filtered_history)
        
        # 최고 지표 계산
        peak_metrics = self._calculate_peak_metrics(filtered_history)
        
        # 트렌드 분석
        trend_analysis = self._analyze_trends(filtered_history)
        
        # 권장사항 생성
        recommendations = self._generate_recommendations(average_metrics, peak_metrics, trend_analysis)
        
        report = PerformanceReport(
            start_time=start_time,
            end_time=end_time,
            total_operations=len(filtered_history),
            average_metrics=average_metrics,
            peak_metrics=peak_metrics,
            trend_analysis=trend_analysis,
            recommendations=recommendations
        )
        
        logger.info(f"성능 보고서 생성 완료: {len(filtered_history)}개 스냅샷 분석")
        
        return report
    
    def _calculate_average_metrics(self, history: List[PerformanceSnapshot]) -> Dict[str, float]:
        """평균 지표 계산"""
        if not history:
            return {}
        
        metrics_sum = {}
        metrics_count = {}
        
        for snapshot in history:
            for metric_name, value in snapshot.metrics.items():
                if metric_name not in metrics_sum:
                    metrics_sum[metric_name] = 0.0
                    metrics_count[metric_name] = 0
                
                metrics_sum[metric_name] += value
                metrics_count[metric_name] += 1
        
        average_metrics = {}
        for metric_name in metrics_sum:
            average_metrics[metric_name] = metrics_sum[metric_name] / metrics_count[metric_name]
        
        return average_metrics
    
    def _calculate_peak_metrics(self, history: List[PerformanceSnapshot]) -> Dict[str, float]:
        """최고 지표 계산"""
        if not history:
            return {}
        
        peak_metrics = {}
        
        for snapshot in history:
            for metric_name, value in snapshot.metrics.items():
                if metric_name not in peak_metrics:
                    peak_metrics[metric_name] = value
                else:
                    # 실행 시간, 메모리 사용량, 지연시간, 오류율은 최대값
                    if metric_name in ["execution_time", "memory_usage", "latency", "error_rate"]:
                        peak_metrics[metric_name] = max(peak_metrics[metric_name], value)
                    # 나머지는 최소값
                    else:
                        peak_metrics[metric_name] = min(peak_metrics[metric_name], value)
        
        return peak_metrics
    
    def _analyze_trends(self, history: List[PerformanceSnapshot]) -> Dict[str, str]:
        """트렌드 분석"""
        if len(history) < 2:
            return {"trend": "insufficient_data"}
        
        trends = {}
        
        # 각 지표별 트렌드 분석
        for metric_name in history[0].metrics.keys():
            values = [snapshot.metrics[metric_name] for snapshot in history]
            
            if len(values) >= 3:
                # 선형 회귀를 통한 트렌드 분석
                trend = self._calculate_trend(values)
                trends[metric_name] = trend
            else:
                trends[metric_name] = "insufficient_data"
        
        return trends
    
    def _calculate_trend(self, values: List[float]) -> str:
        """트렌드 계산"""
        if len(values) < 3:
            return "insufficient_data"
        
        # 간단한 트렌드 분석: 처음 1/3과 마지막 1/3의 평균 비교
        first_third = values[:len(values)//3]
        last_third = values[-len(values)//3:]
        
        first_avg = sum(first_third) / len(first_third)
        last_avg = sum(last_third) / len(last_third)
        
        change_ratio = (last_avg - first_avg) / max(first_avg, 0.1)
        
        if change_ratio > 0.1:
            return "improving"
        elif change_ratio < -0.1:
            return "degrading"
        else:
            return "stable"
    
    def _generate_recommendations(self, 
                                average_metrics: Dict[str, float], 
                                peak_metrics: Dict[str, float],
                                trend_analysis: Dict[str, str]) -> List[str]:
        """권장사항 생성"""
        recommendations = []
        
        # 실행 시간 권장사항
        if "execution_time" in average_metrics:
            if average_metrics["execution_time"] > 1.0:
                recommendations.append("실행 시간이 높습니다. 추론 과정을 최적화하거나 병렬 처리를 고려하세요.")
        
        # 메모리 사용량 권장사항
        if "memory_usage" in average_metrics:
            if average_metrics["memory_usage"] > 1000.0:
                recommendations.append("메모리 사용량이 높습니다. 의미 벡터 압축이나 불필요한 데이터 정리를 고려하세요.")
        
        # 정확도 권장사항
        if "accuracy" in average_metrics:
            if average_metrics["accuracy"] < 0.8:
                recommendations.append("정확도가 낮습니다. 전제의 품질을 향상시키거나 논리적 단계를 검증하세요.")
        
        # 신뢰도 권장사항
        if "confidence" in average_metrics:
            if average_metrics["confidence"] < 0.7:
                recommendations.append("신뢰도가 낮습니다. 전제와 논리적 단계의 신뢰성을 향상시키세요.")
        
        # 트렌드 기반 권장사항
        for metric_name, trend in trend_analysis.items():
            if trend == "degrading":
                recommendations.append(f"{metric_name}의 성능이 저하되고 있습니다. 최적화가 필요합니다.")
        
        if not recommendations:
            recommendations.append("현재 성능이 양호합니다. 정기적인 모니터링을 계속하세요.")
        
        return recommendations
    
    def export_performance_data(self, filepath: str, format: str = "json"):
        """성능 데이터 내보내기"""
        if not self.performance_history:
            logger.warning("내보낼 성능 데이터가 없습니다")
            return
        
        try:
            if format.lower() == "json":
                self._export_to_json(filepath)
            else:
                logger.error(f"지원하지 않는 형식: {format}")
                return
            
            logger.info(f"성능 데이터 내보내기 완료: {filepath}")
        
        except Exception as e:
            logger.error(f"성능 데이터 내보내기 실패: {e}")
    
    def _export_to_json(self, filepath: str):
        """JSON 형식으로 내보내기"""
        export_data = {
            "export_timestamp": datetime.now().isoformat(),
            "total_snapshots": len(self.performance_history),
            "snapshots": []
        }
        
        for snapshot in self.performance_history:
            snapshot_data = {
                "timestamp": snapshot.timestamp.isoformat(),
                "metrics": snapshot.metrics,
                "context": snapshot.context,
                "metadata": snapshot.metadata
            }
            export_data["snapshots"].append(snapshot_data)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """성능 요약 정보 반환"""
        if not self.performance_history:
            return {"status": "no_data"}
        
        latest_snapshot = self.performance_history[-1]
        total_snapshots = len(self.performance_history)
        
        # 최근 10개 스냅샷의 평균
        recent_snapshots = self.performance_history[-10:] if total_snapshots >= 10 else self.performance_history
        recent_averages = self._calculate_average_metrics(recent_snapshots)
        
        summary = {
            "status": "active",
            "total_snapshots": total_snapshots,
            "latest_timestamp": latest_snapshot.timestamp.isoformat(),
            "recent_averages": recent_averages,
            "monitoring_active": self.monitoring_active
        }
        
        return summary
