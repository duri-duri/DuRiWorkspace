# 백업 축 분류 및 관리 시스템

## 📋 백업 축 분류 체계

### 1. 학습 시스템 기능적 백업 (Learning System Functional Backups)
- **목적**: DuRiCore, duri_brain, duri_modules 등 학습 시스템의 기능적 백업
- **위치**: `backup_repository/backup_axes_management/learning_system/`
- **특징**: 
  - Python 코드, 학습 모델, 설정 파일
  - 기능적 완전성 보장
  - 개발/연구용 백업

### 2. 도커 시스템 운영적 백업 (Docker System Operational Backups)
- **목적**: Docker 컨테이너, docker-compose.yml 등 운영 시스템 백업
- **위치**: `backup_repository/backup_axes_management/docker_system/`
- **특징**:
  - 컨테이너 설정, 네트워크, 볼륨
  - 운영 환경 복구용
  - 서비스 연속성 보장

### 3. 백업 시스템 자체 백업 (Backup System Self-Backups)
- **목적**: 백업 시스템 자체의 설정, 스크립트, 로그 백업
- **위치**: `backup_repository/backup_axes_management/backup_system/`
- **특징**:
  - Crontab 스케줄, 백업 스크립트
  - 백업 정책, 검증 로그
  - 백업 시스템 복구용

### 4. 마운트 상태 백업 (Mount Status Backups)
- **목적**: 드라이브 마운트 상태, 접근성 정보 백업
- **위치**: `backup_repository/backup_axes_management/mount_status/`
- **특징**:
  - 마운트 포인트 정보
  - 드라이브 접근성 테스트 결과
  - 재발 방지 가이드

### 5. 백업 완전성 테스트 축 (Backup Completeness Testing Axis)
- **목적**: 풀백업의 완전성과 롤백의 완전성을 검증하는 테스트 시스템
- **위치**: `backup_repository/backup_axes_management/backup_completeness_testing/`
- **특징**:
  - USB 롤백 검증 시스템
  - 백업 무결성 테스트
  - 스냅샷 복원 테스트
  - 코딩 품질 검증
  - 스크립트 누락 검사
  - 중요 정보 보존 검증

### 6. 90일 계획 프로젝트 축 (90-Day Project Management Axis)
- **목적**: DuRi 인간형 AI 빌드업 90일 계획의 체계적 관리 및 추적
- **위치**: `backup_repository/backup_axes_management/90day_project_management/`
- **특징**:
  - Day별 Task 관리 및 추적
  - Phase별 진행 상황 모니터링
  - KPI 지표 관리 (품질·성능·운영)
  - PoU 파일럿 결과 관리
  - 특허 및 모델 카드 관리
  - 최종 배포 준비 관리

### 7. 상호 참조 시스템 축 (Cross-Reference System Axis)
- **목적**: 코딩 내용이 여러 축에 해당될 때 원본 스크립트와 연관된 축에서 상호 참조 가능한 시스템 관리
- **위치**: `backup_repository/backup_axes_management/cross_reference_system/`
- **특징**:
  - 하드링크 기반 중복 제거 시스템
  - 대표 파일(Canonical) 관리
  - 시스템 간 연결 및 상호작용 관리
  - 메모리 연관성 분석 시스템
  - 통합 관리자 시스템
  - 공통 리소스 통합 관리

### 8. 크론 스케줄링 시스템 축 (Cron Scheduling System Axis)
- **목적**: 자동화된 백업 및 시스템 작업의 스케줄링 및 실행 관리
- **위치**: `backup_repository/backup_axes_management/cron_scheduling_system/`
- **특징**:
  - 정기 백업 스케줄 관리 (일일/주간/월간)
  - 의존성 기반 작업 순서 관리
  - 스케줄 충돌 방지 및 최적화
  - 작업 실행 상태 모니터링
  - 실패 시 자동 재시도 및 알림
  - 운영시간 기반 스케줄 조정

## 🔄 백업 축별 관리 정책

### 학습 시스템 축
- **백업 주기**: 개발 완료 시점
- **보관 기간**: 6개월
- **검증 방법**: 기능 테스트 통과

### 도커 시스템 축
- **백업 주기**: 서비스 안정화 시점
- **보관 기간**: 3개월
- **검증 방법**: 컨테이너 정상 기동

### 백업 시스템 축
- **백업 주기**: 백업 정책 변경 시
- **보관 기간**: 1년
- **검증 방법**: 백업 스크립트 실행 테스트

