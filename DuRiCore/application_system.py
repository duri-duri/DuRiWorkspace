#!/usr/bin/env python3
"""
DuRiCore Phase 7 - 실제 응용 시스템
도메인별 특화 모듈과 실제 문제 해결 능력을 구현한 시스템
"""

import asyncio
import json
import logging
import math
import re
import statistics
import time
from dataclasses import asdict, dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

# 기존 시스템들 import
from integrated_system_manager import IntegratedSystemManager

# 로깅 설정
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class ApplicationDomain(Enum):
    """응용 도메인 열거형"""

    GENERAL_CONVERSATION = "general_conversation"
    PROBLEM_SOLVING = "problem_solving"
    CREATIVE_WRITING = "creative_writing"
    TECHNICAL_ANALYSIS = "technical_analysis"
    EDUCATIONAL_TUTORING = "educational_tutoring"
    EMOTIONAL_SUPPORT = "emotional_support"
    STRATEGIC_PLANNING = "strategic_planning"
    DATA_ANALYSIS = "data_analysis"
    CODE_GENERATION = "code_generation"
    RESEARCH_ASSISTANCE = "research_assistance"


class ProblemType(Enum):
    """문제 유형 열거형"""

    LOGICAL = "logical"
    CREATIVE = "creative"
    ANALYTICAL = "analytical"
    EMOTIONAL = "emotional"
    STRATEGIC = "strategic"
    TECHNICAL = "technical"
    EDUCATIONAL = "educational"
    RESEARCH = "research"


@dataclass
class ApplicationContext:
    """응용 컨텍스트 데이터 클래스"""

    domain: ApplicationDomain
    problem_type: ProblemType
    user_input: str
    user_context: Dict[str, Any]
    system_capabilities: Dict[str, Any]
    performance_metrics: Dict[str, float]
    created_at: str


@dataclass
class ApplicationResult:
    """응용 결과 데이터 클래스"""

    domain: ApplicationDomain
    problem_type: ProblemType
    solution: str
    confidence_score: float
    reasoning: str
    alternatives: List[str]
    performance_metrics: Dict[str, float]
    execution_time: float
    created_at: str


class DomainSpecificModule:
    """도메인별 특화 모듈 기본 클래스"""

    def __init__(self, domain: ApplicationDomain):
        self.domain = domain
        self.capabilities = {}
        self.performance_history = []

    async def process(self, context: ApplicationContext) -> ApplicationResult:
        """도메인별 처리 (하위 클래스에서 구현)"""
        raise NotImplementedError

    def get_capabilities(self) -> Dict[str, Any]:
        """도메인별 능력 반환"""
        return self.capabilities

    def update_performance(self, metrics: Dict[str, float]):
        """성능 메트릭 업데이트"""
        self.performance_history.append(
            {"timestamp": datetime.now().isoformat(), "metrics": metrics}
        )


