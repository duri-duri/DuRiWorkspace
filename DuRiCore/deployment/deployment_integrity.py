#!/usr/bin/env python3
"""
DuRi Deployment Integrity - Day 76 배포 무결성 강화 (끝판왕 완성)
"""

import os
import json
import hashlib
import hmac
import time
import tempfile
from fnmatch import fnmatch
from pathlib import Path
from typing import Dict, Any, List, Optional
from DuRiCore.global_logging_manager import get_duri_logger

logger = get_duri_logger("deployment_integrity")

class DeploymentIntegrity:
    """배포 무결성 검증 클래스 (Day 76 끝판왕 완성)"""
    
    def __init__(self, mode: str = None):
        self.checksums_file = "DuRiCore/deployment/checksums.json"
        self.metadata_file = "DuRiCore/deployment/deployment_metadata.json"
        self.provenance_file = "DuRiCore/deployment/provenance.json"
        
        # HMAC 서명 파일 경로 보장 (필수 필드)
        self.checksums_sig_file = "DuRiCore/deployment/checksums.sig"
        self.metadata_sig_file = "DuRiCore/deployment/deployment_metadata.sig"
        
        # Day 76: 해시 알고리즘 버저닝 + 스키마 버전 업 (필수 필드)
        self.hash_algorithm = "sha256"  # 기본 알고리즘
        self.hash_version = "1.0"       # 해시 버전
        self.schema_version = "1.1"     # 스키마 버전 업그레이드
        
        # Day 76: 검증 모드 스위치 + 프로덕션 가드레일
        if os.getenv("DURI_ENV") == "prod":
            self.mode = "strict"  # 프로덕션에서는 강제 strict
        else:
            self.mode = mode or os.getenv("DURI_INTEGRITY_MODE", "strict")  # "strict" | "lenient"
        
        # HMAC 서명 키 보장 (필수 필드)
        hmac_key_str = os.getenv("DURI_HMAC_KEY", "")
        self.hmac_key = hmac_key_str.encode() if hmac_key_str else None
        
        logger.info(f"DeploymentIntegrity 초기화: hash_algorithm={self.hash_algorithm}, version={self.hash_version}, schema_version={self.schema_version}, mode={self.mode}, hmac_enabled={bool(self.hmac_key)}")
    
    def _normalize_rel(self, file_path: str) -> str:
        """
        워크스페이스 루트 기준 상대 경로 + POSIX 형태 고정
        
        Args:
            file_path: 파일 경로
            
        Returns:
            정규화된 상대 경로
        """
        p = Path(file_path).resolve()
        root = Path(".").resolve()
        try:
            rel = p.relative_to(root)
        except Exception:
            # 루트 밖이면 제외(보안)
            return "__OUTSIDE__"
        return rel.as_posix()
    
    def _dedup_patterns(self, patterns: List[str]) -> List[str]:
        """
        패턴 중복 제거 및 정렬
        
        Args:
            patterns: 패턴 리스트
            
        Returns:
            중복 제거된 정렬된 패턴 리스트
        """
        # 공백/중복 제거, 순서 안정화를 위해 정렬
        cleaned = [p.strip() for p in patterns if p and p.strip()]
        return sorted(set(cleaned))
    
    def _hmac_sign(self, payload: bytes) -> str:
        """
        HMAC 서명 생성 (타이밍 공격 방지)
        
        Args:
            payload: 서명할 데이터
            
        Returns:
            HMAC 서명 (hex)
        """
        if not self.hmac_key:
            return ""
        return hmac.new(self.hmac_key, payload, hashlib.sha256).hexdigest()
    
    def _hmac_verify(self, payload: bytes, sig: str) -> bool:
        """
        HMAC 서명 검증 (타이밍 공격 방지)
        
        Args:
            payload: 검증할 데이터
            sig: 서명 (hex)
            
        Returns:
            검증 성공하면 True
        """
        if not self.hmac_key:
            return True  # 서명 비활성화 상태
        expected = self._hmac_sign(payload)
        return hmac.compare_digest(expected, sig)
    
    def _atomic_write(self, path: str, data: bytes):
        """
        원자적 쓰기 (경쟁 상태 방지)
        
        Args:
            path: 파일 경로
            data: 쓸 데이터
        """
        d = os.path.dirname(path)
        os.makedirs(d, exist_ok=True)
        fd, tmp = tempfile.mkstemp(dir=d, prefix=".tmp-", suffix=".json")
        try:
            with os.fdopen(fd, "wb") as w:
                w.write(data)
            os.replace(tmp, path)
        except Exception:
            os.unlink(tmp)
            raise
    
    def _calculate_file_hash(self, file_path: str) -> str:
        """
        파일 해시 계산 (대용량 파일 안전성)
        
        Args:
            file_path: 파일 경로
            
        Returns:
            해시값
        """
        try:
            if self.hash_algorithm == "sha256":
                hash_obj = hashlib.sha256()
            elif self.hash_algorithm == "sha512":
                hash_obj = hashlib.sha512()
            else:
                hash_obj = hashlib.sha256()  # 기본값
            
            # 대용량 파일 안전성: 1MB 청크로 최적화
            with open(file_path, 'rb') as f:
                for chunk in iter(lambda: f.read(1024 * 1024), b""):
                    hash_obj.update(chunk)
            
            return hash_obj.hexdigest()
        except Exception as e:
            logger.debug(f"파일 해시 계산 실패: {file_path} - {e}")
            return ""
    
    def _get_ignore_patterns(self) -> List[str]:
        """무시할 파일 패턴 가져오기 (ignore 해시 충돌 여지 최소화)"""
        base = [
            ".git/", "__pycache__/", "*.pyc", "*.pyo", ".pytest_cache/", "node_modules/",
            ".DS_Store", "Thumbs.db", "*.log", ".env", ".env.local", ".env.*.local",
            "*.tmp", "*.temp",
            ".reports/", "DuRi_Day11_15_starter/", "data/prometheus/",
            "DuRiCore/deployment/checksums.json",
            "DuRiCore/deployment/deployment_metadata.json",
            "DuRiCore/deployment/provenance.json",
        ]
        
        # duriignore.json 파일에서 패턴 로드
        try:
            if os.path.exists("duriignore.json"):
                with open("duriignore.json", 'r') as f:
                    cfg = json.load(f)
                patterns = [p for p in cfg.get("patterns", []) if p]
                base += patterns
                logger.info(f"duriignore.json에서 {len(patterns)}개 패턴 로드")
        except Exception as e:
            logger.warning(f"duriignore.json 로드 실패: {e}")
        
        # ENV에서 추가 제외 패턴 가져오기
        extra = os.getenv("DURI_INTEGRITY_EXCLUDES", "")
        if extra:
            env_patterns = [x.strip() for x in extra.split(",") if x.strip()]
            base += env_patterns
            logger.info(f"ENV에서 {len(env_patterns)}개 패턴 로드")
        
        return self._dedup_patterns(base)
    
    def _should_ignore_file(self, file_path: str) -> bool:
        """
        파일 무시 여부 확인 (디렉토리 패턴 매칭 정확도)
        
        Args:
            file_path: 파일 경로
            
        Returns:
            무시해야 하면 True
        """
        rel = self._normalize_rel(file_path)
        if rel == "__OUTSIDE__":
            return True
        
        patterns = self._get_ignore_patterns()
        for pat in patterns:
            if pat.endswith("/"):
                # 디렉토리 패턴: 해당 디렉토리 이하 전부 제외
                if rel == pat[:-1] or rel.startswith(pat):
                    return True
            else:
                # 파일/글롭 패턴
                if fnmatch(rel, pat):
                    return True
        
        return False
    
    def create_deployment_metadata(self, version: str) -> Dict[str, Any]:
        """
        배포 메타데이터 생성 (끝판왕 완성)
        
        Args:
            version: 버전
            
        Returns:
            배포 메타데이터
        """
        try:
            deployment_id = f"deploy_{int(time.time())}_{hashlib.md5(version.encode()).hexdigest()[:8]}"
            
            # 파일 스캔 및 해시 계산 (결정론적 순서)
            checksums = {}
            file_count = 0
            
            for root, dirs, files in os.walk(".", topdown=True):
                # 결정론적 순서 보장
                dirs.sort()
                files.sort()
                
                # .git 디렉토리 제외
                dirs[:] = [d for d in dirs if not d.startswith('.')]
                
                for file in files:
                    file_path = os.path.join(root, file)
                    
                    # 심볼릭 링크 안전가드 (루프/탈출 방지)
                    if os.path.islink(file_path):
                        continue  # 심볼릭 링크는 스킵
                    
                    # 무시할 파일 제외
                    if self._should_ignore_file(file_path):
                        continue
                    
                    # 파일 해시 계산
                    file_hash = self._calculate_file_hash(file_path)
                    if file_hash:
                        # 상대 경로로 저장 (결정론적)
                        rel = self._normalize_rel(file_path)
                        checksums[rel] = file_hash
                        file_count += 1
            
            # ignore 해시 계산 (비출력 제어문자로 충돌 여지 최소화)
            ignore_patterns = self._get_ignore_patterns()
            SEP = "\x1f"  # 비출력 제어문자
            ignore_hash = hashlib.sha256(SEP.join(ignore_patterns).encode()).hexdigest()[:16]
            
            # 메타데이터 생성
            metadata = {
                "deployment_id": deployment_id,
                "version": version,
                "created_at": time.time(),
                "file_count": file_count,
                "schema_version": self.schema_version,  # 스키마 버전 업그레이드
                "hash_algorithm": self.hash_algorithm,
                "hash_version": self.hash_version,
                "mode": self.mode,
                "ignore_hash": ignore_hash,
                "checksums": checksums
            }
            
            # 원자적 쓰기 (경쟁 상태 방지)
            checksums_data = json.dumps(checksums, indent=2, sort_keys=True).encode()
            self._atomic_write(self.checksums_file, checksums_data)
            
            # HMAC for checksums.json
            try:
                with open(self.checksums_file, 'rb') as cf:
                    sig = self._hmac_sign(cf.read())
                if sig:
                    with open(self.checksums_sig_file, 'w') as sf:
                        sf.write(sig)
            except Exception as e:
                logger.warning(f"checksums HMAC 생성 실패: {e}")
            
            metadata_data = json.dumps(metadata, indent=2, sort_keys=True).encode()
            self._atomic_write(self.metadata_file, metadata_data)
            
            # HMAC for deployment_metadata.json
            try:
                with open(self.metadata_file, 'rb') as mf:
                    sig = self._hmac_sign(mf.read())
                if sig:
                    with open(self.metadata_sig_file, 'w') as sf:
                        sf.write(sig)
            except Exception as e:
                logger.warning(f"metadata HMAC 생성 실패: {e}")
            
            logger.info(f"배포 메타데이터 생성 완료: {deployment_id} ({file_count}개 파일)")
            return metadata
            
        except Exception as e:
            logger.error(f"배포 메타데이터 생성 실패: {e}")
            return {}
    
    def verify_integrity(self) -> Dict[str, Any]:
        """
        무결성 검증 (끝판왕 완성)
        
        Returns:
            검증 결과
        """
        try:
            t0 = time.perf_counter()
            bytes_hashed = 0
            
            if not os.path.exists(self.checksums_file):
                return {
                    "integrity_verified": False,
                    "status": "no_checksums",
                    "summary": {"error": "checksums.json not found"}
                }
            
            if not os.path.exists(self.metadata_file):
                return {
                    "integrity_verified": False,
                    "status": "no_metadata",
                    "summary": {"error": "deployment_metadata.json not found"}
                }
            
            # 메타데이터 로드 + HMAC 검증
            with open(self.metadata_file, 'r') as f:
                metadata = json.load(f)
            
            # HMAC 상태 표현 정확화 (켜지지 않은 경우 None)
            metadata_sig_ok = None
            if self.hmac_key:
                try:
                    with open(self.metadata_file, 'rb') as mf:
                        payload = mf.read()
                    with open(self.metadata_sig_file, 'r') as sf:
                        sig = sf.read().strip()
                    metadata_sig_ok = self._hmac_verify(payload, sig)
                except Exception as e:
                    logger.warning(f"metadata HMAC 검증 실패: {e}")
                    metadata_sig_ok = False
            
            # 스키마 버전 확인 (이전 스키마는 policy_changed 처리)
            stored_schema_version = metadata.get("schema_version", "1.0")
            stored_hash_algorithm = metadata.get("hash_algorithm", "sha256")
            stored_hash_version = metadata.get("hash_version", "1.0")
            stored_mode = metadata.get("mode", "strict")
            
            # prod 정책 일관성: hash_algorithm/hash_version 불일치도 prod에서 실패로 격상
            algo_mismatch = (stored_hash_algorithm != self.hash_algorithm or 
                           stored_hash_version != self.hash_version)
            
            if stored_schema_version != self.schema_version:
                logger.warning(f"스키마 버전 불일치: stored={stored_schema_version}, current={self.schema_version}")
            
            if stored_hash_algorithm != self.hash_algorithm:
                logger.warning(f"해시 알고리즘 불일치: stored={stored_hash_algorithm}, current={self.hash_algorithm}")
            
            if stored_hash_version != self.hash_version:
                logger.warning(f"해시 버전 불일치: stored={stored_hash_version}, current={self.hash_version}")
            
            if stored_mode != self.mode:
                logger.warning(f"검증 모드 불일치: stored={stored_mode}, current={self.mode}")
            
            # 체크섬 로드 + HMAC 검증
            with open(self.checksums_file, 'r') as f:
                stored_checksums = json.load(f)
            
            # HMAC 상태 표현 정확화 (켜지지 않은 경우 None)
            checksums_sig_ok = None
            if self.hmac_key:
                try:
                    with open(self.checksums_file, 'rb') as cf:
                        payload = cf.read()
                    with open(self.checksums_sig_file, 'r') as sf:
                        sig = sf.read().strip()
                    checksums_sig_ok = self._hmac_verify(payload, sig)
                except Exception as e:
                    logger.warning(f"checksums HMAC 검증 실패: {e}")
                    checksums_sig_ok = False
            
            # 현재 파일 해시 계산 (결정론적 순서)
            current_checksums = {}
            current_file_count = 0
            
            for root, dirs, files in os.walk(".", topdown=True):
                # 결정론적 순서 보장
                dirs.sort()
                files.sort()
                dirs[:] = [d for d in dirs if not d.startswith('.')]
                
                for file in files:
                    file_path = os.path.join(root, file)
                    
                    # 심볼릭 링크 안전가드 (루프/탈출 방지)
                    if os.path.islink(file_path):
                        continue  # 심볼릭 링크는 스킵
                    
                    if self._should_ignore_file(file_path):
                        continue
                    
                    file_hash = self._calculate_file_hash(file_path)
                    if file_hash:
                        # 상대 경로로 저장 (결정론적)
                        rel = self._normalize_rel(file_path)
                        current_checksums[rel] = file_hash
                        current_file_count += 1
                        
                        # 성능 관측용 바이트 카운트
                        try:
                            bytes_hashed += os.path.getsize(file_path)
                        except Exception:
                            pass
            
            # 비교
            modified_files = []
            missing_files = []
            
            for file_path, stored_hash in stored_checksums.items():
                if file_path not in current_checksums:
                    missing_files.append(file_path)
                elif current_checksums[file_path] != stored_hash:
                    modified_files.append(file_path)
            
            # 새로 추가된 파일 확인
            new_files = [f for f in current_checksums.keys() if f not in stored_checksums]
            
            # ignore 해시 확인 (비출력 제어문자로 충돌 여지 최소화)
            ignore_patterns = self._get_ignore_patterns()
            SEP = "\x1f"  # 비출력 제어문자
            current_ignore_hash = hashlib.sha256(SEP.join(ignore_patterns).encode()).hexdigest()[:16]
            stored_ignore_hash = metadata.get("ignore_hash", "")
            
            ignore_mismatch = current_ignore_hash != stored_ignore_hash
            
            # 새/누락 파일 폭증 방지 가드 (임계치/Treat-as-fatal 운영화)
            total_stored = len(stored_checksums)
            spike_threshold = float(os.getenv("DURI_INTEGRITY_SPIKE_THRESHOLD", "0.3"))
            
            if (len(missing_files) > spike_threshold * total_stored and 
                len(new_files) > spike_threshold * total_stored):
                logger.warning(f"파일 폭증 감지: missing={len(missing_files)}, new={len(new_files)}, total={total_stored}")
                # 프로덕션에서는 실패 처리
                if os.getenv("DURI_ENV") == "prod":
                    status = "corrupted"
                    integrity_verified = False
                    result = {
                        "integrity_verified": integrity_verified,
                        "status": status,
                        "deployment_id": metadata.get("deployment_id"),
                        "schema_version": stored_schema_version,
                        "hash_algorithm": stored_hash_algorithm,
                        "hash_version": stored_hash_version,
                        "mode": self.mode,
                        "summary": {
                            "total_files": len(stored_checksums),
                            "verified_files": len(stored_checksums) - len(modified_files) - len(missing_files),
                            "modified_files": len(modified_files),
                            "missing_files": len(missing_files),
                            "new_files": len(new_files),
                            "scan_duration_ms": int((time.perf_counter() - t0) * 1000),
                            "bytes_hashed": bytes_hashed,
                            "spike_detected": True
                        },
                        "modified_files": modified_files,
                        "missing_files": missing_files,
                        "new_files": new_files,
                        "ignore_info": {
                            "current_hash": current_ignore_hash,
                            "stored_hash": stored_ignore_hash,
                            "mismatch": ignore_mismatch
                        },
                        "signatures": {
                            "checksums_hmac_ok": checksums_sig_ok,
                            "metadata_hmac_ok": metadata_sig_ok,
                            "enabled": bool(self.hmac_key),
                        }
                    }
                    logger.error(f"파일 폭증으로 인한 무결성 검증 실패: {result['summary']}")
                    return result
            
            # 검증 모드 및 정책 변경 감지
            policy_changed = (ignore_mismatch or 
                            stored_schema_version != self.schema_version or
                            (self.mode == "strict" and algo_mismatch))
            
            if self.mode == "strict":
                integrity_verified = (len(modified_files) == 0 and 
                                    len(missing_files) == 0 and 
                                    not policy_changed)
            else:  # lenient: new_files는 허용, 단 policy_changed는 실패로 처리(운영 안정성)
                integrity_verified = (len(modified_files) == 0 and
                                    len(missing_files) == 0 and
                                    not policy_changed)
            
            # HMAC 서명 검증 결과 반영 (정확화된 조건)
            if self.hmac_key and (checksums_sig_ok is False or metadata_sig_ok is False):
                status = "tampered"
                integrity_verified = False
            else:
                status = "verified" if integrity_verified else ("policy_changed" if policy_changed else "corrupted")
            
            # 성능 관측 정보
            scan_ms = int((time.perf_counter() - t0) * 1000)
            
            result = {
                "integrity_verified": integrity_verified,
                "status": status,
                "deployment_id": metadata.get("deployment_id"),
                "schema_version": stored_schema_version,
                "hash_algorithm": stored_hash_algorithm,
                "hash_version": stored_hash_version,
                "mode": self.mode,
                "summary": {
                    "total_files": len(stored_checksums),
                    "verified_files": len(stored_checksums) - len(modified_files) - len(missing_files),
                    "modified_files": len(modified_files),
                    "missing_files": len(missing_files),
                    "new_files": len(new_files),
                    "scan_duration_ms": scan_ms,
                    "bytes_hashed": bytes_hashed
                },
                "modified_files": modified_files,
                "missing_files": missing_files,
                "new_files": new_files,
                "ignore_info": {
                    "current_hash": current_ignore_hash,
                    "stored_hash": stored_ignore_hash,
                    "mismatch": ignore_mismatch
                },
                "signatures": {
                    "checksums_hmac_ok": checksums_sig_ok,
                    "metadata_hmac_ok": metadata_sig_ok,
                    "enabled": bool(self.hmac_key),
                }
            }
            
            if integrity_verified:
                logger.info(f"무결성 검증 성공: {result['summary']}")
            else:
                logger.warning(f"무결성 검증 실패: {result['summary']}")
            
            return result
            
        except Exception as e:
            logger.error(f"무결성 검증 실패: {e}")
            return {
                "integrity_verified": False,
                "status": "error",
                "summary": {"error": str(e)}
            }
    
    def create_provenance(self, build_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        Provenance 정보 생성
        
        Args:
            build_info: 빌드 정보
            
        Returns:
            Provenance 정보
        """
        try:
            provenance = {
                "version": "1.0",
                "created_at": time.time(),
                "build_info": build_info,
                "deployment_id": self.get_deployment_info().get("deployment_id"),
                "hash_algorithm": self.hash_algorithm,
                "hash_version": self.hash_version,
                "signature": self._generate_provenance_signature(build_info)
            }
            
            # 원자적 쓰기
            provenance_data = json.dumps(provenance, indent=2, sort_keys=True).encode()
            self._atomic_write(self.provenance_file, provenance_data)
            
            logger.info("Provenance 정보 생성 완료")
            return provenance
            
        except Exception as e:
            logger.error(f"Provenance 생성 실패: {e}")
            return {}
    
    def verify_provenance(self) -> Dict[str, Any]:
        """
        Provenance 검증
        
        Returns:
            검증 결과
        """
        try:
            if not os.path.exists(self.provenance_file):
                return {
                    "provenance_verified": False,
                    "status": "no_provenance",
                    "error": "provenance.json not found"
                }
            
            with open(self.provenance_file, 'r') as f:
                provenance = json.load(f)
            
            # 서명 검증
            build_info = provenance.get("build_info", {})
            stored_signature = provenance.get("signature", "")
            expected_signature = self._generate_provenance_signature(build_info)
            
            signature_valid = stored_signature == expected_signature
            
            result = {
                "provenance_verified": signature_valid,
                "status": "verified" if signature_valid else "invalid_signature",
                "provenance": provenance,
                "signature_valid": signature_valid
            }
            
            if signature_valid:
                logger.info("Provenance 검증 성공")
            else:
                logger.warning("Provenance 검증 실패: 서명 불일치")
            
            return result
            
        except Exception as e:
            logger.error(f"Provenance 검증 실패: {e}")
            return {
                "provenance_verified": False,
                "status": "error",
                "error": str(e)
            }
    
    def _generate_provenance_signature(self, build_info: Dict[str, Any]) -> str:
        """Provenance 서명 생성"""
        # 간단한 서명 생성 (실제로는 더 강력한 서명 사용)
        signature_data = f"{build_info.get('git_sha', '')}{build_info.get('build_time', '')}{self.hash_algorithm}"
        return hashlib.sha256(signature_data.encode()).hexdigest()
    
    def get_deployment_info(self) -> Dict[str, Any]:
        """배포 정보 가져오기"""
        try:
            if os.path.exists(self.metadata_file):
                with open(self.metadata_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            logger.error(f"배포 정보 로드 실패: {e}")
        
        return {}

# 전역 인스턴스
deployment_integrity = DeploymentIntegrity()
