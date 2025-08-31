"""
📊 DuRi 메타 평가 대시보드 시스템
목표: 각 루프의 진화, 향상된 점수, 개선율, 실패율 등을 대시보드 형태로 시각화하고, 단계별로 비교 평가할 수 있는 시스템
"""
import logging
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum
from datetime import datetime, timedelta
import json
import random
import math

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MetricType(Enum):
    """메트릭 유형"""
    EVOLUTION_SCORE = "evolution_score"
    IMPROVEMENT_RATE = "improvement_rate"
    SUCCESS_RATE = "success_rate"
    FAILURE_RATE = "failure_rate"
    PERFORMANCE_SCORE = "performance_score"

class DashboardView(Enum):
    """대시보드 뷰"""
    OVERVIEW = "overview"
    DETAILED = "detailed"
    COMPARATIVE = "comparative"
    TREND = "trend"

@dataclass
class LoopMetric:
    """루프 메트릭"""
    loop_id: str
    loop_name: str
    phase: str
    evolution_score: float
    improvement_rate: float
    success_rate: float
    failure_rate: float
    performance_score: float
    timestamp: datetime

@dataclass
class PhaseComparison:
    """단계 비교"""
    comparison_id: str
    phase1: str
    phase2: str
    metric_type: MetricType
    phase1_value: float
    phase2_value: float
    improvement: float
    comparison_date: datetime

@dataclass
class TrendAnalysis:
    """트렌드 분석"""
    trend_id: str
    metric_type: MetricType
    time_period: str
    start_value: float
    end_value: float
    trend_direction: str
    growth_rate: float
    analyzed_at: datetime

@dataclass
class DashboardReport:
    """대시보드 리포트"""
    report_id: str
    report_type: DashboardView
    metrics: List[LoopMetric]
    comparisons: List[PhaseComparison]
    trends: List[TrendAnalysis]
    summary: Dict[str, Any]
    generated_at: datetime

