#!/usr/bin/env python3
"""
DuRi 무결성 검증 테스트 - 라운드트립/변조/정책변경
"""

import json
import os
import shutil
import tempfile
import time
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

def _read_json(p: Path):
    """JSON 파일 읽기"""
    return json.loads(p.read_text())

def test_roundtrip_success(tmp_repo):
    """라운드트립 성공 테스트"""
    di = DeploymentIntegrity()
    md = di.create_deployment_metadata("t1")
    assert md and md["deployment_id"]

    r = di.verify_integrity()
    assert r["status"] == "verified"
    assert r["integrity_verified"] is True
    assert r["summary"]["modified_files"] == 0

def test_modification_detected(tmp_repo):
    """파일 변조 감지 테스트"""
    di = DeploymentIntegrity()
    di.create_deployment_metadata("t2")

    # 파일 변조
    Path("app/a.txt").write_text("tampered!\n")
    r = di.verify_integrity()
    assert r["status"] in ("corrupted", "tampered")
    assert r["integrity_verified"] is False
    assert r["summary"]["modified_files"] >= 1

def test_policy_changed(tmp_repo):
    """정책 변경 감지 테스트"""
    di = DeploymentIntegrity()
    di.create_deployment_metadata("t3")

    # ignore 정책 변경
    Path("duriignore.json").write_text(json.dumps({"patterns": ["app/*.txt"]}))
    r = di.verify_integrity()
    assert r["ignore_info"]["mismatch"] is True
    assert r["status"] == "policy_changed"
    assert r["integrity_verified"] is False

def test_tampered_manifest_signature(tmp_repo):
    """메타데이터 서명 위조 감지 테스트"""
    di = DeploymentIntegrity()
    di.create_deployment_metadata("t4")

    # checksums.json 서명 위조
    sig_path = Path("DuRiCore/deployment/checksums.sig")
    if sig_path.exists():
        sig_path.write_text("deadbeef")  # 잘못된 서명
        r = di.verify_integrity()
        assert r["status"] == "tampered"
        assert r["signatures"]["checksums_hmac_ok"] is False
        assert r["integrity_verified"] is False

def test_ignore_pattern_matching(tmp_repo):
    """ignore 패턴 매칭 테스트"""
    di = DeploymentIntegrity()
    
    # 테스트 케이스
    test_cases = [
        ("DuRiCore/deployment/checksums.json", True),
        ("data/prometheus/wal/00000092", True),
        ("DuRi_Day11_15_starter/tools/test.py", True),
        ("DuRiCore/health/canary_endpoint.py", False),
        (".reports/synth/duri_synth.prom", True),
        ("logs/app.log", True),              # *.log
        ("src/app.py", False),
    ]
    
    for path, expected in test_cases:
        result = di._should_ignore_file(path)
        assert result is expected, f"Path {path} should be {'ignored' if expected else 'included'}"

def test_production_mode_guard(tmp_repo):
    """프로덕션 모드 가드레일 테스트"""
    # 프로덕션 환경에서 lenient 설정해도 strict로 강제되는지 확인
    os.environ['DURI_ENV'] = 'prod'
    os.environ['DURI_INTEGRITY_MODE'] = 'lenient'  # 강제로 lenient 설정
    
    di = DeploymentIntegrity()
    assert di.mode == "strict", "프로덕션에서는 lenient 설정해도 strict로 강제되어야 함"
    
    # 환경변수 정리
    del os.environ['DURI_ENV']
    del os.environ['DURI_INTEGRITY_MODE']

def test_hmac_signature_verification(tmp_repo):
    """HMAC 서명 검증 테스트"""
    di = DeploymentIntegrity()
    
    # HMAC 키가 설정되어 있는지 확인
    assert di.hmac_key, "HMAC 키가 설정되어 있어야 함"
    
    # 서명 생성 및 검증 테스트
    test_data = b"test data"
    signature = di._hmac_sign(test_data)
    assert signature, "서명이 생성되어야 함"
    
    # 올바른 서명 검증
    assert di._hmac_verify(test_data, signature), "올바른 서명은 검증되어야 함"
    
    # 잘못된 서명 검증
    assert not di._hmac_verify(test_data, "wrong_signature"), "잘못된 서명은 검증 실패해야 함"

def test_deterministic_checksums(tmp_repo):
    """결정론적 체크섬 생성 테스트"""
    di = DeploymentIntegrity()
    
    # 첫 번째 스냅샷
    md1 = di.create_deployment_metadata("test")
    checksums1 = _read_json(Path("DuRiCore/deployment/checksums.json"))
    
    # 두 번째 스냅샷 (동일한 파일 상태)
    md2 = di.create_deployment_metadata("test")
    checksums2 = _read_json(Path("DuRiCore/deployment/checksums.json"))
    
    # 체크섬이 동일해야 함 (결정론적)
    assert checksums1 == checksums2, "동일한 파일 상태에서 체크섬이 동일해야 함"

def test_performance_metrics(tmp_repo):
    """성능 메트릭 테스트"""
    di = DeploymentIntegrity()
    di.create_deployment_metadata("perf_test")
    
    r = di.verify_integrity()
    assert "scan_duration_ms" in r["summary"], "스캔 시간이 포함되어야 함"
    assert "bytes_hashed" in r["summary"], "해시된 바이트 수가 포함되어야 함"
    assert r["summary"]["scan_duration_ms"] > 0, "스캔 시간이 0보다 커야 함"
    assert r["summary"]["bytes_hashed"] > 0, "해시된 바이트 수가 0보다 커야 함"
