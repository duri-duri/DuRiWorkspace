# SSD 새 역할 설정 스크립트
# DURISSD (I:) 드라이브를 빠른 복구 캐시 + 작업용 버퍼로 설정

Write-Host "🚀 SSD 새 역할 설정 시작..." -ForegroundColor Green

# 기본 폴더 구조 생성
Write-Host "📁 폴더 구조 생성 중..." -ForegroundColor Yellow

try {
    # FAST_RESTORE 캐시 (H: 드라이브의 최신 백업 미러링)
    New-Item -Path "I:\FAST_RESTORE" -ItemType Directory -Force | Out-Null
    New-Item -Path "I:\FAST_RESTORE\FULL" -ItemType Directory -Force | Out-Null
    New-Item -Path "I:\FAST_RESTORE\INCR" -ItemType Directory -Force | Out-Null
    
    # WIP (작업/테스트 공간)
    New-Item -Path "I:\WIP" -ItemType Directory -Force | Out-Null
    New-Item -Path "I:\WIP\EXPERIMENTS" -ItemType Directory -Force | Out-Null
    New-Item -Path "I:\WIP\TEMP_EXTRACT" -ItemType Directory -Force | Out-Null
    New-Item -Path "I:\WIP\TEST_DATA" -ItemType Directory -Force | Out-Null
    
    # CACHE (자동화 스크립트 임시 저장소)
    New-Item -Path "I:\CACHE" -ItemType Directory -Force | Out-Null
    New-Item -Path "I:\CACHE\SCRIPTS" -ItemType Directory -Force | Out-Null
    New-Item -Path "I:\CACHE\LOGS" -ItemType Directory -Force | Out-Null
    New-Item -Path "I:\CACHE\METADATA" -ItemType Directory -Force | Out-Null
    
    Write-Host "✅ 폴더 구조 생성 완료!" -ForegroundColor Green
} catch {
    Write-Host "❌ 폴더 생성 실패: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

# 쓰기 권한 테스트
Write-Host "🔍 쓰기 권한 테스트 중..." -ForegroundColor Yellow

try {
    # 센티넬 파일 생성
    New-Item -Path "I:\FAST_RESTORE\_touch.ok" -ItemType File -Force | Out-Null
    New-Item -Path "I:\WIP\_touch.ok" -ItemType File -Force | Out-Null
    New-Item -Path "I:\CACHE\_touch.ok" -ItemType File -Force | Out-Null
    
    Write-Host "✅ 쓰기 권한 테스트 성공!" -ForegroundColor Green
} catch {
    Write-Host "❌ 쓰기 권한 테스트 실패: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

# 생성 결과 확인
Write-Host "📋 생성 결과 확인 중..." -ForegroundColor Yellow

Write-Host "`n📁 I: 드라이브 구조:" -ForegroundColor Cyan
Get-ChildItem "I:\" -Recurse | Format-Table Name, FullName, LastWriteTime

Write-Host "`n🎯 SSD 새 역할:" -ForegroundColor Green
Write-Host "  • FAST_RESTORE: H: 드라이브 최신 백업 캐시" -ForegroundColor White
Write-Host "  • WIP: 실험 코드, 압축 해제, 임시 데이터 처리" -ForegroundColor White
Write-Host "  • CACHE: 자동화 스크립트 임시 저장소" -ForegroundColor White

Write-Host "`n✅ SSD 설정 완료!" -ForegroundColor Green