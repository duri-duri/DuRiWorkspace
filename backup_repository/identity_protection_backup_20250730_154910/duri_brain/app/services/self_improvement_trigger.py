#!/usr/bin/env python3
"""
SelfImprovementTrigger - Phase 12+
자기 개선 트리거 시스템

목적:
- 진화 필요성을 설명 가능한 형태로 판단
- 자기 개선 트리거 생성
- 관리자 보고 형식 제공
"""

import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
from enum import Enum
import json

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TriggerType(Enum):
    """트리거 유형"""
    PERFORMANCE_LIMITATION = "performance_limitation"
    FUNCTIONALITY_GAP = "functionality_gap"
    INTEGRATION_ISSUE = "integration_issue"
    STABILITY_CONCERN = "stability_concern"
    EVOLUTION_OPPORTUNITY = "evolution_opportunity"

class TriggerPriority(Enum):
    """트리거 우선순위"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

@dataclass
class ImprovementTrigger:
    """개선 트리거"""
    id: str
    trigger_type: TriggerType
    priority: TriggerPriority
    description: str
    current_state: str
    target_state: str
    reasoning: str
    evidence: List[str]
    proposed_solutions: List[str]
    estimated_impact: str
    timestamp: datetime

@dataclass
class EvolutionReport:
    """진화 보고서"""
    id: str
    current_phase: int
    target_phase: int
    trigger_analysis: Dict[str, Any]
    decision_rationale: str
    risk_assessment: Dict[str, Any]
    implementation_plan: List[str]
    success_metrics: List[str]
    fallback_plan: List[str]
    timestamp: datetime

class SelfImprovementTrigger:
    """자기 개선 트리거 시스템"""
    
    def __init__(self):
        self.triggers: List[ImprovementTrigger] = []
        self.evolution_reports: List[EvolutionReport] = []
        self.error_count: Dict[str, int] = {}
        self.performance_metrics: Dict[str, Any] = {}
        
        logger.info("SelfImprovementTrigger 초기화 완료")
    
    def analyze_evolution_need(self, current_phase: int, target_phase: int, 
                             current_systems: Dict[str, Any], performance_data: Dict[str, Any]) -> List[ImprovementTrigger]:
        """진화 필요성 분석"""
        triggers = []
        
        # 1. 성능 한계 분석
        performance_triggers = self._analyze_performance_limitations(performance_data)
        triggers.extend(performance_triggers)
        
        # 2. 기능 격차 분석
        functionality_triggers = self._analyze_functionality_gaps(current_systems, target_phase)
        triggers.extend(functionality_triggers)
        
        # 3. 통합 이슈 분석
        integration_triggers = self._analyze_integration_issues(current_systems)
        triggers.extend(integration_triggers)
        
        # 4. 안정성 우려 분석
        stability_triggers = self._analyze_stability_concerns(current_systems, performance_data)
        triggers.extend(stability_triggers)
        
        # 5. 진화 기회 분석
        evolution_triggers = self._analyze_evolution_opportunities(current_phase, target_phase)
        triggers.extend(evolution_triggers)
        
        # 트리거 저장
        for trigger in triggers:
            self.triggers.append(trigger)
        
        logger.info(f"진화 필요성 분석 완료: {len(triggers)}개 트리거 발견")
        return triggers
    
    def _analyze_performance_limitations(self, performance_data: Dict[str, Any]) -> List[ImprovementTrigger]:
        """성능 한계 분석"""
        triggers = []
        
        # 응답 시간 분석
        if performance_data.get("average_response_time", 0) > 1.0:
            trigger = ImprovementTrigger(
                id=f"performance_trigger_{len(self.triggers) + 1}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                trigger_type=TriggerType.PERFORMANCE_LIMITATION,
                priority=TriggerPriority.HIGH,
                description="응답 시간이 1초를 초과하여 사용자 경험이 저하되고 있습니다.",
                current_state=f"평균 응답 시간: {performance_data.get('average_response_time', 0):.2f}초",
                target_state="평균 응답 시간: 1초 이하",
                reasoning="빠른 응답은 가족과의 자연스러운 대화에 필수적입니다.",
                evidence=[
                    f"현재 평균 응답 시간: {performance_data.get('average_response_time', 0):.2f}초",
                    "사용자 만족도 저하 가능성",
                    "대화 흐름 중단 위험"
                ],
                proposed_solutions=[
                    "알고리즘 최적화",
                    "캐싱 전략 도입",
                    "비동기 처리 구현"
                ],
                estimated_impact="사용자 경험 크게 개선",
                timestamp=datetime.now()
            )
            triggers.append(trigger)
        
        # 메모리 사용량 분석
        if performance_data.get("memory_usage", 0) > 80:
            trigger = ImprovementTrigger(
                id=f"memory_trigger_{len(self.triggers) + 1}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                trigger_type=TriggerType.PERFORMANCE_LIMITATION,
                priority=TriggerPriority.CRITICAL,
                description="메모리 사용량이 80%를 초과하여 시스템 안정성이 위협받고 있습니다.",
                current_state=f"메모리 사용량: {performance_data.get('memory_usage', 0):.1f}%",
                target_state="메모리 사용량: 70% 이하",
                reasoning="높은 메모리 사용량은 시스템 크래시를 유발할 수 있습니다.",
                evidence=[
                    f"현재 메모리 사용량: {performance_data.get('memory_usage', 0):.1f}%",
                    "시스템 안정성 위험",
                    "성능 저하 가능성"
                ],
                proposed_solutions=[
                    "메모리 누수 해결",
                    "가비지 컬렉션 최적화",
                    "메모리 효율적 알고리즘 도입"
                ],
                estimated_impact="시스템 안정성 크게 향상",
                timestamp=datetime.now()
            )
            triggers.append(trigger)
        
        return triggers
    
    def _analyze_functionality_gaps(self, current_systems: Dict[str, Any], target_phase: int) -> List[ImprovementTrigger]:
        """기능 격차 분석"""
        triggers = []
        
        # Phase별 필수 시스템 체크
        phase_requirements = {
            12: ["EthicalConversationSystem", "NarrativeMemoryEnhancer", "EmotionalConversationSystem"],
            13: ["AdvancedLearningSystem", "CreativeThinkingSystem"],
            14: ["MultiModalLearningSystem", "AdvancedReasoningSystem"],
            15: ["AGILevelSystem", "SuperintelligenceSystem"]
        }
        
        if target_phase in phase_requirements:
            required_systems = phase_requirements[target_phase]
            missing_systems = []
            
            for system in required_systems:
                if system not in current_systems or current_systems[system].get("status") != "completed":
                    missing_systems.append(system)
            
            if missing_systems:
                trigger = ImprovementTrigger(
                    id=f"functionality_trigger_{len(self.triggers) + 1}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                    trigger_type=TriggerType.FUNCTIONALITY_GAP,
                    priority=TriggerPriority.HIGH,
                    description=f"Phase {target_phase}에 필요한 시스템이 부족합니다.",
                    current_state=f"현재 구현된 시스템: {len(current_systems)}개",
                    target_state=f"필요한 시스템: {len(required_systems)}개",
                    reasoning=f"Phase {target_phase}로의 진화를 위해 추가 시스템이 필요합니다.",
                    evidence=[
                        f"누락된 시스템: {', '.join(missing_systems)}",
                        f"현재 Phase: {target_phase - 1}",
                        f"목표 Phase: {target_phase}"
                    ],
                    proposed_solutions=[
                        f"Phase {target_phase} 필수 시스템 구현",
                        "시스템 간 통합 강화",
                        "테스트 커버리지 확대"
                    ],
                    estimated_impact="다음 단계 진화 가능",
                    timestamp=datetime.now()
                )
                triggers.append(trigger)
        
        return triggers
    
    def _analyze_integration_issues(self, current_systems: Dict[str, Any]) -> List[ImprovementTrigger]:
        """통합 이슈 분석"""
        triggers = []
        
        # 시스템 간 통합 상태 체크
        integration_issues = []
        
        # 데이터 흐름 체크
        if "TextBasedLearningSystem" in current_systems and "LLMInterface" in current_systems:
            if not self._check_data_flow("text_to_llm"):
                integration_issues.append("텍스트 학습 → LLM 통합 문제")
        
        if "SubtitleBasedLearningSystem" in current_systems and "BasicConversationSystem" in current_systems:
            if not self._check_data_flow("subtitle_to_conversation"):
                integration_issues.append("자막 학습 → 대화 통합 문제")
        
        if integration_issues:
            trigger = ImprovementTrigger(
                id=f"integration_trigger_{len(self.triggers) + 1}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                trigger_type=TriggerType.INTEGRATION_ISSUE,
                priority=TriggerPriority.MEDIUM,
                description="시스템 간 통합에 문제가 있습니다.",
                current_state=f"통합 문제: {len(integration_issues)}개",
                target_state="완전한 시스템 통합",
                reasoning="시스템 간 원활한 데이터 흐름이 전체 성능에 중요합니다.",
                evidence=integration_issues,
                proposed_solutions=[
                    "API 인터페이스 표준화",
                    "데이터 형식 통일",
                    "통합 테스트 강화"
                ],
                estimated_impact="시스템 성능 향상",
                timestamp=datetime.now()
            )
            triggers.append(trigger)
        
        return triggers
    
    def _analyze_stability_concerns(self, current_systems: Dict[str, Any], performance_data: Dict[str, Any]) -> List[ImprovementTrigger]:
        """안정성 우려 분석"""
        triggers = []
        
        # 오류 발생 빈도 체크
        error_threshold = 3
        for system_name, error_count in self.error_count.items():
            if error_count >= error_threshold:
                trigger = ImprovementTrigger(
                    id=f"stability_trigger_{len(self.triggers) + 1}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                    trigger_type=TriggerType.STABILITY_CONCERN,
                    priority=TriggerPriority.CRITICAL,
                    description=f"시스템 '{system_name}'에서 반복적인 오류가 발생하고 있습니다.",
                    current_state=f"오류 발생 횟수: {error_count}회",
                    target_state="오류 발생 횟수: 0회",
                    reasoning="반복적인 오류는 시스템 신뢰성을 저해합니다.",
                    evidence=[
                        f"시스템: {system_name}",
                        f"오류 횟수: {error_count}회",
                        "사용자 경험 저하"
                    ],
                    proposed_solutions=[
                        "오류 원인 분석",
                        "예외 처리 강화",
                        "안정성 테스트 확대"
                    ],
                    estimated_impact="시스템 안정성 크게 향상",
                    timestamp=datetime.now()
                )
                triggers.append(trigger)
        
        return triggers
    
    def _analyze_evolution_opportunities(self, current_phase: int, target_phase: int) -> List[ImprovementTrigger]:
        """진화 기회 분석"""
        triggers = []
        
        # Phase 간 진화 기회 체크
        if target_phase > current_phase:
            trigger = ImprovementTrigger(
                id=f"evolution_trigger_{len(self.triggers) + 1}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                trigger_type=TriggerType.EVOLUTION_OPPORTUNITY,
                priority=TriggerPriority.MEDIUM,
                description=f"Phase {current_phase}에서 Phase {target_phase}로의 진화 기회가 있습니다.",
                current_state=f"현재 Phase: {current_phase}",
                target_state=f"목표 Phase: {target_phase}",
                reasoning="다음 단계 진화를 통해 더 강력한 가족 중심 AI가 될 수 있습니다.",
                evidence=[
                    f"현재 Phase 완성도: 높음",
                    f"다음 Phase 준비도: 충분",
                    "진화 필요성: 명확"
                ],
                proposed_solutions=[
                    f"Phase {target_phase} 시스템 설계",
                    "진화 계획 수립",
                    "단계적 구현"
                ],
                estimated_impact="AI 능력 크게 향상",
                timestamp=datetime.now()
            )
            triggers.append(trigger)
        
        return triggers
    
    def _check_data_flow(self, flow_name: str) -> bool:
        """데이터 흐름 체크"""
        # 실제 구현에서는 더 정교한 데이터 흐름 검사 로직이 필요
        flow_checks = {
            "text_to_llm": True,  # 실제로는 실제 데이터 흐름을 체크
            "subtitle_to_conversation": True
        }
        return flow_checks.get(flow_name, False)
    
    def record_error(self, system_name: str, error_message: str):
        """오류 기록"""
        if system_name not in self.error_count:
            self.error_count[system_name] = 0
        self.error_count[system_name] += 1
        
        logger.warning(f"시스템 '{system_name}' 오류 기록: {error_message}")
    
    def generate_evolution_report(self, current_phase: int, target_phase: int, 
                                triggers: List[ImprovementTrigger]) -> EvolutionReport:
        """진화 보고서 생성"""
        report_id = f"evolution_report_{current_phase}_to_{target_phase}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # 트리거 분석
        trigger_analysis = {
            "total_triggers": len(triggers),
            "critical_triggers": len([t for t in triggers if t.priority == TriggerPriority.CRITICAL]),
            "high_triggers": len([t for t in triggers if t.priority == TriggerPriority.HIGH]),
            "medium_triggers": len([t for t in triggers if t.priority == TriggerPriority.MEDIUM]),
            "low_triggers": len([t for t in triggers if t.priority == TriggerPriority.LOW])
        }
        
        # 결정 근거
        if trigger_analysis["critical_triggers"] > 0:
            decision_rationale = "중요한 문제가 발견되어 즉시 개선이 필요합니다."
        elif trigger_analysis["high_triggers"] > 0:
            decision_rationale = "높은 우선순위 문제가 발견되어 개선이 권장됩니다."
        else:
            decision_rationale = "진화 기회가 발견되어 다음 단계로 진행할 수 있습니다."
        
        # 위험도 평가
        risk_assessment = {
            "technical_risk": "high" if trigger_analysis["critical_triggers"] > 0 else "medium",
            "stability_risk": "high" if trigger_analysis["critical_triggers"] > 0 else "low",
            "evolution_risk": "low" if trigger_analysis["critical_triggers"] == 0 else "medium"
        }
        
        # 구현 계획
        implementation_plan = []
        for trigger in triggers:
            if trigger.priority in [TriggerPriority.CRITICAL, TriggerPriority.HIGH]:
                implementation_plan.extend(trigger.proposed_solutions)
        
        # 성공 지표
        success_metrics = [
            "모든 중요 트리거 해결",
            "시스템 안정성 향상",
            "성능 개선 달성"
        ]
        
        # 대안 계획
        fallback_plan = [
            "현재 Phase 유지",
            "점진적 개선",
            "관리자 개입 요청"
        ]
        
        report = EvolutionReport(
            id=report_id,
            current_phase=current_phase,
            target_phase=target_phase,
            trigger_analysis=trigger_analysis,
            decision_rationale=decision_rationale,
            risk_assessment=risk_assessment,
            implementation_plan=implementation_plan,
            success_metrics=success_metrics,
            fallback_plan=fallback_plan,
            timestamp=datetime.now()
        )
        
        self.evolution_reports.append(report)
        logger.info(f"진화 보고서 생성: {current_phase} → {target_phase}")
        
        return report
    
    def should_report_to_manager(self) -> bool:
        """관리자 보고 필요 여부 판단"""
        # 중요 트리거가 있거나 오류가 3회 이상 발생한 경우
        critical_triggers = [t for t in self.triggers if t.priority == TriggerPriority.CRITICAL]
        high_error_systems = [s for s, count in self.error_count.items() if count >= 3]
        
        return len(critical_triggers) > 0 or len(high_error_systems) > 0
    
    def get_manager_report(self) -> Dict[str, Any]:
        """관리자 보고서 생성"""
        if not self.should_report_to_manager():
            return {"status": "no_report_needed"}
        
        critical_triggers = [t for t in self.triggers if t.priority == TriggerPriority.CRITICAL]
        high_error_systems = [s for s, count in self.error_count.items() if count >= 3]
        
        report = {
            "status": "report_required",
            "critical_issues": len(critical_triggers),
            "high_error_systems": high_error_systems,
            "recommended_actions": [
                "즉시 개입 필요",
                "시스템 안정성 점검",
                "오류 원인 분석"
            ],
            "timestamp": datetime.now().isoformat()
        }
        
        return report
    
    def get_trigger_statistics(self) -> Dict[str, Any]:
        """트리거 통계 제공"""
        total_triggers = len(self.triggers)
        
        # 유형별 통계
        type_stats = {}
        for trigger_type in TriggerType:
            type_triggers = [t for t in self.triggers if t.trigger_type == trigger_type]
            type_stats[trigger_type.value] = len(type_triggers)
        
        # 우선순위별 통계
        priority_stats = {}
        for priority in TriggerPriority:
            priority_triggers = [t for t in self.triggers if t.priority == priority]
            priority_stats[priority.value] = len(priority_triggers)
        
        statistics = {
            'total_triggers': total_triggers,
            'type_statistics': type_stats,
            'priority_statistics': priority_stats,
            'error_statistics': self.error_count,
            'last_updated': datetime.now().isoformat()
        }
        
        logger.info("트리거 통계 생성 완료")
        return statistics
    
    def export_trigger_data(self) -> Dict[str, Any]:
        """트리거 데이터 내보내기"""
        return {
            'triggers': [asdict(t) for t in self.triggers],
            'evolution_reports': [asdict(r) for r in self.evolution_reports],
            'error_count': self.error_count,
            'export_date': datetime.now().isoformat()
        }

# 테스트 함수
def test_self_improvement_trigger():
    """자기 개선 트리거 시스템 테스트"""
    print("🔧 SelfImprovementTrigger 테스트 시작...")
    
    trigger_system = SelfImprovementTrigger()
    
    # 1. 성능 데이터 설정
    performance_data = {
        "average_response_time": 1.5,
        "memory_usage": 85.0,
        "cpu_usage": 70.0
    }
    
    # 2. 현재 시스템 상태
    current_systems = {
        "TextBasedLearningSystem": {"status": "completed", "test_coverage": 95},
        "SubtitleBasedLearningSystem": {"status": "completed", "test_coverage": 92},
        "LLMInterface": {"status": "completed", "test_coverage": 88},
        "BasicConversationSystem": {"status": "completed", "test_coverage": 90}
    }
    
    # 3. 오류 기록
    trigger_system.record_error("TextBasedLearningSystem", "메모리 부족 오류")
    trigger_system.record_error("TextBasedLearningSystem", "타임아웃 오류")
    trigger_system.record_error("TextBasedLearningSystem", "데이터 형식 오류")
    
    # 4. 진화 필요성 분석
    triggers = trigger_system.analyze_evolution_need(11, 12, current_systems, performance_data)
    print(f"✅ 진화 필요성 분석: {len(triggers)}개 트리거 발견")
    
    for trigger in triggers:
        print(f"   - {trigger.trigger_type.value}: {trigger.description}")
        print(f"     우선순위: {trigger.priority.value}")
    
    # 5. 진화 보고서 생성
    report = trigger_system.generate_evolution_report(11, 12, triggers)
    print(f"✅ 진화 보고서 생성: {report.decision_rationale}")
    print(f"   위험도: {report.risk_assessment}")
    
    # 6. 관리자 보고 필요 여부
    should_report = trigger_system.should_report_to_manager()
    print(f"✅ 관리자 보고 필요: {should_report}")
    
    if should_report:
        manager_report = trigger_system.get_manager_report()
        print(f"   관리자 보고서: {manager_report}")
    
    # 7. 통계
    statistics = trigger_system.get_trigger_statistics()
    print(f"✅ 트리거 통계: {statistics['total_triggers']}개 트리거")
    print(f"   유형별 통계: {statistics['type_statistics']}")
    print(f"   우선순위별 통계: {statistics['priority_statistics']}")
    
    # 8. 데이터 내보내기
    export_data = trigger_system.export_trigger_data()
    print(f"✅ 트리거 데이터 내보내기: {len(export_data['triggers'])}개 트리거")
    
    print("🎉 SelfImprovementTrigger 테스트 완료!")

if __name__ == "__main__":
    test_self_improvement_trigger() 