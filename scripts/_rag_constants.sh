#!/usr/bin/env bash
set -Eeuo pipefail
# RAG 시스템 공통 상수 정의
# 사용법: source "$(dirname "$0")/_rag_constants.sh"

# 카테고리별 권장 최소 길이(한글 기준)
declare -A MIN_LEN
MIN_LEN[intake]=200
MIN_LEN[education]=220
MIN_LEN[exercise]=180
MIN_LEN[orders]=120
MIN_LEN[schedule]=140
MIN_LEN[policy]=120
MIN_LEN[diagnosis]=200
MIN_LEN_DEFAULT=200

# 카테고리별 패딩 텍스트
declare -A PAD_TEXT
PAD_TEXT[triage]=" 본 항목은 즉시 상향평가와 의사 직접평가를 권고하는 신호들을 요약합니다. 임상적 판단과 환자 가치에 따라 라우팅 경로와 검사 필요성을 재평가합니다."
PAD_TEXT[orders]=" 본 기준은 레드플래그 존재 시 문서화(증상 발생 시점, 신경학 소견, 염증표지자 등)와 적절한 검사 의뢰 절차를 명시합니다."
PAD_TEXT[education]=" 환자 교육은 이득/한계/대안을 균형 있게 설명하고, 과잉검사의 위험과 비용을 투명하게 공유하는 공동의사결정(SDM)을 포함합니다."
PAD_TEXT[intake]=" 기능제한과 이전 삽화/재발 패턴, 치료 반응, 선호·가치(검사/치료/비용)를 구조화하여 기록합니다."
PAD_TEXT[diagnosis]=" 작업진단과 감별진단을 근거와 함께 제시하고, 추적 계획과 재평가 기준을 명확히 합니다."
PAD_TEXT[schedule]=" 추적 주기와 목표지표(NRS/기능)를 제시하고, 악화 시 후퇴 규칙을 포함합니다."
PAD_TEXT[exercise]=" 통증 없는 범위, 누적 볼륨, 48시간 지연 통증 모니터링, 단계적 진행 규칙을 포함합니다."
PAD_TEXT[policy]=" 안전 경고, 면책 및 상향평가 트리거를 요약합니다."

# 허용된 카테고리 목록
ALLOWED_CATEGORIES='["intake","diagnosis","education","exercise","orders","schedule","policy"]'

# ID 패턴 (영역.주제.v{major}[.minor].NNN) - 실제 사용 패턴에 맞춤
ID_PATTERN='^[a-z]+\.[a-z_.]+\.v[0-9]+(\.[0-9]+)?\.[0-9]{3}$'

# ISO8601 타임스탬프 패턴
TIMESTAMP_PATTERN='^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}(\\+[0-9]{2}:[0-9]{2}|Z)$'
