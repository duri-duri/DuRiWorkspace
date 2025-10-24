from insight.pipeline import PromptPipeline


def test_cleaning_effectiveness():
    """정제 효과 테스트"""
    pipeline = PromptPipeline()

    # 테스트 후보들 (중복, 짧은 것, 금칙어 포함)
    candidates = [
        "This is a very short text",  # 너무 짧음
        "Creative solution for rehabilitation",  # 정상
        "Another creative solution for rehabilitation",  # 중복 가능성
        "This is spam content",  # 금칙어
        "Innovative approach with detailed methodology and comprehensive analysis",  # 정상
        "",  # 빈 문자열
        "   ",  # 공백만
        "Very long text " * 100,  # 너무 김
    ]

    cleaned = pipeline.clean_candidates(candidates)

    # 정제 후에는 유효한 후보만 남아야 함
    assert len(cleaned) > 0
    assert len(cleaned) < len(candidates)

    # 모든 정제된 후보는 길이가 적절해야 함
    for candidate in cleaned:
        tokens = candidate.split()  # 간단한 토큰화
        assert len(tokens) >= pipeline.cleaning_rules["min_length"]
        assert len(tokens) <= pipeline.cleaning_rules["max_length"]
        assert not any(word in candidate.lower() for word in pipeline.cleaning_rules["forbidden_words"])


def test_empty_input_exception():
    """빈 입력 예외 처리 테스트"""
    pipeline = PromptPipeline()

    # 빈 후보 리스트 (명시적으로 빈 리스트 전달)
    result = pipeline.process_pipeline("test prompt", candidates=[])

    # 빈 리스트를 전달하면 정제 후 아무것도 남지 않음
    assert result["cleaned_count"] == 0
    assert result["original_count"] == 0
    assert "error" in result
    assert result["rankings"] == []

    # None 후보
    result = pipeline.process_pipeline("test prompt", candidates=None)

    # None이면 기본 후보 생성되므로 에러가 아님
    assert result["cleaned_count"] > 0
    assert "error" not in result


def test_ranking_stability():
    """상위안 안정성 테스트"""
    pipeline = PromptPipeline()

    # 동일한 후보들로 여러 번 실행
    candidates = [
        "Innovative rehabilitation technique with comprehensive methodology and detailed analysis",
        "Creative approach to physical therapy using novel equipment and advanced techniques",
        "Advanced therapeutic intervention with evidence-based practice and comprehensive evaluation",
    ]

    results = []
    for _ in range(3):
        result = pipeline.process_pipeline("rehabilitation therapy", candidates=candidates)
        results.append(result)

    # 모든 실행에서 동일한 순위가 나와야 함
    for i in range(1, len(results)):
        assert results[i]["rankings"] == results[0]["rankings"]

    # 상위안이 존재해야 함
    assert len(results[0]["rankings"]) > 0
    # 점수 비교 (enhanced_evaluation 결과 구조에 맞게)
    first_score = results[0]["rankings"][0].get("combined_score", results[0]["rankings"][0].get("score", 0))
    last_score = results[0]["rankings"][-1].get("combined_score", results[0]["rankings"][-1].get("score", 0))
    assert first_score >= last_score


def test_integration_status():
    """기존 시스템 통합 상태 테스트"""
    pipeline = PromptPipeline()

    # 통합 상태 확인
    result = pipeline.process_pipeline("test")
    assert "integration_status" in result

    # 평가 방법 확인 (정상적인 후보로 테스트)
    candidates = ["Valid candidate with sufficient length for testing"]
    result = pipeline.process_pipeline("test", candidates=candidates, use_enhanced_evaluation=True)
    assert "evaluation_method" in result
    assert result["evaluation_method"] in [
        "enhanced_integrated",
        "insight_only",
        "none",
    ]


def test_enhanced_evaluation():
    """향상된 평가 시스템 테스트"""
    pipeline = PromptPipeline()

    candidates = [
        "Comprehensive rehabilitation program with evidence-based interventions",
        "Innovative therapeutic approach using cutting-edge technology",
    ]

    # 향상된 평가 실행
    result = pipeline.process_pipeline("rehabilitation therapy", candidates=candidates, use_enhanced_evaluation=True)

    # 결과 구조 확인
    assert "rankings" in result
    assert "evaluation_method" in result
    assert "integration_status" in result

    # 순위 결과 확인
    if result["rankings"]:
        for ranking in result["rankings"]:
            assert "combined_score" in ranking
            assert "text" in ranking
