import pytest
from insight.metrics import (
    tokenize, distinct_n, repeat_penalty, brevity_prior, bleu_like, composite,
    evaluate_text, evaluate_candidates
)

class TestTokenize:
    """토큰화 함수 테스트"""
    
    def test_basic_tokenization(self):
        """기본 토큰화 테스트"""
        text = "Hello world! This is a test."
        tokens = tokenize(text)
        expected = ["hello", "world", "this", "is", "a", "test"]
        assert tokens == expected

    def test_empty_text(self):
        """빈 텍스트 토큰화"""
        assert tokenize("") == []

    def test_special_characters(self):
        """특수문자 처리 테스트"""
        text = "Hello, world! 123 test@email.com"
        tokens = tokenize(text)
        expected = ["hello", "world", "123", "test", "email", "com"]
        assert tokens == expected


class TestDistinctN:
    """고유 n-gram 비율 테스트"""
    
    def test_distinct_1_basic(self):
        """distinct-1 기본 테스트"""
        text = "a b c a b"
        assert distinct_n(text, n=1) == 3/5

    def test_distinct_2_basic(self):
        """distinct-2 기본 테스트"""
        text = "a b c a b"
        # (a,b), (b,c), (c,a), (a,b) -> unique: (a,b), (b,c), (c,a)
        assert distinct_n(text, n=2) == 3/4

    def test_distinct_boundary_values(self):
        """경계값 테스트"""
        assert distinct_n("a a a", n=1) == 1/3
        assert distinct_n("a a a", n=2) == 1/2
        assert distinct_n("a b c", n=3) == 1/1
        assert distinct_n("", n=1) == 0.0

    def test_distinct_repetition(self):
        """반복이 많은 텍스트"""
        text = "the the the cat cat"
        assert distinct_n(text, n=1) == 2/5
        assert distinct_n(text, n=2) == 3/4 # (the,the), (the,cat), (cat,cat) -> unique: (the,the), (the,cat), (cat,cat)


class TestRepeatPenalty:
    """반복 패널티 테스트"""
    
    def test_no_repetition(self):
        """반복 없는 텍스트"""
        text = "the cat sat on the mat"
        penalty = repeat_penalty(text)
        # "the"가 2번 나타나므로 반복 패널티가 있음
        assert penalty > 0.0
    
    def test_high_repetition(self):
        """높은 반복"""
        text = "a a a a a"
        penalty = repeat_penalty(text)
        assert penalty == 0.8  # 4 repeated tokens out of 5
    
    def test_partial_repetition(self):
        """부분 반복"""
        text = "the the cat sat on the mat"
        penalty = repeat_penalty(text)
        # "the"가 3번 나타나므로 더 높은 패널티
        assert penalty > 0.0
    
    def test_empty_text(self):
        """빈 텍스트"""
        assert repeat_penalty("") == 0.0


class TestBrevityPrior:
    """간결성 사전 확률 테스트"""
    
    def test_target_length(self):
        """목표 길이에서 최대 점수"""
        text = "word " * 120
        assert brevity_prior(text, mu=120, sigma=60) == pytest.approx(1.0)

    def test_length_penalty(self):
        """길이 벗어날 때 패널티"""
        text_short = "word " * 60
        text_long = "word " * 180
        text_target = "word " * 120
        
        score_short = brevity_prior(text_short)
        score_long = brevity_prior(text_long)
        score_target = brevity_prior(text_target)
        
        assert score_short < score_target
        assert score_long < score_target
        assert score_short == pytest.approx(score_long) # 대칭성

    def test_empty_text(self):
        """빈 텍스트"""
        assert brevity_prior("") == 0.0

    def test_custom_parameters(self):
        """커스텀 파라미터"""
        text = "word " * 50
        assert brevity_prior(text, mu=50, sigma=10) == pytest.approx(1.0)


