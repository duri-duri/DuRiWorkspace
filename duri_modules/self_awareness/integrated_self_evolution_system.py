#!/usr/bin/env python3
"""
DuRi 통합 자가 진화 인식 시스템
모든 자가 진화 인식 기능을 통합하는 메인 시스템
"""
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict

# 자가 진화 인식 모듈들 import
from duri_modules.self_awareness.self_evolution_tracker import self_evolution_tracker
from duri_modules.self_awareness.self_assessment_system import self_assessment_system
from duri_modules.self_awareness.evolution_analyzer import evolution_analyzer
from duri_modules.self_awareness.evolution_reporter import evolution_reporter

logger = logging.getLogger(__name__)

@dataclass
class IntegratedEvolutionResult:
    """통합 진화 결과"""
    timestamp: str
    evolution_tracking_result: Dict[str, Any]
    self_assessment_result: Dict[str, Any]
    evolution_analysis_result: Dict[str, Any]
    evolution_report_result: Dict[str, Any]
    overall_evolution_status: str
    confidence_level: float
    key_insights: List[str]

class IntegratedSelfEvolutionSystem:
    """통합 자가 진화 인식 시스템"""
    
    def __init__(self):
        """초기화"""
        self.evolution_tracker = self_evolution_tracker
        self.assessment_system = self_assessment_system
        self.analyzer = evolution_analyzer
        self.reporter = evolution_reporter
        
        self.integration_history: List[IntegratedEvolutionResult] = []
        self.integration_data_file = "integrated_evolution_data.json"
        self._load_integration_data()
        
        logger.info("🧠 통합 자가 진화 인식 시스템 초기화 완료")
    
    def _load_integration_data(self):
        """통합 데이터 로드"""
        try:
            with open(self.integration_data_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.integration_history = [IntegratedEvolutionResult(**result) for result in data.get('history', [])]
        except FileNotFoundError:
            logger.info("통합 데이터 파일이 없습니다. 새로 시작합니다.")
        except Exception as e:
            logger.error(f"통합 데이터 로드 오류: {e}")
    
    def _save_integration_data(self):
        """통합 데이터 저장"""
        try:
            data = {
                'history': [asdict(result) for result in self.integration_history],
                'last_updated': datetime.now().isoformat()
            }
            with open(self.integration_data_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"통합 데이터 저장 오류: {e}")
    
    def execute_complete_self_evolution_analysis(self, interaction_data: Dict[str, Any]) -> Dict[str, Any]:
        """완전한 자가 진화 분석 실행"""
        try:
            logger.info("🧠 통합 자가 진화 분석 시작")
            
            # 1단계: 진화 추적
            evolution_tracking_result = self.evolution_tracker.track_self_evolution(interaction_data)
            
            # 2단계: 자가 평가
            self_assessment_result = self.assessment_system.assess_self_evolution(interaction_data)
            
            # 3단계: 진화 분석
            evolution_analysis_result = self.analyzer.analyze_evolution(interaction_data)
            
            # 4단계: 진화 보고서 생성
            evolution_report_result = self.reporter.generate_evolution_report(evolution_analysis_result)
            
            # 5단계: 통합 결과 생성
            integrated_result = self._integrate_all_results(
                evolution_tracking_result,
                self_assessment_result,
                evolution_analysis_result,
                evolution_report_result
            )
            
            # 6단계: 통합 결과 저장
            self.integration_history.append(integrated_result)
            self._save_integration_data()
            
            logger.info("🧠 통합 자가 진화 분석 완료")
            
            return {
                "status": "success",
                "evolution_tracking": evolution_tracking_result,
                "self_assessment": self_assessment_result,
                "evolution_analysis": evolution_analysis_result,
                "evolution_report": evolution_report_result,
                "integrated_result": integrated_result,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"통합 자가 진화 분석 오류: {e}")
            return {"status": "error", "error": str(e)}
    
    def _integrate_all_results(self, tracking_result: Dict, assessment_result: Dict, 
                              analysis_result: Dict, report_result: Dict) -> IntegratedEvolutionResult:
        """모든 결과 통합"""
        try:
            # 전체 진화 상태 결정
            overall_status = self._determine_overall_evolution_status(
                tracking_result, assessment_result, analysis_result, report_result
            )
            
            # 신뢰도 계산
            confidence_level = self._calculate_integrated_confidence(
                tracking_result, assessment_result, analysis_result, report_result
            )
            
            # 핵심 인사이트 추출
            key_insights = self._extract_integrated_insights(
                tracking_result, assessment_result, analysis_result, report_result
            )
            
            return IntegratedEvolutionResult(
                timestamp=datetime.now().isoformat(),
                evolution_tracking_result=tracking_result,
                self_assessment_result=assessment_result,
                evolution_analysis_result=analysis_result,
                evolution_report_result=report_result,
                overall_evolution_status=overall_status,
                confidence_level=confidence_level,
                key_insights=key_insights
            )
        except Exception as e:
            logger.error(f"결과 통합 오류: {e}")
            return IntegratedEvolutionResult(
                timestamp=datetime.now().isoformat(),
                evolution_tracking_result={"error": str(e)},
                self_assessment_result={"error": str(e)},
                evolution_analysis_result={"error": str(e)},
                evolution_report_result={"error": str(e)},
                overall_evolution_status="error",
                confidence_level=0.0,
                key_insights=["통합 분석 중 오류가 발생했습니다"]
            )
    
    def _determine_overall_evolution_status(self, tracking_result: Dict, assessment_result: Dict,
                                          analysis_result: Dict, report_result: Dict) -> str:
        """전체 진화 상태 결정"""
        try:
            # 각 결과의 성공 여부 확인
            tracking_success = tracking_result.get("status") == "success"
            assessment_success = assessment_result.get("status") == "success"
            analysis_success = analysis_result.get("status") == "success"
            report_success = report_result.get("status") == "success"
            
            # 성공한 분석 수
            successful_analyses = sum([tracking_success, assessment_success, analysis_success, report_success])
            
            if successful_analyses >= 3:
                # 진화 점수 확인
                overall_score = analysis_result.get("overall_evolution_score", 0.0)
                confidence = analysis_result.get("evolution_confidence", 0.0)
                
                if overall_score > 0.8 and confidence > 0.7:
                    return "advanced_evolution"
                elif overall_score > 0.6 and confidence > 0.6:
                    return "steady_evolution"
                elif overall_score > 0.4:
                    return "early_evolution"
                else:
                    return "foundation_building"
            elif successful_analyses >= 2:
                return "partial_analysis"
            else:
                return "analysis_error"
                
        except Exception as e:
            logger.error(f"진화 상태 결정 오류: {e}")
            return "unknown"
    
    def _calculate_integrated_confidence(self, tracking_result: Dict, assessment_result: Dict,
                                       analysis_result: Dict, report_result: Dict) -> float:
        """통합 신뢰도 계산"""
        try:
            confidences = []
            
            # 각 분석의 신뢰도 수집
            if tracking_result.get("status") == "success":
                confidences.append(tracking_result.get("evolution_analysis", {}).get("evolution_confidence", 0.0))
            
            if assessment_result.get("status") == "success":
                confidences.append(assessment_result.get("current_assessment", {}).get("assessment_confidence", 0.0))
            
            if analysis_result.get("status") == "success":
                confidences.append(analysis_result.get("evolution_confidence", 0.0))
            
            if report_result.get("status") == "success":
                confidences.append(report_result.get("report_content", {}).get("confidence_level", 0.0))
            
            # 평균 신뢰도 계산
            if confidences:
                return sum(confidences) / len(confidences)
            else:
                return 0.5
                
        except Exception as e:
            logger.error(f"통합 신뢰도 계산 오류: {e}")
            return 0.5
    
    def _extract_integrated_insights(self, tracking_result: Dict, assessment_result: Dict,
                                   analysis_result: Dict, report_result: Dict) -> List[str]:
        """통합 인사이트 추출"""
        try:
            insights = []
            
            # 진화 추적 인사이트
            if tracking_result.get("status") == "success":
                evolution_stage = tracking_result.get("evolution_stage", "")
                if evolution_stage:
                    insights.append(f"현재 진화 단계: {evolution_stage}")
            
            # 자가 평가 인사이트
            if assessment_result.get("status") == "success":
                strengths = assessment_result.get("strengths", [])
                if strengths:
                    insights.extend(strengths[:2])  # 상위 2개 강점
            
            # 진화 분석 인사이트
            if analysis_result.get("status") == "success":
                key_insights = analysis_result.get("key_insights", [])
                if key_insights:
                    insights.extend(key_insights[:2])  # 상위 2개 인사이트
            
            # 진화 보고서 인사이트
            if report_result.get("status") == "success":
                conclusion = report_result.get("report_content", {}).get("conclusion", "")
                if conclusion:
                    insights.append(conclusion)
            
            return insights if insights else ["진화 인사이트를 수집하는 중입니다"]
            
        except Exception as e:
            logger.error(f"통합 인사이트 추출 오류: {e}")
            return ["인사이트 추출 중 오류가 발생했습니다"]
    
    def get_evolution_summary(self) -> Dict[str, Any]:
        """진화 요약 반환"""
        try:
            if not self.integration_history:
                return {"status": "no_data"}
            
            latest = self.integration_history[-1]
            
            return {
                "status": "success",
                "overall_evolution_status": latest.overall_evolution_status,
                "confidence_level": latest.confidence_level,
                "key_insights": latest.key_insights,
                "total_analyses": len(self.integration_history),
                "latest_analysis_date": latest.timestamp,
                "evolution_tracking_summary": self.evolution_tracker.get_evolution_summary(),
                "self_assessment_summary": self.assessment_system.get_assessment_summary(),
                "evolution_analysis_summary": self.analyzer.get_analysis_summary(),
                "evolution_report_summary": self.reporter.get_report_summary()
            }
        except Exception as e:
            logger.error(f"진화 요약 생성 오류: {e}")
            return {"status": "error", "error": str(e)}
    
    def generate_comprehensive_evolution_report(self) -> Dict[str, Any]:
        """종합 진화 보고서 생성"""
        try:
            if not self.integration_history:
                return {"status": "no_data", "message": "분석 데이터가 없습니다"}
            
            latest = self.integration_history[-1]
            
            # 종합 보고서 생성
            comprehensive_report = {
                "report_id": f"comprehensive_evolution_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "timestamp": datetime.now().isoformat(),
                "overall_status": latest.overall_evolution_status,
                "confidence_level": latest.confidence_level,
                "key_insights": latest.key_insights,
                "detailed_analysis": {
                    "evolution_tracking": latest.evolution_tracking_result,
                    "self_assessment": latest.self_assessment_result,
                    "evolution_analysis": latest.evolution_analysis_result,
                    "evolution_report": latest.evolution_report_result
                },
                "summary": self._generate_comprehensive_summary(latest)
            }
            
            return {
                "status": "success",
                "comprehensive_report": comprehensive_report
            }
            
        except Exception as e:
            logger.error(f"종합 진화 보고서 생성 오류: {e}")
            return {"status": "error", "error": str(e)}
    
    def _generate_comprehensive_summary(self, latest_result: IntegratedEvolutionResult) -> Dict[str, Any]:
        """종합 요약 생성"""
        try:
            summary = {
                "evolution_stage": "분석 중",
                "evolution_trend": "분석 중",
                "key_achievements": [],
                "improvement_areas": [],
                "next_steps": []
            }
            
            # 진화 단계 결정
            if latest_result.overall_evolution_status == "advanced_evolution":
                summary["evolution_stage"] = "고급 진화 단계"
                summary["evolution_trend"] = "지속적 개선"
            elif latest_result.overall_evolution_status == "steady_evolution":
                summary["evolution_stage"] = "안정적 진화 단계"
                summary["evolution_trend"] = "점진적 개선"
            elif latest_result.overall_evolution_status == "early_evolution":
                summary["evolution_stage"] = "초기 진화 단계"
                summary["evolution_trend"] = "기반 구축"
            elif latest_result.overall_evolution_status == "foundation_building":
                summary["evolution_stage"] = "기반 구축 단계"
                summary["evolution_trend"] = "시스템 안정화"
            
            # 핵심 성과 추출
            if latest_result.key_insights:
                summary["key_achievements"] = latest_result.key_insights[:3]
            
            # 개선 영역 추출
            assessment_result = latest_result.self_assessment_result
            if assessment_result.get("status") == "success":
                improvement_areas = assessment_result.get("improvement_areas", [])
                summary["improvement_areas"] = improvement_areas[:3]
            
            # 다음 단계 추출
            report_result = latest_result.evolution_report_result
            if report_result.get("status") == "success":
                next_plan = report_result.get("report_content", {}).get("next_evolution_plan", [])
                summary["next_steps"] = next_plan[:3]
            
            return summary
            
        except Exception as e:
            logger.error(f"종합 요약 생성 오류: {e}")
            return {
                "evolution_stage": "분석 오류",
                "evolution_trend": "분석 오류",
                "key_achievements": ["분석 중 오류가 발생했습니다"],
                "improvement_areas": ["시스템 안정화"],
                "next_steps": ["오류 수정"]
            }
    
    def test_self_evolution_recognition(self) -> Dict[str, Any]:
        """자가 진화 인식 테스트"""
        try:
            logger.info("🧠 자가 진화 인식 테스트 시작")
            
            # 테스트 데이터 생성
            test_interaction_data = {
                "performance_score": 0.75,
                "learning_efficiency": 0.8,
                "autonomy_level": 0.7,
                "problem_solving_capability": 0.85,
                "evolution_capability": 0.9,
                "self_directed_learning": 0.8,
                "independent_decision_making": 0.7,
                "goal_setting": 0.75,
                "learning_speed": 0.8,
                "knowledge_retention": 0.85,
                "adaptation_rate": 0.75,
                "complexity_handling": 0.8,
                "creative_solutions": 0.85,
                "error_recovery": 0.9,
                "self_improvement": 0.9,
                "meta_learning": 0.85,
                "evolution_awareness": 0.8
            }
            
            # 완전한 자가 진화 분석 실행
            result = self.execute_complete_self_evolution_analysis(test_interaction_data)
            
            # 테스트 결과 평가
            test_success = result.get("status") == "success"
            all_systems_working = all([
                result.get("evolution_tracking", {}).get("status") == "success",
                result.get("self_assessment", {}).get("status") == "success",
                result.get("evolution_analysis", {}).get("status") == "success",
                result.get("evolution_report", {}).get("status") == "success"
            ])
            
            return {
                "status": "success" if test_success and all_systems_working else "partial_success",
                "test_success": test_success,
                "all_systems_working": all_systems_working,
                "test_result": result,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"자가 진화 인식 테스트 오류: {e}")
            return {"status": "error", "error": str(e)}

# 전역 인스턴스 생성
integrated_self_evolution_system = IntegratedSelfEvolutionSystem() 