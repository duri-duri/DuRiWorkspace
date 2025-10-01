# DuRi Backup (Windows PowerShell, HDD+SSD)

## 파일
- setup_backup_drives.ps1 : H:\, I:\ 기본 폴더 생성 + 권한/로그
- test_sync.ps1            : 보고서 폴더 동기화 테스트(robocopy)
- duri_backup_automation.ps1:
  - Mode=test | incremental | full | status
  - reports 전체 + state 화이트리스트(backup_refs.json, restore_slo.jsonl)
- run_backup_setup.bat     : 최초 셋업 순차 실행 배치

## 일반 사용
1) `run_backup_setup.bat` 더블클릭 → 셋업/테스트 완료
2) 증분 백업:
   ```powershell
   .\duri_backup_automation.ps1 -Mode incremental
   ```
3. 전체 백업:
   ```powershell
   .\duri_backup_automation.ps1 -Mode full
   ```
4. 상태 확인:
   ```powershell
   .\duri_backup_automation.ps1 -Mode status
   ```

## 스케줄러(권장)

* **매일 22:30** 증분:
  ```
  schtasks /Create /TN "DuRi_Incremental_Daily" /TR "powershell -NoProfile -ExecutionPolicy Bypass -File C:\PATH\duri_backup_automation.ps1 -Mode incremental" /SC DAILY /ST 22:30
  ```
* **매주 일요일 23:00** 전체:
  ```
  schtasks /Create /TN "DuRi_Full_Weekly" /TR "powershell -NoProfile -ExecutionPolicy Bypass -File C:\PATH\duri_backup_automation.ps1 -Mode full" /SC WEEKLY /D SUN /ST 23:00
  ```

## 주의

* 삭제 동기화(/MIR)는 사용하지 않음 → 안전 우선.
* 원본: `\\wsl$\Ubuntu-22.04\home\duri\DuRiWorkspace\var\reports, var\state`.
* 로그: `H:\DuRiBackup\_logs`, `I:\DuRiBackup\_logs`.
