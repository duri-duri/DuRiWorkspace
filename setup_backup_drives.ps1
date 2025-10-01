# DuRi 백업 드라이브 설정 스크립트
# 2025-08-20

Write-Host "🚀 DuRi 백업 드라이브 설정 시작..." -ForegroundColor Green

# 1. 기본 디렉토리 구조 생성
Write-Host "📁 1단계: 기본 디렉토리 구조 생성 중..." -ForegroundColor Yellow

try {
    # H: (WD HDD) - 대용량 백업용
    New-Item -Path "H:\DuRiBackup\var" -ItemType Directory -Force | Out-Null
    New-Item -Path "H:\DuRiBackup\reports" -ItemType Directory -Force | Out-Null
    New-Item -Path "H:\DuRiBackup\state" -ItemType Directory -Force | Out-Null

    # I: (Samsung T7 SSD) - 고속 백업용
    New-Item -Path "I:\DuRiBackup\var" -ItemType Directory -Force | Out-Null
    New-Item -Path "I:\DuRiBackup\reports" -ItemType Directory -Force | Out-Null
    New-Item -Path "I:\DuRiBackup\state" -ItemType Directory -Force | Out-Null

    Write-Host "✅ 디렉토리 구조 생성 완료!" -ForegroundColor Green
} catch {
    Write-Host "❌ 디렉토리 생성 실패: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

# 2. 쓰기 권한 테스트
Write-Host "🔍 2단계: 쓰기 권한 테스트 중..." -ForegroundColor Yellow

try {
    # 센티넬 파일 생성
    New-Item -Path "H:\DuRiBackup\reports\_touch.ok" -ItemType File -Force | Out-Null
    New-Item -Path "I:\DuRiBackup\reports\_touch.ok" -ItemType File -Force | Out-Null

    Write-Host "✅ 쓰기 권한 테스트 성공!" -ForegroundColor Green
} catch {
    Write-Host "❌ 쓰기 권한 테스트 실패: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

# 3. 생성 결과 확인
Write-Host "📋 3단계: 생성 결과 확인 중..." -ForegroundColor Yellow

Write-Host "`n📁 H: 드라이브 구조:" -ForegroundColor Cyan
Get-ChildItem "H:\DuRiBackup" -Recurse | Format-Table Name, FullName, LastWriteTime

Write-Host "`n📁 I: 드라이브 구조:" -ForegroundColor Cyan
Get-ChildItem "I:\DuRiBackup" -Recurse | Format-Table Name, FullName, LastWriteTime

# 4. 동기화 테스트 준비
Write-Host "`n⚡ 4단계: 동기화 테스트 준비..." -ForegroundColor Yellow

$currentPath = Get-Location
Write-Host "현재 작업 경로: $currentPath" -ForegroundColor Gray

# robocopy 명령어 생성
$robocopyH = "robocopy `"$currentPath\var\reports`" `"H:\DuRiBackup\reports`" *.* /E /R:2 /W:1 /NFL /NDL /NP"
$robocopyI = "robocopy `"$currentPath\var\reports`" `"I:\DuRiBackup\reports`" *.* /E /R:2 /W:1 /NFL /NDL /NP"

Write-Host "`n📋 실행할 robocopy 명령어:" -ForegroundColor Cyan
Write-Host "H: 드라이브: $robocopyH" -ForegroundColor White
Write-Host "I: 드라이브: $robocopyI" -ForegroundColor White

Write-Host "`n🎯 백업 드라이브 설정 완료!" -ForegroundColor Green
Write-Host "이제 robocopy 명령어를 실행하여 동기화 테스트를 진행하세요." -ForegroundColor Yellow
