#!/usr/bin/env python3
from dataclasses import dataclass, field
from typing import Any, Dict, List

@dataclass
class Message:
    role: str            # "user" | "assistant" | "system" | "inner"
    content: str
    meta: Dict[str, Any] = field(default_factory=dict)

@dataclass
class TurnContext:
    conv_id: str
    messages: List[Message]
    memory: Dict[str, Any] = field(default_factory=dict)

class DuRiCoreAdapter:
    """DuRiCore 통합 대화 서비스 어댑터 (실시스템 바인딩 지점)"""
    def reply(self, ctx: TurnContext) -> Message:
        last_user = next((m for m in reversed(ctx.messages) if m.role=="user"), None)
        text = (last_user.content if last_user else "…")
        return Message(role="assistant", content=f"[core] {text}")

class InnerThoughtAdapter:
    """내부 사고/자기성찰 시스템 어댑터 (실시스템 바인딩 지점)"""
    def reflect(self, ctx: TurnContext, last_assistant: Message) -> Message:
        return Message(role="inner", content=f"(성찰) '{last_assistant.content}' 적절성 점검 완료")

class ExternalLearningAdapter:
    """외부 학습 파이프라인 (크롤/임베딩/인덱싱 바인딩 지점)"""
    def learn(self, ctx: TurnContext) -> Dict[str, Any]:
        return {"learned": True}

class Telemetry:
    """Insight Engine 연동용 계측 포인트 (실제 점수 기록 지점)"""
    def record(self, ctx: TurnContext, event: str, payload: Dict[str, Any]) -> None:
        # TODO: insight/ 모듈 호출해 점수 산출/저장
        # print(f"[tm] {event} {payload}")  # 필요시 임시 로그
        pass

class Orchestrator:
    def __init__(self):
        self.core = DuRiCoreAdapter()
        self.inner = InnerThoughtAdapter()
        self.learnr = ExternalLearningAdapter()
        self.tm = Telemetry()

    def run_turn(self, ctx: TurnContext) -> TurnContext:
        self.tm.record(ctx, "pre_turn", {"n_msgs": len(ctx.messages)})

        # 1) Core 응답
        assistant = self.core.reply(ctx)
        ctx.messages.append(assistant)
        self.tm.record(ctx, "assistant_reply", {"text": assistant.content})

        # 2) 내부 사고(성찰)
        inner = self.inner.reflect(ctx, assistant)
        ctx.messages.append(inner)
        self.tm.record(ctx, "inner_reflect", {"text": inner.content})

        # 3) 외부 학습(비동기 가능)
        learn = self.learnr.learn(ctx)
        ctx.memory["learn"] = learn
        self.tm.record(ctx, "learn", learn)

        self.tm.record(ctx, "post_turn", {"n_msgs": len(ctx.messages)})
        return ctx

if __name__ == "__main__":
    ctx = TurnContext(conv_id="demo-001", messages=[Message(role="user", content="안녕? 오늘 계획 세워줘!")])
    oc = Orchestrator()
    ctx = oc.run_turn(ctx)
    for m in ctx.messages:
        print(f"{m.role:>9}: {m.content}")
