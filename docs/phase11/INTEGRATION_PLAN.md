# Phase 11 Integration Plan
목표: 자아모델 + 기본대화 + 메인루프 + 외부학습을 표준 시퀀스로 통합

## Contracts
- CoreConversation.turn(state, user_msg) -> {reply, new_state, events[]}
- SelfModel.update(trace) -> self_state_delta
- Learning.enqueue(trace) -> job_id

## Telemetry Hooks
- pre_turn, assistant_reply, inner_reflect, learn, post_turn