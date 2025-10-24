#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DuRi Expression Engine - DuRi의 판단 결과를 자연어로 변환하는 엔진

이 모듈은 DuRi의 판단 결과(judgment_trace, thought_flow, decision_tree)를
자연어 문장으로 변환하여 DuRi가 직접 말하는 것처럼 표현합니다.

주요 기능:
- 판단 결과 추출 및 분석
- 자연어 템플릿 매핑
- 의미 보존 문장 구성
- DuRi 명의 출력
"""

import logging
import re
import time
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Union

# 모듈 레지스트리 시스템 import
try:
    from module_registry import BaseModule, ModulePriority, register_module

    MODULE_REGISTRY_AVAILABLE = True
except ImportError:
    MODULE_REGISTRY_AVAILABLE = False

    # Fallback for when module_registry is not available
    class BaseModule:
        def __init__(self):
            self._initialized = False
            self._context = {}

        async def initialize(self):
            pass

        async def execute(self, context):
            pass

        async def cleanup(self):
            pass

    class ModulePriority(Enum):
        CRITICAL = 0
        HIGH = 1
        NORMAL = 2
        LOW = 3
        OPTIONAL = 4

    def register_module(*args, **kwargs):
        def decorator(cls):
            return cls

        return decorator


# 로깅 설정
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


class ExpressionType(Enum):
    """표현 유형"""

    JUDGMENT = "judgment"  # 판단 결과
    THOUGHT_FLOW = "thought_flow"  # 사고 흐름
    DECISION_TREE = "decision_tree"  # 결정 트리
    REASONING = "reasoning"  # 추론 과정
    INTEGRATED = "integrated"  # 통합 표현


class ExpressionStyle(Enum):
    """표현 스타일"""

    FORMAL = "formal"  # 공식적
    CASUAL = "casual"  # 친근한
    PROFESSIONAL = "professional"  # 전문적
    EMPATHETIC = "empathetic"  # 공감적
    ANALYTICAL = "analytical"  # 분석적


@dataclass
class ExpressionContext:
    """표현 컨텍스트"""

    expression_type: ExpressionType
    style: ExpressionStyle
    confidence: float
    context_data: Dict[str, Any]
    user_context: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class ExpressionResult:
    """표현 결과"""

    expression_text: str
    confidence: float
    style: ExpressionStyle
    expression_type: ExpressionType
    processing_time: float
    success: bool = True
    error_message: Optional[str] = None


@register_module(
    name="duri_expression_engine",
    dependencies=[],
    priority=ModulePriority.HIGH,
    version="1.0.0",
    description="DuRi의 판단 결과를 자연어로 변환하는 엔진",
    author="DuRi",
)
class DuRiExpressionEngine(BaseModule):
    """DuRi의 판단 결과를 자연어로 변환하는 엔진"""

    # 자동 등록을 위한 속성들 (메타클래스 방식)
    module_name = "duri_expression_engine"
    dependencies = []
    priority = ModulePriority.HIGH
    version = "1.0.0"
    description = "DuRi의 판단 결과를 자연어로 변환하는 엔진"
    author = "DuRi"

    def __init__(self):
        super().__init__()

        # 표현 템플릿 초기화
        self.expression_templates = self._initialize_templates()

        # 표현 스타일 설정
        self.default_style = ExpressionStyle.CASUAL

        # 신뢰도 임계값
        self.confidence_threshold = 0.5

        # 표현 히스토리
        self.expression_history: List[ExpressionResult] = []

        logger.info("DuRiExpressionEngine 초기화 완료")

    async def initialize(self) -> None:
        """모듈 초기화"""
        if self._initialized:
            logger.info("DuRiExpressionEngine이 이미 초기화되어 있습니다.")
            return

        logger.info("DuRiExpressionEngine 초기화 시작")

        try:
            # 템플릿 검증
            self._validate_templates()

            # 표현 스타일 초기화
            self._initialize_expression_styles()

            self._initialized = True
            logger.info("✅ DuRiExpressionEngine 초기화 완료")

        except Exception as e:
            logger.error(f"❌ DuRiExpressionEngine 초기화 실패: {e}")
            raise

    async def execute(self, context: Dict[str, Any]) -> Any:
        """모듈 실행"""
        if not self._initialized:
            await self.initialize()

        try:
            # 입력 데이터 추출
            judgment_data = context.get("judgment_trace")
            thought_flow = context.get("thought_flow")
            decision_tree = context.get("decision_tree")

            # 표현 타입 결정
            expression_type = self._determine_expression_type(context)

            # 표현 스타일 결정
            style = context.get("style", self.default_style)
            if isinstance(style, str):
                style = ExpressionStyle(style)

            # 표현 컨텍스트 생성
            expression_context = ExpressionContext(
                expression_type=expression_type,
                style=style,
                confidence=context.get("confidence", 0.7),
                context_data=context,
                user_context=context.get("user_context"),
            )

            # 자연어 변환
            result = await self.express_judgment(
                judgment_data=judgment_data,
                thought_flow=thought_flow,
                decision_tree=decision_tree,
                context=expression_context,
            )

            return result

        except Exception as e:
            logger.error(f"❌ DuRiExpressionEngine 실행 실패: {e}")
            return {"status": "error", "message": f"표현 생성 중 오류 발생: {str(e)}"}

    async def express_judgment(
        self,
        judgment_data: Optional[Dict[str, Any]] = None,
        thought_flow: Optional[Dict[str, Any]] = None,
        decision_tree: Optional[Dict[str, Any]] = None,
        context: Optional[ExpressionContext] = None,
        style: Optional[Union[ExpressionStyle, str]] = None,
    ) -> ExpressionResult:
        """판단 결과를 자연어로 표현"""
        start_time = time.time()

        try:
            logger.info("🎯 DuRi 판단 결과 자연어 변환 시작")

            # 표현 컨텍스트 생성
            if context is None:
                # 스타일 처리
                if isinstance(style, str):
                    try:
                        style = ExpressionStyle(style)
                    except ValueError:
                        style = self.default_style
                elif style is None:
                    style = self.default_style

                context = ExpressionContext(
                    expression_type=self._determine_expression_type(
                        {
                            "judgment_trace": judgment_data,
                            "thought_flow": thought_flow,
                            "decision_tree": decision_tree,
                        }
                    ),
                    style=style,
                    confidence=0.7,
                    context_data={},
                )

            # 핵심 판단 포인트 추출
            key_points = await self._extract_key_points(judgment_data, thought_flow, decision_tree)

            # 자연어 템플릿 선택
            template = self._select_template(context.expression_type, context.style)

            # 문장 구성
            expression_text = await self._construct_expression(key_points, template, context)

            # DuRi 명의로 출력 형식 지정
            final_expression = f"DuRi: {expression_text}"

            processing_time = time.time() - start_time

            result = ExpressionResult(
                expression_text=final_expression,
                confidence=context.confidence,
                style=context.style,
                expression_type=context.expression_type,
                processing_time=processing_time,
                success=True,
            )

            # 표현 히스토리에 추가
            self.expression_history.append(result)

            logger.info(f"✅ DuRi 표현 생성 완료: {final_expression[:50]}...")
            return result

        except Exception as e:
            logger.error(f"❌ 판단 결과 표현 실패: {e}")
            processing_time = time.time() - start_time

            return ExpressionResult(
                expression_text="DuRi: 죄송해요, 지금은 제대로 생각을 정리하지 못했어요.",
                confidence=0.0,
                style=context.style if context else self.default_style,
                expression_type=(context.expression_type if context else ExpressionType.INTEGRATED),
                processing_time=processing_time,
                success=False,
                error_message=str(e),
            )

    async def _extract_key_points(
        self,
        judgment_data: Optional[Dict[str, Any]],
        thought_flow: Optional[Dict[str, Any]],
        decision_tree: Optional[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """핵심 판단 포인트 추출"""
        key_points = {
            "decision": None,
            "reasoning": None,
            "confidence": 0.0,
            "alternatives": [],
            "context": {},
            "insights": [],
        }

        # JudgmentTrace에서 추출
        if judgment_data:
            key_points["decision"] = judgment_data.get("decision", "")
            key_points["reasoning"] = judgment_data.get("reasoning", "")
            key_points["confidence"] = judgment_data.get("confidence", 0.0)
            key_points["alternatives"] = judgment_data.get("alternatives", [])
            key_points["context"] = judgment_data.get("context", {})

        # ThoughtFlow에서 추출
        if thought_flow:
            if "final_decision" in thought_flow:
                key_points["decision"] = thought_flow["final_decision"]
            if "thought_process" in thought_flow:
                key_points["reasoning"] = self._extract_reasoning_from_thought_flow(thought_flow["thought_process"])
            if "reflection_result" in thought_flow:
                key_points["insights"].append(thought_flow["reflection_result"])

        # DecisionTree에서 추출
        if decision_tree:
            if "final_decision" in decision_tree:
                key_points["decision"] = decision_tree["final_decision"]
            if "reasoning_path" in decision_tree:
                key_points["reasoning"] = decision_tree["reasoning_path"]

        return key_points

    def _extract_reasoning_from_thought_flow(self, thought_process: List[Dict[str, Any]]) -> str:
        """사고 흐름에서 추론 과정 추출"""
        reasoning_parts = []

        for step in thought_process:
            if "reasoning" in step:
                reasoning_parts.append(step["reasoning"])
            elif "decision" in step:
                reasoning_parts.append(step["decision"])

        return " ".join(reasoning_parts) if reasoning_parts else ""

    def _determine_expression_type(self, context: Dict[str, Any]) -> ExpressionType:
        """표현 타입 결정"""
        if context.get("judgment_trace"):
            return ExpressionType.JUDGMENT
        elif context.get("thought_flow"):
            return ExpressionType.THOUGHT_FLOW
        elif context.get("decision_tree"):
            return ExpressionType.DECISION_TREE
        else:
            return ExpressionType.INTEGRATED

    def _select_template(self, expression_type: ExpressionType, style: ExpressionStyle) -> Dict[str, str]:
        """자연어 템플릿 선택"""
        templates = self.expression_templates.get(expression_type, {})
        return templates.get(style, templates.get(ExpressionStyle.CASUAL, {}))

    async def _construct_expression(
        self,
        key_points: Dict[str, Any],
        template: Dict[str, str],
        context: ExpressionContext,
    ) -> str:
        """문장 구성"""
        try:
            # 기본 템플릿 선택
            base_template = template.get("base", "나는 {decision}라고 생각해요.")

            # 신뢰도에 따른 표현 조정
            confidence_expression = self._get_confidence_expression(key_points["confidence"])

            # 추론 과정 포함 여부 결정
            if key_points["reasoning"] and len(key_points["reasoning"]) > 10:
                reasoning_template = template.get("with_reasoning", "왜냐하면 {reasoning}이기 때문이에요.")
                reasoning_part = reasoning_template.format(reasoning=key_points["reasoning"])
            else:
                reasoning_part = ""

            # 대안 고려 여부 결정
            alternatives_part = ""
            if key_points["alternatives"] and len(key_points["alternatives"]) > 0:
                alternatives_template = template.get(
                    "with_alternatives",
                    "다른 방법도 고려했지만, {alternatives}보다는 이 방법이 더 적절하다고 판단했어요.",
                )
                alternatives_text = ", ".join(key_points["alternatives"][:2])  # 최대 2개만
                alternatives_part = alternatives_template.format(alternatives=alternatives_text)

            # 최종 문장 구성
            expression_parts = []

            # 메인 판단
            main_judgment = base_template.format(
                decision=key_points["decision"] or "이 상황을 분석한 결과",
                confidence=confidence_expression,
            )
            expression_parts.append(main_judgment)

            # 추론 과정
            if reasoning_part:
                expression_parts.append(reasoning_part)

            # 대안 고려
            if alternatives_part:
                expression_parts.append(alternatives_part)

            # 통합
            final_expression = " ".join(expression_parts)

            # 문장 정리 (중복 제거, 자연스러운 연결)
            final_expression = self._cleanup_expression(final_expression)

            return final_expression

        except Exception as e:
            logger.error(f"문장 구성 실패: {e}")
            return "나는 이 상황에 대해 생각해봤어요."

    def _get_confidence_expression(self, confidence: float) -> str:
        """신뢰도에 따른 표현 반환"""
        if confidence >= 0.8:
            return "확실히"
        elif confidence >= 0.6:
            return "대체로"
        elif confidence >= 0.4:
            return "아마도"
        else:
            return "잘 모르겠지만"

    def _cleanup_expression(self, expression: str) -> str:
        """표현 정리"""
        # 중복 공백 제거
        expression = re.sub(r"\s+", " ", expression)

        # 문장 부호 정리
        expression = expression.strip()

        # 자연스러운 연결을 위한 조정
        expression = expression.replace("요.요.", "요.")
        expression = expression.replace("요.요", "요.")

        return expression

    def _initialize_templates(
        self,
    ) -> Dict[ExpressionType, Dict[ExpressionStyle, Dict[str, str]]]:
        """표현 템플릿 초기화"""
        return {
            ExpressionType.JUDGMENT: {
                ExpressionStyle.CASUAL: {
                    "base": "나는 {decision}라고 생각해요.",
                    "with_reasoning": "왜냐하면 {reasoning}이기 때문이에요.",
                    "with_alternatives": "다른 방법도 고려했지만, {alternatives}보다는 이 방법이 더 적절하다고 판단했어요.",  # noqa: E501
                },
                ExpressionStyle.FORMAL: {
                    "base": "제 분석 결과, {decision}입니다.",
                    "with_reasoning": "이는 {reasoning} 때문입니다.",
                    "with_alternatives": "다른 대안들({alternatives})도 검토했으나, 현재 방법이 가장 적절하다고 판단됩니다.",  # noqa: E501
                },
                ExpressionStyle.EMPATHETIC: {
                    "base": "이 상황을 보니 {decision}라고 느껴요.",
                    "with_reasoning": "그런 생각이 드는 이유는 {reasoning}이거든요.",
                    "with_alternatives": "다른 방법들도 생각해봤지만, {alternatives}보다는 이 방법이 더 나을 것 같아요.",  # noqa: E501
                },
            },
            ExpressionType.THOUGHT_FLOW: {
                ExpressionStyle.CASUAL: {
                    "base": "생각해보니 {decision}인 것 같아요.",
                    "with_reasoning": "이유는 {reasoning}이에요.",
                    "with_alternatives": "다른 생각도 했지만, {alternatives}보다는 이게 맞다고 봐요.",
                }
            },
            ExpressionType.DECISION_TREE: {
                ExpressionStyle.CASUAL: {
                    "base": "여러 가지를 고려한 결과, {decision}로 결정했어요.",
                    "with_reasoning": "결정 과정에서 {reasoning}을 중요하게 생각했어요.",
                    "with_alternatives": "다른 선택지들({alternatives})도 있었지만, 이 방법을 선택했어요.",
                }
            },
            ExpressionType.INTEGRATED: {
                ExpressionStyle.CASUAL: {
                    "base": "종합적으로 생각해보니 {decision}인 것 같아요.",
                    "with_reasoning": "그런 판단을 내린 이유는 {reasoning}이에요.",
                    "with_alternatives": "다른 방법들도 고려했지만, {alternatives}보다는 이 방법이 더 적절하다고 봐요.",
                }
            },
        }

    def _validate_templates(self):
        """템플릿 검증"""
        for expression_type, styles in self.expression_templates.items():
            for style, templates in styles.items():
                if "base" not in templates:
                    logger.warning(f"템플릿에 'base' 키가 없음: {expression_type}.{style}")

    def _initialize_expression_styles(self):
        """표현 스타일 초기화"""
        # 스타일별 특성 설정
        self.style_characteristics = {
            ExpressionStyle.CASUAL: {"formality": 0.2, "empathy": 0.8, "clarity": 0.7},
            ExpressionStyle.FORMAL: {"formality": 0.9, "empathy": 0.3, "clarity": 0.9},
            ExpressionStyle.EMPATHETIC: {
                "formality": 0.3,
                "empathy": 0.9,
                "clarity": 0.6,
            },
        }

    async def get_expression_history(self) -> List[ExpressionResult]:
        """표현 히스토리 반환"""
        return self.expression_history.copy()

    async def clear_expression_history(self):
        """표현 히스토리 초기화"""
        self.expression_history.clear()
        logger.info("표현 히스토리 초기화 완료")


# 편의 함수
async def express_duri_judgment(
    judgment_data: Optional[Dict[str, Any]] = None,
    thought_flow: Optional[Dict[str, Any]] = None,
    decision_tree: Optional[Dict[str, Any]] = None,
    style: str = "casual",
) -> str:
    """DuRi의 판단을 자연어로 표현하는 편의 함수"""
    engine = DuRiExpressionEngine()
    await engine.initialize()

    context = {
        "judgment_trace": judgment_data,
        "thought_flow": thought_flow,
        "decision_tree": decision_tree,
        "style": style,
    }

    result = await engine.execute(context)

    if isinstance(result, ExpressionResult):
        return result.expression_text
    else:
        return result.get("message", "DuRi: 표현을 생성할 수 없어요.")
