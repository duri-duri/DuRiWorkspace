#!/usr/bin/env bash
# Day 63: 코딩 PR 모드 고도화 - 코드 도메인 RAG 리뷰 시스템
set -euo pipefail

echo "🔍 코드 도메인 RAG 리뷰 (Day 63)"
echo "================================"

# 변경된 파일들 감지
if [[ -n "${1:-}" ]]; then
    CHANGED_FILES="$1"
else
    # Git 변경 파일 감지
    CHANGED_FILES="$(git diff --name-only HEAD~1 HEAD 2>/dev/null || echo "")"
fi

if [[ -z "$CHANGED_FILES" ]]; then
    echo "⚠️ 변경된 파일 없음 - 건너뜀"
    exit 0
fi

echo "📋 변경된 파일들:"
echo "$CHANGED_FILES" | while read -r file; do
    echo "   - $file"
done

echo
echo "🔍 RAG 기반 코드 리뷰 분석..."

# 각 변경 파일에 대해 RAG 검색 수행
echo "$CHANGED_FILES" | while read -r file; do
    if [[ -z "$file" ]]; then continue; fi

    echo "📄 파일: $file"

    # 파일 확장자에 따른 검색 전략
    case "$file" in
        *.py)
            echo "   🐍 Python 파일 분석..."
            # Python 관련 검색어들
            search_terms=("python best practices" "code quality" "security vulnerabilities" "performance issues" "testing patterns")
            ;;
        *.sh)
            echo "   🐚 Shell 스크립트 분석..."
            search_terms=("shell scripting" "bash best practices" "security" "error handling")
            ;;
        *.yaml|*.yml)
            echo "   ⚙️ YAML 설정 분석..."
            search_terms=("yaml configuration" "deployment" "security" "best practices")
            ;;
        *.md)
            echo "   📝 문서 분석..."
            search_terms=("documentation" "markdown" "clarity" "completeness")
            ;;
        *)
            echo "   📄 일반 파일 분석..."
            search_terms=("code review" "best practices" "quality")
            ;;
    esac

    # 각 검색어로 RAG 검색 수행
    for term in "${search_terms[@]}"; do
        echo "   🔍 검색어: '$term'"

        # RAG 검색 실행 (머신 출력 모드)
        if [[ -f "scripts/rag_search_day62_final.sh" ]]; then
            results="$(FORMAT=ids scripts/rag_search_day62_final.sh "$term" "" "" "3" "1" 2>/dev/null | head -3)"
            if [[ -n "$results" ]]; then
                echo "     📚 관련 문서:"
                echo "$results" | while read -r doc_id; do
                    echo "       - $doc_id"
                done
            else
                echo "     ⚠️ 관련 문서 없음"
            fi
        else
            echo "     ⚠️ RAG 검색 스크립트 없음"
        fi
    done

    echo
done

echo "🎯 리뷰 권장사항:"
echo "   1. 보안 취약점 검토"
echo "   2. 성능 최적화 기회 확인"
echo "   3. 테스트 커버리지 확보"
echo "   4. 문서화 완성도 검토"
echo "   5. 코드 스타일 일관성 확인"

echo
echo "✅ 코드 도메인 RAG 리뷰 완료"


