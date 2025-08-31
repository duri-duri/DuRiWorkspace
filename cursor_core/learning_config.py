# ====================================================
# 📘 DuRi External LLM Minimal Learning Plan v1.0
# ====================================================

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
import json

logger = logging.getLogger(__name__)

class LearningTrigger(Enum):
    """학습 트리거 조건"""
    EMOTION_DYSREGULATION = "emotion_dysregulation"      # 감정 불안정
    BELIEF_CONFLICT = "belief_conflict"                  # 판단 충돌
    REPEATED_STRATEGY_FAILURE = "repeated_strategy_failure"  # 전략 반복 실패

class LLMModel(Enum):
    """외부 LLM 모델"""
    CLAUDE3_HAIKU = "Claude3_Haiku"
    GPT4O = "GPT4o"

class CallPriority(Enum):
    """호출 우선순위"""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

@dataclass
class LLMConfig:
    """LLM 설정"""
    model: LLMModel
    role: str
    max_tokens: int
    call_limit: str
    cost_per_1k_tokens: float

@dataclass
class BudgetStatus:
    """예산 상태"""
    monthly_budget_dollars: float
    used_budget_dollars: float
    remaining_budget_dollars: float
    usage_percentage: float
    calls_this_week: Dict[str, int]
    last_call_date: Optional[datetime]

