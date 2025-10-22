<#
.SYNOPSIS
  FAST_RESTORE 검증 스크립트를 평일/일요일 09:15에 자동 실행하는 스케줄러 등록

.NOTES
  - 관리자 권한이 아니어도 사용자 계정 스케줄러 등록은 가능
  - 기존 작업명이 있으면 덮어쓰기
  - 원장님 작업 시간 맞춤: 평일(월-금) 09:15, 일요일 09:15, 토요일 제외
#>

param(
  [string]$TaskName   = "VerifyFastRestoreDaily",
  [string]$ScriptPath = (Join-Path $env:USERPROFILE 'scripts\verify_fast_restore_enhanced.ps1'),
  [string]$DstRoot    = "I:\DURISSD\FAST_RESTORE\FULL",
  [string]$MetaRoot   = "I:\DURISSD\CACHE\METADATA",
  [string]$LogDir     = "I:\DURISSD\LOGS",
  [string]$SrcSearchRoot = "H:\ARCHIVE\FULL"
)

$ErrorActionPreference = "Stop"

if (-not (Test-Path $ScriptPath)) {
  throw "검증 스크립트를 찾을 수 없습니다: $ScriptPath"
}

# 인자 구성(필요시 경로 오버라이드 전달)
$arg = @(
  '-NoProfile', '-ExecutionPolicy', 'Bypass', '-File',
  ('"{0}"' -f $ScriptPath),
  '-DstRoot',       ('"{0}"' -f $DstRoot),
  '-MetaRoot',      ('"{0}"' -f $MetaRoot),
  '-LogDir',        ('"{0}"' -f $LogDir),
  '-SrcSearchRoot', ('"{0}"' -f $SrcSearchRoot)
) -join ' '

$action = New-ScheduledTaskAction -Execute "powershell.exe" -Argument $arg

# 평일(월-금) 09:15, 일요일 09:15 트리거 생성 (기존 cron과 충돌 방지)
$weekdayTrigger = New-ScheduledTaskTrigger -Weekly -DaysOfWeek Monday,Tuesday,Wednesday,Thursday,Friday -At 09:15
$sundayTrigger = New-ScheduledTaskTrigger -Weekly -DaysOfWeek Sunday -At 09:15

$settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable

# 이미 있으면 제거 후 재등록
if (Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue) {
  Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false
  Write-Host "기존 작업 제거 완료" -ForegroundColor Yellow
}

Register-ScheduledTask -TaskName $TaskName -Action $action -Trigger @($weekdayTrigger, $sundayTrigger) -Settings $settings `
  -Description "FAST_RESTORE 무결성 점검 (평일/일요일 09:15)" -User $env:USERNAME

Write-Host "✅ 스케줄러 등록 완료!" -ForegroundColor Green
Write-Host "  • 작업명: $TaskName" -ForegroundColor White
Write-Host "  • 실행시간: 평일(월-금) 09:15, 일요일 09:15" -ForegroundColor White
Write-Host "  • 제외일: 토요일 (컴퓨터 미사용)" -ForegroundColor White
Write-Host "  • 스크립트: $ScriptPath" -ForegroundColor White

# 작업 상태 확인
$task = Get-ScheduledTask -TaskName $TaskName
Write-Host "  • 상태: $($task.State)" -ForegroundColor White