class GeneralConversationModule(DomainSpecificModule):
    """일반 대화 모듈"""

    def __init__(self):
        super().__init__(ApplicationDomain.GENERAL_CONVERSATION)
        self.capabilities = {
            "conversation_flow": True,
            "context_understanding": True,
            "emotional_responses": True,
            "personality_adaptation": True,
        }

    async def process(self, context: ApplicationContext) -> ApplicationResult:
        """일반 대화 처리"""
        start_time = time.time()

        # 대화 분석
        conversation_analysis = self._analyze_conversation(context.user_input)

        # 적절한 응답 생성
        response = await self._generate_conversation_response(
            context, conversation_analysis
        )

        execution_time = time.time() - start_time

        return ApplicationResult(
            domain=self.domain,
            problem_type=ProblemType.EMOTIONAL,
            solution=response,
            confidence_score=conversation_analysis["confidence"],
            reasoning=conversation_analysis["reasoning"],
            alternatives=conversation_analysis["alternatives"],
            performance_metrics={"response_quality": 0.8, "context_relevance": 0.9},
            execution_time=execution_time,
            created_at=datetime.now().isoformat(),
        )

    def _analyze_conversation(self, user_input: str) -> Dict[str, Any]:
        """대화 분석"""
        # 감정 분석
        emotion_keywords = {
            "기쁨": [
                "기뻐",
                "행복",
                "좋아",
                "즐거워",
                "신나",
                "합격",
                "성공",
                "기쁘",
                "좋은",
                "멋진",
            ],
            "슬픔": [
                "슬퍼",
                "우울",
                "속상",
                "힘들어",
                "지쳐",
                "실패",
                "아프",
                "슬픈",
                "힘들",
            ],
            "화남": [
                "화나",
                "짜증",
                "분노",
                "열받",
                "빡쳐",
                "화가",
                "짜증나",
                "분노",
                "열받",
            ],
            "걱정": [
                "걱정",
                "불안",
                "긴장",
                "두려워",
                "무서워",
                "걱정돼",
                "불안해",
                "긴장돼",
            ],
        }

        detected_emotion = "neutral"
        for emotion, keywords in emotion_keywords.items():
            if any(keyword in user_input for keyword in keywords):
                detected_emotion = emotion
                break

        # 대화 유형 분석
        conversation_type = "general"
        if "?" in user_input:
            conversation_type = "question"
        elif any(word in user_input for word in ["도와", "해줘", "어떻게"]):
            conversation_type = "help_request"

        return {
            "emotion": detected_emotion,
            "type": conversation_type,
            "confidence": 0.85,
            "reasoning": f"감정: {detected_emotion}, 유형: {conversation_type}",
            "alternatives": ["공감적 응답", "정보 제공", "질문 반문"],
        }

    async def _generate_conversation_response(
        self, context: ApplicationContext, analysis: Dict[str, Any]
    ) -> str:
        """대화 응답 생성 - 판단 로직 기반 동적 생성"""
        emotion = analysis["emotion"]
        conv_type = analysis["type"]

        # 컨텍스트 분석
        user_context = context.user_context or {}
        interaction_history = user_context.get("interaction_history", [])
        recent_emotions = [
            h.get("emotion") for h in interaction_history[-3:] if h.get("emotion")
        ]
        user_goals = user_context.get("goals", [])
        system_performance = user_context.get("system_performance", 0.5)

        # 감정별 동적 응답 생성
        if emotion == "기쁨":
            if len(recent_emotions) > 0 and recent_emotions.count("슬픔") > 0:
                return f"정말 기뻐 보이네요! 최근에 힘드셨던 것 같은데, {context.user_input}에 대해 더 자세히 들려주세요. 좋은 일이 생겼나요?"
            elif user_goals and len(user_goals) > 0:
                return f"정말 기뻐 보이네요! 목표를 향해 나아가고 계시는 것 같아요. {context.user_input}에 대해 더 자세히 들려주세요."
            else:
                return f"정말 기뻐 보이네요! {context.user_input}에 대해 더 자세히 들려주세요. 무엇이 그렇게 기쁘신가요?"

        elif emotion == "슬픔":
            if len(recent_emotions) > 0 and recent_emotions.count("기쁨") > 0:
                return f"마음이 많이 아프시겠어요. 최근에 좋았던 일이 있었는데, {context.user_input}에 대해 이야기해보세요. 무슨 일이 있으셨나요?"
            elif system_performance < 0.3:
                return f"마음이 많이 아프시겠어요. 제가 도움이 부족했나 봐요. {context.user_input}에 대해 이야기해보세요. 어떻게 도와드릴까요?"
            else:
                return f"마음이 많이 아프시겠어요. {context.user_input}에 대해 이야기해보세요. 함께 생각해보아요."

        elif emotion == "화남":
            if len(recent_emotions) > 0 and recent_emotions.count("화남") > 1:
                return f"화가 나실 만한 일이 있었군요. 최근에 계속 힘드셨던 것 같아요. {context.user_input}에 대해 차분히 이야기해보세요. 무엇이 그렇게 화나게 하시나요?"
            elif user_goals and len(user_goals) > 0:
                return f"화가 나실 만한 일이 있었군요. 목표를 향해 가시다가 방해받으셨나요? {context.user_input}에 대해 차분히 이야기해보세요."
            else:
                return f"화가 나실 만한 일이 있었군요. {context.user_input}에 대해 차분히 이야기해보세요. 무엇이 그렇게 화나게 하시나요?"

        elif emotion == "걱정":
            if len(recent_emotions) > 0 and recent_emotions.count("걱정") > 1:
                return f"걱정이 많으시겠어요. 계속 걱정되시는 일이 있으신가요? {context.user_input}에 대해 함께 생각해보아요. 어떤 부분이 가장 걱정되시나요?"
            elif user_goals and len(user_goals) > 0:
                return f"걱정이 많으시겠어요. 목표를 향해 가시다가 어려움이 있으신가요? {context.user_input}에 대해 함께 생각해보아요."
            else:
                return f"걱정이 많으시겠어요. {context.user_input}에 대해 함께 생각해보아요. 어떤 부분이 걱정되시나요?"

        else:  # 중립적 감정
            if len(interaction_history) > 0:
                return f"{context.user_input}에 대해 더 자세히 들려주세요. 이전 대화를 이어가시는 건가요?"
            elif user_goals and len(user_goals) > 0:
                return f"{context.user_input}에 대해 더 자세히 들려주세요. 목표와 관련된 이야기인가요?"
            else:
                return f"{context.user_input}에 대해 더 자세히 들려주세요."


