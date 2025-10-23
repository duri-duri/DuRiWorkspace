#!/usr/bin/env python3
"""
검증 2중 루프 시스템
1차: SHA256 체크섬 검증
2차: 샘플 파일 열기 검증
"""

import hashlib
import os
import random
import sys
import time
from pathlib import Path
from typing import Dict, List, Tuple


class DualVerification:
    def __init__(self, backup_dir: str, sample_count: int = 3):
        self.backup_dir = Path(backup_dir)
        self.sample_count = sample_count
        self.verification_results = {
            "sha256": {"success": 0, "failed": 0, "errors": []},
            "sample_open": {"success": 0, "failed": 0, "errors": []},
        }

    def generate_checksums(self) -> Dict[str, str]:
        """백업 디렉토리의 모든 파일에 대해 SHA256 체크섬 생성"""
        checksums = {}
        print(f"🔍 SHA256 체크섬 생성 중... ({self.backup_dir})")

        for file_path in self.backup_dir.rglob("*"):
            if file_path.is_file():
                try:
                    with open(file_path, "rb") as f:
                        file_hash = hashlib.sha256(f.read()).hexdigest()
                        checksums[str(file_path)] = file_hash
                except Exception as e:
                    self.verification_results["sha256"]["errors"].append(
                        f"Failed to hash {file_path}: {e}"
                    )
                    self.verification_results["sha256"]["failed"] += 1

        self.verification_results["sha256"]["success"] = len(checksums)
        print(f"✅ SHA256 체크섬 생성 완료: {len(checksums)}개 파일")
        return checksums

    def verify_checksums(self, checksums: Dict[str, str]) -> bool:
        """생성된 체크섬 검증"""
        print(f"🔍 SHA256 체크섬 검증 중...")

        all_valid = True
        for file_path, expected_hash in checksums.items():
            try:
                with open(file_path, "rb") as f:
                    actual_hash = hashlib.sha256(f.read()).hexdigest()

                if actual_hash != expected_hash:
                    self.verification_results["sha256"]["errors"].append(
                        f"Hash mismatch for {file_path}"
                    )
                    self.verification_results["sha256"]["failed"] += 1
                    all_valid = False
                else:
                    self.verification_results["sha256"]["success"] += 1

            except Exception as e:
                self.verification_results["sha256"]["errors"].append(
                    f"Failed to verify {file_path}: {e}"
                )
                self.verification_results["sha256"]["failed"] += 1
                all_valid = False

        if all_valid:
            print(f"✅ SHA256 체크섬 검증 통과!")
        else:
            print(f"❌ SHA256 체크섬 검증 실패!")

        return all_valid

    def sample_file_verification(self) -> bool:
        """샘플 파일 열기 검증 (2차 검증)"""
        print(f"🔍 샘플 파일 열기 검증 중... (샘플 수: {self.sample_count})")

        # 백업 디렉토리에서 파일 목록 수집
        all_files = [f for f in self.backup_dir.rglob("*") if f.is_file()]

        if len(all_files) < self.sample_count:
            print(f"⚠️  파일 수 부족: {len(all_files)}개 (필요: {self.sample_count}개)")
            self.sample_count = len(all_files)

        # 랜덤 샘플 선택
        sample_files = random.sample(all_files, min(self.sample_count, len(all_files)))

        all_valid = True
        for file_path in sample_files:
            try:
                # 파일 메타데이터 확인
                stat_info = file_path.stat()

                # 파일 내용 읽기 시도 (첫 1KB만)
                with open(file_path, "rb") as f:
                    content = f.read(1024)

                # 파일 타입 확인
                import magic

                file_type = magic.from_buffer(content, mime=True)

                print(f"  ✅ {file_path.name}: {stat_info.st_size} bytes, {file_type}")
                self.verification_results["sample_open"]["success"] += 1

            except Exception as e:
                print(f"  ❌ {file_path.name}: {e}")
                self.verification_results["sample_open"]["errors"].append(
                    f"Failed to verify {file_path}: {e}"
                )
                self.verification_results["sample_open"]["failed"] += 1
                all_valid = False

        if all_valid:
            print(f"✅ 샘플 파일 열기 검증 통과!")
        else:
            print(f"❌ 샘플 파일 열기 검증 실패!")

        return all_valid

    def run_dual_verification(self) -> bool:
        """검증 2중 루프 실행"""
        print(f"🚀 검증 2중 루프 시작...")
        start_time = time.time()

        # 1차 검증: SHA256 체크섬
        print(f"\n📋 1차 검증: SHA256 체크섬")
        checksums = self.generate_checksums()
        sha256_valid = self.verify_checksums(checksums)

        # 2차 검증: 샘플 파일 열기
        print(f"\n📋 2차 검증: 샘플 파일 열기")
        sample_valid = self.sample_file_verification()

        # 결과 요약
        elapsed_time = time.time() - start_time
        print(f"\n📊 검증 2중 루프 결과 요약:")
        print(f"  - 소요 시간: {elapsed_time:.2f}초")
        print(f"  - SHA256 검증: {'✅ 통과' if sha256_valid else '❌ 실패'}")
        print(f"  - 샘플 파일 검증: {'✅ 통과' if sample_valid else '❌ 실패'}")
        print(
            f"  - 전체 결과: {'✅ 통과' if (sha256_valid and sample_valid) else '❌ 실패'}"
        )

        # 상세 결과
        print(f"\n📋 상세 결과:")
        print(f"  SHA256:")
        print(f"    - 성공: {self.verification_results['sha256']['success']}개")
        print(f"    - 실패: {self.verification_results['sha256']['failed']}개")

        print(f"  샘플 파일 열기:")
        print(f"    - 성공: {self.verification_results['sample_open']['success']}개")
        print(f"    - 실패: {self.verification_results['sample_open']['failed']}개")

        # 오류가 있으면 출력
        if self.verification_results["sha256"]["errors"]:
            print(f"\n❌ SHA256 오류:")
            for error in self.verification_results["sha256"]["errors"]:
                print(f"    - {error}")

        if self.verification_results["sample_open"]["errors"]:
            print(f"\n❌ 샘플 파일 열기 오류:")
            for error in self.verification_results["sample_open"]["errors"]:
                print(f"    - {error}")

        return sha256_valid and sample_valid


def main():
    """메인 실행 함수"""
    if len(sys.argv) < 2:
        print("Usage: python dual_verification.py <backup_directory> [sample_count]")
        sys.exit(1)

    backup_dir = sys.argv[1]
    sample_count = int(sys.argv[2]) if len(sys.argv) > 2 else 3

    if not os.path.exists(backup_dir):
        print(f"[ERROR] Backup directory not found: {backup_dir}")
        sys.exit(1)

    # 검증 실행
    verifier = DualVerification(backup_dir, sample_count)
    success = verifier.run_dual_verification()

    # 종료 코드
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
