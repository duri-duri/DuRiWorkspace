<# 초기 드라이브 구조 생성 & 권한/쓰기 테스트 #>
param(
  [string]$H = "H:\DuRiBackup",
  [string]$I = "I:\DuRiBackup"
)

$ErrorActionPreference = "Stop"
$dirs = @("var","reports","state","_logs")

foreach($root in @($H,$I)){
  foreach($d in $dirs){ New-Item -Path (Join-Path $root $d) -ItemType Directory -Force | Out-Null }
  # 센티넬/로그 파일
  New-Item -Path (Join-Path $root "reports\_touch.ok") -ItemType File -Force | Out-Null
  $stamp = Join-Path $root ("_logs\setup_"+(Get-Date -Format "yyyyMMdd_HHmmss")+".log")
  "[$(Get-Date)] setup OK for $root" | Out-File -FilePath $stamp -Encoding UTF8
}

Write-Host "✅ Folders ready:" -ForegroundColor Green
Get-ChildItem $H,$I -Recurse | Select-Object FullName,Length | Out-Host



