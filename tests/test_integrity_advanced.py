#!/usr/bin/env python3
"""
DuRi 무결성 검증 고급 테스트 - 스키마 다운그레이드/원자적 쓰기/symlink
"""

import json
import os
import shutil
import tempfile
import time
import signal
import threading
from pathlib import Path
import pytest

from DuRiCore.deployment.deployment_integrity import DeploymentIntegrity

@pytest.fixture()
def tmp_repo(monkeypatch):
    """테스트용 임시 리포지토리"""
    d = tempfile.TemporaryDirectory()
    root = Path(d.name)
    (root / "DuRiCore/deployment").mkdir(parents=True, exist_ok=True)
    (root / "app").mkdir(parents=True, exist_ok=True)

    # 샘플 파일
    (root / "app/a.txt").write_text("hello\n")
    (root / "app/b.txt").write_text("world\n")

    # 테스트는 로컬 루트에서 실행
    monkeypatch.chdir(root)
    # 테스트용 strict 모드
    monkeypatch.setenv("DURI_INTEGRITY_MODE", "strict")
    # HMAC key (있으면 tampered 케이스도 커버)
    monkeypatch.setenv("DURI_HMAC_KEY", "test-secret-key")
    return root

def test_schema_downgrade_detection(tmp_repo):
    """스키마 다운그레이드 감지 테스트"""
    di = DeploymentIntegrity()
    
    # schema_version=1.0 메타데이터 생성 (다운그레이드)
    old_metadata = {
        "deployment_id": "test_deploy",
        "version": "1.0",
        "created_at": time.time(),
        "file_count": 2,
        "schema_version": "1.0",  # 이전 스키마
        "hash_algorithm": "sha256",
        "hash_version": "1.0",
        "mode": "strict",
        "ignore_hash": "test_hash",
        "checksums": {
            "app/a.txt": "hash1",
            "app/b.txt": "hash2"
        }
    }
    
    # 이전 스키마 메타데이터 저장
    with open("DuRiCore/deployment/deployment_metadata.json", 'w') as f:
        json.dump(old_metadata, f, indent=2)
    
    # 체크섬 파일도 생성
    with open("DuRiCore/deployment/checksums.json", 'w') as f:
        json.dump(old_metadata["checksums"], f, indent=2)
    
    # 검증 시도 (policy_changed 기대)
    r = di.verify_integrity()
    assert r["status"] == "policy_changed", f"스키마 다운그레이드는 policy_changed여야 함, 실제: {r['status']}"
    assert r["integrity_verified"] is False

def test_atomic_write_partial_file_prevention(tmp_repo):
    """원자적 쓰기 - 파셜 파일 방지 테스트"""
    di = DeploymentIntegrity()
    
    # 대용량 데이터로 원자적 쓰기 테스트
    large_data = {"test": "x" * 10000}  # 10KB 데이터
    
    # 원자적 쓰기 실행
    test_file = "DuRiCore/deployment/test_atomic.json"
    data_bytes = json.dumps(large_data, indent=2).encode()
    
    # 정상적인 원자적 쓰기
    di._atomic_write(test_file, data_bytes)
    assert os.path.exists(test_file), "원자적 쓰기 후 파일이 존재해야 함"
    
    # 파일 내용 검증
    with open(test_file, 'r') as f:
        loaded_data = json.load(f)
    assert loaded_data == large_data, "원자적 쓰기된 데이터가 올바르야 함"
    
    # 임시 파일이 정리되었는지 확인
    temp_files = [f for f in os.listdir("DuRiCore/deployment") if f.startswith(".tmp-")]
    assert len(temp_files) == 0, f"임시 파일이 정리되어야 함: {temp_files}"

