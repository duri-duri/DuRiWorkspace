<# 리포트 폴더 동기화(드라이런X, 실제 소량 복사) - 로깅 포함 #>
param(
  [string]$SrcReports="\\wsl$\Ubuntu-22.04\home\duri\DuRiWorkspace\var\reports",
  [string]$Hdst = "H:\DuRiBackup\reports",
  [string]$Idst = "I:\DuRiBackup\reports",
  [int]$Threads = 8
)

$ts = (Get-Date -Format "yyyyMMdd_HHmmss")
$Hlog = "H:\DuRiBackup\_logs\testsync_$ts.log"
$Ilog = "I:\DuRiBackup\_logs\testsync_$ts.log"

robocopy $SrcReports $Hdst *.* /E /R:2 /W:1 /MT:$Threads /NP /LOG:$Hlog
robocopy $SrcReports $Idst *.* /E /R:2 /W:1 /MT:$Threads /NP /LOG:$Ilog

Write-Host "✅ test sync done. Logs:" -ForegroundColor Green
Write-Host "  - $Hlog"
Write-Host "  - $Ilog"
