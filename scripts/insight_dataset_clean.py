#!/usr/bin/env python3
"""
Insight Dataset Cleaning Script
Raw txt/csv → 정제(중복/길이/금칙어)
"""

import argparse
import pathlib
import csv
import json
from typing import List, Set
import re

def load_candidates(input_path: str) -> List[str]:
    """입력 파일에서 후보 로드"""
    path = pathlib.Path(input_path)
    candidates = []
    
    if path.suffix.lower() == '.csv':
        with open(path, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            for row in reader:
                if row and row[0].strip():
                    candidates.append(row[0].strip())
    else:
        # txt 파일로 가정
        with open(path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line:
                    candidates.append(line)
    
    return candidates

def tokenize_simple(text: str) -> List[str]:
    """간단한 토큰화"""
    return re.findall(r'\w+', text.lower())

def calculate_similarity(tokens1: Set[str], tokens2: Set[str]) -> float:
    """Jaccard 유사도 계산"""
    if not tokens1 or not tokens2:
        return 0.0
    intersection = len(tokens1 & tokens2)
    union = len(tokens1 | tokens2)
    return intersection / union if union > 0 else 0.0

def clean_dataset(candidates: List[str], 
                 min_length: int = 10,
                 max_length: int = 500,
                 forbidden_words: List[str] = None,
                 duplicate_threshold: float = 0.8) -> List[str]:
    """데이터셋 정제"""
    if forbidden_words is None:
        forbidden_words = ["spam", "test", "dummy", "placeholder"]
    
    cleaned = []
    seen_tokens = []
    
    print(f"원본 후보 수: {len(candidates)}")
    
    for i, candidate in enumerate(candidates):
        if not candidate or not candidate.strip():
            continue
            
        tokens = set(tokenize_simple(candidate))
        
        # 길이 체크
        if len(tokens) < min_length:
            print(f"길이 부족 제외 [{i}]: {candidate[:50]}...")
            continue
        if len(tokens) > max_length:
            print(f"길이 초과 제외 [{i}]: {candidate[:50]}...")
            continue
            
        # 금칙어 체크
        if any(word in candidate.lower() for word in forbidden_words):
            print(f"금칙어 제외 [{i}]: {candidate[:50]}...")
            continue
            
        # 중복 체크
        is_duplicate = False
        for seen_token_set in seen_tokens:
            similarity = calculate_similarity(tokens, seen_token_set)
            if similarity > duplicate_threshold:
                print(f"중복 제외 [{i}]: {candidate[:50]}... (유사도: {similarity:.2f})")
                is_duplicate = True
                break
        
        if not is_duplicate:
            cleaned.append(candidate)
            seen_tokens.append(tokens)
    
    print(f"정제 후 후보 수: {len(cleaned)}")
    print(f"제외된 후보 수: {len(candidates) - len(cleaned)}")
    
    return cleaned

def save_cleaned(candidates: List[str], output_path: str, format: str = "txt"):
    """정제된 데이터 저장"""
    path = pathlib.Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    
    if format == "csv":
        with open(path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['candidate'])
            for candidate in candidates:
                writer.writerow([candidate])
    elif format == "json":
        with open(path, 'w', encoding='utf-8') as f:
            json.dump({"candidates": candidates}, f, ensure_ascii=False, indent=2)
    else:
        # txt 파일
        with open(path, 'w', encoding='utf-8') as f:
            for candidate in candidates:
                f.write(f"{candidate}\n")

def main():
    parser = argparse.ArgumentParser(description="Insight Dataset Cleaning")
    parser.add_argument("input", help="입력 파일 경로")
    parser.add_argument("-o", "--output", help="출력 파일 경로")
    parser.add_argument("--format", choices=["txt", "csv", "json"], default="txt", help="출력 형식")
    parser.add_argument("--min-length", type=int, default=10, help="최소 토큰 수")
    parser.add_argument("--max-length", type=int, default=500, help="최대 토큰 수")
    parser.add_argument("--duplicate-threshold", type=float, default=0.8, help="중복 임계값")
    parser.add_argument("--forbidden-words", nargs="+", default=["spam", "test", "dummy"], help="금칙어")
    
    args = parser.parse_args()
    
    # 입력 로드
    candidates = load_candidates(args.input)
    
    # 정제
    cleaned = clean_dataset(
        candidates,
        min_length=args.min_length,
        max_length=args.max_length,
        forbidden_words=args.forbidden_words,
        duplicate_threshold=args.duplicate_threshold
    )
    
    # 출력 저장
    if args.output:
        save_cleaned(cleaned, args.output, args.format)
        print(f"정제된 데이터 저장: {args.output}")
    else:
        # 기본 출력
        for candidate in cleaned:
            print(candidate)

if __name__ == "__main__":
    main()
