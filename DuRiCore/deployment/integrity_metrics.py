#!/usr/bin/env python3
"""
DuRi 무결성 검증 메트릭 노출 (감사/가시성)
"""

import time
from typing import Dict, Any
from DuRiCore.global_logging_manager import get_duri_logger

logger = get_duri_logger("integrity_metrics")

class IntegrityMetrics:
    """무결성 검증 메트릭 노출 클래스"""
    
    def __init__(self):
        self.metrics = {}
    
    def record_integrity_scan(self, integrity_result: Dict[str, Any]):
        """
        무결성 검증 결과를 메트릭으로 기록
        
        Args:
            integrity_result: 무결성 검증 결과
        """
        try:
            # 기본 메트릭
            self.metrics.update({
                "duri_integrity_scan_info": {
                    "value": 1,
                    "labels": {
                        "deployment_id": integrity_result.get("deployment_id", "unknown"),
                        "schema_version": integrity_result.get("schema_version", "unknown"),
                        "hash_algorithm": integrity_result.get("hash_algorithm", "unknown"),
                        "hash_version": integrity_result.get("hash_version", "unknown"),
                        "mode": integrity_result.get("mode", "unknown"),
                        "status": integrity_result.get("status", "unknown"),
                    }
                },
                "duri_integrity_scan_duration_ms": {
                    "value": integrity_result["summary"].get("scan_duration_ms", 0),
                    "labels": {
                        "deployment_id": integrity_result.get("deployment_id", "unknown"),
                    }
                },
                "duri_integrity_scan_bytes_hashed": {
                    "value": integrity_result["summary"].get("bytes_hashed", 0),
                    "labels": {
                        "deployment_id": integrity_result.get("deployment_id", "unknown"),
                    }
                },
                "duri_integrity_files_total": {
                    "value": integrity_result["summary"].get("total_files", 0),
                    "labels": {
                        "deployment_id": integrity_result.get("deployment_id", "unknown"),
                        "type": "total"
                    }
                },
                "duri_integrity_files_verified": {
                    "value": integrity_result["summary"].get("verified_files", 0),
                    "labels": {
                        "deployment_id": integrity_result.get("deployment_id", "unknown"),
                        "type": "verified"
                    }
                },
                "duri_integrity_files_modified": {
                    "value": integrity_result["summary"].get("modified_files", 0),
                    "labels": {
                        "deployment_id": integrity_result.get("deployment_id", "unknown"),
                        "type": "modified"
                    }
                },
                "duri_integrity_files_missing": {
                    "value": integrity_result["summary"].get("missing_files", 0),
                    "labels": {
                        "deployment_id": integrity_result.get("deployment_id", "unknown"),
                        "type": "missing"
                    }
                },
                "duri_integrity_files_new": {
                    "value": integrity_result["summary"].get("new_files", 0),
                    "labels": {
                        "deployment_id": integrity_result.get("deployment_id", "unknown"),
                        "type": "new"
                    }
                }
            })
            
            # ignore 정책 메트릭
            if "ignore_info" in integrity_result:
                ignore_info = integrity_result["ignore_info"]
                self.metrics["duri_integrity_ignore_hash"] = {
                    "value": 1,
                    "labels": {
                        "deployment_id": integrity_result.get("deployment_id", "unknown"),
                        "current_hash": ignore_info.get("current_hash", "unknown"),
                        "stored_hash": ignore_info.get("stored_hash", "unknown"),
                        "mismatch": str(ignore_info.get("mismatch", False)).lower()
                    }
                }
            
            # HMAC 서명 메트릭
            if "signatures" in integrity_result:
                sig_info = integrity_result["signatures"]
                self.metrics["duri_integrity_hmac_status"] = {
                    "value": 1,
                    "labels": {
                        "deployment_id": integrity_result.get("deployment_id", "unknown"),
                        "checksums_ok": str(sig_info.get("checksums_hmac_ok", False)).lower(),
                        "metadata_ok": str(sig_info.get("metadata_hmac_ok", False)).lower(),
                        "enabled": str(sig_info.get("enabled", False)).lower()
                    }
                }
            
            # 상태별 카운터
            status = integrity_result.get("status", "unknown")
            self.metrics[f"duri_integrity_status_{status}"] = {
                "value": 1,
                "labels": {
                    "deployment_id": integrity_result.get("deployment_id", "unknown"),
                }
            }
            
            logger.info(f"무결성 메트릭 기록 완료: {len(self.metrics)}개 메트릭")
            
        except Exception as e:
            logger.error(f"무결성 메트릭 기록 실패: {e}")
    
    def get_prometheus_metrics(self) -> str:
        """
        Prometheus 형식 메트릭 출력
        
        Returns:
            Prometheus 형식 메트릭 문자열
        """
        try:
            lines = []
            timestamp = int(time.time() * 1000)  # milliseconds
            
            for metric_name, metric_data in self.metrics.items():
                value = metric_data["value"]
                labels = metric_data["labels"]
                
                # 라벨 문자열 생성
                label_pairs = [f'{k}="{v}"' for k, v in labels.items()]
                label_str = "{" + ",".join(label_pairs) + "}" if label_pairs else ""
                
                # 메트릭 라인 생성
                line = f"{metric_name}{label_str} {value} {timestamp}"
                lines.append(line)
            
            return "\n".join(lines) + "\n"
            
        except Exception as e:
            logger.error(f"Prometheus 메트릭 생성 실패: {e}")
            return ""
    
    def export_to_file(self, file_path: str):
        """
        메트릭을 파일로 내보내기
        
        Args:
            file_path: 출력 파일 경로
        """
        try:
            metrics_text = self.get_prometheus_metrics()
            if metrics_text:
                with open(file_path, 'w') as f:
                    f.write(metrics_text)
                logger.info(f"메트릭 내보내기 완료: {file_path}")
            else:
                logger.warning("내보낼 메트릭이 없습니다")
                
        except Exception as e:
            logger.error(f"메트릭 내보내기 실패: {e}")
    
    def clear_metrics(self):
        """메트릭 초기화"""
        self.metrics.clear()
        logger.info("메트릭 초기화 완료")

# 전역 인스턴스
integrity_metrics = IntegrityMetrics()
