from DuRiCore.trace import emit_trace
import json, os, sys, time, uuid
STRICT = os.getenv('TRACE_MODE', 'strict').lower() == 'strict'

def new_trace_id() -> str:
    return uuid.uuid4().hex[:16]

def emit_trace(envelope: dict, *, stream=sys.stdout, flush_threshold=32):
    envelope.setdefault('audit', {})
    env_audit = envelope['audit']
    env_audit.setdefault('version', 'trace-v2')
    env_audit.setdefault('ts', time.strftime('%Y-%m-%dT%H:%M:%S%z'))
    env_audit.setdefault('trace_id', new_trace_id())
    _buf = []
    _buf.append(json.dumps(envelope, ensure_ascii=False))
    if len(_buf) >= flush_threshold:
        stream.write('\n'.join(_buf) + '\n')
        stream.flush()
        _buf.clear()
    else:
        stream.write(json.dumps(envelope, ensure_ascii=False) + '\n')
        stream.flush()

def to_trace(input_obj, intent: str, decision: dict, *, options=None, rationale=None, uncertainty=None, next_action: str='') -> dict:
    return {'input': input_obj, 'intent': intent, 'options': options or [], 'decision': decision, 'rationale': rationale or [], 'uncertainty': uncertainty or {}, 'next_action': next_action, 'audit': {}}

