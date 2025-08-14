import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ART  = ROOT / "artifacts_phase1"

def _load_json_latest(glob):
    p = max((ART).glob(glob), key=lambda x: x.stat().st_mtime)
    return json.load(open(p))

def test_fixed_split_indices_consistent():
    # Phase1ProblemSolver에서 저장한 split 인덱스 파일을 사용 (이름은 프로젝트에 맞춰 조정)
    # 예: artifacts_phase1/fixed_split_indices.json
    split_file = ART / "fixed_split_indices.json"
    assert split_file.exists(), "fixed split indices가 저장되지 않았습니다."

    indices = json.load(open(split_file))
    for k in ("train_idx","valid_idx","test_idx"):
        assert k in indices and isinstance(indices[k], list) and len(indices[k])>0

    # 최신 실행의 evidence에도 같은 인덱스가 기록되어 있다고 가정하면 비교(없으면 스킵)
    ev_path = max(ART.glob("evidence_*.json"), key=lambda p: p.stat().st_mtime)
    evidence = json.load(open(ev_path))
    ev_idx = evidence.get("split_indices", {})
    if ev_idx:
        assert indices["train_idx"] == ev_idx["train_idx"]
        assert indices["valid_idx"] == ev_idx["valid_idx"]
        assert indices["test_idx"]  == ev_idx["test_idx"]