### 마운트 상태 축
- **백업 주기**: 마운트 문제 발생/해결 시
- **보관 기간**: 6개월
- **검증 방법**: 드라이브 접근성 테스트

### 백업 완전성 테스트 축
- **백업 주기**: 백업 시스템 변경 시
- **보관 기간**: 2년
- **검증 방법**: 롤백 완전성 테스트 통과

### 90일 계획 프로젝트 축
- **백업 주기**: Day별 완료 시점
- **보관 기간**: 5년 (프로젝트 완료 후)
- **검증 방법**: Day별 체크포인트 달성 확인

### 상호 참조 시스템 축
- **백업 주기**: 참조 관계 변경 시
- **보관 기간**: 3년 (연관성 유지)
- **검증 방법**: 하드링크 무결성 및 연결 강도 확인

### 크론 스케줄링 시스템 축
- **백업 주기**: 스케줄 변경 시
- **보관 기간**: 2년 (스케줄 이력 유지)
- **검증 방법**: 스케줄 실행 성공률 및 충돌 검사

## 📁 백업 축별 디렉터리 구조

```
backup_repository/backup_axes_management/
├── learning_system/           # 학습 시스템 기능적 백업
│   ├── functional_backups/    # 기능적 백업들
│   ├── model_backups/        # 모델 백업들
│   └── config_backups/       # 설정 백업들
├── docker_system/            # 도커 시스템 운영적 백업
│   ├── container_backups/    # 컨테이너 백업들
│   ├── compose_backups/     # Compose 파일 백업들
│   └── volume_backups/      # 볼륨 백업들
├── backup_system/           # 백업 시스템 자체 백업
│   ├── script_backups/      # 스크립트 백업들
│   ├── config_backups/      # 설정 백업들
│   └── log_backups/         # 로그 백업들
├── mount_status/            # 마운트 상태 백업
│   ├── mount_info/          # 마운트 정보
│   ├── access_tests/        # 접근성 테스트
│   └── error_analysis/       # 오류 분석
└── backup_completeness_testing/  # 백업 완전성 테스트 축
    ├── rollback_tests/       # 롤백 테스트
    ├── integrity_verification/  # 무결성 검증
    ├── snapshot_tests/      # 스냅샷 테스트
    └── completeness_reports/ # 완전성 보고서
└── 90day_project_management/  # 90일 계획 프로젝트 축
    ├── day_tasks/           # Day별 Task 관리
    ├── phase_progress/      # Phase별 진행 상황
    ├── kpi_metrics/         # KPI 지표 관리
    ├── pou_pilots/         # PoU 파일럿 결과
    ├── patents_models/     # 특허 및 모델 카드
    └── deployment_prep/    # 배포 준비 관리
└── cross_reference_system/  # 상호 참조 시스템 축
    ├── hardlink_management/ # 하드링크 관리
    ├── canonical_files/    # 대표 파일 관리
    ├── system_connections/ # 시스템 간 연결
    ├── memory_associations/ # 메모리 연관성
    ├── unified_management/ # 통합 관리
    └── resource_integration/ # 리소스 통합
└── cron_scheduling_system/  # 크론 스케줄링 시스템 축
    ├── schedule_management/ # 스케줄 관리
    ├── dependency_management/ # 의존성 관리
    ├── execution_monitoring/ # 실행 모니터링
    ├── conflict_resolution/ # 충돌 해결
    ├── retry_mechanisms/   # 재시도 메커니즘
    └── schedule_optimization/ # 스케줄 최적화
```

## 🎯 백업 축 분류 기준

### 기능적 백업 (Functional Backups)
- 시스템의 기능적 완전성 보장
- 개발/연구 목적
- 코드, 모델, 설정 중심

### 운영적 백업 (Operational Backups)
- 서비스 연속성 보장
- 운영 환경 복구 목적
- 인프라, 서비스 중심

### 시스템 백업 (System Backups)
- 시스템 자체의 복구 목적
- 설정, 스크립트, 로그 중심
- 백업 시스템 유지보수용

### 상태 백업 (Status Backups)
- 특정 시점의 상태 보존
- 문제 해결, 재발 방지 목적
- 진단 정보 중심

## 📝 백업 축별 메타데이터

각 백업 축별로 다음 메타데이터를 관리:
- **백업 ID**: 고유 식별자
- **백업 시간**: 생성 시점
- **백업 목적**: 백업 이유
- **백업 범위**: 포함된 항목들
- **검증 상태**: 검증 완료 여부
- **보관 기간**: 보관 정책
- **복구 방법**: 복구 절차




