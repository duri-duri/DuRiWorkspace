@echo off
setlocal
REM 실행 정책 우회하여 스크립트 순차 실행
powershell -NoProfile -ExecutionPolicy Bypass -File ".\setup_backup_drives.ps1"
powershell -NoProfile -ExecutionPolicy Bypass -File ".\test_sync.ps1"
powershell -NoProfile -ExecutionPolicy Bypass -File ".\duri_backup_automation.ps1" -Mode test
echo.
echo Done. Check logs under H:\DuRiBackup\_logs and I:\DuRiBackup\_logs
pause



