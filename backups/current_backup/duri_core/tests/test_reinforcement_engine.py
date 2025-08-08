import os
import json
import random
import shutil
import tempfile
import pytest
from brain.reinforcement_engine import ReinforcementEngine
from duri_common.config.config import Config

TEST_STATS = {
    "happy_dance": {"emotion": "happy", "action": "dance", "success_count": 8, "fail_count": 2, "total_count": 10, "success_rate": 0.8},
    "happy_comfort": {"emotion": "happy", "action": "comfort", "success_count": 8, "fail_count": 2, "total_count": 10, "success_rate": 0.8},
    "happy_explain": {"emotion": "happy", "action": "explain", "success_count": 2, "fail_count": 8, "total_count": 10, "success_rate": 0.2},
    "sad_comfort": {"emotion": "sad", "action": "comfort", "success_count": 9, "fail_count": 1, "total_count": 10, "success_rate": 0.9},
    "sad_dance": {"emotion": "sad", "action": "dance", "success_count": 1, "fail_count": 9, "total_count": 10, "success_rate": 0.1},
}

@pytest.fixture(scope="module")
def setup_test_stats():
    # 임시 디렉토리 생성
    temp_dir = tempfile.mkdtemp()
    stats_path = os.path.join(temp_dir, "experience_stats.json")
    with open(stats_path, "w", encoding="utf-8") as f:
        json.dump(TEST_STATS, f, indent=2, ensure_ascii=False)
    # 환경변수로 EVOLUTION_DIR 지정
    old_evolution_dir = os.environ.get("EVOLUTION_DIR")
    os.environ["EVOLUTION_DIR"] = temp_dir
    yield stats_path
    # 정리
    if old_evolution_dir is not None:
        os.environ["EVOLUTION_DIR"] = old_evolution_dir
    else:
        del os.environ["EVOLUTION_DIR"]
    shutil.rmtree(temp_dir)


def test_greedy_policy(setup_test_stats):
    """
    ε=0.0 (탐험 없음)일 때 항상 성공률이 가장 높은 행동만 선택하는지 테스트
    happy: dance, comfort (동률)
    sad: comfort
    """
    engine = ReinforcementEngine(epsilon=0.0)
    # happy: dance, comfort 둘 다 0.8, 둘 중 하나만 나와야 함
    results = set(engine.choose_action("happy") for _ in range(20))
    assert results.issubset({"dance", "comfort"})
    assert len(results) == 2  # 동률 랜덤성 확인
    # sad: comfort만 0.9
    for _ in range(10):
        assert engine.choose_action("sad") == "comfort"


def test_random_policy(setup_test_stats):
    """
    ε=1.0 (항상 탐험)일 때 happy의 모든 행동이 고르게 나오는지 테스트
    """
    engine = ReinforcementEngine(epsilon=1.0)
    actions = set()
    for _ in range(50):
        actions.add(engine.choose_action("happy"))
    # happy의 모든 행동이 나와야 함
    assert actions == {"dance", "comfort", "explain"}


def test_epsilon_greedy_balance(setup_test_stats):
    """
    ε=0.5일 때 탐험/최적 행동 비율이 대략 1:1에 가까운지 테스트
    """
    engine = ReinforcementEngine(epsilon=0.5)
    counts = {"dance": 0, "comfort": 0, "explain": 0}
    for _ in range(200):
        a = engine.choose_action("happy")
        counts[a] += 1
    # dance/comfort(최적)와 explain(비최적)이 모두 일정 비율 이상 나와야 함
    assert counts["explain"] > 20  # 10% 이상
    assert counts["dance"] > 20
    assert counts["comfort"] > 20


def test_no_experience_returns_random(setup_test_stats):
    """
    경험 데이터가 없는 감정이면 전체 행동 중 무작위 선택
    """
    engine = ReinforcementEngine(epsilon=0.0)
    possible = set(engine.actions)
    results = set(engine.choose_action("unknown_emotion") for _ in range(20))
    assert results.issubset(possible)
    assert len(results) > 0 