class MetaEvalDashboard:
    def __init__(self):
        self.loop_metrics = []
        self.phase_comparisons = []
        self.trend_analyses = []
        self.dashboard_reports = []
        self.visualization_data = {}
        
        # Phase 24 시스템들
        self.evolution_system = None
        self.consciousness_system = None
        self.validation_bridge = None
        self.test_generator = None
        self.refactor_agent = None

    def initialize_phase_24_integration(self):
        """Phase 24 시스템들과 통합"""
        try:
            import sys
            sys.path.append('.')
            from duri_brain.thinking.phase_24_self_evolution_ai import get_phase24_system
            from duri_brain.thinking.phase_23_enhanced import get_phase23_enhanced_system
            from duri_brain.thinking.external_validation_bridge import get_external_validation_bridge
            from duri_brain.thinking.unit_test_generator import get_unit_test_generator
            from duri_brain.thinking.code_refactor_agent import get_code_refactor_agent
            
            self.evolution_system = get_phase24_system()
            self.consciousness_system = get_phase23_enhanced_system()
            self.validation_bridge = get_external_validation_bridge()
            self.test_generator = get_unit_test_generator()
            self.refactor_agent = get_code_refactor_agent()
            
            logger.info("✅ Phase 24 시스템들과 통합 완료")
            return True
        except Exception as e:
            logger.error(f"❌ Phase 24 시스템 통합 실패: {e}")
            return False

    def collect_loop_metrics(self, loop_name: str, phase: str) -> LoopMetric:
        """루프 메트릭 수집"""
        logger.info(f"📊 루프 메트릭 수집: {loop_name}")
        
        # 메트릭 계산 (시뮬레이션)
        evolution_score = random.uniform(0.6, 0.95)
        improvement_rate = random.uniform(0.05, 0.25)
        success_rate = random.uniform(0.7, 0.95)
        failure_rate = 1.0 - success_rate
        performance_score = random.uniform(0.65, 0.9)
        
        metric = LoopMetric(
            loop_id=f"loop_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            loop_name=loop_name,
            phase=phase,
            evolution_score=evolution_score,
            improvement_rate=improvement_rate,
            success_rate=success_rate,
            failure_rate=failure_rate,
            performance_score=performance_score,
            timestamp=datetime.now()
        )
        
        self.loop_metrics.append(metric)
        logger.info(f"✅ 루프 메트릭 수집 완료: {metric.loop_id}")
        return metric

    def compare_phases(self, phase1: str, phase2: str, metric_type: MetricType) -> PhaseComparison:
        """단계 비교"""
        logger.info(f"📈 단계 비교: {phase1} vs {phase2}")
        
        # 각 단계의 메트릭 찾기
        phase1_metrics = [m for m in self.loop_metrics if m.phase == phase1]
        phase2_metrics = [m for m in self.loop_metrics if m.phase == phase2]
        
        if not phase1_metrics or not phase2_metrics:
            # 시뮬레이션 데이터 생성
            phase1_value = random.uniform(0.6, 0.8)
            phase2_value = random.uniform(0.7, 0.9)
        else:
            # 실제 메트릭 값 사용
            if metric_type == MetricType.EVOLUTION_SCORE:
                phase1_value = sum(m.evolution_score for m in phase1_metrics) / len(phase1_metrics)
                phase2_value = sum(m.evolution_score for m in phase2_metrics) / len(phase2_metrics)
            elif metric_type == MetricType.IMPROVEMENT_RATE:
                phase1_value = sum(m.improvement_rate for m in phase1_metrics) / len(phase1_metrics)
                phase2_value = sum(m.improvement_rate for m in phase2_metrics) / len(phase2_metrics)
            elif metric_type == MetricType.SUCCESS_RATE:
                phase1_value = sum(m.success_rate for m in phase1_metrics) / len(phase1_metrics)
                phase2_value = sum(m.success_rate for m in phase2_metrics) / len(phase2_metrics)
            else:
                phase1_value = random.uniform(0.6, 0.8)
                phase2_value = random.uniform(0.7, 0.9)
        
        improvement = phase2_value - phase1_value
        
        comparison = PhaseComparison(
            comparison_id=f"comp_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            phase1=phase1,
            phase2=phase2,
            metric_type=metric_type,
            phase1_value=phase1_value,
            phase2_value=phase2_value,
            improvement=improvement,
            comparison_date=datetime.now()
        )
        
        self.phase_comparisons.append(comparison)
        logger.info(f"✅ 단계 비교 완료: 개선율 {improvement:.3f}")
        return comparison

    def analyze_trends(self, metric_type: MetricType, time_period: str = "recent") -> TrendAnalysis:
        """트렌드 분석"""
        logger.info(f"📈 트렌드 분석: {metric_type.value}")
        
        # 최근 메트릭들 수집
        recent_metrics = sorted(self.loop_metrics, key=lambda x: x.timestamp)[-10:]
        
        if len(recent_metrics) < 2:
            # 시뮬레이션 데이터 생성
            start_value = random.uniform(0.6, 0.8)
            end_value = random.uniform(0.7, 0.9)
        else:
            # 실제 메트릭 값 사용
            if metric_type == MetricType.EVOLUTION_SCORE:
                start_value = recent_metrics[0].evolution_score
                end_value = recent_metrics[-1].evolution_score
            elif metric_type == MetricType.IMPROVEMENT_RATE:
                start_value = recent_metrics[0].improvement_rate
                end_value = recent_metrics[-1].improvement_rate
            elif metric_type == MetricType.SUCCESS_RATE:
                start_value = recent_metrics[0].success_rate
                end_value = recent_metrics[-1].success_rate
            else:
                start_value = random.uniform(0.6, 0.8)
                end_value = random.uniform(0.7, 0.9)
        
        trend_direction = "상승" if end_value > start_value else "하락" if end_value < start_value else "유지"
        growth_rate = (end_value - start_value) / start_value if start_value > 0 else 0.0
        
        trend = TrendAnalysis(
            trend_id=f"trend_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            metric_type=metric_type,
            time_period=time_period,
            start_value=start_value,
            end_value=end_value,
            trend_direction=trend_direction,
            growth_rate=growth_rate,
            analyzed_at=datetime.now()
        )
        
        self.trend_analyses.append(trend)
        logger.info(f"✅ 트렌드 분석 완료: {trend_direction} ({growth_rate:.2%})")
        return trend

    def generate_overview_dashboard(self) -> DashboardReport:
        """개요 대시보드 생성"""
        logger.info("📊 개요 대시보드 생성")
        
        # 주요 메트릭 수집
        total_loops = len(self.loop_metrics)
        avg_evolution_score = sum(m.evolution_score for m in self.loop_metrics) / total_loops if total_loops > 0 else 0.0
        avg_success_rate = sum(m.success_rate for m in self.loop_metrics) / total_loops if total_loops > 0 else 0.0
        avg_improvement_rate = sum(m.improvement_rate for m in self.loop_metrics) / total_loops if total_loops > 0 else 0.0
        
        summary = {
            "total_loops": total_loops,
            "average_evolution_score": avg_evolution_score,
            "average_success_rate": avg_success_rate,
            "average_improvement_rate": avg_improvement_rate,
            "overall_performance": "우수" if avg_evolution_score > 0.8 else "양호" if avg_evolution_score > 0.6 else "개선 필요"
        }
        
        report = DashboardReport(
            report_id=f"overview_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            report_type=DashboardView.OVERVIEW,
            metrics=self.loop_metrics,
            comparisons=self.phase_comparisons,
            trends=self.trend_analyses,
            summary=summary,
            generated_at=datetime.now()
        )
        
        self.dashboard_reports.append(report)
        logger.info(f"✅ 개요 대시보드 생성 완료: {report.report_id}")
        return report

    def generate_detailed_dashboard(self) -> DashboardReport:
        """상세 대시보드 생성"""
        logger.info("📊 상세 대시보드 생성")
        
        # 상세 분석
        phase_breakdown = {}
        for metric in self.loop_metrics:
            if metric.phase not in phase_breakdown:
                phase_breakdown[metric.phase] = []
            phase_breakdown[metric.phase].append(metric)
        
        detailed_summary = {
            "phase_breakdown": {phase: len(metrics) for phase, metrics in phase_breakdown.items()},
            "best_performing_phase": max(phase_breakdown.keys(), key=lambda p: sum(m.evolution_score for m in phase_breakdown[p]) / len(phase_breakdown[p])) if phase_breakdown else "N/A",
            "total_comparisons": len(self.phase_comparisons),
            "total_trends": len(self.trend_analyses)
        }
        
        report = DashboardReport(
            report_id=f"detailed_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            report_type=DashboardView.DETAILED,
            metrics=self.loop_metrics,
            comparisons=self.phase_comparisons,
            trends=self.trend_analyses,
            summary=detailed_summary,
            generated_at=datetime.now()
        )
        
        self.dashboard_reports.append(report)
        logger.info(f"✅ 상세 대시보드 생성 완료: {report.report_id}")
        return report

    def generate_comparative_dashboard(self) -> DashboardReport:
        """비교 대시보드 생성"""
        logger.info("📊 비교 대시보드 생성")
        
        # 비교 분석
        positive_comparisons = [c for c in self.phase_comparisons if c.improvement > 0]
        negative_comparisons = [c for c in self.phase_comparisons if c.improvement < 0]
        
        comparative_summary = {
            "total_comparisons": len(self.phase_comparisons),
            "positive_comparisons": len(positive_comparisons),
            "negative_comparisons": len(negative_comparisons),
            "average_improvement": sum(c.improvement for c in self.phase_comparisons) / len(self.phase_comparisons) if self.phase_comparisons else 0.0,
            "best_improvement": max((c.improvement for c in self.phase_comparisons), default=0.0)
        }
        
        report = DashboardReport(
            report_id=f"comparative_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            report_type=DashboardView.COMPARATIVE,
            metrics=self.loop_metrics,
            comparisons=self.phase_comparisons,
            trends=self.trend_analyses,
            summary=comparative_summary,
            generated_at=datetime.now()
        )
        
        self.dashboard_reports.append(report)
        logger.info(f"✅ 비교 대시보드 생성 완료: {report.report_id}")
        return report

    def generate_trend_dashboard(self) -> DashboardReport:
        """트렌드 대시보드 생성"""
        logger.info("📊 트렌드 대시보드 생성")
        
        # 트렌드 분석
        upward_trends = [t for t in self.trend_analyses if t.trend_direction == "상승"]
        downward_trends = [t for t in self.trend_analyses if t.trend_direction == "하락"]
        
        trend_summary = {
            "total_trends": len(self.trend_analyses),
            "upward_trends": len(upward_trends),
            "downward_trends": len(downward_trends),
            "average_growth_rate": sum(t.growth_rate for t in self.trend_analyses) / len(self.trend_analyses) if self.trend_analyses else 0.0,
            "strongest_growth": max((t.growth_rate for t in self.trend_analyses), default=0.0)
        }
        
        report = DashboardReport(
            report_id=f"trend_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            report_type=DashboardView.TREND,
            metrics=self.loop_metrics,
            comparisons=self.phase_comparisons,
            trends=self.trend_analyses,
            summary=trend_summary,
            generated_at=datetime.now()
        )
        
        self.dashboard_reports.append(report)
        logger.info(f"✅ 트렌드 대시보드 생성 완료: {report.report_id}")
        return report

    def export_visualization_data(self) -> Dict[str, Any]:
        """시각화 데이터 내보내기"""
        logger.info("📊 시각화 데이터 내보내기")
        
        # 차트용 데이터 구조
        chart_data = {
            "evolution_scores": [m.evolution_score for m in self.loop_metrics],
            "improvement_rates": [m.improvement_rate for m in self.loop_metrics],
            "success_rates": [m.success_rate for m in self.loop_metrics],
            "failure_rates": [m.failure_rate for m in self.loop_metrics],
            "performance_scores": [m.performance_score for m in self.loop_metrics],
            "timestamps": [m.timestamp.isoformat() for m in self.loop_metrics],
            "phases": [m.phase for m in self.loop_metrics],
            "loop_names": [m.loop_name for m in self.loop_metrics]
        }
        
        self.visualization_data = chart_data
        logger.info("✅ 시각화 데이터 내보내기 완료")
        return chart_data

    def get_dashboard_status(self) -> Dict[str, Any]:
        """대시보드 상태 확인"""
        total_metrics = len(self.loop_metrics)
        total_comparisons = len(self.phase_comparisons)
        total_trends = len(self.trend_analyses)
        total_reports = len(self.dashboard_reports)
        
        if total_metrics > 0:
            avg_evolution_score = sum(m.evolution_score for m in self.loop_metrics) / total_metrics
            avg_success_rate = sum(m.success_rate for m in self.loop_metrics) / total_metrics
        else:
            avg_evolution_score = 0.0
            avg_success_rate = 0.0
        
        status = {
            "system": "Meta Evaluation Dashboard",
            "total_metrics": total_metrics,
            "total_comparisons": total_comparisons,
            "total_trends": total_trends,
            "total_reports": total_reports,
            "average_evolution_score": avg_evolution_score,
            "average_success_rate": avg_success_rate,
            "dashboard_health": "healthy" if total_metrics > 0 else "no_data"
        }
        
        return status

