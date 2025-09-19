from pathlib import Path
import json
import runpy

def test_phase11_contract_minimal():
    """기존 contracts/test_reasoning_contract.py 패턴 활용"""
    # 오케스트레이터 실행
    runpy.run_path(str(Path("scripts/core/phase11/orchestrator.py")))
    
    # JSONL 이벤트 파일 생성 확인
    events_file = Path("DuRiCore/memory/phase11_traces/events.jsonl")
    assert events_file.exists(), "events.jsonl 파일이 생성되어야 합니다"
    
    # 이벤트 내용 검증
    lines = events_file.read_text(encoding="utf-8").strip().splitlines()
    assert len(lines) > 0, "이벤트 로그가 기록되어야 합니다"
    
    # 필수 이벤트 확인
    events = [json.loads(line) for line in lines]
    event_types = [event["event"] for event in events]
    
    assert "assistant_reply" in event_types, "assistant_reply 이벤트가 있어야 합니다"
    assert "inner_reflect" in event_types, "inner_reflect 이벤트가 있어야 합니다"
    assert "learn" in event_types, "learn 이벤트가 있어야 합니다"
    
    # 컨텍스트 스냅샷 파일 확인
    snapshot_file = Path("DuRiCore/memory/phase11_traces/last_context.json")
    assert snapshot_file.exists(), "컨텍스트 스냅샷 파일이 생성되어야 합니다"
    
    # 스냅샷 내용 검증
    snapshot = json.loads(snapshot_file.read_text(encoding="utf-8"))
    assert "conv_id" in snapshot, "스냅샷에 conv_id가 있어야 합니다"
    assert "messages" in snapshot, "스냅샷에 messages가 있어야 합니다"
    assert "memory" in snapshot, "스냅샷에 memory가 있어야 합니다"
