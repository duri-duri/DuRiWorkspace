<# DuRi 백업 자동화: full | incremental | test | status #>
[CmdletBinding()]
param(
  [ValidateSet("full","incremental","test","status")]
  [string]$Mode = "test",

  [string]$RepoRoot = "\\wsl$\Ubuntu-22.04\home\duri\DuRiWorkspace",
  [string]$HRoot = "H:\DuRiBackup",
  [string]$IRoot = "I:\DuRiBackup",
  [int]$Threads = 8
)

$ErrorActionPreference = "Stop"
$ts = (Get-Date -Format "yyyyMMdd_HHmmss")
$Hlog = Join-Path $HRoot ("_logs\backup_"+$Mode+"_"+$ts+".log")
$Ilog = Join-Path $IRoot ("_logs\backup_"+$Mode+"_"+$ts+".log")

# 소스 경로
$SrcReports = Join-Path $RepoRoot "var\reports"
$SrcState   = Join-Path $RepoRoot "var\state"

# 대상 경로
$HReports = Join-Path $HRoot "reports"
$IReports = Join-Path $IRoot "reports"
$HState   = Join-Path $HRoot "state"
$IState   = Join-Path $IRoot "state"

function Copy-Reports([switch]$DryRun){
  $flag = @("/E","/R:2","/W:1","/MT:$Threads","/NP")
  if($DryRun){ $flag += "/L" }
  robocopy $SrcReports $HReports *.* $flag /LOG+:$Hlog
  robocopy $SrcReports $IReports *.* $flag /LOG+:$Ilog
}

function Copy-StateWhitelist([switch]$DryRun){
  $files = @("backup_refs.json","restore_slo.jsonl")
  foreach($f in $files){
    $src = Join-Path $SrcState $f
    foreach($dst in @($HState,$IState)){
      if($DryRun){
        "DRY: $src -> $dst" | Tee-Object -FilePath $Hlog -Append | Out-Null
        "DRY: $src -> $dst" | Tee-Object -FilePath $Ilog -Append | Out-Null
      } else {
        if(Test-Path $src){ Copy-Item $src -Destination $dst -Force }
      }
    }
  }
}

switch ($Mode) {
  "status" {
    Write-Host "📊 Drive status" -ForegroundColor Cyan
    Get-PSDrive H,I | Select-Object Name,Free,Used, @{n='Total(GB)';e={[math]::Round(($_.Used+$_.Free)/1GB,2)}}
    Write-Host "`n🔎 Latest logs (H: and I:)" -ForegroundColor Cyan
    Get-ChildItem "$HRoot\_logs" -Filter *.log | Sort-Object LastWriteTime -Descending | Select -First 3 | ft -Auto
    Get-ChildItem "$IRoot\_logs" -Filter *.log | Sort-Object LastWriteTime -Descending | Select -First 3 | ft -Auto
    break
  }
  "test" {
    Write-Host "🧪 TEST: DRY-RUN for reports + list state files" -ForegroundColor Yellow
    Copy-Reports -DryRun
    Copy-StateWhitelist -DryRun
    Write-Host "Logs: `n - $Hlog`n - $Ilog"
    break
  }
  "incremental" {
    Write-Host "🔁 INCREMENTAL copy (reports + state whitelist)" -ForegroundColor Green
    Copy-Reports           # 변경분만 복사
    Copy-StateWhitelist
    Write-Host "Logs: `n - $Hlog`n - $Ilog"
    break
  }
  "full" {
    Write-Host "📦 FULL copy (reports + state whitelist)" -ForegroundColor Green
    # reports는 /E로 충분. (윈도우 측에서 삭제 동기화는 하지 않음: 안전 우선)
    Copy-Reports
    Copy-StateWhitelist
    Write-Host "Logs: `n - $Hlog`n - $Ilog"
    break
  }
}
