#!/bin/bash

echo "🌅 DuRi 작업 재개 스크립트 시작..."
echo "=================================="

# 1. 작업 디렉토리로 이동
cd /home/duri/DuRiWorkspace/DuRiCore
echo "✅ 작업 디렉토리 이동 완료: $(pwd)"

# 2. 현재 상태 확인
echo "📊 현재 시스템 상태 확인 중..."
ls -la *.py | head -10

# 3. 통합 시스템 상태 확인
echo "🔍 통합 시스템 상태 확인 중..."
python3 -c "
try:
    from integrated_evolution_system import DuRiIntegratedEvolutionSystem
    print('✅ 통합 시스템 로드 성공')
    
    system = DuRiIntegratedEvolutionSystem()
    print('✅ 시스템 인스턴스 생성 성공')
    
    # 기본 상태 확인
    status = system.get_integration_status()
    print(f'📊 통합 상태: {status}')
    
except Exception as e:
    print(f'❌ 오류 발생: {e}')
    print('🔧 문제 해결이 필요합니다.')
"

# 4. 다음 작업 준비
echo ""
echo "🎯 다음 작업 단계:"
echo "1. 시스템 검증 및 테스트"
echo "2. 성능 벤치마크 실행"
echo "3. 새로운 기능 테스트"
echo "4. Phase 5: 시스템 안정성 검증 시작"
echo ""
echo "🚀 작업을 시작하려면: python3 integrated_evolution_system.py"
echo "📝 테스트를 위해: python3 test_safety_controller.py"

echo ""
echo "✨ DuRi 작업 재개 준비 완료!"





