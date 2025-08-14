"""
고급 분석 기능 모듈
ML 통합 과정의 데이터를 심층 분석하고 인사이트를 제공합니다.
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, Any, List, Optional, Tuple, Union
from dataclasses import dataclass
from datetime import datetime, timedelta
import json
import logging
from pathlib import Path
import warnings

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 경고 무시
warnings.filterwarnings('ignore')

@dataclass
class AnalysisResult:
    """분석 결과 데이터 클래스"""
    analysis_id: str
    analysis_type: str
    timestamp: datetime
    summary: Dict[str, Any]
    detailed_results: Dict[str, Any]
    visualizations: List[str]
    recommendations: List[str]
    confidence_score: float

class DataAnalyzer:
    """데이터 분석기 기본 클래스"""
    
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
    
    def analyze(self, data: Any) -> AnalysisResult:
        """데이터 분석 - 하위 클래스에서 구현"""
        raise NotImplementedError("하위 클래스에서 구현해야 합니다")
    
    def get_analysis_capabilities(self) -> List[str]:
        """분석 능력 반환 - 하위 클래스에서 구현"""
        raise NotImplementedError("하위 클래스에서 구현해야 합니다")

class PerformanceTrendAnalyzer(DataAnalyzer):
    """성능 트렌드 분석기"""
    
    def __init__(self):
        super().__init__("PerformanceTrend", "ML 모델 성능 트렌드 분석")
    
    def analyze(self, data: Dict[str, Any]) -> AnalysisResult:
        """성능 트렌드 분석"""
        try:
            analysis_id = f"perf_trend_{int(datetime.now().timestamp())}"
            
            # 성능 데이터 추출
            performance_data = data.get('performance_history', [])
            if not performance_data:
                return self._create_empty_result(analysis_id, "성능 데이터가 없습니다")
            
            # 데이터프레임 변환
            df = pd.DataFrame(performance_data)
            
            # 트렌드 분석
            trend_analysis = self._analyze_trends(df)
            
            # 이상치 탐지
            anomaly_detection = self._detect_anomalies(df)
            
            # 예측 분석
            prediction_analysis = self._predict_future_performance(df)
            
            # 요약 통계
            summary_stats = self._calculate_summary_stats(df)
            
            # 시각화 생성
            viz_files = self._create_visualizations(df, analysis_id)
            
            # 권장사항 생성
            recommendations = self._generate_recommendations(trend_analysis, anomaly_detection)
            
            # 신뢰도 점수 계산
            confidence_score = self._calculate_confidence_score(df, trend_analysis)
            
            return AnalysisResult(
                analysis_id=analysis_id,
                analysis_type="PerformanceTrend",
                timestamp=datetime.now(),
                summary=summary_stats,
                detailed_results={
                    "trend_analysis": trend_analysis,
                    "anomaly_detection": anomaly_detection,
                    "prediction_analysis": prediction_analysis
                },
                visualizations=viz_files,
                recommendations=recommendations,
                confidence_score=confidence_score
            )
        
        except Exception as e:
            logger.error(f"성능 트렌드 분석 실패: {str(e)}")
            return self._create_error_result(analysis_id, str(e))
    
    def _analyze_trends(self, df: pd.DataFrame) -> Dict[str, Any]:
        """트렌드 분석"""
        try:
            trends = {}
            
            # 주요 메트릭 추출
            metrics = ['accuracy', 'f1_score', 'precision', 'recall']
            available_metrics = [col for col in metrics if col in df.columns]
            
            for metric in available_metrics:
                if metric in df.columns:
                    # 선형 트렌드 계산
                    x = np.arange(len(df))
                    y = df[metric].values
                    
                    if len(y) > 1:
                        slope, intercept = np.polyfit(x, y, 1)
                        trend_direction = "improving" if slope > 0 else "declining" if slope < 0 else "stable"
                        
                        trends[metric] = {
                            "slope": slope,
                            "intercept": intercept,
                            "trend_direction": trend_direction,
                            "change_rate": slope * len(df) / y[0] if y[0] != 0 else 0,
                            "current_value": y[-1],
                            "initial_value": y[0]
                        }
            
            return trends
        
        except Exception as e:
            logger.error(f"트렌드 분석 실패: {str(e)}")
            return {}
    
    def _detect_anomalies(self, df: pd.DataFrame) -> Dict[str, Any]:
        """이상치 탐지"""
        try:
            anomalies = {}
            
            # 주요 메트릭에 대한 이상치 탐지
            metrics = ['accuracy', 'f1_score', 'precision', 'recall']
            
            for metric in metrics:
                if metric in df.columns:
                    values = df[metric].values
                    
                    if len(values) > 2:
                        # IQR 방법을 사용한 이상치 탐지
                        Q1 = np.percentile(values, 25)
                        Q3 = np.percentile(values, 75)
                        IQR = Q3 - Q1
                        
                        lower_bound = Q1 - 1.5 * IQR
                        upper_bound = Q3 + 1.5 * IQR
                        
                        anomaly_indices = np.where((values < lower_bound) | (values > upper_bound))[0]
                        
                        if len(anomaly_indices) > 0:
                            anomalies[metric] = {
                                "anomaly_count": len(anomaly_indices),
                                "anomaly_indices": anomaly_indices.tolist(),
                                "anomaly_values": values[anomaly_indices].tolist(),
                                "lower_bound": lower_bound,
                                "upper_bound": upper_bound
                            }
            
            return anomalies
        
        except Exception as e:
            logger.error(f"이상치 탐지 실패: {str(e)}")
            return {}
    
    def _predict_future_performance(self, df: pd.DataFrame) -> Dict[str, Any]:
        """미래 성능 예측"""
        try:
            predictions = {}
            
            # 간단한 선형 예측
            metrics = ['accuracy', 'f1_score', 'precision', 'recall']
            
            for metric in metrics:
                if metric in df.columns:
                    values = df[metric].values
                    
                    if len(values) > 2:
                        # 선형 회귀로 미래 3개 지점 예측
                        x = np.arange(len(values))
                        y = values
                        
                        slope, intercept = np.polyfit(x, y, 1)
                        
                        future_x = np.arange(len(values), len(values) + 3)
                        future_y = slope * future_x + intercept
                        
                        predictions[metric] = {
                            "next_3_predictions": future_y.tolist(),
                            "prediction_confidence": self._calculate_prediction_confidence(values),
                            "trend_strength": abs(slope)
                        }
            
            return predictions
        
        except Exception as e:
            logger.error(f"미래 성능 예측 실패: {str(e)}")
            return {}
    
    def _calculate_summary_stats(self, df: pd.DataFrame) -> Dict[str, Any]:
        """요약 통계 계산"""
        try:
            summary = {
                "total_records": len(df),
                "date_range": {
                    "start": df.index[0] if len(df) > 0 else None,
                    "end": df.index[-1] if len(df) > 0 else None
                }
            }
            
            # 메트릭별 통계
            metrics = ['accuracy', 'f1_score', 'precision', 'recall']
            
            for metric in metrics:
                if metric in df.columns:
                    values = df[metric].values
                    summary[metric] = {
                        "mean": float(np.mean(values)),
                        "std": float(np.std(values)),
                        "min": float(np.min(values)),
                        "max": float(np.max(values)),
                        "median": float(np.median(values))
                    }
            
            return summary
        
        except Exception as e:
            logger.error(f"요약 통계 계산 실패: {str(e)}")
            return {}
    
    def _create_visualizations(self, df: pd.DataFrame, analysis_id: str) -> List[str]:
        """시각화 생성"""
        try:
            viz_files = []
            
            # 1. 성능 트렌드 그래프
            plt.figure(figsize=(12, 8))
            
            metrics = ['accuracy', 'f1_score', 'precision', 'recall']
            available_metrics = [col for col in metrics if col in df.columns]
            
            for i, metric in enumerate(available_metrics):
                plt.subplot(2, 2, i+1)
                plt.plot(df.index, df[metric], marker='o', linewidth=2, markersize=6)
                plt.title(f'{metric.replace("_", " ").title()} Trend')
                plt.xlabel('Time')
                plt.ylabel(metric.replace("_", " ").title())
                plt.grid(True, alpha=0.3)
                plt.xticks(rotation=45)
            
            plt.tight_layout()
            trend_file = f"performance_trend_{analysis_id}.png"
            plt.savefig(trend_file, dpi=300, bbox_inches='tight')
            plt.close()
            viz_files.append(trend_file)
            
            # 2. 성능 분포 히스토그램
            plt.figure(figsize=(12, 8))
            
            for i, metric in enumerate(available_metrics):
                plt.subplot(2, 2, i+1)
                plt.hist(df[metric], bins=20, alpha=0.7, edgecolor='black')
                plt.title(f'{metric.replace("_", " ").title()} Distribution')
                plt.xlabel(metric.replace("_", " ").title())
                plt.ylabel('Frequency')
                plt.grid(True, alpha=0.3)
            
            plt.tight_layout()
            dist_file = f"performance_distribution_{analysis_id}.png"
            plt.savefig(dist_file, dpi=300, bbox_inches='tight')
            plt.close()
            viz_files.append(dist_file)
            
            return viz_files
        
        except Exception as e:
            logger.error(f"시각화 생성 실패: {str(e)}")
            return []
    
    def _generate_recommendations(self, trend_analysis: Dict, anomaly_detection: Dict) -> List[str]:
        """권장사항 생성"""
        recommendations = []
        
        try:
            # 트렌드 기반 권장사항
            for metric, trend in trend_analysis.items():
                if trend['trend_direction'] == 'declining':
                    recommendations.append(f"{metric} 성능이 하락하고 있습니다. 모델 재훈련을 고려해보세요.")
                elif trend['trend_direction'] == 'improving':
                    recommendations.append(f"{metric} 성능이 개선되고 있습니다. 현재 전략을 유지하세요.")
            
            # 이상치 기반 권장사항
            for metric, anomalies in anomaly_detection.items():
                if anomalies['anomaly_count'] > 0:
                    recommendations.append(f"{metric}에서 {anomalies['anomaly_count']}개의 이상치가 발견되었습니다. 데이터 품질을 확인해보세요.")
            
            # 일반적인 권장사항
            if not recommendations:
                recommendations.append("현재 성능이 안정적입니다. 정기적인 모니터링을 계속하세요.")
            
            return recommendations
        
        except Exception as e:
            logger.error(f"권장사항 생성 실패: {str(e)}")
            return ["분석 중 오류가 발생했습니다."]
    
    def _calculate_confidence_score(self, df: pd.DataFrame, trend_analysis: Dict) -> float:
        """신뢰도 점수 계산"""
        try:
            if len(df) < 2:
                return 0.0
            
            # 데이터 품질 점수
            data_quality_score = min(1.0, len(df) / 100)  # 최대 100개 데이터 기준
            
            # 트렌드 일관성 점수
            trend_consistency = 0.0
            if trend_analysis:
                consistent_trends = sum(1 for trend in trend_analysis.values() if abs(trend['slope']) > 0.001)
                trend_consistency = consistent_trends / len(trend_analysis) if trend_analysis else 0.0
            
            # 최종 신뢰도 점수
            confidence = (data_quality_score * 0.6) + (trend_consistency * 0.4)
            
            return round(confidence, 2)
        
        except Exception as e:
            logger.error(f"신뢰도 점수 계산 실패: {str(e)}")
            return 0.0
    
    def _create_empty_result(self, analysis_id: str, message: str) -> AnalysisResult:
        """빈 결과 생성"""
        return AnalysisResult(
            analysis_id=analysis_id,
            analysis_type="PerformanceTrend",
            timestamp=datetime.now(),
            summary={"message": message},
            detailed_results={},
            visualizations=[],
            recommendations=["데이터가 부족합니다."],
            confidence_score=0.0
        )
    
    def _create_error_result(self, analysis_id: str, error_message: str) -> AnalysisResult:
        """오류 결과 생성"""
        return AnalysisResult(
            analysis_id=analysis_id,
            analysis_type="PerformanceTrend",
            timestamp=datetime.now(),
            summary={"error": error_message},
            detailed_results={},
            visualizations=[],
            recommendations=["분석 중 오류가 발생했습니다."],
            confidence_score=0.0
        )
    
    def get_analysis_capabilities(self) -> List[str]:
        """분석 능력 반환"""
        return [
            "성능 트렌드 분석",
            "이상치 탐지",
            "미래 성능 예측",
            "통계적 요약",
            "시각화 생성",
            "권장사항 제공"
        ]

class IntegrationEfficiencyAnalyzer(DataAnalyzer):
    """통합 효율성 분석기"""
    
    def __init__(self):
        super().__init__("IntegrationEfficiency", "ML 통합 과정의 효율성 분석")
    
    def analyze(self, data: Dict[str, Any]) -> AnalysisResult:
        """통합 효율성 분석"""
        try:
            analysis_id = f"integration_eff_{int(datetime.now().timestamp())}"
            
            # 통합 데이터 추출
            integration_data = data.get('integration_history', [])
            if not integration_data:
                return self._create_empty_result(analysis_id, "통합 데이터가 없습니다")
            
            # 효율성 분석
            efficiency_metrics = self._analyze_efficiency(integration_data)
            
            # 병목 지점 분석
            bottleneck_analysis = self._analyze_bottlenecks(integration_data)
            
            # 리소스 사용량 분석
            resource_analysis = self._analyze_resource_usage(integration_data)
            
            # 최적화 기회 분석
            optimization_opportunities = self._identify_optimization_opportunities(efficiency_metrics, bottleneck_analysis)
            
            # 시각화 생성
            viz_files = self._create_efficiency_visualizations(integration_data, analysis_id)
            
            # 권장사항 생성
            recommendations = self._generate_efficiency_recommendations(efficiency_metrics, bottleneck_analysis)
            
            # 신뢰도 점수 계산
            confidence_score = self._calculate_efficiency_confidence(integration_data, efficiency_metrics)
            
            return AnalysisResult(
                analysis_id=analysis_id,
                analysis_type="IntegrationEfficiency",
                timestamp=datetime.now(),
                summary=efficiency_metrics,
                detailed_results={
                    "bottleneck_analysis": bottleneck_analysis,
                    "resource_analysis": resource_analysis,
                    "optimization_opportunities": optimization_opportunities
                },
                visualizations=viz_files,
                recommendations=recommendations,
                confidence_score=confidence_score
            )
        
        except Exception as e:
            logger.error(f"통합 효율성 분석 실패: {str(e)}")
            return self._create_error_result(analysis_id, str(e))
    
    def _analyze_efficiency(self, integration_data: List[Dict]) -> Dict[str, Any]:
        """효율성 분석"""
        try:
            efficiency = {}
            
            # 실행 시간 분석
            execution_times = [item.get('execution_time', 0) for item in integration_data]
            if execution_times:
                efficiency['execution_time'] = {
                    "mean": float(np.mean(execution_times)),
                    "median": float(np.median(execution_times)),
                    "min": float(np.min(execution_times)),
                    "max": float(np.max(execution_times)),
                    "std": float(np.std(execution_times))
                }
            
            # 성공률 분석
            success_count = sum(1 for item in integration_data if item.get('status') == 'completed')
            total_count = len(integration_data)
            efficiency['success_rate'] = (success_count / total_count) * 100 if total_count > 0 else 0
            
            # 처리량 분석
            if execution_times:
                throughput = 1.0 / np.mean(execution_times) if np.mean(execution_times) > 0 else 0
                efficiency['throughput'] = throughput
            
            return efficiency
        
        except Exception as e:
            logger.error(f"효율성 분석 실패: {str(e)}")
            return {}
    
    def _analyze_bottlenecks(self, integration_data: List[Dict]) -> Dict[str, Any]:
        """병목 지점 분석"""
        try:
            bottlenecks = {}
            
            # 단계별 실행 시간 분석
            phase_times = {}
            for item in integration_data:
                phase = item.get('phase', 'unknown')
                if phase not in phase_times:
                    phase_times[phase] = []
                phase_times[phase].append(item.get('execution_time', 0))
            
            # 각 단계별 평균 실행 시간
            for phase, times in phase_times.items():
                if times:
                    bottlenecks[phase] = {
                        "avg_time": float(np.mean(times)),
                        "max_time": float(np.max(times)),
                        "total_runs": len(times)
                    }
            
            # 가장 느린 단계 식별
            if bottlenecks:
                slowest_phase = max(bottlenecks.items(), key=lambda x: x[1]['avg_time'])
                bottlenecks['slowest_phase'] = {
                    "phase": slowest_phase[0],
                    "avg_time": slowest_phase[1]['avg_time']
                }
            
            return bottlenecks
        
        except Exception as e:
            logger.error(f"병목 지점 분석 실패: {str(e)}")
            return {}
    
    def _analyze_resource_usage(self, integration_data: List[Dict]) -> Dict[str, Any]:
        """리소스 사용량 분석"""
        try:
            resource_usage = {}
            
            # 메모리 사용량 분석
            memory_usage = [item.get('memory_usage', 0) for item in integration_data if item.get('memory_usage')]
            if memory_usage:
                resource_usage['memory'] = {
                    "mean": float(np.mean(memory_usage)),
                    "max": float(np.max(memory_usage)),
                    "min": float(np.min(memory_usage))
                }
            
            # CPU 사용량 분석
            cpu_usage = [item.get('cpu_usage', 0) for item in integration_data if item.get('cpu_usage')]
            if cpu_usage:
                resource_usage['cpu'] = {
                    "mean": float(np.mean(cpu_usage)),
                    "max": float(np.max(cpu_usage)),
                    "min": float(np.min(cpu_usage))
                }
            
            return resource_usage
        
        except Exception as e:
            logger.error(f"리소스 사용량 분석 실패: {str(e)}")
            return {}
    
    def _identify_optimization_opportunities(self, efficiency_metrics: Dict, bottleneck_analysis: Dict) -> List[str]:
        """최적화 기회 식별"""
        opportunities = []
        
        try:
            # 실행 시간 최적화 기회
            if 'execution_time' in efficiency_metrics:
                avg_time = efficiency_metrics['execution_time']['mean']
                if avg_time > 60:  # 1분 이상
                    opportunities.append("실행 시간이 길어 최적화가 필요합니다.")
            
            # 성공률 개선 기회
            if 'success_rate' in efficiency_metrics:
                success_rate = efficiency_metrics['success_rate']
                if success_rate < 90:
                    opportunities.append(f"성공률이 {success_rate:.1f}%로 개선이 필요합니다.")
            
            # 병목 지점 최적화 기회
            if 'slowest_phase' in bottleneck_analysis:
                slowest = bottleneck_analysis['slowest_phase']
                opportunities.append(f"{slowest['phase']} 단계가 가장 느리므로 최적화를 우선적으로 고려하세요.")
            
            return opportunities
        
        except Exception as e:
            logger.error(f"최적화 기회 식별 실패: {str(e)}")
            return ["분석 중 오류가 발생했습니다."]
    
    def _create_efficiency_visualizations(self, integration_data: List[Dict], analysis_id: str) -> List[str]:
        """효율성 시각화 생성"""
        try:
            viz_files = []
            
            # 1. 실행 시간 분포
            execution_times = [item.get('execution_time', 0) for item in integration_data]
            
            plt.figure(figsize=(10, 6))
            plt.hist(execution_times, bins=20, alpha=0.7, edgecolor='black')
            plt.title('Execution Time Distribution')
            plt.xlabel('Execution Time (seconds)')
            plt.ylabel('Frequency')
            plt.grid(True, alpha=0.3)
            
            time_dist_file = f"execution_time_dist_{analysis_id}.png"
            plt.savefig(time_dist_file, dpi=300, bbox_inches='tight')
            plt.close()
            viz_files.append(time_dist_file)
            
            # 2. 단계별 실행 시간 비교
            phase_times = {}
            for item in integration_data:
                phase = item.get('phase', 'unknown')
                if phase not in phase_times:
                    phase_times[phase] = []
                phase_times[phase].append(item.get('execution_time', 0))
            
            if phase_times:
                phases = list(phase_times.keys())
                avg_times = [np.mean(phase_times[phase]) for phase in phases]
                
                plt.figure(figsize=(10, 6))
                plt.bar(phases, avg_times, alpha=0.7)
                plt.title('Average Execution Time by Phase')
                plt.xlabel('Phase')
                plt.ylabel('Average Time (seconds)')
                plt.xticks(rotation=45)
                plt.grid(True, alpha=0.3)
                
                phase_time_file = f"phase_time_comparison_{analysis_id}.png"
                plt.savefig(phase_time_file, dpi=300, bbox_inches='tight')
                plt.close()
                viz_files.append(phase_time_file)
            
            return viz_files
        
        except Exception as e:
            logger.error(f"효율성 시각화 생성 실패: {str(e)}")
            return []
    
    def _generate_efficiency_recommendations(self, efficiency_metrics: Dict, bottleneck_analysis: Dict) -> List[str]:
        """효율성 권장사항 생성"""
        recommendations = []
        
        try:
            # 실행 시간 기반 권장사항
            if 'execution_time' in efficiency_metrics:
                avg_time = efficiency_metrics['execution_time']['mean']
                if avg_time > 120:  # 2분 이상
                    recommendations.append("실행 시간이 매우 깁니다. 알고리즘 최적화를 고려하세요.")
                elif avg_time > 60:  # 1분 이상
                    recommendations.append("실행 시간이 깁니다. 병렬 처리를 고려하세요.")
            
            # 성공률 기반 권장사항
            if 'success_rate' in efficiency_metrics:
                success_rate = efficiency_metrics['success_rate']
                if success_rate < 80:
                    recommendations.append("성공률이 낮습니다. 오류 처리와 로깅을 강화하세요.")
                elif success_rate < 95:
                    recommendations.append("성공률을 더 높일 수 있습니다. 안정성을 개선하세요.")
            
            # 병목 지점 기반 권장사항
            if 'slowest_phase' in bottleneck_analysis:
                slowest = bottleneck_analysis['slowest_phase']
                recommendations.append(f"{slowest['phase']} 단계를 최적화하여 전체 성능을 개선하세요.")
            
            return recommendations
        
        except Exception as e:
            logger.error(f"효율성 권장사항 생성 실패: {str(e)}")
            return ["분석 중 오류가 발생했습니다."]
    
    def _calculate_efficiency_confidence(self, integration_data: List[Dict], efficiency_metrics: Dict) -> float:
        """효율성 분석 신뢰도 점수 계산"""
        try:
            if len(integration_data) < 2:
                return 0.0
            
            # 데이터 품질 점수
            data_quality_score = min(1.0, len(integration_data) / 50)  # 최대 50개 데이터 기준
            
            # 메트릭 완성도 점수
            metric_completeness = 0.0
            required_metrics = ['execution_time', 'success_rate']
            available_metrics = sum(1 for metric in required_metrics if metric in efficiency_metrics)
            metric_completeness = available_metrics / len(required_metrics)
            
            # 최종 신뢰도 점수
            confidence = (data_quality_score * 0.7) + (metric_completeness * 0.3)
            
            return round(confidence, 2)
        
        except Exception as e:
            logger.error(f"효율성 신뢰도 점수 계산 실패: {str(e)}")
            return 0.0
    
    def _create_empty_result(self, analysis_id: str, message: str) -> AnalysisResult:
        """빈 결과 생성"""
        return AnalysisResult(
            analysis_id=analysis_id,
            analysis_type="IntegrationEfficiency",
            timestamp=datetime.now(),
            summary={"message": message},
            detailed_results={},
            visualizations=[],
            recommendations=["데이터가 부족합니다."],
            confidence_score=0.0
        )
    
    def _create_error_result(self, analysis_id: str, error_message: str) -> AnalysisResult:
        """오류 결과 생성"""
        return AnalysisResult(
            analysis_id=analysis_id,
            analysis_type="IntegrationEfficiency",
            timestamp=datetime.now(),
            summary={"error": error_message},
            detailed_results={},
            visualizations=[],
            recommendations=["분석 중 오류가 발생했습니다."],
            confidence_score=0.0
        )
    
    def get_analysis_capabilities(self) -> List[str]:
        """분석 능력 반환"""
        return [
            "통합 효율성 분석",
            "병목 지점 식별",
            "리소스 사용량 분석",
            "최적화 기회 식별",
            "성능 시각화",
            "효율성 권장사항"
        ]

class AdvancedAnalyticsEngine:
    """고급 분석 엔진"""
    
    def __init__(self):
        self.analyzers: Dict[str, DataAnalyzer] = {}
        self.analysis_history: List[AnalysisResult] = []
        
        # 기본 분석기 등록
        self._register_default_analyzers()
    
    def _register_default_analyzers(self):
        """기본 분석기 등록"""
        self.analyzers['performance_trend'] = PerformanceTrendAnalyzer()
        self.analyzers['integration_efficiency'] = IntegrationEfficiencyAnalyzer()
        
        logger.info(f"기본 분석기 등록 완료: {len(self.analyzers)}개")
    
    def add_analyzer(self, name: str, analyzer: DataAnalyzer):
        """분석기 추가"""
        self.analyzers[name] = analyzer
        logger.info(f"분석기 추가: {name}")
    
    def remove_analyzer(self, name: str):
        """분석기 제거"""
        if name in self.analyzers:
            del self.analyzers[name]
            logger.info(f"분석기 제거: {name}")
    
    def run_analysis(self, analysis_type: str, data: Dict[str, Any]) -> Optional[AnalysisResult]:
        """분석 실행"""
        try:
            if analysis_type not in self.analyzers:
                logger.error(f"알 수 없는 분석 유형: {analysis_type}")
                return None
            
            analyzer = self.analyzers[analysis_type]
            logger.info(f"분석 시작: {analysis_type}")
            
            # 분석 실행
            result = analyzer.analyze(data)
            
            # 결과를 히스토리에 추가
            self.analysis_history.append(result)
            
            logger.info(f"분석 완료: {analysis_type} - ID: {result.analysis_id}")
            return result
        
        except Exception as e:
            logger.error(f"분석 실행 실패: {str(e)}")
            return None
    
    def run_comprehensive_analysis(self, data: Dict[str, Any]) -> Dict[str, AnalysisResult]:
        """포괄적 분석 실행"""
        try:
            results = {}
            
            for analysis_type, analyzer in self.analyzers.items():
                logger.info(f"포괄적 분석 실행 중: {analysis_type}")
                result = self.run_analysis(analysis_type, data)
                if result:
                    results[analysis_type] = result
            
            logger.info(f"포괄적 분석 완료: {len(results)}개 분석 완료")
            return results
        
        except Exception as e:
            logger.error(f"포괄적 분석 실패: {str(e)}")
            return {}
    
    def get_analysis_summary(self) -> Dict[str, Any]:
        """분석 요약 정보 반환"""
        try:
            if not self.analysis_history:
                return {"message": "분석 히스토리가 없습니다"}
            
            summary = {
                "total_analyses": len(self.analysis_history),
                "analysis_types": {},
                "recent_analyses": [],
                "overall_confidence": 0.0
            }
            
            # 분석 유형별 통계
            for result in self.analysis_history:
                analysis_type = result.analysis_type
                if analysis_type not in summary["analysis_types"]:
                    summary["analysis_types"][analysis_type] = {
                        "count": 0,
                        "avg_confidence": 0.0
                    }
                
                summary["analysis_types"][analysis_type]["count"] += 1
                summary["analysis_types"][analysis_type]["avg_confidence"] += result.confidence_score
            
            # 평균 신뢰도 계산
            for analysis_type in summary["analysis_types"]:
                count = summary["analysis_types"][analysis_type]["count"]
                total_confidence = summary["analysis_types"][analysis_type]["avg_confidence"]
                summary["analysis_types"][analysis_type]["avg_confidence"] = total_confidence / count
            
            # 최근 분석 결과
            recent_results = sorted(self.analysis_history, key=lambda x: x.timestamp, reverse=True)[:5]
            summary["recent_analyses"] = [
                {
                    "analysis_id": result.analysis_id,
                    "analysis_type": result.analysis_type,
                    "timestamp": result.timestamp.isoformat(),
                    "confidence_score": result.confidence_score
                }
                for result in recent_results
            ]
            
            # 전체 평균 신뢰도
            total_confidence = sum(result.confidence_score for result in self.analysis_history)
            summary["overall_confidence"] = total_confidence / len(self.analysis_history)
            
            return summary
        
        except Exception as e:
            logger.error(f"분석 요약 생성 실패: {str(e)}")
            return {"error": str(e)}
    
    def export_analysis_report(self, analysis_id: str, filepath: str = None) -> str:
        """분석 보고서 내보내기"""
        try:
            # 분석 결과 찾기
            result = next((r for r in self.analysis_history if r.analysis_id == analysis_id), None)
            if not result:
                raise ValueError(f"분석 결과를 찾을 수 없습니다: {analysis_id}")
            
            if not filepath:
                filepath = f"analysis_report_{analysis_id}.json"
            
            # 보고서 데이터 구성
            report_data = {
                "analysis_info": {
                    "analysis_id": result.analysis_id,
                    "analysis_type": result.analysis_type,
                    "timestamp": result.timestamp.isoformat(),
                    "confidence_score": result.confidence_score
                },
                "summary": result.summary,
                "detailed_results": result.detailed_results,
                "recommendations": result.recommendations,
                "visualizations": result.visualizations
            }
            
            # JSON 파일로 저장
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(report_data, f, ensure_ascii=False, indent=2)
            
            logger.info(f"분석 보고서 내보내기 완료: {filepath}")
            return filepath
        
        except Exception as e:
            logger.error(f"분석 보고서 내보내기 실패: {str(e)}")
            raise

# 사용 예시
if __name__ == "__main__":
    # 고급 분석 엔진 생성
    analytics_engine = AdvancedAnalyticsEngine()
    
    # 샘플 데이터
    sample_data = {
        "performance_history": [
            {"timestamp": "2024-01-01", "accuracy": 0.85, "f1_score": 0.82},
            {"timestamp": "2024-01-02", "accuracy": 0.87, "f1_score": 0.84},
            {"timestamp": "2024-01-03", "accuracy": 0.86, "f1_score": 0.83},
            {"timestamp": "2024-01-04", "accuracy": 0.88, "f1_score": 0.85},
            {"timestamp": "2024-01-05", "accuracy": 0.89, "f1_score": 0.86}
        ],
        "integration_history": [
            {"phase": "phase1", "execution_time": 45, "status": "completed", "memory_usage": 512},
            {"phase": "phase2", "execution_time": 120, "status": "completed", "memory_usage": 1024},
            {"phase": "phase1", "execution_time": 42, "status": "completed", "memory_usage": 498},
            {"phase": "phase2", "execution_time": 118, "status": "completed", "memory_usage": 1012}
        ]
    }
    
    # 성능 트렌드 분석
    print("=== 성능 트렌드 분석 ===")
    trend_result = analytics_engine.run_analysis("performance_trend", sample_data)
    if trend_result:
        print(f"분석 ID: {trend_result.analysis_id}")
        print(f"신뢰도 점수: {trend_result.confidence_score}")
        print(f"권장사항: {trend_result.recommendations}")
    
    # 통합 효율성 분석
    print("\n=== 통합 효율성 분석 ===")
    efficiency_result = analytics_engine.run_analysis("integration_efficiency", sample_data)
    if efficiency_result:
        print(f"분석 ID: {efficiency_result.analysis_id}")
        print(f"신뢰도 점수: {efficiency_result.confidence_score}")
        print(f"권장사항: {efficiency_result.recommendations}")
    
    # 분석 요약
    print("\n=== 분석 요약 ===")
    summary = analytics_engine.get_analysis_summary()
    print(f"총 분석 수: {summary['total_analyses']}")
    print(f"전체 평균 신뢰도: {summary['overall_confidence']:.2f}")