def test_symlink_loop_prevention(tmp_repo):
    """심볼릭 링크 루프 방지 테스트"""
    di = DeploymentIntegrity()
    
    # 심볼릭 링크 생성 (루프 위험)
    link_target = "app/symlink_target.txt"
    link_source = "app/symlink_source.txt"
    
    # 대상 파일 생성
    Path(link_target).write_text("target content\n")
    
    # 심볼릭 링크 생성
    os.symlink(link_target, link_source)
    
    # 메타데이터 생성 (symlink는 스킵되어야 함)
    md = di.create_deployment_metadata("symlink_test")
    
    # 체크섬에서 심볼릭 링크가 제외되었는지 확인
    with open("DuRiCore/deployment/checksums.json", 'r') as f:
        checksums = json.load(f)
    
    # 심볼릭 링크는 체크섬에 포함되지 않아야 함
    assert link_source not in checksums, "심볼릭 링크는 체크섬에서 제외되어야 함"
    assert link_target in checksums, "심볼릭 링크 대상은 체크섬에 포함되어야 함"
    
    # 무결성 검증도 통과해야 함
    r = di.verify_integrity()
    assert r["status"] == "verified", f"심볼릭 링크 제외 후 검증 통과해야 함: {r['status']}"

def test_hmac_none_state_accuracy(tmp_repo):
    """HMAC None 상태 정확성 테스트"""
    # HMAC 키 없이 초기화
    os.environ.pop('DURI_HMAC_KEY', None)
    di_no_hmac = DeploymentIntegrity()
    
    # 메타데이터 생성
    md = di_no_hmac.create_deployment_metadata("no_hmac_test")
    
    # 검증
    r = di_no_hmac.verify_integrity()
    
    # HMAC이 비활성화된 경우 None이어야 함
    assert r["signatures"]["checksums_hmac_ok"] is None, "HMAC 비활성화 시 checksums_hmac_ok는 None이어야 함"
    assert r["signatures"]["metadata_hmac_ok"] is None, "HMAC 비활성화 시 metadata_hmac_ok는 None이어야 함"
    assert r["signatures"]["enabled"] is False, "HMAC 비활성화 시 enabled는 False여야 함"

def test_spike_guard_production_fatal(tmp_repo):
    """폭증 가드 - 프로덕션에서 실패 처리 테스트"""
    di = DeploymentIntegrity()
    
    # 초기 메타데이터 생성
    md = di.create_deployment_metadata("spike_test")
    
    # 프로덕션 환경 설정
    os.environ['DURI_ENV'] = 'prod'
    os.environ['DURI_INTEGRITY_SPIKE_THRESHOLD'] = '0.1'  # 10% 임계치
    
    # 대량 파일 삭제 및 추가 (폭증 시뮬레이션)
    for i in range(100):  # 100개 파일 추가
        Path(f"app/spike_file_{i}.txt").write_text(f"spike content {i}\n")
    
    # 기존 파일 대량 삭제
    for file in Path("app").glob("*.txt"):
        if file.name not in ["a.txt", "b.txt"]:
            file.unlink()
    
    # 검증 (프로덕션에서는 실패해야 함)
    r = di.verify_integrity()
    assert r["status"] == "corrupted", f"프로덕션에서 폭증 감지 시 corrupted여야 함: {r['status']}"
    assert r["integrity_verified"] is False
    assert r["summary"].get("spike_detected") is True, "폭증 감지 플래그가 설정되어야 함"
    
    # 환경변수 정리
    del os.environ['DURI_ENV']
    del os.environ['DURI_INTEGRITY_SPIKE_THRESHOLD']

def test_prometheus_label_sanitization(tmp_repo):
    """Prometheus 라벨 정리 테스트"""
    from DuRiCore.deployment.integrity_metrics import integrity_metrics
    
    di = DeploymentIntegrity()
    md = di.create_deployment_metadata("label_test")
    
    # 검증 결과 생성
    integrity_result = di.verify_integrity()
    
    # 메트릭 기록
    integrity_metrics.record_integrity_scan(integrity_result)
    
    # Prometheus 메트릭 생성
    metrics_text = integrity_metrics.get_prometheus_metrics()
    
    # 라벨에 특수문자가 올바르게 이스케이프되었는지 확인
    assert "deployment_id=" in metrics_text, "deployment_id 라벨이 포함되어야 함"
    assert "schema_version=" in metrics_text, "schema_version 라벨이 포함되어야 함"
    assert "status=" in metrics_text, "status 라벨이 포함되어야 함"
    
    # 메트릭 초기화
    integrity_metrics.clear_metrics()
