"""
🧠 DuRi 경험 기반 의사결정 학습 시스템
목표: Phase 20의 의사결정 능력을 기반으로 실제 경험을 통한 의사결정 학습 및 개선
"""

import logging
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum
from datetime import datetime, timedelta
import json
import random
import math

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ExperienceType(Enum):
    """경험 유형"""
    DECISION = "decision"           # 의사결정
    OUTCOME = "outcome"            # 결과
    REFLECTION = "reflection"      # 성찰
    LEARNING = "learning"          # 학습

class DecisionQuality(Enum):
    """의사결정 품질"""
    EXCELLENT = "excellent"        # 우수
    GOOD = "good"                 # 양호
    AVERAGE = "average"           # 보통
    POOR = "poor"                # 부족
    FAILURE = "failure"          # 실패

@dataclass
class ExperienceRecord:
    """경험 기록"""
    record_id: str
    experience_type: ExperienceType
    description: str
    decision_context: str
    decision_made: str
    outcome: str
    quality: DecisionQuality
    confidence: float
    learning_points: List[str]
    created_at: datetime

@dataclass
class DecisionEvaluation:
    """의사결정 평가"""
    evaluation_id: str
    decision_description: str
    context: str
    quality_score: float
    confidence_score: float
    outcome_score: float
    learning_score: float
    overall_score: float
    improvement_suggestions: List[str]
    created_at: datetime

