import requests
import time

BASE_URL = "http://localhost:8083"

def test_meta_flow():
    # 1. 기억 저장 (short)
    memory = {
        "type": "test",
        "context": "meta_flow_test",
        "content": "자동화 테스트용 기억입니다.",
        "source": "pytest",
        "tags": ["meta", "test"],
        "importance_score": 77
    }
    r = requests.post(f"{BASE_URL}/memory/save", json=memory)
    print("STEP 1 (memory save):", r.status_code, r.text)
    assert r.status_code == 200
    memory_id = r.json()["memory"]["id"]

    # 2. 진실(Truth) 저장
    truth = memory.copy()
    truth["content"] = "이것은 진실입니다."
    truth["memory_level"] = "truth"
    truth["importance_score"] = 99
    r = requests.post(f"{BASE_URL}/memory/save", json=truth)
    print("STEP 2 (truth save):", r.status_code, r.text)
    assert r.status_code == 200
    truth_id = r.json()["memory"]["id"]

    # 3. 판단(judge) 요청 (mock)
    situation = {
        "type": "test",
        "context": "meta_flow_test",
        "content": "이것은 진실입니다.",
        "tags": ["meta", "test"]
    }
    r = requests.post(f"{BASE_URL}/memory/judge", json=situation)
    print("STEP 3 (judge):", r.status_code, r.text)
    assert r.status_code == 200
    judgment = r.json()["judgment"]
    assert "judgment" in judgment

    # 4. 진화(evolve) 요청 (mock)
    r = requests.post(f"{BASE_URL}/memory/auto/evolve")
    print("STEP 4 (evolve):", r.status_code, r.text)
    assert r.status_code == 200
    assert r.json()["success"]

    # 5. 메타 리포트/인사이트로 결과 검증
    r = requests.get(f"{BASE_URL}/memory/meta/report")
    print("STEP 5 (meta report):", r.status_code, r.text)
    assert r.status_code == 200
    report = r.json()["report"]
    assert report["total_memories"] >= 2
    assert report["total_truths"] >= 1

    r = requests.get(f"{BASE_URL}/memory/meta/insights")
    print("STEP 6 (meta insights):", r.status_code, r.text)
    assert r.status_code == 200
    insights = r.json()["insights"]
    assert "recent_new_truths" in insights
    assert "top_tags" in insights

    # 6. 정리 (삭제)
    requests.delete(f"{BASE_URL}/memory/{memory_id}")
    requests.delete(f"{BASE_URL}/memory/{truth_id}")

if __name__ == "__main__":
    test_meta_flow()
    print("✅ meta_flow 자동화 테스트 통과!") 