def get_meta_eval_dashboard():
    """메타 평가 대시보드 시스템 인스턴스 반환"""
    return MetaEvalDashboard()

if __name__ == "__main__":
    # 메타 평가 대시보드 시스템 테스트
    dashboard = get_meta_eval_dashboard()
    
    if dashboard.initialize_phase_24_integration():
        logger.info("🚀 메타 평가 대시보드 시스템 테스트 시작")
        
        # 루프 메트릭 수집
        dashboard.collect_loop_metrics("Evolution Loop", "Phase 24")
        dashboard.collect_loop_metrics("Consciousness Loop", "Phase 23")
        dashboard.collect_loop_metrics("Validation Loop", "Phase 24")
        dashboard.collect_loop_metrics("Test Loop", "Phase 24")
        
        # 단계 비교
        dashboard.compare_phases("Phase 23", "Phase 24", MetricType.EVOLUTION_SCORE)
        dashboard.compare_phases("Phase 23", "Phase 24", MetricType.SUCCESS_RATE)
        
        # 트렌드 분석
        dashboard.analyze_trends(MetricType.EVOLUTION_SCORE)
        dashboard.analyze_trends(MetricType.IMPROVEMENT_RATE)
        
        # 대시보드 생성
        overview = dashboard.generate_overview_dashboard()
        detailed = dashboard.generate_detailed_dashboard()
        comparative = dashboard.generate_comparative_dashboard()
        trend = dashboard.generate_trend_dashboard()
        
        # 시각화 데이터 내보내기
        chart_data = dashboard.export_visualization_data()
        
        # 최종 상태 확인
        status = dashboard.get_dashboard_status()
        logger.info(f"평균 진화 점수: {status['average_evolution_score']:.3f}")
        logger.info(f"평균 성공률: {status['average_success_rate']:.3f}")
        
        logger.info("✅ 메타 평가 대시보드 시스템 테스트 완료")
    else:
        logger.error("❌ 메타 평가 대시보드 시스템 초기화 실패") 