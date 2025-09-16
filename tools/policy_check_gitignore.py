#!/usr/bin/env python3
"""
정책 일치성 검증 도구
storage_policy.yml과 .gitignore의 일치성을 검증
"""

import yaml
import os
import sys
from pathlib import Path

def load_yaml(file_path):
    """YAML 파일 로드"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    except Exception as e:
        print(f"[ERROR] Failed to load {file_path}: {e}")
        return None

def load_gitignore(file_path):
    """gitignore 파일 로드"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = [line.strip() for line in f if line.strip() and not line.startswith('#')]
        return lines
    except Exception as e:
        print(f"[ERROR] Failed to load {file_path}: {e}")
        return []

def extract_policy_patterns(policy_data):
    """storage_policy.yml에서 Git 추적 패턴 추출"""
    try:
        git_section = policy_data.get('profiles', {}).get('default', {}).get('git', {})
        track_patterns = git_section.get('track', [])
        ignore_patterns = git_section.get('ignore', [])
        return track_patterns, ignore_patterns
    except Exception as e:
        print(f"[ERROR] Failed to extract policy patterns: {e}")
        return [], []

def check_pattern_consistency(policy_patterns, gitignore_patterns):
    """정책과 gitignore 패턴 일치성 검증"""
    track_patterns, ignore_patterns = policy_patterns
    
    # ignore_patterns가 gitignore에 포함되어야 함
    missing_in_gitignore = []
    for pattern in ignore_patterns:
        if pattern not in gitignore_patterns:
            missing_in_gitignore.append(pattern)
    
    # gitignore에 있지만 정책에 없는 패턴
    extra_in_gitignore = []
    for pattern in gitignore_patterns:
        if pattern not in ignore_patterns:
            extra_in_gitignore.append(pattern)
    
    return missing_in_gitignore, extra_in_gitignore

def main():
    """메인 검증 로직"""
    print("🔍 정책 일치성 검증 시작...")
    
    # 파일 경로 설정
    repo_root = Path(__file__).parent.parent
    policy_file = repo_root / "configs" / "storage_policy.yml"
    gitignore_file = repo_root / ".gitignore"
    
    # 파일 존재 확인
    if not policy_file.exists():
        print(f"[ERROR] Policy file not found: {policy_file}")
        sys.exit(1)
    
    if not gitignore_file.exists():
        print(f"[ERROR] .gitignore file not found: {gitignore_file}")
        sys.exit(1)
    
    # 파일 로드
    policy_data = load_yaml(policy_file)
    if policy_data is None:
        sys.exit(1)
    
    gitignore_patterns = load_gitignore(gitignore_file)
    
    # 패턴 추출
    policy_patterns = extract_policy_patterns(policy_data)
    if not policy_patterns[0] and not policy_patterns[1]:
        sys.exit(1)
    
    # 일치성 검증
    missing, extra = check_pattern_consistency(policy_patterns, gitignore_patterns)
    
    # 결과 출력
    print(f"\n📊 검증 결과:")
    print(f"  - 정책 파일: {policy_file}")
    print(f"  - .gitignore: {gitignore_file}")
    print(f"  - 정책 추적 패턴: {len(policy_patterns[0])}개")
    print(f"  - 정책 무시 패턴: {len(policy_patterns[1])}개")
    print(f"  - .gitignore 패턴: {len(gitignore_patterns)}개")
    
    if missing:
        print(f"\n❌ .gitignore에 누락된 패턴:")
        for pattern in missing:
            print(f"    - {pattern}")
    
    if extra:
        print(f"\n⚠️  .gitignore에 추가된 패턴:")
        for pattern in extra:
            print(f"    - {pattern}")
    
    if not missing and not extra:
        print(f"\n✅ 정책 일치성 검증 통과!")
        print(f"   모든 패턴이 정확히 일치합니다.")
        return 0
    else:
        print(f"\n❌ 정책 일치성 검증 실패!")
        if missing:
            print(f"   누락된 패턴: {len(missing)}개")
        if extra:
            print(f"   추가된 패턴: {len(extra)}개")
        return 1

if __name__ == "__main__":
    sys.exit(main())



