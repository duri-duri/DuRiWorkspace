# DuRi 백업 자동화 메인 스크립트
# 2025-08-20

param(
    [Parameter(Mandatory=$false)]
    [ValidateSet("full", "incremental", "test", "status")]
    [string]$Mode = "test",
    
    [Parameter(Mandatory=$false)]
    [string]$SourcePath = "",
    
    [Parameter(Mandatory=$false)]
    [switch]$Force
)

# 스크립트 설정
$scriptVersion = "1.0.0"
$logFile = "duri_backup_$(Get-Date -Format 'yyyyMMdd_HHmmss').log"

# 로깅 함수
function Write-Log {
    param([string]$Message, [string]$Level = "INFO")
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $logMessage = "[$timestamp] [$Level] $Message"
    
    switch ($Level) {
        "ERROR" { Write-Host $logMessage -ForegroundColor Red }
        "WARN"  { Write-Host $logMessage -ForegroundColor Yellow }
        "SUCCESS" { Write-Host $logMessage -ForegroundColor Green }
        default { Write-Host $logMessage -ForegroundColor White }
    }
    
    Add-Content -Path $logFile -Value $logMessage
}

# 초기화
Write-Log "🚀 DuRi 백업 자동화 시작 (v$scriptVersion)" "SUCCESS"
Write-Log "모드: $Mode" "INFO"

# 백업 경로 설정
$hddBackupRoot = "H:\DuRiBackup"
$ssdBackupRoot = "I:\DuRiBackup"
$currentPath = Get-Location

if ([string]::IsNullOrEmpty($SourcePath)) {
    $SourcePath = $currentPath
}

Write-Log "소스 경로: $SourcePath" "INFO"
Write-Log "HDD 백업 경로: $hddBackupRoot" "INFO"
Write-Log "SSD 백업 경로: $ssdBackupRoot" "INFO"

# 백업 경로 존재 확인
if (-not (Test-Path $hddBackupRoot)) {
    Write-Log "❌ HDD 백업 경로가 없습니다: $hddBackupRoot" "ERROR"
    Write-Log "먼저 setup_backup_drives.ps1을 실행하세요." "WARN"
    exit 1
}

if (-not (Test-Path $ssdBackupRoot)) {
    Write-Log "❌ SSD 백업 경로가 없습니다: $ssdBackupRoot" "ERROR"
    Write-Log "먼저 setup_backup_drives.ps1을 실행하세요." "WARN"
    exit 1
}

# 백업 함수들
function Start-FullBackup {
    Write-Log "📁 전체 백업 시작..." "INFO"
    
    $timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
    $hddFullPath = Join-Path $hddBackupRoot "full_$timestamp"
    $ssdFullPath = Join-Path $ssdBackupRoot "full_$timestamp"
    
    # HDD 전체 백업 (대용량, 장기 보관)
    try {
        New-Item -Path $hddFullPath -ItemType Directory -Force | Out-Null
        Write-Log "HDD 전체 백업 시작: $hddFullPath" "INFO"
        
        $hddResult = robocopy $SourcePath $hddFullPath *.* /E /R:3 /W:2 /NFL /NDL /NP /TEE
        
        Write-Log "HDD 백업 완료 - 파일: $($hddResult[0]), 디렉토리: $($hddResult[1])" "SUCCESS"
    } catch {
        Write-Log "HDD 백업 실패: $($_.Exception.Message)" "ERROR"
    }
    
    # SSD 전체 백업 (고속, 빠른 복구용)
    try {
        New-Item -Path $ssdFullPath -ItemType Directory -Force | Out-Null
        Write-Log "SSD 전체 백업 시작: $ssdFullPath" "INFO"
        
        $ssdResult = robocopy $SourcePath $ssdFullPath *.* /E /R:3 /W:2 /NFL /NDL /NP /TEE
        
        Write-Log "SSD 백업 완료 - 파일: $($ssdResult[0]), 디렉토리: $($ssdResult[1])" "SUCCESS"
    } catch {
        Write-Log "SSD 백업 실패: $($_.Exception.Message)" "ERROR"
    }
}