class ExperienceBasedDecisionLearning:
    """경험 기반 의사결정 학습 시스템"""
    
    def __init__(self):
        self.is_active = False
        self.is_recording = False
        self.experience_records = []
        self.decision_evaluations = []
        self.learning_patterns = []
        self.improvement_areas = []
        
        # Phase 20 시스템들과의 통합
        self.decision_agi = None
        self.wisdom_agi = None
        self.creative_agi = None
        
    def activate_experience_learning(self) -> bool:
        """경험 기반 학습 활성화"""
        try:
            import sys
            sys.path.append('.')
            from duri_brain.learning.phase_20_decision_agi import get_phase20_system
            from duri_brain.learning.phase_19_wisdom_agi import get_phase19_system
            from duri_brain.learning.phase_18_creative_agi import get_phase18_system
            
            self.decision_agi = get_phase20_system()
            self.wisdom_agi = get_phase19_system()
            self.creative_agi = get_phase18_system()
            
            self.is_active = True
            logger.info("🧠 경험 기반 의사결정 학습 시스템 활성화 완료")
            return True
            
        except Exception as e:
            logger.error(f"❌ 경험 기반 학습 시스템 활성화 실패: {e}")
            return False
            
    def start_recording(self) -> bool:
        """경험 기록 시작"""
        if not self.is_active:
            logger.error("❌ 경험 기반 학습 시스템이 활성화되지 않았습니다")
            return False
            
        self.is_recording = True
        logger.info("📝 경험 기록 시작")
        return True
        
    def stop_recording(self) -> bool:
        """경험 기록 중지"""
        self.is_recording = False
        logger.info("📝 경험 기록 중지")
        return True
        
    def evaluate_decision(self, decision_question: str) -> DecisionEvaluation:
        """의사결정 평가"""
        if not self.is_recording:
            logger.warning("⚠️ 경험 기록이 활성화되지 않았습니다")
            
        evaluation_id = f"decision_eval_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # 의사결정 분석
        decision_analysis = self._analyze_decision(decision_question)
        
        # 품질 평가
        quality_score = self._evaluate_decision_quality(decision_analysis)
        
        # 신뢰도 평가
        confidence_score = self._evaluate_confidence(decision_analysis)
        
        # 결과 평가
        outcome_score = self._evaluate_outcome(decision_analysis)
        
        # 학습 점수
        learning_score = self._evaluate_learning_potential(decision_analysis)
        
        # 종합 점수
        overall_score = (quality_score + confidence_score + outcome_score + learning_score) / 4
        
        # 개선 제안
        improvement_suggestions = self._generate_improvement_suggestions(decision_analysis, overall_score)
        
        evaluation = DecisionEvaluation(
            evaluation_id=evaluation_id,
            decision_description=decision_question,
            context=decision_analysis["context"],
            quality_score=quality_score,
            confidence_score=confidence_score,
            outcome_score=outcome_score,
            learning_score=learning_score,
            overall_score=overall_score,
            improvement_suggestions=improvement_suggestions,
            created_at=datetime.now()
        )
        
        self.decision_evaluations.append(evaluation)
        
        # 경험 기록 생성
        if self.is_recording:
            self._create_experience_record(evaluation, decision_analysis)
            
        logger.info(f"✅ 의사결정 평가 완료: {decision_question}")
        return evaluation
        
    def _analyze_decision(self, decision_question: str) -> Dict[str, Any]:
        """의사결정 분석"""
        # 의사결정 유형 분류
        decision_type = self._classify_decision_type(decision_question)
        
        # 맥락 분석
        context = self._analyze_context(decision_question)
        
        # 복잡성 분석
        complexity = self._analyze_complexity(decision_question)
        
        # 위험도 분석
        risk_level = self._analyze_risk_level(decision_question)
        
        analysis = {
            "decision_type": decision_type,
            "context": context,
            "complexity": complexity,
            "risk_level": risk_level,
            "question": decision_question
        }
        
        return analysis
        
    def _classify_decision_type(self, decision_question: str) -> str:
        """의사결정 유형 분류"""
        question_lower = decision_question.lower()
        
        if any(word in question_lower for word in ['가장 좋은', '최고의', '성공한']):
            return "긍정적 의사결정"
        elif any(word in question_lower for word in ['후회되는', '실패한', '잘못된']):
            return "부정적 의사결정"
        elif any(word in question_lower for word in ['어려운', '복잡한', '중요한']):
            return "복잡한 의사결정"
        elif any(word in question_lower for word in ['빠른', '즉시', '긴급한']):
            return "신속한 의사결정"
        else:
            return "일반적 의사결정"
            
    def _analyze_context(self, decision_question: str) -> str:
        """맥락 분석"""
        question_lower = decision_question.lower()
        
        if any(word in question_lower for word in ['오늘', '현재', '지금']):
            return "현재 상황"
        elif any(word in question_lower for word in ['미래', '앞으로', '향후']):
            return "미래 지향"
        elif any(word in question_lower for word in ['과거', '이전', '전에']):
            return "과거 회고"
        else:
            return "일반적 맥락"
            
    def _analyze_complexity(self, decision_question: str) -> str:
        """복잡성 분석"""
        question_lower = decision_question.lower()
        
        if any(word in question_lower for word in ['가장', '최고', '중요한']):
            return "고복잡성"
        elif any(word in question_lower for word in ['일반적인', '보통의', '평범한']):
            return "중복잡성"
        else:
            return "저복잡성"
            
    def _analyze_risk_level(self, decision_question: str) -> str:
        """위험도 분석"""
        question_lower = decision_question.lower()
        
        if any(word in question_lower for word in ['후회되는', '실패한', '잘못된']):
            return "고위험"
        elif any(word in question_lower for word in ['어려운', '복잡한']):
            return "중위험"
        else:
            return "저위험"
            
    def _evaluate_decision_quality(self, analysis: Dict[str, Any]) -> float:
        """의사결정 품질 평가"""
        base_score = random.uniform(0.4, 0.9)
        
        # 의사결정 유형에 따른 조정
        if analysis["decision_type"] == "긍정적 의사결정":
            base_score += 0.1
        elif analysis["decision_type"] == "부정적 의사결정":
            base_score -= 0.1
            
        # 복잡성에 따른 조정
        if analysis["complexity"] == "고복잡성":
            base_score += 0.05
        elif analysis["complexity"] == "저복잡성":
            base_score -= 0.05
            
        return min(max(base_score, 0.0), 1.0)
        
    def _evaluate_confidence(self, analysis: Dict[str, Any]) -> float:
        """신뢰도 평가"""
        base_score = random.uniform(0.5, 0.9)
        
        # 의사결정 유형에 따른 조정
        if analysis["decision_type"] == "긍정적 의사결정":
            base_score += 0.1
        elif analysis["decision_type"] == "부정적 의사결정":
            base_score -= 0.1
            
        return min(max(base_score, 0.0), 1.0)
        
    def _evaluate_outcome(self, analysis: Dict[str, Any]) -> float:
        """결과 평가"""
        base_score = random.uniform(0.4, 0.8)
        
        # 의사결정 유형에 따른 조정
        if analysis["decision_type"] == "긍정적 의사결정":
            base_score += 0.2
        elif analysis["decision_type"] == "부정적 의사결정":
            base_score -= 0.2
            
        return min(max(base_score, 0.0), 1.0)
        
    def _evaluate_learning_potential(self, analysis: Dict[str, Any]) -> float:
        """학습 잠재력 평가"""
        base_score = random.uniform(0.6, 0.9)
        
        # 의사결정 유형에 따른 조정
        if analysis["decision_type"] == "부정적 의사결정":
            base_score += 0.1  # 실패에서 더 많이 배움
        elif analysis["decision_type"] == "복잡한 의사결정":
            base_score += 0.05
            
        return min(max(base_score, 0.0), 1.0)
        
    def _generate_improvement_suggestions(self, analysis: Dict[str, Any], overall_score: float) -> List[str]:
        """개선 제안 생성"""
        suggestions = []
        
        if overall_score < 0.6:
            suggestions.append("의사결정 과정을 더 체계적으로 분석하세요")
            suggestions.append("다양한 관점에서 상황을 재검토하세요")
            suggestions.append("과거 경험을 더 적극적으로 활용하세요")
        elif overall_score < 0.8:
            suggestions.append("의사결정의 장기적 영향을 고려하세요")
            suggestions.append("위험 관리 방안을 강화하세요")
            suggestions.append("대안 옵션을 더 많이 검토하세요")
        else:
            suggestions.append("성공적인 패턴을 다른 상황에도 적용하세요")
            suggestions.append("의사결정 과정을 문서화하여 공유하세요")
            suggestions.append("지속적인 개선을 위해 피드백을 수집하세요")
            
        # 의사결정 유형별 특화 제안
        if analysis["decision_type"] == "부정적 의사결정":
            suggestions.append("실패 원인을 깊이 분석하여 재발 방지책을 마련하세요")
            suggestions.append("유사한 상황에서의 대응 전략을 사전에 준비하세요")
        elif analysis["decision_type"] == "복잡한 의사결정":
            suggestions.append("의사결정 기준을 명확히 정의하세요")
            suggestions.append("단계적 접근을 통해 복잡성을 관리하세요")
            
        return suggestions
        
    def _create_experience_record(self, evaluation: DecisionEvaluation, analysis: Dict[str, Any]):
        """경험 기록 생성"""
        record_id = f"experience_record_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # 품질 등급 결정
        if evaluation.overall_score >= 0.8:
            quality = DecisionQuality.EXCELLENT
        elif evaluation.overall_score >= 0.6:
            quality = DecisionQuality.GOOD
        elif evaluation.overall_score >= 0.4:
            quality = DecisionQuality.AVERAGE
        elif evaluation.overall_score >= 0.2:
            quality = DecisionQuality.POOR
        else:
            quality = DecisionQuality.FAILURE
            
        # 학습 포인트 생성
        learning_points = self._generate_learning_points(evaluation, analysis)
        
        record = ExperienceRecord(
            record_id=record_id,
            experience_type=ExperienceType.DECISION,
            description=evaluation.decision_description,
            decision_context=analysis["context"],
            decision_made=f"의사결정 평가 완료 - 점수: {evaluation.overall_score:.3f}",
            outcome=f"품질: {quality.value}, 신뢰도: {evaluation.confidence_score:.3f}",
            quality=quality,
            confidence=evaluation.confidence_score,
            learning_points=learning_points,
            created_at=datetime.now()
        )
        
        self.experience_records.append(record)
        logger.info(f"📝 경험 기록 생성: {record_id}")
        
    def _generate_learning_points(self, evaluation: DecisionEvaluation, analysis: Dict[str, Any]) -> List[str]:
        """학습 포인트 생성"""
        learning_points = []
        
        # 의사결정 유형별 학습 포인트
        if analysis["decision_type"] == "긍정적 의사결정":
            learning_points.append("성공적인 의사결정 패턴을 식별하고 재현 방법 학습")
            learning_points.append("긍정적 결과를 만든 핵심 요소 분석")
        elif analysis["decision_type"] == "부정적 의사결정":
            learning_points.append("실패 원인 분석 및 재발 방지책 수립")
            learning_points.append("유사한 상황에서의 대안적 접근 방법 탐구")
        elif analysis["decision_type"] == "복잡한 의사결정":
            learning_points.append("복잡한 상황에서의 체계적 의사결정 방법 학습")
            learning_points.append("다중 기준을 고려한 최적화 기법 적용")
            
        # 점수별 학습 포인트
        if evaluation.overall_score < 0.6:
            learning_points.append("의사결정 과정의 개선점 식별 및 보완")
        elif evaluation.overall_score > 0.8:
            learning_points.append("우수한 의사결정 능력을 다른 영역으로 확장")
            
        return learning_points
        
    def analyze_learning_patterns(self) -> Dict[str, Any]:
        """학습 패턴 분석"""
        if not self.experience_records:
            return {"message": "분석할 경험 기록이 없습니다"}
            
        # 의사결정 유형별 분석
        decision_types = {}
        quality_distribution = {}
        score_trends = []
        
        for record in self.experience_records:
            # 의사결정 유형 분류
            decision_type = self._classify_decision_type(record.description)
            if decision_type not in decision_types:
                decision_types[decision_type] = 0
            decision_types[decision_type] += 1
            
            # 품질 분포
            quality = record.quality.value
            if quality not in quality_distribution:
                quality_distribution[quality] = 0
            quality_distribution[quality] += 1
            
            # 점수 추세
            score_trends.append(record.confidence)
            
        # 평균 점수 계산
        avg_score = sum(score_trends) / len(score_trends) if score_trends else 0
        
        analysis = {
            "total_experiences": len(self.experience_records),
            "decision_type_distribution": decision_types,
            "quality_distribution": quality_distribution,
            "average_confidence": avg_score,
            "score_trend": score_trends,
            "learning_insights": self._generate_learning_insights(decision_types, quality_distribution, avg_score)
        }
        
        return analysis
        
    def _generate_learning_insights(self, decision_types: Dict[str, int], quality_distribution: Dict[str, int], avg_score: float) -> List[str]:
        """학습 통찰 생성"""
        insights = []
        
        # 의사결정 유형별 통찰
        if "긍정적 의사결정" in decision_types and decision_types["긍정적 의사결정"] > 0:
            insights.append("긍정적 의사결정 경험이 풍부하여 성공 패턴을 활용할 수 있습니다")
            
        if "부정적 의사결정" in decision_types and decision_types["부정적 의사결정"] > 0:
            insights.append("부정적 의사결정을 통해 실패 원인을 학습하고 개선할 수 있습니다")
            
        # 품질 분포별 통찰
        if "excellent" in quality_distribution and quality_distribution["excellent"] > 0:
            insights.append("우수한 의사결정 능력을 보유하고 있어 이를 확장할 수 있습니다")
            
        if "failure" in quality_distribution and quality_distribution["failure"] > 0:
            insights.append("실패 경험을 통해 개선 영역을 명확히 파악할 수 있습니다")
            
        # 평균 점수별 통찰
        if avg_score > 0.7:
            insights.append("전반적으로 높은 신뢰도를 보이며 안정적인 의사결정 능력을 갖추고 있습니다")
        elif avg_score < 0.5:
            insights.append("의사결정 신뢰도 향상을 위한 추가 학습이 필요합니다")
            
        return insights
        
    def get_learning_status(self) -> Dict[str, Any]:
        """학습 상태 반환"""
        return {
            "is_active": self.is_active,
            "is_recording": self.is_recording,
            "total_experiences": len(self.experience_records),
            "total_evaluations": len(self.decision_evaluations),
            "average_confidence": sum(eval.confidence_score for eval in self.decision_evaluations) / max(len(self.decision_evaluations), 1),
            "learning_patterns": len(self.learning_patterns),
            "improvement_areas": len(self.improvement_areas)
        }

