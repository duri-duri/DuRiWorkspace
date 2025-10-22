<#
.SYNOPSIS
  FAST_RESTORE 파일 무결성(SHA256) 검증 + 자동 srcPath 보정 + 로그 롤링 + 실패 전용 로그

.NOTES
  - PowerShell 5.1 호환
  - 로그: JSON Lines (한 줄당 하나의 JSON)
#>

param(
  [string]$DstRoot        = "I:\DURISSD\FAST_RESTORE\FULL",
  [string]$MetaRoot       = "I:\DURISSD\CACHE\METADATA",
  [string]$LogDir         = "I:\DURISSD\LOGS",
  [string]$SrcSearchRoot  = "H:\ARCHIVE\FULL",   # srcPath 빈 경우 자동 탐색 루트
  [long]  $LogMaxBytes    = 10MB,                # 로그 롤링 임계값
  [int]   $SearchDepth    = 2                    # 폭주 방지(루트/1/2단계)
)

$ErrorActionPreference = "Stop"

try {
  # --- 경로/이름 로드 (개행 제거) ---
  $latestName = (Get-Content -Raw -Encoding ASCII (Join-Path $DstRoot "LATEST.txt")).Trim()
  if (-not $latestName) { throw "LATEST.txt 가 비었습니다: $(Join-Path $DstRoot 'LATEST.txt')" }

  $dstPath = Join-Path $DstRoot $latestName
  if (-not (Test-Path $dstPath)) { throw "대상 파일이 존재하지 않습니다: $dstPath" }

  $metaFile = Join-Path $MetaRoot "last_full_src_path.txt"
  if (Test-Path $metaFile) {
    $srcPath = (Get-Content -Raw -Encoding ASCII $metaFile).Trim()
  } else {
    $srcPath = ""
  }

  # --- srcPath 자동 보정 ---
  if (-not $srcPath -or -not (Test-Path $srcPath)) {
    $paths = @($SrcSearchRoot)
    if ($SearchDepth -ge 1) { $paths += (Join-Path $SrcSearchRoot "*") }
    if ($SearchDepth -ge 2) { $paths += (Join-Path $SrcSearchRoot "*\*") }

    $srcCandidate = Get-ChildItem -Path $paths -File -Filter $latestName -ErrorAction SilentlyContinue |
                    Select-Object -First 1 -ExpandProperty FullName

    if (-not $srcCandidate) {
      throw "소스 파일($latestName)을 $SrcSearchRoot 하위($SearchDepth 단계)에서 찾지 못했습니다."
    }

    New-Item -ItemType Directory -Path $MetaRoot -Force | Out-Null
    $srcCandidate | Set-Content -Encoding ASCII -NoNewline $metaFile
    $srcPath = $srcCandidate
  }

  # --- 해시 계산(각 1회) ---
  $hSrc = (Get-FileHash $srcPath -Algorithm SHA256).Hash
  $hDst = (Get-FileHash $dstPath -Algorithm SHA256).Hash
  $ok   = ($hSrc -eq $hDst)

  # --- 레코드 객체 ---
  $rec = [pscustomobject]@{
    Timestamp  = (Get-Date).ToString("yyyy-MM-dd HH:mm:ssK")
    File       = (Split-Path $dstPath -Leaf)
    SRC        = [string]$srcPath
    DST        = [string]$dstPath
    SRC_SHA256 = $hSrc
    DST_SHA256 = $hDst
    Match      = $ok
  }

  # --- 로그 디렉토리/파일 ---
  New-Item -ItemType Directory -Path $LogDir -Force | Out-Null
  $logFile  = Join-Path $LogDir "fast_restore_verify.log"
  $errFile  = Join-Path $LogDir "fast_restore_verify_errors.log"

  # --- 로그 롤링 ---
  if (Test-Path $logFile) {
    $size = (Get-Item $logFile).Length
    if ($size -ge $LogMaxBytes) {
      $ts = (Get-Date).ToString("yyyyMMdd_HHmmss")
      Rename-Item $logFile "$($logFile).$ts.bak"
    }
  }

  # --- JSONL Append ---
  ($rec | ConvertTo-Json -Compress) | Add-Content -Encoding UTF8 $logFile

  # --- 상태 출력 (색상 PS 5.1 호환) ---
  Write-Host ("[FAST_RESTORE_LOG] {0} {1} → {2} | OK={3}" -f $rec.Timestamp,$rec.File,$DstRoot,$rec.Match) `
    -ForegroundColor $(if ($ok) { 'Green' } else { 'Red' })

  # --- 실패 전용 로그 + 종료코드 ---
  if (-not $ok) {
    ($rec | ConvertTo-Json -Compress) | Add-Content -Encoding UTF8 $errFile
    exit 1
  }

  exit 0
}
catch {
  # 치명적 예외도 에러 로그로 남기고 비정상 종료
  try {
    New-Item -ItemType Directory -Path $LogDir -Force | Out-Null
    $errFile = Join-Path $LogDir "fast_restore_verify_errors.log"
    $errRec = [pscustomobject]@{
      Timestamp = (Get-Date).ToString("yyyy-MM-dd HH:mm:ssK")
      File      = $latestName
      Error     = $_.Exception.Message
      SRC       = [string]$srcPath
      DST       = [string]$dstPath
      Match     = $false
    }
    ($errRec | ConvertTo-Json -Compress) | Add-Content -Encoding UTF8 $errFile
  } catch { }

  Write-Host ("[FAST_RESTORE_LOG][ERROR] {0} {1}" -f (Get-Date).ToString("yyyy-MM-dd HH:mm:ssK"), $_.Exception.Message) `
    -ForegroundColor Red
  exit 2
}
