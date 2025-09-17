#!/usr/bin/env bash
set -euo pipefail

echo "🚀 DuRiWorkspace 부트스트랩 시작..."

# Git 훅 경로 설정
echo "📁 Git 훅 경로 설정 중..."
git config core.hooksPath .githooks

# 훅 파일 권한 확인
if [ -d ".githooks" ]; then
    echo "🔧 훅 파일 권한 설정 중..."
    chmod +x .githooks/*
    echo "✅ 훅 파일 권한 설정 완료"
else
    echo "⚠️  .githooks 디렉토리를 찾을 수 없습니다."
    exit 1
fi

# Git 설정 확인
echo "📋 현재 Git 설정:"
echo "  - core.hooksPath: $(git config core.hooksPath)"
echo "  - 훅 파일 개수: $(ls -1 .githooks/ | wc -l)"

echo "🎉 부트스트랩 완료! 이제 main/release/* 브랜치에서 커밋이 차단됩니다."
echo "💡 개발 시에는 'git pr-start'로 작업 브랜치를 만드세요."
