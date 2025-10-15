#!/usr/bin/env python3
"""
DuRi 배포 산출물 무결성 관리
"""

import hashlib
import os
import json
from typing import Dict, Any
from datetime import datetime

class DeploymentIntegrityManager:
    def __init__(self, artifacts_dir: str = "./artifacts", logs_dir: str = "./logs"):
        self.artifacts_dir = artifacts_dir
        self.logs_dir = logs_dir
        os.makedirs(artifacts_dir, exist_ok=True)
        os.makedirs(logs_dir, exist_ok=True)
        
    def calculate_sha256(self, file_path: str) -> str:
        """파일 SHA256 체크섬 계산"""
        try:
            with open(file_path, 'rb') as f:
                return hashlib.sha256(f.read()).hexdigest()
        except Exception as e:
            print(f"❌ 체크섬 계산 실패: {e}")
            return ""
            
    def create_deployment_artifact(self, deploy_id: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """배포 아티팩트 생성"""
        try:
            # 아티팩트 파일 생성
            artifact_path = f"{self.artifacts_dir}/{deploy_id}.tar.gz"
            log_path = f"{self.logs_dir}/{deploy_id}.log"
            
            # 가상의 아티팩트 파일 생성
            with open(artifact_path, 'w') as f:
                f.write(f"Deployment artifact for {deploy_id}\\n")
                f.write(f"Config: {json.dumps(config, indent=2)}\\n")
                f.write(f"Created: {datetime.now().isoformat()}\\n")
                
            # 로그 파일 생성
            with open(log_path, 'w') as f:
                f.write(f"Deployment log for {deploy_id}\\n")
                f.write(f"Config: {json.dumps(config, indent=2)}\\n")
                f.write(f"Status: DEPLOYING\\n")
                f.write(f"Timestamp: {datetime.now().isoformat()}\\n")
                
            # 체크섬 계산
            artifact_checksum = self.calculate_sha256(artifact_path)
            log_checksum = self.calculate_sha256(log_path)
            
            # 메타데이터 생성
            metadata = {
                "deploy_id": deploy_id,
                "artifact_path": artifact_path,
                "log_path": log_path,
                "image_tag": f"duri:{deploy_id}",
                "artifact_checksum": artifact_checksum,
                "log_checksum": log_checksum,
                "artifact_size": os.path.getsize(artifact_path),
                "log_size": os.path.getsize(log_path),
                "created_at": datetime.now().isoformat(),
                "config": config
            }
            
            # 메타데이터 파일 저장
            metadata_path = f"{self.artifacts_dir}/{deploy_id}.metadata.json"
            with open(metadata_path, 'w') as f:
                json.dump(metadata, f, indent=2)
                
            return metadata
            
        except Exception as e:
            print(f"❌ 배포 아티팩트 생성 실패: {e}")
            return {}
            
    def verify_deployment(self, deploy_id: str) -> Dict[str, Any]:
        """배포 무결성 검증"""
        try:
            metadata_path = f"{self.artifacts_dir}/{deploy_id}.metadata.json"
            
            if not os.path.exists(metadata_path):
                return {"valid": False, "error": "메타데이터 파일 없음"}
                
            # 메타데이터 로드
            with open(metadata_path, 'r') as f:
                metadata = json.load(f)
                
            # 파일 존재 확인
            artifact_path = metadata.get('artifact_path')
            log_path = metadata.get('log_path')
            
            if not os.path.exists(artifact_path):
                return {"valid": False, "error": "아티팩트 파일 없음"}
                
            if not os.path.exists(log_path):
                return {"valid": False, "error": "로그 파일 없음"}
                
            # 체크섬 검증
            current_artifact_checksum = self.calculate_sha256(artifact_path)
            current_log_checksum = self.calculate_sha256(log_path)
            
            artifact_valid = current_artifact_checksum == metadata.get('artifact_checksum')
            log_valid = current_log_checksum == metadata.get('log_checksum')
            
            return {
                "valid": artifact_valid and log_valid,
                "artifact_valid": artifact_valid,
                "log_valid": log_valid,
                "current_artifact_checksum": current_artifact_checksum,
                "current_log_checksum": current_log_checksum,
                "stored_artifact_checksum": metadata.get('artifact_checksum'),
                "stored_log_checksum": metadata.get('log_checksum'),
                "metadata": metadata
            }
            
        except Exception as e:
            return {"valid": False, "error": str(e)}
