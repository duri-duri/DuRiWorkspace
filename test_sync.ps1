# DuRi 동기화 테스트 스크립트
# 2025-08-20

Write-Host "🔄 DuRi 동기화 테스트 시작..." -ForegroundColor Green

# 현재 작업 경로 확인
$currentPath = Get-Location
Write-Host "현재 작업 경로: $currentPath" -ForegroundColor Cyan

# var/reports 폴더 존재 확인
$reportsPath = Join-Path $currentPath "var\reports"
if (-not (Test-Path $reportsPath)) {
    Write-Host "❌ var\reports 폴더를 찾을 수 없습니다: $reportsPath" -ForegroundColor Red
    Write-Host "현재 위치에서 var\reports 폴더를 생성하거나 올바른 위치로 이동하세요." -ForegroundColor Yellow
    exit 1
}

Write-Host "✅ var\reports 폴더 확인됨: $reportsPath" -ForegroundColor Green

# 1. H: 드라이브 동기화 테스트
Write-Host "`n📁 1단계: H: 드라이브 (WD HDD) 동기화 테스트..." -ForegroundColor Yellow

$hddDest = "H:\DuRiBackup\reports"
if (-not (Test-Path $hddDest)) {
    Write-Host "❌ H: 드라이브 대상 폴더가 없습니다: $hddDest" -ForegroundColor Red
    Write-Host "먼저 setup_backup_drives.ps1을 실행하세요." -ForegroundColor Yellow
    exit 1
}

Write-Host "H: 드라이브 대상: $hddDest" -ForegroundColor Gray

# robocopy 실행 (H: 드라이브)
try {
    Write-Host "robocopy 실행 중..." -ForegroundColor Gray
    $hddResult = robocopy $reportsPath $hddDest *.* /E /R:2 /W:1 /NFL /NDL /NP

    Write-Host "H: 드라이브 동기화 결과:" -ForegroundColor Cyan
    Write-Host "  복사된 파일: $($hddResult[0])" -ForegroundColor White
    Write-Host "  복사된 디렉토리: $($hddResult[1])" -ForegroundColor White
    Write-Host "  실패한 파일: $($hddResult[2])" -ForegroundColor White

    if ($hddResult[0] -gt 0 -or $hddResult[1] -gt 0) {
        Write-Host "✅ H: 드라이브 동기화 성공!" -ForegroundColor Green
    } else {
        Write-Host "⚠️ H: 드라이브 동기화 완료 (변경사항 없음)" -ForegroundColor Yellow
    }
} catch {
    Write-Host "❌ H: 드라이브 동기화 실패: $($_.Exception.Message)" -ForegroundColor Red
}

# 2. I: 드라이브 동기화 테스트
Write-Host "`n💾 2단계: I: 드라이브 (Samsung T7 SSD) 동기화 테스트..." -ForegroundColor Yellow

$ssdDest = "I:\DuRiBackup\reports"
if (-not (Test-Path $ssdDest)) {
    Write-Host "❌ I: 드라이브 대상 폴더가 없습니다: $ssdDest" -ForegroundColor Red
    Write-Host "먼저 setup_backup_drives.ps1을 실행하세요." -ForegroundColor Yellow
    exit 1
}

Write-Host "I: 드라이브 대상: $ssdDest" -ForegroundColor Gray

# robocopy 실행 (I: 드라이브)
try {
    Write-Host "robocopy 실행 중..." -ForegroundColor Gray
    $ssdResult = robocopy $reportsPath $ssdDest *.* /E /R:2 /W:1 /NFL /NDL /NP

    Write-Host "I: 드라이브 동기화 결과:" -ForegroundColor Cyan
    Write-Host "  복사된 파일: $($ssdResult[0])" -ForegroundColor White
    Write-Host "  복사된 디렉토리: $($ssdResult[1])" -ForegroundColor White
    Write-Host "  실패한 파일: $($ssdResult[2])" -ForegroundColor White

    if ($ssdResult[0] -gt 0 -or $ssdResult[1] -gt 0) {
        Write-Host "✅ I: 드라이브 동기화 성공!" -ForegroundColor Green
    } else {
        Write-Host "⚠️ I: 드라이브 동기화 완료 (변경사항 없음)" -ForegroundColor Yellow
    }
} catch {
    Write-Host "❌ I: 드라이브 동기화 실패: $($_.Exception.Message)" -ForegroundColor Red
}

# 3. 최종 결과 요약
Write-Host "`n📊 동기화 테스트 결과 요약:" -ForegroundColor Cyan

$hddFiles = Get-ChildItem $hddDest -Recurse -File | Measure-Object | Select-Object -ExpandProperty Count
$ssdFiles = Get-ChildItem $ssdDest -Recurse -File | Measure-Object | Select-Object -ExpandProperty Count

Write-Host "H: 드라이브 (WD HDD): $hddFiles 개 파일" -ForegroundColor White
Write-Host "I: 드라이브 (Samsung T7): $ssdFiles 개 파일" -ForegroundColor White

Write-Host "`n🎯 동기화 테스트 완료!" -ForegroundColor Green
Write-Host "이제 백업 자동화 스크립트를 생성할 수 있습니다." -ForegroundColor Yellow
