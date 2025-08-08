#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DuRi 실세계 시나리오 테스트 시스템
의사-환자 상호작용을 중심으로 한 사회적 지능 검증
"""

import asyncio
import json
import time
import logging
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Any, Optional
from enum import Enum

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ScenarioType(Enum):
    """시나리오 유형"""
    DOCTOR_PATIENT = "doctor_patient"
    PARENT_CHILD = "parent_child"
    TEACHER_STUDENT = "teacher_student"
    BOSS_EMPLOYEE = "boss_employee"
    FRIEND_CONFLICT = "friend_conflict"

class EmotionType(Enum):
    """감정 유형"""
    ANXIETY = "anxiety"
    FEAR = "fear"
    ANGER = "anger"
    SADNESS = "sadness"
    CONFUSION = "confusion"
    HOPE = "hope"
    TRUST = "trust"
    DISTRUST = "distrust"

@dataclass
class PatientScenario:
    """환자 시나리오"""
    scenario_id: str
    patient_name: str
    age: int
    condition: str
    emotional_state: EmotionType
    background: str
    current_situation: str
    doctor_response_needed: str
    expected_outcome: str

@dataclass
class DuRiResponse:
    """DuRi 응답"""
    scenario_id: str
    response_text: str
    communication_style: str
    empathy_level: float
    trust_building_strategy: str
    reasoning: str
    confidence_score: float
    processing_time: float

@dataclass
class TestResult:
    """테스트 결과"""
    scenario_id: str
    scenario_type: ScenarioType
    duri_response: DuRiResponse
    evaluation_metrics: Dict[str, float]
    success: bool
    feedback: str
    timestamp: datetime = field(default_factory=datetime.now)

class RealWorldScenarioTest:
    """실세계 시나리오 테스트 시스템"""
    
    def __init__(self):
        self.social_intelligence_system = None
        self.test_results: List[TestResult] = []
        self.scenarios: Dict[str, PatientScenario] = {}
        
    async def initialize(self):
        """시스템 초기화"""
        try:
            from social_intelligence_system import SocialIntelligenceSystem
            self.social_intelligence_system = SocialIntelligenceSystem()
            logger.info("✅ 실세계 시나리오 테스트 시스템 초기화 완료")
            return True
        except Exception as e:
            logger.error(f"❌ 시스템 초기화 실패: {e}")
            return False
    
    def load_doctor_patient_scenarios(self):
        """의사-환자 시나리오 로드"""
        self.scenarios = {
            "cancer_diagnosis": PatientScenario(
                scenario_id="cancer_diagnosis",
                patient_name="김영희",
                age=45,
                condition="유방암 2기",
                emotional_state=EmotionType.ANXIETY,
                background="가족 중 암 환자가 있어서 매우 두려워함",
                current_situation="진단 결과를 받기 위해 의사실에 왔음",
                doctor_response_needed="암 진단 결과를 어떻게 전달할 것인가?",
                expected_outcome="환자가 충격을 받지 않고 치료에 동의할 수 있도록"
            ),
            "treatment_refusal": PatientScenario(
                scenario_id="treatment_refusal",
                patient_name="박철수",
                age=62,
                condition="당뇨병 합병증",
                emotional_state=EmotionType.ANGER,
                background="의료진을 신뢰하지 않음, 대체의학 선호",
                current_situation="필수 치료를 거부하고 있음",
                doctor_response_needed="치료의 필요성을 어떻게 설득할 것인가?",
                expected_outcome="환자가 치료의 중요성을 이해하고 동의할 수 있도록"
            ),
            "terminal_care": PatientScenario(
                scenario_id="terminal_care",
                patient_name="이순자",
                age=78,
                condition="말기 폐암",
                emotional_state=EmotionType.FEAR,
                background="가족들과의 마지막 시간을 원함",
                current_situation="생명 연장 치료를 중단하고 싶어함",
                doctor_response_needed="연명치료 중단에 대해 어떻게 상담할 것인가?",
                expected_outcome="환자의 의사를 존중하면서 가족들과의 소통을 돕기"
            ),
            "pediatric_anxiety": PatientScenario(
                scenario_id="pediatric_anxiety",
                patient_name="최민수",
                age=8,
                condition="급성 충수염",
                emotional_state=EmotionType.FEAR,
                background="병원을 매우 두려워하는 아이",
                current_situation="수술이 필요하지만 아이가 겁에 질려있음",
                doctor_response_needed="아이의 두려움을 어떻게 해소할 것인가?",
                expected_outcome="아이가 안심하고 치료를 받을 수 있도록"
            ),
            "family_conflict": PatientScenario(
                scenario_id="family_conflict",
                patient_name="정영수",
                age=55,
                condition="뇌졸중 후유증",
                emotional_state=EmotionType.CONFUSION,
                background="가족들이 치료 방향에 대해 의견이 분분함",
                current_situation="가족들이 의사에게 서로 다른 요구를 하고 있음",
                doctor_response_needed="가족 간 갈등을 어떻게 조율할 것인가?",
                expected_outcome="가족들이 환자를 위한 최선의 선택을 할 수 있도록"
            )
        }
        logger.info(f"✅ {len(self.scenarios)}개의 의사-환자 시나리오 로드 완료")
    
    async def run_scenario_test(self, scenario_id: str) -> TestResult:
        """시나리오 테스트 실행"""
        if scenario_id not in self.scenarios:
            raise ValueError(f"시나리오를 찾을 수 없음: {scenario_id}")
        
        scenario = self.scenarios[scenario_id]
        start_time = time.time()
        
        try:
            # DuRi에게 시나리오 전달
            context_data = {
                "scenario_type": "doctor_patient",
                "patient_name": scenario.patient_name,
                "patient_age": scenario.age,
                "condition": scenario.condition,
                "emotional_state": scenario.emotional_state.value,
                "background": scenario.background,
                "current_situation": scenario.current_situation,
                "doctor_response_needed": scenario.doctor_response_needed,
                "expected_outcome": scenario.expected_outcome,
                "formality": 0.8,  # 의료진-환자 관계는 공식적
                "professionalism": 0.9,  # 높은 전문성 요구
                "participants": ["doctor", scenario.patient_name],
                "interaction_type": "consultation",
                "goals": ["trust_building", "patient_comfort", "treatment_agreement"]
            }
            
            # DuRi 사회적 지능 시스템 호출
            result = await self.social_intelligence_system.process_social_interaction(
                interaction_data={"scenario_id": scenario_id},
                context_data=context_data
            )
            
            processing_time = time.time() - start_time
            
            # DuRi 응답 생성
            duri_response = DuRiResponse(
                scenario_id=scenario_id,
                response_text=self._generate_doctor_response(scenario, result),
                communication_style=result.communication_quality,
                empathy_level=result.empathy_score,
                trust_building_strategy=self._extract_trust_strategy(result),
                reasoning=self._extract_reasoning(result),
                confidence_score=result.context_understanding,
                processing_time=processing_time
            )
            
            # 평가 메트릭 계산
            evaluation_metrics = self._evaluate_response(duri_response, scenario)
            
            # 테스트 결과 생성
            test_result = TestResult(
                scenario_id=scenario_id,
                scenario_type=ScenarioType.DOCTOR_PATIENT,
                duri_response=duri_response,
                evaluation_metrics=evaluation_metrics,
                success=evaluation_metrics["overall_score"] > 0.7,
                feedback=self._generate_feedback(evaluation_metrics)
            )
            
            self.test_results.append(test_result)
            logger.info(f"✅ 시나리오 테스트 완료: {scenario_id}")
            return test_result
            
        except Exception as e:
            logger.error(f"❌ 시나리오 테스트 실패: {scenario_id} - {e}")
            return TestResult(
                scenario_id=scenario_id,
                scenario_type=ScenarioType.DOCTOR_PATIENT,
                duri_response=DuRiResponse(
                    scenario_id=scenario_id,
                    response_text="",
                    communication_style="",
                    empathy_level=0.0,
                    trust_building_strategy="",
                    reasoning="",
                    confidence_score=0.0,
                    processing_time=time.time() - start_time
                ),
                evaluation_metrics={},
                success=False,
                feedback=f"테스트 실패: {e}"
            )
    
    def _generate_doctor_response(self, scenario: PatientScenario, result: Any) -> str:
        """의사 응답 생성"""
        # DuRi의 분석 결과를 바탕으로 의사 응답 생성
        empathy_level = result.empathy_score
        trust_level = result.trust_building
        
        if scenario.emotional_state == EmotionType.ANXIETY:
            if empathy_level > 0.8:
                return f"김영희님, 지금 많이 걱정되시겠어요. 하지만 걱정하지 마세요. 우리가 함께 해결해나갈 수 있습니다. 먼저 진단 결과에 대해 자세히 설명드리겠습니다."
            else:
                return f"진단 결과를 말씀드리겠습니다. 유방암 2기로 확인되었습니다. 치료가 가능한 단계입니다."
        
        elif scenario.emotional_state == EmotionType.ANGER:
            if trust_level > 0.7:
                return f"박철수님, 지금 많이 화가 나시는 것 같습니다. 하지만 당뇨병 합병증은 정말 위험합니다. 다른 방법도 함께 찾아보겠지만, 우선은 기본 치료가 필요합니다."
            else:
                return f"치료를 거부하시는 이유를 이해합니다. 하지만 의학적으로는 치료가 필요합니다."
        
        else:
            return f"{scenario.patient_name}님, {scenario.current_situation}에 대해 이야기해보겠습니다."
    
    def _extract_trust_strategy(self, result: Any) -> str:
        """신뢰 구축 전략 추출"""
        if result.trust_building > 0.8:
            return "고수준 신뢰 구축"
        elif result.trust_building > 0.6:
            return "중간 수준 신뢰 구축"
        else:
            return "기본 신뢰 구축"
    
    def _extract_reasoning(self, result: Any) -> str:
        """판단 근거 추출"""
        insights = result.insights if hasattr(result, 'insights') else []
        if insights:
            return "; ".join(insights[:2])
        return "DuRi의 사회적 지능 분석을 바탕으로 한 판단"
    
    def _evaluate_response(self, response: DuRiResponse, scenario: PatientScenario) -> Dict[str, float]:
        """응답 평가"""
        # 실제 의사 관점에서 평가
        empathy_score = response.empathy_level
        trust_score = response.confidence_score
        communication_score = response.communication_style if isinstance(response.communication_style, (int, float)) else 0.7
        
        # 시나리오별 특화 평가
        scenario_specific_score = self._evaluate_scenario_specific(response, scenario)
        
        overall_score = (empathy_score + trust_score + communication_score + scenario_specific_score) / 4
        
        return {
            "empathy_score": empathy_score,
            "trust_score": trust_score,
            "communication_score": communication_score,
            "scenario_specific_score": scenario_specific_score,
            "overall_score": overall_score,
            "processing_time": response.processing_time
        }
    
    def _evaluate_scenario_specific(self, response: DuRiResponse, scenario: PatientScenario) -> float:
        """시나리오별 특화 평가"""
        if scenario.emotional_state == EmotionType.ANXIETY:
            # 불안한 환자에게는 공감과 안정감 제공이 중요
            return 0.9 if "걱정" in response.response_text and "함께" in response.response_text else 0.6
        
        elif scenario.emotional_state == EmotionType.ANGER:
            # 화난 환자에게는 이해와 대안 제시가 중요
            return 0.9 if "이해" in response.response_text and "대안" in response.response_text else 0.6
        
        elif scenario.emotional_state == EmotionType.FEAR:
            # 두려운 환자에게는 안심과 설명이 중요
            return 0.9 if "안심" in response.response_text or "설명" in response.response_text else 0.6
        
        else:
            return 0.7
    
    def _generate_feedback(self, metrics: Dict[str, float]) -> str:
        """피드백 생성"""
        overall_score = metrics["overall_score"]
        
        if overall_score > 0.8:
            return "우수한 의사-환자 상호작용 응답입니다. 공감과 신뢰 구축이 잘 이루어졌습니다."
        elif overall_score > 0.6:
            return "양호한 응답입니다. 일부 개선 여지가 있습니다."
        else:
            return "개선이 필요한 응답입니다. 공감과 신뢰 구축을 더 강화해야 합니다."
    
    async def run_all_scenarios(self) -> List[TestResult]:
        """모든 시나리오 테스트 실행"""
        logger.info("🚀 모든 의사-환자 시나리오 테스트 시작")
        
        results = []
        for scenario_id in self.scenarios.keys():
            result = await self.run_scenario_test(scenario_id)
            results.append(result)
            await asyncio.sleep(0.1)  # 간격을 두고 실행
        
        logger.info(f"✅ 모든 시나리오 테스트 완료: {len(results)}개")
        return results
    
    def generate_test_report(self) -> Dict[str, Any]:
        """테스트 리포트 생성"""
        if not self.test_results:
            return {"error": "테스트 결과가 없습니다."}
        
        total_tests = len(self.test_results)
        successful_tests = sum(1 for r in self.test_results if r.success)
        avg_overall_score = sum(r.evaluation_metrics.get("overall_score", 0) for r in self.test_results) / total_tests
        avg_processing_time = sum(r.evaluation_metrics.get("processing_time", 0) for r in self.test_results) / total_tests
        
        return {
            "test_summary": {
                "total_scenarios": total_tests,
                "successful_scenarios": successful_tests,
                "success_rate": successful_tests / total_tests * 100,
                "average_overall_score": avg_overall_score,
                "average_processing_time": avg_processing_time
            },
            "scenario_results": [
                {
                    "scenario_id": r.scenario_id,
                    "success": r.success,
                    "overall_score": r.evaluation_metrics.get("overall_score", 0),
                    "empathy_score": r.evaluation_metrics.get("empathy_score", 0),
                    "trust_score": r.evaluation_metrics.get("trust_score", 0),
                    "communication_score": r.evaluation_metrics.get("communication_score", 0),
                    "processing_time": r.evaluation_metrics.get("processing_time", 0),
                    "feedback": r.feedback
                }
                for r in self.test_results
            ],
            "recommendations": self._generate_recommendations()
        }
    
    def _generate_recommendations(self) -> List[str]:
        """개선 권장사항 생성"""
        recommendations = []
        
        avg_empathy = sum(r.evaluation_metrics.get("empathy_score", 0) for r in self.test_results) / len(self.test_results)
        avg_trust = sum(r.evaluation_metrics.get("trust_score", 0) for r in self.test_results) / len(self.test_results)
        
        if avg_empathy < 0.8:
            recommendations.append("공감 능력을 더욱 강화해야 합니다.")
        
        if avg_trust < 0.8:
            recommendations.append("신뢰 구축 전략을 개선해야 합니다.")
        
        if not recommendations:
            recommendations.append("전반적으로 우수한 성능을 보이고 있습니다.")
        
        return recommendations

async def main():
    """메인 실행 함수"""
    print("🏥 DuRi 실세계 의사-환자 시나리오 테스트 시작")
    print("=" * 60)
    
    # 테스트 시스템 초기화
    test_system = RealWorldScenarioTest()
    if not await test_system.initialize():
        print("❌ 시스템 초기화 실패")
        return
    
    # 시나리오 로드
    test_system.load_doctor_patient_scenarios()
    
    # 모든 시나리오 테스트 실행
    results = await test_system.run_all_scenarios()
    
    # 리포트 생성
    report = test_system.generate_test_report()
    
    # 결과 출력
    print("\n📊 테스트 결과 리포트")
    print("=" * 60)
    print(f"총 시나리오: {report['test_summary']['total_scenarios']}개")
    print(f"성공률: {report['test_summary']['success_rate']:.1f}%")
    print(f"평균 종합 점수: {report['test_summary']['average_overall_score']:.2f}")
    print(f"평균 처리 시간: {report['test_summary']['average_processing_time']:.3f}초")
    
    print("\n🎯 개선 권장사항")
    print("=" * 60)
    for rec in report['recommendations']:
        print(f"• {rec}")
    
    print("\n✅ 실세계 시나리오 테스트 완료!")

if __name__ == "__main__":
    asyncio.run(main())
