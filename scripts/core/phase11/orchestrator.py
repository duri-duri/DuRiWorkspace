#!/usr/bin/env python3
from dataclasses import dataclass, field
from typing import Any, Dict, List
from datetime import datetime

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
    """Insight Engine 연동용 계측 포인트 (기존 시스템 활용)"""
    def __init__(self):
        import os
        from datetime import datetime
        # 기존 judgment_trace_store.py 패턴 활용
        self.log_dir = "DuRiCore/memory/phase11_traces"
        os.makedirs(self.log_dir, exist_ok=True)
        self.events_file = os.path.join(self.log_dir, "events.jsonl")
        self.snapshot_file = os.path.join(self.log_dir, "last_context.json")
    
    def record(self, ctx: TurnContext, event: str, payload: Dict[str, Any]) -> None:
        """기존 judgment_trace_store.py 패턴으로 JSONL 기록"""
        import json
        import time
        
        record = {
            "timestamp": time.time(),
            "datetime": datetime.now().isoformat(),
            "conv_id": ctx.conv_id,
            "event": event,
            "payload": payload,
            "phase": "phase11"
        }
        
        # JSONL 형식으로 저장 (기존 패턴 활용)
        with open(self.events_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")
        
        # 최소 가시성 (CI/디버깅용)
        print(f"[phase11::telemetry] {event} {payload}")
    
    def snapshot(self, ctx: TurnContext) -> None:
        """컨텍스트 스냅샷 저장"""
        import json
        from datetime import datetime
        
        snapshot = {
            "conv_id": ctx.conv_id,
            "messages": [{"role": m.role, "content": m.content, "meta": m.meta} for m in ctx.messages],
            "memory": ctx.memory,
            "timestamp": datetime.now().isoformat()
        }
        
        with open(self.snapshot_file, "w", encoding="utf-8") as f:
            json.dump(snapshot, f, ensure_ascii=False, indent=2)

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
        self.tm.snapshot(ctx)
        return ctx

if __name__ == "__main__":
    ctx = TurnContext(conv_id="demo-001", messages=[Message(role="user", content="안녕? 오늘 계획 세워줘!")])
    oc = Orchestrator()
    ctx = oc.run_turn(ctx)
    for m in ctx.messages:
        print(f"{m.role:>9}: {m.content}")