class TestBleuLike:
    """BLEU-like 점수 테스트"""
    
    def test_perfect_match(self):
        """완벽 매치"""
        candidate = "the cat sat on the mat"
        references = ["the cat sat on the mat"]
        assert bleu_like(candidate, references) == pytest.approx(1.0)

    def test_no_match(self):
        """매치 없음"""
        candidate = "completely different text"
        references = ["the cat sat on the mat"]
        assert bleu_like(candidate, references) == pytest.approx(0.0)

    def test_partial_match(self):
        """부분 매치"""
        candidate = "the cat sat"
        references = ["the cat sat on the mat"]
        score = bleu_like(candidate, references)
        assert 0.0 < score < 1.0
    
    def test_brevity_penalty(self):
        """간결성 패널티 테스트"""
        candidate = "the cat sat on the mat"
        short_ref = ["the cat"]
        long_ref = ["the cat sat on the mat and played"]

        score_short = bleu_like(candidate, short_ref)
        score_long = bleu_like(candidate, long_ref)

        # 두 점수 모두 유효한 범위 내에 있어야 함
        assert 0.0 <= score_short <= 1.0
        assert 0.0 <= score_long <= 1.0
    
    def test_empty_inputs(self):
        """빈 입력 테스트"""
        assert bleu_like("", ["test"]) == 0.0
        assert bleu_like("test", []) == 0.0


class TestComposite:
    """복합 점수 계산 테스트"""
    
    def test_equal_weights(self):
        """균등 가중치"""
        scores = {"a": 0.5, "b": 0.7, "c": 0.9}
        assert composite(scores) == pytest.approx((0.5 + 0.7 + 0.9) / 3)

    def test_custom_weights(self):
        """커스텀 가중치"""
        scores = {"a": 0.5, "b": 0.7, "c": 0.9}
        weights = {"a": 0.2, "b": 0.3, "c": 0.5}
        assert composite(scores, weights) == pytest.approx(0.5*0.2 + 0.7*0.3 + 0.9*0.5)

    def test_empty_scores(self):
        """빈 점수"""
        assert composite({}) == 0.0

    def test_zero_weights(self):
        """0 가중치"""
        scores = {"a": 0.5, "b": 0.7}
        weights = {"a": 0.0, "b": 0.0}
        assert composite(scores, weights) == 0.0


class TestEvaluateText:
    """evaluate_text 함수 테스트"""
    
    def test_basic_evaluation(self):
        """기본 평가"""
        text = "This is a test sentence."
        result = evaluate_text(text)
        assert "composite_score" in result
        assert 0.0 <= result["composite_score"] <= 1.0
        assert "metrics" not in result # detailed=False by default

    def test_with_references(self):
        """참조 포함 평가"""
        text = "The cat sat on the mat."
        references = ["A cat was sitting on a mat.", "The mat had a cat."]
        result = evaluate_text(text, references=references, detailed=True)
        assert "composite_score" in result
        assert "metrics" in result
        assert "bleu_like" in result["metrics"]
        assert 0.0 <= result["metrics"]["bleu_like"] <= 1.0


class TestEvaluateCandidates:
    """evaluate_candidates 함수 테스트"""
    
    def test_ranking_consistency(self):
        """순위 일관성"""
        candidates = [
            "The quick brown fox jumps over the lazy dog.",
            "A fast brown fox leaps over a sleepy canine.",
            "The dog is lazy."
        ]
        references = ["A quick brown fox jumps over the lazy dog."]
        results = evaluate_candidates(candidates, references=references)
        
        assert len(results) == 3
        assert results[0]["composite_score"] >= results[1]["composite_score"]
        assert results[1]["composite_score"] >= results[2]["composite_score"]
        assert "metrics" not in results[0] # detailed=False by default

    def test_custom_weights(self):
        """커스텀 가중치"""
        candidates = ["short text", "a longer text with more words"]
        weights = {"distinct_1": 0.5, "brevity_prior": 0.5}
        results = evaluate_candidates(candidates, weights=weights, detailed=True)
        
        assert len(results) == 2
        assert "metrics" in results[0] # detailed=True
        assert "distinct_1" in results[0]["metrics"]
        assert "brevity_prior" in results[0]["metrics"]