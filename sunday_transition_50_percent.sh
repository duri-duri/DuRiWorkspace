#!/bin/bash
set -Eeuo pipefail

# 일요일 50% 전환 스크립트
# 토요일 25% 전환 완료 후 일요일 50% 전환 실행

echo "🚀 일요일 50% 전환 시작 - $(date)"

# 환경변수 설정
export DURI_UNIFIED_REASONING_ROLLOUT=50
export DURI_UNIFIED_CONVERSATION_ROLLOUT=50
export DURI_UNIFIED_LEARNING_ROLLOUT=50
export DURI_UNIFIED_REASONING_MODE=auto
export DURI_UNIFIED_CONVERSATION_MODE=auto
export DURI_UNIFIED_LEARNING_MODE=auto

echo "✅ 환경변수 설정 완료:"
echo "  - DURI_UNIFIED_REASONING_ROLLOUT=50"
echo "  - DURI_UNIFIED_CONVERSATION_ROLLOUT=50"
echo "  - DURI_UNIFIED_LEARNING_ROLLOUT=50"

# 시스템 상태 확인
echo "📊 시스템 상태 확인 중..."
python3 -c "
import os
print(f'현재 전환 상태:')
print(f'  - Reasoning: {os.getenv(\"DURI_UNIFIED_REASONING_ROLLOUT\", \"0\")}%')
print(f'  - Conversation: {os.getenv(\"DURI_UNIFIED_CONVERSATION_ROLLOUT\", \"0\")}%')
print(f'  - Learning: {os.getenv(\"DURI_UNIFIED_LEARNING_ROLLOUT\", \"0\")}%')
"

# 통합 테스트 실행
echo "🧪 통합 테스트 실행 중..."
cd DuRiCore
python3 -c "
import sys
sys.path.append('.')
from unified.reasoning.router import process as reasoning_process
from unified.conversation.service import UnifiedConversationService
from unified.learning_evolution.service import UnifiedLearningEvolutionService

# 테스트 페이로드
test_payload = {'query': '테스트 쿼리', 'confidence': 0.8}

print('테스트 결과:')
try:
    result = reasoning_process(test_payload)
    print(f'  - Reasoning: {result.get(\"result\", \"unknown\")}')
except Exception as e:
    print(f'  - Reasoning: ERROR - {e}')

try:
    conv_service = UnifiedConversationService()
    result = conv_service.handle(test_payload)
    print(f'  - Conversation: {result.get(\"result\", \"unknown\")}')
except Exception as e:
    print(f'  - Conversation: ERROR - {e}')

try:
    learn_service = UnifiedLearningEvolutionService()
    result = learn_service.run(test_payload)
    print(f'  - Learning: {result.get(\"result\", \"unknown\")}')
except Exception as e:
    print(f'  - Learning: ERROR - {e}')
"

echo "✅ 일요일 50% 전환 완료!"
echo "📊 다음 단계: 1-2시간 관찰 후 100% 전환 예정"