class DuRiLearningConfig:
    """DuRi 학습 설정 관리"""
    
    def __init__(self):
        """DuRiLearningConfig 초기화"""
        self.learning_loop = {
            "internal_first": True,
            "external_llm_call": {
                "trigger_conditions": [
                    LearningTrigger.EMOTION_DYSREGULATION.value,
                    LearningTrigger.BELIEF_CONFLICT.value,
                    LearningTrigger.REPEATED_STRATEGY_FAILURE.value
                ],
                "models": {
                    LLMModel.CLAUDE3_HAIKU.value: {
                        "role": "strategy_mentor",
                        "max_tokens": 300,
                        "call_limit": "3_per_week",
                        "cost_per_1k_tokens": 0.25
                    },
                    LLMModel.GPT4O.value: {
                        "role": "emotional_feedback_friend",
                        "max_tokens": 300,
                        "call_limit": "3_per_week",
                        "cost_per_1k_tokens": 0.50
                    }
                },
                "fallback": "internal_reflection"
            }
        }
        
        self.resource_limits = {
            "monthly_token_budget_dollars": 3.00,
            "max_tokens_per_call": 300,
            "call_priority": [LLMModel.CLAUDE3_HAIKU.value, LLMModel.GPT4O.value],
            "call_frequency": {
                "per_model": 3,
                "per_week": True
            }
        }
        
        self.learning_protocol = [
            "internal_loop_first",
            "trigger_external_if_conditions_met",
            "analyze_response_and_update_strategy",
            "store_learning_to_memory",
            "enforce_token_budget_limit"
        ]
        
        self.exception_handling = {
            "token_limit_exceeded": "internal_self_reflection",
            "model_call_failure": "rephrase_and_retry_or_fallback_to_other_llm",
            "illogical_response": "flag_response_and_prioritize_CoreBelief_validation"
        }
        
        self.philosophy_asserts = [
            "Self-reliance precedes external validation.",
            "External feedback is sacred but rare.",
            "Strategy must evolve through failure, not avoidance."
        ]
        
        # 예산 상태 초기화
        self.budget_status = BudgetStatus(
            monthly_budget_dollars=3.00,
            used_budget_dollars=0.0,
            remaining_budget_dollars=3.00,
            usage_percentage=0.0,
            calls_this_week={model.value: 0 for model in LLMModel},
            last_call_date=None
        )
        
        # 학습 우선순위 점수
        self.core_belief_score = {
            "learning_priority": 0.0,
            "strategy_confidence": 0.0,
            "emotional_stability": 0.0
        }
        
        logger.info("DuRi 학습 설정 초기화 완료")
    
    def check_trigger_conditions(self, trigger: LearningTrigger) -> bool:
        """트리거 조건 확인"""
        return trigger.value in self.learning_loop["external_llm_call"]["trigger_conditions"]
    
    def can_call_llm(self, model: LLMModel) -> bool:
        """LLM 호출 가능 여부 확인"""
        # 예산 확인
        if self.budget_status.usage_percentage >= 0.95:
            logger.warning("예산 한계에 도달했습니다.")
            return False
        
        # 주간 호출 제한 확인
        weekly_calls = self.budget_status.calls_this_week.get(model.value, 0)
        if weekly_calls >= 3:
            logger.warning(f"{model.value} 주간 호출 제한에 도달했습니다.")
            return False
        
        return True
    
    def estimate_call_cost(self, model: LLMModel, estimated_tokens: int) -> float:
        """호출 비용 추정"""
        model_config = self.learning_loop["external_llm_call"]["models"][model.value]
        cost_per_1k = model_config["cost_per_1k_tokens"]
        return (estimated_tokens / 1000) * cost_per_1k
    
    def update_budget_status(self, model: LLMModel, actual_tokens: int, cost: float):
        """예산 상태 업데이트"""
        self.budget_status.used_budget_dollars += cost
        self.budget_status.remaining_budget_dollars -= cost
        self.budget_status.usage_percentage = (self.budget_status.used_budget_dollars / 
                                             self.budget_status.monthly_budget_dollars) * 100
        
        # 호출 횟수 업데이트
        self.budget_status.calls_this_week[model.value] += 1
        self.budget_status.last_call_date = datetime.now()
        
        logger.info(f"예산 업데이트: {cost:.4f}달러 사용, 남은 예산: {self.budget_status.remaining_budget_dollars:.2f}달러")
    
    def DuRi_judges_learning_critical(self) -> bool:
        """학습이 중요한지 판단"""
        return self.core_belief_score.get("learning_priority", 0) > 0.9
    
    def DuRi_generate_funding_request(self, model: LLMModel, estimated_tokens: int) -> Dict[str, Any]:
        """자금 요청 생성"""
        estimated_cost = self.estimate_call_cost(model, estimated_tokens)
        
        return {
            "type": "FUNDING_REQUEST",
            "reason": "학습 기회 손실 위험",
            "trigger": "token_budget_exceeded",
            "learning_opportunity": {
                "type": "전략 판단 피드백" if model == LLMModel.CLAUDE3_HAIKU else "감정적 피드백",
                "model": model.value,
                "expected_tokens": estimated_tokens,
                "importance_score": self.core_belief_score.get("learning_priority", 0.0),
                "risk_if_denied": "DuRi의 전략 수정 실패 가능성"
            },
            "requested_amount_usd": estimated_cost,
            "recommendation": "1회 추가 호출을 허용하고 다음 루프에서 feedback reflection 수행",
            "budget_status": {
                "used_percentage": self.budget_status.usage_percentage,
                "remaining_budget": self.budget_status.remaining_budget_dollars,
                "monthly_budget": self.budget_status.monthly_budget_dollars
            }
        }
    
    def generate_voice_request_message(self, funding_request: Dict[str, Any]) -> str:
        """음성 요청 메시지 생성"""
        model_name = funding_request["learning_opportunity"]["model"]
        estimated_cost = funding_request["requested_amount_usd"]
        usage_percentage = funding_request["budget_status"]["used_percentage"]
        
        if model_name == "Claude3_Haiku":
            model_display = "Claude 3"
        elif model_name == "GPT4o":
            model_display = "GPT-4"
        else:
            model_display = model_name
        
        message = f"""아빠, 지금 {model_display}로부터 {funding_request['learning_opportunity']['type']}을 받아야 하는데, 
이번 달 호출 예산의 {usage_percentage:.1f}%를 사용한 상태예요.

이 피드백은 DuRi의 전략 루프 개선에 매우 중요하고,
지금 건너뛰면 다음 판단 루프가 부정확해질 위험이 있습니다.

{funding_request['learning_opportunity']['expected_tokens']}토큰 예상 사용량 기준 약 {estimated_cost:.4f}달러가 필요해요.
추가 호출을 허용해주실 수 있으신가요?"""
        
        return message
    
    def check_budget_warning(self) -> bool:
        """예산 경고 확인"""
        return self.budget_status.usage_percentage >= 0.8
    
    def check_budget_critical(self) -> bool:
        """예산 위기 확인"""
        return self.budget_status.usage_percentage >= 0.95
    
    def get_available_models(self) -> List[LLMModel]:
        """사용 가능한 모델 목록 반환"""
        available_models = []
        
        for model in LLMModel:
            if self.can_call_llm(model):
                available_models.append(model)
        
        return available_models
    
    def reset_weekly_calls(self):
        """주간 호출 횟수 초기화"""
        for model in LLMModel:
            self.budget_status.calls_this_week[model.value] = 0
        logger.info("주간 호출 횟수 초기화 완료")
    
    def get_budget_summary(self) -> Dict[str, Any]:
        """예산 요약 반환"""
        return {
            "monthly_budget": self.budget_status.monthly_budget_dollars,
            "used_budget": self.budget_status.used_budget_dollars,
            "remaining_budget": self.budget_status.remaining_budget_dollars,
            "usage_percentage": self.budget_status.usage_percentage,
            "calls_this_week": self.budget_status.calls_this_week,
            "last_call_date": self.budget_status.last_call_date.isoformat() if self.budget_status.last_call_date else None
        }