function Start-IncrementalBackup {
    Write-Log "🔄 증분 백업 시작..." "INFO"
    
    $timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
    $hddIncrPath = Join-Path $hddBackupRoot "incremental_$timestamp"
    $ssdIncrPath = Join-Path $ssdBackupRoot "incremental_$timestamp"
    
    # 증분 백업 실행
    try {
        New-Item -Path $hddIncrPath -ItemType Directory -Force | Out-Null
        New-Item -Path $ssdIncrPath -ItemType Directory -Force | Out-Null
        
        # 변경된 파일만 백업
        $hddResult = robocopy $SourcePath $hddIncrPath *.* /E /XO /R:2 /W:1 /NFL /NDL /NP
        $ssdResult = robocopy $SourcePath $ssdIncrPath *.* /E /XO /R:2 /W:1 /NFL /NDL /NP
        
        Write-Log "증분 백업 완료 - HDD: $($hddResult[0]) 파일, SSD: $($ssdResult[0]) 파일" "SUCCESS"
    } catch {
        Write-Log "증분 백업 실패: $($_.Exception.Message)" "ERROR"
    }
}

function Test-BackupSystem {
    Write-Log "🧪 백업 시스템 테스트 시작..." "INFO"
    
    # 기본 동기화 테스트
    try {
        $testPath = Join-Path $SourcePath "var\reports"
        if (Test-Path $testPath) {
            Write-Log "var\reports 폴더 테스트 동기화..." "INFO"
            
            $hddTest = robocopy $testPath "$hddBackupRoot\reports" *.* /E /R:1 /W:1 /NFL /NDL /NP
            $ssdTest = robocopy $testPath "$ssdBackupRoot\reports" *.* /E /R:1 /W:1 /NFL /NDL /NP
            
            Write-Log "테스트 동기화 완료" "SUCCESS"
        } else {
            Write-Log "var\reports 폴더가 없어 테스트를 건너뜁니다." "WARN"
        }
    } catch {
        Write-Log "테스트 실패: $($_.Exception.Message)" "ERROR"
    }
}

function Get-BackupStatus {
    Write-Log "📊 백업 상태 확인..." "INFO"
    
    # HDD 상태
    $hddFullBackups = Get-ChildItem $hddBackupRoot -Directory | Where-Object { $_.Name -like "full_*" } | Sort-Object LastWriteTime -Descending
    $hddIncrBackups = Get-ChildItem $hddBackupRoot -Directory | Where-Object { $_.Name -like "incremental_*" } | Sort-Object LastWriteTime -Descending
    
    Write-Log "HDD 백업 상태:" "INFO"
    Write-Log "  전체 백업: $($hddFullBackups.Count)개" "INFO"
    if ($hddFullBackups.Count -gt 0) {
        Write-Log "  최신 전체 백업: $($hddFullBackups[0].Name) ($($hddFullBackups[0].LastWriteTime))" "INFO"
    }
    Write-Log "  증분 백업: $($hddIncrBackups.Count)개" "INFO"
    
    # SSD 상태
    $ssdFullBackups = Get-ChildItem $ssdBackupRoot -Directory | Where-Object { $_.Name -like "full_*" } | Sort-Object LastWriteTime -Descending
    $ssdIncrBackups = Get-ChildItem $ssdBackupRoot -Directory | Where-Object { $_.Name -like "incremental_*" } | Sort-Object LastWriteTime -Descending
    
    Write-Log "SSD 백업 상태:" "INFO"
    Write-Log "  전체 백업: $($ssdFullBackups.Count)개" "INFO"
    if ($ssdFullBackups.Count -gt 0) {
        Write-Log "  최신 전체 백업: $($ssdFullBackups[0].Name) ($($ssdFullBackups[0].LastWriteTime))" "INFO"
    }
    Write-Log "  증분 백업: $($ssdIncrBackups.Count)개" "INFO"
}

# 메인 실행 로직
try {
    switch ($Mode) {
        "full" {
            Start-FullBackup
        }
        "incremental" {
            Start-IncrementalBackup
        }
        "test" {
            Test-BackupSystem
        }
        "status" {
            Get-BackupStatus
        }
        default {
            Write-Log "알 수 없는 모드: $Mode" "ERROR"
            Write-Log "사용 가능한 모드: full, incremental, test, status" "INFO"
            exit 1
        }
    }
} catch {
    Write-Log "백업 실행 중 오류 발생: $($_.Exception.Message)" "ERROR"
    exit 1
}

Write-Log "🎯 DuRi 백업 자동화 완료!" "SUCCESS"
Write-Log "로그 파일: $logFile" "INFO"


