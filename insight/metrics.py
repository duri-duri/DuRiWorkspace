from typing import List, Dict, Any, Optional
import math
from collections import Counter
import re

def tokenize(text: str) -> List[str]:
    """텍스트를 소문자 토큰 리스트로 변환"""
    # 알파벳과 숫자만 포함하는 토큰 추출
    tokens = re.findall(r'\b[a-zA-Z0-9]+\b', text.lower())
    return tokens


def distinct_n(text: str, n: int = 1) -> float:
    """
    고유 n-gram 비율 계산
    
    Args:
        text: 입력 텍스트
        n: n-gram 크기
    
    Returns:
        고유 n-gram 비율 (0.0 ~ 1.0)
    """
    tokens = tokenize(text)
    if not tokens:
        return 0.0
    
    ngrams = [tuple(tokens[i:i+n]) for i in range(len(tokens) - n + 1)]
    if not ngrams:
        return 0.0
    
    unique_ngrams = len(set(ngrams))
    total_ngrams = len(ngrams)
    
    return unique_ngrams / total_ngrams


def repeat_penalty(text: str) -> float:
    """
    반복 토큰 패널티 계산
    
    Args:
        text: 입력 텍스트
    
    Returns:
        반복 패널티 점수 (0.0 ~ 1.0, 높을수록 반복 많음)
    """
    tokens = tokenize(text)
    if not tokens:
        return 0.0
    
    token_counts = Counter(tokens)
    total_tokens = len(tokens)
    
    # 반복 토큰의 비율 계산 (정확한 계산)
    repeated_count = 0
    for count in token_counts.values():
        if count > 1:
            repeated_count += count - 1  # 첫 번째는 제외하고 나머지만 반복으로 계산
    
    penalty = repeated_count / total_tokens
    return min(1.0, penalty)


def brevity_prior(text: str, mu: int = 120, sigma: int = 60) -> float:
    """
    길이 가우시안 prior 계산
    
    Args:
        text: 입력 텍스트
        mu: 목표 길이 (평균)
        sigma: 표준 편차
    
    Returns:
        간결성 사전 확률 (0.0 ~ 1.0)
    """
    length = len(tokenize(text))
    if length == 0:
        return 0.0
    
    exponent = -0.5 * ((length - mu) / sigma) ** 2
    score = math.exp(exponent)
    
    return score


def bleu_like(candidate: str, references: List[str], n: int = 4) -> float:
    """
    간단한 BLEU-like 점수 계산 (외부 의존 없음)
    
    Args:
        candidate: 후보 텍스트
        references: 참조 텍스트 리스트
        n: 최대 n-gram 크기
    
    Returns:
        BLEU-like 점수 (0.0 ~ 1.0)
    """
    candidate_tokens = tokenize(candidate)
    if not candidate_tokens:
        return 0.0
    
    if not references:
        return 0.0
    
    # 참조 텍스트들의 n-gram 수집
    ref_ngrams = []
    for ref in references:
        ref_tokens = tokenize(ref)
        for i in range(1, n + 1):
            ref_ngrams.extend([tuple(ref_tokens[j:j+i]) for j in range(len(ref_tokens) - i + 1)])
    
    if not ref_ngrams:
        return 0.0
    
    ref_ngram_counts = Counter(ref_ngrams)
    
    # 후보의 n-gram과 매칭
    precision_scores = []
    for i in range(1, n + 1):
        candidate_ngrams = [tuple(candidate_tokens[j:j+i]) for j in range(len(candidate_tokens) - i + 1)]
        if not candidate_ngrams:
            continue
            
        candidate_counts = Counter(candidate_ngrams)
        
        # 각 n-gram에 대해 최대 매칭 수 계산
        matches = 0
        for ngram, count in candidate_counts.items():
            ref_count = ref_ngram_counts.get(ngram, 0)
            matches += min(count, ref_count)
        
        precision = matches / len(candidate_ngrams) if candidate_ngrams else 0.0
        precision_scores.append(precision)
    
    if not precision_scores or all(p == 0 for p in precision_scores):
        return 0.0
    
    # 기하평균 precision (0이 아닌 값만 사용)
    non_zero_precisions = [p for p in precision_scores if p > 0]
    if not non_zero_precisions:
        return 0.0
    
    geometric_mean = math.exp(sum(math.log(p) for p in non_zero_precisions) / len(non_zero_precisions))
    
    # Brevity penalty
    candidate_length = len(candidate_tokens)
    ref_lengths = [len(tokenize(ref)) for ref in references]
    
    # 가장 가까운 참조 길이 찾기
    if not ref_lengths:
        brevity_penalty = 1.0
    else:
        closest_ref_length = min(ref_lengths, key=lambda x: abs(x - candidate_length))
        if candidate_length == 0: # 후보 길이가 0이면 패널티 0
            brevity_penalty = 0.0
        elif candidate_length < closest_ref_length:
            brevity_penalty = math.exp(1 - closest_ref_length / candidate_length)
        else:
            brevity_penalty = 1.0
    
    return geometric_mean * brevity_penalty


def composite(scores: Dict[str, float], weights: Optional[Dict[str, float]] = None) -> float:
    """
    가중합으로 복합 점수 계산
    
    Args:
        scores: 각 메트릭 점수를 담은 딕셔너리
        weights: 각 메트릭에 대한 가중치를 담은 딕셔너리. None이면 균등 가중치.
    
    Returns:
        복합 점수 (0.0 ~ 1.0)
    """
    if not scores:
        return 0.0
    
    if weights is None:
        # 기본 균등 가중치
        num_metrics = len(scores)
        if num_metrics == 0:
            return 0.0
        weights = {metric: 1.0 / num_metrics for metric in scores}
    
    composite_score = 0.0
    total_weight = 0.0
    
    for metric, score in scores.items():
        weight = weights.get(metric, 0.0)
        composite_score += score * weight
        total_weight += weight
        
    return composite_score / total_weight if total_weight > 0 else 0.0


def evaluate_text(text: str, references: List[str] = None, weights: Optional[Dict[str, float]] = None, detailed: bool = False) -> Dict[str, Any]:
    """
    단일 텍스트에 대한 모든 메트릭을 평가하고 복합 점수를 계산합니다.
    """
    if references is None:
        references = []

    scores = {
        "distinct_1": distinct_n(text, n=1),
        "distinct_2": distinct_n(text, n=2),
        "repeat_penalty": repeat_penalty(text),
        "brevity_prior": brevity_prior(text),
    }
    
    if references:
        scores["bleu_like"] = bleu_like(text, references)
    
    composite_score = composite(scores, weights)
    
    result = {"composite_score": composite_score}
    if detailed:
        result["metrics"] = scores
    
    return result

def evaluate_candidates(candidates: List[str], references: List[str] = None, weights: Optional[Dict[str, float]] = None, detailed: bool = False) -> List[Dict[str, Any]]:
    """
    여러 후보 텍스트를 평가하고 복합 점수를 기준으로 순위를 매깁니다.
    """
    if references is None:
        references = []

    results = []
    for i, candidate in enumerate(candidates):
        eval_result = evaluate_text(candidate, references, weights, detailed=True) # 항상 상세 점수 포함
        results.append({
            "index": i,
            "text": candidate,
            "composite_score": eval_result["composite_score"],
            "metrics": eval_result["metrics"]
        })
    
    results.sort(key=lambda x: x["composite_score"], reverse=True)
    
    # 상세 정보가 필요 없으면 metrics 필드 제거
    if not detailed:
        for res in results:
            res.pop("metrics", None)

    return results