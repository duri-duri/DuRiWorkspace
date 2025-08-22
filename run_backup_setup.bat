@echo off
chcp 65001 >nul
echo 🚀 DuRi 백업 드라이브 설정 자동화
echo ======================================
echo.

echo 📁 1단계: 백업 드라이브 구조 생성...
powershell -ExecutionPolicy Bypass -File "setup_backup_drives.ps1"
if %errorlevel% neq 0 (
    echo ❌ 백업 드라이브 설정 실패
    pause
    exit /b 1
)

echo.
echo 🔄 2단계: 동기화 테스트...
powershell -ExecutionPolicy Bypass -File "test_sync.ps1"
if %errorlevel% neq 0 (
    echo ❌ 동기화 테스트 실패
    pause
    exit /b 1
)

echo.
echo 🧪 3단계: 백업 시스템 테스트...
powershell -ExecutionPolicy Bypass -File "duri_backup_automation.ps1" -Mode test
if %errorlevel% neq 0 (
    echo ❌ 백업 시스템 테스트 실패
    pause
    exit /b 1
)

echo.
echo 🎯 모든 설정이 완료되었습니다!
echo.
echo 📋 사용 가능한 명령어:
echo   전체 백업: powershell -File "duri_backup_automation.ps1" -Mode full
echo   증분 백업: powershell -File "duri_backup_automation.ps1" -Mode incremental
echo   상태 확인: powershell -File "duri_backup_automation.ps1" -Mode status
echo.
pause