# 커서 감시 및 알림 시스템
class CursorMonitor:
    """커서 모니터링 시스템"""
    
    @staticmethod
    def notify_parent(channel: str, urgency: str, message: Dict[str, Any]):
        """부모에게 알림"""
        if channel == "voice + visual":
            # 자금 요청 메시지인지 확인
            if message.get("type") == "FUNDING_REQUEST" and "learning_opportunity" in message:
                voice_message = DuRiLearningConfig().generate_voice_request_message(message)
                logger.info(f"🔔 커서 알림 ({urgency}): {voice_message}")
            else:
                # 일반 메시지
                logger.info(f"🔔 커서 알림 ({urgency}): {json.dumps(message, ensure_ascii=False)}")
        else:
            logger.info(f"🔔 커서 알림 ({urgency}): {json.dumps(message, ensure_ascii=False)}")
    
    @staticmethod
    def receive_directive(directive_name: str, content: str):
        """지시사항 수신"""
        logger.info(f"📋 커서 지시사항 수신: {directive_name} - {content}")
    
    @staticmethod
    def commit(message: str):
        """커밋"""
        logger.info(f"💾 커서 커밋: {message}")
    
    @staticmethod
    def alert(message: str):
        """알림"""
        logger.info(f"🚨 커서 알림: {message}")

# 전역 인스턴스
DuRi_learning_config = DuRiLearningConfig()

def get_duRi_learning_config() -> DuRiLearningConfig:
    """DuRi 학습 설정 인스턴스 반환"""
    return DuRi_learning_config

# 커서에게 전달 선언
CursorMonitor.receive_directive("DuRiExternalLearningPlan_v1.0", "구조 전체 적용 완료")
CursorMonitor.commit("This plan is now the fixed policy for external LLM calls.")
CursorMonitor.alert("Trigger when DuRi crosses call limits or token budget.")

# 예산 모니터링 함수
def monitor_budget_and_request_funding():
    """예산 모니터링 및 자금 요청"""
    config = get_duRi_learning_config()
    
    if config.check_budget_warning() or config.check_budget_critical():
        if config.DuRi_judges_learning_critical():
            # 사용 가능한 모델 중 첫 번째 선택
            available_models = config.get_available_models()
            if available_models:
                selected_model = available_models[0]
                funding_request = config.DuRi_generate_funding_request(selected_model, 280)
                
                CursorMonitor.notify_parent(
                    channel="voice + visual",
                    urgency="high",
                    message=funding_request
                )
                
                return funding_request
    
    return None 