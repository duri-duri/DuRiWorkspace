# DuRi USB 증분 동기화 시스템 사용법

## 🎯 목적
USB를 매개체로 병원용과 집용 콜드 백업을 효율적으로 동기화

## 📋 사용 시나리오

### 시나리오 1: 병원 → 집 동기화
1. **병원에서**: USB에 최신 백업 상태 내보내기
   ```bash
   ./scripts/usb_incremental_sync.sh export
   ```

2. **집에서**: USB의 증분 데이터를 집용 콜드 백업에 가져오기
   ```bash
   ./scripts/usb_incremental_sync.sh import
   ```

### 시나리오 2: 집 → 병원 동기화
1. **집에서**: 집용 콜드 백업 상태를 USB에 내보내기
   ```bash
   ./scripts/usb_incremental_sync.sh export
   ```

2. **병원에서**: USB의 증분 데이터를 병원용 콜드 백업에 가져오기
   ```bash
   ./scripts/usb_incremental_sync.sh import
   ```

## 🔄 동작 원리

### Export (내보내기)
- **메타데이터 생성**: 파일명, 크기, 해시, 타임스탬프를 JSON으로 저장
- **증분 파일 복사**: 최근 7일 이내의 새 백업 파일들만 USB로 복사
- **SHA256 파일 복사**: 무결성 검증을 위한 해시 파일들도 복사
- **상태 파일 생성**: 언제, 어디서 내보냈는지 기록

### Import (가져오기)
- **메타데이터 분석**: USB의 메타데이터와 현재 상태 비교
- **증분 복사**: 집용에 없는 파일들만 복사
- **중복 방지**: 이미 존재하는 파일은 스킵
- **무결성 검증**: SHA256 파일로 검증

## 📁 USB 구조
```
/mnt/g/DuRiSync/
├── metadata/           # 메타데이터 JSON 파일들
│   ├── hosp_metadata_20250910_143022.json
│   └── home_current_20250910_150000.json
├── increments/         # 증분 백업 파일들
│   ├── FULL__2025-09-05__1920__host-duri-head.tar.zst
│   ├── FULL__2025-09-05__1920__host-duri-head.tar.zst.sha256
│   └── ...
├── logs/              # 동기화 로그
├── last_export.txt    # 마지막 내보내기 시간
├── last_import.txt    # 마지막 가져오기 시간
├── source_location.txt # 내보낸 위치 (hosp/home)
└── target_location.txt # 가져온 위치 (hosp/home)
```

## ⚡ 효율성
- **용량 절약**: 전체 백업이 아닌 증분만 전송
- **시간 절약**: 중복 파일은 스킵
- **안전성**: SHA256 해시로 무결성 검증
- **추적성**: 모든 작업이 로그에 기록

## 🛡️ 안전장치
- 마운트 상태 확인
- 파일 무결성 검증
- 중복 파일 방지
- 상세한 로그 기록
- 원자적 파일 복사

## 📊 예상 사용량
- **메타데이터**: 수 KB (JSON 파일)
- **증분 파일**: 최근 7일치만 (보통 수 GB)
- **총 사용량**: USB 용량의 1-5% 정도

## 🔧 문제 해결
- USB가 마운트되지 않음: `sudo mount /dev/sdX /mnt/g`
- 권한 문제: `sudo chown -R duri:duri /mnt/g/DuRiSync`
- 로그 확인: `/var/log/duri2-backup/usb_sync_*.log`
