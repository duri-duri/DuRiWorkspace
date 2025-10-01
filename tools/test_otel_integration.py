#!/usr/bin/env python3
"""
OTel 통합 직접 테스트 스크립트
JudgmentTraceSystem의 span 래핑과 로그 상관키 주입을 검증합니다.
"""

import json
import logging
import os
import sys

# 경로 설정
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

# 로깅 설정 (기본 로그 출력)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    style="%",
)

from duri_core.core.metrics import maybe_expose_metrics_port

# OTel 초기화
from ops.observability.otel_init import get_tracer, init_tracing


def test_otel_integration():
    """OTel 통합 테스트"""
    print("🚀 OTel 통합 테스트 시작")

    # 1. OTel 초기화
    print("\n1️⃣ OTel 초기화...")
    init_tracing(service_name="duri-core")
    tracer = get_tracer("duri.test")
    print("✅ OTel 초기화 완료")

    # 2. 메트릭 포트 노출 (선택적)
    print("\n2️⃣ 메트릭 포트 설정...")
    port = maybe_expose_metrics_port()
    if port:
        print(f"✅ 메트릭 포트 {port}에서 노출")
    else:
        print("ℹ️ 메트릭 포트 미설정 (PROM_PORT 환경변수 필요)")

    # 3. 직접 span 생성 및 로그 테스트
    print("\n3️⃣ 직접 span 생성 및 로그 테스트...")

    with tracer.start_as_current_span("test.plan") as span:
        span.set_attribute("test.phase", "plan")
        span.set_attribute("test.type", "integration")

        # 현재 span context에서 trace_id, span_id 추출
        ctx = span.get_span_context()
        trace_id = f"{ctx.trace_id:032x}"
        span_id = f"{ctx.span_id:016x}"

        print(f"📊 Span 생성됨: trace_id={trace_id}, span_id={span_id}")

        # 로그에 trace_id, span_id 주입
        logger = logging.getLogger("test.otel")
        logger.info(
            "test_plan_completed",
            extra={"trace_id": trace_id, "span_id": span_id, "phase": "plan"},
        )

        # 중첩 span 테스트
        with tracer.start_as_current_span("test.edit") as edit_span:
            edit_span.set_attribute("test.phase", "edit")

            edit_ctx = edit_span.get_span_context()
            edit_trace_id = f"{edit_ctx.trace_id:032x}"
            edit_span_id = f"{edit_ctx.span_id:016x}"

            print(
                f"📊 중첩 Span 생성됨: trace_id={edit_trace_id}, span_id={edit_span_id}"
            )

            logger.info(
                "test_edit_completed",
                extra={
                    "trace_id": edit_trace_id,
                    "span_id": edit_span_id,
                    "phase": "edit",
                },
            )

    # 4. JudgmentTraceSystem 테스트
    print("\n4️⃣ JudgmentTraceSystem 테스트...")
    try:
        from duri_core.tracing.judgment_trace_system import (
            JudgmentTraceSystem,
            JudgmentType,
        )

        trace_system = JudgmentTraceSystem()

        # 판단 추적 시작
        trace_id = trace_system.start_judgment_trace(
            judgment_id="test_001",
            judgment_type=JudgmentType.LOGICAL,
            context_data={"test": True},
        )

        print(f"✅ 판단 추적 시작: {trace_id}")

        # 판단 단계 추가 (OTel span 래핑됨)
        success = trace_system.add_judgment_step(
            trace_id=trace_id,
            step_name="test",
            input_data={"input": "test"},
            output_data={"output": "success"},
            reasoning="OTel 통합 테스트",
            confidence_score=0.95,
        )

        print(f"✅ 판단 단계 추가: {success}")

        # 판단 추적 완료
        success = trace_system.complete_judgment_trace(
            trace_id=trace_id, final_decision="OTel 통합 성공", final_confidence=0.95
        )

        print(f"✅ 판단 추적 완료: {success}")

    except Exception as e:
        print(f"❌ JudgmentTraceSystem 테스트 실패: {e}")
        import traceback

        traceback.print_exc()

    print("\n🎯 OTel 통합 테스트 완료")

    # 5. 로그 검증 안내
    print("\n📋 로그 검증 방법:")
    print("1. 위 로그에서 trace_id, span_id, phase 필드 확인")
    print("2. 메트릭 확인: curl localhost:9108/metrics | grep latency_seconds")
    print("3. OTLP 엔드포인트 확인: http://localhost:4318/v1/traces")


if __name__ == "__main__":
    test_otel_integration()
