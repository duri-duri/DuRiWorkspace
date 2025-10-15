#!/bin/bash
# DuRi CI 무결성 검증 게이트 (끝판왕 수준)

set -e

echo "🔍 DuRi 무결성 검증 시작..."

# 환경변수 확인
GIT_TAG=${GIT_TAG:-"dev"}
DURI_INTEGRITY_MODE=${DURI_INTEGRITY_MODE:-"strict"}
DURI_HMAC_KEY=${DURI_HMAC_KEY:-""}

echo "📋 검증 설정:"
echo "   - GIT_TAG: $GIT_TAG"
echo "   - DURI_INTEGRITY_MODE: $DURI_INTEGRITY_MODE"
echo "   - DURI_HMAC_KEY: ${DURI_HMAC_KEY:+설정됨}"

# CI 파이프라인 분기: 검증 전용 vs 릴리스용
if [[ "$GIT_TAG" == "dev" || "$GIT_TAG" == "main" ]]; then
    echo "🔍 검증 전용 모드: 기존 manifest 검증만 수행"
    MODE="verify_only"
else
    echo "🚀 릴리스 모드: 새 manifest 생성 + 검증 + 서명"
    MODE="release"
fi

# 무결성 검증
python3 - << 'PY'
import sys
import os
from DuRiCore.deployment.deployment_integrity import deployment_integrity as d

git_tag = os.getenv('GIT_TAG', 'dev')
mode = os.getenv('MODE', 'verify_only')

if mode == "release":
    # 릴리스 모드: 새 manifest 생성
    print(f"배포 메타데이터 생성: {git_tag}")
    metadata = d.create_deployment_metadata(git_tag)
    
    if not metadata:
        print("❌ 배포 메타데이터 생성 실패")
        sys.exit(1)
    
    print(f"✅ 배포 메타데이터 생성 성공: {metadata['deployment_id']}")
    print(f"   - 스키마 버전: {metadata['schema_version']}")
    print(f"   - 해시 알고리즘: {metadata['hash_algorithm']}")
    print(f"   - 해시 버전: {metadata['hash_version']}")
    print(f"   - 검증 모드: {metadata['mode']}")
    print(f"   - ignore 해시: {metadata['ignore_hash']}")
    print(f"   - 파일 수: {metadata['file_count']}")
    
    # 아티팩트 업로드용 파일 목록
    artifact_files = [
        "DuRiCore/deployment/checksums.json",
        "DuRiCore/deployment/deployment_metadata.json",
        "DuRiCore/deployment/checksums.sig",
        "DuRiCore/deployment/deployment_metadata.sig"
    ]
    
    print("📦 아티팩트 파일:")
    for f in artifact_files:
        if os.path.exists(f):
            print(f"   ✅ {f}")
        else:
            print(f"   ❌ {f} (누락)")

# 무결성 검증 (공통)
print("무결성 검증 중...")
integrity_result = d.verify_integrity()

# 감사/가시성: 메트릭 라벨 출력
print("📊 감사/가시성 메트릭:")
print(f"   - deployment_id: {integrity_result.get('deployment_id', 'unknown')}")
print(f"   - schema_version: {integrity_result.get('schema_version', 'unknown')}")
print(f"   - hash_algorithm: {integrity_result.get('hash_algorithm', 'unknown')}")
print(f"   - hash_version: {integrity_result.get('hash_version', 'unknown')}")
print(f"   - mode: {integrity_result.get('mode', 'unknown')}")
print(f"   - status: {integrity_result.get('status', 'unknown')}")
print(f"   - scan_duration_ms: {integrity_result['summary'].get('scan_duration_ms', 0)}")
print(f"   - bytes_hashed: {integrity_result['summary'].get('bytes_hashed', 0)}")

if 'ignore_info' in integrity_result:
    print(f"   - ignore_hash: {integrity_result['ignore_info'].get('current_hash', 'unknown')}")

# 완전 철벽: 모든 실패 상태 체크
if (not integrity_result['integrity_verified']) or \
   (integrity_result['status'] in ('tampered','policy_changed','corrupted','error')):
    print(f"❌ 무결성 검증 실패: {integrity_result['status']}")
    print(f"   - 수정된 파일: {integrity_result['summary']['modified_files']}")
    print(f"   - 누락된 파일: {integrity_result['summary']['missing_files']}")
    print(f"   - 새 파일: {integrity_result['summary']['new_files']}")
    
    # HMAC 서명 상태
    if 'signatures' in integrity_result:
        sig_info = integrity_result['signatures']
        print(f"   - HMAC 서명: checksums={sig_info['checksums_hmac_ok']}, metadata={sig_info['metadata_hmac_ok']}")
    
    # ignore 정책 변경
    if integrity_result.get('ignore_info', {}).get('mismatch'):
        print(f"   - ignore 정책 변경 감지")
    
    sys.exit(1)

print(f"✅ 무결성 검증 성공: {integrity_result['summary']}")

# Provenance 검증 (선택적)
print("Provenance 검증 중...")
provenance_result = d.verify_provenance()

if not provenance_result['provenance_verified']:
    print(f"⚠️ Provenance 검증 실패: {provenance_result['status']}")
    # Provenance 실패는 경고만 (필수는 아님)
else:
    print("✅ Provenance 검증 성공")

print("🎉 모든 검증 통과!")
PY

echo "✅ CI 무결성 검증 완료!"
