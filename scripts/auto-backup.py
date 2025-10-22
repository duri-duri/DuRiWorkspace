#!/usr/bin/env python3
"""
DuRi 백업 자동화 시스템

사용법:
    python3 auto-backup.py 백업 "일반 작업 완료"
    python3 auto-backup.py 백업백업 "통합 테스트 성공"
    python3 auto-backup.py 백업백업백업 "중요 시스템 완성"
"""

import logging
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path

# 로깅 설정
logging.basicConfig(level=logging.INFO, format="%(levelname)s:%(message)s")
logger = logging.getLogger(__name__)


class DuRiAutoBackup:
    """DuRi 백업 자동화 시스템"""

    def __init__(self):
        """초기화"""
        self.script_dir = Path(__file__).parent
        self.project_root = self.script_dir.parent
        self.backup_dir = Path("/mnt/c/Users/admin/Desktop/두리백업")

        # 백업 스크립트 매핑
        self.backup_scripts = {
            "백업": "duri-backup.sh",
            "백업백업": "duri-backup-backup.sh",
            "백업백업백업": "duri-backup-backup-backup.sh",
        }

        # 백업 수준별 설명
        self.backup_levels = {
            "백업": "일반 백업",
            "백업백업": "중요 백업",
            "백업백업백업": "완벽한 복제 수준",
        }

        logger.info("🔄 DuRi 백업 자동화 시스템 초기화 완료")

    def validate_backup_level(self, level: str) -> bool:
        """백업 수준 유효성 검사"""
        if level not in self.backup_scripts:
            logger.error(f"❌ 잘못된 백업 수준: {level}")
            logger.info(f"사용 가능한 수준: {', '.join(self.backup_scripts.keys())}")
            return False
        return True

    def create_backup_description(self, level: str, description: str) -> str:
        """백업 설명 생성"""
        timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
        level_desc = self.backup_levels[level]
        return f"{level_desc}_{timestamp}_{description}"

    def execute_backup(self, level: str, description: str) -> bool:
        """백업 실행"""
        try:
            logger.info(f"🛡️ {level} 시작: {description}")

            # 백업 스크립트 경로
            script_path = self.script_dir / self.backup_scripts[level]

            if not script_path.exists():
                logger.error(f"❌ 백업 스크립트를 찾을 수 없습니다: {script_path}")
                return False

            # 백업 설명 생성
            backup_desc = self.create_backup_description(level, description)

            # 백업 스크립트 실행
            logger.info(f"📁 백업 스크립트 실행: {script_path}")
            logger.info(f"📝 백업 설명: {backup_desc}")

            result = subprocess.run(
                [str(script_path), backup_desc],
                capture_output=True,
                text=True,
                cwd=self.project_root,
            )

            if result.returncode == 0:
                logger.info(f"✅ {level} 완료!")
                logger.info(f"📋 출력: {result.stdout.strip()}")
                return True
            else:
                logger.error(f"❌ {level} 실패!")
                logger.error(f"오류: {result.stderr.strip()}")
                return False

        except Exception as e:
            logger.error(f"❌ {level} 실행 중 오류 발생: {e}")
            return False

    def show_backup_info(self, level: str, description: str):
        """백업 정보 표시"""
        print("\n" + "=" * 60)
        print(f"🛡️ DuRi {level} 실행")
        print("=" * 60)
        print(f"📅 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"📝 설명: {description}")
        print(f"📁 저장 위치: {self.backup_dir}")
        print(f"🔧 백업 수준: {self.backup_levels[level]}")
        print("=" * 60)

    def run(self, level: str, description: str) -> bool:
        """백업 자동화 실행"""
        try:
            # 백업 수준 검증
            if not self.validate_backup_level(level):
                return False

            # 백업 정보 표시
            self.show_backup_info(level, description)

            # 백업 실행
            success = self.execute_backup(level, description)

            if success:
                print(f"\n🎉 {level}가 성공적으로 완료되었습니다!")
                print(f"📁 백업 파일이 {self.backup_dir}에 저장되었습니다.")
            else:
                print(f"\n❌ {level} 실행에 실패했습니다.")

            return success

        except Exception as e:
            logger.error(f"❌ 백업 자동화 실행 중 오류: {e}")
            return False


def main():
    """메인 함수"""
    if len(sys.argv) != 3:
        print("❌ 사용법: python3 auto-backup.py [백업수준] [설명]")
        print("📋 예시:")
        print('   python3 auto-backup.py 백업 "일반 작업 완료"')
        print('   python3 auto-backup.py 백업백업 "통합 테스트 성공"')
        print('   python3 auto-backup.py 백업백업백업 "중요 시스템 완성"')
        sys.exit(1)

    level = sys.argv[1]
    description = sys.argv[2]

    # 백업 자동화 실행
    auto_backup = DuRiAutoBackup()
    success = auto_backup.run(level, description)

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