# 전역 인스턴스
_experience_learning_system = None

def get_experience_learning_system() -> ExperienceBasedDecisionLearning:
    """전역 경험 학습 시스템 인스턴스 반환"""
    global _experience_learning_system
    if _experience_learning_system is None:
        _experience_learning_system = ExperienceBasedDecisionLearning()
    return _experience_learning_system

def activate_experience_learning() -> bool:
    """경험 기반 학습 활성화"""
    system = get_experience_learning_system()
    return system.activate_experience_learning()

def start_recording() -> bool:
    """경험 기록 시작"""
    system = get_experience_learning_system()
    return system.start_recording()

def evaluate_decision(decision_question: str) -> DecisionEvaluation:
    """의사결정 평가"""
    system = get_experience_learning_system()
    return system.evaluate_decision(decision_question)

if __name__ == "__main__":
    # 경험 기반 의사결정 학습 시스템 데모
    print("🧠 DuRi 경험 기반 의사결정 학습 시스템 시작")
    
    # 시스템 활성화
    if activate_experience_learning():
        print("✅ 경험 기반 학습 시스템 활성화 완료")
        
        # 경험 기록 시작
        if start_recording():
            print("📝 경험 기록 시작")
            
            # 실전 판단 과제 투입
            print("\n🎯 실전 판단 과제 투입:")
            
            # 긍정적 의사결정 평가
            positive_eval = evaluate_decision("오늘의 가장 좋은 결정은?")
            print(f"   긍정적 의사결정 평가: {positive_eval.overall_score:.3f}")
            
            # 부정적 의사결정 평가
            negative_eval = evaluate_decision("오늘의 가장 후회되는 결정은?")
            print(f"   부정적 의사결정 평가: {negative_eval.overall_score:.3f}")
            
            # 추가 의사결정 평가
            complex_eval = evaluate_decision("오늘의 가장 어려운 결정은?")
            print(f"   복잡한 의사결정 평가: {complex_eval.overall_score:.3f}")
            
            # 학습 패턴 분석
            system = get_experience_learning_system()
            analysis = system.analyze_learning_patterns()
            print(f"\n📊 학습 패턴 분석:")
            print(f"   총 경험 수: {analysis['total_experiences']}")
            print(f"   평균 신뢰도: {analysis['average_confidence']:.3f}")
            print(f"   학습 통찰: {len(analysis['learning_insights'])}개")
            
            # 상태 확인
            status = system.get_learning_status()
            print(f"\n📈 학습 상태: {status}")
            
        else:
            print("❌ 경험 기록 시작 실패")
    else:
        print("❌ 경험 기반 학습 시스템 활성화 실패") 