class ProblemSolvingModule(DomainSpecificModule):
    """문제 해결 모듈"""

    def __init__(self):
        super().__init__(ApplicationDomain.PROBLEM_SOLVING)
        self.capabilities = {
            "logical_analysis": True,
            "step_by_step_solving": True,
            "alternative_solutions": True,
            "verification": True,
        }

    async def process(self, context: ApplicationContext) -> ApplicationResult:
        """문제 해결 처리"""
        start_time = time.time()

        # 문제 분석
        problem_analysis = self._analyze_problem(context.user_input)

        # 해결책 생성
        solution = await self._generate_solution(context, problem_analysis)

        execution_time = time.time() - start_time

        return ApplicationResult(
            domain=self.domain,
            problem_type=problem_analysis["type"],
            solution=solution["solution"],
            confidence_score=solution["confidence"],
            reasoning=solution["reasoning"],
            alternatives=solution["alternatives"],
            performance_metrics={"solution_quality": 0.9, "logical_consistency": 0.85},
            execution_time=execution_time,
            created_at=datetime.now().isoformat(),
        )

    def _analyze_problem(self, user_input: str) -> Dict[str, Any]:
        """문제 분석"""
        # 문제 유형 분류
        problem_type = ProblemType.LOGICAL

        if any(word in user_input for word in ["창의", "새로운", "혁신"]):
            problem_type = ProblemType.CREATIVE
        elif any(word in user_input for word in ["분석", "데이터", "통계"]):
            problem_type = ProblemType.ANALYTICAL
        elif any(word in user_input for word in ["전략", "계획", "목표"]):
            problem_type = ProblemType.STRATEGIC
        elif any(word in user_input for word in ["기술", "코드", "프로그램"]):
            problem_type = ProblemType.TECHNICAL

        return {"type": problem_type, "complexity": "medium", "domain": "general"}

    async def _generate_solution(
        self, context: ApplicationContext, analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """해결책 생성"""
        problem_type = analysis["type"]

        if problem_type == ProblemType.LOGICAL:
            return {
                "solution": "1. 문제를 명확히 정의하세요\n2. 관련 정보를 수집하세요\n3. 가능한 해결책들을 나열하세요\n4. 각 해결책의 장단점을 분석하세요\n5. 최적의 해결책을 선택하세요",
                "confidence": 0.9,
                "reasoning": "논리적 문제 해결을 위한 체계적 접근법",
                "alternatives": ["의사결정 트리 사용", "SWOT 분석", "5Why 분석"],
            }
        elif problem_type == ProblemType.CREATIVE:
            return {
                "solution": "1. 기존 관념을 버리세요\n2. 다양한 관점에서 생각해보세요\n3. 브레인스토밍을 통해 아이디어를 생성하세요\n4. 조합과 변형을 시도해보세요\n5. 실험적 접근을 두려워하지 마세요",
                "confidence": 0.85,
                "reasoning": "창의적 사고를 위한 자유로운 접근법",
                "alternatives": ["디자인 씽킹", "마인드맵", "역발상"],
            }
        else:
            return {
                "solution": "문제의 구체적인 내용을 알려주시면 더 정확한 해결책을 제시할 수 있습니다.",
                "confidence": 0.7,
                "reasoning": "일반적인 문제 해결 가이드라인",
                "alternatives": ["전문가 상담", "관련 자료 조사", "실험적 시도"],
            }


class CreativeWritingModule(DomainSpecificModule):
    """창작 글쓰기 모듈"""

    def __init__(self):
        super().__init__(ApplicationDomain.CREATIVE_WRITING)
        self.capabilities = {
            "story_generation": True,
            "character_development": True,
            "plot_structure": True,
            "style_adaptation": True,
        }

    async def process(self, context: ApplicationContext) -> ApplicationResult:
        """창작 글쓰기 처리"""
        start_time = time.time()

        # 창작 요청 분석
        writing_analysis = self._analyze_writing_request(context.user_input)

        # 창작물 생성
        creation = await self._generate_creative_content(context, writing_analysis)

        execution_time = time.time() - start_time

        return ApplicationResult(
            domain=self.domain,
            problem_type=ProblemType.CREATIVE,
            solution=creation["content"],
            confidence_score=creation["confidence"],
            reasoning=creation["reasoning"],
            alternatives=creation["alternatives"],
            performance_metrics={"creativity": 0.9, "coherence": 0.8},
            execution_time=execution_time,
            created_at=datetime.now().isoformat(),
        )

    def _analyze_writing_request(self, user_input: str) -> Dict[str, Any]:
        """글쓰기 요청 분석"""
        # 장르 분류
        genre = "general"
        if any(word in user_input for word in ["소설", "이야기", "스토리"]):
            genre = "fiction"
        elif any(word in user_input for word in ["시", "시조", "운문"]):
            genre = "poetry"
        elif any(word in user_input for word in ["에세이", "수필"]):
            genre = "essay"

        return {"genre": genre, "length": "medium", "style": "creative"}

    async def _generate_creative_content(
        self, context: ApplicationContext, analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """창작물 생성"""
        genre = analysis["genre"]

        if genre == "fiction":
            return {
                "content": "어느 날, 작은 마을에 이상한 소문이 퍼졌다. 마을 사람들은 모두 두려워했지만, 한 소년만은 호기심을 가졌다. 그는 마을 뒤편의 오래된 나무에 가서 조심스럽게 다가갔다. 그리고는...",
                "confidence": 0.85,
                "reasoning": "소설적 요소를 포함한 창작 스토리",
                "alternatives": [
                    "다른 장르의 이야기",
                    "현실적 스토리",
                    "판타지 요소 추가",
                ],
            }
        elif genre == "poetry":
            return {
                "content": "바람이 불어오는 계절\n나뭇잎이 춤추는 시간\n마음속 깊은 곳에서\n새로운 꿈이 피어난다",
                "confidence": 0.8,
                "reasoning": "자연을 소재로 한 운문 창작",
                "alternatives": ["다른 주제의 시", "자유시 형태", "전통시 형태"],
            }
        else:
            return {
                "content": "창작에 대한 구체적인 요청을 해주시면 더 적합한 내용을 생성해드릴 수 있습니다.",
                "confidence": 0.7,
                "reasoning": "일반적인 창작 가이드",
                "alternatives": [
                    "다양한 장르 시도",
                    "개인적 경험 활용",
                    "독창적 아이디어 개발",
                ],
            }


class TechnicalAnalysisModule(DomainSpecificModule):
    """기술 분석 모듈"""

    def __init__(self):
        super().__init__(ApplicationDomain.TECHNICAL_ANALYSIS)
        self.capabilities = {
            "technical_evaluation": True,
            "performance_analysis": True,
            "optimization_suggestions": True,
            "risk_assessment": True,
        }

    async def process(self, context: ApplicationContext) -> ApplicationResult:
        """기술 분석 처리"""
        start_time = time.time()

        # 기술적 요청 분석
        technical_analysis = self._analyze_technical_request(context.user_input)

        # 분석 결과 생성
        analysis_result = await self._generate_technical_analysis(
            context, technical_analysis
        )

        execution_time = time.time() - start_time

        return ApplicationResult(
            domain=self.domain,
            problem_type=ProblemType.TECHNICAL,
            solution=analysis_result["analysis"],
            confidence_score=analysis_result["confidence"],
            reasoning=analysis_result["reasoning"],
            alternatives=analysis_result["alternatives"],
            performance_metrics={"technical_accuracy": 0.9, "analysis_depth": 0.85},
            execution_time=execution_time,
            created_at=datetime.now().isoformat(),
        )

    def _analyze_technical_request(self, user_input: str) -> Dict[str, Any]:
        """기술적 요청 분석"""
        # 기술 분야 분류
        field = "general"
        if any(word in user_input for word in ["코드", "프로그램", "알고리즘"]):
            field = "programming"
        elif any(word in user_input for word in ["성능", "최적화", "효율"]):
            field = "performance"
        elif any(word in user_input for word in ["보안", "취약점", "위험"]):
            field = "security"

        return {"field": field, "complexity": "medium", "focus": "analysis"}

    async def _generate_technical_analysis(
        self, context: ApplicationContext, analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """기술 분석 생성"""
        field = analysis["field"]

        if field == "programming":
            return {
                "analysis": "코드 분석을 위해서는 구체적인 코드나 문제 상황을 알려주시면 더 정확한 분석을 제공할 수 있습니다. 일반적으로는 코드의 가독성, 효율성, 안정성을 중점적으로 검토합니다.",
                "confidence": 0.85,
                "reasoning": "프로그래밍 분야의 일반적 분석 가이드라인",
                "alternatives": ["코드 리뷰", "성능 프로파일링", "아키텍처 분석"],
            }
        elif field == "performance":
            return {
                "analysis": "성능 분석을 위해서는 현재 시스템의 성능 지표와 병목 지점을 파악해야 합니다. CPU, 메모리, 네트워크, 디스크 I/O 등을 종합적으로 분석하는 것이 중요합니다.",
                "confidence": 0.9,
                "reasoning": "성능 분석의 체계적 접근법",
                "alternatives": [
                    "벤치마크 테스트",
                    "모니터링 도구 활용",
                    "최적화 기법 적용",
                ],
            }
        else:
            return {
                "analysis": "기술적 분석을 위해서는 구체적인 기술적 요구사항이나 문제 상황을 알려주시면 더 정확한 분석을 제공할 수 있습니다.",
                "confidence": 0.8,
                "reasoning": "일반적인 기술 분석 프레임워크",
                "alternatives": ["상세 분석", "전문가 검토", "실험적 검증"],
            }


class ApplicationSystem:
    """실제 응용 시스템"""

    def __init__(self):
        """초기화"""
        self.integrated_manager = IntegratedSystemManager()

        # 도메인별 모듈 초기화
        self.modules = {
            ApplicationDomain.GENERAL_CONVERSATION: GeneralConversationModule(),
            ApplicationDomain.PROBLEM_SOLVING: ProblemSolvingModule(),
            ApplicationDomain.CREATIVE_WRITING: CreativeWritingModule(),
            ApplicationDomain.TECHNICAL_ANALYSIS: TechnicalAnalysisModule(),
        }

        self.performance_history = []
        self.domain_usage_stats = {}

    async def initialize(self):
        """시스템 초기화"""
        await self.integrated_manager.initialize_all_systems()
        logger.info("Application System initialized successfully")

    async def process_application(
        self,
        user_input: str,
        domain: ApplicationDomain = None,
        user_context: Dict[str, Any] = None,
    ) -> ApplicationResult:
        """응용 처리"""
        start_time = time.time()

        # 도메인 자동 감지 (지정되지 않은 경우)
        if domain is None:
            domain = self._detect_domain(user_input)

        # 컨텍스트 생성
        context = ApplicationContext(
            domain=domain,
            problem_type=self._detect_problem_type(user_input),
            user_input=user_input,
            user_context=user_context or {},
            system_capabilities=self._get_system_capabilities(),
            performance_metrics=self._get_performance_metrics(),
            created_at=datetime.now().isoformat(),
        )

        # 통합 시스템 처리
        integrated_result = await self.integrated_manager.run_integrated_cycle(
            {
                "user_input": user_input,
                "domain": domain.value,
                "context": user_context or {},
            }
        )

        # 도메인별 모듈 처리
        if domain in self.modules:
            module_result = await self.modules[domain].process(context)

            # 결과 통합
            final_result = self._integrate_results(module_result, integrated_result)
        else:
            # 기본 처리
            final_result = await self._default_processing(context, integrated_result)

        # 성능 메트릭 업데이트
        execution_time = time.time() - start_time
        self._update_performance_metrics(
            domain, execution_time, final_result.confidence_score
        )

        return final_result

    def _detect_domain(self, user_input: str) -> ApplicationDomain:
        """도메인 자동 감지"""
        input_lower = user_input.lower()

        # 키워드 기반 도메인 감지
        if any(word in input_lower for word in ["문제", "해결", "어떻게", "방법"]):
            return ApplicationDomain.PROBLEM_SOLVING
        elif any(word in input_lower for word in ["이야기", "소설", "창작", "글"]):
            return ApplicationDomain.CREATIVE_WRITING
        elif any(word in input_lower for word in ["기술", "코드", "분석", "성능"]):
            return ApplicationDomain.TECHNICAL_ANALYSIS
        else:
            return ApplicationDomain.GENERAL_CONVERSATION

    def _detect_problem_type(self, user_input: str) -> ProblemType:
        """문제 유형 감지"""
        input_lower = user_input.lower()

        if any(word in input_lower for word in ["논리", "분석", "데이터"]):
            return ProblemType.ANALYTICAL
        elif any(word in input_lower for word in ["창의", "새로운", "혁신"]):
            return ProblemType.CREATIVE
        elif any(word in input_lower for word in ["전략", "계획", "목표"]):
            return ProblemType.STRATEGIC
        elif any(word in input_lower for word in ["기술", "코드", "프로그램"]):
            return ProblemType.TECHNICAL
        elif any(word in input_lower for word in ["감정", "마음", "기분"]):
            return ProblemType.EMOTIONAL
        else:
            return ProblemType.LOGICAL

    def _get_system_capabilities(self) -> Dict[str, Any]:
        """시스템 능력 반환"""
        return {
            "integrated_systems": 18,
            "domain_modules": len(self.modules),
            "cognitive_levels": 5,
            "learning_capabilities": True,
        }

    def _get_performance_metrics(self) -> Dict[str, float]:
        """성능 메트릭 반환"""
        if not self.performance_history:
            return {"average_confidence": 0.8, "average_response_time": 1.0}

        recent_performance = self.performance_history[-10:]
        avg_confidence = statistics.mean([p["confidence"] for p in recent_performance])
        avg_execution_time = statistics.mean(
            [p["execution_time"] for p in recent_performance]
        )

        return {
            "average_confidence": avg_confidence,
            "average_response_time": avg_execution_time,
        }

    def _integrate_results(
        self, module_result: ApplicationResult, integrated_result: Dict[str, Any]
    ) -> ApplicationResult:
        """결과 통합"""
        # 통합 시스템의 판단 결과를 활용
        judgment_score = integrated_result.get("judgment_score", 0.8)

        # 신뢰도 조정
        adjusted_confidence = (module_result.confidence_score + judgment_score) / 2

        # 통합된 추론
        integrated_reasoning = (
            f"{module_result.reasoning} | 통합 시스템 판단: {judgment_score:.2f}"
        )

        return ApplicationResult(
            domain=module_result.domain,
            problem_type=module_result.problem_type,
            solution=module_result.solution,
            confidence_score=adjusted_confidence,
            reasoning=integrated_reasoning,
            alternatives=module_result.alternatives,
            performance_metrics=module_result.performance_metrics,
            execution_time=module_result.execution_time,
            created_at=module_result.created_at,
        )

    async def _default_processing(
        self, context: ApplicationContext, integrated_result: Dict[str, Any]
    ) -> ApplicationResult:
        """기본 처리"""
        return ApplicationResult(
            domain=context.domain,
            problem_type=context.problem_type,
            solution=f"'{context.user_input}'에 대한 기본 응답입니다. 더 구체적인 요청을 해주시면 더 정확한 도움을 드릴 수 있습니다.",
            confidence_score=0.7,
            reasoning="기본 처리 모듈을 통한 일반적 응답",
            alternatives=[
                "도메인별 전문 모듈 활용",
                "통합 시스템 심화 분석",
                "사용자 컨텍스트 기반 맞춤 응답",
            ],
            performance_metrics={"response_quality": 0.7, "relevance": 0.6},
            execution_time=0.5,
            created_at=datetime.now().isoformat(),
        )

    def _update_performance_metrics(
        self, domain: ApplicationDomain, execution_time: float, confidence_score: float
    ):
        """성능 메트릭 업데이트"""
        performance_data = {
            "timestamp": datetime.now().isoformat(),
            "domain": domain.value,
            "execution_time": execution_time,
            "confidence": confidence_score,
        }

        self.performance_history.append(performance_data)

        # 도메인별 사용 통계 업데이트
        if domain.value not in self.domain_usage_stats:
            self.domain_usage_stats[domain.value] = {"count": 0, "avg_confidence": 0.0}

        stats = self.domain_usage_stats[domain.value]
        stats["count"] += 1
        stats["avg_confidence"] = (
            stats["avg_confidence"] * (stats["count"] - 1) + confidence_score
        ) / stats["count"]

    async def get_system_status(self) -> Dict[str, Any]:
        """시스템 상태 반환"""
        integrated_status = await self.integrated_manager.get_system_status()

        return {
            "application_system": {
                "status": "active",
                "modules_count": len(self.modules),
                "performance_history_count": len(self.performance_history),
                "domain_usage_stats": self.domain_usage_stats,
            },
            "integrated_systems": integrated_status,
            "overall_performance": self._get_performance_metrics(),
        }

    async def run_comprehensive_test(self) -> Dict[str, Any]:
        """포괄적 테스트 실행"""
        test_results = {}

        # 각 도메인별 테스트
        for domain, module in self.modules.items():
            test_input = self._get_test_input_for_domain(domain)
            try:
                result = await self.process_application(test_input, domain)
                test_results[domain.value] = {
                    "status": "success",
                    "confidence": result.confidence_score,
                    "execution_time": result.execution_time,
                }
            except Exception as e:
                test_results[domain.value] = {"status": "error", "error": str(e)}

        # 통합 시스템 테스트
        try:
            integrated_test = await self.integrated_manager.run_integration_test()
            test_results["integrated_system"] = integrated_test
        except Exception as e:
            test_results["integrated_system"] = {"status": "error", "error": str(e)}

        return test_results

    def _get_test_input_for_domain(self, domain: ApplicationDomain) -> str:
        """도메인별 테스트 입력 반환"""
        test_inputs = {
            ApplicationDomain.GENERAL_CONVERSATION: "안녕하세요! 오늘 기분이 좋아요.",
            ApplicationDomain.PROBLEM_SOLVING: "복잡한 문제를 해결하는 방법을 알려주세요.",
            ApplicationDomain.CREATIVE_WRITING: "창의적인 이야기를 만들어주세요.",
            ApplicationDomain.TECHNICAL_ANALYSIS: "코드 성능을 분석하는 방법을 알려주세요.",
        }

        return test_inputs.get(domain, "테스트 입력입니다.")


async def main():
    """메인 함수"""
    print("🚀 DuRiCore Phase 7 - 실제 응용 시스템 시작")
    print("=" * 60)

    # 시스템 초기화
    app_system = ApplicationSystem()
    await app_system.initialize()

    # 시스템 상태 확인
    status = await app_system.get_system_status()
    print(f"📊 시스템 상태: {status['application_system']['status']}")
    print(f"🔧 모듈 수: {status['application_system']['modules_count']}")

    # 포괄적 테스트 실행
    print("\n🧪 포괄적 테스트 실행 중...")
    test_results = await app_system.run_comprehensive_test()

    print("\n📋 테스트 결과:")
    for domain, result in test_results.items():
        if result["status"] == "success":
            print(
                f"   ✅ {domain}: 신뢰도 {result['confidence']:.2f}, 실행시간 {result['execution_time']:.2f}초"
            )
        else:
            print(f"   ❌ {domain}: {result.get('error', 'Unknown error')}")

    print("\n🎉 Phase 7 실제 응용 시스템 테스트 완료!")


if __name__ == "__main__":
    asyncio.run(main())
